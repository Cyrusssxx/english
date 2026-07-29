# -*- coding: utf-8 -*-
"""
从「英语词库」3 个 txt 词表构建 3 个内置词书数据文件（符合 vocab.html 导入契约）：
  pwa/data/deck_core.json       —— 考研真题核心词汇（2230）
  pwa/data/deck_syllabus.json   —— 考研考纲词汇·乱序（5554）
  pwa/data/deck_confusable.json —— 考研形近易混词汇（1013）

txt 格式统一为 `word  词性.释义`：首个空白前的 token 为 word，其余为 meaning。
释义 100% 照抄词表，无 AI 生成。真题词组词书（deck_phrases.json）由 build_phrases.py 单独产出。

运行：python -X utf8 tools/build_decks.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')
LIB_DIR = r"d:\ai code\英语词库"

# (源 txt 文件名, 输出文件名, 词书名)
DECKS = [
    ('考研真题核心词汇书.txt', 'deck_core.json', '考研真题核心词汇'),
    ('完全版考研考纲词汇（乱序）.txt', 'deck_syllabus.json', '考研考纲词汇（乱序）'),
    ('考研形近易混词汇.txt', 'deck_confusable.json', '考研形近易混词汇'),
]


def parse_txt(path):
    """逐行解析 `word  词性.释义`；首空白前为 word，其余为 meaning。按 word 去重（保留首现）。"""
    words = []
    seen = set()
    with open(path, encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            parts = re.split(r'\s+', line, maxsplit=1)
            word = parts[0].strip()
            meaning = parts[1].strip() if len(parts) > 1 else ''
            if not word or not meaning:
                continue
            key = word.lower()
            if key in seen:
                continue
            seen.add(key)
            words.append({'word': word, 'meaning': meaning})
    return words


def main():
    for src, out_name, deck_name in DECKS:
        src_path = os.path.join(LIB_DIR, src)
        words = parse_txt(src_path)
        deck = {'name': deck_name, 'words': words}
        out_path = os.path.join(DATA_DIR, out_name)
        with open(out_path, 'w', encoding='utf-8') as fp:
            json.dump(deck, fp, ensure_ascii=False)
        size = os.path.getsize(out_path)
        print(f'{out_name}：{len(words)} 词（{deck_name}），体积 {size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
