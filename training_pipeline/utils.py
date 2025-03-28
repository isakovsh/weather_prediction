import os 
import logging
import json
import joblib
import pandas as pd
import wandb

from pathlib import Path
from typing import Union, Optional
from dotenv import load_dotenv

load_dotenv()





def save_json(data: dict, file_name: str):
    """
    Save a dictionary as a JSON file.

    Args:
        data: data to save.
        file_name: Name of the JSON file.
        save_dir: Directory to save the JSON file.

    Returns: None
    """

    data_path = Path(file_name)
    with open(data_path, "w") as f:
        json.dump(data, f)


def load_json(file_name: str) -> dict:
    """
    Load a JSON file.

    Args:
        file_name: Name of the JSON file.
        save_dir: Directory of the JSON file.

    Returns: Dictionary with the data.
    """

    data_path = Path(file_name)
    with open(data_path, "r") as f:
        return json.load(f)


def save_model(model, model_path: Union[str, Path]):
    """
    Template for saving a model.

    Args:
        model: Trained model.
        model_path: Path to save the model.
    """

    joblib.dump(model, model_path)


def load_model(model_path: Union[str, Path]):
    """
    Template for loading a model.

    Args:
        model_path: Path to the model.

    Returns: Loaded model.
    """

    return joblib.load(model_path)


def load_data_from_parquet(data_path: str) -> pd.DataFrame:
    """
    Template for loading data from a parquet file.

    Args:
        data_path: Path to the parquet file.

    Returns: Dataframe with the data.
    """

    return pd.read_parquet(data_path)


def get_logger(name: str) -> logging.Logger:
    """
    Template for getting a logger.

    Args:
        name: Name of the logger.

    Returns: Logger.
    """

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)

    return logger


def get_root_dir(default_value: str = ".") -> Path:
    """
    Get the root directory of the project.

    Args:
        default_value: Default value to use if the environment variable is not set.

    Returns:
        Path to the root directory of the project.
    """

    return Path(os.getenv("ML_PIPELINE_ROOT_DIR", default_value))


ML_PIPELINE_ROOT_DIR = get_root_dir()
OUTPUT_DIR = ML_PIPELINE_ROOT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)