# import modules
import pandas as pd

def json_normalize(col, df):
    """
    json_normalize - function to normalize json structures in dataframe
    col - colume names from dataframes
    df - Dataframe
    return flatten nested JSON structures columns into a tabular format
    """
    return pd.json_normalize(df[f'{col}'])