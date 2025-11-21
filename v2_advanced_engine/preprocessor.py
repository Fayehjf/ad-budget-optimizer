import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self):
        pass

    def clean_and_feature_engineer(self, df):
        """
        清洗数据并生成 V1/V2 所需的基础特征
        """
        print("  [预处理] 正在清洗数据并生成特征...")
        df = df.copy()

        
        # 如果没有 category_id，默认归为 "Default_Category"
        if 'category_id' not in df.columns:
            df['category_id'] = 'Default_Category'

        # 如果没有 timestamp 但有 hour，自动生成一个伪造的 timestamp (假设是今天)
        if 'timestamp' not in df.columns and 'hour' in df.columns:
            today = pd.Timestamp.now().normalize()
            # 为每一行生成一个带日期的时间戳
            df['timestamp'] = df['hour'].apply(lambda h: today + pd.Timedelta(hours=int(h)))


        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['weekday'] = df['timestamp'].dt.weekday
            df['is_weekend'] = df['weekday'].apply(lambda x: 1 if x >= 5 else 0)
        
        # 计算复合指标
        if 'revenue' in df.columns and 'roas' in df.columns:
            df['efficiency_score'] = df['revenue'] * np.log1p(df['roas'])
        else:
            df['efficiency_score'] = 0

        df = df.fillna(0)
        
        print(f" [预处理] 完成。已自动兼容数据结构。")
        return df