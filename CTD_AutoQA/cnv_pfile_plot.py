import os
from Toolkits import cnv_tk
from Toolkits import p_tk
from Toolkits import dir_tk
import plotly.graph_objects as go

"""
cnv_pfile_plot
--------------

Plots cnv df along side pfile df
"""
def CompareFiles(cnv, cnv_df, p, p_df):
    """
    :param cnv: Cast Object from the cnv_tk (Already populated)
    :param cnv_df: CNV Dataframe from the cnv_tk
    :param p: Cast Object from the p_tk (Already populated)
    :param p_df: Pfile Dataframe from the p_tk
    :return:
    """
    # TODO: consider adding these lines at the end of the meta function for each toolkit
    if cnv.castType == "":
        cnv_tk.getCastType(cnv)
    if p.castType == "":
        p_tk.getCastType(p)

    if not cnv.Latitude.__str__() == p.Latitude.__str__():
        print("WARNING: LATITUDES NOT MATCHED")

    if not cnv.Longitude.__str__() == p.Longitude.__str__():
        print("WARNING: LONGITUDES NOT MATCHED")

    print("CNV Date: " + cnv.CastDatetime.__str__())
    print("PFile Date: " + p.CastDatetime.__str__())

    # TODO: Check if tow

    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(x=cnv_df["Temperature"], y=cnv_df["Pressure"],
                             mode='lines+markers',
                             name='CNV File'))
    fig.add_trace(go.Scatter(x=p_df["Temperature"], y=p_df["Pressure"],
                             mode='lines+markers',
                             name='P File'))
    fig.show()

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    # TODO: Swap reading methods to system args
    print("Select CNV File")
    cnvfile = dir_tk.selectSingleFile()
    print("Select P File")
    pfile = dir_tk.selectSingleFile()

    pfile = pfile.name
    cnvfile = cnvfile.name

    if cnvfile.lower().endswith(".cnv") and pfile.lower().__contains__(".p"):

        CNV_cast = cnv_tk.Cast(cnvfile)
        cnv_tk.cnv_meta(CNV_cast, cnvfile)
        cnv_df = cnv_tk.cnv_to_dataframe(CNV_cast)
        cnv_df = cnv_tk.StandardizedDF(CNV_cast, cnv_df)

        P_cast = p_tk.Cast(pfile)
        datafile = pfile
        p_tk.read_pFile(P_cast, pfile)
        p_tk.getChannelInfo(P_cast, datafile)
        p_df = p_tk.pfile_to_dataframe(P_cast, pfile)
        P_cast.DataLimit = len(p_df.index)
        p_tk.pfile_meta(P_cast, datafile)
        p_df = cnv_tk.StandardizedDF(P_cast, p_df)

        CompareFiles(CNV_cast, cnv_df, P_cast, p_df)
