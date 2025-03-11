import os
import hopsworks
import joblib

from dotenv import load_dotenv 

load_dotenv()


def get_best_model(model_version):
    """Gets the best model from the model registry"""

    project = hopsworks.login(
        api_key_value=os.getenv("FS_API_KEY"),project=os.getenv("FS_PROJECT_NAME")
    )
    
    mr = project.get_model_registry()
    model = mr.get_model("best_model", version=model_version)
    model_dir = model.download()
    model_path = os.path.join(model_dir, f"best_model.pkl")
    trained_model = joblib.load(model_path)
    return trained_model
