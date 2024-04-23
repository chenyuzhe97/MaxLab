import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import time

# 配置文件表
config_table = {}
count = 0


# 添加配置
def add_config():
    global count
    count += 1
    repeat_count = repeat_count_entry.get()
    chip_number = chip_number_entry.get()
    seed = seed_entry.get()
    game_type = game_type_entry.get()
    experiment_number = experiment_number_entry.get()
    epoch = epoch_entry.get()

    # 构建大参数字典
    big_params = {
        "芯片号": chip_number,
        "种子": seed,
        "游戏种类": game_type,
        "实验绝对序号": experiment_number,
        "单次实验轮次": epoch,
        "重复次数": repeat_count
    }

    # 添加到配置文件表
    config_table[count] = big_params
    print("配置已添加。当前配置文件表:", config_table)


# 确定配置并关闭窗口
def confirm_and_close():
    print("最终配置文件表:", config_table)
    root.destroy()


# 创建窗口
root = tk.Tk()
root.title("配置文件生成器")

# 创建输入框和标签
tk.Label(root, text="重复次数:").grid(row=0, column=0)
repeat_count_entry = tk.Entry(root)
repeat_count_entry.grid(row=0, column=1, columnspan=2)

tk.Label(root, text="芯片号:").grid(row=1, column=0)
chip_number_entry = tk.Entry(root)
chip_number_entry.grid(row=1, column=1, columnspan=2)

tk.Label(root, text="种子:").grid(row=2, column=0)
seed_entry = tk.Entry(root)
seed_entry.grid(row=2, column=1, columnspan=2)

tk.Label(root, text="游戏种类:").grid(row=3, column=0)
game_type_entry = tk.Entry(root)
game_type_entry.grid(row=3, column=1, columnspan=2)

tk.Label(root, text="实验绝对序号:").grid(row=4, column=0)
experiment_number_entry = tk.Entry(root)
experiment_number_entry.grid(row=4, column=1, columnspan=2)

tk.Label(root, text="每次实验轮次:").grid(row=5, column=0)
epoch_entry = tk.Entry(root)
epoch_entry.grid(row=5, column=1, columnspan=2)

# 创建按钮
add_button = ttk.Button(root, text="添加", command=add_config)
add_button.grid(row=6, column=0)

confirm_button = ttk.Button(root, text="确定", command=confirm_and_close)
confirm_button.grid(row=6, column=2)

# 运行窗口
root.mainloop()

print(config_table)

for cfg_file in config_table.values():
    for _ in range(int(cfg_file['重复次数'])):
        # 首先运行 del_csv.sh 脚本
        try:
            subprocess.run(['/home/admin1/Desktop/env/maxlab_lib/del_csv.sh'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute del_csv.sh: {e}")
            sys.exit(1)  # 如果脚本运行失败，则退出程序

        # 启动 3.exe，并传递参数 1
        proc_exe = subprocess.Popen(['/home/admin1/Desktop/env/maxlab_lib/build/example_filtered', '1'])

        try:
            # 执行 1.py 并等待其完成

            subprocess.run(['python', 'stimulate_zuizhong1.0.py'
                               , cfg_file['芯片号'], cfg_file['种子'], cfg_file['游戏种类'], cfg_file['实验绝对序号'],
                            cfg_file['单次实验轮次']])

            # 1.py 执行完毕后，尝试优雅地终止 3.exe
            proc_exe.terminate()  # 或者使用 proc_exe.kill() 如果 terminate() 无效

            # 确保 3.exe 已经终止
            proc_exe.wait()

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # 确保即使发生错误，3.exe 也能被终止
            proc_exe.terminate()
            proc_exe.wait()

        try:
            subprocess.run(['/home/admin1/Desktop/env/maxlab_lib/move_csv.sh'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute del_csv.sh: {e}")
            sys.exit(1)  # 如果脚本运行失败，则退出程序
        time.sleep(15)
