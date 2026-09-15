# -*- coding: utf-8 -*-
'''把 `apply_plan.py` 里的人工方案落库：
  ① 往 writing_templates.json 插入新增句池句子（幂等，靠 `_plan_ver` 标记）
  ② 给动态骨架 ② 的首句补上时间跨度（同步改 en_struct 片段）
  ③ 写出 tools/apply_plan.json（供 build_apply_from_templates.py 使用）
用法：python tools/build_apply_plan.py
'''
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_plan as P                                    # noqa: E402

TPL = os.path.join(ROOT, 'pwa', 'data', 'writing_templates.json')
OUT = os.path.join(ROOT, 'tools', 'apply_plan.json')
VER = 'plan-2026-09-15d'


def wc(t):
    return len([x for x in re.split(r'\s+', (t or '').strip()) if re.search(r'[A-Za-z]', x)])


def load():
    return json.load(io.open(TPL, encoding='utf-8'))


def sec(d, sid):
    return [s for s in d['sections'] if s['id'] == sid][0]


# ---------- ① 句池补句 ----------
def add_pool(d):
    added = 0
    for sid, rows in P.NEW_POOL.items():
        s = sec(d, sid)
        pool = s.setdefault('sentences', [])
        have = {x['en'] for x in pool}
        for freq, tag, en, cn in rows:
            if en in have:
                continue
            pool.append({'en': en, 'cn': cn, 'freq': freq, 'tag': tag})
            added += 1
    return added


def sort_pool(d):
    '''**不重排**：新句一律追加在池尾，保证 apply_plan.py 里写的序号始终指向同一句。
    页面上「考频优先」的展示顺序由前端按 freq 排序完成（见 writing.js 的渲染段）。'''
    for s in d['sections']:
        for x in (s.get('sentences') or []):
            try:
                x['freq'] = int(x.get('freq', 2))
            except (TypeError, ValueError):
                x['freq'] = 2


# ---------- ② 骨架 ② 首句补时间 ----------
def fix_skel(d):
    """把骨架 ② 首句的「over the period」换成「from {{time1}} to {{time2}}」（看不出年份是硬伤）。
       骨架重置后已自带时间跨度 → 直接跳过。"""
    sid, idx = P.SKEL_FIX[0], P.SKEL_FIX[1]
    s = sec(d, sid)
    sk = s['skeletons'][idx]
    if 'over the period' not in sk['en']:
        return 'n/a（重置后的骨架已含时间跨度）'
    if 'from {{time1}} to {{time2}}' in sk['en']:
        return 'already'
    assert 'over the period' in sk['en'], sk['en'][:80]
    sk['en'] = sk['en'].replace('over the period', 'from {{time1}} to {{time2}}')
    sk['cn'] = sk['cn'].replace('这一时期', '{{time1}} 到 {{time2}} 期间')
    hit = 0
    for sent in sk['struct']:                       # struct 是「句子 → 片段」两层
        for seg in sent:
            if 'over the period' in seg[0]:
                seg[0] = seg[0].replace('over the period', 'from {{time1}} to {{time2}}')
                hit += 1
    assert hit == 1, hit
    flat = ' '.join(''.join(seg[0] for seg in sent) for sent in sk['struct'])
    assert flat == sk['en'], '\n%s\n%s' % (flat, sk['en'])
    return 'ok'


# ---------- ③ 写 apply_plan.json ----------
def parse_refs(txt, sec_d, year):
    """refs 形如 't1 t2 f:差距'：t/f + 序号，或 f:标签（按句池 tag 查；重排/增句都不会错位）"""
    out = []
    for tok in str(txt).split():
        kind, rest = tok[0], tok[1:]
        if kind not in ('t', 'f', 'n'):
            raise SystemExit('%s 的 refs 写法不对：%r' % (year, tok))
        if rest.startswith(':'):
            tag = rest[1:]
            hit = [i for i, x in enumerate(sec_d.get('sentences') or [])
                   if (x.get('tag') or '').strip() == tag]
            if len(hit) != 1:
                raise SystemExit('%s：标签 %r 命中 %d 条（要求唯一）' % (year, tag, len(hit)))
            out.append([kind, hit[0] + 1])
        else:
            out.append([kind, int(rest)])
    return out


def build_spec(d):
    old = json.load(io.open(os.path.join(ROOT, 'tools', 'apply_tpl_spec.json'), encoding='utf-8'))
    out = {}
    for y, c in P.CHART.items():
        sp1 = dict(c['s'])
        sp1['chart'] = c['ch']
        sp1['topic'] = c['topic']
        cn1 = dict(c['scn'])
        cn1['chart'] = c['chcn']
        cn1['topic'] = c['topiccn']
        t2 = c.get('topic2', c['topic'])
        t3 = c.get('topic3', c['topic'])
        SEC = {s['id']: s for s in d['sections']}
        for sid in (c['p1'][0], c['p2'][0], c['p3'][0]):
            if sid not in SEC:
                raise SystemExit('%s 引用了不存在的段 %s' % (y, sid))
        out[y] = {
            'title': old.get(y, {}).get('title', ''),
            'fixed': True,
            'p1': [c['p1'][0], parse_refs(c['p1'][1], SEC[c['p1'][0]], y)],
            'p2': [c['p2'][0], parse_refs(c['p2'][1], SEC[c['p2'][0]], y)],
            'p3': [c['p3'][0], parse_refs(c['p3'][1], SEC[c['p3'][0]], y)],
            'slots_p1': sp1, 'slots_p1_cn': cn1,
            'slots_p2': {'topic': t2}, 'slots_p2_cn': {'topic': c.get('topic2cn', c['topiccn'])},
            'slots_p3': {'topic': t3}, 'slots_p3_cn': {'topic': c.get('topic3cn', c['topiccn'])},
            'pl': sorted(c.get('pl') or []),
        }
    return out


def fix_guide(d):
    '''适配表：事物个数 / 提示语与真题原图对齐（幂等）'''
    fixed = 0
    for r in d['chart_guide']['table']:
        f = P.GUIDE_FIX.get(r['year'])
        if not f:
            continue
        for k, v in f.items():
            if r.get(k) != v:
                r[k] = v
                fixed += 1
    return fixed


def main():
    d = load()
    # 三个修正都是幂等的（补句看文本是否存在、改句看是否已改过、纠错看值是否相同），
    # 所以每次运行都跑一遍——不要用版本号守卫（曾导致后续修正不落库）。
    n = add_pool(d)
    st = fix_skel(d)
    g = fix_guide(d)
    sort_pool(d)
    json.dump(d, io.open(TPL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('句池补句 %d 条；骨架②首句 %s；适配表纠错 %d 处' % (n, st, g))

    spec = build_spec(load())
    json.dump(spec, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(spec, io.open(os.path.join(ROOT, 'tools', 'apply_tpl_spec.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)     # 后备 spec 与人工方案保持一致（否则残留旧段落 id）
    print('apply_plan.json 已写出：%d 年' % len(spec))
    for y in sorted(spec):
        a = spec[y]
        print('  %s %-14s %-16s %-16s | %s | %s' % (
            y, a['p1'][0], a['p2'][0], a['p3'][0],
            ' '.join('%s%d' % tuple(r) for r in a['p1'][1]),
            ' '.join('%s%d' % tuple(r) for r in a['p2'][1]) + ' / '
            + ' '.join('%s%d' % tuple(r) for r in a['p3'][1])))


if __name__ == '__main__':
    main()
