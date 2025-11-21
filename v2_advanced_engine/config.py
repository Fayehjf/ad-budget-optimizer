class Config:
    ENABLE_CLUSTERING = True
    ENABLE_FORECASTING = True
    
    # 模型参数
    MOVING_AVG_WINDOW = 3  # 循环移动平均的窗口大小
    CLUSTERS_COUNT = 3     # 聚类数数量
    FORECAST_HORIZON = 24  # 预测多少4小时
    
    # 权重融合系数
    ALPHA_FORECAST = 0.2   # 预测增益的影响力
    BETA_CLUSTER = 0.3     # 聚类形状的修正力