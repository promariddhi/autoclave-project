from PyQt5.QtWidgets import (QVBoxLayout, 
                             QPushButton, 
                             QFileDialog, 
                             QWizardPage, 
                             QMessageBox, 
                             QTextBrowser,
                             
)

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument
import matplotlib.pyplot as plt
import base64
from io import BytesIO

import re

class ReportPreview(QWizardPage):
    def __init__(self, plots, data):
        super().__init__()
        self.plot_obj = plots
        self.data = data
        layout = QVBoxLayout()

        self.setTitle("Preview and Save File")

        self.generated_html_content = ""

        self.web_view = QTextBrowser()
        self.web_view.setHtml(self.generated_html_content)


        layout.addWidget(self.web_view)

        save_html_button = QPushButton("Save HTML")
        save_html_button.clicked.connect(self.save_html)
        save_pdf_button = QPushButton("Save PDF")
        save_pdf_button.clicked.connect(self.save_pdf)

        layout.addWidget(save_html_button)
        layout.addWidget(save_pdf_button)

        self.setLayout(layout)

        self.refreshed = False

    def initializePage(self):
        if not self.refreshed:
            self.preview_html(self.plot_obj, self.data)


    def generate_plot(self, curr_plot):
        plt.rcdefaults()
        fig, self.ax = plt.subplots(figsize=(8, 6))
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
                self.ax2.plot(curr_plot.dataframe[curr_plot.x_axis], curr_plot.dataframe[i], label=i, linestyle='-.')
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
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()
        plt.close(fig)

        return image_base64 
    
    def generate_html(self, plots, data):
        plots_html = ""

        for plot in plots:
            plot_base64 = self.generate_plot(plot)
            plots_html += f'<img src="data:image/png;base64,{plot_base64}" alt="{plot.title}" class="plots"><br>'


        html_rows = ""
        for item in data:
            html_rows += f'<tr>\n    <td>{item[0].strip(":")}</td>\n    <td>{item[1].replace('\n','<br>')}</td>\n</tr>\n'



        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Preview</title>
            <style>
            table, th, td {{
                border: 1px solid black;
                border-collapse: collapse;
                width : 100%;
            }}
            th, td {{
                padding: 15px;
            }}
            .plots{{
            width: 100%;
            }}
            </style>
        </head>
        <body>
            <center>{plots_html}</center>
            <center>
                <table><tbody>
                    {html_rows}
                    </tbody>
                </table>
            </center>
        </body>
        </html>
        """

        

        return html_content
    
    def preview_html(self, plots, data):
        self.plots = plots.plot_list
        self.data = data
        checked_data = [i for _, i in enumerate(self.data.data) if self.data.checked[_]]
        self.generated_html_content = self.generate_html(self.plots, checked_data)
        self.web_view.setHtml(self.generated_html_content)

    def save_html(self):
        save_path,_ = QFileDialog.getSaveFileName(self, "Save HTML File", "", "HTML Files (*.html)")
        if save_path:
            try:
                with open(save_path, "w") as file:
                    file.write(self.generated_html_content)
                QMessageBox.information(self, "Success", f"File saved as HTML: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save HTML: {str(e)}")

    def save_pdf(self):
        save_path,_ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF Files (*.pdf)")
        if save_path:
            try:
                # Set up QPrinter for printing to PDF
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(save_path)
                printer.setPageMargins(0,0,0,0,QPrinter.Millimeter)
                
                # Create a QTextDocument and set its HTML content
                doc = QTextDocument()
                doc.setHtml(self.generated_html_content)

                # Print the document to the PDF file
                doc.print_(printer)

                # Show success message
                QMessageBox.information(self, "Success", f"File saved as PDF: {save_path}")
            except Exception as e:
                # Show error message
                QMessageBox.critical(self, "Error", f"Could not save PDF: {str(e)}")


