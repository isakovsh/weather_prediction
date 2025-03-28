import os 
import hopsworks
from dotenv import load_dotenv 

load_dotenv()

# project = hopsworks.login(
#         api_key_file=os.getenv("FS_API_KEY"),project=os.getenv("FS_PROJECT_NAME")
#     )

# fs = project.get_feature_store()

        
# feature_view = fs.get_feature_view(
#             name="weather_data", version=1
#         )

# data , _ = feature_view.get_training_data(
#             training_dataset_version = 1
#         )

# print(data)

import os
import hopsworks
from dotenv import load_dotenv

load_dotenv(".env")

api_key_path = os.getenv("FS_API_KEY")
project_name = os.getenv("FS_PROJECT_NAME")

print(f"FS_API_KEY: {api_key_path}")
print(f"FS_PROJECT_NAME: {project_name}")



project = hopsworks.login(api_key_value=api_key_path, project=project_name)
