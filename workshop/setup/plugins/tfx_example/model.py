# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Python source file include taxi pipeline functions and necesasry utils."""
from __future__ import division
from __future__ import print_function

import os

import tensorflow as tf
import tensorflow_model_analysis as tfma
import tensorflow_transform as transform
from tensorflow_transform.beam.tft_beam_io import transform_fn_io
from tensorflow_transform.saved import saved_transform_io
from tensorflow_transform.tf_metadata import metadata_io
from tensorflow_transform.tf_metadata import schema_utils
from tfx.executors.trainer import TrainingSpec

def _build_estimator(transform_output,
                     config,
                     hidden_units=None,
                     warm_start_from=None):
  """Build an estimator for predicting the tipping behavior of taxi riders.

  Args:
    transform_output: directory in which the tf-transform model was written
      during the preprocessing step.
    config: tf.contrib.learn.RunConfig defining the runtime environment for the
      estimator (including model_dir).
    hidden_units: [int], the layer sizes of the DNN (input layer first)
    warm_start_from: Optional directory to warm start from.

  Returns:
    Resulting DNNLinearCombinedClassifier.
  """
  metadata_dir = os.path.join(transform_output,
                              transform_fn_io.TRANSFORMED_METADATA_DIR)
  transformed_metadata = metadata_io.read_metadata(metadata_dir)
  transformed_feature_spec = transformed_metadata.schema.as_feature_spec()

  transformed_feature_spec.pop(_transformed_name(_LABEL_KEY))

  real_valued_columns = [
      tf.feature_column.numeric_column(key, shape=())
      for key in _transformed_names(_DENSE_FLOAT_FEATURE_KEYS)
  ]
  categorical_columns = [
      tf.feature_column.categorical_column_with_identity(
          key, num_buckets=_VOCAB_SIZE + _OOV_SIZE, default_value=0)
      for key in _transformed_names(_VOCAB_FEATURE_KEYS)
  ]
  categorical_columns += [
      tf.feature_column.categorical_column_with_identity(
          key, num_buckets=_FEATURE_BUCKET_COUNT, default_value=0)
      for key in _transformed_names(_BUCKET_FEATURE_KEYS)
  ]
  categorical_columns += [
      tf.feature_column.categorical_column_with_identity(  # pylint: disable=g-complex-comprehension
          key, num_buckets=num_buckets, default_value=0)
      for key, num_buckets in zip(
          _transformed_names(_CATEGORICAL_FEATURE_KEYS),
          _MAX_CATEGORICAL_FEATURE_VALUES)
  ]
  return tf.estimator.DNNLinearCombinedClassifier(
      config=config,
      linear_feature_columns=categorical_columns,
      dnn_feature_columns=real_valued_columns,
      dnn_hidden_units=hidden_units or [100, 70, 50, 25],
      warm_start_from=warm_start_from)


def _example_serving_receiver_fn(transform_output, schema):
  """Build the serving in inputs.

  Args:
    transform_output: directory in which the tf-transform model was written
      during the preprocessing step.
    schema: the schema of the input data.

  Returns:
    Tensorflow graph which parses examples, applying tf-transform to them.
  """
  raw_feature_spec = _get_raw_feature_spec(schema)
  raw_feature_spec.pop(_LABEL_KEY)

  raw_input_fn = tf.estimator.export.build_parsing_serving_input_receiver_fn(
      raw_feature_spec, default_batch_size=None)
  serving_input_receiver = raw_input_fn()

  _, transformed_features = (
      saved_transform_io.partially_apply_saved_transform(
          os.path.join(transform_output, transform_fn_io.TRANSFORM_FN_DIR),
          serving_input_receiver.features))

  return tf.estimator.export.ServingInputReceiver(
      transformed_features, serving_input_receiver.receiver_tensors)


def _eval_input_receiver_fn(transform_output, schema):
  """Build everything needed for the tf-model-analysis to run the model.

  Args:
    transform_output: directory in which the tf-transform model was written
      during the preprocessing step.
    schema: the schema of the input data.

  Returns:
    EvalInputReceiver function, which contains:
      - Tensorflow graph which parses raw untransformed features, applies the
        tf-transform preprocessing operators.
      - Set of raw, untransformed features.
      - Label against which predictions will be compared.
  """
  # Notice that the inputs are raw features, not transformed features here.
  raw_feature_spec = _get_raw_feature_spec(schema)

  serialized_tf_example = tf.placeholder(
      dtype=tf.string, shape=[None], name='input_example_tensor')

  # Add a parse_example operator to the tensorflow graph, which will parse
  # raw, untransformed, tf examples.
  features = tf.parse_example(serialized_tf_example, raw_feature_spec)

  # Now that we have our raw examples, process them through the tf-transform
  # function computed during the preprocessing step.
  _, transformed_features = (
      saved_transform_io.partially_apply_saved_transform(
          os.path.join(transform_output, transform_fn_io.TRANSFORM_FN_DIR),
          features))

  # The key name MUST be 'examples'.
  receiver_tensors = {'examples': serialized_tf_example}

  # NOTE: Model is driven by transformed features (since training works on the
  # materialized output of TFT, but slicing will happen on raw features.
  features.update(transformed_features)

  return tfma.export.EvalInputReceiver(
      features=features,
      receiver_tensors=receiver_tensors,
      labels=transformed_features[_transformed_name(_LABEL_KEY)])


def _input_fn(filenames, transform_output, batch_size=200):
  """Generates features and labels for training or evaluation.

  Args:
    filenames: [str] list of CSV files to read data from.
    transform_output: directory in which the tf-transform model was written
      during the preprocessing step.
    batch_size: int First dimension size of the Tensors returned by input_fn

  Returns:
    A (features, indices) tuple where features is a dictionary of
      Tensors, and indices is a single Tensor of label indices.
  """
  metadata_dir = os.path.join(transform_output,
                              transform_fn_io.TRANSFORMED_METADATA_DIR)
  transformed_metadata = metadata_io.read_metadata(metadata_dir)
  transformed_feature_spec = transformed_metadata.schema.as_feature_spec()

  transformed_features = tf.contrib.learn.io.read_batch_features(
      filenames,
      batch_size,
      transformed_feature_spec,
      reader=_gzip_reader_fn)

  # We pop the label because we do not want to use it as a feature while we're
  # training.
  return transformed_features, transformed_features.pop(
      _transformed_name(_LABEL_KEY))


# TFX will call this function
def trainer_fn(hparams, schema):
  """Build the estimator using the high level API.

  Args:
    hparams: Holds hyperparameters used to train the model as name/value pairs.
    schema: Holds the schema of the training examples.

  Returns:
    The estimator that will be used for training and eval
  """
  # Number of nodes in the first layer of the DNN
  first_dnn_layer_size = 100
  num_dnn_layers = 4
  dnn_decay_factor = 0.7

  train_batch_size = 40
  eval_batch_size = 40

  train_input_fn = lambda: _input_fn(  # pylint: disable=g-long-lambda
      hparams.train_files,
      hparams.transform_output,
      batch_size=train_batch_size)

  eval_input_fn = lambda: _input_fn(  # pylint: disable=g-long-lambda
      hparams.eval_files,
      hparams.transform_output,
      batch_size=eval_batch_size)

  train_spec = tf.estimator.TrainSpec(  # pylint: disable=g-long-lambda
      train_input_fn,
      max_steps=hparams.train_steps)

  serving_receiver_fn = lambda: _example_serving_receiver_fn(  # pylint: disable=g-long-lambda
      hparams.transform_output, schema)

  exporter = tf.estimator.FinalExporter('chicago-taxi', serving_receiver_fn)
  eval_spec = tf.estimator.EvalSpec(
      eval_input_fn,
      steps=hparams.eval_steps,
      exporters=[exporter],
      name='chicago-taxi-eval')

  run_config = tf.estimator.RunConfig(
      save_checkpoints_steps=999, keep_checkpoint_max=1)

  run_config = run_config.replace(model_dir=hparams.serving_model_dir)

  estimator = _build_estimator(
      transform_output=hparams.transform_output,

      # Construct layers sizes with exponetial decay
      hidden_units=[
          max(2, int(first_dnn_layer_size * dnn_decay_factor**i))
          for i in range(num_dnn_layers)
      ],
      config=run_config,
      warm_start_from=hparams.warm_start_from)

  # Input receiver for TFMA
  receiver_fn = lambda: _eval_input_receiver_fn(  # pylint: disable=g-long-lambda
      hparams.transform_output, schema)

  return TrainingSpec(estimator, train_spec, eval_spec, receiver_fn)