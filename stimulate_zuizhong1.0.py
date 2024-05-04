#!/usr/bin/python
"""
STIMULATION EXAMPLES

This script can be used to run stimulation on a MaxTwo or

MaxOne system via the Python API. Several combinations of pulse
trains can be run and the script can be called from the command
line directly.

Warning: No recordings are made in this example, but you can find
an example about how to record in another script, called `recordings.py`.
"""
import random
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from agent import Agent
from elecsvread import get_ele, read_cfg
from read_cpp1 import suan_pai
from tqdm import tqdm
from game import Game
from mxfunction import *

debug = 0
event_counter = 1  # variable to keep track of the event_id

# 打印传递给脚本的所有参数（不包括模块名）
for i, arg in enumerate(sys.argv[1:], start=1):
    print(f"Argument {i}: {arg}")

random.seed(42)  # 设置种子值为42

chip_number = sys.argv[1]
seed = sys.argv[2]
game_type = sys.argv[3]
experiment_number = sys.argv[4]
epoch = sys.argv[5]


def rearrange_cards(cards, position):
    for i, card in enumerate(cards):
        # Check if the card is a list and contains the position
        if isinstance(card, list) and card[1] == position:
            # Move the matched card to the front
            cards.insert(0, cards.pop(i))
            return cards
    return cards


def rearrange_cards_second_position(cards, position):
    for i, card in enumerate(cards):
        # Check if the card is a list and contains the position
        if isinstance(card, list) and card[1] == position:
            # Move the matched card to the second position
            # Note: Inserting at index 1 to place it at the second position
            cards.insert(1, cards.pop(i))
            return cards
    return cards


def compare_rainforce(card_name, ren_pai):
    guize = {'red_1': 3, 'red_2': 4, 'black_1': 1, 'black_2': 2}
    if guize[ren_pai[0][0]] > guize[ren_pai[1][0]]:
        if guize[ren_pai[0][0]] > guize[ren_pai[2][0]]:
            big = ren_pai[0][0]
        else:
            big = ren_pai[2][0]
    else:
        if guize[ren_pai[1][0]] > guize[ren_pai[2][0]]:
            big = ren_pai[1][0]
        else:
            big = ren_pai[2][0]
    print("big牌为:", big)
    print("card牌为：", card_name)
    if big == card_name:
        return 1
    else:
        return 0


def fapai():
    cards = [['red_1', 0], ['red_1', 1], ['red_2', 2], ['red_2', 3], ['black_1', 4], ['black_1', 5], ['black_2', 6],
             ['black_2', 7]]

    selected_cards = random.sample(cards, 6)
    return selected_cards


def deal_cards(selected_cards, ele_num, array):
    # 将前三张牌发给类器官
    organ_cards = selected_cards[:3]
    # 将后三张牌发给NPC
    npc_cards = selected_cards[3:]

    # 根据类器官拿到的牌执行相应的刺激命令

    for card, region in zip(organ_cards, ele_num.keys()):
        if debug == 1:
            print("region:", region)
        if card == 'red_1':
            stim_region(ele_num[region], red, 1, 0.5, array)
        elif card == 'red_2':
            stim_region(ele_num[region], red, 2, 0.5, array)
        elif card == 'black_1':
            stim_region(ele_num[region], black, 1, 0.5, array)
        elif card == 'black_2':
            stim_region(ele_num[region], black, 2, 0.5, array)

    return organ_cards, npc_cards


def fen_pai(pai, agent):
    # 初始化数据
    nao_pai_ori = pai[:3]
    nao_pai = [nao_pai_ori[0][0], nao_pai_ori[1][0], nao_pai_ori[2][0]]
    nao_pai_index = [nao_pai_ori[0][1], nao_pai_ori[1][1], nao_pai_ori[2][1]]
    nao_pai_zong_wei_pai_xu.append(nao_pai_ori)
    print("脑排序前:", nao_pai_ori)

    ren_pai_ori = pai[3:]
    ren_pai = [ren_pai_ori[0][0], ren_pai_ori[1][0], ren_pai_ori[2][0]]
    ren_pai_index = [ren_pai_ori[0][1], ren_pai_ori[1][1], ren_pai_ori[2][1]]
    ren_pai_qian_all.append(ren_pai_ori)
    print("人排序前:", ren_pai_ori)
    # 初始化数据

    # 1.排序脑子牌过程，脑子打牌初始化,脑子的牌排一排
    nao_pai_shun_xu = suan_pai()
    nao_pai_ori = [nao_pai_ori[i] for i in nao_pai_shun_xu]
    nao_pai = [nao_pai_ori[0][0], nao_pai_ori[1][0], nao_pai_ori[2][0]]
    print("脑排序后:", nao_pai)
    nao_pai_zong_pai_xu.append(nao_pai)

    # 2.排序人的牌过程，得到强化学习的牌
    # 强化学习初始化
    if agent:
        agent.getinfo([[], ren_pai_index])
        ren_card_index = agent.chupai()
        percentages_rainforce_win.append(compare_rainforce(cards[ren_card_index][0], ren_pai_ori))
        print("索引号", ren_card_index)
        agent_index.append(cards[ren_card_index])
        # 插牌进第一张，目前只能出第一张
        ren_pai_ori = rearrange_cards(ren_pai_ori.copy(), ren_card_index)

        if game_type == "5.2" or "6.4" or "6.5" or "6.6":
            agent.play(ren_pai_ori[0][1], nao_pai_ori[0][1])
            ren_card_index = agent.chupai()
            ren_pai_ori = rearrange_cards_second_position(ren_pai_ori.copy(), ren_card_index)
        ren_pai = [ren_pai_ori[0][0], ren_pai_ori[1][0], ren_pai_ori[2][0]]
        print("人排序后:", ren_pai_ori)
    ren_pai_zong.append(ren_pai)

    return nao_pai, ren_pai, nao_pai_ori, ren_pai_ori


def draw_picutre(filename, win_plt, lose_plt, draw_plt):
    # 绘制折线图
    plt.figure(figsize=(10, 6))
    plt.plot(win_plt, label='1', marker='o', linestyle='-')
    plt.plot(draw_plt, label='0', marker='o', linestyle='-')
    plt.plot(lose_plt, label='-1', marker='o', linestyle='-')

    plt.title('Percentage of 1, 0, -1 Over Iterations')
    plt.xlabel('Iteration')
    plt.ylabel('Percentage (%)')
    plt.legend()
    plt.grid(True)
    # 芯片号，种子，实验时间，游戏种类，实验绝对序号
    plt.savefig('图片/' + filename, format='png')
    # 显示图形
    # plt.show()


def get_agent(game_type):
    # 定义一个映射字典，只包括你想要处理的game_type值
    model_mapping = {
        "5.1": "model/first200000.p",
        "5.2": "model/first200000.p",
        "6.1": "model/first1000000_minIndex.p",
        "6.2": "model/first1000000_middleIndex.p",
        "6.3": "model/first2000000_maxIndex.p",
        "6.4": "model/two1000000min.p",
        "6.5": "model/two1000000middle.p",
        "6.6": "model/two2000000max.p",
    }

    if game_type not in model_mapping:
        print("当前实验为：", game_type)
        # 如果game_type不在字典中，直接返回None
        return None

    # 从映射字典中获取模型路径
    model_path = model_mapping[game_type]
    print("当前实验为（已开启强化学习）：", game_type)
    # 假设Agent是构造函数或者创建实例的函数
    return Agent(model_path)


def give_reward(jiangli, stim_electrodes, array):
    if jiangli == 0:
        if result == 1:
            print("win")
            stim_region(stim_electrodes, win, 20, 0.005, array)
        elif result == -1:
            print("lose")
            stim_region(stim_electrodes, lose, 20, 0.2, array)
        else:
            print("draw")
            time.sleep(5)
    elif jiangli == 1:  # 4.1 only give win
        if result == 1:
            print("win")
            stim_region(stim_electrodes, win, 20, 0.005, array)
    elif jiangli == 2:  # 4.2 only give lose
        if result == -1:
            print("lose")
            stim_region(stim_electrodes, lose, 20, 0.2, array)
    elif jiangli == 3:  # 4.3 fan
        if result == 1:
            print("win")
            stim_region(stim_electrodes, lose, 20, 0.2, array)
        elif result == -1:
            print("lose")
            stim_region(stim_electrodes, win, 20, 0.005, array)
        else:
            print("draw")
            time.sleep(5)
    elif jiangli == 4:
        time.sleep(5)
    elif jiangli == 5:
        time.sleep(0)


if __name__ == "__main__":
    cfg_name = read_cfg()
    agent = get_agent(game_type)
    now = datetime.now()
    # 格式化为年月日时分秒
    formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
    # 新方法
    ele_num = get_ele(cfg_name)
    # # 老方法
    # ele_num = get_ele("ele_number3.csv")
    initialize_system()
    filename = 'A:{}实验时间{}种子编号{}芯片号{}游戏种类{}绝对实验编号{}轮次'.format(formatted_time, seed, chip_number,
                                                              game_type, experiment_number,
                                                              epoch)
    print(filename)
    game = Game()

    array = mx.Array("stimulation")
    array.reset()
    array.clear_selected_electrodes()
    data = pd.read_csv(cfg_name)
    # 老方法
    # data = pd.read_csv("ele_number3.csv")
    data = data.iloc[:, 2]
    data = data.values.tolist()
    if debug == 1:
        print(len(data))

    for key in ['D', 'E', 'F']:
        ele_num[key] = ele_num[key][:1]
    excluded_items = set(ele_num['D'] + ele_num['E'] + ele_num['F'])
    data = [item for item in data if item not in excluded_items]

    stim_electrodes = ele_num['D'] + ele_num['E'] + ele_num['F']
    print(stim_electrodes)
    array.select_stimulation_electrodes(stim_electrodes)
    array.select_electrodes(data)
    array.route()

    # Select the subset of wells we want to stimulate.
    wells = list(range(1))
    mx.activate(wells)
    array.download(wells)
    mx.offset()

    mx.clear_events()  # Empty event-buffer before adding anything to it
    red = prepare_stim_sequence(10, 2000, 200, amplitude=500)  # 刺激1  对应红色纸牌
    black = prepare_stim_sequence(1, 2000, 200, amplitude=1000)  # 刺激2  对应黑色纸牌
    win = prepare_stim_sequence(1, 2000, 200, amplitude=1000)  # 刺激
    lose = prepare_stim_sequence(1, 2000, 200, amplitude=1000)  # 刺激
    epoch = int(epoch)
    cards = [['red_1', 0], ['red_1', 1], ['red_2', 2], ['red_2', 3], ['black_1', 4], ['black_1', 5], ['black_2', 6],
             ['black_2', 7]]
    jieguo = []
    draw_plot = []
    nao_pai_zong_wei_pai_xu = []
    nao_pai_zong_pai_xu = []
    ren_pai_zong = []
    ren_pai_qian_all = []
    percentages_win = []
    percentages_lose = []
    percentages_draw = []
    percentages_rainforce_win = []
    agent_index = []
    # 刺激过程
    for t in tqdm(range(epoch)):
        pai = fapai()
        deal_cards(pai, ele_num, array)
        time.sleep(0.1)
        nao_pai, ren_pai, nao_pai_ori, ren_pai_ori = fen_pai(pai, agent)
        # 开始游戏
        result, wenzi = game.start_game(game_type, nao_pai, ren_pai)

        # 选择奖励类型
        jiangli = game.get_jiangli()
        print("当前给的奖励类型为：", jiangli)
        jieguo.append(wenzi)
        draw_plot.append(result)

        if agent:
            # 更新强化学习参数
            if game_type == "5.2" or "6.4" or "6.5" or "6.6":
                print(ren_pai_ori[1][1], nao_pai_ori[1][1], result)
                agent.play(ren_pai_ori[1][1], nao_pai_ori[1][1], result)
            else:
                print(ren_pai_ori[0][1], nao_pai_ori[0][1], result)
                agent.play(ren_pai_ori[0][1], nao_pai_ori[0][1], result)

        start_time = time.time()
        give_reward(jiangli, stim_electrodes, array)
        print("给奖励的时间：", time.time() - start_time)
        length = len(draw_plot)
        percentages_win.append(draw_plot.count(1) / length * 100)
        percentages_lose.append(draw_plot.count(-1) / length * 100)
        percentages_draw.append(draw_plot.count(0) / length * 100)
        draw_picutre(filename, percentages_win, percentages_lose, percentages_draw)
        time.sleep(1)
        if agent:
            agent.save_model("./", "name")

    print("脑子未排序结果:", nao_pai_zong_wei_pai_xu)
    print("脑子排序结果:", nao_pai_zong_pai_xu)
    print("输赢结果:", jieguo)
    if agent:
        print("强化学习策略正确率", f"{sum(percentages_rainforce_win) / len(percentages_rainforce_win) * 100}%")
    # 将结果写入文本文件
    with open('图片/' + filename + '.txt', 'w') as file:

        def write_data(file, label, data_list):
            file.write(f"{label}:\n")
            for item in data_list:
                file.write(f"{item}\n")


        write_data(file, "人未排序结果", ren_pai_qian_all)
        write_data(file, "人排序结果:", ren_pai_zong)
        write_data(file, "脑子未排序结果", nao_pai_zong_wei_pai_xu)
        write_data(file, "脑子排序结果", nao_pai_zong_pai_xu)
        write_data(file, "输赢结果", jieguo)
        write_data(file, "强化学习牌索引", agent_index)

        # 如果需要，也可以写入其他统计信息
        file.write("胜率:\n")
        if percentages_win:
            file.write(f"{percentages_win[-1]}%\n")
        file.write("败率:\n")
        if percentages_lose:
            file.write(f"{percentages_lose[-1]}%\n")
        file.write("平局率:\n")
        if percentages_draw:
            file.write(f"{percentages_draw[-1]}%\n")
        if agent:
            file.write("强化学习最大排概率:\n")
            file.write(f"{sum(percentages_rainforce_win) / len(percentages_rainforce_win) * 100}%")
