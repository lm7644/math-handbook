#!/usr/bin/env python3
# 组装教科书版：读 tb/tb00..tb15.html → textbook.html（现代教科书主题，含专属组件样式）
import re, pathlib, sys

ROOT = pathlib.Path(__file__).parent
TB = ROOT / "tb"
CH_LABEL = ["第零章","第一章","第二章","第三章","第四章","第五章","第六章","第七章",
            "第八章","第九章","第十章","第十一章","第十二章","第十三章","第十四章","第十五章"]

def read(p): return p.read_text(encoding="utf-8")

def meta(html, num):
    title = re.search(r'<h2 class="ch-title">(.*?)</h2>', html, re.S)
    sub = re.search(r'<p class="ch-sub">(.*?)</p>', html, re.S)
    return (re.sub(r'\s+',' ',title.group(1)).strip() if title else f"第{num}章",
            re.sub(r'\s+',' ',sub.group(1)).strip() if sub else "")

chapters=[]
for i in range(16):
    f=TB/f"tb{i:02d}.html"
    if not f.exists():
        print(f"缺 tb{i:02d}.html"); continue
    h=read(f); t,s=meta(h,f"{i:02d}")
    chapters.append({"num":f"{i:02d}","label":CH_LABEL[i],"title":t,"sub":s,"html":h})

# 短名取「：」前；无「：」用全名
def short_name(t): return t.split("：")[0] if "：" in t else t

nav="\n".join(f'<li><a href="#tb{c["num"]}" data-nav="tb{c["num"]}"><span class="n">{c["num"]}</span><span class="nt">{c["title"]}</span><span class="ns">{short_name(c["title"])}</span></a></li>' for c in chapters)
toc_rows="\n".join(
    f'''<a class="toc-row" href="#tb{c["num"]}"><span class="toc-num">{c["num"]}</span>
    <span class="toc-body"><span class="toc-title">{c["title"]}</span>
    {f'<span class="toc-sub">{c["sub"]}</span>' if c["sub"] else '<span class="toc-sub toc-sub-none">（目录原图无副标题）</span>'}</span></a>'''
    for c in chapters)
# ---------- 交叉引用链接化 ----------
# 1) 建立全书锚点映射（式 eq-n-m / 图 fig-n-m / 例 ex-n-m）
eq_map, fig_map, ex_map = {}, {}, {}
for c in chapters:
    for m in re.finditer(r'\\tag\{(\d+)\.(\d+)\}', c["html"]):
        eq_map[f"{m.group(1)}.{m.group(2)}"] = f"eq-{m.group(1)}-{m.group(2)}"
    for m in re.finditer(r'<figcaption>图\s*(\d+)\.(\d+)', c["html"]):
        fig_map[f"{m.group(1)}.{m.group(2)}"] = f"fig-{m.group(1)}-{m.group(2)}"
    for m in re.finditer(r'<span class="box-tag">例\s*(\d+)\.(\d+)', c["html"]):
        ex_map[f"{m.group(1)}.{m.group(2)}"] = f"ex-{m.group(1)}-{m.group(2)}"

# 2) 锚点注入：在目标元素上补 id（display 公式前插空锚点；figure/example 补 id 属性）
def _insert_id(h, pos, idattr):
    return h[:pos] + idattr + h[pos:]

for c in chapters:
    h = c["html"]
    ins = []  # (pos, text) 倒序应用
    for m in re.finditer(r'\\\[(?:(?!\\\]).)*?\\tag\{(\d+)\.(\d+)\}(?:(?!\\\]).)*?\\\]', h, re.S):
        ins.append((m.start(), f'<span id="eq-{m.group(1)}-{m.group(2)}" class="anchor"></span>'))
    for m in re.finditer(r'<figcaption>图\s*(\d+)\.(\d+)', h):
        fp = h.rfind('<figure class="fig">', 0, m.start())
        if fp >= 0:
            ins.append((fp, f'<figure class="fig" id="fig-{m.group(1)}-{m.group(2)}">'))
            ins.append((fp + len('<figure class="fig">'), ''))
    for m in re.finditer(r'<span class="box-tag">例\s*(\d+)\.(\d+)', h):
        dp = h.rfind('<div class="example">', 0, m.start())
        if dp >= 0:
            ins.append((dp, f'<div class="example" id="ex-{m.group(1)}-{m.group(2)}">'))
            ins.append((dp + len('<div class="example">'), ''))
    # 去重（figure/example 可能多次匹配同一位置）并按倒序应用
    seen = set(); ops = []
    for pos, txt in sorted(ins, key=lambda x: -x[0]):
        if txt and (pos, txt) not in seen:
            seen.add((pos, txt)); ops.append((pos, txt))
    # figure/example 的替换是「整段替换开标签」，特殊处理
    for pos, txt in ops:
        if txt.startswith('<figure'):
            h = h[:pos] + txt + h[pos + len('<figure class="fig">'):]
        elif txt.startswith('<div class="example"'):
            h = h[:pos] + txt + h[pos + len('<div class="example">'):]
        else:
            h = h[:pos] + txt + h[pos:]
    c["html"] = h

# 3) 链接化（保护 code/pre/a/figcaption/box-tag 后做文本替换）
def _protect(h):
    store = []
    def stash(m):
        store.append(m.group(0)); return f"\x00{len(store)-1}\x00"
    h = re.sub(r'<code>.*?</code>', stash, h, flags=re.S)
    h = re.sub(r'<pre>.*?</pre>', stash, h, flags=re.S)
    h = re.sub(r'<a [^>]*>.*?</a>', stash, h, flags=re.S)
    h = re.sub(r'<figcaption>.*?</figcaption>', stash, h, flags=re.S)
    h = re.sub(r'<span class="box-tag">.*?</span>', stash, h, flags=re.S)
    return h, store

_xref_stats = {"式": 0, "图": 0, "例": 0, "章": 0, "miss": []}

def _eq_link(m):
    k = f"{m.group(1)}.{m.group(2)}"
    if k in eq_map:
        _xref_stats["式"] += 1
        return f'式 (<a class="xref" href="#{eq_map[k]}">{k}</a>)'
    _xref_stats["miss"].append("式" + k); return m.group(0)

def _fig_link(m):
    k = f"{m.group(1)}.{m.group(2)}"
    if k in fig_map:
        _xref_stats["图"] += 1
        return f'图 <a class="xref" href="#{fig_map[k]}">{k}</a>'
    _xref_stats["miss"].append("图" + k); return m.group(0)

def _ex_link(m):
    k = f"{m.group(1)}.{m.group(2)}"
    if k in ex_map:
        _xref_stats["例"] += 1
        return f'例 <a class="xref" href="#{ex_map[k]}">{k}</a>'
    _xref_stats["miss"].append("例" + k); return m.group(0)

def _ch_link(m):
    lbl = "第" + m.group(1) + "章"
    if lbl in CH_LABEL:
        _xref_stats["章"] += 1
        return f'<a class="xref" href="#tb{CH_LABEL.index(lbl):02d}">{lbl}</a>'
    return m.group(0)

for c in chapters:
    h, store = _protect(c["html"])
    h = re.sub(r'式\s*[（(](\d{1,2})\.(\d{1,2})[）)]', _eq_link, h)
    h = re.sub(r'图\s*(\d{1,2})\.(\d{1,2})', _fig_link, h)
    h = re.sub(r'例\s*(\d{1,2})\.(\d{1,2})', _ex_link, h)
    h = re.sub(r'第(零|一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五)章', _ch_link, h)
    for i, frag in enumerate(store):
        h = h.replace(f"\x00{i}\x00", frag)
    c["html"] = h

print(f"xref: 式={_xref_stats['式']} 图={_xref_stats['图']} 例={_xref_stats['例']} 章={_xref_stats['章']} miss={len(_xref_stats['miss'])}")
if _xref_stats["miss"]:
    print("miss:", _xref_stats["miss"][:10])

# ---------- 档案卡凸耳：box-tag 拆分为「编号凸耳 + 标签」 ----------
_TAGNUM = re.compile(r'<span class="box-tag">((?:定义|结论|例|约定|记号|假设|引理|推论|定理|命题|性质|备注)\s*(\d+\.\d+))([^<]*)</span>')
_TAGANY = re.compile(r'<span class="box-tag">([^<]+)</span>')

def _card_tabs(h):
    def numbered(m):
        full, num, rest = m.group(1), m.group(2), m.group(3)
        label = full.replace(num, "", 1).strip()
        return (f'<span class="box-tag"><span class="ctab">{num}</span>'
                f'<span class="clabel">{label}{rest.strip()}</span></span>')
    h = _TAGNUM.sub(numbered, h)
    def bare(m):
        inner = m.group(1).strip()
        if "·" in inner:
            head, tail = inner.split("·", 1)
            head, tail = head.strip(), tail.strip()
        else:
            head, tail = inner, ""
        return (f'<span class="box-tag bare"><span class="ctab">{head}</span>'
                f'<span class="clabel">{tail}</span></span>')
    h = _TAGANY.sub(bare, h)
    return h

for c in chapters:
    c["html"] = _card_tabs(c["html"])

body="\n\n".join(f'<div class="chapter-wrap" id="wrap-tb{c["num"]}" data-running="{c["label"]}　{c["title"]}（教科书版）">\n{c["html"]}\n</div>' for c in chapters)

# 每章命名页：打印页眉随章变化
print_pages_css = "\n  ".join(
    f'@page pgt{c["num"]}{{@top-center{{content:"{c["label"]} · {short_name(c["title"])}";font-family:Menlo,monospace;font-size:8.5pt;color:#666;letter-spacing:.05em}}}}\n'
    f'  #wrap-tb{c["num"]}{{page:pgt{c["num"]}}}'
    for c in chapters)

tpl=read(ROOT/"_template_textbook.html")
tpl=tpl.replace("__PRINT_PAGES__",print_pages_css).replace("__NAV__",nav).replace("__TOC_ROWS__",toc_rows).replace("__BODY__",body)
# ---------- 硬检查：输出含未完成标记则构建失败 ----------
_hits = [m for m in re.finditer(r"待核|TODO|FIXME|XXX", tpl)]
if _hits:
    for m in _hits[:20]:
        i = m.start()
        ch = tpl.rfind('id="wrap-tb', 0, i)
        loc = tpl[ch + 11:ch + 13] if ch >= 0 else "封面/模板区"
        print(f"构建失败：发现未完成标记 {m.group(0)!r}（章 {loc}）上下文：{tpl[max(0,i-40):i+40]!r}")
    sys.exit(1)

(ROOT/"textbook.html").write_text(tpl,encoding="utf-8")
print(f"built textbook.html  chapters={len(chapters)}  size={len(tpl)}")
