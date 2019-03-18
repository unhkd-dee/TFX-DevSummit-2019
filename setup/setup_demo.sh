#!/bin/bash
# Set up the environment for the TFX workshop


GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)

printf "${GREEN}Installing TFX workshop${NORMAL}\n\n"

# TF/TFX prereqs
printf "${GREEN}Installing TensorFlow${NORMAL}\n"
pip install tensorflow==1.13.1

printf "${GREEN}Installing TFX${NORMAL}\n"
pip install tfx==0.12.0

printf "${GREEN}Installing Google API Client${NORMAL}\n"
pip install google-api-python-client

printf "${GREEN}Installing required Jupyter version${NORMAL}\n"
pip install --upgrade notebook==5.7.2
jupyter nbextension install --py --symlink --sys-prefix tensorflow_model_analysis
jupyter nbextension enable --py --sys-prefix tensorflow_model_analysis

# Docker images
printf "${GREEN}Installing docker${NORMAL}\n"
pip install docker
docker build -t ..

# Airflow
# Set this to avoid the GPL version; no functionality difference either way
printf "${GREEN}Preparing environment for Airflow${NORMAL}\n"
export SLUGIFY_USES_TEXT_UNIDECODE=yes
printf "${GREEN}Installing Airflow${NORMAL}\n"
pip install apache-airflow
printf "${GREEN}Initializing Airflow database${NORMAL}\n"
airflow initdb

# Adjust configuration
printf "${GREEN}Adjusting Airflow config${NORMAL}\n"
sed -i'.orig' 's/dag_dir_list_interval = 300/dag_dir_list_interval = 1/g' ~/airflow/airflow.cfg
sed -i'.orig' 's/job_heartbeat_sec = 5/job_heartbeat_sec = 1/g' ~/airflow/airflow.cfg
sed -i'.orig' 's/scheduler_heartbeat_sec = 5/scheduler_heartbeat_sec = 1/g' ~/airflow/airflow.cfg
sed -i'.orig' 's/dag_default_view = tree/dag_default_view = graph/g' ~/airflow/airflow.cfg
sed -i'.orig' 's/load_examples = True/load_examples = False/g' ~/airflow/airflow.cfg

printf "${GREEN}Refreshing Airflow to pick up new config${NORMAL}\n"
airflow resetdb --yes
airflow initdb

# Copy Dag to ~/airflow/dags
mkdir -p ~/airflow/dags
cp dags/taxi_pipeline.py ~/airflow/dags/
cp dags/taxi_utils.py ~/airflow/dags/
cp dags/taxi_pipeline_solution.py ~/airflow/dags/
cp dags/taxi_utils_solution.py ~/airflow/dags/

# Copy data to ~/airflow/data
cp -R data ~/airflow

printf "\n${GREEN}TFX workshop installed${NORMAL}\n"
