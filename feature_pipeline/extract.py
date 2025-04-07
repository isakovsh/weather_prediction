import requests 
from typing import Optional 
from utils import get_console_logger
import pandas as pd 
from json import JSONDecodeError
from datetime import datetime 

logger = get_console_logger(name = "Extracting")

def download_historical_data(
        from_day : Optional[str] = "2024-01-01",
        to_day : Optional[str] = "2025-02-12",
        url : Optional[str] = "https://archive-api.open-meteo.com/v1/archive"
):
    """Downloads historical data from the API"""

    params = {
    "latitude": 37.5665,  # Seoul's latitude
    "longitude": 126.9780,  # Seoul's longitude
    "start_date": from_day,
    "end_date": to_day,
    "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "surface_pressure", 
               "cloudcover", "precipitation", "shortwave_radiation", "dew_point_2m"],
    "timezone": "Asia/Seoul"  # Set timezone to Seoul
}

# Make the API request
    logger.info(f"Requesting data from API with URL: {url}")
    try:
        response = requests.get(url,params=params)
        response = response.json()
    except JSONDecodeError:
        logger.error(
            f"Response status = {response.status_code}. Could not decode response from API with URL: {url}"
        )

        return None
    
    data = pd.DataFrame(response['hourly'])
    

    meatadata = {
        "from_day":from_day,
        "to_day": to_day,
        "url": url,
        "extracted_date": datetime.now().isoformat()
    }

    return data , meatadata

def download_current_data(
        url : Optional[str] = "https://api.open-meteo.com/v1/forecast"
):
    "Downloads current data from the API"

    params_forecast = {
    "latitude": 37.5665,
    "longitude": 126.9780,
    "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "surface_pressure", 
               "cloudcover", "precipitation", "shortwave_radiation", "dew_point_2m"],
    "timezone": "Asia/Seoul"
}

    # Fetch current weather data
    logger.info("Extracting current weather")
    try:
        response_forecast = requests.get(url, params=params_forecast)
        forecast_data = response_forecast.json()
    except Exception as e:
        return f"Error {e}"

    # Extract real-time data
    current_weather = pd.DataFrame(forecast_data["current"])

    meta_data = {
        "url":url, 
        "curren_time": datetime.now()
    }

    return current_weather , meta_data