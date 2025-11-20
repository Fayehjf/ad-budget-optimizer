# 智能广告预算分配与平滑系统 (Smart Ad Budget Allocation & Pacing System)

## 1. 项目概览 (Project Overview)

本项目旨在解决亚马逊广告投放中的两个核心预算管理挑战：

    1. 单个广告活动 (Intra-campaign)：如何在 24 小时内平滑分配预算，避免预算在低效时段过早耗尽，同时覆盖高效转化时段。

    2. 多广告活动组合 (Inter-campaign)：在总预算有限（$100）的硬性约束下，如何在多个 Campaign 之间进行最优分配，以最大化整体收益。

## 2. 任务一：单个广告活动的小时级平滑分配

### 2.1 核心思路与方法 (Methodology)

为了实现预算的智能平滑分配，我们摒弃了简单的平均分配，采用了基于历史效率的循环加权移动平均算法 (Weighted Circular Moving Average)。

* 复合效率指标 (Composite Metric)：

    * 单纯依赖 Revenue 会偏向高流量但低效率的时段；单纯依赖 ROAS 会偏向偶然出单的低流量时段。

    * 本算法构建了 Efficiency Score = Revenue * log(1 + ROAS)，兼顾了规模与效率。

* 循环平滑 (Circular Smoothing)：

    * 为了防止预算曲线出现剧烈跳变，使用了窗口为 3 的移动平均。

    * 创新点：采用了“循环”处理逻辑，将 23:00 与次日 00:00 的数据首尾相连进行平滑，保证了跨午夜时段的预算分配连续性。

### 2.2 结果分析 (Result Analysis)

基于输出结果中 Campaign_A 的数据分析：

* 双峰模式识别：算法成功识别出该 Campaign 的两个高效转化时段：

    * 早高峰：预算权重在凌晨开始攀升，于 06:00 达到全天峰值 (1.22)。

    * 晚高峰：在 21:00 出现了第二个预算高峰 (1.20)。

* 低效时段节流：在转化较差的傍晚时段 (18:00 - 19:00)，预算被自动压低至 0.50 左右，有效避免了无效花费。

* 平滑度验证：相邻小时的预算变化幅度控制在合理范围内（例如 05:00 到 06:00 从 1.1 升至 1.22），未出现陡峭的阶梯状跳变，符合平滑度约束。

## 3. 任务二：多广告活动预算分配优化

### 3.1 核心思路与方法 (Methodology)

在总预算固定（$100）的约束下，为了实现“最大化总收入”的目标，采用了 基于全局 ROAS 的贪心算法 (Greedy Strategy based on Global ROAS)。

* 优先级排序：计算每个 Campaign 过去 7 天的全局 ROAS，优先满足高 ROAS 活动的预算需求。

* 饱和度封顶：分配金额严格受限于该 Campaign 的单日预算上限，防止过度分配导致无法消耗。

### 3.2 结果分析 (Result Analysis)

基于输出结果，总预算 $100 被精准分配，未出现闲置资金 (unallocated_budget: 0.0)。

详细分配决策表：

| 优先级 | 广告活动      | ROAS | 分配金额 | 状态说明                     |
|--------|---------------|------|----------|------------------------------|
| Tier 1 | Campaign_A    | 2.41 | $20.00   | 满额分配 (表现最优，优先喂饱) |
| Tier 1 | Campaign_H    | 2.23 | $10.00   | 满额分配                     |
| Tier 1 | Campaign_J    | 2.18 | $10.00   | 满额分配                     |
| Tier 1 | Campaign_B    | 1.99 | $25.00   | 满额分配                     |
| Tier 1 | Campaign_C    | 1.97 | $15.00   | 满额分配                     |
| Tier 1 | Campaign_I    | 1.92 | $10.00   | 满额分配                     |
| Tier 1 | Campaign_G    | 1.76 | $5.00    | 满额分配                     |
| Tier 2 | Campaign_E    | 1.67 | $5.00    | 部分分配 (预算耗尽截断点)     |
| Tier 3 | Campaign_F    | Low  | $0.00    | 无预算 (效率低于截断值)       |
| Tier 3 | Campaign_D    | Low  | $0.00    | 无预算 (效率低于截断值)       |


* 截断效应 (Cut-off Effect)：Campaign_E 成为了“边际活动”。虽然它的 ROAS (1.67) 尚可，但由于前序高优活动已占用了 $95，它只能获得剩余的 $5。

* 优胜劣汰：Campaign_F 和 Campaign_D 由于历史表现不佳（ROAS 低于 E），在本次分配周期中被暂停预算支持，从而保护了整体 ROI。

## 4. 结论与展望 (Conclusion & Future Work)

### 4.1 结论

本系统成功实现了一个 工程化就绪 的预算优化模块：

    1. 准确性：通过复合指标和贪心算法，理论上实现了在历史数据假设下的收益最大化。

    2. 鲁棒性：代码包含完整的异常处理（如缺失值填充、文件路径检查），并在 JSON 输出中提供了详细的分配理由。

    3. 稳定性：小时级分配采用了循环平滑机制，有效防止了广告系统的竞价抖动。

### 4.2 局限性与改进方向

当前采用的贪心算法虽然能最大化短期收益，但在长期运行中可能面临 “冷启动 (Cold Start)” 问题：被分配为 0 预算的 Campaign (如 F 和 D) 将失去积累数据证明自己的机会。

V2.0 版本规划：

    * 引入 Epsilon-Greedy 或 汤普森采样 (Thompson Sampling) 机制。

    * 预留 10% - 20% 的“探索预算”专门分配给低效或新 Campaign，以动态发掘潜在的黑马。

### 5. 如何运行 (How to Run)

本项目采用 Python 开发，依赖极简，易于部署。

1. 环境准备：

```bash
# 创建并激活虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行优化器：确保 data_for_ads.csv 位于根目录，然后执行：

```bash
python budget_optimizer.py
```

4. 查看结果： 运行成功后，结果将自动保存至 allocation_result.json。