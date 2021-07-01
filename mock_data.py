import pandas as pd
import numpy as np
import calendar
from datetime import datetime
import random

# Event data
# Normal distribution per venue regarding time ?

attributes = ['timestamp', 'deviceID', 'targetID', 'queueing', 'freeSeats', 'event']


# Specify date range, start/end hours of the data frame.
# Specify a normal distributed mean and std for footfall (e.g. queue, free seats) in the given time frame.
# Specify the use case/attribute.

def create_df(date_range, intervals: dict, devices: dict, device_id: str, use_case: str):
    df_collection = []
    for key, value in intervals.items():
        interval_filter = (date_range.hour <= value[1]) & (date_range.hour >= value[0])
        filtered_ts = date_range[interval_filter]
        df = pd.DataFrame(filtered_ts, columns=["timestamp"])
        traffic = np.random.normal(loc=devices[device_id][key][use_case]["mean"], scale=devices[device_id][key][use_case]["std"], size=(len(df)))
        df[use_case] = traffic.astype(int)

        # Append df to collection
        df_collection.append(df)

    return df_collection


# Specify devices, start, end as well as frequency of time series
# Interval - timestamp approach.
def synthesise_data(device_info: dict, intervals: dict, start_ts: str, end_ts: str, freq_ts: str, use_case: str, use_case_dict: dict):
    target = [k for k, v in use_case_dict.items() if v == use_case]
    target_id = target[0]
    device_lst = []
    # Devices for loop
    for key in device_info:
        date_rng = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)

        # Concatenate low and peak times
        frames = create_df(date_rng, intervals, device_info, key, use_case)
        df = pd.concat(frames)

        # Bring in other attributes
        df['targetID'] = target_id
        df['deviceID'] = key

        if use_case == "queueing":
            df['freeSeats'] = ""
        else:
            df['queueing'] = ""

        df['event'] = ""

        # Append device-specific df to device_lst
        device_lst.append(df)

    # sort dataframe

    # Concat the df in the device_lst
    df_total = pd.concat(device_lst)

    df_total = df_total.sort_values(["timestamp", "deviceID"], ascending=(True, True))
    df_total = df_total.reset_index(drop=True)

    # Reorder dataframe
    df_total = df_total[attributes]

    return df_total.head(500000)


# Specify parameters

# Devices (venues) have different footfall means/stds.

devices = {"1": {"midnight": {"queueing": {"mean": 1, "std": 1},
                              "freeSeats": {"mean": 25, "std": 2}},

                 "early_morning": {"queueing": {"mean": 4, "std": 2},
                                   "freeSeats": {"mean": 23, "std": 2}},

                 "morning": {"queueing": {"mean": 16, "std": 3},
                             "freeSeats": {"mean": 18, "std": 4}},

                 "noon": {"queueing": {"mean": 24, "std": 4},
                          "freeSeats": {"mean": 12, "std": 4}},

                 "early_evening": {"queueing": {"mean": 12, "std": 2},
                                   "freeSeats": {"mean": 20, "std": 3}},

                 "evening": {"queueing": {"mean": 8, "std": 2},
                             "freeSeats": {"mean": 21, "std": 4}}},

           "2": {"midnight": {"queueing": {"mean": 3, "std": 1},
                              "freeSeats": {"mean": 32, "std": 4}},

                 "early_morning": {"queueing": {"mean": 10, "std": 2},
                                   "freeSeats": {"mean": 29, "std": 3}},

                 "morning": {"queueing": {"mean": 26, "std": 4},
                             "freeSeats": {"mean": 20, "std": 4}},

                 "noon": {"queueing": {"mean": 44, "std": 5},
                          "freeSeats": {"mean": 10, "std": 2}},

                 "early_evening": {"queueing": {"mean": 32, "std": 3},
                                   "freeSeats": {"mean": 16, "std": 3}},

                 "evening": {"queueing": {"mean": 14, "std": 2},
                             "freeSeats": {"mean": 26, "std": 4}}}
           }

intervals = {"midnight": [0, 4],
             "early_morning": [5, 7],
             "morning": [8, 11],
             "noon": [12, 16],
             "early_evening": [17, 20],
             "evening": [21, 23]}

start_ts = "28/6/2019"
end_ts = "now"
interval_freq = "10S"

use_cases = {"1": "queueing",
             "2": "freeSeats",
             "3": "event"}


# Use Case 1: Queueing
print(synthesise_data(devices, intervals, start_ts, end_ts, interval_freq, use_cases["1"], use_cases))


# Use Case 2: Free Seats
print(synthesise_data(devices, intervals, start_ts, end_ts, interval_freq, use_cases["2"], use_cases))
