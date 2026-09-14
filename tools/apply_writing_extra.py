#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 tools/writing_extra.py 的内容合并进 pwa/data/writing_templates.json（幂等）。

- 首跑：按 PRUNE 删句池冗余 + 写入 teacher / flow / data_lang / mistakes / checklist
- 再跑：只同步这几个新键（不再动句池），并在末尾打印体检（句池句数、疑似重复组）

用法：python tools/apply_writing_extra.py
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import writing_extra as EX

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.abspath(__file__))
FP = os.path.join(os.path.normpath(os.path.join(ROOT, '..')), 'pwa', 'data', 'writing_templates.json')

STOP = set(('a an the to of in for and or is are be been it its this that with as at on by you your '
            'i we our me my can could will would should not no so such from into than then there their '
            'they them he she his her do does did have has had more most very while when which').split())


def words(s):
    s = re.sub(r'\{\{.+?\}\}', ' ', (s or '').lower())
    return set(w for w in re.findall(r"[a-z][a-z'-]+", s) if w not in STOP)


def main():
    d = json.load(open(FP, encoding='utf-8'))
    sections = {s['id']: s for s in d['sections']}

    if d.get('_extra_ver') != EX.VER:
        dropped = 0
        for sid, keep in EX.PRUNE.items():
            s = sections.get(sid)
            if not s:
                raise SystemExit('PRUNE 里有未知 section：%s' % sid)
            before = len(s.get('sentences') or [])
            s['sentences'] = [x for i, x in enumerate(s.get('sentences') or []) if i in set(keep)]
            dropped += before - len(s['sentences'])
        d['_extra_ver'] = EX.VER
        print('句池删冗余：- %d 句' % dropped)
    else:
        print('句池已是 %d 版保留清单，跳过（只同步新板块）' % EX.VER)

    d['teacher'] = EX.TEACHER
    d['flow'] = EX.FLOW
    d['data_lang'] = EX.DATA_LANG
    d['mistakes'] = EX.MISTAKES
    d['checklist'] = EX.CHECKLIST
    json.dump(d, io.open(FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---------- 体检 ----------
    tot = 0
    hot = []
    for s in d['sections']:
        items = [x['en'] for x in (s.get('sentences') or [])]
        tot += len(items)
        mx = 0
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = words(items[i]), words(items[j])
                if a and b:
                    mx = max(mx, len(a & b) / len(a | b))
        if mx >= 0.6:
            hot.append((s['id'], round(mx, 2)))
    print('句池合计 %d 句 | 相似度 ≥0.6 的组: %s' % (tot, hot or '无'))
    print('新板块：老师视角 %d 条 / 答题动线 %d 步 / 数据语言 %d 组 + %d 条错误 / 自查表 %d 条'
          % (len(EX.TEACHER), len(EX.FLOW), len(EX.DATA_LANG), len(EX.MISTAKES), len(EX.CHECKLIST)))
    for sid in EX.PRUNE:
        s = sections[sid]
        print('   %-16s %d 句' % (sid, len(s['sentences'])))


if __name__ == '__main__':
    main()
