《人工智能编程语言》第3次作业 公交 IC 卡刷卡数据分析


# 李云迪-24345033-第三次人工智能编程作业

## 1. 任务拆解与 AI 协作策略
我是分别把六个任务交给AI的，我首先把作业要求的第三方库的硬性要求告诉AI，然后开始任务。
任务1：数据预处理
首先引导AI完成数据读取与基础清洗，重点验证其是否正确使用制表符分隔符读取ICData.csv，并成功构造ride_stops字段。人工确认异常值（ride_stops == 0）被准确识别并删除，同时检查缺失值处理逻辑的合理性。
任务2：时间分布分析
明确要求AI使用numpy实现早晚时段刷卡量统计，避免仅依赖pandas；同时强制指定使用matplotlib.pyplot绘制24小时柱状图，确保图表风格、颜色高亮、中文标签和网格线等格式合规。
任务3：线路站点分析
严格限定函数签名必须为analyze_route_stops(df, route_col='线路号', stops_col='ride_stops')，防止AI擅自修改参数名。可视化部分则要求使用seaborn.barplot生成带误差棒的水平条形图，体现统计稳定性。
任务4：高峰小时系数计算
强调“自动识别”高峰小时的核心要求，避免手动指定时间段。通过结构化Prompt指导AI先进行小时级聚合，再在高峰小时内按5分钟和15分钟粒度重新切片，最终正确计算PHF5与PHF15。
任务5：线路驾驶员信息批量导出
指导AI筛选线路1101–1120范围内的记录，在根目录创建线路驾驶员信息文件夹，并为每条线路生成独立txt文件，内容包含去重后的车辆编号与驾驶员编号映射关系。
任务6：服务绩效排名与热力图
要求AI分别统计Top 10司机、线路、上车站点和车辆的服务人次，构建4×10矩阵后使用seaborn.heatmap绘制成热力图，确保标注数值、配色方案和坐标轴标签均符合规范。
首先就是我要求按照搭建github开源项目的格式进行开发，于是生成了hw3这个新项目并连接到仓库，自动生成了src、main、init、figure等文件夹方便管理查看。
整个开发过程遵循迭代式开发模式，每个任务完成后立即测试输出结果，确认无误后再进入下一阶段。

## 2. 核心 Prompt 迭代记录
在开发初期，初次提交的 Prompt 虽然概括了整体功能需求，但因指令模糊导致 AI 生成的代码未能完全符合技术规范。通过分析问题根源，对 Prompt 进行精细化重构
初代 Prompt
"开发公交IC卡数据分析程序，包含数据预处理、时间分析、站点分析等功能。
该 Prompt 存在表述宽泛、约束缺失的问题，导致 AI 在实现过程中出现以下关键错误：
库使用违规：在任务2的24小时分布图中，AI 自动选用 seaborn 替代 matplotlib 绘图，违背了“必须使用 matplotlib”的硬性要求。
接口签名偏离：AI 将 analyze_route_stops 函数参数名修改为 route_column 和 stops_column，破坏了规定的函数签名结构。
算法逻辑偏差：高峰小时系数（PHF）计算时，AI 手动指定 8:00–9:00 为高峰时段，未按要求从数据中自动识别最大刷卡量对应的时间段。
这些问题暴露出仅依赖高层次描述无法确保技术细节合规，必须通过精确指令进行引导。

优化后的 Prompt
"开发完整的公交IC卡刷卡数据分析Python程序，实现6个任务，具体要求：
时间分布分析：必须使用 numpy 统计早7点前和晚22点后刷卡量，必须使用 matplotlib（不是 seaborn）绘制24小时柱状图
线路站点分析：函数签名必须为 analyze_route_stops(df, route_col='线路号', stops_col='ride_stops')，参数名不能修改
高峰小时系数计算：必须自动识别高峰小时，计算 PHF5 和 PHF15
确保使用 numpy、pandas、matplotlib、seaborn 四个库，添加中文注释。"


## 3. Debug 记录
报错现象：热力图中文乱码 
解决过程：排查乱码原因：重新检查英文字段是否正常输出，发现英文显示正常则表明代码逻辑正确。
         询问ai，得到回复是pycharm的seaborn字体没有中文，需要更换字体，使用以下代码配置， 配置完成后依然显示失败，发现是后面matplotlab的格式覆盖了前面的字体设置，需要在格式这里重新配置一次字体。然后中文就显示正常了。
         
         # 中文字体设置（Windows）
           plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
           plt.rcParams["axes.unicode_minus"] = False
报错现象：时间解析时出现时区警告
使用 
          #
             pd.to_datetime(df['交易时间']) 解析“交易时间”列时，控制台输出以下警告信息：
             UserWarning: Parsing dates in %Y/%m/%d %H:%M format when dayfirst=False

该警告提示 pandas 在自动推断日期格式时可能存在歧义，影响解析的一致性与性能。
解决过程如下：

显式指定时间格式
由于数据中“交易时间”的格式固定为 YYYY/M/D HH:MM，直接传入 format 参数进行精确解析：

df['交易时间'] = pd.to_datetime(df['交易时间'], format='%Y/%m/%d %H:%M')
消除隐式推断风险
显式格式化避免了 pandas 对日/月顺序的猜测，提升了解析效率与准确性。
         
          
     


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
