from matplotlib.widgets import RectangleSelector
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import stats

import matplotlib

matplotlib.use("Qt5Agg")

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def filter_graph_data(joined_df: pd.DataFrame) -> pd.DataFrame:
    joined_df = joined_df.filter(items=["Rep_1(ml/l)", "Sbeox0ML/L", "Sbeox1ML/L"])

    return joined_df


class Plotter(QtWidgets.QWidget):
    def __init__(self, df):
        super().__init__()

        self.df = df.copy()
        self.original_df = df.copy()

        self.setWindowTitle("Plotter")
        self.setGeometry(100, 100, 800, 600)

        frame = QtWidgets.QFrame(self)
        frame_layout = QtWidgets.QHBoxLayout(frame)

        var_names = [c for c in df.columns if c not in ["index", "Rep_1(ml/l)"]]
        self.var_selected = QtWidgets.QComboBox(self)
        self.var_selected.addItems(var_names)
        self.var_selected.currentIndexChanged.connect(self.update_plot)
        frame_layout.addWidget(self.var_selected)

        done_button = QtWidgets.QPushButton("Done", self)
        done_button.clicked.connect(self.close)
        frame_layout.addWidget(done_button)

        save_image_button = QtWidgets.QPushButton("Save Plot as Image", self)
        save_image_button.clicked.connect(self.save_image)
        frame_layout.addWidget(save_image_button)

        reset_button = QtWidgets.QPushButton("Reset Graph", self)
        reset_button.clicked.connect(self.reset_plot)
        frame_layout.addWidget(reset_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(frame)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)
        self.canvas.ax = self.canvas.figure.subplots()

        self.rs = RectangleSelector(
            self.canvas.ax, self.onselect, interactive=True, useblit=True, button=[1]
        )

        self.update_plot()

    def closeEvent(self, event):
        self.df.to_csv("updated_data.csv", index=False)
        app = QtWidgets.QApplication.instance()
        app.quit()

    def determine_outliers(self):
        var = self.var_selected.currentText()

        x_q1 = self.df[var].quantile(0.25)
        x_q3 = self.df[var].quantile(0.75)
        x_iqr = x_q3 - x_q1

        y_q1 = self.df["Rep_1(ml/l)"].quantile(0.25)
        y_q3 = self.df["Rep_1(ml/l)"].quantile(0.75)
        y_iqr = y_q3 - y_q1

        upper_bound_x = x_q3 + 1.5 * x_iqr
        lower_bound_x = x_q1 - 1.5 * x_iqr

        upper_bound_y = y_q3 + 1.5 * y_iqr
        lower_bound_y = y_q1 - 1.5 * y_iqr

        outliers = self.df.loc[
            (self.df[var] < lower_bound_x)
            | (self.df[var] > upper_bound_x)
            | (self.df["Rep_1(ml/l)"] < lower_bound_y)
            | (self.df["Rep_1(ml/l)"] > upper_bound_y)
        ]

        return outliers

    def update_plot(self):
        var = self.var_selected.currentText()
        canvas = self.canvas
        ax = canvas.ax
        ax.clear()
        ax.scatter(
            self.df[var], self.df["Rep_1(ml/l)"], color="blue", label="Data Points"
        )

        outliers = self.determine_outliers()
        ax.scatter(
            outliers[var],
            outliers["Rep_1(ml/l)"],
            color="grey",
            label="Suggested Outliers",
        )

        idx = np.isfinite(self.df[var]) & np.isfinite(self.df["Rep_1(ml/l)"])
        z = np.polyfit(self.df[var][idx], self.df["Rep_1(ml/l)"][idx], 1)
        slope = z[0]
        intercept = z[1]
        p = np.poly1d(z)

        self.df["Slope"] = z[0]
        self.df["y-int"] = z[1]

        self.df["Trendline"] = p(self.df[var])
        self.df = self.df.sort_values(by=["Trendline"])
        ax = self.df.plot(
            x=var,
            y="Trendline",
            color="red",
            ax=ax,
            label=f"Slope = {slope:.4f},  Y-Intercept: {intercept:.4f}",
        )

        ax.legend()

        ax.set_xlabel(var)
        ax.set_ylabel("Rep_1(ml/l)")
        canvas.draw()

    def reset_plot(self):
        self.df = self.original_df
        self.update_plot()

    def save_image(self):
        var = self.var_selected.currentText()
        sample = var.replace("ML/L", "")
        self.figure.savefig(f"plot_{sample}.png")

    def onselect(self, eclick, erelease):
        if eclick.ydata > erelease.ydata:
            eclick.ydata, erelease.ydata = erelease.ydata, eclick.ydata
            if eclick.xdata > erelease.xdata:
                eclick.xdata, erelease.xdata = erelease.xdata, eclick.xdata

        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        var = self.var_selected.currentText()
        selected_data = self.df[
            (self.df[var] >= x1)
            & (self.df[var] <= x2)
            & (self.df["Rep_1(ml/l)"] >= y1)
            & (self.df["Rep_1(ml/l)"] <= y2)
        ]

        self.df.loc[selected_data.index, var] = np.nan

        self.update_plot()


def new_and_old_SOC_calculations(path: str, joined_df: pd.DataFrame):
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Expected {path} to be in the current working directory, but it was not found"
        )

    updated_graph_df = pd.read_csv(path)

    # take in csv from graph output
    # get slope and y-int from each Sbeox
    # take value and apply to new calibrated columns
    # calculate new SOC
    # calculate old SOC??
    # return full of with new cols

    pass


if __name__ == "__main__":
    joined_df = pd.read_csv("atl001_2022_joined.csv")
    graph_data = filter_graph_data(joined_df)

    app = QtWidgets.QApplication([])
    plotter = Plotter(graph_data)

    plotter.show()
    app.exec_()
    app.quit()
    sys.exit()
