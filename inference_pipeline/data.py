import os
import requests
import hopsworks
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple
from utils import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logger = get_logger("Inference Data")


def get_current_data(url: str = "https://api.open-meteo.com/v1/forecast") -> Tuple[pd.DataFrame, dict]:
    """Fetches current weather data from the API."""
    params = {
        "latitude": 37.5665,
        "longitude": 126.9780,
        "current": [
            "temperature_2m", "relative_humidity_2m", "wind_speed_10m",
            "surface_pressure", "cloudcover", "precipitation",
            "shortwave_radiation", "dew_point_2m"
        ],
        "timezone": "Asia/Seoul"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json().get("current", {})
        return pd.DataFrame([weather_data]), {"url": url, "current_time": datetime.now()}
    except requests.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")
        return pd.DataFrame(), {}


def get_feature_store():
    """Connects to the Hopsworks Feature Store."""
    api_key = os.getenv("FS_API_KEY")
    project_name = os.getenv("FS_PROJECT_NAME")
    
    if not api_key or not project_name:
        logger.error("Missing FS_API_KEY or FS_PROJECT_NAME in environment variables.")
        return None
    
    try:
        project = hopsworks.login(api_key_value=api_key, project=project_name)
        return project.get_feature_store()
    except Exception as e:
        logger.error(f"Error connecting to Hopsworks Feature Store: {e}")
        return None


def get_historical_temperatures(feature_view_version: int = 1, num_records: int = 3) -> list:
    """Fetches the last `num_records` temperature readings from the Feature Store."""
    fs = get_feature_store()
    if fs is None:
        return []
    
    try:
        fv = fs.get_feature_view(name="weather_data", version=feature_view_version)
        df = fv.query.read().sort_values("time", ascending=False).head(num_records)
        return df["temperature_2m"].tolist()
    except Exception as e:
        logger.error(f"Error retrieving historical data: {e}")
        return []


def prepare_inference_data(current_data: pd.DataFrame, historical_data: list) -> pd.DataFrame:
    """Merges current and historical data for inference."""
    if current_data.empty:
        logger.warning("Current data is empty. Cannot prepare inference data.")
        return current_data
    
    current_data['time'] = pd.to_datetime(current_data['time'])
    current_data['hour'] = current_data['time'].dt.hour
    current_data['day'] = current_data['time'].dt.day
    current_data['month'] = current_data['time'].dt.month

    for i, temp in enumerate(historical_data, start=1):
        current_data[f"temperature_2m_lag_{i}"] = temp

    current_data.drop(labels=['time','interval'],axis=1,inplace=True)
    
    return current_data


if __name__ == "__main__":
    current_data, _ = get_current_data()
    historical_data = get_historical_temperatures(feature_view_version=1)
    final_data = prepare_inference_data(current_data, historical_data)
    # print(final_data)
    print(final_data.info())
