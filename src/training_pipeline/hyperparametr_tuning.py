import os 
from dotenv import load_dotenv
from functools import partial
from typing import Optional

import fire
import numpy as np
import pandas as pd
import wandb

from xgboost import XGBRegressor

import utils 
from data import load_data_from_feature_store 
from utils import init_wandb_run , OUTPUT_DIR  , get_logger 

load_dotenv()
logger = get_logger("Hyperparametr tuning")


import wandb
from xgboost import XGBRegressor
from sklearn.model_selection import cross_val_score

wandb.login()

sweep_config = {
    'method': 'bayes',  # Bayesian Optimization for efficiency
    'metric': {'name': 'neg_mean_squared_error', 'goal': 'minimize'},
    'parameters': {
        'learning_rate': {'min': 0.01, 'max': 0.2},
        'max_depth': {'values': [3, 6]},  # Reduced range
        'n_estimators': {'values': [50, 100, 150]},  # Reduced max value
        'min_child_weight': {'values': [1, 3]},  # Fewer choices
        'subsample': {'min': 0.7, 'max': 1.0},  # Remove lower range
        'colsample_bytree': {'min': 0.7, 'max': 1.0},  # Same
        'gamma': {'values': [0, 0.1]},  # Remove 0.2 option
        'reg_alpha': {'min': 0.0, 'max': 0.05},  # Lower range
        'reg_lambda': {'min': 0.01, 'max': 0.5}  # Reduced range
    }
}

sweep_id = wandb.sweep(sweep_config, project="Seoul_weather_prediction")


def train():
    wandb.init()
    config = wandb.config
    
    model = XGBRegressor(
        learning_rate=config.learning_rate,
        max_depth=config.max_depth,
        n_estimators=config.n_estimators,
        min_child_weight=config.min_child_weight,
        subsample=config.subsample,
        colsample_bytree=config.colsample_bytree,
        gamma=config.gamma,
        reg_alpha=config.reg_alpha,
        reg_lambda=config.reg_lambda,
    )
    
    X_train , _  , y_train , _ = load_data_from_feature_store(feature_view_version=1,training_dataset_version=1)
    scores = cross_val_score(model, X_train, y_train, cv=3, scoring='neg_mean_squared_error')
    wandb.log({"neg_mean_squared_error": scores.mean()})

# Run the Sweep with Fewer Trials
wandb.agent(sweep_id, function=train, count=10)  



if __name__ == "__main__":
    fire.Fire(train())

    

