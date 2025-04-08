import fire
from typing import Optional

from extract import download_current_data , download_historical_data 
from transform import transform_data 
from load import to_feature_store 

from utils import get_console_logger , save_json

logger = get_console_logger("ETL pipeline")

def run(
    feature_group_version : Optional[int] = 1    
):
    
    logger.info("Downloading data from API")
    # data , metadata = download_historical_data()
    data , metadata = download_current_data()
    logger.info("Sucsessfully downloaded data")

    logger.info("Transforming data")
    data = transform_data(data)
    # Debugging 
    print(data.columns)
    if "interval" in data.columns:
        print("Dropping unexpected column 'interval'")
        data = data.drop(columns=["interval"])
    logger.info("Sucsessfully transformed data")

    logger.info("Loading data to  featurestore")
    to_feature_store(data,feature_group_version)
    logger.info("Sucseesfully loaded data")

    metadata['feature_group_version'] = feature_group_version
    save_json(metadata,"feature_pipeline_metadata.json")
    logger.info("Done")

    return metadata


if __name__ == "__main__":
    fire.Fire(run(feature_group_version=2))