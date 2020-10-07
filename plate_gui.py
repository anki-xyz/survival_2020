from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, \
    QPushButton, QGridLayout, QMessageBox, QCheckBox

import matplotlib.pyplot as plt 
import pandas as pd 
import numpy  as np

MAGIC = 'Cycle(Seconds)/Well'

class PlateGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.l = QGridLayout(self)

        self.plate = None
        self.excel = None

        selectExcelFile = QPushButton("Select Excel File")
        selectPlateFile = QPushButton("Select Plate File")
        analyze = QPushButton("Analyze the shit out of it")
        selectExcelFile.setFixedSize(300, 100)
        selectPlateFile.setFixedSize(300, 100)
        analyze.setFixedSize(300, 100)

        selectExcelFile.clicked.connect(self.selectExcel)
        selectPlateFile.clicked.connect(self.selectPlate)
        analyze.clicked.connect(self.analyzeTheShit)

        self.c1 = QCheckBox("Show raw data")
        self.c2 = QCheckBox("Show individual samples")
        self.c3 = QCheckBox("Show mean samples")

        self.c1.setChecked(True)
        self.c2.setChecked(True)
        self.c3.setChecked(True)

        self.l.addWidget(selectExcelFile)
        self.l.addWidget(selectPlateFile)
        self.l.addWidget(analyze)
        self.l.addWidget(self.c1)
        self.l.addWidget(self.c2)
        self.l.addWidget(self.c3)

    def selectExcel(self):
        fn = QFileDialog.getOpenFileName(filter="*.xlsx")

        if fn:
            self.excel = fn[0]

    def selectPlate(self):
        fn = QFileDialog.getOpenFileName(filter="*.xlsx")

        if fn:
            self.plate = fn[0]

    def analyzeTheShit(self):
        if not self.plate or not self.excel:
            QMessageBox.critical(self, "FORGOT!",
                "You forgot to select both files!")

            return

        df = pd.read_excel(self.excel)

        save = {}

        for column_id, (column_name, column) in enumerate(df.items()):
            for row_id, element in enumerate(column):       
                if element == MAGIC:
                    save['column_name'] = column_name
                    save['column_id'] = column_id
                    save['row_id'] = row_id 
                    break

            if len(save):
                break

        print(save)

        DATA = df.iloc[save['row_id']:, save['column_id']:].values

        df_pretty = pd.DataFrame(DATA[1:], columns=DATA[0, :])
        df_pretty = df_pretty.replace("#SAT", np.nan)
        df_pretty.set_index(MAGIC)
        print(df_pretty.head())

        df_pretty.to_excel(self.excel+"_cleaned.xlsx")

        if self.c1.isChecked():
            df_pretty.plot(legend=False)
            plt.title("Overview raw data")
            plt.show()

        plate_view = pd.read_excel(self.plate, header=1, index_col=0)

        print(plate_view)

        unique_ids = np.unique(plate_view)
        unique_ids = unique_ids[~np.isnan(unique_ids)]
        unique_ids

        d = {}

        for uid in unique_ids:
            d[uid] = []
            
            for column_name, column in plate_view.items():
                for row_name, row in column.items():
                    if row == uid:
                        d[uid].append(f"{row_name}{column_name}")
            
        print(d)

        if self.c2.isChecked():
            for uid, columns in d.items():
                df_pretty[columns].plot()
                plt.title(uid)

        plt.show()

        to_df = {}

        # Show mean sample data if CB is checked
        if self.c3.isChecked():
            for uid, columns in d.items():
                to_df[uid] = df_pretty[columns].mean(1)
            
        df_pretty_mean = pd.DataFrame(to_df)
        print(df_pretty_mean)

        df_pretty_mean.to_excel(self.excel+"_avg.xlsx")

        df_pretty_mean.plot()
        plt.title("Average for unique samples")
        plt.savefig(self.excel+".png", dpi=300)
        plt.show()


if __name__ == '__main__':
    app = QApplication([])

    w = PlateGUI()
    w.show()

    app.exec_()      