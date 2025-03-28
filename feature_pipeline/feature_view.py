from datetime import datetime 
from typing import Optional 

import os
import fire 
import hopsworks 
import hsfs 

from utils import get_console_logger , load_json , save_json
from dotenv import load_dotenv
 
load_dotenv()

logger = get_console_logger("Feature view")

def create(
        feature_group_version : Optional[int] = None,
        from_day : Optional[int] = None , 
        to_day : Optional[int] = None
)->dict:
    """ Create a new feature view version and training dataset
    based on the given feature group version and start and end datetimes. """

    if feature_group_version is None:
        feature_pipeline_metadata = load_json("feature_pipeline_metadata.json")
        feature_group_version = feature_pipeline_metadata['feature_group_version']

        from_day = feature_pipeline_metadata['from_day']
        to_day = feature_pipeline_metadata['to_day']

    project = hopsworks.login(
        api_key_value=os.getenv("FS_API_KEY"), project=os.getenv("FS_PROJECT_NAME")
    )

    fs = project.get_feature_store()

    try:
        feature_views = fs.get_feature_views(name="weather_data")
    except hsfs.client.exceptions.RestAPIError:
        logger.info("No feature views found for weather_data.")

        feature_views = []

    for feature_view in feature_views:
        try:
            feature_view.delete_all_training_datasets()
        except hsfs.client.exceptions.RestAPIError:
            logger.error(
                f"Failed to delete training datasets for feature view {feature_view.name} with version {feature_view.version}."
            )

        try:
            feature_view.delete()
        except hsfs.client.exceptions.RestAPIError:
            logger.error(
                f"Failed to delete feature view {feature_view.name} with version {feature_view.version}."
            )

    # Create feature view in the given feature group version.
    energy_consumption_fg = fs.get_feature_group(
        "weather_data", version=feature_group_version
    )
    ds_query = energy_consumption_fg.select_all()
    feature_view = fs.create_feature_view(
        name="weather_data",
        description="Seoul weather data  for  forecasting model.",
        query=ds_query,
        labels=[],
    )

    logger.info(f"Creating train data set from {from_day} till {to_day}")

    start_time = datetime.strptime(from_day, "%Y-%m-%d")
    end_time = datetime.strptime(to_day, "%Y-%m-%d")

    feature_view.create_training_data(
        description="Weather prediction training dataset",
        data_format="csv",
        start_time=start_time,
        end_time=end_time,
        write_options={"wait_for_job": True},
        coalesce=False,
    )

    metadata = {
        "feature_view_version": feature_view.version,
        "training_dataset_version": 1,
    }

    save_json(
        metadata,
        file_name="feature_view_metadata.json",
    )

    return metadata


if __name__ == "__main__":
    fire.Fire(create())


    