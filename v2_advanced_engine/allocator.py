import numpy as np
from .config import Config

class BudgetAllocator:
    def circular_moving_average(self, raw_weights):
        """
        V1 核心算法：基于历史效率的循环移动平均
        """
        if len(raw_weights) != 24:
            raw_weights = np.resize(raw_weights, 24)

        window = Config.MOVING_AVG_WINDOW
        # 循环拼接：把最后几个小时拼到前面，把最前几个小时拼到后面，解决解决跨午夜（23:00 -> 00:00）的平滑问题
        padded = np.concatenate([raw_weights[-(window//2):], raw_weights, raw_weights[:(window//2)]])
        
        smooth_weights = []
        for i in range(len(raw_weights)):
            # 简单的窗口平均
            val = np.mean(padded[i : i + window])
            smooth_weights.append(val)
            
        return np.array(smooth_weights)

    def fuse_strategies(self, v1_weights, cluster_curve=None, forecast_curve=None):
        """
        V2 核心算法：融合规则(V1)与智能(V2)
        """
        final_weights = v1_weights.copy()
        
        # 聚类修正
        if cluster_curve is not None:
            beta = Config.BETA_CLUSTER
            # 加权融合
            final_weights = (final_weights * (1 - beta)) + (cluster_curve * beta)

        # 预测修正，如果预测未来效率高，则增加权重
        if forecast_curve is not None:
            alpha = Config.ALPHA_FORECAST
            avg_score = np.mean(forecast_curve)
            if avg_score > 0:
                gain_factor = forecast_curve / avg_score
                damped_gain = 1 + alpha * (gain_factor - 1)
                final_weights *= damped_gain

        # 归一化
        total_weight = np.sum(final_weights)
        if total_weight == 0:
            return np.ones(24) / 24 # 兜底：均匀分配
            
        return final_weights / total_weight