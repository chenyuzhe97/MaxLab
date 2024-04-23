import tkinter as tk
from tkinter import filedialog
import csv
from itertools import zip_longest
import re


def read_cfg_and_calculate_coordinates(cfg_path):
    coordinates = []
    with open(cfg_path, 'r') as file:
        content = file.read()
        numbers = re.findall(r'\((\d+)\)', content)
        for number in numbers:
            coord = cal(int(number))
            coordinates.append(coord)
    return coordinates


def cal(n):
    y = int(n / 220)
    x = n % 220
    return x, y


class GridSelector:
    def __init__(self, master, rows=120, cols=220, cell_size=8):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.selections = {}  # Start with an empty dictionary
        self.current_selection = []

        # Canvas for drawing the grid
        self.canvas = tk.Canvas(master, width=self.cols * self.cell_size, height=self.rows * self.cell_size)
        self.canvas.grid(row=0, column=0, rowspan=8)

        # Draw the grid
        self.draw_grid()

        # UI Elements for region label and creating regions
        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.grid(row=0, column=1, sticky='n')

        self.region_label = tk.Label(self.buttons_frame, text="目标区域标签:")
        self.region_label.pack()
        self.region_entry = tk.Entry(self.buttons_frame)
        self.region_entry.pack()

        self.create_region_button = tk.Button(self.buttons_frame, text="创建目标区域", command=self.save_selection_from_entry)
        self.create_region_button.pack(fill=tk.X)

        self.filename_label = tk.Label(self.buttons_frame, text="输出文件名:")
        self.filename_label.pack()
        self.filename_entry = tk.Entry(self.buttons_frame)
        self.filename_entry.pack()

        self.generate_button = tk.Button(self.buttons_frame, text="生成", command=self.generate_csv)
        self.generate_button.pack(fill=tk.X)

        self.preview_button = tk.Button(self.buttons_frame, text="预览", command=self.preview_selections)
        self.preview_button.pack(fill=tk.X)

        # Mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.load_cfg_button = tk.Button(self.buttons_frame, text="读取cfg区域", command=self.load_cfg_area)
        self.load_cfg_button.pack(fill=tk.X)

        self.load_config_button = tk.Button(self.buttons_frame, text="载入配置", command=self.load_config)
        self.load_config_button.pack(fill=tk.X)

    # 载入配置
    def load_config(self):
        config_path = filedialog.askopenfilename(title="选择配置文件", filetypes=(("CSV文件", "*.csv"), ("所有文件", "*.*")))
        if config_path:
            with open(config_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row if there is one
                for row in reader:
                    region = row[0]
                    x = float(row[-2]) / 17.5
                    y = float(row[-1]) / 17.5
                    if region not in self.selections:
                        self.selections[region] = []
                    self.selections[region].append((int(x), int(y)))

    # 添加用于读取CFG文件和更新画布的方法
    # 修改load_cfg_area方法，以使用filedialog选择文件
    def load_cfg_area(self):
        cfg_path = filedialog.askopenfilename(title="选择cfg文件", filetypes=(("cfg文件", "*.cfg"), ("所有文件", "*.*")))
        if cfg_path:  # 确保用户选择了文件
            coordinates = read_cfg_and_calculate_coordinates(cfg_path)
            for x, y in coordinates:
                self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size,
                                             (y + 1) * self.cell_size, fill="black", outline="gray")

    def save_selection_from_entry(self):
        region_name = self.region_entry.get().strip()
        if region_name:  # Only proceed if there is some input
            if region_name not in self.selections:
                self.selections[region_name] = []  # Create new entry in the dictionary if it doesn't exist
            self.save_selection(region_name)

    def save_selection(self, name):
        if self.current_selection:  # Ensure there is something to save
            self.selections[name] = self.current_selection.copy()
            self.current_selection = []
            print(f"Saved to {name}: {self.selections[name]}")

    def preview_selections(self):
        self.canvas.delete("preview")
        colors = ['red', 'green', 'yellow', 'cyan', 'magenta', 'orange']
        for i, key in enumerate(self.selections):
            for x, y in self.selections[key]:
                self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size,
                                             (y + 1) * self.cell_size, fill=colors[i % len(colors)], outline="gray", tags="preview")

    def generate_csv(self):
        with open('selections.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.selections.keys())
            writer.writerows(zip_longest(*self.selections.values(), fillvalue=''))

        filename = self.filename_entry.get().strip()
        if not filename:  # Default filename if not specified
            filename = 'ele_number.csv'
        convert_selections_to_ele_format('selections.csv', filename)

    def on_mouse_down(self, event):
        self.start_cell = (event.x // self.cell_size, event.y // self.cell_size)

    def on_mouse_drag(self, event):
        self.end_cell = (event.x // self.cell_size, event.y // self.cell_size)
        self.redraw_selected_area()

    def on_mouse_up(self, event):
        self.end_cell = (event.x // self.cell_size, event.y // self.cell_size)
        self.redraw_selected_area()
        self.current_selection = self.selected_cells.copy()

    def redraw_selected_area(self):
        self.canvas.delete("selected")
        if not self.start_cell or not self.end_cell:
            return

        self.selected_cells = self.calculate_selection(self.start_cell, self.end_cell)
        for x, y in self.selected_cells:
            self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size,
                                         (y + 1) * self.cell_size, fill="blue", outline="gray", tags="selected")

    def draw_grid(self):
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray")

    def calculate_selection(self, start, end):
        start_x, start_y = min(start[0], end[0]), min(start[1], end[1])
        end_x, end_y = max(start[0], end[0]), max(start[1], end[1])
        return [(j, i) for i in range(start_y, end_y + 1) for j in range(start_x, end_x + 1)]


def convert_selections_to_ele_format(input_path, output_path):
    selections = {}
    with open(input_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for column, value in row.items():
                if column not in selections:
                    selections[column] = []
                if value:  # 忽略空值
                    selections[column].append(eval(value))

    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['Region', 'Electrode', 'Elec_Number', 'X', 'Y']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        electrode_counter = 0
        for region, coords in selections.items():
            for coord in coords:
                elec_number = coord[0] + coord[1] * 220
                x = coord[0] * 17.5
                y = coord[1] * 17.5
                writer.writerow(
                    {'Region': region, 'Electrode': electrode_counter, 'Elec_Number': elec_number, 'X': x, 'Y': y})
                electrode_counter += 1


def main():
    root = tk.Tk()
    root.title("Grid Selector with Input Label")
    app = GridSelector(root)
    root.mainloop()


if __name__ == "__main__":
    main()
