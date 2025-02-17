from PyQt5.QtWidgets import (QWizardPage,
                             QVBoxLayout,
                             QGroupBox,
                             QGridLayout,
                             QFrame,
                             QCheckBox,
                             QLabel,)

from utilities import modify_database, ramp_rates, avg_ramp_rate, ramp_rates_to_string, dwell_time, tc_time

class DataPage(QWizardPage):
    def __init__(self, dataframe_obj, data_obj):
        super().__init__()

        self.dataframe_obj = dataframe_obj
        self.data_obj = data_obj

        self.setTitle("Data")

        self.data_labels = {
            "Cooling" : ["Ramp Rates for Cooling Curves: ", "0.0"],
            "avgCooling" : ["Average Ramp Rate for Cooling Curve:  ", "0.0"],
            "Heating" : ["Ramp Rates for Heating Curves: ", "0.0"],
            "avgHeating" : ["Average Ramp Rate for Heating Curve:  ", "0.0"],
            "dwell" : ["Dwell Times:  ", "0.0"],
            "tc" : ["Maximum width of tc at a given time:  ", "0.0"]
        }

        layout = QVBoxLayout()

        
        
        self.card_group = QGroupBox("Select Data", self)
        self.card_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; padding: 10px;}")
        self.grid_layout = QGridLayout(self.card_group)
        self.checkboxes = []

        
        layout.addWidget(self.card_group)
        self.setLayout(layout)
        self.refreshed = False

    def create_card(self, type, checked):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""QFrame {
    background-color: lightblue;
    border-radius: 10px;
    padding: 10px;
    margin: 10px;
}""")
        card_layout = QVBoxLayout(card)
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        title = QLabel(self.data_labels[type][0])
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        desc = QLabel(self.data_labels[type][1])
        card_layout.addWidget(checkbox)
        card_layout.addWidget(title)
        card_layout.addWidget(desc)
        self.checkboxes.append((type, checkbox))

        return card

    def initializePage(self):
        if not self.refreshed:
            self.refresh(self.dataframe_obj, self.data_obj)
    
    def refresh(self, dataframe, data):
        self.dataframe = dataframe.dataframe
        self.data = data

        self.update()
        self.checkboxes.clear()

        row, col = 0, 0

        for i, title in enumerate(self.data_labels):
            card_widget = self.create_card(title, self.data.checked[i])
            self.grid_layout.addWidget(card_widget, row, col)

            col += 1
            if col > 1:  # Move to the next row after 2 cards per row
                col = 0
                row += 1
    
    def update(self):
        df = modify_database(self.dataframe)
        self.data_labels["Cooling"][1]=ramp_rates_to_string(ramp_rates('Cooling', df))
        self.data_labels["Heating"][1]=ramp_rates_to_string(ramp_rates('Heating', df))
        self.data_labels["avgCooling"][1]=avg_ramp_rate(ramp_rates('Cooling', df))
        self.data_labels["avgHeating"][1]=avg_ramp_rate(ramp_rates('Heating', df))
        self.data_labels["dwell"][1]=(dwell_time(df))
        self.data_labels["tc"][1]=(tc_time(df))


    def validatePage(self):
        data_indexes = []
        checked_indexes = []
        for title_label, checkbox in self.checkboxes:
            data_indexes.append(self.data_labels[title_label])
            checked_indexes.append(checkbox.isChecked())
        self.data.update_data(list(data_indexes), list(checked_indexes))

        return True
