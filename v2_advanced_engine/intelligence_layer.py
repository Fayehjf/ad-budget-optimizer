import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import xgboost as xgb
from .config import Config
import warnings

warnings.filterwarnings('ignore')

class IntelligenceModule:
    def __init__(self):
        # 初始化 KMeans
        self.kmeans = KMeans(
            n_clusters=Config.CLUSTERS_COUNT, 
            random_state=42, 
            n_init=10
        )
        # 初始化 XGBoost
        self.xgb_model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            n_jobs=-1
        )

    def get_cluster_patterns(self, df):
        """
        执行 K-Means 聚类，识别不同品类的流量形态 (Shape)
        """
        if not Config.ENABLE_CLUSTERING:
            print(" [智能层] 聚类模块已禁用。")
            return None
            
        required_cols = ['category_id', 'hour', 'efficiency_score']
        if not all(col in df.columns for col in required_cols):
            print(" [智能层] 缺少聚类所需列，跳过聚类。")
            return None

        try:
            # 行=品类, 列=0-23点
            pivot_df = df.pivot_table(
                index='category_id', 
                columns='hour', 
                values='efficiency_score', 
                aggfunc='mean'
            ).fillna(0)
            
            pivot_df = pivot_df.reindex(columns=range(24), fill_value=0)
            
            # 归一化
            row_sums = pivot_df.sum(axis=1)
            normalized_data = pivot_df.div(row_sums.replace(0, 1), axis=0)

            if len(normalized_data) < Config.CLUSTERS_COUNT:
                print(f" [智能层] 品类数量不足 ({len(normalized_data)}个)，无法进行聚类分析(需要至少{Config.CLUSTERS_COUNT}个)。跳过聚类。")
                return None
            
            # 训练
            self.kmeans.fit(normalized_data)
            
            # 结果
            profiles = {i: center for i, center in enumerate(self.kmeans.cluster_centers_)}
            labels = self.kmeans.labels_
            mapping = dict(zip(pivot_df.index, labels))
            
            print(f" [智能层] 聚类完成。已识别 {Config.CLUSTERS_COUNT} 种典型流量模式。")
            return {'profiles': profiles, 'mapping': mapping}
            
        except Exception as e:
            print(f" [智能层] 聚类失败: {str(e)}")
            return None

    def predict_future_efficiency(self, df):
        """
        执行 XGBoost，预测未来 24 小时趋势
        """
        if not Config.ENABLE_FORECASTING:
            print(" [智能层] 预测模块已禁用。")
            return None
            
        try:
            df_train = self._create_time_features(df.copy()).dropna()
            
            if len(df_train) < 24:
                print(" [智能层] 数据不足，无法进行预测。")
                return None
            
            features = ['hour', 'is_weekend', 'lag_24h', 'rolling_mean_7d']
            X = df_train[features]
            y = df_train['efficiency_score']
            
            # 训练
            self.xgb_model.fit(X, y)
            
            # 逻辑：取数据集中最后的 24 小时作为参考，来预测“下一个 24 小时”
            last_timestamp = df['timestamp'].max()
            future_dates = [last_timestamp + pd.Timedelta(hours=i+1) for i in range(24)]
            
            future_df = pd.DataFrame({'timestamp': future_dates})
            future_df['hour'] = future_df['timestamp'].dt.hour
            future_df['weekday'] = future_df['timestamp'].dt.weekday
            future_df['is_weekend'] = (future_df['weekday'] >= 5).astype(int)
            
            # 构造特征
            last_24h_data = df.sort_values('timestamp').tail(24)['efficiency_score'].values
            if len(last_24h_data) < 24:
                 last_24h_data = np.pad(last_24h_data, (24-len(last_24h_data), 0), 'edge')
            future_df['lag_24h'] = last_24h_data
            
            current_rolling = df_train['rolling_mean_7d'].iloc[-1]
            future_df['rolling_mean_7d'] = current_rolling
            
            # 预测
            preds = self.xgb_model.predict(future_df[features])
            predicted_scores = np.maximum(0, preds) # 确保非负
            
            print(" [智能层] XGBoost 预测模型训练完成，已生成未来 24h 趋势。")
            return predicted_scores
            
        except Exception as e:
            print(f" [智能层] 预测失败: {str(e)}")
            return None

    def _create_time_features(self, df):
        df = df.sort_values('timestamp')
        df['hour'] = df['timestamp'].dt.hour
        df['weekday'] = df['timestamp'].dt.weekday
        df['is_weekend'] = (df['weekday'] >= 5).astype(int)
        df['lag_24h'] = df['efficiency_score'].shift(24)
        df['rolling_mean_7d'] = df['efficiency_score'].rolling(window=24*7, min_periods=1).mean()
        return df