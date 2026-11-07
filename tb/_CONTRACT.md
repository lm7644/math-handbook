# 教科书版章节写作契约（所有写作代理必读）

你在写《大模型数学·现代教科书版》的若干章。这是**面向零基础自学者**的版本，与已有的「学术严谨版」定位不同：更厚、更慢、更细。章名与副标题照录原文 16 章目录（各章标「据原文目录」）。

## 0. 定位（与学术版的根本区别）

| | 学术严谨版 | 本教科书版 |
|---|---|---|
| 读者 | 有工程基础想补数学 | **零基础自学** |
| 节奏 | 定义→结论→例 | **直觉/类比 → 形式化定义 → 一步步推导（不跳步）→ 上手例 → 检查点/自测题** |
| 口吻 | 精炼 | 讲透、像老师站旁边讲 |

**最高纪律：**
1. **不跳步**。每步推导都要交代「为什么这么走」。禁止「显然可得」「易证」。
2. **直觉先行**：每个概念先给生活类比或几何直觉，再给形式化定义。
3. **公式正确**（与学术版同标准）：拿不准标 `<span class="todo">【待核】</span>`，绝不猜。每章公式将被独立复核。
4. **每章落在 AI 上**：具体到机制（矩阵乘法→注意力 QK^T；链式法则→反向传播；KL→RLHF），每章末尾有「在 AI 中的位置」。
5. **有趣**：允许恰当的比喻、小故事、对话感；但不许牺牲准确，不许灌水凑字数。

## 1. 文件与结构

- 每章一个 HTML 片段：`tb/tbNN.html`（NN=00..15）。**只写片段**，无 html/head/body/style，无外链，无 emoji。
- 根结构（标题/副标题**逐字用给你的原文**）：

```html
<section class="chapter" id="tb02" data-num="02">
  <header class="ch-open">
    <p class="ch-kicker">第二章 · 据原文目录 · 教科书版</p>
    <h2 class="ch-title">微积分与反向传播</h2>
    <p class="ch-sub">从链式法则手推一次梯度怎么流</p>
    <p class="ch-lede">…120–180 字，用大白话说清这章要解决什么困惑、为什么值得读…</p>
    <div class="ch-map"><span class="map-tag">本章路线</span>直觉 → 定义 → 推导 → 例子 → 自测</div>
  </header>
  <nav class="ch-toc">…章内小节链接…</nav>
  <h3 id="tb02-s1">…</h3>…
  <h3 id="tb02-ai">…在 AI 中的位置…</h3>
  <div class="quiz"><span class="box-tag">自测题</span>…题目 + <details><summary>看答案</summary>…</details>…</div>
</section>
```

- 小节 id：`tbNN-s1`、`tbNN-s2`…；「在 AI 中的位置」固定 `tbNN-ai`，是自测题**之前**的最后一节正文。
- 公式编号 `\[...\tag{2.3}\]`（章号.序号），行内 `\(...\)`、独立 `\[...\]`。记法与学术版一致（向量粗小写、矩阵粗大写、转置 ᵀ、注意力统一写法 softmax(QKᵀ/√d_k)V）。

## 2. 教科书版专属组件

| 组件 | 写法 | 用途 |
|---|---|---|
| 直觉框 | `<div class="intuition"><span class="box-tag">直觉 · 先建立感觉</span><p>类比/几何画面/生活例子</p></div>` | 每个重要概念**先有这个** |
| 定义框 | `<div class="def"><span class="box-tag">定义 2.1</span>…</div>` | 直觉之后给形式化 |
| 推导框 | `<div class="derive"><span class="box-tag">推导 · 一步步来</span><p>每一步交代理由…</p></div>` | 不跳步的推导 |
| 上手例 | `<div class="example"><span class="box-tag">例 2.1 · 动手算</span>…题目+分步解…</div>` | 真实数字，python3 验算 |
| 检查点 | `<div class="checkpoint"><span class="box-tag">检查点 ✓</span><p>你现在应该能：…（3–5 条可自查的能力）</p></div>` | 每 1–2 小节一个 |
| 常见坑 | `<div class="warn"><span class="box-tag">常见坑</span>…</div>` | ≥1/章 |
| 自测题 | `<div class="quiz">…</div>`（章末） | 3–5 题，**附答案**（用 `<details><summary>看答案</summary>答案与解析</details>` 折叠） |
| 批注 | `<aside class="mn">…</aside>` | 记忆钩子、易混对比，2–5 条/章 |

## 3. 每章硬性要求

1. **直觉框 ≥2**（重要概念都有类比）。
2. **推导框**：核心结论的推导全程不跳步，每步一句「为什么」。
3. **上手例 ≥2**：真实数字、有中间步骤、python3 验算。
4. **检查点 ≥2**。
5. **自测题 3–5 道，全部附答案与解析**（答案也要 python3 验算）。
6. **「在 AI 中的位置」**（正文最后一节，自测题之前）：≥3 行具体机制。
7. 篇幅目标见各章任务（教科书版比学术版厚，约 1.3–1.6 倍）。

## 4. 诚实边界

- 引用只用户口本白名单：Strang《Introduction to Linear Algebra》、李航《统计学习方法（第2版）》、Goodfellow et al.《Deep Learning》、Bishop《PRML》、Cover & Thomas《Elements of Information Theory》、Boyd & Vandenberghe《Convex Optimization》、3Blue1Brown 视频系列；论文 Vaswani 2017(1706.03762)、Kaplan 2020(2001.08361)、Hoffmann 2022(2203.15556)、Schulman 2017 PPO(1707.06347)、Ouyang 2022 InstructGPT(2203.02155)、Rafailov 2023 DPO(2305.18290)、Shao 2024 GRPO(2402.03300)、Hu 2021 LoRA(2106.09685)、Dao 2022 FlashAttention(2205.14135)。其余一律不引，不编造页码出处。

## 5. 自检清单

- [ ] 章名/副标题逐字一致；结构符合 §1；章末有自测题（附答案）。
- [ ] `\[`/`\]`、`\(`/`\)` 配对（grep 数相等）；`\tag` 章内连续。
- [ ] 直觉框≥2、推导不跳步、上手例≥2、检查点≥2、自测题≥3。
- [ ] 例题与自测题答案 python3 验算通过。
- [ ] 矩阵推导标维度；「在 AI 中的位置」具体。
- [ ] 无 emoji、无外链、无 `$`、无 style 属性。

## 6. 交活报告（≤200 字）

文件名；display 公式数（含 tag 数）；直觉框/上手例/检查点/自测题各几个；python3 验算了哪些；【待核】条目；AI 落点 3–8 条；自评页数。
