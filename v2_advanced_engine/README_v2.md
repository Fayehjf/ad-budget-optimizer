# 智能多策略预算分配引擎

## 1. 项目摘要

本项目构建了一个**混合驱动（Hybrid-Driven）**的广告预算分配引擎。它旨在解决单一启发式算法在面对业务快速扩张、多品类差异化投放时的局限性。

V2 引擎在 V1（基于历史效率的循环加权移动平均）基础上完成了架构级升级，引入了：

* 模块化分层架构

* K-Means 聚类（模式识别）

* XGBoost 算法（趋势预测）

系统能够根据数据量级自动在“规则模式”与“AI 增强模式”间无缝切换，实现了从“经验决策”向“数据智能决策”的进化。

## 2. 核心逻辑

### V1: The Baseline (启发式规则)

* 核心痛点：单纯依赖 Revenue 偏向高流量低效时段，单纯依赖 ROAS 忽略规模效应；且无法应对未来的趋势变化。

* 解决方案：构建 Efficiency Score = Revenue * log(1 + ROAS) 复合指标，并使用**循环平滑（Circular Smoothing）**处理跨午夜数据。

* 局限性：静态的历史平均，无法感知“即将到来的大促”或“不同品类的流量形态差异”。

### V2: The Advanced Engine (智能 + 规则融合)

* 核心理念：稳定性遇上智能化

* 架构升级：采用 OOP（面向对象）设计，将数据处理、智能分析、决策分配解耦。将系统拆解为：

    * Data Preprocessor

    * Intelligence Layer（聚类 + 预测）

    * Allocation Layer（规则 + AI 加权融合）

* 算法升级：

    1. Pattern Recognition (K-Means): 自动识别品类是“早高峰型”、“晚高峰型”还是“平稳型”，解决多品类管理难题。

    2. Trend Forecasting (XGBoost): 基于时序特征预测未来 24h 效率，捕捉潜在机会。

    3. Ensemble Allocation: 将 V1 的稳定性与 V2 的预测性加权融合。

## 3. 系统架构

项目采用 Layered Architecture (分层架构) 设计，确保高内聚低耦合：

graph TD
    A[Input Data (CSV)] --> B(Data Preprocessor Layer)
    B --> C{Intelligence Layer}
    C -- Data Sufficient --> D[K-Means Clustering]
    C -- Data Sufficient --> E[XGBoost Forecasting]
    C -- Data Insufficient --> F[Skip AI Modules]
    D --> G(Allocation Layer)
    E --> G
    F --> G
    G --> H[Final Optimization Result (JSON)]


📂 模块详解

1. preprocessor.py (数据层):

    负责数据清洗、缺失值自动填充（兼容 V1/V2 数据结构）、特征工程（Time Lags, Rolling Window）。

2. intelligence_layer.py (智能层):

    K-Means: 对 [Category x Hour] 矩阵进行归一化聚类，提取流量形状（Shape）。

    XGBoost: 构建监督学习任务，预测下一时间步的 Efficiency Score。

    Graceful Degradation (优雅降级): 当数据不足（如新品类冷启动）时，自动关闭 AI 模块，不阻断流程。

3. allocator.py (决策层):

    实现 V1 的 Circular Moving Average。

    实现多策略融合公式：

    $$W_{final} = W_{base} \cdot (1-\alpha) + W_{cluster} \cdot \alpha \cdot \text{TrendGain}$$

4. auto_optimizer.py (引擎入口):

    自动化流水线封装，支持一键运行、多格式导出、路径自适应。

## 4. 技术亮点

### 4.1 鲁棒性设计 (Robustness & Fallback)

系统内置了完备的异常处理机制。如果输入数据缺少 category_id，或者样本量不足以进行聚类（如 n_samples < n_clusters），智能层会自动捕获异常并输出 Log 提示，自动回退到 V1 算法。这保证了生产环境下的绝对可用性。

### 4.2 自动化特征工程

为了支持 XGBoost，系统自动生成时序特征：

    * Lag Features: 昨日同期表现 (lag_24h)。

    * Rolling Features: 过去 7 天的滑动平均 (rolling_mean_7d)。

    * Context Features: 周末/工作日标记 (is_weekend)。

### 4.3 跨品类自适应

通过 K-Means 聚类，系统不再需要人工为每个品类设定规则。只需设定 Cluster 数量，算法会自动发现数据中的隐含模式（Latent Patterns），极大地降低了业务扩张时的人力维护成本。

## 5. 局限性与思考

虽然 V2 版本在架构上实现了质的飞跃，但在实际落地中仍存在以下改进空间：

* 当前局限

    * 冷启动问题: 对于完全没有历史数据的新广告活动，XGBoost 和 K-Means 都无法工作，目前只能回退到平均值或规则。

    * 反馈延迟: 当前模型是离线训练。实际广告投放中，调整预算后，市场反应（ROAS）会有延迟，当前模型尚未包含这种动态反馈机制。

    * 算力开销: 对每个请求都实时重新训练 XGBoost 模型在数据量巨大时效率较低。

* 未来改进方向

    1. 模型持久化: 将训练好的模型保存为 .json 或 .pkl 文件，线上只做推理（Inference），定期离线更新模型。

    2. 强化学习: 引入 Bandit 算法或 RL（如 PPO），让 Agent 在“探索（Exploration）”和“利用（Exploitation）”之间寻找平衡，实现动态竞价。

    3. 带约束优化: 引入 Scipy 或 CVXPY 求解器，加入硬约束条件（如：早高峰必须花完 30% 预算，单小时花费不超过 $X）。

## 6. 运行指南

* 确保已安装依赖：

```bash
pip install -r requirements.txt
```

* 运行自动化引擎

在项目根目录 下运行：

```bash
python v2_advanced_engine/main.py
```

* 输出结果

程序运行后，将在 v2_advanced_engine/ 目录下生成 optimization_results.json 文件，包含每个品类、每小时的详细预算分配建议。
