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
debug = 0
import time
import pandas as pd
import maxlab as mx
import random
from typing import List, Optional
from pathlib import Path
from elecsvread import get_ele, get_ele2, read_cfg
from read_cpp1 import suan_pai
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import os
import csv
import re
from stimulate_zuizhong46 import send_stim_pulses_all_units
from tqdm import tqdm


def powerup_stim_unit(stim_unit: int) -> mx.StimulationUnit:
    """Power up and connect a stimulation unit

    This function powers up and connect a specific stimulation
    unit in the MaxOne/Two. Without it, we would not be able to
    send the prepared sequence to the device and it thus needs
    to be run before running `mx.send(stim)` (as shown in the
    function `configure_and_powerup_stim_units).

    Parameters
    ----------
    stim_unit : str
        The index of the stimulation unit to power up

    Returns
    -------
    mx.StimulationUnit
        The powered up stimulation unit

    """
    return (
        mx.StimulationUnit(stim_unit)
        .power_up(True)
        .connect(True)
        .set_voltage_mode()
        .dac_source(0)
    )


def configure_and_powerup_stim_units(stim_units: List[int]) -> List[mx.StimulationUnit]:
    """Configure and powerup the stimulation units

    Once the electrodes are connected to the stimulation units,
    the stimulation units need to be configured and powererd up.

    Parameters
    ----------
    stim_units : List[str]
        List of stimulation units indices corresponding to the connected
        stimulation electrodes

    Returns
    -------
    List[mx.StimulationUnit]
        List of stimulation unit objects corresponding to the connected
        stimulation electrodes.

    """
    stim_unit_commands: List[mx.StimulationUnit] = []
    for stim_unit in stim_units:
        stim = powerup_stim_unit(stim_unit)
        stim_unit_commands.append(stim)
        mx.send(stim)
    return stim_unit_commands


def poweroff_all_stim_units() -> None:
    """Poweroff all stimulation units

    This function is used to make sure that every stimulation units is
    powered-off before starting sequentially to send the sequences to the
    different stimulation units individually.

    Returns
    -------
    None

    """
    for stimulation_unit in range(0, 32):
        stim = mx.StimulationUnit(stimulation_unit)
        stim.power_up(False)
        stim.connect(False)
        mx.send(stim)


def configure_and_powerup_stim_units(stim_units: List[int]) -> List[mx.StimulationUnit]:
    """Configure and powerup the stimulation units

    Once the electrodes are connected to the stimulation units,
    the stimulation units need to be configured and powererd up.

    Parameters
    ----------
    stim_units : List[str]
        List of stimulation units indices corresponding to the connected
        stimulation electrodes

    Returns
    -------
    List[mx.StimulationUnit]
        List of stimulation unit objects corresponding to the connected
        stimulation electrodes.

    """
    stim_unit_commands: List[mx.StimulationUnit] = []
    for stim_unit in stim_units:
        stim = powerup_stim_unit(stim_unit)
        stim_unit_commands.append(stim)
        mx.send(stim)
    return stim_unit_commands


def prepare_stim_sequence(
        number_pulses_per_train: int,
        inter_pulse_interval: int,
        phase: int,
        amplitude: int,
        changing_amplitude: Optional[bool] = False,
        max_amplitude: Optional[int] = None,
        amplitude_interval: Optional[int] = None,
) -> mx.Sequence:
    """Prepare a stimulation sequence.

    This is just and example and it only illustrates how sequences
    can be constructed.

    Parameters
    ----------
    number_pulses_per_train : int
        Number of repetitions of one pulse.
    inter_pulse_interval : int
        Number of samples to delay between two consecutive pulses.
    phase : int
        Number of samples before the switch from high-low (and vice versa)
        voltage when creating stimulation pulse.
    amplitude : int
        Amplitude of the pulse (minimal if changing_amplitude is True).
        Unit is millivolt.
    changing_amplitude : Optional[bool]
        Whether the pulse amplitude changes, by default False.
    max_amplitude : Optional[int]
        Maximal amplitude of the pulse if changing_amplitude is True.
        Unit is millivolt.
    amplitude_interval : Optional[int]
        Increment amplitude interval if changing_amplitude is True.
        Unit is millivolt.

    Returns
    -------
    mx.Sequence
        Sequence object filled with the stimulation sequence.

    """
    seq = mx.Sequence()
    dac_lsb_mV = float(mx.query_DAC_lsb_mV())
    if changing_amplitude:
        if max_amplitude is None or amplitude_interval is None:
            raise ValueError(
                "Both max_amplitude and amplitude_interval are required for changing_amplitude."
            )
        for cur_amplitude in range(amplitude, max_amplitude, amplitude_interval):
            for _ in range(number_pulses_per_train):
                seq = create_stim_pulse(seq, int(cur_amplitude / dac_lsb_mV), phase)
                seq.append(mx.DelaySamples(inter_pulse_interval))
            seq.append(mx.DelaySamples(inter_pulse_interval))
    else:
        for _ in range(number_pulses_per_train):
            seq = create_stim_pulse(seq, int(amplitude / dac_lsb_mV), phase)
            seq.append(mx.DelaySamples(inter_pulse_interval))
    return seq


random.seed(42)  # 设置种子值为42
event_counter = 1  # variable to keep track of the event_id


def fapai():
    cards = ['red_1', 'red_1', 'red_2', 'red_2', 'black_1', 'black_1', 'black_2', 'black_2']
    selected_cards = random.sample(cards, 6)
    return selected_cards


def initialize_system() -> None:
    """Initialize system into a defined state

    The function initializes the system into a defined state before
    starting any script. This way, one can be sure that the system
    is always in the same state while running the script, regardless
    of what has been done before with it. The function also powers on
    the stimulation units, which are turned off by default.

    Raises
    ------
    RuntimeError
        If system does not initialize correctly.

    """
    mx.initialize()
    if mx.send(mx.Core().enable_stimulation_power(True)) != "Ok":
        raise RuntimeError("The system didn't initialize correctly.")


def deal_cards(selected_cards):
    # 将前三张牌发给类器官
    organ_cards = selected_cards[:3]
    # 将后三张牌发给NPC
    npc_cards = selected_cards[3:]

    # 根据类器官拿到的牌执行相应的刺激命令

    for card, region in zip(organ_cards, ele_num.keys()):
        if debug == 1:
            print("region:", region)
        if card == 'red_1':
            stim_region(ele_num[region], red, 2, 0.5)
        elif card == 'red_2':
            stim_region(ele_num[region], red, 4, 0.5)
        elif card == 'black_1':
            stim_region(ele_num[region], black, 2, 0.5)
        elif card == 'black_2':
            stim_region(ele_num[region], black, 4, 0.5)

    return organ_cards, npc_cards


def extract_txt():
    file_path = 'celebration.txt'

    # 使用正则表达式提取数值
    pattern = r'([ABC]):(\d+) ([\d.]+)%'

    # 初始化列表用于存储提取的百分比信息
    percentages = []

    with open(file_path, 'r') as file:
        content = file.read()
        matches = re.findall(pattern, content)
        percentages = [float(match[2]) for match in matches]

    return percentages


def create_stim_pulse(
        seq: mx.Sequence, amplitude: int, delay_samples: int
) -> mx.Sequence:
    """Create stimulation pulse

    The stimulation units can be controlled through three independent
    sources, what we call DAC channels (for digital analog converter).
    By programming a DAC channel with digital values, we can control
    the output the stimulation units. DAC inputs are in the range between
    0 to 1023 bits, whereas 512 corresponds to zero volt and one bit
    corresponds to 2.9 mV. Thus, to give a pulse of 100mV, the DAC
    channel temporarily would need to be set to 512 + 34 (100mV/2.9)
    and back again to 512.

    Notes
    -----
    In this example, all 32 units are controlled through the same DAC
    channel ( dac_source(0) ),  thus by programming a biphasic pulse
    on DAC channel 0, all the stimulation units exhibit the biphasic
    pulse.
    When the stimulation buffers are set to voltage mode, they act like
    an inverting amplifier. Thus here we need to program a negative first
    biphasic pulse, to get a positive first pulse on the chip.

    Parameters
    ----------
    seq : mx.Sequence
        Sequence object holding a sequence of commands, as generated
        by `mx.Sequence()`.
    amplitude : int
        Amplitude of the pulse, with units [100mV/2.9], as explained above.
    delay_samples : int
        How many samples should sand between different sequence amplitude.

    Returns
    -------
    mx.Sequence
        Sequence object filled by the pulse.

    """
    global event_counter
    event_counter += 1
    seq.append(mx.Event(0, 1, event_counter, f"amplitude {amplitude} event_id {event_counter}"))
    seq.append(mx.DAC(0, 512 - amplitude))
    seq.append(mx.DelaySamples(delay_samples))
    seq.append(mx.DAC(0, 512 + amplitude))
    seq.append(mx.DelaySamples(delay_samples))
    seq.append(mx.DAC(0, 512))
    return seq


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


def connect_stim_units_to_stim_electrodes(
        stim_electrodes: List[int], array: mx.Array
) -> List[int]:
    """Connect the stimulation units to the stimulation electrodes

    Once an array configuration has been obtained, either through routing
    or through loading a previous configuration, the stimulation units
    can be connected to the desired electrodes.

    Notes
    -----
    With this step, one needs to be careful, in rare cases it can happen
    that an electrode cannot be stimulated. For example, the electrode
    could not be routed (due to routing constraints), and the error message
    "No stimulation channel can connect to electrode: ..." will be printed.
    If this situation occurs, it is recommended to then select the electrode
    next to it.

    Parameters
    ----------
    stim_electrodes : List[int]
        List of the index of the stimulation electrodes
    array : mx.Array
        The configured array

    Returns
    -------
    List[str]
        List of stimulation units indices corresponding to the connected
        stimulation electrodes

    Raises
    ------
    RuntimeError
        If an electrode cannot be connected to a stimulation unit.
        If two electrodes are connected to the same stimulation unit.
    """
    stim_units: List[int] = []
    for stim_el in stim_electrodes:
        array.connect_electrode_to_stimulation(stim_el)
        stim = array.query_stimulation_at_electrode(stim_el)
        if len(stim) == 0:
            raise RuntimeError(
                f"No stimulation channel can connect to electrode: {str(stim_el)}"
            )
        stim_unit_int = int(stim)
        if stim_unit_int in stim_units:
            raise RuntimeError(
                f"Two electrodes connected to the same stim unit.\
                               This is not allowed. Please Select a neighboring electrode of {stim_el}!"
            )
        else:
            stim_units.append(stim_unit_int)

    return stim_units


def stim_region(stim_electrodes, card_mode, time, step):
    # print("cunrrent:", stim_electrodes, '\nlen:', len(stim_electrodes))
    stim_units = connect_stim_units_to_stim_electrodes(stim_electrodes, array)  # stim_electrodes number
    configure_and_powerup_stim_units(stim_units)
    send_stim_pulses_all_units(card_mode, time, step)
    poweroff_all_stim_units()  # close



def suan_pai():
    result = []
    # 新方法
    filename = read_cfg()
    data = get_ele2(filename)

    # # 老方法
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

    Q_base = dict()
    Q_base['A'] = 0
    Q_base['B'] = 0
    Q_base['C'] = 0
    # 外部大循环，执行40次
    # 在两次大循环之间等待5秒

    # for n in range(0, 1):
    #     for i in list:
    #         sim(i[0], i[1], i[2], i[3])
    #     # time.sleep(0.09)

    # 获取当前路径下的所有 CSV 文件
    #       current_files = set(file for file in os.listdir(monitor_path) if file.endswith(file_extension))

    count = 0
    epoch = int(100)
    while True:
        current_files = set(
            os.path.join(monitor_path, file) for file in os.listdir(monitor_path) if file.endswith(file_extension))
        if count == 0:
            pre = len(current_files)
            count += 1
        next = len(current_files)
        # print(current_files)
        if pre != next:
            print(next / float(epoch) * 100, "%", sep="")

        if len(current_files) >= epoch:
            # 只考虑最新的50个CSV文件
            latest_files = sorted(current_files, key=os.path.getmtime, reverse=True)[:epoch]

            # 检查是否有新文件出现
            new_files = set(latest_files) - last_checked_files

            if new_files:
                if debug == 1:
                    print("New CSV file(s) detected:", new_files)
                # 对每个新文件执行代码
                for new_file in new_files:
                    csv_file_path = os.path.join(monitor_path, new_file)
                    numeric_line_count, runtime = count_numeric_lines(csv_file_path, data)
                    result.append(numeric_line_count)
                    Q_base['A'] += numeric_line_count['A']
                    Q_base['B'] += numeric_line_count['B']
                    Q_base['C'] += numeric_line_count['C']

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

            # 更新上次检测到的文件列表
            last_checked_files = current_files
            break
        pre = next
    sum = 0
    for num in Q_base.values():
        sum += num
    for i, j in Q_base.items():
        print(i, ":", j, " ", j / sum * 100, '%', sep="")

    def dapaishunxu(data):

        # 假设我们只处理列表中的第一个字典
        dic = data[0]

        # 获取字典的值，并倒序排序
        sorted_values_desc = sorted(dic.values(), reverse=True)

        # 创建一个排名字典，其中值按照大小倒序排列
        rank_dict_desc = {value: rank for rank, value in enumerate(sorted_values_desc)}

        # 使用原字典的键和倒序排名字典的值创建一个新的排名字典
        ranked_dic_desc = {key: rank_dict_desc[value] for key, value in dic.items()}

        # 按照原列表中键的顺序输出排名
        output_list = [ranked_dic_desc[key] for key in dic.keys()]
        print(output_list)

        return output_list

    return Q_base


if __name__ == "__main__":

    # 新方法
    filename = read_cfg()
    ele_num = get_ele(filename)

    # # 老方法
    # ele_num = get_ele("ele_number5.csv")
    mx.initialize()
    mx.send(mx.Core().enable_stimulation_power(True))
    array = mx.Array("stimulation")
    array.reset()
    array.clear_selected_electrodes()
    data = pd.read_csv(filename)
    data = data.iloc[:, 2]
    data = data.values.tolist()
    if debug == 1:
        print(len(data))

    ele_num['D'] = ele_num['D']
    ele_num['E'] = ele_num['E']
    ele_num['F'] = ele_num['F']  #[:1]
    # # filter
    data = [item for item in data if item not in ele_num['D']]
    data = [item for item in data if item not in ele_num['E']]
    data = [item for item in data if item not in ele_num['F']]

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

    red = prepare_stim_sequence(0, 0, 0, amplitude=0)  # 刺激1  对应红色纸牌
    black = prepare_stim_sequence(0, 0, 0, amplitude=0)  # 刺激2  对应黑色纸牌
    win = prepare_stim_sequence(0, 0, 0, amplitude=0)  # 刺激
    lose = prepare_stim_sequence(0, 0, 0, amplitude=0)  # 刺激

    # stim_unit_commands = configure_and_powerup_stim_units(stim_units)
    # seq_1 = prepare_stim_sequence(1, 2000, 200, amplitude=500)
    # seq_2 = prepare_stim_sequence(1, 2000, 200, amplitude=100)
    #
    # # The pulse trains can be delivered whenever seems reasonable, or following
    # # a specific stimulation schedudle, such as:
    #
    # # times is interval,number_pulse_trains chong fu ci shu
    # for i in range(5):
    #     start = time.time()
    #     send_stim_pulses_all_units(seq_1, 1,0.8)
    #     end = time.time()
    #     print(end-start)
    #     send_stim_pulses_all_units(seq_2, 2,0.4)

    jieguo = []
    draw_plot = []
    nao_pai_zong_wei_pai_xu = []
    nao_pai_zong_pai_xu = []
    ren_pai_zong = []

    percentages_win = []
    percentages_lose = []
    percentages_draw = []

    total_result = []  # 用于记录每次suanpai()的结果
    for t in tqdm(range(100)):  # 重复100次
        pai = fapai()
        deal_cards(pai)
        time.sleep(0.1)
        A = suan_pai()
        total_result.append(A)  # 将结果添加到total_result中

    # 计算平均结果
    all_result = [0, 0, 0]
    for one in total_result:
        all_result[0] += one['A']
        all_result[1] += one['B']
        all_result[2] += one['C']

    avg_list = []
    for i in all_result:
        print("平均结果：", i / len(total_result))
        avg_list.append(i / len(total_result))
    # average_result = sum(total_result) / len(total_result)
    # print("平均结果：", average_result)

    avg_dict = {'A': avg_list[0], 'B': avg_list[1], 'C': avg_list[2]}
    sum_all = avg_list[0] + avg_list[1] + avg_list[2]
    with open('celebration.txt', 'w') as file:  # 打开文件用于写入
        for i, j in avg_dict.items():
            print(i, ":", j, " ", j / sum_all * 100, '%', sep="", file=file)  # 将输出写入文件
