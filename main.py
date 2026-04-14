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

    # 1.2 将「交易时间」字段转换为datetime类型，并提取小时整数
    print("\n【步骤2】解析交易时间并提取小时...")
    # 使用pd.to_datetime将字符串时间转换为datetime对象
    df['交易时间'] = pd.to_datetime(df['交易时间'], format='%Y/%m/%d %H:%M')
    # 使用dt.hour属性提取小时整数，创建新列hour
    df['hour'] = df['交易时间'].dt.hour
    print(f"时间解析完成，hour列范围: {df['hour'].min()} - {df['hour'].max()}")
    # 1.3 计算搭乘站点数=abs(下车站点-上车站点)，构造新列ride_stops
    print("\n【步骤3】计算搭乘站点数...")
    # 使用abs函数计算绝对值，得到搭乘站点数
    df['ride_stops'] = abs(df['下车站点'] - df['上车站点'])
    print(
        f"ride_stops统计: 最小值={df['ride_stops'].min()}, 最大值={df['ride_stops'].max()}, 平均值={df['ride_stops'].mean():.2f}")

    # 1.4 删除ride_stops=0的异常记录
    print("\n【步骤4】删除异常记录...")
    # 记录删除前的行数
    rows_before = len(df)
    # 筛选出ride_stops不为0的记录
    df = df[df['ride_stops'] != 0]
    # 计算删除的行数
    rows_deleted = rows_before - len(df)
    print(f"删除ride_stops=0的记录数: {rows_deleted} 行")
    print(f"剩余记录数: {len(df)} 行")

    # 1.5 检查并处理缺失值
    print("\n【步骤5】检查缺失值...")
    # 使用isnull().sum()统计每列的缺失值数量
    missing_values = df.isnull().sum()
    print("各列缺失值数量:")
    print(missing_values)

    # 处理策略说明
    if missing_values.sum() > 0:
        print("\n缺失值处理策略:")
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in ['int64', 'float64']:
                    # 数值型列使用均值填充
                    mean_val = df[col].mean()
                    df[col].fillna(mean_val, inplace=True)
                    print(f"  - {col}: 使用均值({mean_val:.2f})填充")
                else:
                    # 非数值型列使用众数填充
                    mode_val = df[col].mode()[0]
                    df[col].fillna(mode_val, inplace=True)
                    print(f"  - {col}: 使用众数({mode_val})填充")
    else:
        print("数据无缺失值，无需处理")

    print("\n任务1完成！")
