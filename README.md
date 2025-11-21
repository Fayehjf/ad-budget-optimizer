# 🎯 智能广告预算分配系统


本项目旨在解决电商广告投放中的预算分配难题。通过两个版本的迭代，我们构建了一套既能解决单日平滑投放（Intra-day Pacing），又能应对多品类、多活动复杂场景（Inter-campaign Optimization）的解决方案。

# 📚 项目架构概览

本项目包含两个核心版本，分别代表了不同的工程阶段与解决思路：

| 版本 | 核心驱动 | 关键技术 | 适用场景 | 文档入口 |
|------|---------------------|-------------------------|------------------------|------------|
| **V1: Heuristic Script** | 规则驱动 (Rule-Based) | • 循环加权移动平均<br>• 贪心算法<br>• 复合效率指标 | • 单品类/少活动<br>• 数据量小<br>• 快速冷启动 | [点击查看 V1 详情](https://github.com/Fayehjf/ad-budget-optimizer/blob/main/v1_heuristic_script/README_v1.md) |
| **V2: Advanced Engine** | AI 混合驱动 (Hybrid AI) | • K-Means 聚类（模式识别）<br>• XGBoost 回归（趋势预测）<br>• OOP 分层架构 | • 多品类/全店投放<br>• 业务快速扩张期<br>• 需捕捉复杂流量趋势 | [点击查看 V2 详情](https://github.com/Fayehjf/ad-budget-optimizer/blob/main/v2_advanced_engine/README_v2.md) |


# 🚀 V1: 启发式基础版 (Heuristic Baseline)

V1 版本 是项目的基石，重点解决了“如何平滑地花钱”这一问题。

* 核心逻辑：利用历史数据的 Revenue 和 ROAS 构建复合指标，通过循环平滑算法 消除跨午夜的数据抖动。

* 主要产出：一个轻量级的脚本，能够生成平滑的 24 小时预算权重曲线。

* 📂 对应目录：v1_heuristic_script/

# 🧠 V2: 智能进阶版 (Advanced Engine)

V2 版本 是为了应对规模化挑战而生的企业级引擎。

* 核心逻辑：在 V1 的稳定性基础上，引入了机器学习模块。

    * 智能层：自动识别流量模式（早/晚高峰型）并预测未来效率。

    * 鲁棒性：具备自动降级机制，当数据不足时自动回退到 V1 规则，保证系统永不崩溃。

* 架构设计：采用分层架构（数据层 -> 智能层 -> 决策层），支持一键运行和模块化扩展。

* 📂 对应目录：v2_advanced_engine/
