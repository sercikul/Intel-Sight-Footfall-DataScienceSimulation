import pandas as pd
import numpy as np
import calendar
from datetime import datetime
import random

# Event data
# Normal distribution per venue regarding time ?

attributes = ['targetID', 'deviceID', 'timestamp', 'queueing', 'freeSeats', 'event']


# Specify date range, start/end hours of the data frame.
# Specify a normal distributed mean and std for footfall (e.g. queue, free seats) in the given time frame.
# Specify the use case/attribute.

def create_df(date_range, start_hour: int, end_hour: int, mean: int, std: int, use_case: str):
    interval_filter = (date_range.hour <= end_hour) & (date_range.hour >= start_hour)
    filtered_ts = date_range[interval_filter]
    df = pd.DataFrame(filtered_ts, columns=["timestamp"])
    traffic = np.random.normal(loc=mean, scale=std, size=(len(df)))
    df[use_case] = traffic.astype(int)

    return df


# Specify devices, start, end as well as frequency of time series
# Interval - timestamp approach.
def synthesise_data(device_info: dict, start_ts: str, end_ts: str, freq_ts: str, use_case: str):
    target_id = "1"
    device_lst = []
    # Devices for loop
    for key in device_info:
        date_rng = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)

        # Queue from 0 to 4 A.M.
        midnight_queue_df = create_df(date_rng, 0, 4, device_info[key]["midnight"]["mean"], device_info[key]["midnight"]["std"], use_case)
        # Queue from 5 to 7 A.M.
        early_morning_queue_df = create_df(date_rng, 5, 7, device_info[key]["early_morning"]["mean"], device_info[key]["early_morning"]["std"], use_case)
        # Queue from 8 to 11 A.M.
        morning_queue_df = create_df(date_rng, 8, 11, device_info[key]["morning"]["mean"], device_info[key]["morning"]["std"], use_case)
        # Queue from 12 to 4 P.M.
        noon_queue_df = create_df(date_rng, 12, 16, device_info[key]["noon"]["mean"], device_info[key]["noon"]["std"], use_case)
        # Queue from 5 to 8 P.M.
        early_evening_queue_df = create_df(date_rng, 17, 20, device_info[key]["early_evening"]["mean"], device_info[key]["early_evening"]["std"], use_case)
        # Queue from 9 to 11 P.M.
        evening_queue_df = create_df(date_rng, 21, 23, device_info[key]["evening"]["mean"], device_info[key]["evening"]["std"], use_case)
        # Concatenate low and peak times
        frames = [midnight_queue_df, early_morning_queue_df, morning_queue_df, noon_queue_df, early_evening_queue_df,
                  evening_queue_df]
        df = pd.concat(frames)

        # Bring in other attributes
        df['targetID'] = target_id
        df['deviceID'] = key
        df['freeSeats'] = ""
        df['event'] = ""

        # Append device-specific df to device_lst
        device_lst.append(df)

    # sort dataframe

    # Concat the df in the device_lst
    df_total = pd.concat(device_lst)

    df_total = df_total.sort_values(["timestamp", "deviceID"], ascending=(True, True))
    df_total = df_total.reset_index(drop=True)

    return df_total.head(50)


# Specify parameters

devices = {"1": {"midnight": {"mean": 1, "std": 1},
                 "early_morning": {"mean": 4, "std": 2},
                 "morning": {"mean": 16, "std": 3},
                 "noon": {"mean": 24, "std": 4},
                 "early_evening": {"mean": 12, "std": 2},
                 "evening": {"mean": 8, "std": 2}},

           "2": {"midnight": {"mean": 3, "std": 1},
                 "early_morning": {"mean": 10, "std": 2},
                 "morning": {"mean": 26, "std": 4},
                 "noon": {"mean": 44, "std": 5},
                 "early_evening": {"mean": 32, "std": 3},
                 "evening": {"mean": 14, "std": 2}}
           }

start_ts = "28/6/2019"
end_ts = "now"
interval_freq = "10S"
use_case = "queueing"

print(synthesise_data(devices, start_ts, end_ts, interval_freq, use_case))
