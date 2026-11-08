# math-handbook · 大模型数学背景知识手册

[中文](#中文) · [English](#english)

---

## 中文

### 这是什么

一套面向「要做大模型、想补数学」读者的数学参考手册，三个版本同源自建：

- 章节骨架（16 章章名与副标题）照录一篇公众号文章给出的目录图；
- **全部正文为重新撰写**，不是原作者那份 PDF，也不声称与其有关；
- 每个知识点都落到它在大模型里的具体位置（注意力、反向传播、KV Cache……）。

### 三个版本各自适合谁

| 版本 | 文件 | 适合谁 | 篇幅 |
|---|---|---|---|
| 学术版（底版） | `index.html` | 有工程背景、想严谨速通的读者：定义→推导→例子，紧凑密度高；作参照与来源 | 16 章 · 约 100 打印页（284 条展示公式，其中 170 条编号式；51 个例题） |
| 教科书版（主入口） | `textbook.html` | 零基础自学者：更厚、更慢、更细，带术语索引与章内导引 | 16 章 · 约 200 打印页（421 条展示公式，其中 175 条编号式；122 个例题） |
| 速查表（附录） | `textbook.html#cheatsheet` | 临时查证：62 条高频公式按 12 组归类，带出处章回指 | 教科书版末尾附录 |

> 独立的 `cheatsheet.html` 已改为重定向页，访问它会自动跳到教科书版末尾的速查表附录。

### 怎么本地打开

直接双击任一 HTML 文件即可。**无外部依赖**：公式渲染用的 MathJax 已随仓内置（`vendor/tex-svg-full.js`），断网可用。

### 怎么重新构建

只需要 Python 3（纯标准库，无第三方依赖）：

```bash
python3 build.py             # chapters/*.html + _template.html          → index.html
python3 build_textbook.py    # tb/*.html + _template_textbook.html
                             #   + build_cheatsheet.py 的 62 条数据        → textbook.html（含速查表附录）
```

输出与仓内成品逐字节一致（已验证）。`build_cheatsheet.py` 现为速查表数据的维护入口（不再产出独立页面，`cheatsheet.html` 是静态重定向页）；`gen_term_index.py` 是一次性工具：它为 `tb08.html` 生成术语索引节，其结果已包含在仓内 `tb08.html` 中，**重新构建不需要再跑**（重复运行会产生略微不同的索引排序）。

### 目录结构

```
index.html / textbook.html   两份成品（单文件，离线；textbook.html 含速查表附录）
cheatsheet.html              重定向页 → textbook.html#cheatsheet
chapters/    学术版 16 章源文件（ch00–ch15）+ 写作契约
tb/          教科书版 16 章源文件（tb00–tb15）+ 写作契约
_template.html / _template_textbook.html       两个版本的页面模板
build.py / build_textbook.py / build_cheatsheet.py / gen_term_index.py
vendor/tex-svg-full.js                          MathJax（Apache-2.0，见 NOTICE）
```

### 未收录内容及原因

- `assets/`：原公众号文章的封面图、目录图与**联系人二维码**，属第三方素材且含个人联系方式，不适合公开再分发；
- `dossier.html`：对原文的逐字转录档案页，包含第三方推广文全文，公开仓不宜转载。

### 已知边界

- 打印请用浏览器自带打印（macOS `⌘P`），三版均已做打印样式适配；**未内置 PDF 导出**；
- 创新性有限：章节骨架取自公开目录，正文为工程视角的重新整理与推导，目标是准确与可用，不追求学术原创；
- 公式经多轮复核（剩余 0 处待核标记），但内容仅供学习参考，关键场景请以标准教材为准。

### License

- 代码（`build*.py`、`gen_term_index.py`、`_template*.html`）:**MIT**;
- 文档与教材正文（`chapters/`、`tb/`、三份成品 HTML):**CC BY 4.0**;
- `vendor/` 内 MathJax:**Apache-2.0**（详见 `NOTICE`)。

见 `LICENSE` 全文。

---

## English

### What this is

A math reference handbook for readers who build large language models and want to fill in the math. Three editions built from one source tree:

- The 16-chapter skeleton (chapter titles and subtitles) is transcribed from a table of contents published in a WeChat article;
- **All body text is an original rewrite** — this is *not* the original author's PDF and makes no claim to be;
- Every topic is tied to where it is actually used inside LLMs (attention, backprop, KV cache, …).

### Which edition is for you

| Edition | File | For whom | Size |
|---|---|---|---|
| Academic (base) | `index.html` | Engineers who want a rigorous fast track: definitions → derivations → worked examples; the reference edition | 16 chapters · ~100 printed pages (284 display formulas, 170 of them numbered; 51 worked examples) |
| Textbook (main entry) | `textbook.html` | Self-learners starting from zero: slower, thicker, with a term index and guided reading | 16 chapters · ~200 printed pages (421 display formulas, 175 of them numbered; 122 worked examples) |
| Cheatsheet (appendix) | `textbook.html#cheatsheet` | Quick lookup: 62 high-frequency formulas in 12 groups with chapter back-references | Appendix at the end of the textbook edition |

> The standalone `cheatsheet.html` is now a redirect page that jumps to the cheatsheet appendix at the end of the textbook edition.

### Open locally

Double-click any HTML file. **No external dependencies** — MathJax ships with the repo (`vendor/tex-svg-full.js`), so everything works offline.

### Rebuild

Python 3 only (standard library, nothing to install):

```bash
python3 build.py             # chapters/*.html + _template.html          → index.html
python3 build_textbook.py    # tb/*.html + _template_textbook.html
                             #   + the 62 entries in build_cheatsheet.py  → textbook.html (with cheatsheet appendix)
```

Outputs are byte-identical to the files in this repo (verified). `build_cheatsheet.py` is now the maintenance entry for the cheatsheet data (it no longer produces a standalone page; `cheatsheet.html` is a static redirect). `gen_term_index.py` is a one-off tool that generated the term-index section in `tb08.html`; its result is already committed, so **you do not need to run it** for a rebuild (re-running produces a slightly different index ordering).

### Not included, and why

- `assets/`: cover image, TOC image and a **personal contact QR code** from the original WeChat article — third-party material containing personal contact details, not appropriate to redistribute;
- `dossier.html`: an archival page transcribing the full original article — not suitable for republishing.

### Known limits

- Print via the browser (macOS `⌘P`); print styles are built in, but **no built-in PDF export**;
- Limited novelty: the chapter skeleton comes from a public TOC; the value is accuracy and usability, not academic originality;
- Formulas went through multiple review rounds (zero pending-review markers remain), but this is a learning resource — consult standard textbooks for critical work.

### License

- Code (`build*.py`, `gen_term_index.py`, `_template*.html`): **MIT**;
- Content (`chapters/`, `tb/`, the three built HTML files): **CC BY 4.0**;
- MathJax under `vendor/`: **Apache-2.0** (see `NOTICE`).

See `LICENSE` for the full texts.
