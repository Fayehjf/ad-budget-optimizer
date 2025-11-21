import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from v2_advanced_engine.auto_optimizer import AutoBudgetOptimizer

def main():
    data_path = os.path.join(parent_dir, 'data', 'data_for_ads.csv')

    if not os.path.exists(data_path):
        print(f"错误: 找不到文件。请检查路径是否正确: {data_path}")
        return

    # 初始化引擎 (总预算 2000)
    optimizer = AutoBudgetOptimizer(total_budget=2000)

    # 运行优化
    optimizer.run(data_path) 

if __name__ == "__main__":
    main()