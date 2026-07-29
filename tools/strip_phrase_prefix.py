# -*- coding: utf-8 -*-
"""
去掉题库 JSON 里词组释义的「词组：」前缀（用户诉求：词组的翻译别加"词组"两个字）。

做法：窄字符串替换，只把 meaning 值开头的 "词组：" / "词组:" 前缀删掉，
不重新序列化 JSON —— 保证除该前缀外文件逐字节不变、diff 最小。

运行：python -X utf8 tools/strip_phrase_prefix.py
"""
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')

# 只命中 meaning 值紧跟的「词组：/词组:」前缀，全/半角冒号各一条
NEEDLES = ['"meaning": "词组：', '"meaning": "词组:']
REPL = '"meaning": "'


def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '20*.json')))
    total = 0
    for f in files:
        with open(f, encoding='utf-8') as fp:
            text = fp.read()
        n = sum(text.count(nd) for nd in NEEDLES)
        if not n:
            continue
        for nd in NEEDLES:
            text = text.replace(nd, REPL)
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(text)
        total += n
        print(f'  {os.path.basename(f)}: 去除 {n} 处')
    print(f'完成：共去除 {total} 处「词组：」前缀，覆盖 {len(files)} 个题库文件')


if __name__ == '__main__':
    main()
