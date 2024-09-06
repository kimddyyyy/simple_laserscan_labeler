#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PySide6 import QtCore, QtWidgets

os.environ['QT_QPA_PLATFORM'] = 'xcb'

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.max_range = 20
        self.current_index = -1
        self.data_dir = None
        self.label_dir = None
        self.data_list = []
        self.label_list = []

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        self.press = None 
        self.rect_patch = None
        self.data = []
        self.label = []

        # matplotlib figure event
        self.init_gui()
        self.canvas.mpl_connect("button_press_event", self.on_press)  # 마우스 버튼 클릭 이벤트
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)  # 마우스 이동 이벤트
        self.canvas.mpl_connect("button_release_event", self.on_release)  # 마우스 버튼 해제 이벤트
        self.canvas.mpl_connect("scroll_event", self.on_scroll)  # 마우스 휠 이벤트 연결

    def init_gui(self):
        self.setWindowTitle("LaserScan Labeler")
        
        self.grid_layout = QtWidgets.QGridLayout()

        self.data_dir_label = QtWidgets.QLabel("No data directory selected")
        self.data_dir_label.setAlignment(QtCore.Qt.AlignLeft)
        self.label_dir_label = QtWidgets.QLabel("No label directory selected")
        self.label_dir_label.setAlignment(QtCore.Qt.AlignLeft)
        self.select_data_dir_button = QtWidgets.QPushButton("Select Data Directory")
        self.select_data_dir_button.clicked.connect(self.select_data_directory)
        self.select_label_dir_button = QtWidgets.QPushButton("Select Label Directory")
        self.select_label_dir_button.clicked.connect(self.select_label_directory)

        self.data_list_widget = QtWidgets.QListWidget()
        self.data_list_widget.itemClicked.connect(self.read_data)
        self.label_list_widget = QtWidgets.QListWidget()
        self.label_list_widget.itemClicked.connect(self.read_label)

        self.canvas = FigureCanvas(self.fig)  # Matplotlib canvas

        self.grid_layout.addWidget(self.data_dir_label, 0, 1, 1, 1)  
        self.grid_layout.addWidget(self.label_dir_label, 0, 2, 1, 1) 
        self.grid_layout.addWidget(self.select_data_dir_button, 1, 1, 1, 1) 
        self.grid_layout.addWidget(self.select_label_dir_button, 1, 2, 1, 1)
        self.grid_layout.addWidget(self.data_list_widget, 2, 1, 10, 1)  
        self.grid_layout.addWidget(self.label_list_widget, 2, 2, 10, 1) 
        self.grid_layout.addWidget(self.canvas, 0, 0, 12, 1) 

        self.grid_layout.setColumnStretch(0, 3)
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setColumnStretch(2, 1)

        self.setLayout(self.grid_layout)

    def select_data_directory(self):
        self.data_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if self.data_dir:
            self.data_dir_label.setText(self.data_dir)
            self.update_data_list()

    def select_label_directory(self):
        self.label_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Label Directory")
        if self.label_dir:
            self.label_dir_label.setText(self.label_dir)
            self.update_label_list()

    def update_data_list(self):
        self.data_list = []
        self.data_list_widget.clear()

        for file_name in os.listdir(self.data_dir):
            if file_name.endswith('.txt'):
                self.data_list.append(file_name)

        self.data_list.sort()

        for data_file in self.data_list:
            self.data_list_widget.addItem(data_file)

        self.current_index = 0

    def update_label_list(self):
        self.label_list = []
        self.label_list_widget.clear()

        for file_name in os.listdir(self.label_dir):
            if file_name.endswith('.txt'):
                self.label_list.append(file_name)

        self.label_list.sort()

        for label_file in self.label_list:
            self.label_list_widget.addItem(label_file)


    def read_data(self, item):
        self.current_index = self.data_list_widget.row(item)
        file_name = item.text()
        file_path = os.path.join(self.data_dir, file_name)

        self.data = []
        with open(file_path, 'r') as f:
            for line in f:
                data = line.strip().split(",")
                i = int(data[0]) 
                r = float(data[1]) 
                t = float(data[2]) 
                x = float(data[3]) 
                y = float(data[4]) 
                l = int(data[5]) 
                self.data.append([i, r, t, x, y, l])

        self.data = np.array(self.data)
        self.plot_data(self.data)

    def read_label(self, item):
        file_name = item.text()
        file_path = os.path.join(self.label_dir, file_name)

        self.label = []
        with open(file_path, 'r') as f:
            for line in f:
                data = line.strip().split(",")
                i = int(data[0]) 
                r = float(data[1]) 
                t = float(data[2]) 
                x = float(data[3]) 
                y = float(data[4]) 
                l = int(data[5]) 
                self.label.append([i, r, t, x, y, l])

        self.label = np.array(self.label)
        self.plot_data(self.label)

    def plot_data(self, data):
        self.ax.clear()
        self.ax.set_xlim(-self.max_range, self.max_range)
        self.ax.set_ylim(-self.max_range, self.max_range)

        colors = ['green' if label == 0 else 'red' for label in data[:, 5]]
        self.ax.scatter(data[:, 3], data[:, 4], c=colors, s=5)
        self.canvas.draw()


    # pyside keyboard event handler
    def keyPressEvent(self, event):
        print("got key event")
        if event.key() == QtCore.Qt.Key_Right:
            self.move_to_next_data()
        elif event.key() == QtCore.Qt.Key_Left:
            self.move_to_prev_data()
        elif event.key() == QtCore.Qt.Key_Escape:  
            self.save_label()
            self.update_label_list()

    def move_to_next_data(self):
        if self.data_list:
            self.current_index = (self.current_index + 1) % len(self.data_list)
            self.data_list_widget.setCurrentRow(self.current_index)
            self.read_data(self.data_list_widget.currentItem())

    def move_to_prev_data(self):
        if self.data_list:
            self.current_index = (self.current_index - 1) % len(self.data_list)
            self.data_list_widget.setCurrentRow(self.current_index)
            self.read_data(self.data_list_widget.currentItem())

    def save_label(self):
        if self.label_dir is None:
            QtWidgets.QMessageBox.warning(self, "Warning", "No save directory selected.")
            return
        else:
            print("enter save label")

            file_name = f"label_{self.current_index:04d}.txt"
            save_path = os.path.join(self.label_dir, file_name)

            with open(save_path, 'w') as f:
                for data in self.data:
                    f.write(f"{int(data[0])},{float(data[1])},{float(data[2])},{float(data[3])},{float(data[4])},{int(data[5])}\n")
            
            print("save")

    # matplotlib canvas event handler
    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        self.press = (event.xdata, event.ydata)
        if self.rect_patch is not None:
            self.rect_patch.remove()
        self.rect_patch = None

    def on_motion(self, event):
        if self.press is None or event.inaxes != self.ax:
            return
        x0, y0 = self.press
        x1, y1 = event.xdata, event.ydata

        if None not in (x0, y0, x1, y1):
            if self.rect_patch is not None:
                self.rect_patch.remove()
            self.rect_patch = plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor='blue', linewidth=2)
            self.ax.add_patch(self.rect_patch)
            self.canvas.draw()

    def on_release(self, event):
        if self.press is None:
            return
        x0, y0 = self.press
        x1, y1 = event.xdata, event.ydata

        num_selected = 0
        if None not in (x0, y0, x1, y1):
            xmin, xmax = min(x0, x1), max(x0, x1)
            ymin, ymax = min(y0, y1), max(y0, y1)

            for data in self.data:
                x, y = data[3], data[4]
                if xmin <= x <= xmax and ymin <= y <= ymax:
                    data[5] = 1  # label 값을 1로 변경
                    num_selected += 1

        self.press = None
        self.plot_data(self.data)

        print(f"{num_selected} points selected.")

    def on_scroll(self, event):
        delta = event.step
        self.max_range += delta
        self.max_range = max(1, self.max_range) 
        self.ax.set_xlim(-self.max_range, self.max_range)
        self.ax.set_ylim(-self.max_range, self.max_range)
        self.canvas.draw()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.resize(1600, 1200)
    main_window.show()

    sys.exit(app.exec())
