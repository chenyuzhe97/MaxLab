import random
from itertools import combinations


def factorial(n):
    """
    专门用来计算阶乘
    返回值：阶乘结果 n!
    -------

    """
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)


def minimum_power_resolution(base, n):
    """

    参数
    ----------
    base:底数
    n：你需要计算的数字

    返回值:返回比n大的，由base控制的最小幂级数
    例如:minimum_power_resolution(2,56)，返回结果为6，因为2^6=64，大于56
    -------

    """
    power = 0
    while base ** power <= n:
        power += 1
    return power


# 计算排列组合数
def combination(n, k):
    """
    计算排列组合，肯定会的吧！
    返回值：组合数结果
    """
    return factorial(n) // (factorial(k) * factorial(n - k))


def generate_combination_codes(cards, max_combinations):
    all_combinations = []
    for r in range(max_combinations, max_combinations + 1):
        all_combinations.extend(combinations(range(len(cards)), r))

    code_mapping = {}
    code = 0
    for combination in all_combinations:
        combination_set = set(combination)
        sorted_set = sorted(combination_set)
        combination_tuple = tuple(sorted_set)
        if combination_tuple not in code_mapping:
            code_mapping[combination_tuple] = code
            code += 1

    return code_mapping


def distribution_stimulation(stim_function_number, stim_electrode_area):
    # 获取 stim_electrode_area 的长度
    length = len(stim_electrode_area)
    # 构造二进制掩码，长度与 stim_electrode_area 相同
    binary_mask = f'{stim_function_number:0{length}b}'
    reversed_electrode_area = stim_electrode_area[::-1]
    # 筛选需要保留的元素
    selected_region = [area for i, area in enumerate(reversed_electrode_area) if binary_mask[::-1][i] == '1']
    print("刺激位置为：", binary_mask)
    print("对应区域电极编号为：", selected_region)
    # stim_region(selected_region, stim_mode, 1, 0.5, array)
    # cpp程序


def deal_cards(cards, stim_electrode_area, cards_number):
    if cards_number == 4:
        original_cards = [['red_1', 0], ['red_2', 1], ['black_1', 2], ['black_2', 3]]
    elif cards_number == 8:
        original_cards = [['red_1', 0], ['red_1', 1], ['red_2', 2], ['red_2', 3],
                          ['black_1', 4], ['black_1', 5], ['black_2', 6], ['black_2', 7]]
    else:
        raise "总牌数都不知道，程序不知道怎么运行。"
    print("注意一下你的游戏总牌数为:", cards_number, "\n牌池为:", original_cards)

    length_of_distribution = 3
    scale_number = 2

    length_cards = len(original_cards)
    combinations_count = combination(length_cards, length_of_distribution)
    maximum_coding_length = minimum_power_resolution(scale_number, combinations_count)
    code_mapping = generate_combination_codes(original_cards, length_of_distribution)

    print("最大编码长度为:", maximum_coding_length)
    print("能容纳组合的最大长度为:", 2 ** maximum_coding_length)
    print("当前组合数量为:", combinations_count)
    print("对应编码表为：", code_mapping)

    mapping_cards = cards
    mapping_cards = sorted(mapping_cards, key=lambda x: x[1])
    mapping_id = [cards_number[1] for cards_number in mapping_cards]
    mapping_id = tuple(mapping_id)
    stim_function_number = code_mapping[mapping_id]
    print("当前编码表为:", mapping_id)
    print("调用的刺激方案为：", stim_function_number)
    distribution_stimulation(stim_function_number + 1, stim_electrode_area)


if __name__ == '__main__':
    # # 传入的cards应该放这里
    stim_electrode_area = [6, 7, 8, 9]
    cards = [['red_1', 0], ['red_2', 1], ['black_1', 2], ['black_2', 3]]
    cards = random.sample(cards, 3)
    organ_cards = cards[:3]
    deal_cards(cards, stim_electrode_area, 4)
