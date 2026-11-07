#!/usr/bin/env python3
# 生成极简工具书数据：从复核过的公式里精选，注入 cheatsheet.html 的 __DATA__
import json, pathlib, re

ROOT = pathlib.Path(__file__).parent

# 每条: (组, 中文名, 英文名, LaTeX公式或None, 备注(用在哪), 出处章)
E = [
# ---- 符号 ----
("符号","实数向量空间","vector space",r"\mathbb{R}^{n}", "向量 x 的活动范围；嵌入向量 x∈ℝ^d","01"),
("符号","向量 / 矩阵","vector / matrix",r"\mathbf{x}\ (\text{粗小写}),\quad \mathbf{W}\ (\text{粗大写})", "向量粗小写、矩阵粗大写、标量斜体——全书约定","01"),
("符号","转置 / 逆","transpose / inverse",r"\mathbf{W}^{\top},\quad \mathbf{W}^{-1}", "转置 ᵀ、逆 ⁻¹；(AB)ᵀ=BᵀAᵀ","01"),
("符号","期望 / 概率","expectation",r"\mathbb{E}[\cdot],\quad p(\cdot)", "期望 E、概率密度 p","03"),
("符号","损失 / 梯度","loss / gradient",r"\mathcal{L},\quad \nabla_{\boldsymbol{\theta}}\mathcal{L}", "花体 L 表损失，∇ 表梯度","02"),
("符号","逐元素乘","Hadamard",r"\mathbf{a}\odot\mathbf{b}", "对应位相乘，区别于矩阵乘；全书统一写 ⊙","02"),
("符号","关键维度记号","dims",r"d_{\text{model}},\ d_k,\ h,\ V,\ L,\ s", "d_model=隐维 d_k=头维 h=头数 V=词表 L=层数 s=序列长（s 见第九章）","06"),
# ---- 线性代数 ----
("线性代数","嵌入查表","embedding lookup",r"\mathbf{e}_t=\mathbf{o}_t^{\top}\mathbf{E}", "one-hot 乘嵌入矩阵 = 取第 t 行；LLM 第一步","01"),
("线性代数","点积与余弦","dot / cosine",r"\operatorname{cos\_sim}=\dfrac{\mathbf{x}\cdot\mathbf{y}}{\|\mathbf{x}\|_2\|\mathbf{y}\|_2}", "余弦相似度，检索与注意力打分的底","01"),
("线性代数","线性层","linear layer",r"\mathbf{y}=\mathbf{W}\mathbf{x}+\mathbf{b}", "W 形状 d_out×d_in；FFN 与投影的基本件","01"),
("线性代数","矩阵乘法维度","matmul dims",r"\mathbb{R}^{n\times d_k}\times\mathbb{R}^{d_k\times m}\to\mathbb{R}^{n\times m}", "每次矩阵乘先对齐内维","01"),
("线性代数","低秩分解","LoRA",r"\Delta\mathbf{W}=\mathbf{B}\mathbf{A},\ \mathbf{B}\in\mathbb{R}^{d\times r},\ \mathbf{A}\in\mathbb{R}^{r\times d}", "r≪d，参数量 d²→2dr；微调省参数","01"),
("线性代数","特征值","eigenvalue",r"\mathbf{A}\mathbf{v}=\lambda\mathbf{v}", "对称矩阵可正交对角化；协方差主方向","01"),
# ---- 微积分与求导 ----
("微积分与求导","梯度","gradient",r"\nabla f(\mathbf{x})=\left[\tfrac{\partial f}{\partial x_1}\ \cdots\ \tfrac{\partial f}{\partial x_n}\right]^{\top}", "偏导排成列向量；指向上升最快方向","02"),
("微积分与求导","链式法则","chain rule",r"\frac{\partial\mathcal{L}}{\partial\mathbf{x}}=\left(\frac{\partial\mathbf{y}}{\partial\mathbf{x}}\right)^{\top}\nabla_{\mathbf{y}}\mathcal{L}", "反向传播的数学本质；向量形式注意转置","02"),
("微积分与求导","xᵀa 求导","identity",r"\dfrac{\partial(\mathbf{x}^{\top}\mathbf{a})}{\partial\mathbf{x}}=\mathbf{a}", "分母布局；线性层 backward 基础","10"),
("微积分与求导","xᵀAx 求导","quadratic",r"\dfrac{\partial(\mathbf{x}^{\top}\mathbf{A}\mathbf{x})}{\partial\mathbf{x}}=(\mathbf{A}+\mathbf{A}^{\top})\mathbf{x}", "A 对称时=2Ax","10"),
("微积分与求导","逆矩阵微分","inverse diff",r"d(\mathbf{X}^{-1})=-\mathbf{X}^{-1}(d\mathbf{X})\mathbf{X}^{-1}", "注意逆在两边、负号在前","10"),
("微积分与求导","tr 循环性","trace cyclic",r"\operatorname{tr}(\mathbf{A}\mathbf{B}\mathbf{C})=\operatorname{tr}(\mathbf{B}\mathbf{C}\mathbf{A})", "矩阵微积分调换顺序的关键","10"),
("微积分与求导","CE 对 logits 梯度","softmax-CE grad",r"\frac{\partial\mathcal{L}}{\partial\mathbf{z}}=\mathbf{p}-\mathbf{y}", "softmax+交叉熵的合成梯度=预测减真值","15"),
# ---- 概率与采样 ----
("概率与采样","自回归分解","autoregressive",r"P(x_1,\dots,x_T)=\prod_{t=1}^{T}P(x_t\mid x_1,\dots,x_{t-1})", "LLM 的定义式：逐 token 条件概率","03"),
("概率与采样","类别分布","categorical",r"P(X=k)=p_k,\ \sum_k p_k=1", "词表上的 next-token 分布","03"),
("概率与采样","高斯密度","Gaussian",r"f(x)=\dfrac{1}{\sqrt{2\pi}\sigma}\exp\!\left(-\tfrac{(x-\mu)^2}{2\sigma^2}\right)", "初始化与噪声；Z=(X−μ)/σ 标准化","03"),
("概率与采样","贝叶斯","Bayes",r"P(A\mid B)=\dfrac{P(B\mid A)P(A)}{P(B)}", "注意基础率；别把 P(A|B) 当 P(B|A)","03"),
("概率与采样","极大似然","MLE",r"\hat{\theta}=\arg\max_\theta\sum_i\ln q_\theta(y_i)", "训练=MLE；与最小交叉熵等价","04"),
("概率与采样","温度采样","temperature",r"p_i\propto p_i^{1/T}\ \Leftrightarrow\ \operatorname{softmax}(z_i/T)", "T<1 更尖锐（更确定），T>1 更平（更随机）","03"),
# ---- 信息论与损失 ----
("信息论与损失","熵","entropy",r"H(p)=-\sum_x p(x)\log p(x)", "不确定性的度量；bit 用 log2、nat 用 ln","04"),
("信息论与损失","交叉熵","cross-entropy",r"H(p,q)=-\sum_x p(x)\log q(x)", "LLM 训练损失；=H(p)+KL(p‖q)","04"),
("信息论与损失","KL 散度","KL divergence",r"\operatorname{KL}(p\|q)=\sum_x p(x)\log\dfrac{p(x)}{q(x)}", "≥0，不对称，不是距离；RLHF 用 KL(π_θ‖π_ref)","04"),
("信息论与损失","困惑度","perplexity",r"\mathrm{PPL}=\exp\!\left(-\tfrac{1}{N}\textstyle\sum_i\ln q(y_i)\right)", "LM 评估标准；与平均损失单调对应","04"),
# ---- 优化器与调度 ----
("优化器与调度","梯度下降","gradient descent",r"\boldsymbol{\theta}_{t+1}=\boldsymbol{\theta}_t-\eta\,\nabla_{\boldsymbol{\theta}}\mathcal{L}", "η=学习率；η>2/λmax 发散（=临界等幅震荡）","05"),
("优化器与调度","动量","momentum",r"\mathbf{v}\leftarrow\beta\mathbf{v}+\nabla\mathcal{L},\quad \boldsymbol{\theta}\leftarrow\boldsymbol{\theta}-\eta\mathbf{v}", "β≈0.9；抑制峡谷震荡","05"),
("优化器与调度","Adam","Adam",r"\hat m_t=\tfrac{m_t}{1-\beta_1^t},\ \hat v_t=\tfrac{v_t}{1-\beta_2^t},\ \theta\leftarrow\theta-\eta\tfrac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}", "偏差修正不可省；LLM 训练常取 β2=0.95","05"),
("优化器与调度","解耦权重衰减","AdamW",r"\theta\leftarrow\theta-\eta\,\lambda\,\theta", "与 L2 不等价（Adam 下）；LLM 训练标配","05"),
("优化器与调度","warmup","lr warmup",r"\eta_t=\eta_{\max}\cdot t/T_w\ (t\le T_w)", "线性升温；Adam 二阶矩未稳时防炸","05"),
# ---- Transformer 组件 ----
("Transformer 组件","缩放点积注意力","attention",r"\operatorname{softmax}\!\left(\dfrac{\mathbf{Q}\mathbf{K}^{\top}}{\sqrt{d_k}}\right)\mathbf{V}", "全书统一写法；除以 √d_k 防 softmax 饱和","06"),
("Transformer 组件","为什么除 √d_k","scaling",r"\operatorname{Var}(\mathbf{q}\cdot\mathbf{k})=d_k\ (\text{分量独立、零均值、单位方差})", "d 大时分数尺度~√d_k，不除则饱和、梯度消失","06"),
("Transformer 组件","正弦位置编码","sinusoidal PE",r"PE_{(pos,2i)}=\sin\!\tfrac{pos}{10000^{2i/d}},\ PE_{(pos,2i+1)}=\cos\!\tfrac{pos}{10000^{2i/d}}", "相对位置可线性表示；RoPE 的思想源头","06"),
("Transformer 组件","LayerNorm","LayerNorm",r"\hat x_i=\dfrac{x_i-\mu}{\sqrt{\sigma^2+\epsilon}},\ \ y_i=\gamma_i\hat x_i+\beta_i", "按 token 内特征维归一；pre-norm 更稳","06"),
("Transformer 组件","残差连接","residual",r"\mathbf{y}=\mathbf{x}+F(\mathbf{x})\ \Rightarrow\ \tfrac{\partial\mathbf{y}}{\partial\mathbf{x}}=\mathbf{I}+\tfrac{\partial F}{\partial\mathbf{x}}", "梯度高速路：+I 保证深层可训","06"),
("Transformer 组件","FFN","feed-forward",r"\operatorname{FFN}(\mathbf{x})=\varphi(\mathbf{x}\mathbf{W}_1+\mathbf{b}_1)\mathbf{W}_2+\mathbf{b}_2", "d_model→4d_model→d_model；约占 2/3 参数","06"),
# ---- 数值稳定 ----
("数值稳定","浮点格式","float formats",r"\text{FP32/TF32/FP16/BF16}", "BF16 指数位同 FP32（范围大）、尾数 7 位（精度低）——深度学习够用","07"),
("数值稳定","log-sum-exp","log-sum-exp",r"\operatorname{softmax}(z_i)=\dfrac{e^{z_i-m}}{\sum_j e^{z_j-m}},\ m=\max_j z_j", "减最大值防 exp 溢出；softmax/CE 必用","07"),
("数值稳定","稳定交叉熵","stable CE",r"\log p(y)=z_y-m-\log\Bigl(\textstyle\sum_j e^{z_j-m}\Bigr)", "log_softmax 合并算，不先 exp 再取 log","07"),
("数值稳定","损失缩放","loss scaling",r"\mathcal{L}_{\text{scaled}}=S\cdot\mathcal{L},\ \ \nabla\leftarrow\nabla/S", "混合精度下防梯度下溢成 0","07"),
("数值稳定","梯度裁剪","grad clip",r"\mathbf{g}\leftarrow\mathbf{g}\cdot\min\!\bigl(1,\ c/\lVert\mathbf{g}\rVert_2\bigr)", "按全局范数裁剪；LLM 常用 c=1.0","07"),
# ---- 训练估算 ----
("训练估算","训练 FLOPs","C≈6ND",r"C\approx 6ND", "N=参数量 D=token 数；前向 2N 反向 4N（每 token）","09"),
("训练估算","显存四本账","memory",r"\text{参数}+\text{梯度}+\text{Adam}(m,v)+\text{激活}", "混合精度+AdamW 静态显存≈16N 字节","09"),
("训练估算","Chinchilla 最优","compute-optimal",r"D^{*}\approx 20N", "每个参数配约 20 token；小模型喂更多数据更划算","09"),
("训练估算","流水线气泡","pipeline bubble",r"\text{气泡比}=\dfrac{p-1}{m+p-1}", "p=流水线级数 m=micro-batch 数；m 越大气泡越小","09"),
# ---- 部署推理 ----
("部署推理","KV cache 显存","KV cache",r"M_{\text{KV}}=2\cdot L\cdot d_{\text{model}}\cdot n_{\text{ctx}}\cdot B\cdot b", "2=K和V；b=字节数(BF16=2)；7B×2048×bs1≈1 GiB","13"),
("部署推理","GQA/MQA 省显存","GQA",r"M_{\text{KV}}\propto n_{\text{kv\_heads}}", "分组查询注意力砍 KV 头数；GQA-8 省 4 倍","13"),
("部署推理","对称量化","quantization",r"q=\operatorname{round}(x/s),\ \ \tilde x=s\,q,\ \ |\tilde x-x|\le s/2", "INT8/INT4 显存与精度取舍；s=量化步长","13"),
("部署推理","All-Reduce 通信","all-reduce",r"\text{通信量}=\dfrac{2(N-1)}{N}\,K", "N 卡 K 元素；TP 要放单机 NVLink 内","13"),
# ---- RL 与对齐 ----
("RL 与对齐","策略梯度","policy gradient",r"\nabla_\theta J=\mathbb{E}\bigl[\textstyle\sum_t\nabla_\theta\log\pi_\theta(a_t|s_t)\,\hat A_t\bigr]", "对数导数技巧；采样即可估梯度","11"),
("RL 与对齐","PPO 裁剪","PPO clip",r"\mathcal{L}^{\text{CLIP}}=\mathbb{E}_t\bigl[\min(r_t\hat A_t,\ \operatorname{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t)\bigr]", "r_t=π_θ/π_old；信任区防大步跑偏","11"),
("RL 与对齐","KL 惩罚","KL penalty",r"\mathcal{L}=\mathbb{E}[r]-\beta\,\operatorname{KL}(\pi_\theta\|\pi_{\text{ref}})", "防 reward hacking、保语言能力","11"),
("RL 与对齐","DPO 损失","DPO",r"\mathcal{L}_{\text{DPO}}=-\log\sigma\!\bigl(\beta\log\tfrac{\pi_\theta(y_w)}{\pi_{\text{ref}}(y_w)}-\beta\log\tfrac{\pi_\theta(y_l)}{\pi_{\text{ref}}(y_l)}\bigr)", "无需奖励模型、离线；直接拉偏好对","11"),
("RL 与对齐","GRPO 优势","GRPO",r"\hat A_i=\dfrac{r_i-\operatorname{mean}(\{r\}_G)}{\operatorname{std}(\{r\}_G)}", "同 prompt 采 G 条组内标准化；无价值网络","11"),
# ---- 检索 RAG ----
("检索 RAG","三种度量","metrics",r"\cos=\tfrac{q\cdot d}{\|q\|\|d\|},\ \ \text{dot}=q^{\top}d,\ \ d_2=\|q-d\|_2", "归一化后 dot=cos、d₂²=2−2cos；别用未归一点积","12"),
("检索 RAG","RAG 后验","RAG posterior",r"p(\text{doc}|\text{query})\approx\operatorname{softmax}(\text{score})", "检索分数当近似后验；top-k 截断后重归一化","12"),
("检索 RAG","暴力 vs ANN","ANN",r"\text{暴力 }O(Nd)\ \to\ \text{IVF/HNSW 亚线性}", "召回率↔延迟取舍；nprobe/ef 调参","12"),
]

# 注入
tpl = (ROOT/"cheatsheet.html").read_text(encoding="utf-8")
def esc(s): return s.replace("\\","\\\\") if False else s
data = []
for g,t,en,f,n,tag in E:
    data.append({"g":g,"t":t,"en":en,"f":f,"n":n,"tag":tag})
js = json.dumps(data, ensure_ascii=False)
out = tpl.replace("__DATA__", js)

# ---------- 硬检查：输出含未完成标记则构建失败 ----------
import re as _re, sys as _sys
_hits = [m for m in _re.finditer(r"待核|TODO|FIXME|XXX", out)]
if _hits:
    for m in _hits[:20]:
        i = m.start()
        print(f"构建失败：发现未完成标记 {m.group(0)!r} 上下文：{out[max(0,i-40):i+40]!r}")
    _sys.exit(1)

(ROOT/"cheatsheet.html").write_text(out, encoding="utf-8")
print(f"cheatsheet.html 注入 {len(data)} 条, 组数={len(set(d['g'] for d in data))}, size={len(out)}")
