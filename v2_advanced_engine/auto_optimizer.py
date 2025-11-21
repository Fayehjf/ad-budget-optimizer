import pandas as pd
import numpy as np
import os
from .preprocessor import DataProcessor
from .intelligence_layer import IntelligenceModule
from .allocator import BudgetAllocator
from .config import Config

class AutoBudgetOptimizer:
    """
    V2 自动化预算优化引擎
    """
    def __init__(self, total_budget=1000):
        self.total_budget = total_budget
        self.processor = DataProcessor()
        self.brain = IntelligenceModule()
        self.allocator = BudgetAllocator()

    def run(self, data_path, output_format='json'):
        print(f"\n 开始预算优化流程 | 总预算: ${self.total_budget}")
        
        try:
            df_raw = pd.read_csv(data_path)
            df_clean = self.processor.clean_and_feature_engineer(df_raw)
        except Exception as e:
            print(f"数据加载失败: {e}")
            return None
        
        print(" 正在识别流量模式与趋势...")
        cluster_info = self.brain.get_cluster_patterns(df_clean)
        forecast_curve = self.brain.predict_future_efficiency(df_clean)
        
        print(" 计算最佳预算分配权重...")
        results = []
        
        if 'category_id' not in df_clean.columns:
            # 如果没有品类区分，就当成一个整体处理
            categories = ['all']
            df_clean['category_id'] = 'all'
        else:
            categories = df_clean['category_id'].unique()

        # 遍历每个品类，匹配它真实的 Cluster
        for cat_id in categories:
            cat_data = df_clean[df_clean['category_id'] == cat_id]
            if len(cat_data) == 0: continue

            # 计算 V1 Baseline
            hourly_stats = cat_data.groupby('hour')['efficiency_score'].mean().reindex(range(24), fill_value=0).values
            v1_baseline = self.allocator.circular_moving_average(hourly_stats)
            
            # 查找该品类对应的 Cluster Curve
            current_cluster_curve = None
            found_cluster_id = "Unknown"
            
            if cluster_info and 'mapping' in cluster_info:
                cluster_id = cluster_info['mapping'].get(cat_id)
                if cluster_id is not None:
                    current_cluster_curve = cluster_info['profiles'][cluster_id]
                    found_cluster_id = str(cluster_id)

            # 计算
            final_weights = self.allocator.fuse_strategies(
                v1_weights=v1_baseline,
                cluster_curve=current_cluster_curve, # 传入该品类特定的曲线
                forecast_curve=forecast_curve        # 传入预测趋势
            )
            
            cat_budget = self.total_budget / len(categories)
            hourly_budget = final_weights * cat_budget
            
            # 结果
            for h in range(24):
                results.append({
                    'category_id': cat_id,
                    'hour': h,
                    'cluster_group': found_cluster_id, # 标记它被分到了哪一类
                    'base_weight_v1': round(v1_baseline[h], 4),
                    'final_weight_v2': round(final_weights[h], 4),
                    'recommended_budget': round(hourly_budget[h], 2)
                })

        result_df = pd.DataFrame(results)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(current_dir, f"optimization_results.{output_format}")
        
        if output_format == 'json':
            result_df.to_json(output_file, orient='records', indent=4)
        else:
            result_df.to_csv(output_file, index=False)
            
        print(f" 优化完成！结果已保存至: {os.path.abspath(output_file)}")
        print("-" * 30)
        print(result_df.head()) # 打印前几行看看
        
        return result_df