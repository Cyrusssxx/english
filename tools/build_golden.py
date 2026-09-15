# -*- coding: utf-8 -*-
'''精选好句：解析《考研英语作文万能句素材本》→ pwa/data/golden_sentences.json
- 大作文：33 句精挑（删 3 句太单薄的），按「原因 / 背景·观念 / 结尾」三类重排（素材本文末自述的诉求）
- 小作文：从 small_writing.json 的弹药句里按通用度精挑 ★★ 以上
用法：python tools/build_golden.py    （源 md 更新后重跑即可）'''
import io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'golden_source.md')
OUT = os.path.join(ROOT, 'pwa', 'data', 'golden_sentences.json')
SWJ = os.path.join(ROOT, 'pwa', 'data', 'small_writing.json')

DROP = {15, 19, 20}                      # 太单薄/太低级：政府支持文化产业一句 / 需要放松一句 / 忘记烦恼所以喜欢一句
CAT = {}
CAT.update({n: 'ending' for n in (10, 11, 14, 25, 26, 27, 30, 31)})
CAT.update({n: 'background' for n in (2, 9, 17, 24, 32)})
CAT.update({n: 'reason' for n in (1, 3, 4, 5, 6, 7, 8, 12, 13, 16, 18, 21, 22, 23, 28, 29, 33)})

CATS = [
    {'id': 'reason', 'title': '第二段 · 原因 / 机制句',
     'desc': '接在引入句或高级衔接词后面；For one thing / Moreover 这类开头词句子里自带，别再重复加。'},
    {'id': 'background', 'title': '背景 · 观念 / 意义句',
     'desc': '第二段开头引出分论点，或第三段谈意义时用。'},
    {'id': 'ending', 'title': '结尾 · 总结 / 预测 / 利弊句',
     'desc': '收束段直接用；先写立场句（On balance...）再接这些。'},
]


def unesc(s):
    s = re.sub(r'\\([()\-*_.])', r'\1', s or '')
    return re.sub(r'\*{2,}', '……', s).strip()


def parse(md):
    items = {}
    cur = None
    for line in md.splitlines():
        m = re.match(r'^\s*(\d+)\.\s+(.*)$', line)
        if m:
            cur = int(m.group(1))
            items[cur] = {'en': unesc(m.group(2)), 'cn': ''}
            continue
        if cur is None:
            continue
        cm = re.match(r'^>\s?(.+)$', line)
        if cm and not items[cur]['cn']:
            txt = unesc(cm.group(1))
            if txt:
                items[cur]['cn'] = txt
    out = []
    for n in sorted(items):
        if n in DROP:
            continue
        it = items[n]
        en, use, year = it['en'], None, None
        # 尾部（...）组：年份 / 用法标注
        while True:
            m = re.search(r'（([^（）]+)）\s*$', en)
            if not m:
                break
            tag = m.group(1)
            if re.fullmatch(r'\d{4}', tag):
                year, en = tag, en[:m.start()].strip()
            elif '分论点' in tag or '第二段开头' in tag or tag == '结尾句':
                use = tag.replace('，可用于', ' · 可用于')
                en = en[:m.start()].strip()
            else:
                break
        # 开头（结尾句）标注（md 中写作 \(结尾句\)，unesc 后是 ASCII 括号）
        m = re.match(r'^\((结尾句)\)\s*', en)
        if m:
            use, en = m.group(1), en[m.end():].strip()
        # 开头衔接词 \(...,\) → 去括号
        m = re.match(r'^\(([^()]*)\)\s*(.*)$', en)
        if m:
            linker, rest = m.group(1).strip(), m.group(2)
            en = (linker if linker.endswith(',') else linker + ',') + ' ' + rest
        out.append({'n': n, 'en': en, 'cn': it['cn'], 'year': year, 'use': use, 'cat': CAT.get(n, 'reason')})
    return out


def small_picks():
    d = json.load(io.open(SWJ, encoding='utf-8'))
    picks = []
    for bank in d.get('banks', []):
        for it in bank.get('items', []):
            if it.get('tier') == 'ammo' and (it.get('freq') or 0) >= 2:
                picks.append({'en': it['en'], 'cn': it.get('cn', ''), 'tag': it.get('tag', ''),
                              'freq': it.get('freq', 2), 'bank': bank.get('label', '')})
    picks.sort(key=lambda x: -x['freq'])
    return picks[:20]


def main():
    md = io.open(SRC, encoding='utf-8').read()
    big = parse(md)
    small = small_picks()
    json.dump({'big': big, 'cats': CATS, 'small': small, 'dropped': len(DROP)},
              io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    from collections import Counter
    cnt = Counter(x['cat'] for x in big)
    print('精选好句生成：%d 句（原因 %d / 背景观念 %d / 结尾 %d）+ 小作文弹药精挑 %d 句'
          % (len(big), cnt['reason'], cnt['background'], cnt['ending'], len(small)))
    for x in big[:2] + big[-2:]:
        print('  [%s%s] %s' % (x['year'] or '', '/' + x['use'] if x['use'] else '', x['en'][:70]))


if __name__ == '__main__':
    main()
