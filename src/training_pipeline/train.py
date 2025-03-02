import os 
import hopsworks 
import wandb
import time 
import numpy as np
from dotenv import load_dotenv 
import fire

from xgboost import XGBRegressor 
from sklearn.metrics import mean_absolute_error , mean_squared_error
from data import load_data_from_feature_store 

from utils import get_logger ,save_model, OUTPUT_DIR 

load_dotenv()

logger = get_logger("Traininig pieline")
def load_best_configs(sweep_id:str):
    """ Loads best config from givem sweep"""
    wandb.login()
    api = wandb.Api()
    sweep = api.sweep(f'isakovsh/Seoul_weather_prediction/{sweep_id}')
    best_run = min(sweep.runs, key=lambda run: run.summary["neg_mean_squared_error"])
    best_config = best_run.config
    run_name = best_run.name

    return best_config
    



def train(configs):
    """Trains model with best config and saves to the model registry"""

    metrics = {}

    logger.info("Start loading data from feature store")
    X_train , X_test , y_train , y_test = load_data_from_feature_store(feature_view_version=1,training_dataset_version=1)
    logger.info("Sucsessfully loaded data")

    logger.info("Initializing model")
    model = XGBRegressor(
        gamma = configs['gamma'],
        max_depth= configs['max_depth'],
        reg_alpha= configs['reg_alpha'],
        subsample= configs['subsample'],
        reg_lambda= configs['reg_lambda'],
        n_estimators= configs['n_estimators'],
        learning_rate= configs['learning_rate'],
        colsample_bytree= configs['colsample_bytree'],
        min_child_weight= configs['min_child_weight']
    )

    logger.info("Start training")
    start_time = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start_time
    logger.info("Completed trainig")

    # Predict and evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test,y_pred)
    rmse = np.sqrt(mse) 

    metrics['MSE'] = mse
    metrics['MAE'] = mae
    metrics['RMSE'] = rmse
    metrics['Train_time'] = mse 

    # save model locally
    model_path = OUTPUT_DIR/"best_model.pkl"
    save_model(model,model_path)
    logger.info("Sucsessfully saved model to ",model_path)

    add_best_model_to_model_registry(model_path,metrics)
    return "Finish"


def add_best_model_to_model_registry(model_path,metrics) -> int:
    """Adds the best model artifact to the model registry."""

    project = hopsworks.login(
        api_key_value=os.getenv("FS_API_KEY"),project=os.getenv("FS_PROJECT_NAME")
    )


    mr = project.get_model_registry()
    py_model = mr.python.create_model("best_model", metrics=metrics)
    py_model.save(model_path)

    return py_model.version

if __name__ == "__main__":
    configs = load_best_configs("28pf7slw")
    fire.Fire(train(configs))
