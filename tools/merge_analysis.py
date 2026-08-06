# -*- coding: utf-8 -*-
"""
把 _analysis_{year}.json 合并进对应年份 extra 的作文 writing_analysis 字段。

_analysis_{year}.json 格式：
{
  "2010_writinga": {"prompt": "...", "framework": "...", "template": "..."},
  "2010_writingb": {"prompt": "...", "framework": "...", "template": "..."}
}

- prompt: 审题/解读要点（小作文=指令关键词解读；大作文=图表分析+行文思路）
- framework: 思路框架（整篇写作结构）
- template: 应用模板（可套用的英文模板 + 适用说明）

运行：python -X utf8 tools/merge_analysis.py
"""
import json
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES = os.path.join(ROOT, 'tools', 'extracted', 'modules')


def main():
    files = sorted(glob.glob(os.path.join(MODULES, '_analysis_*.json')))
    if not files:
        print('未找到 _analysis_*.json')
        return
    total = 0
    for f in files:
        year = os.path.basename(f).replace('_analysis_', '').replace('.json', '')
        extra_path = os.path.join(MODULES, f'{year}_extra.json')
        if not os.path.exists(extra_path):
            print(f'⚠ 缺 {year}_extra.json，跳过')
            continue
        ana = json.load(open(f, encoding='utf-8'))
        extra = json.load(open(extra_path, encoding='utf-8'))
        by_id = {a['id']: a for a in extra['articles']}
        cnt = 0
        for aid, val in ana.items():
            if aid in by_id and val:
                by_id[aid]['writing_analysis'] = val
                cnt += 1
        json.dump(extra, open(extra_path, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        print(f'{year}: 写入 {cnt} 篇')
        total += cnt
    print(f'共写入 {total} 篇作文解析')


if __name__ == '__main__':
    main()
