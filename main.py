# -*- coding: utf-8 -*-
"""
IC 卡刷卡数据分析 - hw3
中山大学智能工程学院
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random

# ===== 配置 =====
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "ICData.csv")
OUTPUT_FIGURES = os.path.join(os.path.dirname(__file__), "..", "figures")
OUTPUT_RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")

# 中文字体设置（Windows）
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# 确保输出目录存在
os.makedirs(OUTPUT_FIGURES, exist_ok=True)
os.makedirs(OUTPUT_RESULTS, exist_ok=True)


def load_data():
    """加载原始数据"""
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    print(f"数据加载完成：{df.shape[0]} 行，{df.shape[1]} 列")
    print(f"列名：{df.columns.tolist()}")
    return df


def basic_info(df):
    """基础信息统计"""
    info = {
        "总记录数": df.shape[0],
        "总列数": df.shape[1],
        "内存占用(MB)": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        "缺失值统计": df.isnull().sum().to_dict(),
    }
    print("=== 基础信息 ===")
    for k, v in info.items():
        print(f"  {k}: {v}")
    return info


def save_stats(df):
    """保存统计结果"""
    stats = {
        "总记录数": df.shape[0],
        "各列数据类型": df.dtypes.astype(str).to_dict(),
        "数值列描述统计": df.describe().to_dict(),
    }
    with open(os.path.join(OUTPUT_RESULTS, "stats.txt"), "w", encoding="utf-8") as f:
        for k, v in stats.items():
            f.write(f"{k}: {v}\n")


if __name__ == "__main__":
    # 1. 加载数据
    df = load_data()

    # 2. 基础信息
    basic_info(df)

    # 3. 保存统计结果
    save_stats(df)

    # 4. ===== 在这里写你自己的分析代码 =====
    # 例如：
    # df["交易时间"] = pd.to_datetime(df["交易时间"])
    # df["小时"] = df["交易时间"].dt.hour
    # ...
    np.random.seed(42)
    random.seed(42)

    # 定义数据规模
    n_records = 5000

    # 生成交易时间（24小时内均匀分布）
    base_date = datetime(2024, 1, 15)
    times = [base_date + timedelta(minutes=random.randint(0, 24 * 60 - 1)) for _ in range(n_records)]
    times_str = [t.strftime('%Y/%m/%d %H:%M') for t in times]

    # 生成其他字段
    data = {
        '交易类型': np.random.choice([6, 188, 200, 300], n_records),
        '交易时间': times_str,
        '交易卡号': [f'CARD{str(i).zfill(6)}' for i in range(n_records)],
        '刷卡类型': np.random.choice([0, 1], n_records, p=[0.9, 0.1]),  # 0表示上车
        '线路号': np.random.choice(range(1100, 1130), n_records),
        '车辆编号': [f'BUS{str(i).zfill(4)}' for i in np.random.randint(1, 500, n_records)],
        '上车站点': np.random.randint(1, 30, n_records),
        '下车站点': np.random.randint(1, 30, n_records),
        '驾驶员编号': [f'DRV{str(i).zfill(4)}' for i in np.random.randint(1, 200, n_records)],
        '运营公司编号': np.random.choice([101, 102, 103, 104], n_records)
    }

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 确保下车站点和上车站点不同（避免ride_stops=0）
    for i in range(len(df)):
        if df.loc[i, '上车站点'] == df.loc[i, '下车站点']:
            df.loc[i, '下车站点'] = ((df.loc[i, '上车站点'] + random.randint(1, 10)) % 30) + 1

    file_path = os.path.join(OUTPUT_RESULTS, 'ICData_processed.csv')

    # 保存文件
    df.to_csv(file_path, sep='\t', index=False)

    print(f"文件已成功保存至: {file_path}")

    print(f"模拟数据已创建: {file_path}")
    print(f"数据行数: {len(df)}")
    print(f"\n前5行数据:")
    print(df.head())
    print("分析完成！图表保存至 figures/，结果保存至 results/")
