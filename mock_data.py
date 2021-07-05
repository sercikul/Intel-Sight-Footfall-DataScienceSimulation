import pandas as pd
import numpy as np
import calendar
from datetime import datetime
import random
from numpy.random import choice

# Event data
# Normal distribution per venue regarding time ?

attributes = ['timestamp', 'deviceID', 'targetID', 'queueing', 'freeSeats', 'event']


# Specify date range, start/end hours of the data frame.
# Specify a normal distributed mean and std for footfall (e.g. queue, free seats) in the given time frame.
# Specify the use case/attribute.

# Timestamp approach (Use Cases 1 (queueing) and 2 (freeSeats))
def create_df_timestamp(date_range, intervals: dict, device: dict, use_case: str):
    df_collection = []
    for key, value in intervals.items():
        interval_filter = (date_range.hour <= value[1]) & (date_range.hour >= value[0])
        filtered_ts = date_range[interval_filter]
        df = pd.DataFrame(filtered_ts, columns=["timestamp"])
        traffic = np.random.normal(loc=device["footfall"][key]["mean"],
                                   scale=device["footfall"][key]["std"], size=(len(df)))
        df[use_case] = traffic.astype(int)
        # Append df to collection
        df_collection.append(df)

    return df_collection


# Event-based approach
def create_df_event(start_ts: str, end_ts: str, intervals: dict, device: dict):
    df_collection = []
    start_num = pd.to_datetime(start_ts).value // 10 ** 9
    end_num = pd.to_datetime(end_ts).value // 10 ** 9
    events = device["events"]
    for key, value in intervals.items():
        frequency = (end_num - start_num) // device["footfall"][key]["freq"]
        event_weights = device["footfall"][key]["weights"]
        date_rng = pd.to_datetime(np.random.randint(start_num, end_num, frequency), unit='s')
        interval_filter = (date_rng.hour <= value[1]) & (date_rng.hour >= value[0])
        filtered_ts = date_rng[interval_filter]
        df_event = pd.DataFrame(filtered_ts, columns=["timestamp"])
        # Create event column with values
        df_event['event'] = np.random.choice(events, size=len(df_event), p=event_weights)

        # Append dataframes
        df_collection.append(df_event)

    return df_collection


# Specify devices, start, end as well as frequency of time series
# Interval - timestamp approach.

# Synthesise data for use cases 1 and 2.

# CLARIFY IF ONE DEVICEID FOR ONE TARGET
def synthesise_data(devices: list, use_cases: dict, intervals: dict, start_ts: str, end_ts: str, freq_ts: str):
    device_lst = []
    # Devices for loop
    for device in devices:
        target_id = device["useCase"]
        device_id = device["deviceID"]
        use_case = use_cases[target_id]
        # If not event-based.
        if use_case != "event":
            date_rng = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)

            # Concatenate low and peak times
            stamp_frames = create_df_timestamp(date_rng, intervals, device, use_case)
            df = pd.concat(stamp_frames)
        else:
            event_frames = create_df_event(start_ts, end_ts, intervals, device)
            df = pd.concat(event_frames)

        # Bring in other attributes
        df['targetID'] = target_id
        df['deviceID'] = device_id

        # Append device-specific df to device_lst
        device_lst.append(df)

    # Concat the df in the device_lst
    df_total = pd.concat(device_lst)

    # Replace null with empty string

    # Convert floats to int
    df_total["queueing"] = df_total["queueing"].astype(pd.Int64Dtype())
    df_total["freeSeats"] = df_total["freeSeats"].astype(pd.Int64Dtype())

    df_total = df_total.sort_values(["timestamp", "deviceID"], ascending=(True, True))
    df_total = df_total.reset_index(drop=True)

    # Reorder dataframe
    df_total = df_total[attributes]

    return df_total


# Parameters
start = "28/6/2019"
end = "now"

# Specify parameters

# Devices (venues) have different footfall means/stds.

# Target use cases
use_cases = {"1": "queueing",
             "2": "freeSeats",
             "3": "event"}

devices = [{"deviceID": "1",
            "useCase": "1",
            "footfall": {"midnight": {"mean": 1, "std": 1},
                         "early_morning": {"mean": 4, "std": 2},
                         "morning": {"mean": 16, "std": 3},
                         "noon": {"mean": 24, "std": 4},
                         "early_evening": {"mean": 12, "std": 2},
                         "evening": {"mean": 8, "std": 2}}},

           {"deviceID": "2",
            "useCase": "2",
            "footfall": {"midnight": {"mean": 32, "std": 2},
                         "early_morning": {"mean": 29, "std": 3},
                         "morning": {"mean": 20, "std": 4},
                         "noon": {"mean": 10, "std": 4},
                         "early_evening": {"mean": 16, "std": 3},
                         "evening": {"mean": 26, "std": 2}}},

           {"deviceID": "3",
            "useCase": "3",
            "events": ["personIn", "personOut"],
            "footfall": {"midnight": {"freq": 400, "weights": [0.4, 0.6]},
                         "early_morning": {"freq": 60, "weights": [0.8, 0.2]},
                         "morning": {"freq": 25, "weights": [0.7, 0.3]},
                         "noon": {"freq": 17, "weights": [0.8, 0.2]},
                         "early_evening": {"freq": 22, "weights": [0.2, 0.8]},
                         "evening": {"freq": 80, "weights": [0.1, 0.9]}}}
           ]

intervals = {"midnight": [0, 4],
             "early_morning": [5, 7],
             "morning": [8, 11],
             "noon": [12, 16],
             "early_evening": [17, 20],
             "evening": [21, 23]}


start_ts = "28/6/2019"
end_ts = "now"
interval_freq = "10S"

# Create the data set
print(synthesise_data(devices, use_cases, intervals, start_ts, end_ts, interval_freq))