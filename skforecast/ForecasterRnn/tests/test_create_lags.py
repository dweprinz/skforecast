# Unit test _create_lags ForecasterRnn
# ==============================================================================
import re
import pytest
import numpy as np
import pandas as pd
from skforecast.ForecasterRnn import ForecasterRnn
from skforecast.ForecasterRnn.utils import create_and_compile_model
import tensorflow as tf

lags = 6
steps = 3
levels = "l1"
activation = "relu"
optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
loss = tf.keras.losses.MeanSquaredError()
recurrent_units = 100
dense_units = [128, 64]

def test_check_create_lags_exception_when_n_splits_less_than_0():
    """
    Check exception is raised when n_splits in _create_lags is less than 0.
    """
    series = pd.DataFrame(np.arange(10), columns=['l1'])
    y_array = np.arange(10)

    model = create_and_compile_model(
        series=series,
        lags=20,
        steps=steps,
        levels=levels,
        recurrent_units=recurrent_units,
        dense_units=dense_units,
        activation=activation,
        optimizer=optimizer,
        loss=loss,
    )
    forecaster = ForecasterRnn(model, levels)

    err_msg = re.escape(
                f'The maximum lag ({forecaster.max_lag}) must be less than the length '
                f'of the series minus the number of steps ({len(series)-(forecaster.steps-1)}).'
            )
    with pytest.raises(ValueError, match = err_msg):
        forecaster._create_lags(y=y_array, lags=forecaster.max_lag)

  
  # parametrize tests
@pytest.mark.parametrize("lags, steps, expected", [
    # test_create_lags_when_lags_is_3_steps_1_and_y_is_numpy_arange_10
    ([1, 2, 3], 1, (np.array([[2., 1., 0.],
                          [3., 2., 1.],
                          [4., 3., 2.],
                          [5., 4., 3.],
                          [6., 5., 4.],
                          [7., 6., 5.],
                          [8., 7., 6.]]),
                np.array([[3., 4., 5., 6., 7., 8., 9.]])
                )),
    # test_create_lags_when_lags_is_list_interspersed_lags_steps_1_and_y_is_numpy_arange_10
    ([1, 5], 1, (np.array([[4., 0.],
                          [5., 1.],
                          [6., 2.],
                          [7., 3.],
                          [8., 4.]]),
                np.array([[5., 6., 7., 8., 9.]])
                )),
    # test_create_lags_when_lags_is_3_steps_2_and_y_is_numpy_arange_10
    (3, 2, (np.array([[2., 1., 0.],
                          [3., 2., 1.],
                          [4., 3., 2.],
                          [5., 4., 3.],
                          [6., 5., 4.],
                          [7., 6., 5.]]),
                np.array([[3., 4., 5., 6., 7., 8.],
                          [4., 5., 6., 7., 8., 9.]])
                )),
    # test_create_lags_when_lags_is_3_steps_5_and_y_is_numpy_arange_10
    (3, 5, (np.array([[2., 1., 0.],
                          [3., 2., 1.],
                          [4., 3., 2.]]),
                np.array([[3., 4., 5.],
                          [4., 5., 6.],
                          [5., 6., 7.],
                          [6., 7., 8.],
                          [7., 8., 9.]])
                )),
    ]
)    
def test_create_lags_several_configurations(lags, steps, expected):
    """
    Test matrix of lags created with different configurations.
    """
    series = pd.DataFrame(np.arange(10), columns=['l1'])
    model = create_and_compile_model(
        series=series,
        lags=lags,
        steps=steps,
        levels=levels,
        recurrent_units=recurrent_units,
        dense_units=dense_units,
        activation=activation,
        optimizer=optimizer,
        loss=loss,
    )
    forecaster = ForecasterRnn(model, levels, lags)
    
    if isinstance(lags, int):
        lags = np.arange(1, lags+1)
    results = forecaster._create_lags(y=np.arange(10), lags = lags)

    np.testing.assert_array_equal(results[0], expected[0])
    np.testing.assert_array_equal(results[1], np.transpose(expected[1]))