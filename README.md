《人工智能编程语言》第3次作业 公交 IC 卡刷卡数据分析


# 李云迪-24345033-第三次人工智能编程作业
## 1. 任务拆解与 AI 协作策略
（描述你如何将6项分析任务分步拆解给 AI？先让 AI 做数据读取，再做可视化，还是一次性让 AI 完成全部代码？）
## 2. 核心 Prompt 迭代记录
（展示一次你修改 Prompt 让 AI 代码从'不符合要求'变成'符合规范'的迭代过程） 初代 Prompt：... AI 生成的问题：...（例如：用了 seaborn 替代 matplotlib 画柱状图 / 函数签名不符合要求 / PHF 计算方法错误） 优化后的 Prompt：...
## 3. Debug 记录
报错现象：热力图中文乱码 
解决过程：排查乱码原因：重新检查英文字段是否正常输出，发现英文显示正常则表明代码逻辑正确。
         询问ai，得到回复是pycharm的seaborn字体没有中文，需要更换字体，使用以下代码配置， 配置完成后依然显示失败，发现是后面matplotlab的格式覆盖了前面的字体设置，需要在格式这里重新配置一次字体。然后中文就显示正常了。
         
         # 中文字体设置（Windows）
           plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
           plt.rcParams["axes.unicode_minus"] = False
         
          
     


## 4. 人工代码审查（逐行中文注释） （贴出任务4 PHF 计算的核心代码，并加上你自己的逐行中文注释）

 # ========任务4：高峰小时系数计算==========
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
