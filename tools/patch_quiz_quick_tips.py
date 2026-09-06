# -*- coding: utf-8 -*-
"""给全部英二阅读题生成「考题速览 quick」+「技巧 tip」（2007-2026，约 397 题）。
- 已有 quick/tip 的题（如 2021_text3 手写版）跳过不覆盖。
- 2007-2009 老题无 qtype/stem_cn：按题干特征自动分类题型，quick 只写题型名。
- 其余年份：quick = 题型中文名 + '：' + stem_cn；tip = 题型技巧库。
- 各文件按原缩进写回，避免重排（缩进 map 已普查）。
"""
import json, glob, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = 'pwa/data/'

INDENT = {2007: 1, 2008: 1, 2009: 1, 2024: 1, 2026: 1}  # 其余 2

# ============ 题型中文名映射 ============
QTYPE_CN = {
    'detail': '事实细节', 'viewpoint': '人物观点', 'opinion': '人物观点',
    'inference': '事实推断', '推理题': '推理题', '细节题': '细节题',
    'main_idea': '主旨大意', '主旨题': '主旨大意', 'attitude': '态度题', '态度题': '态度题',
    'vocabulary': '词义题', '词义题': '词义题', 'example': '例证题',
    '句意题': '句意题', '判断': '判断',
}

# ============ 题型技巧库（纯通用规律，不带题目细节） ============
TIPS = {
    '事实细节': '事实细节题：答案必为原文同义改写——先定位题干关键词所在句（含前后句），警惕张冠李戴（偷换主语）与断章取义。',
    '人物观点': '人物观点题：只认此人（或该群体）说过的话——答案必须有他/她/他们本人的直接或间接表述作依据；他人、机构的观点即使文中属实，也只是干扰项。',
    '事实推断': '推断题：答案必有原文事实依据——由信息合理推出即可，禁止无中生有、绝对化（all / never）与原文相悖。',
    '推理题': '推断题：答案必有原文事实依据——由信息合理推出即可，禁止无中生有、绝对化（all / never）与原文相悖。',
    '主旨大意': '主旨题：看首尾段 ＋ 各段首句的重复话题词；正确项是全文整体概括，干扰项多为局部细节（以偏概全）、过度拔高或与主旨相反。',
    '态度题': '态度题：答案 = 作者的“态度词”——找评价性形容词/副词与转折词后的立场；中性项（indifferent / objective 等）常是干扰，作者完全中立少见。',
    '词义题': '词义题：本义 / 常义多为干扰——答案看上下文逻辑（并列 / 转折 / 因果 / 举例），把四个选项代回原句验证语义通顺且与主旨一致。',
    '例证题': '例证题：例子本身不是答案——问例子的目的时，答案在其前的论点句或之后的总结句（论点先行或尾随）。',
    '句意题': '句意题：表层含义不选——答案需结合该句在段落中的作用（承上启下 / 观点句），常为段内同义改写。',
    '判断': '判断题：逐项回原文定位比对，重点核对主语、时态、程度词（all / most / some），张冠李戴与偷换程度是高频干扰。',
}

DEFAULT_TIP = '先读题干找关键词 → 回原文定位句（含前后句）→ 比对选项：答案常为原文同义改写；排除无中生有、偷换概念、以偏概全。'

# ============ 2007-2009 题干自动分类 ============
def cls_from_stem(stem):
    s = (stem or '').lower()
    if re.search(r'(attitude|author.s attitude|author holds|opinion of the author)', s): return 'attitude'
    if re.search(r'(closest in meaning|\bword\b |\bphrase\b |\bterm\b | most probably mean)', s): return 'vocabulary'
    if re.search(r'(best title|most appropriate title|best summarizes|main idea|primarily about|primarily concerned|intends to tell|summarize)', s): return 'main_idea'
    if re.search(r'(cited as an example|example to|is mentioned (as|to)|the case of|the story of .*? shows)', s): return 'example'
    if re.search(r'(we can infer|it can be inferred|suggest(s|ed)? that|imply|conclude|indicate|we learn|learn from)', s): return 'inference'
    if re.search(r'(believe|believed|agree|according to [a-z]|holds? that|held that|view|argue|pointed out|says|said)', s): return 'viewpoint'
    return 'detail'

def qtype_cn(q):
    t = q.get('qtype')
    if t:
        return QTYPE_CN.get(t, t)
    return QTYPE_CN.get(cls_from_stem(q.get('stem', '')) or 'detail', '细节题')

def tip_for(q):
    return TIPS.get(qtype_cn(q), DEFAULT_TIP)

def quick_for(q):
    cn = qtype_cn(q)
    stem_cn = q.get('stem_cn')
    if stem_cn:
        return f'{cn}：{stem_cn}'.replace('？？', '？')
    return cn

# ============ 主流程 ============
def main():
    changed_files = []
    total_q = added_q = skipped_q = 0
    for p in sorted(glob.glob(BASE + '*.json')):
        y = os.path.basename(p).split('.')[0]
        if not y.isdigit() or int(y) < 2007:
            continue
        d = json.load(open(p, encoding='utf-8'))
        touched = False
        for a in d.get('articles', []):
            if not isinstance(a, dict) or not str(a.get('type', '')).startswith('text'):
                continue
            for q in a.get('questions', []):
                if not isinstance(q, dict):
                    continue
                total_q += 1
                if not q.get('qtype'):
                    q['qtype'] = cls_from_stem(q.get('stem', ''))  # 老题补题型（badge 显示用）
                    touched = True
                if q.get('quick') and q.get('tip'):
                    skipped_q += 1
                    continue
                q['quick'] = quick_for(q)
                q['tip'] = tip_for(q)
                added_q += 1
                touched = True
        if touched:
            indent = INDENT.get(int(y), 2)
            json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=indent)
            changed_files.append(os.path.basename(p))
    print(f'总阅读题 {total_q} | 新增 quick/tip {added_q} | 跳过已有 {skipped_q}')
    print('改动文件:', changed_files)

if __name__ == '__main__':
    main()