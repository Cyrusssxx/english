# -*- coding: utf-8 -*-
"""
生成小作文「真题套用示范」（2010–2026，17 篇）

数据源：tools/apply_small_plan.py（人工挑句组 + 槽位值）+ pwa/data/small_writing.json（句库）
输出：
  pwa/data/small_apply.json        每篇示范（写进 {year}.json 的 writinga.apply）
  pwa/data/small_apply_marks.json  逐句标注（前端渲染来源/槽位，键 = 年份，与大作文分开文件以免冲突）
  pwa/data/{year}.json             注入 apply 字段（文章页显示在「参考范文」上方）

用法：python tools/build_small_apply.py [--check]
      --check 只体检不写文件
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
DATA = os.path.join(ROOT, 'pwa', 'data')

import apply_small_plan as P      # noqa: E402

SW_FP = os.path.join(DATA, 'small_writing.json')
OUT_AP = os.path.join(DATA, 'small_apply.json')
OUT_MK = os.path.join(DATA, 'small_apply_marks.json')

PH = re.compile(r'\{\{(.+?)\}\}')
PARA_CN = ['第一段', '第二段', '第三段']
MIN_W, MAX_W = 90, 120          # 真题要求 about 100 words


# 槽位前若是 to / should / could / must / be able to / wish to 等，值必须是动词短语（不能以冠词开头）
VBE = re.compile(r'(?:\bto|\bshould|\bcould|\bmust|\bable\s+to|\bwish\s+to|\bwill)\s+$', re.I)
# 这些 to 是介词（不是不定式），后面的槽位填名词没问题
PREP_TO = re.compile(r'(?:with\s+regard|due|according|owing|thanks|prior|in\s+addition|close|up|back|next|subject|refer|refers|lead|leads|adapt|look\s+forward|object|belong|contribute|respond|point|points)\s+to\s+$', re.I)


def check_verb_slot(tpl, slots, where):
    """模板里 to/should/could 后面的槽位若填了名词（以 a/an/the 开头），直接报错"""
    for m in PH.finditer(tpl or ''):
        key = m.group(1)
        v = slots.get(key)
        if not v:
            continue
        pre = (tpl or '')[:m.start()]
        if PREP_TO.search(pre):
            continue
        if VBE.search(pre) and re.match(r'^(a|an|the)\s+', v[0], re.I):
            raise SystemExit('%s：槽位 %r 在 to/should 之后，必须是动词短语，不能填 %r' % (where, key, v[0]))


def wc(t):
    return len([x for x in re.split(r'\s+', (t or '').strip()) if re.search(r'[A-Za-z0-9]', x)])


def load():
    d = json.load(io.open(SW_FP, encoding='utf-8'))
    return d, {b['id']: b for b in d['banks']}


def fill(tpl, slots, where):
    """把模板里的 {{key}} 换成 (en, cn) 的第 i 项；返回 (文本, spans)"""
    lang = 0 if tpl is None else None
    return _fill(tpl, slots, where, lang)


def fill_both(tpl_en, tpl_cn, slots, where):
    en, sp_en = _fill(tpl_en, slots, where, 0)
    cn, sp_cn = _fill(tpl_cn, slots, where, 1)
    # 槽位集合必须与模板一致（多了/少了都报错，避免中英错位）
    need = set(PH.findall(tpl_en or ''))
    if need != set(PH.findall(tpl_cn or '')):
        raise SystemExit('%s：中英模板槽位不一致\n  EN %s\n  CN %s' % (where, tpl_en, tpl_cn))
    miss = need - set(slots)
    if miss:
        raise SystemExit('%s：缺槽位 %s' % (where, sorted(miss)))
    extra = set(slots) - need
    if extra:
        raise SystemExit('%s：多余槽位 %s（模板里没有）' % (where, sorted(extra)))
    return en, cn, sp_en, sp_cn


def _fill(tpl, slots, where, lang):
    text, spans = [], []
    for i, seg in enumerate(PH.split(tpl or '')):
        if not seg:
            continue
        if i % 2 == 0:                      # 普通文本
            spans.append({'t': 't', 'x': seg})
            text.append(seg)
        else:                               # 槽位
            v = slots.get(seg)
            if v is None:
                continue
            if not isinstance(v, (list, tuple)) or len(v) < 2:
                raise SystemExit('%s：槽位 %r 必须写成 (英文, 中文) 二元组' % (where, seg))
            val = v[lang]
            spans.append({'t': 's', 'x': val})
            text.append(val)
    return ''.join(text), spans


def build():
    d, banks = load()
    out_ap, out_mk = {}, {}
    report = []
    for y in sorted(P.PLAN):
        c = P.PLAN[y]
        paras_mk, texts_en, texts_cn = [], [], []
        slots_seen, keys_seen = [], []
        for pi, para in enumerate(c['paras']):
            sents, en_list, cn_list, pw = [], [], [], 0
            for (bid, idx, slots) in para:
                b = banks.get(bid)
                if not b:
                    raise SystemExit('%s：没有段落 %s' % (y, bid))
                if idx >= len(b['items']):
                    raise SystemExit('%s：%s 只有 %d 句，取了第 %d 句' % (y, bid, len(b['items']), idx + 1))
                it = b['items'][idx]
                where = '%s %s[%d]' % (y, bid, idx)
                check_verb_slot(it['en'], slots, where)
                en, cn, sp_en, sp_cn = fill_both(it['en'], it['cn'], slots, where)
                sents.append({
                    'kind': 'tpl',
                    'spans': sp_en, 'spans_cn': sp_cn,
                    'src': '%s · 模板第%d句' % (b['label'], idx + 1),
                })
                en_list.append(en)
                cn_list.append(cn)
                pw += wc(en)
                for k, v in slots.items():
                    slots_seen.append({'name': k, 'en': v[0], 'cn': v[1], 'para': PARA_CN[pi]})
                keys_seen.append({'en': it['en'], 'cn': it['cn'], 'src': '%s · 模板第%d句' % (b['label'], idx + 1)})
            paras_mk.append({'wc': pw, 'sents': sents})
            texts_en.append(' '.join(en_list))
            texts_cn.append(''.join(cn_list))

        # 去重（按 name+en / en+src）
        slot_phr, seen_s = [], set()
        for s in slots_seen:
            k = (s['name'], s['en'])
            if k in seen_s:
                continue
            seen_s.add(k)
            slot_phr.append(s)
        key_phr, seen_k = [], set()
        for k2 in keys_seen:
            if k2['en'] in seen_k:
                continue
            seen_k.add(k2['en'])
            key_phr.append(k2)

        body_en = '\n\n'.join(texts_en)
        body_cn = '\n\n'.join(texts_cn)
        total = sum(p['wc'] for p in paras_mk)

        # 正文（含称呼/落款）用于 fallback 与展示
        full_en = '\n'.join([x for x in [c.get('salutation'), body_en, c.get('close')] if x])
        full_cn = '\n'.join([x for x in [c.get('salutation'), body_cn, c.get('close')] if x])

        out_ap[y] = {
            'title': c['title'],
            'typeId': c['typeId'],
            'apply_en': full_en, 'apply_cn': full_cn,
            'tips': c['tips'],
            'slot_phrases': slot_phr, 'key_phrases': key_phr,
        }
        out_mk[y] = {
            'wc': total, 'req': 95,       # 小作文要求 about 100 words，95 起算达标（大作文是 150）
            'salutation': c.get('salutation') or '',
            'close': c.get('close') or '',
            'paras': paras_mk,
            'slot_phrases': slot_phr, 'key_phrases': key_phr,
        }
        flag = '' if MIN_W <= total <= MAX_W else '  ⚠ 词数越界'
        report.append('  %s  %3d 词（%s）｜%s｜槽位 %d 个%s' % (
            y, total, '/'.join(str(p['wc']) for p in paras_mk),
            c['typeId'], len(slot_phr), flag))
    return out_ap, out_mk, report


def inject(out_ap):
    """把示范写进 pwa/data/{year}.json 的 writinga 文章（文章页显示在参考范文上方）"""
    n = 0
    for y, ap in out_ap.items():
        fp = os.path.join(DATA, '%s.json' % y)
        if not os.path.exists(fp):
            print('  ⚠ %s.json 不存在，跳过' % y)
            continue
        d = json.load(io.open(fp, encoding='utf-8'))
        hit = [a for a in d.get('articles', []) if a.get('id') == P.PLAN[y]['aid']]
        if not hit:
            print('  ⚠ %s 没有 %s，跳过' % (y, P.PLAN[y]['aid']))
            continue
        hit[0]['apply'] = {
            'apply_en': ap['apply_en'], 'apply_cn': ap['apply_cn'],
            'tips': ap['tips'],
            'slot_phrases': ap['slot_phrases'], 'key_phrases': ap['key_phrases'],
            'title': ap['title'],
        }
        json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        n += 1
    return n


def main():
    out_ap, out_mk, report = build()
    print('\n'.join(report))
    bad = [r for r in report if '⚠' in r]
    print('\n共 %d 篇；越界 %d 篇' % (len(report), len(bad)))
    if bad:
        print('\n'.join(bad))
    if '--check' in sys.argv:
        return
    json.dump(out_ap, io.open(OUT_AP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(out_mk, io.open(OUT_MK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n = inject(out_ap)
    print('\n已写 small_apply.json / small_apply_marks.json；注入 year.json %d 篇' % n)


if __name__ == '__main__':
    main()
