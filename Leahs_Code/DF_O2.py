from pathlib import Path
from io import StringIO

import pandas
import geopandas


def generate_bot_df(path: str) -> pandas.DataFrame:
    """
    This function generates a Pandas DataFrame from a CSV file located at the specified path.
    The generated DataFrame contains only a subset of columns.

    Args:
        path (str): The file path to the CSV file containing the source data.

    Returns:
        pandas.DataFrame: The generated DataFrame containing the specified columns.

    Raises:
        FileNotFoundError: If the file at the specified path does not exist.
    """
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Expected {path} to be in the current working directory, but it was not found"
        )

    bot_df = pandas.read_csv(path)
    bot_df = bot_df.filter(
        items=[
            "Stickr",
            "ShTrpStn",
            "latitude",
            "longitude",
            "PrDM",
            "Sbeox0ML/L",
            "Sbeox1ML/L",
        ]
    )

    return bot_df


def generate_o2_df(path: str) -> pandas.DataFrame:
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
    o2_df = pandas.read_csv(StringIO(o2_csv))
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

    return o2_df


def generate_met_df(path: str) -> pandas.DataFrame:
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

    met_df = pandas.read_csv(path)
    met_df = met_df.filter(items=["Station", "Wind Dir [deg/10]", "Wind Speed [kts]"])

    met_df["Wind Speed [kts]"] = met_df["Wind Speed [kts]"].apply(
        lambda x: round(x / 1.944, 4)  # decimal place tbd
    )
    met_df = met_df.rename(columns={"Wind Speed [kts]": "Wind Speed [m/s]"})

    return met_df


def filter_out_non_null_winkler_diff(df):
    # TODO WINKLER & other cols do not seem to exist, missing code??

    # df["WINKLER-DIFF"] = abs(df["Rep_1(ml/l)"].astype(float)-df["Rep_2(ml/l)"].astype(float))
    # df = df[pandas.notnull(df["WINKLER"])]
    # filtered_df = df.loc[(df["WINKLER"] > 9) | (df["WINKLER"] < 2) | (df["WINKLER-DIFF"] > 0.2),["Sample","Station-ID","Sbeox0ML/L","WINKLER","WINKLER-DIFF"]]
    # print(filtered_df)
    return df


def join_bot_o2_met_dfs(
    bot_df: pandas.DataFrame,
    o2_df: pandas.DataFrame,
    met_df: pandas.DataFrame,
) -> pandas.DataFrame:
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


def generate_oxy_graph():
    #line graph will live here
    return 1


def generate_map(df):
    """
    Generate a GeoDataFrame from a DataFrame containing latitude and longitude columns.
    Writes it as both GeoJSON and Shapefile formats in the "tmp" folder.

    Args:
        df (pandas.DataFrame): A DataFrame containing latitude and longitude columns.

    Returns:
        str: A message indicating that the geographical data has been added to the "tmp" folder.

    Raises:
        None.
    """

    joined_gdf = geopandas.GeoDataFrame(
        df,
        geometry=geopandas.points_from_xy(df.longitude, df.latitude),
    )
    joined_gdf.to_file("tmp/joined_gdf.geojson")
    joined_gdf.to_file("tmp/joined_gdf.shp")

    return f"Geographical data added to tmp folder"


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

    print(generate_map(joined_df))  # temp? checking purposes
