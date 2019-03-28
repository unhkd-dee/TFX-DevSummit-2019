# TFX Developer Tutorial

[![Python](https://img.shields.io/pypi/pyversions/tfx.svg?style=plastic)](
https://github.com/tensorflow/tfx)
[![PyPI](https://badge.fury.io/py/tfx.svg)](https://badge.fury.io/py/tfx)

## Introduction

This tutorial is designed to introduce TensorFlow Extended (TFX)
and help you learn to create your own machine learning
pipelines.  It runs locally, and shows integration with TFX and TensorBoard
as well as interaction with TFX in Jupyter notebooks.

Key Term: A TFX pipeline is a Directed Acyclic Graph, or "DAG".  We will often
refer to pipelines as DAGs.

You'll follow a typical ML development process,
starting by examining the dataset, and end up with a complete
working pipeline.  Along the way you'll explore ways to debug
and update your pipeline, and measure performance.

### Learn more

Please see the [TFX User Guide](https://www.tensorflow.org/tfx/guide) to learn
more.

## Step by step

You'll gradually create your pipeline by working step by step,
following a typical ML development process.  Here are the steps:

1. [Setup your environment](#step_1:_setup_your_environment)
1. [Bring up initial pipeline skeleton](
#step_2:_bring_up_initial_pipeline_skeleton)
1. [Dive into your data](#step_3:_dive_into_your_data)
1. [Feature engineering](#step_4:_feature_engineering)
1. [Training](#step_5:_training)
1. [Analyzing model performance](#step_6:_analyzing_model_performance)
1. [Ready for production](#step_7:_ready_for_production)

## Prerequisites

* Linux or MacOS
* Virtualenv
* Python 2.7
* Git

## Tutorial Materials

The code for this tutorial is available at:
[https://github.com/tensorflow/tfx/tree/master/examples/](
https://github.com/tensorflow/tfx/tree/master/examples/)

The code is organized by the steps that you're working on, so
for each step you'll have the code you need and instructions
on what to do with it.

The tutorial files include both an exercise and the solution to
the exercise, in case you get stuck.

#### Exercise

* taxi_pipeline.py
* taxi_utils.py
* taxi DAG

#### Solution

* taxi_pipeline_solution.py
* taxi_utils_solution.py
* taxi_solution DAG

## What you're doing

You’re learning how to create an ML pipeline using TFX

* TFX pipelines are appropriate when datasets are large
* TFX pipelines are appropriate when training/serving consistency is important
* TFX pipelines are appropriate when version management for inference is
important
* Google uses TFX pipelines for production ML

You’re following a typical ML development process

* Understanding our data
* Feature engineering
* Training
* Analyze model performance
* Lather, rinse, repeat
* Ready for production

### Adding the code for each step

The tutorial is designed so that all the code is included in the files, but all
the code for steps 3-7 is commented out and marked with inline comments. The
inline comments identify which step the line of code applies to. For example,
the code for step 3 is marked with the comment `# Step 3`.

The code that you will add for each step typically falls into 3 regions of the
code:

* imports
* The DAG configuration
* The list returned from the create_pipeline() call
* The supporting code in taxi_utils.py

As you go through the tutorial you'll uncomment the lines of code that apply to
the tutorial step that you're currently working on.  That will add the code for
that step, and update your pipeline.  As you do that **we strongly encourage
you to review the code that you're uncommenting**.

## Chicago Taxi Dataset

![Taxi](images/workshop/taxi.png)

![Chicago taxi](images/workshop/chicago.png)

You're using the [Taxi Trips dataset](
https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew)
released by the City of Chicago.

Note: This site provides applications using data that has been modified
for use from its original source, www.cityofchicago.org, the official website of
the City of Chicago. The City of Chicago makes no claims as to the content,
accuracy, timeliness, or completeness of any of the data provided at this site.
The data provided at this site is subject to change at any time. It is
understood that the data provided at this site is being used at one’s own risk.

You can [read more](https://cloud.google.com/bigquery/public-data/chicago-taxi)
about
the dataset in [Google BigQuery](https://cloud.google.com/bigquery/). Explore
the full dataset in the
[BigQuery UI](
https://bigquery.cloud.google.com/dataset/bigquery-public-data:chicago_taxi_trips).

### Goal - Binary classification

Will the customer tip more or less than 20%?

## Step 1: Setup your environment

The setup script (`setup_demo.sh`) installs TFX and
[Airflow](https://airflow.apache.org/), and configures
Airflow in a way that makes it easy to work with for this tutorial.

In a shell:

```bash
virtualenv -p python2.7 tfx-env
source tfx-env/bin/activate
mkdir tfx; cd tfx

pip install tensorflow==1.13.1
pip install tfx==0.12.0
git clone https://github.com/tensorflow/tfx.git
cd tfx/examples/workshop/setup
./setup_demo.sh
```

You should review `setup_demo.sh` to see what it's doing.

## Step 2: Bring up initial pipeline skeleton

### Hello World

In a shell:

```bash
# Open a new terminal window, and in that window ...
source tfx-env/bin/activate
airflow webserver -p 8080

# Open another new terminal window, and in that window ...
source tfx-env/bin/activate
airflow scheduler
```

### In a browser:

* Open a browser and go to http://127.0.0.1:8080

#### DAG view buttons

![DAG buttons](images/workshop/airflow_dag_buttons.png)

* Use the button on the left to _enable_ the taxi DAG
* Use the button on the right to _trigger_ the taxi DAG
* Click on taxi

![Graph refresh button](images/workshop/graph_refresh_button.png)

* Wait for the CsvExampleGen component to turn dark green (~1 minutes)
* Use the _graph refresh_ button on the right or refresh the page
* Wait for pipeline to complete
  * All dark green
  * Use refresh button on right side or refresh page

![Setup complete](images/workshop/step2.png)

## Step 3: Dive into our data

The first task in any data science or ML project is to understand
and clean the data.

* Understand the data types for each feature
* Look for anomalies and missing values
* Understand the distributions for each feature

### Components

![Data Components](images/workshop/examplegen1.png)
![Data Components](images/workshop/examplegen2.png)

* [ExampleGen](https://www.tensorflow.org/tfx/guide/examplegen)
ingests and splits the input dataset.
* [StatisticsGen](https://www.tensorflow.org/tfx/guide/statsgen)
calculates statistics for the dataset.
* [SchemaGen](https://www.tensorflow.org/tfx/guide/schemagen)
SchemaGen examines the statistics and creates a data schema.
* [ExampleValidator](https://www.tensorflow.org/tfx/guide/exampleval)
looks for anomalies and missing values in the dataset.

### In an editor:

* Uncomment the lines marked `Step 3` in both `taxi_pipeline.py` and
`taxi_utils.py`
* Take a moment to review the code that you uncommented

### In a browser:

* Return to DAGs list page in Airflow
* Click the refresh button on the right side for the taxi DAG
  * You should see "DAG [taxi] is now fresh as a daisy"
* Trigger taxi
* Wait for pipeline to complete
  * All dark green
  * Use refresh on right side or refresh page

![Dive into data](images/workshop/step3.png)

### Back on Jupyter:

* Open step3.ipynb
* Follow the notebook

![Dive into data](images/workshop/step3notebook.png)

### More advanced example

The example presented here is really only meant to get you started. For a more
advanced example see the [TensorFlow Data Validation Colab](
https://www.tensorflow.org/tfx/tutorials/data_validation/chicago_taxi)

For more information on using TFDV to explore and validate a
dataset, [see the examples on tensorflow.org](
https://www.tensorflow.org/tfx/data_validation)

## Step 4: Feature engineering

You can increase the predictive quality of our data and/or reduce
dimensionality with feature engineering.

* Feature crosses
* Vocabularies
* Embeddings
* PCA
* Categorical encoding

One of the benefits of using TFX is that you will write your transformation
code once, and the resulting transforms will be consistent between training
and serving.

### Components

![Transform](images/workshop/transform.png)

* [Transform](https://www.tensorflow.org/tfx/guide/transform)
performs feature engineering on the dataset.

### In an editor:

* Uncomment the lines marked `Step 4` in both `taxi_pipeline.py` and
`taxi_utils.py`
* Take a moment to review the code that you uncommented

### In a browser:

* Return to DAGs list page in Airflow
* Click the refresh button on the right side for the taxi DAG
  * You should see "DAG [taxi] is now fresh as a daisy"
* Trigger taxi
* Wait for pipeline to complete
  * All dark green
  * Use refresh on right side or refresh page

![Feature Engineering](images/workshop/step4.png)

### Back on Jupyter:

* Open step4.ipynb
* Follow the notebook

### More advanced example

The example presented here is really only meant to get you started. For a more
advanced example see the [TensorFlow Transform Colab](
https://www.tensorflow.org/tfx/tutorials/transform/census).

## Step 5: Training

Train a TensorFlow model with our nice, clean, transformed data.

* Include the transformations from step 4 so that they are applied consistently
* Save the results as a SavedModel for production
* Visualize and explore the training process using TensorBoard
* Also save an EvalSavedModel for analysis of model performance

### Components

* [Trainer](https://www.tensorflow.org/tfx/guide/trainer)
trains the model using TensorFlow
[Estimators](https://www.tensorflow.org/guide/estimators)

### In an editor:

* Uncomment the lines marked `Step 5` in both `taxi_pipeline.py` and
`taxi_utils.py`
* Take a moment to review the code that you uncommented

### In a browser:

* Return to DAGs list page in Airflow
* Click the refresh button on the right side for the taxi DAG
  * You should see "DAG [taxi] is now fresh as a daisy"
* Trigger taxi
* Wait for pipeline to complete
  * All dark green
  * Use refresh on right side or refresh page

![Training a Model](images/workshop/step5.png)

### Back on Jupyter:

* Open step5.ipynb
* Follow the notebook

![Training a Model](images/workshop/step5tboard.png)

### More advanced example

The example presented here is really only meant to get you started. For a more
advanced example see the [TensorBoard Tutorial](
https://www.tensorflow.org/tensorboard/r1/summaries).

## Step 6: Analyzing model performance

Understanding more than just the top level metrics.

* Users experience model performance for their queries only
* Poor performance on slices of data can be hidden by top level metrics
* Model fairness is important
* Often key subsets of users or data are very important, and may be small
    * Performance in critical but unusual conditions
    * Performance for key audiences such as influencers

### Components

* [Evaluator](https://www.tensorflow.org/tfx/guide/evaluator)
performs deep analysis of the training results.

### In an editor:

* Uncomment the lines marked `Step 6` in both `taxi_pipeline.py` and
`taxi_utils.py`
* Take a moment to review the code that you uncommented

### In a browser:

* Return to DAGs list page in Airflow
* Click the refresh button on the right side for the taxi DAG
  * You should see "DAG [taxi] is now fresh as a daisy"
* Trigger taxi
* Wait for pipeline to complete
  * All dark green
  * Use refresh on right side or refresh page

![Analyzing model performance](images/workshop/step6.png)

### Back on Jupyter:

* Open step6.ipynb
* Follow the notebook

![Analyzing model performance](images/workshop/step6notebook.png)

### More advanced example

The example presented here is really only meant to get you started.
For more information on using TFMA to analyze model
performance, [see the examples on tensorflow.org](
https://www.tensorflow.org/tfx/model_analysis).

## Step 7: Ready for production

If the new model is ready, make it so.

* If we’re replacing a model that is currently in production, first make sure
that the new one is better
* ModelValidator tells Pusher if the model is OK
* Pusher deploys SavedModels to well-known locations

Deployment targets receive new models from well-known locations

* TensorFlow Serving
* TensorFlow Lite
* TensorFlow JS
* TensorFlow Hub

### Components

* [ModelValidator](https://www.tensorflow.org/tfx/guide/modelval)
ensures that the model is "good enough" to be pushed to production.
* [Pusher](https://www.tensorflow.org/tfx/guide/pusher)
deploys the model to a serving infrastructure.

### In an editor:

* Uncomment the lines marked `Step 7` in both `taxi_pipeline.py` and
`taxi_utils.py`
* Take a moment to review the code that you uncommented

### In a browser:

* Return to DAGs list page in Airflow
* Click the refresh button on the right side for the taxi DAG
  * You should see "DAG [taxi] is now fresh as a daisy"
* Trigger taxi
* Wait for pipeline to complete
  * All dark green
  * Use refresh on right side or refresh page

![Ready for production](images/workshop/step7.png)

## Next Steps

You have now trained and validated your model, and exported a `SavedModel` file
under the `~/airflow/saved_models/taxi` directory.  Your model is now
ready for production.  You can now deploy your model to any of the TensorFlow
deployment targets, including:

* [TensorFlow Serving](https://www.tensorflow.org/tfx/guide/serving), for
serving your model on a server or server farm and processing REST and/or gRPC
inference requests.
* [TensorFlow Lite](https://www.tensorflow.org/lite), for including your model
in an Android or iOS native mobile application, or in a Raspberry Pi, IoT or
microcontroller application.
* [TensorFlow.js](https://www.tensorflow.org/js), for running your model in a
web browser or a Node.JS application.
