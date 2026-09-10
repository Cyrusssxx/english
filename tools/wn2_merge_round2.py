# -*- coding: utf-8 -*-
"""合并本轮 5 个判义代理 + 3 个短语筛选代理的结果"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
TOOLS = 'tools'

WORDS = [
    # (词, 僻义, 档位, 例句 sid)  —— 5 个判义代理（0~1205 段）
    ('article', 'n. 物品；用品（配发的物资）', '高', '2012_cloze_s05'),
    ('content', 'a. 满足的，甘愿的', '高', '2017_newtype_s30'),
    ('peer', 'v. 凝视，端详', '高', '2010_newtype_s17'),
    ('stress', 'n. 强调，重视', '中', '2017_text1_s20'),
    ('express', 'a. 明确的，清楚的（express claims）', '中', '2024_text4_s09'),
    ('respect', 'n. 方面，点（in limited respects）', '中', '2012_text4_s06'),
    ('character', 'n. （社会、时代的）特征，性质', '中', '2012_text4_s03'),
    ('brand', 'v. 给……打上（污名）烙印', '中', '2013_text2_s08'),
    ('print', 'n. 印刷品，纸媒', '中', 'en1_2016_text4_s05'),
    ('capital', 'n. 资本，资金', '中', '2017_cloze_s03'),
    ('grant', 'v. 视……为理所当然（take for granted）', '中', '2011_text3_s09'),
    ('formation', 'n. 队形，编队', '中', '2010_newtype_s05'),
    ('jump', 'n. 猛增，激增', '中', '2015_text4_s06'),
    ('premium', 'a. 优质的，高级的', '中', '2023_cloze_s11'),
    ('stage', 'v. 举办，上演，筹划', '中', '2026_text4_s02'),
    ('credit', 'n. 学分；认可，功劳', '中', '2017_text3_s14'),
    ('thin', 'a. 微薄的，稀少的', '低', '2012_text4_s08'),
    ('spring', 'n. 泉水', '中', '2010_text3_s10'),
    ('volume', 'n. 量，大量', '中', '2016_translation_s05'),
    ('snap', 'a. 仓促的，下意识的（snap decisions）', '中', '2013_text3_s02'),
    ('saw', 'v. 见证，经历（see 的过去式）', '中', '2025_translation_s09'),
    ('engagement', 'n. 参与；参与度', '中', '2026_text2_s15'),
    ('bottom', 'n. 实质，本质（at bottom）', '中', '2012_newtype_s01'),
    ('curious', 'a. 奇怪的，奇特的', '中', '2018_text1_s01'),
    ('trick', 'n. 诀窍，窍门', '低', '2021_cloze_s40'),
    ('awkward', 'a. 尴尬的，令人窘迫的', '低', '2025_translation_s02'),
    ('original', 'n. 原作，真迹', '中', '2014_text2_s08'),
    ('wisdom', 'n. 普遍看法，公认观点', '中', '2015_text1_s03'),
    ('below', 'n. 底层，下层（from below）', '中', '2012_newtype_s26'),
    ('index', 'n. 指数，指标', '中', '2014_cloze_s07'),
    ('lean', 'a. 贫乏的，艰难的（lean times）', '中', '2012_text4_s15'),
    ('blank', 'a. 茫然的，无表情的', '中', '2017_text2_s10'),
    ('secretary', 'n. （英国）大臣，部长', '高', '2011_newtype_s02'),
    ('rein', 'v. 控制，约束（rein in）', '中', '2019_text4_s20'),
    ('sole', 'a. 唯一的，仅有的', '中', '2016_text1_s16'),
    ('compensation', 'n. 薪酬，报酬', '中', '2011_text1_s03'),
    ('ritual', 'n. 惯例，习俗', '低', '2012_text1_s02'),
    ('broken', 'a. 失灵的，积弊深重的（broken system）', '低', '2013_text2_s09'),
    ('sadly', 'adv. 遗憾的是（作评注性状语）', '低', '2011_text2_s18'),
]

# 同族/近义重复：已有更合适词条，不重复收
DUP = {'argue', 'buys', 'dismissed'}

PHRASES = [
    # (短语, 释义, 类别) —— 3 个短语筛选代理（0~1200 段）
    ('all but', '除……之外全部', '商业经济'),
    ('cross section', '（社会的）横断面；各阶层代表', '政法'),
    ('under fire', '受到抨击；遭到批评', '商业经济'),
    ('trade up', '越换越好；另谋高就', '商业经济'),
    ('shrugged off', '对……不予理会；摆脱', '商业经济'),
    ('stayed afloat', '维持经营；免于破产', '商业经济'),
    ('pushing journalists overboard', '把记者推下船（喻大举裁员）', '商业经济'),
    ('take for granted', '认为理所当然', '教育文化历史'),
    ('make it', '成功；渡过难关', '商业经济'),
    ('quick fix', '权宜之计；临时凑合的办法', '商业经济'),
    ('write off', '认定……失败；一笔勾销', '商业经济'),
    ('put on hold', '暂缓；搁置', '教育文化历史'),
    ('came into its own', '大放异彩；进入全盛期', '社会生活'),
    ('connecting the dots', '串联线索；看清内在联系', '政法'),
    ('shifting landscape', '不断变化的局面；形势', '政法'),
    ('find silver linings', '寻找（困境中的）一线希望', '社会生活'),
    ('better off', '境况更好；更宽裕', '社会生活'),
    ('social fabric', '社会结构；社会肌理', '社会生活'),
    ('stand out', '脱颖而出；出众', '商业经济'),
    ('eating jobs', '吞噬工作岗位', '商业经济'),
    ('shed workers', '裁减员工', '商业经济'),
    ('for good', '永久地；一劳永逸地', '政法'),
    ('hail them as', '将……誉为', '政法'),
    ('brand them as', '给……打上（污名）烙印', '政法'),
    ('gray areas', '灰色地带；规则的模糊区', '政法'),
    ('middle ground', '中间立场；折中方案', '政法'),
    ('rise above', '超越；克服（诱惑等）', '科学科技'),
    ('climb the corporate ladder', '在职场步步高升', '商业经济'),
    ('break through the glass ceiling', '打破玻璃天花板（无形晋升障碍）', '商业经济'),
    ('run counter to', '与……背道而驰；相悖', '商业经济'),
    ('soft pressure', '软压力；非强制的劝导', '商业经济'),
    ('in place', '已就绪；已实施到位', '商业经济'),
    ('wears off', '（感觉）逐渐消退', '社会生活'),
    ('creeps in', '悄然出现；渐渐产生', '社会生活'),
    ('wage slaves', '为薪水所困的上班族', '社会生活'),
    ('hot stuff', '了不起的人物；大人物', '科学科技'),
    ('the cream of', '……中的精华；佼佼者', '科学科技'),
    ('eating up', '吞噬；耗尽', '商业经济'),
    ('leave no room for', '不给……留余地', '商业经济'),
    ('shoulder the blame', '承担责任、过错', '政法'),
    ('politically charged', '政治敏感的；引发争议的', '政法'),
    ('face up to', '正视；勇于面对', '政法'),
    ('hold true', '（说法、规律）成立；适用', '社会生活'),
    ('kick back', '放松；休息', '社会生活'),
    ('the home front', '家庭大后方', '社会生活'),
    ('struggle to navigate', '艰难地应付、摸索（复杂局面）', '教育文化历史'),
    ('a big deal', '了不起的事；举足轻重', '商业经济'),
    ('in this together', '同舟共济；共进退', '商业经济'),
    ('have it all', '兼顾一切；拥有一切', '商业经济'),
    ('buy into it', '接受，认同，买账', '商业经济'),
    ('have a long way to go', '仍有很长的路要走；任重道远', '商业经济'),
    ('jobs picture', '就业状况，就业形势', '商业经济'),
    ('a big jump', '大幅增长，激增', '商业经济'),
    ('making ends meet', '收支相抵；勉强维持生计', '商业经济'),
    ('packed to the brim', '挤得满满的', '教育文化历史'),
    ('remain in the driver\'s seat', '处于掌控、主导地位', '政法'),
    ('goes too far', '做得太过分，太过火', '政法'),
    ('slot it in', '把……安插、安排进去', '教育文化历史'),
    ('fuel the efficiency mind-set', '助长效率至上的思维', '教育文化历史'),
    ('the run-up to', '……的前夕，筹备期', '社会生活'),
    ('making excited bids for', '急切地争取、设法吸引（注意）', '科学科技'),
    ('get some work out of the way', '把……处理完，解决掉', '科学科技'),
    ('lessen the blow', '减轻打击、冲击', '教育文化历史'),
    ('too late in the game', '为时已晚，太迟', '教育文化历史'),
    ('at the expense of', '以……为代价，牺牲', '科学科技'),
    ('tease out', '梳理出，厘清', '科学科技'),
    ('accepted wisdom', '普遍看法，公认观点', '教育文化历史'),
    ('opens more doors', '带来更多机会；打开门路', '教育文化历史'),
    ('staring us in the face', '明摆在眼前，显而易见', '教育文化历史'),
    ('a wake-up call', '警钟，警示', '教育文化历史'),
    ('a quick put-down', '贬损（奚落）之语', '科学科技'),
    ('around the clock', '昼夜不停地', '科学科技'),
    ('the makeup', '（团队等的）组成，构成', '科学科技'),
    ('not so much', '与其说……倒不如说', '科学科技'),
    ('putting a premium on being busy', '高度重视（忙碌）', '商业经济'),
    ('stick to it', '坚持下去', '商业经济'),
    ('a bad rap', '恶名，差评', '社会生活'),
    ('rein in', '抑制，约束', '社会生活'),
    ('turn on', '取决于', '社会生活'),
    ('striking a subtle balance', '达成微妙的平衡', '科学科技'),
    ('figuring out', '弄清楚，想出', '科学科技'),
    ('come to see', '逐渐意识到', '科学科技'),
    ('compounded by', '因……而加剧，雪上加霜', '政法'),
    ('leaving it up to', '把……交给（某人）决定', '政法'),
    ('writing off', '忽视；一笔勾销', '政法'),
    ('putting things into perspective', '客观正确地认识（事物重要性）', '政法'),
    ('upped their game', '提升表现，提高水平', '商业经济'),
    ('ripping people off', '剥削，敲竹杠', '商业经济'),
    ('Far from it', '远非如此，恰恰相反', '政法'),
    ('give or take', '出入，大约（误差范围）', '社会生活'),
    ('hit the streets', '涌入、走上街头（求职等）', '社会生活'),
    ('train wreck', '惨败，灾难', '社会生活'),
    ('let go of', '放弃；解雇', '商业经济'),
    ('gold standard', '标杆，典范', '商业经济'),
    ('from the ground up', '从零开始；彻底地', '商业经济'),
    ('chew up', '蚕食，摧毁', '商业经济'),
    ('placing big bets on', '大力投入，寄予厚望', '科学科技'),
    ('considerable buzz', '热议，高度关注', '商业经济'),
    ('go with', '采纳，采取（策略等）', '商业经济'),
    ('making headlines', '成为新闻焦点，登上头条', '商业经济'),
    ('under way', '在进行中', '科学科技'),
]

# 碎片化的非短语（句子片段），剔除
PH_DROP = {'go home from home', 'the odd 30 minutes', 'what does work', "can't make it academically",
           'making time to read', 'the deal went through', 'change the picture', 'is struck that',
           'gear lessons toward', 'forge closer collaborations', 'jumping off a sinking ship',
           'losing yourself in a book', 'take a magnifying glass to', 'the rest of the equation',
           'turned the country on its political head'}


def main():
    print('=== 单词 ===')
    pool = json.load(open(os.path.join(TOOLS, 'wn2_all_worklist.json'), encoding='utf-8'))
    by = {r['w'].lower(): r for r in pool['rows']}
    dec = json.load(open(os.path.join(TOOLS, 'wn2_decisions.json'), encoding='utf-8'))
    have = {x['w'].lower() for x in dec['words']}
    added, fixed, skipped = 0, [], []
    for w, u, t, sid in WORDS:
        if w.lower() in DUP:
            skipped.append(w + '(同族重复)')
            continue
        r = by.get(w.lower())
        if not r:
            skipped.append(w + '(不在池)')
            continue
        if w.lower() in have:
            skipped.append(w + '(已存在)')
            continue
        if sid not in {o['sid'] for o in r['occ']}:
            alt = [o['sid'] for o in r['occ'] if o['ok']] or [o['sid'] for o in r['occ']]
            fixed.append((w, sid, alt[0] if alt else '无'))
            if not alt:
                skipped.append(w + '(无句)')
                continue
            sid = alt[0]
        dec['words'].append({'w': w, 'uncommon': u, 'tier': t, 'sid': sid, 'sids': [sid]})
        added += 1
    print('入库 %d ｜sid 修正 %s ｜跳过 %s' % (added, fixed, skipped))

    # 标记 1205 词区间为已判（除 keeps）
    done = {x['w'].lower() for x in dec['words']} | {w.lower() for w in dec.get('dropped', [])}
    todo = [r for r in pool['rows'] if r['w'].lower() not in done]
    n = 0
    for r in todo[:1205]:
        dec.setdefault('dropped', []).append(r['w'])
        n += 1
    print('单词标记丢弃 %d' % n)

    print('=== 短语 ===')
    ph = {r['w'].strip().lower(): r for r in json.load(
        open(os.path.join(TOOLS, 'wn2_phrases_worklist.json'), encoding='utf-8'))['rows']}
    have_ph = {x['w'].strip().lower() for x in dec.get('phrases', [])}
    ok, miss = 0, []
    for w, m, c in PHRASES:
        if w in PH_DROP or len(w.split()) > 4:
            dec.setdefault('pdropped', []).append(w)
            continue
        if w.lower() not in ph:
            miss.append(w)
            continue
        if w.lower() in have_ph:
            continue
        dec.setdefault('phrases', []).append({'w': ph[w.lower()]['w'], 'meaning': m, 'cat': c})
        ok += 1
    print('短语入库 %d ｜找不到 %s' % (ok, miss))
    allph = json.load(open(os.path.join(TOOLS, 'wn2_phrases_worklist.json'), encoding='utf-8'))['rows']
    done_ph = {x['w'].strip().lower() for x in dec.get('phrases', [])} | \
              {w.strip().lower() for w in dec.get('pdropped', [])}
    todo_ph = [r for r in allph if r['w'].strip().lower() not in done_ph]
    for r in todo_ph[:1200]:
        dec.setdefault('pdropped', []).append(r['w'])
    print('短语标记丢弃 %d ｜累计已筛 %d' % (min(1200, len(todo_ph)), len(dec['pdropped'])))

    json.dump(dec, open(os.path.join(TOOLS, 'wn2_decisions.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


main()
