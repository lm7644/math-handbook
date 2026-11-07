#!/usr/bin/env python3
# 组装手册：读取 chapters/ch00..ch15.html + 封面/凡例/附录，输出 index.html
# 用法：python3 build.py [theme]   theme ∈ {academic, textbook, minimal} 默认 academic
import re, sys, pathlib

ROOT = pathlib.Path(__file__).parent
CH = ROOT / "chapters"
THEME = sys.argv[1] if len(sys.argv) > 1 else "academic"
if THEME not in ("academic", "textbook", "minimal"):
    THEME = "academic"

def read(p):
    return p.read_text(encoding="utf-8")

# 从章节文件提取元信息（章名/副标题/章内目录）
def chapter_meta(html, num):
    title = re.search(r'<h2 class="ch-title">(.*?)</h2>', html, re.S)
    sub = re.search(r'<p class="ch-sub">(.*?)</p>', html, re.S)
    toc = re.findall(r'<h3 id="(ch\d+-(?:s\d+|ai))"><span class="h3-num">[\d.]+</span>(.*?)</h3>', html, re.S)
    return {
        "num": num,
        "title": re.sub(r'\s+', ' ', title.group(1)).strip() if title else f"第{num}章",
        "sub": re.sub(r'\s+', ' ', sub.group(1)).strip() if sub else "",
        "toc": [(tid, re.sub(r'\s+', ' ', t).strip()) for tid, t in toc],
    }

CH_LABEL = ["第零章","第一章","第二章","第三章","第四章","第五章","第六章","第七章",
            "第八章","第九章","第十章","第十一章","第十二章","第十三章","第十四章","第十五章"]

chapters = []
for i in range(16):
    f = CH / f"ch{i:02d}.html"
    html = read(f)
    m = chapter_meta(html, f"{i:02d}")
    m["html"] = html
    m["label"] = CH_LABEL[i]
    chapters.append(m)

# 短名取「：」前；无「：」用全名
def short_name(t): return t.split("：")[0] if "：" in t else t

# ---------- 侧边导航 ----------
nav_items = "\n".join(
    f'<li><a href="#ch{c["num"]}" data-nav="ch{c["num"]}"><span class="n">{c["num"]}</span><span class="nt">{c["title"]}</span><span class="ns">{short_name(c["title"])}</span></a></li>'
    for c in chapters
)

# ---------- 总目录页 ----------
toc_rows = "\n".join(
    f'''<a class="toc-row" href="#ch{c["num"]}">
      <span class="toc-num">{c["num"]}</span>
      <span class="toc-body"><span class="toc-title">{c["title"]}</span>
      {f'<span class="toc-sub">{c["sub"]}</span>' if c["sub"] else '<span class="toc-sub toc-sub-none">（目录原图无副标题）</span>'}</span>
    </a>'''
    for c in chapters
)

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

# ---------- 叙述流引用：灰线地址样式（非链接，闭合档案体系） ----------
def _ghost_refs(h):
    store = []
    def stash(m):
        store.append(m.group(0)); return f"\x00{len(store)-1}\x00"
    h = re.sub(r'<code>.*?</code>', stash, h, flags=re.S)
    h = re.sub(r'<pre>.*?</pre>', stash, h, flags=re.S)
    h = re.sub(r'<a [^>]*>.*?</a>', stash, h, flags=re.S)
    h = re.sub(r'<figcaption>.*?</figcaption>', stash, h, flags=re.S)
    h = re.sub(r'<span class="box-tag">.*?</span>', stash, h, flags=re.S)
    h = re.sub(r'式\s*[（(](\d{1,2}\.\d{1,2})[）)]', r'<span class="ref">式 (\1)</span>', h)
    h = re.sub(r'图\s*(\d{1,2}\.\d{1,2})', r'<span class="ref">图 \1</span>', h)
    h = re.sub(r'例\s*(\d{1,2}\.\d{1,2})', r'<span class="ref">例 \1</span>', h)
    for i, frag in enumerate(store):
        h = h.replace(f"\x00{i}\x00", frag)
    return h

for c in chapters:
    c["html"] = _ghost_refs(c["html"])

# ---------- 正文拼接：每章前插页眉 ----------
body_parts = []
for c in chapters:
    running = f'{c["label"]}　{c["title"]}'
    body_parts.append(f'<!-- ===== {c["label"]} ===== -->\n<div class="chapter-wrap" id="wrap-ch{c["num"]}" data-running="{running}">\n{c["html"]}\n</div>')
body = "\n\n".join(body_parts)

# 每章命名页：打印页眉随章变化
print_pages = []
for c in chapters:
    hdr = f'{c["label"]} · {short_name(c["title"])}'
    print_pages.append(
        f'@page pgc{c["num"]}{{@top-center{{content:"{hdr}";font-family:Menlo,monospace;font-size:8.5pt;color:#666;letter-spacing:.05em}}}}\n'
        f'  #wrap-ch{c["num"]}{{page:pgc{c["num"]}}}')
print_pages_css = "\n  ".join(print_pages)

PAGE = read(ROOT / "_template.html")
PAGE = PAGE.replace("__PRINT_PAGES__", print_pages_css)
PAGE = PAGE.replace("__NAV__", nav_items)
PAGE = PAGE.replace("__TOC_ROWS__", toc_rows)
PAGE = PAGE.replace("__BODY__", body)
PAGE = PAGE.replace("__THEME__", THEME)
# ---------- 硬检查：输出含未完成标记则构建失败 ----------
_hits = [m for m in re.finditer(r"待核|TODO|FIXME|XXX", PAGE)]
if _hits:
    for m in _hits[:20]:
        i = m.start()
        ch = PAGE.rfind('id="wrap-ch', 0, i)
        loc = PAGE[ch + 11:ch + 13] if ch >= 0 else "封面/模板区"
        print(f"构建失败：发现未完成标记 {m.group(0)!r}（章 {loc}）上下文：{PAGE[max(0,i-40):i+40]!r}")
    sys.exit(1)

(ROOT / "index.html").write_text(PAGE, encoding="utf-8")
print(f"built index.html  theme={THEME}  chapters=16  size={len(PAGE)}")
