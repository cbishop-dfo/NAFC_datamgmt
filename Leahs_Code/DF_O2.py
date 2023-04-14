from pathlib import Path
from io import StringIO
from typing import Tuple
from matplotlib.widgets import RectangleSelector
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import stats

import matplotlib
matplotlib.use("Qt5Agg")

import numpy as np
import matplotlib.pyplot as plt
#import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import geopandas




def generate_bot_df(path: str) -> pd.DataFrame:
    """
    This function generates a Pandas DataFrame from a CSV file located at the specified path.
    The generated DataFrame contains only a subset of columns.

    Args:
        

    Returns:
        pandas.DataFrame: The generated DataFrame containing the specified columns.

    Raises:
        FileNotFoundError: If the file at the specified path does not exist.
    """
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Expected {path} to be in the current working directory, but it was not found"
        )

    bot_df = pd.read_csv(path)
    bot_df = bot_df.filter(
        items=[
            "Stickr",
            "Station-ID",
            "ShTrpStn",
            "latitude",
            "longitude",
            "PrDM",
            "Sbeox0ML/L",
            "Sbeox1ML/L",
        ]
    )

    return bot_df


def generate_o2_df(path: str) -> pd.DataFrame:
    """
    This function generates a Pandas DataFrame from a text file located at the specified path.
    The header of the file is discarded, reads the rest of the file as CSV.
    The generated DataFrame contains only a subset of columns.

    Args:
        path (str): The file path to the text file containing the source data.

    Returns:
        pandas.DataFrame: The generated DataFrame containing the specified columns.

    Raises:
        FileNotFoundError: If the file at the specified path does not exist.
    """
    mean_o2_file_path = Path(path)
    if not mean_o2_file_path.exists():
        raise FileNotFoundError(
            f"Expected {path} to be in the current working directory, but it was not found"
        )

    mean_o2_file = mean_o2_file_path.read_text()
    _header, o2_csv = mean_o2_file.split("\n\n")
    o2_df = pd.read_csv(StringIO(o2_csv))
    o2_df = o2_df.filter(
        items=[
            "Sample",
            "[O2](ml/l)",
            "std_[O2](ml/l)",
            "Rep_1(ml/l)",
            "Rep_2(ml/l)",
            "Rep_3(ml/l)",
            "Rep_4(ml/l)",
            "Rep_5(ml/l)",
            "Rep_6(ml/l)",
        ]
    )
    # sbeox is eventually altered later in orig_oxy_code
    # masterdf["DO2"][smd] = float(startmasterdf["Sbeox0ML/L"][smd]) * slp + intt DO2 calibrated
    return o2_df


def generate_met_df(path: str) -> pd.DataFrame:
    """
    This function generates a Pandas DataFrame containing weather data from a CSV file located at the specified path.
    Converts and renames the "Wind Speed" column from knots into metres per second.

    Args:
        path (str): A file path to the CSV file containing the weather data.

    Returns:
        pandas.DataFrame:
        A DataFrame containing the weather data filtered to include only the columns 'Station',
        'Wind Dir [deg/10]', and the converted 'Wind Speed [m/s]'.

    Raises:
        FileNotFoundError: If the file at the specified path does not exist.
    """
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Expected {path} to be in the current working directory, but it was not found"
        )

    met_df = pd.read_csv(path)
    met_df = met_df.filter(items=["Station", "Wind Dir [deg/10]", "Wind Speed [kts]"])

    knot_to_mps_conversion = 1.944
    met_df["Wind Speed [kts]"] = met_df["Wind Speed [kts]"].apply(
        lambda x: round(x / knot_to_mps_conversion, 4)
    )
    met_df = met_df.rename(columns={"Wind Speed [kts]": "Wind Speed [m/s]"})

    return met_df


def seperate_based_on_winkler_diff(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    
    """
    df["WINKLER-DIFF"] = df.apply(
        lambda x: abs(x["Rep_1(ml/l)"] - x["Rep_2(ml/l)"]), axis=1
    )
    df["WINKLER"] = df.apply(
        lambda x: ((x["Rep_1(ml/l)"] + x["Rep_2(ml/l)"]) / 2), axis=1
    )

    df = df[pd.notnull(df["WINKLER"])]

    wanted_columns = ["Stickr", "Station-ID", "Sbeox0ML/L", "WINKLER", "WINKLER-DIFF"]

    successful_titrations_df = df.loc[
        (df["WINKLER"] <= 9) & (df["WINKLER"] >= 2) & (df["WINKLER-DIFF"] <= 0.2),
        wanted_columns,
    ]

    failed_titrations_df = df.loc[
        (df["WINKLER"] > 9) | (df["WINKLER"] < 2) | (df["WINKLER-DIFF"] > 0.2),
        wanted_columns, 
    ]

    return successful_titrations_df, failed_titrations_df


def join_bot_o2_met_dfs(
    bot_df: pd.DataFrame,
    o2_df: pd.DataFrame,
    met_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    This function joins three pandas DataFrames: bot_df, o2_df, and met_df then returns a merged DataFrame.

    Parameters:
    bot_df: pandas.DataFrame
        DataFrame containing the data of bot samples.
    o2_df: pandas.DataFrame
        DataFrame containing the O2 data.
    met_df: pandas.DataFrame
        DataFrame containing the data of meteorological samples.

    Returns:
    pandas.DataFrame
        A merged DataFrame of all three input DataFrames, joined on common columns:
        bot_df and met_df are joined on "ShTrpStn" and "Station".
        o2_df and join_dfs are joined on "Stickr" and "Sample".

    Raises:
        None.
    """

    join_dfs = bot_df.merge(met_df, how="inner", left_on="ShTrpStn", right_on="Station")
    join_dfs = join_dfs.merge(o2_df, how="inner", left_on="Stickr", right_on="Sample")
    join_dfs.drop(["Station", "Sample"], axis=1, inplace=True)

    return join_dfs


def filter_graph_data(joined_df: pd.DataFrame) -> pd.DataFrame:

    graph_df = joined_df.filter(items=["Rep_1(ml/l)", "Sbeox0ML/L", "Sbeox1ML/L"])

    return graph_df


def generate_map(df: pd.DataFrame) -> None:
    """
    Generate a GeoDataFrame from a DataFrame containing latitude and longitude columns.
    Writes it as both GeoJSON and Shapefile formats in the "tmp" folder.

    Args:
        df (pandas.DataFrame): A DataFrame containing latitude and longitude columns.

    Raises:
        None.
    """

    joined_gdf = geopandas.GeoDataFrame(
        df,
        geometry=geopandas.points_from_xy(df.longitude, df.latitude),
    )
    joined_gdf.to_file("tmp/joined_gdf.geojson")
    joined_gdf.to_file("tmp/joined_gdf.shp")

    print("Geographical data added to tmp folder")
    # generate png of map for excel


def new_and_old_SOC_calculations(path: str, joined_df: pd.DataFrame):

    if not Path(path).exists():
        raise FileNotFoundError(
            f"Expected {path} to be in the current working directory, but it was not found"
        )

    updated_graph_df = pd.read_csv(path)

    

    #take in csv from graph output
    #get slope and y-int from each Sbeox
    #take value and apply to new calibrated columns
    #calculate new SOC
    #calculate old SOC?? 
    #return full of with new cols
    

    df["New_SOC"] = df.apply(lambda x: abs(x["WINKLER"] / x["Sbeox1ML/L"]), axis=1)


    
    return joined_df

def write_final_excel():
    pass

if __name__ == "__main__":
    year = int(input("Year: "))
    ship_name = input("Ship name: ")
    ship_trip = input("Ship trip: ")
    bot_df = generate_bot_df(f"{ship_name}{ship_trip}.bot")
    o2_df = generate_o2_df(f"{ship_name}{ship_trip}_meanO2.txt")
    met_df = generate_met_df(f"{ship_name}{ship_trip}_{year}_met.csv")


    joined_df = join_bot_o2_met_dfs(bot_df, o2_df, met_df)
    output_file = f"{ship_name}{ship_trip}_{year}_joined.csv"
    joined_df.to_csv(output_file, index=False)
    print(f"Written joined bot, o2 and met DataFrame to {output_file}")


    graph_df = filter_graph_data(joined_df)
    #plotter = Plotter(graph_df)
    #plotter.show()

    #joined_df, failed_titrations = seperate_based_on_winkler_diff(joined_df)
