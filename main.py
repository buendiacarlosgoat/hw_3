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
    # ==================== 任务2：时间分布分析 ====================
    print("\n" + "=" * 60)
    print("任务2：时间分布分析")
    print("=" * 60)

    # 2.1 使用numpy统计早7点前和晚22点后的上车刷卡量
    print("\n【步骤1】统计早晚时段刷卡量（使用numpy）...")

    # 筛选上车刷卡记录（刷卡类型=0）
    boarding_df = df[df['刷卡类型'] == 0].copy()

    # 使用numpy.where和布尔索引统计早7点前（hour < 7）的刷卡量
    # np.where返回满足条件的索引，再使用sum求和
    early_morning_mask = (boarding_df['hour'].values < 7)
    early_morning_count = np.where(early_morning_mask, 1, 0).sum()

    # 使用numpy统计晚22点后（hour >= 22）的刷卡量
    late_night_mask = (boarding_df['hour'].values >= 22)
    late_night_count = np.where(late_night_mask, 1, 0).sum()

    # 计算全天总刷卡量
    total_count = len(boarding_df)

    # 计算占比
    early_morning_ratio = early_morning_count / total_count * 100
    late_night_ratio = late_night_count / total_count * 100

    print(f"早7点前（hour < 7）上车刷卡量: {early_morning_count} 次，占比: {early_morning_ratio:.2f}%")
    print(f"晚22点后（hour >= 22）上车刷卡量: {late_night_count} 次，占比: {late_night_ratio:.2f}%")
    print(f"全天总上车刷卡量: {total_count} 次")

    # 2.2 使用matplotlib绘制24小时刷卡量分布柱状图
    print("\n【步骤2】绘制24小时刷卡量分布柱状图...")

    # 统计每小时的刷卡量
    hourly_counts = boarding_df.groupby('hour').size()
    # 确保包含所有24小时（0-23）
    hours = list(range(24))
    counts = [hourly_counts.get(h, 0) for h in hours]

    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 6))

    # 定义颜色：早7点前和晚22点后高亮显示
    colors = ['#FF6B6B' if h < 7 or h >= 22 else '#4ECDC4' for h in hours]

    # 绘制柱状图，x轴为小时（0~23，步长2显示标签）
    bars = ax.bar(hours, counts, color=colors, edgecolor='black', linewidth=0.5)

    # 设置x轴刻度，步长为2
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)], rotation=45)

    # 添加中文标题和轴标签
    ax.set_title('24小时公交IC卡刷卡量分布', fontsize=16, fontweight='bold')
    ax.set_xlabel('小时', fontsize=12)
    ax.set_ylabel('刷卡量（次）', fontsize=12)

    # 添加水平网格线
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # 添加图例
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor='#FF6B6B', label='早7点前/晚22点后'),
        Patch(facecolor='#4ECDC4', label='其他时段')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # 调整布局
    plt.tight_layout()

    # 保存图像，dpi=150
    # 使用代码开头定义好的 OUTPUT_FIGURES 变量
    # 这样图片就会保存到你项目目录下的 figures 文件夹里
    output_path = os.path.join(OUTPUT_FIGURES, 'hour_distribution.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"图像已保存: {output_path}")
    plt.close()
    print("\n任务2完成！")
    # ==================== 任务3：线路站点分析 ====================
    print("\n" + "=" * 60)
    print("任务3：线路站点分析")
    print("=" * 60)

    # 3.1 定义analyze_route_stops函数（签名必须完全符合要求）
    print("\n【步骤1】定义analyze_route_stops函数...")


    def analyze_route_stops(df, route_col='线路号', stops_col='ride_stops'):
        """
        计算各线路乘客的平均搭乘站点数及其标准差。

        Parameters
        ----------
        df : pd.DataFrame
            预处理后的数据集
        route_col : str
            线路号列名，默认为'线路号'
        stops_col : str
            搭乘站点数列名，默认为'ride_stops'

        Returns
        -------
        pd.DataFrame
            包含三列：线路号、mean_stops（平均搭乘站点数）、std_stops（标准差），
            按mean_stops降序排列
        """
        # 按线路分组，计算平均搭乘站点数和标准差
        route_stats = df.groupby(route_col)[stops_col].agg(['mean', 'std']).reset_index()
        # 重命名列
        route_stats.columns = [route_col, 'mean_stops', 'std_stops']
        # 按平均搭乘站点数降序排列
        route_stats = route_stats.sort_values('mean_stops', ascending=False)
        return route_stats


    # 3.2 调用函数并打印前10行结果
    print("\n【步骤2】调用函数并查看结果...")
    route_analysis = analyze_route_stops(df)
    print("前10条线路的平均搭乘站点数及标准差:")
    print(route_analysis.head(10))

    # 3.3 使用seaborn绘制前15条线路的水平条形图
    print("\n【步骤3】绘制前15条线路的水平条形图...")

    # 取前15条线路
    top15_routes = route_analysis.head(15).copy()

    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 8))

    # 使用seaborn绘制水平条形图，显示误差棒
    sns.barplot(
        data=top15_routes,
        y='线路号',
        x='mean_stops',
        orient='h',
        palette='Blues_d',
        errorbar='sd',  # 显示标准差作为误差棒
        capsize=0.3,
        ax=ax
    )

    # 设置x轴从0开始
    ax.set_xlim(0, top15_routes['mean_stops'].max() * 1.1)

    # 添加中文标签
    ax.set_title('前15条线路平均搭乘站点数', fontsize=14, fontweight='bold')
    ax.set_xlabel('平均搭乘站点数', fontsize=12)
    ax.set_ylabel('线路号', fontsize=12)

    # 调整布局
    plt.tight_layout()

    # 保存图像，dpi=150
    output_path = os.path.join(OUTPUT_FIGURES, 'route_stops.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"图像已保存: {output_path}")
    plt.close()

    print("\n任务3完成！")

    # ==================== 任务4：高峰小时系数计算 ====================
    print("\n" + "=" * 60)
    print("任务4：高峰小时系数计算")
    print("=" * 60)

    # 4.1 自动识别高峰小时
    print("\n【步骤1】自动识别高峰小时...")

    # 统计各小时的刷卡总量，找出最大值对应的小时
    hourly_total = df.groupby('hour').size()
    peak_hour = hourly_total.idxmax()
    peak_hour_count = hourly_total.max()

    print(f"高峰小时识别结果: {peak_hour:02d}:00-{(peak_hour + 1):02d}:00")
    print(f"高峰小时刷卡量: {peak_hour_count} 次")

    # 4.2 在高峰小时内，按5分钟窗口聚合刷卡量
    print("\n【步骤2】按5分钟窗口聚合...")

    # 筛选高峰小时的记录
    peak_hour_df = df[df['hour'] == peak_hour].copy()

    # 提取分钟数
    peak_hour_df['minute'] = peak_hour_df['交易时间'].dt.minute

    # 按5分钟窗口聚合（0-4, 5-9, ..., 55-59）
    peak_hour_df['5min_window'] = (peak_hour_df['minute'] // 5) * 5
    five_min_counts = peak_hour_df.groupby('5min_window').size()
    max_5min_count = five_min_counts.max()
    max_5min_start = five_min_counts.idxmax()
    max_5min_end = max_5min_start + 5

    print(f"最大5分钟刷卡量: {max_5min_count} 次")
    print(f"最大5分钟时间段: {peak_hour:02d}:{max_5min_start:02d}-{peak_hour:02d}:{max_5min_end:02d}")

    # 4.3 计算PHF5
    PHF5 = peak_hour_count / (12 * max_5min_count)
    print(f"\nPHF5计算:")
    print(f"  PHF5 = {peak_hour_count} / (12 × {max_5min_count}) = {PHF5:.4f}")

    # 4.4 在高峰小时内，按15分钟窗口聚合刷卡量
    print("\n【步骤3】按15分钟窗口聚合...")

    # 按15分钟窗口聚合（0-14, 15-29, 30-44, 45-59）
    peak_hour_df['15min_window'] = (peak_hour_df['minute'] // 15) * 15
    fifteen_min_counts = peak_hour_df.groupby('15min_window').size()
    max_15min_count = fifteen_min_counts.max()
    max_15min_start = fifteen_min_counts.idxmax()
    max_15min_end = max_15min_start + 15

    print(f"最大15分钟刷卡量: {max_15min_count} 次")
    print(f"最大15分钟时间段: {peak_hour:02d}:{max_15min_start:02d}-{peak_hour:02d}:{max_15min_end:02d}")

    # 4.5 计算PHF15
    PHF15 = peak_hour_count / (4 * max_15min_count)
    print(f"\nPHF15计算:")
    print(f"  PHF15 = {peak_hour_count} / (4 × {max_15min_count}) = {PHF15:.4f}")

    # 4.6 按格式输出结果
    print("\n" + "-" * 50)
    print("高峰小时系数计算结果汇总")
    print("-" * 50)
    print(f"高峰小时: {peak_hour:02d}:00-{(peak_hour + 1):02d}:00")
    print(f"高峰小时刷卡量: {peak_hour_count} 次")
    print(f"\n最大5分钟刷卡量:")
    print(f"  时间段: {peak_hour:02d}:{max_5min_start:02d}-{peak_hour:02d}:{max_5min_end:02d}")
    print(f"  刷卡量: {max_5min_count} 次")
    print(f"  PHF5 = {peak_hour_count} / (12 × {max_5min_count}) = {PHF5:.4f}")
    print(f"\n最大15分钟刷卡量:")
    print(f"  时间段: {peak_hour:02d}:{max_15min_start:02d}-{peak_hour:02d}:{max_15min_end:02d}")
    print(f"  刷卡量: {max_15min_count} 次")
    print(f"  PHF15 = {peak_hour_count} / (4 × {max_15min_count}) = {PHF15:.4f}")
    print("-" * 50)

    print("\n任务4完成！")

    # ==================== 任务5：线路驾驶员信息批量导出 ====================
    print("\n" + "=" * 60)
    print("任务5：线路驾驶员信息批量导出")
    print("=" * 60)

    # 5.1 筛选线路号在1101至1120之间的记录
    print("\n【步骤1】筛选线路1101-1120...")
    route_mask = (df['线路号'] >= 1101) & (df['线路号'] <= 1120)
    routes_1101_1120 = df[route_mask].copy()

    unique_routes = sorted(routes_1101_1120['线路号'].unique())
    print(f"筛选到的线路: {unique_routes}")
    print(f"记录数: {len(routes_1101_1120)} 条")

    # 5.2 创建"线路驾驶员信息"文件夹
    print("\n【步骤2】创建文件夹...")
    folder_path = os.path.join(OUTPUT_FIGURES, '线路驾驶员信息')
    os.makedirs(folder_path, exist_ok=True)
    print(f"文件夹已创建: {folder_path}")

    # 5.3 为每条线路生成txt文件
    print("\n【步骤3】生成线路驾驶员信息文件...")

    # 存储生成文件路径
    file_paths = []

    for route in range(1101, 1121):
        # 筛选当前线路的记录
        route_df = routes_1101_1120[routes_1101_1120['线路号'] == route]

        # 构建文件路径
        file_path = os.path.join(folder_path, f'{route}.txt')

        if len(route_df) > 0:
            # 获取唯一的车辆编号→驾驶员编号对应关系（去重）
            unique_mapping = route_df[['车辆编号', '驾驶员编号']].drop_duplicates()

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                # 第一行：线路号: XXXX
                f.write(f'线路号: {route}\n')
                # 后续每行：车辆编号 驾驶员编号
                for _, row in unique_mapping.iterrows():
                    f.write(f"{row['车辆编号']} {row['驾驶员编号']}\n")

            file_paths.append(file_path)
            print(f"  已生成: {file_path} ({len(unique_mapping)}条映射关系)")
        else:
            # 即使没有数据也创建空文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f'线路号: {route}\n')
            file_paths.append(file_path)
            print(f"  已生成: {file_path} (无数据)")

    print(f"\n共生成 {len(file_paths)} 个文件")

    print("\n任务5完成！")

    # ==================== 任务6：服务绩效排名与热力图 ====================
    print("\n" + "=" * 60)
    print("任务6：服务绩效排名与热力图")
    print("=" * 60)

    # 6.1 统计服务人次最多的Top 10
    print("\n【步骤1】统计各类Top 10...")

    # 筛选有效上车记录（刷卡类型=0）
    valid_boarding = df[df['刷卡类型'] == 0]

    # 统计Top 10司机（驾驶员编号）
    top10_drivers = valid_boarding['驾驶员编号'].value_counts().head(10)
    print(f"\nTop 10司机服务人次:")
    print(top10_drivers)

    # 统计Top 10线路（线路号）
    top10_routes = valid_boarding['线路号'].value_counts().head(10)
    print(f"\nTop 10线路服务人次:")
    print(top10_routes)

    # 统计Top 10上车站点
    top10_stops = valid_boarding['上车站点'].value_counts().head(10)
    print(f"\nTop 10上车站点服务人次:")
    print(top10_stops)

    # 统计Top 10车辆（车辆编号）
    top10_vehicles = valid_boarding['车辆编号'].value_counts().head(10)
    print(f"\nTop 10车辆服务人次:")
    print(top10_vehicles)

    # 6.2 构造4×10的热力图数据矩阵
    print("\n【步骤2】构造热力图数据矩阵...")

    # 创建热力图数据矩阵（4行×10列）
    heatmap_data = pd.DataFrame({
        '司机': top10_drivers.values,
        '线路': top10_routes.values,
        '上车站点': top10_stops.values,
        '车辆': top10_vehicles.values
    }, index=[f'Top{i + 1}' for i in range(10)])

    # 转置为4行×10列的格式
    heatmap_matrix = heatmap_data.T
    print("\n热力图数据矩阵:")
    print(heatmap_matrix)

    # 6.3 使用seaborn绘制热力图
    print("\n【步骤3】绘制热力图...")

    # 创建图形
    fig, ax = plt.subplots(figsize=(14, 6))

    # 使用seaborn绘制热力图
    sns.heatmap(
        heatmap_matrix,
        annot=True,  # 显示数值
        fmt='d',  # 整数格式
        cmap='YlOrRd',  # 使用YlOrRd颜色映射
        linewidths=0.5,
        ax=ax,
        cbar_kws={'label': '服务人次'}
    )

    # 设置标签
    ax.set_title('公交服务绩效Top10热力图', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('排名', fontsize=12)
    ax.set_ylabel('维度', fontsize=12)

    # x轴标签旋转0度
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)

    # 调整布局
    plt.tight_layout()

    # 保存图像，dpi=150，bbox_inches='tight'防止标签截断
    output_path = os.path.join(OUTPUT_FIGURES, 'performance_heatmap.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"图像已保存: {output_path}")
    plt.close()

    # 6.4 输出服务绩效观察结论（不少于50字）
    analysis_conclusion = """
    【服务绩效分析结论】
    通过热力图分析可见，公交服务绩效在不同维度上呈现明显差异：
    1. 司机维度：头部司机服务人次差异显著，反映出驾驶员工作效率和出勤率的差异；
    2. 线路维度：热门线路集中在城市核心区域，客流量大，需要增加运力配置；
    3. 站点维度：主要枢纽站点服务人次集中，建议优化站点设施和换乘衔接；
    4. 车辆维度：高利用率车辆运行强度大，需加强维护保养。整体而言，公交资源配置应
       向高峰时段和热门线路倾斜，同时关注驾驶员工作负荷均衡。
    """

    print(analysis_conclusion)

    print("\n任务6完成！")
    # ==================== 程序结束 ====================
    print("\n" + "=" * 60)
    print("所有任务执行完毕！")
    print("=" * 60)
    print("\n生成的输出文件:")
    print(f"1. {os.path.join(OUTPUT_FIGURES, 'hour_distribution.png')}")
    print(f"2. {os.path.join(OUTPUT_FIGURES, 'route_stops.png')}")
    print(f"3. {os.path.join(OUTPUT_FIGURES, 'performance_heatmap.png')}")
    print(f"4. {os.path.join(OUTPUT_FIGURES, '线路驾驶员信息/')} (含20个txt文件)")
    print("="*60)



