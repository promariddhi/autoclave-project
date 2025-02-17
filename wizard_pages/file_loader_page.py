from PyQt5.QtWidgets import QWizardPage, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox
import pandas as pd
import re

class FileLoadingPage(QWizardPage):
    def __init__(self, dataframe):
        super().__init__()
        self.dataframe = dataframe

        self.setTitle("File Upload")
        self.setSubTitle("Enter File Path or Browse...")

        main_layout = QVBoxLayout()

        child_layout1 = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("No File Selected")
        child_layout1.addWidget(self.file_input)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.open_file_dialog_box)
        child_layout1.addWidget(browse_button)

        main_layout.addLayout(child_layout1)
        
        child_layout2 = QHBoxLayout()
        self.sheet_input_label = QLabel("Sheet Name: ")
        self.sheet_input_label.setStyleSheet("color: white;")
        self.sheet_input = QLineEdit()
        self.sheet_input.setText("GENERAL")
        child_layout2.addWidget(self.sheet_input_label)
        child_layout2.addWidget(self.sheet_input)

        main_layout.addLayout(child_layout2)

        self.setLayout(main_layout) 
    
    def open_file_dialog_box(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a file", "", "Excel Files (*.xlsx)")
        if file_path:
            self.file_input.setText(file_path)
        else:
            self.file_input.clear()
    
    def validatePage(self):
        try:
            data = pd.read_excel(self.file_input.text().strip(), self.sheet_input.text().strip())
        except FileNotFoundError:
            QMessageBox.critical(None, "Error", "File name or path wrong!")
            return False
        except ValueError:
            QMessageBox.critical(None, "Error", "Sheet name wrong!")
            return  False
        
        cols = data.dtypes.to_dict()
        for i in cols.keys():
            cols[i] = str(cols[i])
        self.dataframe.update_data(data, cols, re.search(r"([A-Za-z0-9-]+)_\w+.xlsx", self.file_input.text().strip()).group(1))
        return True