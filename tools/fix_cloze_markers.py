# -*- coding: utf-8 -*-
"""完形填空空白标记归一化：_n_ → [n]（幂等，只改需要改的文件）

全站约定：正文里的空位写作 `[n]`（article.js 的 renderArticle 把 `[n]` 渲染成可点空白槽
`<span class="blank" id="blank-n">`，点击填词）。若某年导入时用了 `_n_`，空位就成了普通文字、
点不了，也不会随作答回填。

用法：python tools/fix_cloze_markers.py [--dry]
"""
import io
import json
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'pwa', 'data')

PAT = re.compile(r'_([0-9]{1,2})_')


def main():
    dry = '--dry' in sys.argv
    files = sorted(glob.glob(os.path.join(DATA, '[0-9][0-9][0-9][0-9].json')))
    files += sorted(glob.glob(os.path.join(DATA, 'en1', '*.json')))
    total = 0
    for fp in files:
        try:
            d = json.load(io.open(fp, encoding='utf-8'))
        except Exception:
            continue
        arts = d.get('articles')
        if not isinstance(arts, list):
            continue
        changed = 0
        for a in arts:
            if not isinstance(a, dict) or a.get('type') != 'cloze':
                continue
            for s in a.get('sentences') or []:
                en = s.get('en') or ''
                if not PAT.search(en):
                    continue
                s['en'] = PAT.sub(lambda m: '[' + m.group(1) + ']', en)
                changed += 1
        if changed:
            total += changed
            print('%s：%d 句完成 [_n_] → [n]%s' % (os.path.basename(fp), changed, '（dry-run 不写盘）' if dry else ''))
            if not dry:
                json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('合计 %d 句%s' % (total, '（dry-run）' if dry else ''))


if __name__ == '__main__':
    main()
