from pathlib import Path
from io import StringIO
from typing import Tuple
from matplotlib.widgets import RectangleSelector
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from openpyxl import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.drawing.image import Image
from mpl_toolkits.basemap import Basemap

import matplotlib

matplotlib.use("Qt5Agg")
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import DF_O2


def split_data(joined_df: pd.DataFrame, instr_df: pd.DataFrame):
    """ """
    join_dfs = joined_df.merge(
        instr_df, how="inner", left_on="ShTrpStn", right_on="Filename"
    )
    join_dfs.drop(["Filename"], axis=1, inplace=True)

    df1 = join_dfs[
        join_dfs["Primary Oxygen Serial Number"]
        == instr_df["Primary Oxygen Serial Number"].iloc[0]
    ]
    df1 = df1[
        df1["Secondary Oxygen Serial Number"]
        == instr_df["Secondary Oxygen Serial Number"].iloc[0]
    ]

    outer = join_dfs.merge(df1, how="outer", indicator=True)
    anti_join = outer[(outer._merge == "left_only")].drop("_merge", axis=1)

    print(anti_join)

    return df1, anti_join


def SOCcalc_split(split_df1: pd.DataFrame, split_df2: pd.DataFrame):
    """
    Calculate the new and old dissolved oxygen Standard Output Calibration (SOC) values from an instrument and a dataset.

    Args:
        instr_df (pd.DataFrame): A DataFrame containing the primary and secondary old dissolved oxygen SOC values.
        joined_df (pd.DataFrame): A DataFrame containing dissolved oxygen measurements and reference values.

    Returns:
        Tuple[List[float], float]: A tuple containing the new dissolved oxygen SOC values (as a list with primary and secondary
        values) and the averaged Winkler oxygen calculation.
    """

    df1 = split_df1.copy()
    df2 = split_df2.copy()

    newSOC = []
    oldSOC = []

    df1["WinkOxCalc0"] = df1.apply(
        lambda x: round((x["WINKLER"] / x["Sbeox0ML/L"]), 4), axis=1
    )
    df1["WinkOxCalc1"] = df1.apply(
        lambda x: round((x["WINKLER"] / x["Sbeox1ML/L"]), 4), axis=1
    )

    df2["WinkOxCalc0"] = df2.apply(
        lambda x: round((x["WINKLER"] / x["Sbeox0ML/L"]), 4), axis=1
    )
    df2["WinkOxCalc1"] = df2.apply(
        lambda x: round((x["WINKLER"] / x["Sbeox1ML/L"]), 4), axis=1
    )

    df_list = [df1, df2]

    for i in df_list:
        oldSOC_val = [
            i["Primary Oxygen Old SOC"].iloc[1],
            i["Secondary Oxygen Old SOC"].iloc[1],
        ]

        winklerOx_calc = []
        winklerOx_calc.extend(i["WinkOxCalc0"].values.tolist())
        winklerOx_calc.extend(i["WinkOxCalc1"].values.tolist())
        winklerOx_avg = round(sum(winklerOx_calc) / len(winklerOx_calc), 4)

        oldSOC.extend([oldSOC_val[0], oldSOC_val[1]])
        newSOC.append(round(float((winklerOx_avg) * (oldSOC_val[0])), 4))
        newSOC.append(round(float((winklerOx_avg) * (oldSOC_val[1])), 4))

    return newSOC, oldSOC


def instruments_used(df: pd.DataFrame):
    prim, ind1 = np.unique(df["Primary Oxygen Serial Number"].values.tolist(), return_index=True)
    sec, ind2 = np.unique(df["Secondary Oxygen Serial Number"].values.tolist(), return_index= True)

    primList = prim[np.argsort(ind1)]
    secList = sec[np.argsort(ind2)]

    instr = pd.DataFrame(
        {
            "Primary": primList,
            "Secondary": secList,
        }
    )

    return instr, primList, secList


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
        self.df.to_csv(f"updated_data_{ship_name}{ship_trip}{df_num}.csv", index=False)
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

        label = var.replace("ML/L", "")
        self.df[f"Slope_{label}"] = z[0]
        self.df[f"yint_{label}"] = z[1]

        self.df[f"Trendline_{label}"] = p(self.df[var])
        self.df = self.df.sort_values(by=[f"Trendline_{label}"])
        ax = self.df.plot(
            x=var,
            y=f"Trendline_{label}",
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
        self.figure.savefig(f"plot_{sample}_{graphic_titles}_{df_num}.png")

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


def updated_graph_dfs(path1: str, path2: str):

    if not Path(path1).exists() or not Path(path2).exists:
        raise FileNotFoundError(
            f"{path1} and {path2} required to be in the current working directory. Did you save both graphs?"
        )

    graphA_df = pd.read_csv(path1)
    graphB_df = pd.read_csv(path2)

    return graphA_df, graphB_df


def regression_data(
    graphA_df: pd.DataFrame,
    graphB_df: pd.DataFrame,
    newSOC: list,
    oldSOC: list,
):
    """ """

    summary = pd.DataFrame
    instr_list = []

    for i in range(0, len(primList)):
        instr_list.append(primList[i])
        instr_list.append(secList[i])
    
    slope = [graphA_df["Slope_Sbeox0"].iloc[0], graphA_df["Slope_Sbeox1"].iloc[0],graphB_df["Slope_Sbeox0"].iloc[0], graphB_df["Slope_Sbeox1"].iloc[0]]
    yint = [graphA_df["yint_Sbeox0"].iloc[0], graphA_df["yint_Sbeox1"].iloc[0], graphB_df["yint_Sbeox0"].iloc[0], graphB_df["yint_Sbeox1"].iloc[0]]

    summary = pd.DataFrame(
        {
            "Instr": instr_list,
            "Slope": slope,
            "y-int": yint,
            "OldSOC": oldSOC,
            "NewSOC": newSOC,
        }
    )

    return summary

def calibrated_dO2_sheet(orig_bot_df: pd.DataFrame, graph_df: pd.DataFrame) -> pd.DataFrame:

    calibrated_df = orig_bot_df.copy()
    calibrated_df["Sbeox0_Calibrated"] = graph_df["Trendline_Sbeox0"]
    calibrated_df["Sbeox1_Calibrated"] = graph_df["Trendline_Sbeox1"]

    return calibrated_df

def write_to_DO2_excel(
    bot_file,
    txt_file,
    fail_tit,
    instr: pd.DataFrame,
    title: str,
    instr_used: pd.DataFrame,
    station_id: pd.DataFrame,
    reg_data: pd.DataFrame,
):
    start_date = bot_file["Date"].min()
    end_date = bot_file["Date"].max()

    wb = Workbook()

    # Summary sheet with map
    ws = wb.active
    ws.title = "Summary"
    ws["A1"] = "Oxygen Calibration"
    ws["A2"] = f"AZMP Survey for {ship_name} {ship_trip}"
    ws["A3"] = f"{start_date} to {end_date}"

    ws["A5"] = "The following instruments were used:"
    ws["A11"] = "The following stations were occupied:"
    ws["A18"] = "The regression data is:"

    map_img = Image(f"{title}_map.png")
    map_img.anchor = "I2"
    ws.add_image(map_img)

    ws = wb.create_sheet("Plots", 1)
    wb.active = 1
    plot0A_png = Image(f"plot_Sbeox0_{graphic_titles}_0.png")
    plot0A_png.anchor = "A1"
    plot1A_png = Image(f"plot_Sbeox1_{graphic_titles}_0.png")
    plot1A_png.anchor = "A30"
    ws.add_image(plot0A_png)
    ws.add_image(plot1A_png)
    plot0B_png = Image(f"plot_Sbeox0_{graphic_titles}_1.png")
    plot0B_png.anchor = "N1"
    plot1B_png = Image(f"plot_Sbeox1_{graphic_titles}_1.png")
    plot1B_png.anchor = "N30"
    ws.add_image(plot0B_png)
    ws.add_image(plot1B_png)

    wb.save(f"DO2_calibration_output_{title}.xlsx")
    with pd.ExcelWriter(
        f"DO2_calibration_output_{title}.xlsx",
        mode="a",
        engine="openpyxl",
        if_sheet_exists="overlay",
    ) as writer:
        instr_used.to_excel(
            writer, sheet_name="Summary", startrow=5, index=False, header=True
        )
        station_id.to_excel(
            writer, sheet_name="Summary", startrow=11, index=False, header=False
        )
        reg_data.to_excel(
            writer, sheet_name="Summary", startrow=18, index=False, header=True
        )
        # master_bot.to_excel(writer, sheet_name='Master bottle file')
        # all_data.to_excel(writer, sheet_name='Data')
        bot_file.to_excel(writer, sheet_name="Original bot file", index=False)
        txt_file.to_excel(writer, sheet_name="Original text file", index=False)
        fail_tit.to_excel(writer, sheet_name="Failed Titrations", index=False)
        instr.to_excel(writer, sheet_name="Instruments", index=False)


def write_to_bot_excel(bot_file, met_file, title: str):
    """ """
    with pd.ExcelWriter(f"master_bot_output_{title}.xlsx", mode="w") as writer:
        met_file.to_excel(writer, sheet_name="met file", index=False)
        bot_file.to_excel(writer, sheet_name="Original bot file", index=False)


if __name__ == "__main__":

    year = int(input("Year: "))
    ship_name = input("Ship name: ")
    ship_trip = input("Ship trip: ")
    graphic_titles = f"{ship_name}{ship_trip}_{year}"

    instr_df = DF_O2.generate_instrument_df(f"{ship_name}{ship_trip}_{year}_Instruments.csv")
    instr_used, primList, secList= instruments_used(instr_df)

    orig_bot_df, bot_df = DF_O2.generate_bot_df(f"{ship_name}{ship_trip}.bot")
    orig_o2_df, o2_df = DF_O2.generate_o2_df(f"{ship_name}{ship_trip}_meanO2.txt")
    met_df = DF_O2.generate_met_df(f"{ship_name}{ship_trip}_{year}_met.csv")

    joined_df = DF_O2.join_bot_o2_met_dfs(bot_df, o2_df, met_df)

    successful_titration, failed_titrations = DF_O2.seperate_based_on_winkler_diff(
        joined_df
    )

    joined_file = f"{ship_name}{ship_trip}_{year}_joined.csv"
    print(f"Written joined bot, o2 and met DataFrame to {joined_file}")
    successful_titration.to_csv(joined_file, index=False)

    station_id = DF_O2.stations_occupied(joined_df)
    DF_O2.generate_map(joined_df, bot_df, graphic_titles)


    df1, df2 = split_data(successful_titration, instr_df)
    newSOC, oldSOC = SOCcalc_split(df1, df2)
    
    #df_list = [df1, df2]
    df_num=0
    #for i in df_list:
    
    graphA_df = DF_O2.filter_graph_data(df1)
    app = QtWidgets.QApplication([])
    plotter = Plotter(graphA_df)
    plotter.show()
    app.exec_()

    df_num+= 1
    graphB_df = DF_O2.filter_graph_data(df2)
    plotter = Plotter(graphB_df)
    plotter.show()
    app.exec_()
    app.quit()
        
    
    graphA_df, graphB_df= updated_graph_dfs(f"updated_data_{ship_name}{ship_trip}0.csv", f"updated_data_{ship_name}{ship_trip}1.csv")
    #prDMplt = pressure_plot(updated_graph_df, joined_df)
    
    
    reg_data = regression_data(graphA_df, graphB_df, newSOC, oldSOC)
    #dO2_cal = calibrated_dO2_sheet(orig_bot_df, updated_graph_df)

    write_to_DO2_excel(
        orig_bot_df,
        orig_o2_df,
        failed_titrations,
        instr_df,
        graphic_titles,
        instr_used,
        station_id,
        reg_data,
    )
    #write_to_bot_excel(orig_bot_df, met_df, graphic_titles)