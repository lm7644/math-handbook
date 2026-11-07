#!/usr/bin/env python3
# 生成 tb08 术语索引节：扫描 tb/*.html 的 <span class="kt"> 首现处，写入 tb08.html §8.6（幂等）
import re, pathlib, html as htmllib

ROOT = pathlib.Path(__file__).parent
TB = ROOT / "tb"

terms = {}  # term -> (chapter_num, sec_id, sec_num, sec_title)
for i in range(16):
    f = TB / f"tb{i:02d}.html"
    if not f.exists(): continue
    s = f.read_text(encoding="utf-8")
    # 按 h3 节切分
    parts = list(re.finditer(r'<h3 id="(tb\d+-(?:s\d+|ai))"><span class="h3-num">([\d.]+)</span>(.*?)</h3>', s))
    for m in re.finditer(r'<span class="kt">([^<]{1,30})</span>', s):
        term = m.group(1).strip()
        if term in terms: continue
        sec = None
        for h in parts:
            if h.start() < m.start(): sec = h
            else: break
        if sec:
            terms[term] = (i, sec.group(1), sec.group(2), re.sub(r'\s+', ' ', sec.group(3)).strip())

# 按术语拼音首字母分组太复杂——按章分组列出
by_ch = {}
for t, (i, sid, snum, stitle) in terms.items():
    by_ch.setdefault(i, []).append((t, sid, snum, stitle))

rows = []
for i in sorted(by_ch):
    items = "；".join(
        f'<a class="xref" href="#{sid}">{htmllib.escape(t)}</a><span class="ti-sec">({snum})</span>'
        for t, sid, snum, stitle in sorted(by_ch[i], key=lambda x: x[2]))
    rows.append(f'<tr><td>第{i:02d}章</td><td>{items}</td></tr>')

section = f'''
  <h3 id="tb08-s6"><span class="h3-num">8.6</span> 术语索引</h3>
  <p>全书 <span class="kt">关键术语</span>（正文加粗标记者）的首见位置，按章归组，点击词条跳到定义处；共 {len(terms)} 条。符号（字母）请查 8.1 的符号总表，公式请查 8.2 的速查表。</p>
  <table class="tbl ti-table"><thead><tr><th>章</th><th>术语（首见节）</th></tr></thead><tbody>
  {chr(10).join(rows)}
  </tbody></table>
'''

f = TB / "tb08.html"
s = f.read_text(encoding="utf-8")
# 幂等：若已有 8.6 节则先移除旧版
s = re.sub(r'\n?\s*<h3 id="tb08-s6">.*?(?=<h3 id="tb08-|</section>)', '\n', s, flags=re.S)
s = re.sub(r'(</section>\s*)$', section + r'\1', s)
f.write_text(s, encoding="utf-8")
print(f"术语索引: {len(terms)} 条, 覆盖 {len(by_ch)} 章 → tb08 §8.6")
