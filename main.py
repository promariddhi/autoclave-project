from PyQt5.QtWidgets import QApplication, QWizard
import sys
from PyQt5.QtCore import Qt, QFile, QTextStream
import resources_rc  


from wizard_pages.file_loader_page import FileLoadingPage
from wizard_pages.data_page import DataPage
from wizard_pages.report_parameters_page import ReportParametersPage
from wizard_pages.plotter_page import PlotterPage
from wizard_pages.report_preview import ReportPreview

from shared import Dataframe, Plots, Data

class Wizard(QWizard):
    def __init__(self):
        super().__init__()
        self.dataframe = Dataframe()
        self.plots = Plots()
        self.data = Data()

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.85)

        self.setWindowTitle("Autoclave Data Analyser")
        self.setGeometry((screen_width - window_width) // 2, (screen_height - window_height) // 2, window_width, window_height)
        self.setWizardStyle(QWizard.ModernStyle)

        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

        self.page1 = FileLoadingPage(self.dataframe)
        self.page2 = ReportParametersPage(self.dataframe, self.plots)
        self.page3 = PlotterPage(self.plots)
        self.page4 = DataPage(self.dataframe, self.data)
        self.page5 = ReportPreview(self.plots, self.data)

        self.addPage(self.page1)
        self.addPage(self.page2)
        self.addPage(self.page3)
        self.addPage(self.page4)
        self.addPage(self.page5)
    
    def nextId(self):
        if self.currentPage()==self.page2 and self.page2.no_plots_chosen():
            return 3
        return super().nextId()


def main():

    app = QApplication(sys.argv)

    wizard = Wizard()

    file = QFile(":/styles.qss")
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        stylesheet = stream.readAll()
        app.setStyleSheet(stylesheet)


    wizard.exec_()

    wizard.rejected.connect(app.quit)

if __name__ == "__main__":
    main()