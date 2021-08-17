# Time Series Predictions - SKTIME

# %matplotlib inline
#from mock_data import *
from pred_utils import *

# Remove later when these information are in the db
use_cases = {"1": "queueing",
             "2": "freeSeats",
             "3": "event"}

# Time Series Forecasts

def predict_future(total_df):
    # General variables: fh (pre-specified)
    device_lst = []
    # Forecasting Horizon (2 months = 1460 h)
    fh = np.arange(1, 1460 + 1)
    # 1. Retrieve all devices (deviceID)
    devices = total_df["deviceID"].values.ravel()
    device_arr = pd.unique(devices)
    # 2. Loop through devices
    for i in device_arr:
        uc = use_cases[i]
        # 3. Filter dataframe for device and respective use case
        # 4. Pre-Process data for all (if "event": pass in function to process)
        y_uc = total_df[total_df["deviceID"] == i]
        y_uc = y_uc.reindex(["timestamp", uc], axis=1)
        # Make data univariate for forecasts and in 1 hour intervals
        y_uc = y_uc.set_index("timestamp")
        if uc == "event":
            # Person enters +1, Person leaves -1

            # Create numpy array of length y_uc. Do cumulative sum.
            y_uc[y_uc == "personIn"] = 1
            y_uc[y_uc == "personOut"] = -1
            y_uc["event"] = pd.to_numeric(np.cumsum(y_uc["event"]))

        # Sum Footfall
        y = y_uc.groupby(pd.Grouper(freq="60Min")).aggregate(np.mean)
        y.columns = ["y"]
        y["y"] = y["y"].fillna(0)
        y["y"] = y["y"].astype(float)
        y = pd.Series(y["y"])
        # Handle anomalies
        y_ = anomaly_handler(y, uc)
        # plot_series(y_)
        # Do log transformation to prevent negative forecasts
        y_log = np.log(y_ + 1)
        # 5. Get Prophet Param Dictionary (from function, argument is n_calls)
        prophet_param_dict = get_tuned_hyperparameters(optimise_prophet, param_names_prophet,
                                                       param_space_prophet, y_log, calls=3)
        # 6. Get Naive Param Dictionary (from function, argument is n_calls)
        naive_param_dict = get_tuned_hyperparameters(optimise_naive, param_names_naive,
                                                     param_space_naive, y_log, calls=50)
        # 7. MultiPlex Ensemble Predictions
        y_pred = ensemble_predictions(prophet_param_dict, naive_param_dict, fh, y_log)
        # If more than available seats predicted, cap the predictions to maximum available
        if uc == "freeSeats":
            y_pred[y_pred > np.max(y.values)] = np.max(y.values)
        # Print for now to test
        # plot_series(y_, y_pred, labels=["y", "y_pred"])

        # 8. Create forecast dataframe
        y_pred_df = y_pred.to_frame()

        y_pred_df = y_pred_df.rename_axis("timestamp")
        y_pred_df["timestamp"] = y_pred_df.index
        y_pred_df = y_pred_df.reset_index(drop=True)

        y_pred_df["recordType"] = uc
        y_pred_df["deviceID"] = i

        device_lst.append(y_pred_df)

    # 9. Concatanete all dataframes
    # 10. Return concatenated dataframes

    y_pred_df_total = pd.concat(device_lst, sort=True)
    y_pred_df_total = y_pred_df_total.sort_values(["timestamp", "deviceID"], ascending=(True, True))
    y_pred_df_total = y_pred_df_total.reset_index(drop=True)

    # 11. Make dictionary
    y_pred_df_total = y_pred_df_total.to_dict("records")

    return y_pred_df_total
