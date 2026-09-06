"""合并 struct 批次到 pwa/data/{year}.json。
批次支持两种格式:
  1) .py  : DATA = { sid: {"v":1,"nodes":[...]} }
  2) .txt : 大纲行  <深度>|<角色>|<文本>[|lead:引导词][|mod:修饰对象]
            sid 行不带 | ; 深度=节点层级(1起)，工具自动建树
校验: 角色白名单; depth-first 平铺 t(空格归一) == 原句 en
用法: python tools/merge_struct.py <batch file> [--force]
"""
import json, re, sys, os

sys.stdout.reconfigure(encoding='utf-8')
ROLES = {'主语','谓语','宾语','表语','定语','状语','补语','同位语','插入语','举例','并列','并列词','目的状语',
         '定语从句','状语从句','宾语从句','主语从句','表语从句','同位语从句','不定式短语','分词短语',
         '原因状语从句','方式状语从句','条件状语从句','让步状语从句','时间状语从句','地点状语从句',
         '比较状语从句','结果状语从句','目的状语从句',
         '时间状语','地点状语','方式状语','程度状语','原因状语','目的状语','条件状语','让步状语','比较状语','结果状语'}

# 各文件 JSON 缩进（写回必须匹配原格式，否则整文件重排）：
# en1 目录全部 indent=1；en2 按年份：2007/2008/2009/2024/2026 = 1，其余 = 2
def file_indent(exam, year):
    if exam == 'en1':
        return 1
    return 1 if int(year) in (2007, 2008, 2009, 2024, 2026) else 2
norm = lambda s: re.sub(r'\s+', ' ', s.strip())

def build_from_outline(lines):
    """行: <depth>|<role>|<text>[|lead:..][|mod:..] → 树"""
    DATA, sid, stack = {}, None, []
    for raw in lines:
        line = raw.rstrip('\n')
        if not line.strip() or line.strip().startswith('#'):
            continue
        if '|' not in line:
            sid = line.strip()
            DATA[sid] = {'v': 1, 'nodes': []}
            stack = []
            continue
        parts = line.split('|')
        depth = int(parts[0].strip())
        node = {'r': parts[1].strip(), 't': parts[2].strip()}
        for extra in parts[3:]:
            extra = extra.strip()
            if extra.lower().startswith('lead:'):
                node['lead'] = extra[5:].strip()
            elif extra.lower().startswith('mod:'):
                node['mod'] = extra[4:].strip()
        if node['r'] not in ROLES:
            raise ValueError(f'{sid}: 角色越界 {node["r"]!r}')
        if not node['t']:
            raise ValueError(f'{sid}: 空 t ({node["r"]})')
        entry = DATA[sid]['nodes']
        if depth == 1:
            entry.append(node); stack = [node]
        else:
            if depth > len(stack) + 1:
                raise ValueError(f'{sid}: 深度跳级 {depth} (当前栈 {len(stack)})')
            stack[depth - 2].setdefault('nodes', []).append(node)
            stack = stack[:depth - 1] + [node]
    return DATA

def flatten(nodes, out):
    for n in nodes:
        bad = [k for k in n if k not in ('r','t','lead','mod','nodes','v')]
        if bad: raise ValueError(f'非法字段 {bad} in {n.get("r")}')
        if n.get('r') not in ROLES: raise ValueError(f'角色越界: {n.get("r")!r}')
        if not n.get('t'): raise ValueError(f'空 t in {n.get("r")}')
        out.append(n['t'])
        if n.get('nodes'): flatten(n['nodes'], out)

def load_batch(path):
    if path.endswith('.txt'):
        return build_from_outline(open(path, encoding='utf-8').readlines())
    ns = {}
    exec(open(path, encoding='utf-8').read(), ns)
    return ns['DATA']

def year_of(sid):
    """en1_2024_text1_s01 → ('en1','2024'); 2024_text1_s01 → ('en2','2024')"""
    m = re.match(r'(en1)_(\d{4})_', sid)
    if m: return (m.group(1), m.group(2))
    m = re.match(r'(\d{4})_', sid)
    if m: return ('en2', m.group(1))
    raise ValueError(f'无法从 sid 解析年份: {sid}')

def main(batch_path, force=False):
    DATA = load_batch(batch_path)
    byfile = {}
    for sid in DATA:
        exam, year = year_of(sid)
        byfile.setdefault((exam, year), []).append(sid)
    ok = fail = skip = 0
    for (exam, year), sids in byfile.items():
        p = os.path.join('pwa/data', exam, f'{year}.json') if exam == 'en1' else os.path.join('pwa/data', f'{year}.json')
        d = json.load(open(p, encoding='utf-8'))
        smap = {s['id']: s for a in d.get('articles', []) for s in a.get('sentences', [])}
        for sid in sids:
            s = smap.get(sid)
            if not s: print(f'✗ {sid}: 数据中不存在'); fail += 1; continue
            if s.get('struct') and not force: print(f'- {sid}: 已有 struct，跳过'); skip += 1; continue
            st = DATA[sid]
            try:
                out = []
                flatten(st['nodes'], out)
                # 贴连感知 join：段以破折号(—)开头/结尾时与前段不插空格（支持 workforce—which…—will 等原句贴连）
                got = ''
                for t in out:
                    t = str(t).strip()
                    if not t:
                        continue
                    if got and (got.endswith('\u2014') or t.startswith('\u2014')):
                        got += t
                    else:
                        got += (' ' if got else '') + t
                if norm(got) != norm(s['en']):
                    exp, g = norm(s['en']), norm(got)
                    i = 0
                    while i < min(len(exp), len(g)) and exp[i] == g[i]: i += 1
                    raise ValueError(f'平铺还原不符@{i}\n  期望: ...{exp[max(0,i-25):i+35]}\n  实得: ...{g[max(0,i-25):i+35]}')
            except ValueError as e:
                print(f'✗ {sid}: {e}'); fail += 1; continue
            s['struct'] = {'v': 1, 'nodes': st['nodes']}
            ok += 1
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=file_indent(exam, year))
    print(f'\n结果: 成功 {ok} / 失败 {fail} / 跳过 {skip}')
    sys.exit(1 if fail else 0)

if __name__ == '__main__':
    force = '--force' in sys.argv
    batch = next(a for a in sys.argv[1:] if not a.startswith('--'))
    main(batch, force)
