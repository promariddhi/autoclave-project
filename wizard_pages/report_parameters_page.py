from PyQt5.QtWidgets import (QWizardPage, 
                             QVBoxLayout, 
                             QPushButton, 
                             QScrollArea, 
                             QWidget, 
                             QGroupBox, 
                             QHBoxLayout, 
                             QFormLayout, 
                             QLineEdit, 
                             QCheckBox,
                             QComboBox,
                             QListWidget,
                             QMessageBox,
                             QListWidgetItem)

from shared import Plotting

class ReportParametersPage(QWizardPage):
    def __init__(self, dataframe, plots):
        super().__init__()

        self.setTitle("Plot Configuration")
        self.setSubTitle("Configure the columns and settings for the plot.")

        main_layout = QVBoxLayout()

        self.add_button = QPushButton("+ Add Plot Settings")
        self.add_button.clicked.connect(lambda: self.add_plot_settings(dataframe))
        main_layout.addWidget(self.add_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
    
        self.plot_settings_container = QVBoxLayout(scroll_content)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)
        self.plots_object = plots
        self.plots = {}

        self.count = 0

    def add_plot_settings(self, dataframe):
        self.count += 1
        plot_object = Plotting()
        
        graph_title = dataframe.title
        columns = [ i for i in dataframe.columns if dataframe.columns[i] != 'object']

        settings_group = QGroupBox("Plot Settings")
        settings_layout = QFormLayout()

        settings_group.setObjectName(str(self.count))
        child_layout = QHBoxLayout()
        close_button = QPushButton("X")
        close_button.setFixedWidth(50)
        close_button.setStyleSheet("color: red; font-weight: bold;")  # Optional styling
        close_button.clicked.connect(lambda: self.remove_plot_settings(settings_group))
        child_layout.addWidget(close_button)

        self.set_button = QPushButton("Set")
        child_layout.addWidget(self.set_button)
        settings_layout.addRow(child_layout)

        # Graph title
        title_input = QLineEdit()
        title_input.setText(graph_title)
        settings_layout.addRow("Graph Title:", title_input)
        title_input.textChanged.connect(lambda: self.set_button.setDisabled(False))

        # X-axis label
        x_label_input = QLineEdit()
        x_label_input.setText('Cycle time, min')
        x_label_input.textChanged.connect(lambda: self.set_button.setDisabled(False))

        settings_layout.addRow("X-axis Label:", x_label_input)

        # Y-axis label
        y_label_input = QLineEdit()
        y_label_input.setText(u'Temp (\u00B0C)')
        settings_layout.addRow("Y-axis Label:", y_label_input)
        y_label_input.textChanged.connect(lambda: self.set_button.setDisabled(False))


        second_y_label_input = QLineEdit()
        second_y_label_input.setText('Pressure (bar)')
        second_y_label_input.textChanged.connect(lambda: self.set_button.setDisabled(False))
        settings_layout.addRow("Second Y-axis Label:", second_y_label_input)

        # Show legend checkbox
        show_legend_checkbox = QCheckBox("Show Legend")
        show_legend_checkbox.setChecked(True)
        show_legend_checkbox.stateChanged.connect(lambda: self.set_button.setDisabled(False))
        settings_layout.addRow(show_legend_checkbox)

        # X-axis column (single selection)
        x_axis_dropdown = QComboBox()
        x_axis_dropdown.addItems(columns)
        x_axis_dropdown.setCurrentIndex(0)
        x_axis_dropdown.currentIndexChanged.connect(lambda: self.set_button.setDisabled(False))
        settings_layout.addRow("X-axis Column:", x_axis_dropdown)

        # Y-axis columns (multi-selection)
        self.y_axis_list = QListWidget()
        self.y_axis_list.setSelectionMode(QListWidget.MultiSelection)
        for col in columns:
            item = QListWidgetItem(col)
            self.y_axis_list.addItem(item)
        self.y_axis_list.selectionModel().selectionChanged.connect(lambda: self.set_button.setDisabled(False))
        settings_layout.addRow("Y-axis Columns:", self.y_axis_list)
        self.selected_items = [item.text() for item in self.y_axis_list.selectedItems()]
        self.set_button.clicked.connect(self.set_selected_items)
        self.set_button.clicked.connect(lambda: plot_object.update_data(graph_title,x_label_input.text().strip(), y_label_input.text().strip(), second_y_label_input.text().strip(), show_legend_checkbox.isChecked(), x_axis_dropdown.currentText(), self.selected_items, dataframe.dataframe))
        self.set_button.clicked.connect(lambda: self.set_button.setDisabled(True))
        self.plots[self.count] = plot_object
        # Add the settings layout to the group box
        settings_group.setLayout(settings_layout)

        # Add the group box to the container
        self.plot_settings_container.addWidget(settings_group)
    
    def set_selected_items(self):
        self.selected_items = [item.text() for item in self.y_axis_list.selectedItems()]
        if not self.selected_items:
            QMessageBox.warning(None, "Warning", "Y axis columns names missing")


    
    def remove_plot_settings(self, plot_settings):
        plot_settings.setParent(None)


    def no_plots_chosen(self):
        if self.plot_settings_container.count() == 0:
            return True
        return False
    
    def validatePage(self):
        plot_indexes = []
        for i in range(self.plot_settings_container.count()):
            item = self.plot_settings_container.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QGroupBox):
                plot_indexes.append(widget.objectName())
        list = [self.plots[int(i)] for i in plot_indexes]
        self.plots_object.update_data(list)
        return True
