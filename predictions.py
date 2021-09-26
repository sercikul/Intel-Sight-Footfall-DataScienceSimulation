import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
from pred_utils import *

# Use Case Scenarios
use_cases = {"1": "queueing",
             "2": "freeSeats",
             "3": "event"}


def create_future_data(total_df):
    """Machine Learning/Analytics unit. Does hyperparameter tuning, model selection
    on historical data. Predicts the next 2 months and returns predictions dataset."""
    device_lst = []
    # Forecasting Horizon (2 months = 1460 h)
    fh = np.arange(1, 1460 + 1)
    # Retrieve all devices (deviceID)
    devices = total_df["deviceID"].values.ravel()
    device_arr = pd.unique(devices)
    # Loop through devices
    for i in device_arr:
        # Filter dataframe for device and respective use case and
        # pre-process data for all scenarios.
        y_uc = total_df[total_df["deviceID"] == i]
        uc_arr = y_uc["recordType"].unique()
        record_type = uc_arr[0]
        uc = use_cases[record_type]
        y_uc = y_uc.reindex(["timestamp", uc], axis=1)
        # Make data univariate for forecasts and in 1 hour intervals
        y_uc = y_uc.set_index("timestamp")
        if uc == "event":
            # Person enters +1, Person leaves -1.
            y_uc[y_uc == "personIn"] = 1
            y_uc[y_uc == "personOut"] = -1
            y_uc["event"] = pd.to_numeric(np.cumsum(y_uc["event"]))

        # Aggregate footfall on hourly basis
        y = y_uc.groupby(pd.Grouper(freq="60Min")).aggregate(np.mean)
        y.columns = ["y"]
        y["y"] = y["y"].fillna(0)
        y["y"] = y["y"].astype(float)
        y = pd.Series(y["y"])
        # Handle anomalies
        y_ = anomaly_handler(y, uc)
        # Do log transformation to prevent negative forecasts
        y_log = np.log(y_ + 1)
        # Get Prophet Param Dictionary
        print(f"\nProphet Hyperparameter Tuning for {uc} is now conducted.\n")
        prophet_param_dict = get_tuned_hyperparameters(optimise_prophet, param_names_prophet,
                                                       param_space_prophet, y_log, calls=3)
        # Get Naive Param Dictionary
        print(f"\nNaiveForecaster Hyperparameter Tuning for {uc} is now conducted.\n")
        naive_param_dict = get_tuned_hyperparameters(optimise_naive, param_names_naive,
                                                     param_space_naive, y_log, calls=50)
        # Model Selection through Ensemble Predictions
        print(f"\nModel Selection for {uc} is now under progress.\n")
        y_pred = ensemble_predictions(prophet_param_dict, naive_param_dict, fh, y_log)
        # If more than available seats predicted, cap the predictions to max. available
        if uc == "freeSeats":
            y_pred[y_pred > np.max(y.values)] = np.max(y.values)
        # Create forecast dataframe
        y_pred_df = y_pred.to_frame()
        y_pred_df = y_pred_df.rename_axis("timestamp")
        y_pred_df["timestamp"] = y_pred_df.index
        y_pred_df = y_pred_df.reset_index(drop=True)
        y_pred_df["recordType"] = uc
        y_pred_df["deviceID"] = i
        device_lst.append(y_pred_df)
    # Concatenate all dataframes and return them
    y_pred_df_total = pd.concat(device_lst, sort=True)
    y_pred_df_total = y_pred_df_total.sort_values(["timestamp", "deviceID"], ascending=(True, True))
    y_pred_df_total = y_pred_df_total.reset_index(drop=True)
    # Convert dataframe to JSON-like dictionary
    y_pred_df_total = y_pred_df_total.to_dict("records")
    return y_pred_df_total
