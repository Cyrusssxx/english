# -*- coding: utf-8 -*-
"""给「通知 / 介绍信」各补一封场景范文（招募志愿者 / 推荐信）——方案 A，不新增类型、不新增句库。

背景：
  - 第 11 类「会议纪要」当初是手工写进 small_writing.json 的，生成器里没有，
    所以**不能重跑 build_small_writing.py**（会静默丢类型、4 组句库与整信）。
  - 本脚本因此做「定点补丁」：只往 letters.notice / letters.intro 里挂 variants，
    再往 decisions 末尾追加 2 条场景指引；banks / guide / types 一律不动并做哈希断言。
  - 文案真源在 tools/small_writing_extra.py 的 LETTER_VARIANTS / DECISIONS，
    本脚本只负责「把它们塞进已有 JSON」，避免同一段文字两处维护。

场景范文的写法约定：
  - rows 每行仍是 [src, en, cn]，src 保留来源 bank#idx（前端用它自动分段 + 记来源）；
  - 但 en 已把 {{槽位}} 填成具体内容 → 前端判定「与句库原文不同」→ 自动走独立高亮键，
    不会污染句库共享高亮；因此本封是「照抄就能用」的示范，不是新的必背句。
  - 句句都来自已背的句子库，只是换了填法 —— 背诵量 +0。

可重复运行（幂等）：已存在同 id 的 variant 时覆盖更新，decisions 按 q 去重。
"""
import io
import json
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import small_writing_extra as EXTRA          # noqa: E402

JSON_PATH = os.path.join(ROOT, 'pwa', 'data', 'small_writing.json')

SCENE_Q = ('考到「招募志愿者」怎么写？', '考到「推荐信」怎么写？')


def md5(obj):
    return hashlib.md5(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def main():
    data = json.load(io.open(JSON_PATH, encoding='utf-8'))

    letters = data.get('letters') or {}
    for tid in ('notice', 'intro'):
        assert tid in letters, 'letters.%s 不存在' % tid
        assert isinstance(letters[tid], dict) and letters[tid].get('rows'), 'letters.%s 结构异常' % tid

    before = {k: md5(data[k]) for k in ('banks', 'guide', 'types')}
    before_rows = {tid: md5(letters[tid].get('rows')) for tid in ('notice', 'intro')}
    before_cn = {tid: md5(letters[tid].get('cn_paras')) for tid in ('notice', 'intro')}

    # 1) 挂场景范文（幂等：同 id 覆盖）
    for tid, variants in EXTRA.LETTER_VARIANTS.items():
        assert tid in letters, 'LETTER_VARIANTS 指向不存在的类型 %s' % tid
        cur = [v for v in (letters[tid].get('variants') or []) if v.get('id') not in {x['id'] for x in variants}]
        cur.extend(json.loads(json.dumps(variants, ensure_ascii=False)))
        letters[tid]['variants'] = cur

    # 2) 追加场景指引（按 q 去重）
    dec = data.get('decisions') or []
    existing = {d.get('q') for d in dec}
    added = 0
    for d in EXTRA.DECISIONS:
        if d.get('q') in SCENE_Q and d['q'] not in existing:
            dec.append(dict(d))
            added += 1
    data['decisions'] = dec

    # 断言：句库 / 真题表 / 类型表 / 通用整信内容零变化
    for k in ('banks', 'guide', 'types'):
        assert md5(data[k]) == before[k], '%s 被改动！' % k
    for tid in ('notice', 'intro'):
        assert md5(letters[tid].get('rows')) == before_rows[tid], '%s.rows 被改动！' % tid
        assert md5(letters[tid].get('cn_paras')) == before_cn[tid], '%s.cn_paras 被改动！' % tid

    json.dump(data, io.open(JSON_PATH, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)

    # 复核
    chk = json.load(io.open(JSON_PATH, encoding='utf-8'))
    print('decisions: %d 条（本次新增 %d）' % (len(chk['decisions']), added))
    for tid in ('notice', 'intro'):
        for v in chk['letters'][tid].get('variants') or []:
            print('letters.%s.variants[%s] %s: %d 行, cn_paras %d 段'
                  % (tid, v['id'], v['name'], len(v['rows']), len(v['cn_paras'])))
    print('banks/guide/types 未改动 ✓')


if __name__ == '__main__':
    main()
