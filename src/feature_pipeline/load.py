import hopsworks
import pandas as pd 
import os 
from dotenv import load_dotenv 

load_dotenv()

def to_feature_store(
        data : pd.DataFrame,
        feature_group_version
):
    project = hopsworks.login(
        api_key_value=os.getenv("FS_API_KEY"), project=os.getenv("FS_PROJECT_NAME")
    )

    feature_store = project.get_feature_store()

    weather_feature_group = feature_store.get_or_create_feature_group(
        name="weather_data",
        version=feature_group_version,
        description="Seoul hourly weather  data.",
        primary_key=["time"],
        # event_time="datetime_utc",
        online_enabled=False,
    )

    weather_feature_group.insert(
        features=data,
        overwrite=False,
        write_options={
            "wait_for_job": True,
        },
    )

    # Update statistics.
    weather_feature_group.statistics_config = {
        "enabled": True,
        "histograms": True,
        "correlations": True,
    }
    weather_feature_group.update_statistics_config()
    weather_feature_group.compute_statistics()

    return weather_feature_group


    
    