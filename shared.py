from PyQt5.QtCore import QObject, pyqtSignal

class Plotting:
    def __init__(self):
        self.title = ""
        self.x_label = ""
        self.y_label = ""
        self.second_y_label = ""
        self.legend = True
        self.x_axis = ""
        self.y_axis = []
        self.dataframe = None

    def update_data(self, title, x_label, y_label, second_y_label, legend, x_col, y_cols, dataframe):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.second_y_label = second_y_label
        self.legend = legend
        self.x_axis = x_col
        self.y_axis = y_cols
        self.dataframe = dataframe

class Plots:
    def __init__(self):
        self.plot_list = []
    
    def update_data(self, list):
        self.plot_list = list



class Dataframe(QObject):
    data_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dataframe = None
        self.columns = {}
        self.title = ""
    
    def update_data(self, dataframe, columns, title):
        self.dataframe = dataframe
        self.columns = columns
        self.title = title
        self.data_updated.emit()

class Data:
    def __init__(self):
        self.data = []
        self.checked = [True, True, True, True, True, True]
    
    def update_data(self, data, checked):
        self.data = data
        self.checked = checked

