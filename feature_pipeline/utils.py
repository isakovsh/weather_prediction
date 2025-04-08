import logging
import json
from typing import Optional
from pathlib import Path

def get_console_logger(name: Optional[str] = 'weather_predection') -> logging.Logger:
    
    # Create logger if it doesn't exist
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create console handler with formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add console handler to the logger
        logger.addHandler(console_handler)

    return logger


def save_json(data: dict, file_name: str):
    """
    Save a dictionary as a JSON file.

    Args:
        data: data to save.
        file_name: Name of the JSON file.

    Returns: None
    """

    data_path =  Path(file_name)
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

    data_path =  Path(file_name)
    if not data_path.exists():
        raise FileNotFoundError(f"Cached JSON from {data_path} does not exist.")

    with open(data_path, "r") as f:
        return json.load(f)