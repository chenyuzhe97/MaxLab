import random
from itertools import combinations




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

def calculate_code(card_list, code_mapping):
    card_set = set(card_list)
    sorted_set = sorted(card_set)
    combination_tuple = tuple(sorted_set)
    return code_mapping[combination_tuple]

def stim_ruler(area,mode):
    # 等我吃完饭再写！！！
    pass
    # area_mapping = {
    #     0:,
    # 1:,
    # 2:,
    # 3:,
    # }

cards = [['red_1', 0], ['red_2', 1], ['black_1', 2], ['black_2', 3]]
cards = random.sample(cards, 4)
organ_cards = cards[:3]

code_mapping = generate_combination_codes(cards, 3)
print(code_mapping)
# 数据结构：
# mapping编号，排序一下
# 映射表
# 电极区域制作表

mapping_cards = organ_cards
mapping_cards = sorted(mapping_cards, key=lambda x: x[1])
maping_ID = [cards_number[1] for cards_number in mapping_cards]
maping_ID = tuple(maping_ID)
print(maping_ID)


print(code_mapping[maping_ID])
# 012->0->area0
# 013->1->area1
# 123->2->area2
if code_mapping[maping_ID]
stim_area =

# 刺激是相同的

#
# if card == 'red_1':
#     stim_region(ele_num[region], red, 1, 0.5, array)
# elif card == 'red_2':
#     stim_region(ele_num[region], red, 2, 0.5, array)
# elif card == 'black_1':
#     stim_region(ele_num[region], black, 1, 0.5, array)
# elif card == 'black_2':
#     stim_region(ele_num[region], black, 2, 0.5, array)
