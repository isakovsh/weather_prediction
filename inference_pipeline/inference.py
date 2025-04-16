import os
import pytz
import hopsworks
import pandas as pd
from datetime import datetime ,timedelta
from typing import Optional 
from data import get_current_data , get_historical_temperatures , prepare_inference_data 
from model import get_best_model
from dotenv import load_dotenv 
from utils import get_logger 


load_dotenv()
logger = get_logger("Inference Pipeline")
timezone = pytz.timezone("Asia/Seoul")  

now = datetime.now(timezone).replace(minute=0,second=0, microsecond=0)
next_hour = now + pd.Timedelta(hours=1)


def predict(model_version:Optional[int]=2):
    """Generate temperature prediction for the next hour."""
    try:
        logger.info("Loading current weather data from API...")
        current_data , _ = get_current_data()
        logger.info("Loaded current weather data")

        logger.info("Loading historical data from FS...")
        historical_data = get_historical_temperatures()
        logger.info("Loaded historical data")

        logger.info("Strart preapring inference data...")
        inference_data = prepare_inference_data(current_data,historical_data)
        logger.info("Sucsessfully prepared inference data")

        logger.info("Loading model from model registry...")
        model = get_best_model(model_version=model_version)
        logger.info("Loaded model from model registry")

        logger.info("Start predicting")
        prediction = model.predict(inference_data)
        logger.info("Finishid predictions")

        return current_data['temperature_2m'], prediction[0]

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise
    


def save_weather_data(real_temp: Optional[float] = None, 
                      pred_temp: Optional[float] = None,
                      feature_group_version: int = 1) -> None:
    """Save weather data to feature store with timezone handling"""
    try:
        # Timezone setup
        
        
        # Hopsworks connection
        project = hopsworks.login(
            api_key_value=os.getenv("FS_API_KEY"),
            project=os.getenv("FS_PROJECT_NAME")
        )
        fs = project.get_feature_store()
        fg = fs.get_or_create_feature_group(
            name="weather_prediction_data",
            version=feature_group_version,
            primary_key=["time"],
            event_time="time",
            online_enabled=False,
            statistics_config={
                "enabled": True,
                "histograms": True,
                "correlations": True
            }
        )
        
        # Update previous prediction with real temperature
         if real_temp is not None:
            df = fg.read()
            if df.empty:
                logger.warning("Feature group is empty. Skipping last entry update.")
                last_entry = None  # Skip or handle case appropriately
            else:
                last_entry = df.sort_values("time", ascending=False).iloc[[0]]
                
            if last_entry is not None and not last_entry.empty:
                last_entry["real_temperature"] = real_temp
                fg.insert(last_entry, overwrite=True, write_options={"wait_for_job": True})
                logger.info("Updated real temperature for current hour")
                
        # Save new prediction
        if pred_temp is not None:
            new_data = pd.DataFrame([{
                "time": pd.to_datetime(next_hour),
                "real_temperature": -1,
                "predicted_temperature": pred_temp
            }])
            fg.insert(new_data, write_options={"wait_for_job": True})
            logger.info("Saved prediction for next hour")
        
        # Update statistics
        fg.compute_statistics()
        
    except Exception as e:
        logger.error(f"Data saving failed: {str(e)}")
        raise

def run():
    """Orchestrate prediction and saving process."""
    try:

        current_temp , predicted_temp = predict(model_version=2)
        save_weather_data(real_temp = current_temp,pred_temp=predicted_temp)
        logger.info("Pipeline executed successfully")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    run()
    
