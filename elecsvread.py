import pandas as pd
import re


def extract_numbers_from_cfg(file_path):
    # 打开文件
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 使用正则表达式找到所有括号内的内容
    matches = re.findall(r'\((.*?)\)', content)

    # 初始化一个空列表来存储所有数字
    numbers = []

    # 遍历匹配的内容，进一步提取数字
    for match in matches:
        # 在当前括号内容中查找数字
        numbers_in_match = re.findall(r'\d+', match)

        # 将找到的数字添加到列表中
        numbers.extend(numbers_in_match)

    return numbers


def flatten_nested_list(nested_list):
    flattened_list = [item for sublist in nested_list for item in sublist]
    return flattened_list


def selcet_ele(data, region):
    # 当年跳着写的
    step = 17
    data = data[data['Region'] == region]
    data = data.iloc[::step]
    data.iloc[:, 1:]
    data = data.iloc[:, 1:].values.tolist()
    data = flatten_nested_list(data)
    return data


def selcet_ele2(data, region):
    # 新方法，现在都用这个
    data = data[data['Region'] == region]
    data = data.iloc[::]
    data.iloc[:, 1:]
    data = data.iloc[:, 1:].values.tolist()
    data = flatten_nested_list(data)
    return data


def get_ele(filename=None):
    # 用电极编号定位
    data = pd.read_csv(filename, usecols=[0, 2])
    ele = ['D', 'E', 'F']
    ele_all = dict()
    for i in ele:
        dataA = selcet_ele2(data, i)
        ele_all[i] = dataA
    return ele_all


def get_ele2(filename=None):
    # 用通道定位
    data = pd.read_csv(filename, usecols=[0, 1])
    print("算牌：",data)
    ele = ['A', 'B', 'C']
    ele_all = dict()
    for i in ele:
        dataA = selcet_ele2(data, i)
        ele_all[i] = dataA
    return ele_all


def write_to_file(data):
    file_name = 'cfg.txt'
    with open(file_name, 'w') as file:
        file.write(data)


def read_cfg(file_name='cfg.txt'):
    with open(file_name, 'r') as file:
        contents = file.read()
        return contents


if __name__ == '__main__':
    data = get_ele()
    print(data)
