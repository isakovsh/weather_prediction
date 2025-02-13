import pandas as pd 
from utils import get_console_logger 

logger = get_console_logger()

def transform_data(df:pd.DataFrame):
    df["time"] = pd.to_datetime(df["time"])
    df["hour"] = df["time"].dt.hour
    df["day"] = df["time"].dt.day
    df["month"] = df["time"].dt.month

    return df 