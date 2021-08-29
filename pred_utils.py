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
#warnings.filterwarnings("ignore")
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import pandas as pd


# Prophet parameters
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


# PROPHET FORECASTER
def optimise_prophet(params, param_names, y_log):
    params = dict(zip(param_names, params))
    model = Prophet(**params)
    tuned_score = tune_hyperparameters(model, y_log)
    return tuned_score


# Naive parameters
hourly, daily, weekly, monthly = 1, 24, 168, 730

param_space_naive = [
    space.Categorical(["last"], name="strategy"),
    space.Categorical([hourly, daily, weekly, monthly], name="sp")
]

param_names_naive = [
    "strategy",
    "sp",
]


# NAIVE FORECASTER
def optimise_naive(params, param_names, y_log):
    params = dict(zip(param_names, params))
    model = NaiveForecaster(**params)
    tuned_score = tune_hyperparameters(model, y_log)
    return tuned_score


# Hyperparamater tuning
def tune_hyperparameters(model, y_log):
    train_size = int(len(y_log) * 0.4)
    fh = np.arange(1, int(train_size * 0.2) + 1)
    rest_of_train = int(len(y_log) - (train_size + len(fh)))
    # Split 4 times.
    n_splits = 4
    step_len = int((rest_of_train / n_splits))
    cv = SlidingWindowSplitter(fh=fh, window_length=train_size, step_length=step_len)
    smape_lst = []
    for idx in cv.split(y_log):
        train, validate = y_log[idx[0]], y_log[idx[1]]
        model.fit(train)
        pred = model.predict(fh)
        y_pred = np.exp(pred) - 1
        y_valid = np.exp(validate) - 1
        smape = mean_absolute_percentage_error(y_pred, y_valid)
        smape_lst.append(smape)

    return np.mean(smape_lst)


def get_tuned_hyperparameters(optimise_forecaster, param_names, param_space, y_log, calls):
    optimisation = partial_optimiser(optimise_forecaster, param_names, y_log)
    result = optimisation_result(optimisation, param_space, calls)
    param_dict = dict(zip(param_names, result.x))
    return param_dict


def partial_optimiser(optimise_forecaster, param_names, y_log):
    return partial(optimise_forecaster, param_names=param_names, y_log=y_log)


def optimisation_result(optimisation, param_space, calls):
    result = gp_minimize(optimisation,
                         dimensions=param_space,
                         n_calls=calls,
                         n_initial_points=calls,
                         verbose=10,
                         n_jobs=2)
    return result


# ENSEMBLE FORECASTER
def ensemble_predictions(prophet_params, naive_params, fh, y_log):
    forecaster = MultiplexForecaster(forecasters=[("fbprophet", Prophet(**prophet_params)),
                                                  ("naive", NaiveForecaster(**naive_params))])
    # Cross-validation
    train_size = int(len(y_log) * 0.4)
    fhcv = np.arange(1, train_size * 0.2 + 1)
    rest_of_train = int(len(y_log) - (train_size + len(fhcv)))
    # Split 4 times
    n_splits = 4
    step_len = int((rest_of_train / n_splits))
    cv = SlidingWindowSplitter(fh=fhcv, window_length=train_size, step_length=step_len)
    mse = MeanSquaredError()
    forecaster_param_grid = {"selected_forecaster": ["fbprophet", "naive"]}
    gscv = ForecastingGridSearchCV(forecaster, cv=cv, param_grid=forecaster_param_grid,
                                   verbose=0, n_jobs=2, scoring=mse)

    # Fit and Predict
    gscv.fit(y_log)
    y_pred_lg = gscv.predict(fh)
    y_pred = np.exp(y_pred_lg) - 1

    #print(gscv.cv_results_)
    return y_pred


# Anomaly handler

def anomaly_handler(y, use_case):
    threshold = 2.2
    y_no_anom = y.rename(use_case)
    upper = y.quantile(0.75)
    monthly_y = y_no_anom.groupby(pd.Grouper(freq="M")).aggregate(np.mean)
    std_y = y_no_anom.groupby(pd.Grouper(freq="M")).aggregate(np.std)
    for i in y_no_anom.index:
        # Mean and std from respective month and year
        mean_s = monthly_y[(monthly_y.index.month == i.month) & (monthly_y.index.year == i.year)]
        std_s = std_y[(std_y.index.month == i.month) & (std_y.index.year == i.year)]
        mean = np.array(mean_s)[0]
        std = np.array(std_s)[0]
        # Calculate Z score
        z = (y_no_anom[i] - mean) / std
        if z > threshold:
            # outliers.append(i.to_datetime())
            y_no_anom[i] = upper
        # print(y_outliers[i])
    return y_no_anom

