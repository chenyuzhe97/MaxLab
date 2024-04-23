import time
import os
import csv
import re
import pandas as pd
from elecsvread import get_ele, get_ele2, read_cfg

debug = 0


def extract_txt():
    file_path = 'celebration.txt'

    # 使用正则表达式提取数值
    #
    pattern = r':\s*(\d+\.?\d*)'

    # 使用正则表达式找到所有匹配项

    with open(file_path, 'r') as file:
        content = file.read()
        matches = re.findall(pattern, content)
        numbers = [float(match) for match in matches]
        print(numbers)
    percentage = []
    for n in numbers:
        print(type(n))
        percentage.append(n / sum(numbers))
    return percentage


def count_numeric_lines(csv_file, data):
    Q_all = {'A': 0, 'B': 0, 'C': 0}
    start_time = time.time()  # 记录开始时间
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        # count = sum(1 for row in reader if any(re.match(r'^-?\d+(?:\.\d+)?$', item) for item in row))
        # 遍历并打印每一行
        for row in reader:
            if len(row) == 2:
                num = int(row[0])
                val = float(row[1])
                if num in data['A']:
                    Q_all['A'] += 1
                elif num in data['B']:
                    Q_all['B'] += 1
                elif num in data['C']:
                    Q_all['C'] += 1
    end_time = time.time()  # 记录结束时间
    execution_time = end_time - start_time  # 计算代码执行时间
    for key, value in Q_all.items():
        if debug == 1:
            print(key, value)
    return Q_all, execution_time


def suan_pai():
    result = []

    # 新方法
    filename = read_cfg()
    data = get_ele2(filename)

    # 老方法
    # data = get_ele2("ele_number5.csv")
    # print("mydata",data['B'])
    # 设置检测路径和文件扩展名
    monitor_path = '/home/admin1/Desktop/env/maxlab_lib/build/'

    file_extension = '.csv'

    # 初始化上次检测到的文件列表
    last_checked_files = set()

    # 设置阈值和统计变量
    threshold = 350  # 设置阈值为350
    total_checks = 0  # 记录总共检测的次数
    spikes_over_threshold = 0  # 记录超过阈值的次数
    new_file = 3

    # 外部大循环，执行40次
    # 在两次大循环之间等待5秒

    # for n in range(0, 1):
    #     for i in list:
    #         sim(i[0], i[1], i[2], i[3])
    #     # time.sleep(0.09)

    # 获取当前路径下的所有 CSV 文件
    #       current_files = set(file for file in os.listdir(monitor_path) if file.endswith(file_extension))
    current_files = set(
        os.path.join(monitor_path, file) for file in os.listdir(monitor_path) if file.endswith(file_extension))

    # print(current_files)
    if len(current_files) >= 1:
        # 只考虑最新的50个CSV文件
        latest_files = sorted(current_files, key=os.path.getmtime, reverse=True)[:1]

        # 检查是否有新文件出现
        new_files = set(latest_files) - last_checked_files

        if new_files:
            if debug == 1:
                print("New CSV file(s) detected:", new_files)
            # 对每个新文件执行代码
            for new_file in new_files:
                csv_file_path = os.path.join(monitor_path, new_file)
                numeric_line_count, runtime = count_numeric_lines(csv_file_path, data)

                def celibrate(numeric_line_count):
                    n = extract_txt()
                    print('i am n', n)
                    for i in range(len(n)):
                        n[i] = float(n[i])
                    numeric_line_count['A'] /= n[0]
                    numeric_line_count['B'] /= n[1]
                    numeric_line_count['C'] /= n[2]
                    return numeric_line_count

                numeric_line_count = celibrate(numeric_line_count)
                print(numeric_line_count)

                result.append(numeric_line_count)
                if debug == 1:
                    print(f"Number of spikes in {new_file}: {numeric_line_count}")
                    print("Execution time:", runtime, "seconds")

                # 计算超过阈值的百分比

                total_checks += 1

                # 每3秒钟输出一次百分比            if total_checks >= 50:
                #                 percentage = (spikes_over_threshold / 50) * 100
                #                 print(f"Percentage of spikes over threshold: {percentage:.2f}%")
                #
                #         # 更新检测次数
                # if total_checks % 6 == 0:  # 每3秒钟执行一次（6个循环是3秒）
                percentage = (spikes_over_threshold / total_checks) * 100
                print(f"Percentage of spikes over threshold: {percentage:.2f}%")

        # 更新上次检测到的文件列表
        last_checked_files = current_files

    def dapaishunxu(data):
        # A:113 B:1344 C:15555
        # 假设我们只处理列表中的第一个字典
        dic = data[0]
        print("dapaishunxudata", data)
        print("dic", dic)
        # 获取字典的值，并倒序排序
        values_list = list(dic.values())
        # 对原始列表的索引按照对应值的大小进行排序（从大到小）
        indices_sorted_by_value = sorted(range(len(values_list)), key=lambda x: values_list[x], reverse=True)

        # 由于索引是从0开始的，为了方便理解，我们将索引加1进行编号
        indices_sorted_with_natural_numbers = [index + 1 for index in indices_sorted_by_value]
        output_list = [index - 1 for index in indices_sorted_with_natural_numbers]

        print(output_list)

        return output_list

    return dapaishunxu(result)


if __name__ == "__main__":
    suan_pai()
