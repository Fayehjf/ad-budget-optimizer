import pandas as pd
import numpy as np
import json
import os

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

class AdBudgetOptimizer:
    def __init__(self, data_path):
        """
        初始化优化器。
        """
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"错误：找不到输入文件 '{data_path}'。请确保该文件位于当前目录下。")
            
        self.df = pd.read_csv(data_path)
        self._preprocess_data()

    def _preprocess_data(self):
        """
        数据预处理与特征工程。
        """
        numeric_cols = ['spend', 'revenue', 'roas', 'orders', 'impressions', 'clicks']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(0)

        if 'date' in self.df.columns:
            try:
                self.df['date'] = pd.to_datetime(self.df['date'])
            except Exception:
                pass

        # *** 核心逻辑：复合效率指标 ***
        self.df['efficiency_score'] = self.df['revenue'] * np.log1p(self.df['roas'])

    def optimize_hourly_pacing(self, target_campaign, daily_budget, smoothing_window=3):
        """
        任务一：小时级平滑分配 (Pacing)。
        """
        camp_data = self.df[self.df['campaign_name'] == target_campaign]
        
        if camp_data.empty:
            return {}

        hourly_stats = camp_data.groupby('hour')['efficiency_score'].mean().reset_index()

        full_hours = pd.DataFrame({'hour': range(24)})
        hourly_stats = pd.merge(full_hours, hourly_stats, on='hour', how='left').fillna(0)

        epsilon = 0.05 * hourly_stats['efficiency_score'].mean()
        weights = hourly_stats['efficiency_score'] + epsilon

        # 循环移动平均 (Circular Smoothing)
        padded_weights = pd.concat([weights.iloc[-1:], weights, weights.iloc[:1]])
        smoothed_weights = padded_weights.rolling(window=smoothing_window, center=True).mean().dropna()
        
        normalized_weights = smoothed_weights / smoothed_weights.sum()
        hourly_allocation = (normalized_weights * daily_budget).round(2)
        
        return {str(int(h)): val for h, val in zip(hourly_stats['hour'], hourly_allocation)}

    def optimize_portfolio_allocation(self, total_budget, campaigns_whitelist=None):
        """
        任务二：多广告活动预算分配 (Portfolio Allocation)。
        """
        summary = self.df.groupby('campaign_name').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'daily_budget': 'max' 
        }).reset_index()

        summary['global_roas'] = summary['revenue'] / (summary['spend'] + 0.01)
        
        if campaigns_whitelist:
            summary = summary[summary['campaign_name'].isin(campaigns_whitelist)]

        summary = summary.sort_values(by='global_roas', ascending=False)
        
        remaining_budget = total_budget
        allocation_result = {}
        allocation_rationale = {}

        for _, row in summary.iterrows():
            camp_name = row['campaign_name']
            camp_cap = row['daily_budget']
            camp_roas = row['global_roas']
            
            amount = min(remaining_budget, camp_cap)
            if amount < 0: amount = 0
                
            allocation_result[camp_name] = round(amount, 2)
            remaining_budget -= amount
            
            if amount == camp_cap:
                status = "Full Budget (High Efficiency)"
            elif amount > 0:
                status = "Partial Budget (Budget Exhausted)" 
            else:
                status = "No Budget (Low Efficiency)" 
            
            allocation_rationale[camp_name] = f"ROAS: {camp_roas:.2f}, Status: {status}"

            if remaining_budget <= 0:
                break
        
        for camp in summary['campaign_name']:
            if camp not in allocation_result:
                allocation_result[camp] = 0.0
                allocation_rationale[camp] = "ROAS: Low, Status: No Budget"
                
        return allocation_result, remaining_budget, allocation_rationale

    def generate_report(self, output_file):
        """
        生成 JSON 格式的最终策略报告。
        """
        print("正在运行预算优化算法...")
        
        # --- 任务一输出：小时级平滑 (以 Campaign_A 为例) ---
        task1_campaign = "Campaign_A"
        camp_a_budget = self.df[self.df['campaign_name'] == task1_campaign]['daily_budget'].max()
        
        if pd.isna(camp_a_budget): 
            camp_a_budget = 20.0
        
        weekly_strategy = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        hourly_dist = self.optimize_hourly_pacing(task1_campaign, camp_a_budget)
        
        for day in days:
            weekly_strategy[day] = {
                "daily_budget": camp_a_budget,
                "hourly_allocation": hourly_dist,
                "total": sum(hourly_dist.values())
            }

        task1_output = {
            "campaign_name": task1_campaign,
            "methodology": "Weighted Circular Moving Average (循环加权移动平均)",
            "weekly_budget_strategy": weekly_strategy
        }

        # --- 任务二输出：多活动分配 ---
        total_pot = 100.0
        all_camps = self.df['campaign_name'].unique().tolist()
        alloc_map, leftover, rationale = self.optimize_portfolio_allocation(total_pot, all_camps)
        
        task2_output = {
            "total_budget_constraint": total_pot,
            "optimization_target": "Maximize Revenue (Greedy ROAS Strategy)",
            "final_allocation": alloc_map,
            "unallocated_budget": round(leftover, 2),
            "allocation_rationale": rationale
        }

        final_report = {
            "task_1_hourly_pacing": task1_output,
            "task_2_portfolio_optimization": task2_output
        }

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=4, ensure_ascii=False, cls=NpEncoder)
            print(f"成功：优化结果已保存至 '{output_file}'")
        except Exception as e:
            print(f"错误：保存报告失败 - {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    INPUT_FILE = os.path.join(current_dir, '..', 'data', 'data_for_ads.csv')
    OUTPUT_FILE = os.path.join(current_dir, 'allocation_result.json')
    
    try:
        optimizer = AdBudgetOptimizer(INPUT_FILE)
        optimizer.generate_report(OUTPUT_FILE)
    except Exception as e:
        print(f"执行出错: {e}")