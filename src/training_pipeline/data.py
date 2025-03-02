import os 
import hopsworks
import pandas as pd 
from dotenv import load_dotenv 

load_dotenv()

def load_data_from_feature_store(
        feature_view_version : int , training_dataset_version : int 
):
    """
    Loads time series data from a feature store, processes it by adding lag features and
    rolling windows, and splits it into training and testing datasets.
    
    Arguments:
        feature_view_version (int): The version number of the feature view that holds the data in the feature store.
        training_dataset_version (int): The version number of the training dataset in the feature store.
    Returns:
        X_train (pandas.DataFrame): Features for training, excluding the target variable and time column.
        X_test (pandas.DataFrame): Features for testing, excluding the target variable and time column.
        y_train (pandas.Series): Target variable (temperature_2m) for training.
        y_test (pandas.Series): Target variable (temperature_2m) for testing.
    """
    project = hopsworks.login(
        api_key_value=os.getenv("FS_API_KEY"),project=os.getenv("FS_PROJECT_NAME")
    )

    fs = project.get_feature_store()

  
    feature_view = fs.get_feature_view(
            name="weather_data", version=feature_view_version
        )

    df , _ = feature_view.get_training_data(
            training_dataset_version = training_dataset_version
        )
    
    df['time'] = pd.to_datetime(df['time'])

    df = df.sort_values(by='time')
    df = create_lagged_features(df,'temperature_2m')

    cutoff_date = df['time'].iloc[int(len(df) * 0.8)]  # 80% cutoff date

    # Split the data based on the cutoff date
    train_data = df[df['time'] <= cutoff_date]
    test_data = df[df['time'] > cutoff_date]

    X_train = train_data.drop(labels=['time','temperature_2m'],axis = 1)
    y_train = train_data['temperature_2m']

    X_test = test_data.drop(labels=['time','temperature_2m'],axis = 1)
    y_test = test_data['temperature_2m']

    return X_train , X_test , y_train , y_test 

def create_lagged_features(df, target, lags=[1, 2, 3], rolling_windows=[3, 6]):
    """Adds lag features and rolling window averages to the dataframe."""
    data = df.copy()

    for lag in lags:
        data[f"{target}_lag_{lag}"] = data[target].shift(lag)

    data.fillna(method='ffill',inplace = True)
    return data

       