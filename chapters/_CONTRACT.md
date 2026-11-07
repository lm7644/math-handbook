# 章节写作契约（所有写作代理必读，逐条遵守）

你在为《学大模型需要的数学背景知识手册》写其中若干章。这本手册**依据一篇公众号文章里的 16 章目录重写**——不是原作者的 PDF。读者是「要做大模型、想补数学」的工程背景读者。

## 0. 最高原则

1. **写手册正文**，不是文章评述、不是章节导读。定义 → 符号约定 → 结论 → 推导 → 可算的例子 → 常见误用。
2. **每条公式必须正确**。拿不准的地方在正文中插入标记 `<span class="todo">【待核】</span>` 并说明疑点，**绝不猜**。宁缺毋滥。
3. **必须落在 AI 上**：每个知识点都要答「它在大模型里用在哪」，具体到机制（例：矩阵乘法 → 注意力 $QK^\top$；链式法则 → 反向传播；KL 散度 → RLHF 策略约束）。与 AI 无关的凑页内容一律不写。
4. **每章末尾必须有一节「在 AI 中的位置」**：本章哪些结论用在哪些具体组件，缺了它会出什么故障（例：不知道 log-sum-exp，softmax 在 logits 大时溢出成 NaN）。
5. **删虚**：宁可薄，不注水。公式推一遍能讲清的，不要绕三段话。

## 1. 文件与结构

- 你写的每一章是一个 HTML 片段文件：`chapters/chNN.html`（NN = 00..15，两位数字）。
- **只写片段**：不要 `<html>`/`<head>`/`<body>`，不要 `<style>`，不要外链任何资源（CSS/JS/图片/字体），不要 emoji。
- 根元素与章头固定结构（标题与副标题**逐字用给你的原文**，不得改写）：

```html
<section class="chapter" id="ch02" data-num="02">
  <header class="ch-open">
    <p class="ch-kicker">第二章 · 据原文目录</p>
    <h2 class="ch-title">微积分与反向传播</h2>
    <p class="ch-sub">从链式法则手推一次梯度怎么流</p>
    <p class="ch-lede">…80–140 字：本章回答什么问题、在 AI 哪里用上、学完能做什么…</p>
  </header>
  <nav class="ch-toc" aria-label="章内目录">
    <a href="#ch02-s1">2.1 …</a><a href="#ch02-s2">2.2 …</a>…
  </nav>
  <h3 id="ch02-s1"><span class="h3-num">2.1</span> …</h3>
  …
  <h3 id="ch02-ai"><span class="h3-num">2.X</span> 在 AI 中的位置</h3>
  …
</section>
```

- 小节编号：章号.序号（第零章用 0.1、0.2…）。`id` 规则：`chNN-s1`、`chNN-s2`…；「在 AI 中的位置」固定 `chNN-ai` 且必须是最后一节。
- 章内目录 `<nav class="ch-toc">` 列出全部小节链接。

## 2. 可用组件（类名固定，组装方已定义样式，禁止自造样式）

| 组件 | 写法 |
|---|---|
| 定义框 | `<div class="def"><span class="box-tag">定义 2.1</span><p>…</p></div>` |
| 结论/定理框 | `<div class="thm"><span class="box-tag">结论 2.1</span><p>…</p></div>`（需要时内含推导段落） |
| 例题框 | `<div class="example"><span class="box-tag">例 2.1</span><p><strong>题目</strong>…</p><p><strong>解</strong> …（中间步骤编号或分步列）</p></div>` |
| 常见误用框 | `<div class="warn"><span class="box-tag">常见误用</span><p>…错在哪、怎么改…</p></div>` |
| 页边批注 | `<aside class="mn">一句话直觉、记忆钩子、易混点对比</aside>`（跟在相关段落后，每章 2–5 条） |
| 表格 | `<table class="tbl"><thead>…</thead><tbody>…</tbody></table>` |
| 图 | `<figure class="fig"><svg …>…</svg><figcaption>图 2.1　说明</figcaption></figure>`（SVG 颜色一律用 `var(--ink)`、`var(--accent)`、`var(--accent2)`、`var(--line)`，禁止写死色值；线宽 1.2–2） |
| 术语首现 | `<span class="kt">交叉熵</span>（cross-entropy）`——中英对照只在第一次出现给 |
| 待核 | `<span class="todo">【待核】</span>：说明缺什么把握` |

框内编号：定义/结论/例各自独立序列，按「章号.序号」编（第零章为 0.x）。

## 3. 数学写法（全手册统一，严禁自创记法）

- 行内公式 `\(...\)`；独立公式 `\[ ... \]`。**被后文引用或作为关键结论的独立公式必须带编号**：`\[ ... \tag{2.3} \]`，正文引用写作「式 (2.3)」。编号 = 章号.序号，每章从 1 起连续编号（第零章用 0.x）。
- 向量：粗体小写 `\(\mathbf{x}\)`；矩阵：粗体大写 `\(\mathbf{W}\)`；标量：斜体；集合/空间：`\(\mathbb{R}^{n}\)`；损失：`\(\mathcal{L}\)`；算子正体：`\operatorname{softmax}`、`\operatorname{diag}`、`\operatorname{tr}`、`\operatorname{rank}`、`\operatorname{KL}`（用 `\operatorname{...}`，不要直接打文字）。
- 注意力统一写法（各章一致）：
  `\operatorname{Attention}(\mathbf{Q},\mathbf{K},\mathbf{V})=\operatorname{softmax}\!\left(\dfrac{\mathbf{Q}\mathbf{K}^{\top}}{\sqrt{d_k}}\right)\mathbf{V}`
- 转置 `^{\top}`、逆 `^{-1}`、期望 `\mathbb{E}[\cdot]`、概率 `p(\cdot)`/`P(\cdot)`、梯度 `\nabla_{\mathbf{x}}`、偏导 `\dfrac{\partial \mathcal{L}}{\partial \mathbf{W}}`。
- 矩阵乘法维度**每次出现时给维度标注**（如 \(\mathbf{Q}\in\mathbb{R}^{n\times d_k}\)），正文推导先说维度再写等式。
- LaTeX 里不准出现 HTML；HTML 里不准出现 `$` 定界符。

## 4. 每章硬性内容要求

1. **可算的例题 ≥ 1**（建议 2–3 个）：真实数字代入，写出中间步骤与结果，结果自己用 Python 验算过（命令：`python3 -c "..."`）。例题要贴近 AI 场景（注意力分数、损失值、显存估算……），不是纯数学题。
2. **常见误用框 ≥ 1**。
3. **「在 AI 中的位置」小节**：用表格或分条列出「本章结论 → 具体 AI 组件/机制 → 缺了会怎样」，至少 3 行，禁止「在机器学习中有广泛应用」这类空话。
4. **页边批注 2–5 条**：直觉解释或易混点。
5. 语言：直白、口语化但不失严谨；术语首现给中英对照；一句话能说清的别写三句。

## 5. 引用与资源

- 只允许引用以下**真实存在**的读物（需要时才引，格式：作者《书名》或 作者 et al., 论文标题, 年份, arXiv 号）：
  - Gilbert Strang《Introduction to Linear Algebra》；李航《统计学习方法（第 2 版）》；Goodfellow, Bengio & Courville《Deep Learning》（MIT Press）；Bishop《Pattern Recognition and Machine Learning》；Cover & Thomas《Elements of Information Theory》；Boyd & Vandenberghe《Convex Optimization》；3Blue1Brown 视频系列《线性代数的本质》《微积分的本质》。
  - 论文：Vaswani et al. 2017（Attention Is All You Need, arXiv:1706.03762）；Kaplan et al. 2020（arXiv:2001.08361）；Hoffmann et al. 2022（Chinchilla, arXiv:2203.15556）；Schulman et al. 2017（PPO, arXiv:1707.06347）；Ouyang et al. 2022（InstructGPT, arXiv:2203.02155）；Rafailov et al. 2023（DPO, arXiv:2305.18290）；Shao et al. 2024（GRPO/DeepSeekMath, arXiv:2402.03300）；Hu et al. 2021（LoRA, arXiv:2106.09685）；Dao et al. 2022（FlashAttention, arXiv:2205.14135）。
- 除此之外**不得编造**任何文献、页码、出处。推荐读物集中写进第八章，其他章节至多提一次名字。

## 6. 自检清单（交活前逐项过）

- [ ] 章名、副标题与给你的原文**逐字一致**；结构符合 §1。
- [ ] 所有 `\tag{n.m}` 编号章内连续、无重复、被引用处编号存在。
- [ ] `\[`-`\]`、`\(`-`\)` 配对；跑一遍：`grep -o '\\\[' chapters/chNN.html | wc -l` 与 `\\\]` 数量相等。
- [ ] 例题数值用 Python 验算通过。
- [ ] 每个矩阵推导处标了维度。
- [ ] 「在 AI 中的位置」是最末小节且有 ≥3 行具体机制。
- [ ] 无 emoji、无外链、无 `$...$`、无 style 属性。
- [ ] 篇幅达标（见任务给出的目标）。

## 7. 交活时报告（≤200 字）

返回：实际文件名；本章 display 公式数（含 \tag 数）；例题数；Python 验算了哪些数；【待核】条目（没有就写「无」）；本章「AI 机制落点」3–8 条（供组装方做《AI 关联度核对表》）；自评页数（按 450 字正文+3 条公式≈1 页估算）。
