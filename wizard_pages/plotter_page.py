from PyQt5.QtWidgets import (QWizardPage,
                             QVBoxLayout,
                             QHBoxLayout,
                             QPushButton,
                             QScrollArea,
                             QWidget)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

import re

class PlotterPage(QWizardPage):
    def __init__(self, plots):
        super().__init__()
        self.plot_objects = plots

        self.setTitle("Plots")
        self.setSubTitle("View plots that will appear on the report...")

        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)    

        
        self.figure = Figure(figsize=(6, 7))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax2 = self.ax.twinx()

        scroll_area.setWidget(self.canvas)
        layout.addWidget(scroll_area)

        self.curr_index = 0

        child_layout = QHBoxLayout()
        self.back_button = QPushButton('< Previous')
        self.next_button = QPushButton('Next >')
        self.back_button.clicked.connect(lambda: self.updatePlot(self.curr_index - 1))
        self.next_button.clicked.connect(lambda: self.updatePlot(self.curr_index + 1))
        self.back_button.clicked.connect(self.button_enabling)
        self.next_button.clicked.connect(self.button_enabling)
        child_layout.addWidget(self.back_button)
        child_layout.addWidget(self.next_button)
        layout.addLayout(child_layout)

        self.setLayout(layout)

        self.refreshed = False

    def initializePage(self):
        if not self.refreshed:
            self.refresh(self.plot_objects)

    def button_enabling(self):
        if self.curr_index - 1 < 0:
            self.back_button.setDisabled(True)
        else:
            self.back_button.setDisabled(False)
        if self.curr_index + 1 >= len(self.plots):
            self.next_button.setDisabled(True)
        else:
            self.next_button.setDisabled(False)

    def refresh(self, plots):
        self.plots = plots.plot_list
        self.ax.clear()
        self.curr_index = 0
        self.button_enabling()
        self.updatePlot(self.curr_index)


    def updatePlot(self, index):
        if index < 0 or index >= len(self.plots):
            return
        else:
            self.curr_index = index
        self.ax.clear()
        curr_plot = self.plots[self.curr_index]
        if not curr_plot.x_axis or not curr_plot.y_axis:
            self.canvas.draw()
            return
        tc_cols = [i for i in curr_plot.y_axis if re.search(r"^TC\d+", i) or i=='AIR TEMP.']
        other_cols = [i for i in curr_plot.y_axis if i not in tc_cols]
        if tc_cols and other_cols:
            if hasattr(self, 'ax2') and self.ax2 is not None:
                self.ax2.remove()
                self.ax2 = None
            self.ax2 = self.ax.twinx()
            for i in tc_cols:
                self.ax.plot(curr_plot.dataframe[curr_plot.x_axis], curr_plot.dataframe[i] , label=i)
            for i in other_cols:
                self.ax2.plot(curr_plot.dataframe[curr_plot.x_axis], curr_plot.dataframe[i], label=i, linestyle='--')
            self.ax2.set_ylabel(curr_plot.second_y_label)

            if curr_plot.legend:
                handles, labels = self.ax.get_legend_handles_labels()
                handles2, labels2 = self.ax2.get_legend_handles_labels()
                self.ax.legend(handles2+handles, labels2+labels, loc='upper center', ncol=6, bbox_to_anchor=(0.5, -0.15))
        else:
            if hasattr(self, 'ax2') and self.ax2 is not None:
                self.ax2.remove()
                self.ax2 = None
            for i in curr_plot.y_axis:
                self.ax.plot(curr_plot.dataframe[curr_plot.x_axis], curr_plot.dataframe[i] , label=i)
            if curr_plot.legend:
                self.ax.legend(loc='upper center', ncol=6, bbox_to_anchor=(0.5, -0.15))
        self.ax.set_title(curr_plot.title)
        self.ax.set_xlabel(curr_plot.x_label)
        self.ax.set_ylabel(curr_plot.y_label)
        self.figure.tight_layout()
        self.canvas.draw()
