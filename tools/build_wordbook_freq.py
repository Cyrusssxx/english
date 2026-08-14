"""Build pwa/data/wordbook_freq.json — 真题高频词词书.

Derives a clean high-frequency *content-word* list from pwa/data/freq.json
(word -> {c: count, a: ?}). Strips stopwords + non-content tokens, then keeps
the top N by count. This is the "真题高频词" book used by chain.html's 随机抽词.
"""
import json, re

FREQ = 'pwa/data/freq.json'
OUT = 'pwa/data/wordbook_freq.json'
TOP = 700          # 词书容量
MIN_LEN = 4        # 只收 4 字母以上的词，过滤冠词/代词等噪声

STOP = set([
    "the","a","an","and","or","but","if","then","else","of","to","in","on","at","by",
    "for","with","as","from","into","about","over","under","again","more","most","some",
    "such","only","than","that","this","these","those","it","its","they","them","their",
    "we","our","you","your","he","his","she","her","i","me","my","who","which","what",
    "when","where","how","why","is","are","was","were","be","been","being","am","do",
    "does","did","done","has","have","had","having","will","would","shall","should",
    "can","could","may","might","must","need","not","no","yes","so","too","very","just",
    "also","even","still","yet","already","each","all","any","both","either","neither",
    "one","two","three","first","last","new","old","up","down","out","off","now","here",
    "there","after","before","because","while","although","though","through","between",
    "among","above","below","own","same","other","another","many","much","few","little",
    "per","via","upon","within","without","against","since","until","whether","whatever",
    "him","us","get","got","go","going","make","made","take","taken","put","set","see",
    "seen","look","like","use","used","using","say","said","come","came","know","known",
    "think","thought","want","find","found","give","given","tell","told","ask","back",
    "well","way","time","year","work","world","life","people","man","men","woman","women",
    "day","things","thing","place","part","case","fact","point","group","number","system",
    "problem","result","change","level","example","idea","process","state","house","water",
])

def is_content(w):
    if len(w) < MIN_LEN:
        return False
    if not re.fullmatch(r"[a-z]+", w):
        return False
    if w in STOP:
        return False
    return True

def main():
    freq = json.load(open(FREQ, encoding='utf-8'))
    rows = []
    for w, meta in freq.items():
        lw = w.lower()
        if not is_content(lw):
            continue
        c = (meta.get('c') if isinstance(meta, dict) else meta) or 0
        rows.append((lw, c))
    rows.sort(key=lambda x: -x[1])
    words = [w for w, _ in rows[:TOP]]
    seen = set(); uniq = []
    for w in words:
        if w not in seen:
            seen.add(w); uniq.append(w)
    json.dump({"id": "freq", "name": "真题高频词", "words": uniq},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"OK: {len(uniq)} 个真题高频词 -> {OUT}")

if __name__ == '__main__':
    main()
