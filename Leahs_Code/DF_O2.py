from pathlib import Path
from io import StringIO

import pandas
import geopandas


def generate_bot_df(path: str) -> pandas.DataFrame:
    """
    This function generates a Pandas DataFrame from a CSV file located at the specified path.
    Raises a FileNotFoundError if the file is not located in the working directory.
    The generated DataFrame contains only a subset of columns.
    The resulting DataFrame is indexed by the "Stickr" column.

    Args:
        path (str): The file path to the CSV file containing the source data.

    Returns:
        pandas.DataFrame: The generated DataFrame containing the specified columns and indexed by "Stickr".
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
    bot_df = bot_df.set_index("Stickr")

    return bot_df


def generate_o2_df(path: str) -> pandas.DataFrame:
    """
    This function generates a Pandas DataFrame from a text file located at the specified path.
    Raises a FileNotFoundError if the file is not located in the working directory.
    The header of the file is discarded, reads the rest of the file as CSV
    The generated DataFrame contains only a subset of columns.
    The resulting DataFrame is indexed by the "Sample" column.

    Args:
        path (str): The file path to the text file containing the source data.

    Returns:
        pandas.DataFrame: The generated DataFrame containing the specified columns and indexed by "Sample".
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
    o2_df = o2_df.set_index("Sample")

    return o2_df


def filter_out_non_null_winkler_diff(df):
    # TODO WINKLER & other cols do not seem to exist, missing code??

    # df["WINKLER-DIFF"] = abs(df["Rep_1(ml/l)"].astype(float)-df["Rep_2(ml/l)"].astype(float))
    # df = df[pandas.notnull(df["WINKLER"])]
    # filtered_df = df.loc[(df["WINKLER"] > 9) | (df["WINKLER"] < 2) | (df["WINKLER-DIFF"] > 0.2),["Sample","Station-ID","Sbeox0ML/L","WINKLER","WINKLER-DIFF"]]
    # print(filtered_df)
    return df


def join_bot_and_o2_dfs(
    bot_df: pandas.DataFrame, o2_df: pandas.DataFrame
) -> pandas.DataFrame:
    # return bot_df.join(o2_df)
    return bot_df.merge(o2_df, how="inner", left_index=True, right_index=True)


if __name__ == "__main__":
    ship_num = int(input("Ship number: "))
    ship_name = input("Ship name: ")
    ship_trip = int(input("Ship trip: "))
    bot_df = generate_bot_df(f"{ship_num}{ship_trip}.bot")
    o2_df = generate_o2_df(f"{ship_name}{ship_trip}_meanO2.txt")
    #in case of inconsistent file names, input full file names instead??

    joined_df = join_bot_and_o2_dfs(bot_df, o2_df)
    output_file = f"{ship_name}{ship_trip}_joined_bot_and_o2.csv"
    # joined_df.to_csv(output_file)
    # print(f"Written joined bot and o2 DataFrame to {output_file}")

    # possible map code
    joined_gdf = geopandas.GeoDataFrame(
        joined_df,
        geometry=geopandas.points_from_xy(joined_df.longitude, joined_df.latitude),
    )

    joined_gdf.to_file("tmp/joined_gdf.shp")