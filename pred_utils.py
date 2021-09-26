import logging

logger = logging.getLogger('fbprophet.plot')
logger.setLevel(logging.CRITICAL)

from sktime.forecasting.fbprophet import Prophet
from sktime.forecasting.naive import NaiveForecaster
from sktime.performance_metrics.forecasting import mean_absolute_percentage_error

from functools import partial
from skopt import space
from skopt import gp_minimize
from sktime.forecasting.model_selection import (
    ForecastingGridSearchCV,
    SlidingWindowSplitter,
)
from sktime.forecasting.compose import MultiplexForecaster
from sktime.performance_metrics.forecasting import MeanSquaredError
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import pandas as pd

# PARAMETER SPACE FOR FACEBOOK'S PROPHET LIBRARY
param_space_prophet = [
    space.Categorical([True], name="yearly_seasonality"),
    space.Categorical([0.01, 0.1, 1, 5], name="seasonality_prior_scale"),
    space.Categorical([0.01, 0.1, 1, 5], name="holidays_prior_scale"),
    space.Categorical([0.001, 0.05, 0.1, 0.5], name="changepoint_prior_scale"),
    space.Real(0.8, 0.95, name="changepoint_range"),
]

param_names_prophet = [
    "yearly_seasonality",
    "seasonality_prior_scale",
    "holidays_prior_scale",
    "changepoint_prior_scale",
    "changepoint_range"
]


def optimise_prophet(params, param_names, y_log):
    """Returns accuracy score for tuned parameter combinations of Prophet"""
    params = dict(zip(param_names, params))
    model = Prophet(**params)
    tuned_score = tune_hyperparameters(model, y_log)
    return tuned_score


# PARAMETER SPACE FOR NAIVE FORECASTER
hourly, daily, weekly, monthly = 1, 24, 168, 730

param_space_naive = [
    space.Categorical(["last"], name="strategy"),
    space.Categorical([hourly, daily, weekly, monthly], name="sp")
]

param_names_naive = [
    "strategy",
    "sp",
]


def optimise_naive(params, param_names, y_log):
    """Returns accuracy score for tuned parameter combination of Naive"""
    params = dict(zip(param_names, params))
    model = NaiveForecaster(**params)
    tuned_score = tune_hyperparameters(model, y_log)
    return tuned_score


def tune_hyperparameters(model, y_log):
    """General function for hyperparameter tuning"""
    # Training data
    train_size = int(len(y_log) * 0.4)
    # Forecasting horizon of each data segment
    fh = np.arange(1, int(train_size * 0.2) + 1)
    rest_of_train = int(len(y_log) - (train_size + len(fh)))
    # Cross Validation based on sliding window. Split 4 times.
    n_splits = 4
    step_len = int((rest_of_train / n_splits))
    cv = SlidingWindowSplitter(fh=fh, window_length=train_size, step_length=step_len)
    smape_lst = []
    for idx in cv.split(y_log):
        # Train, validate and predict for each split data segment
        train, validate = y_log[idx[0]], y_log[idx[1]]
        model.fit(train)
        pred = model.predict(fh)
        y_pred = np.exp(pred) - 1
        y_valid = np.exp(validate) - 1
        # (Symmetric) Mean Absolute Percentage Error (MAPE) as accuracy metric
        smape = mean_absolute_percentage_error(y_pred, y_valid)
        smape_lst.append(smape)
    return np.mean(smape_lst)


def get_tuned_hyperparameters(optimise_forecaster, param_names, param_space, y_log, calls):
    """Function wrapper to return optimal hyperparameter combination"""
    optimisation = partial_optimiser(optimise_forecaster, param_names, y_log)
    result = optimisation_result(optimisation, param_space, calls)
    param_dict = dict(zip(param_names, result.x))
    return param_dict


def partial_optimiser(optimise_forecaster, param_names, y_log):
    """Returns function to partially apply Bayesian model optimisation"""
    return partial(optimise_forecaster, param_names=param_names, y_log=y_log)


def optimisation_result(optimisation, param_space, calls):
    """Bayesian hyperparameter tuning"""
    result = gp_minimize(optimisation,
                         dimensions=param_space,
                         n_calls=calls,
                         n_initial_points=calls,
                         verbose=10,
                         n_jobs=2)
    return result


def ensemble_predictions(prophet_params, naive_params, fh, y_log):
    """Ensemble forecaster for model selection. Selects model with highest accuracy."""
    forecaster = MultiplexForecaster(forecasters=[("fbprophet", Prophet(**prophet_params)),
                                                  ("naive", NaiveForecaster(**naive_params))])
    # Training data and forecasting horizon
    train_size = int(len(y_log) * 0.4)
    fhcv = np.arange(1, train_size * 0.2 + 1)
    # Cross Validation based on sliding window. Split 4 times.
    rest_of_train = int(len(y_log) - (train_size + len(fhcv)))
    n_splits = 4
    step_len = int((rest_of_train / n_splits))
    cv = SlidingWindowSplitter(fh=fhcv, window_length=train_size, step_length=step_len)
    # Mean Squared Error (MSE) as accuracy metric
    mse = MeanSquaredError()
    forecaster_param_grid = {"selected_forecaster": ["fbprophet", "naive"]}
    gscv = ForecastingGridSearchCV(forecaster, cv=cv, param_grid=forecaster_param_grid,
                                   verbose=0, n_jobs=2, scoring=mse)
    # Fit and Predict
    gscv.fit(y_log)
    print(gscv.cv_results_)
    y_pred_lg = gscv.predict(fh)
    y_pred = np.exp(y_pred_lg) - 1
    return y_pred


def anomaly_handler(y, use_case):
    """Function to detect and handle anomalies in order to avoid biased predictions."""
    # Threshold (Z-score) to identify as anomaly
    threshold = 2.2
    y_no_anom = y.rename(use_case)
    # Determine upper quartile of the data to later replace anomaly
    upper = y.quantile(0.75)
    # Get monthly aggregated footfall statistics
    monthly_y = y_no_anom.groupby(pd.Grouper(freq="M")).aggregate(np.mean)
    std_y = y_no_anom.groupby(pd.Grouper(freq="M")).aggregate(np.std)
    for i in y_no_anom.index:
        # Monthly statistics to compare the anomaly with "what is normal" in that specific season.
        # Consideration of seasonality is important, since an anomalous footfall in the summer
        # might be normal in the winter etc.
        mean_s = monthly_y[(monthly_y.index.month == i.month) & (monthly_y.index.year == i.year)]
        std_s = std_y[(std_y.index.month == i.month) & (std_y.index.year == i.year)]
        mean = np.array(mean_s)[0]
        std = np.array(std_s)[0]
        # Calculate Z score
        z = (y_no_anom[i] - mean) / std
        if z > threshold:
            y_no_anom[i] = upper
    return y_no_anom
