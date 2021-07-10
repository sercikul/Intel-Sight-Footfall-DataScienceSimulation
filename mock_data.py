import pandas as pd
import numpy as np
#import rapidjson as json
from utilities import *
from scipy.stats import truncnorm
from datetime import date, timedelta, datetime
import random
from numpy.random import choice

# Further to-dos
# Change "deviceID" to "_id"
# Add some "noise" to your data

# Use moving averages to make data more realistic
# Values should depend on PAST values and not be completely random


# Event data
# Normal distribution per venue regarding time ?

attributes = ['timestamp', 'deviceID', 'targetID', 'queueing', 'freeSeats', 'event']


# Specify date range, start/end hours of the data frame.
# Specify a normal distributed mean and std for footfall (e.g. queue, free seats) in the given time frame.
# Specify the use case/attribute.


# Timestamp approach (Use Cases 1 (queueing) and 2 (freeSeats))
# def create_df_timestamp(date_range, intervals: dict, device: dict, use_case: str):
#   df_collection = []
#  for key, value in intervals.items():
#     interval_filter = (date_range.hour <= value[1]) & (date_range.hour >= value[0])
#    filtered_ts = date_range[interval_filter]
#   df = pd.DataFrame(filtered_ts, columns=["timestamp"])
#  traffic = np.random.normal(loc=device["footfall"][key]["mean"],
#                                scale=device["footfall"][key]["std"], size=(len(df)))

# Apply exponentially-weighted-moving average to give recent data more weight
# df[use_case] = traffic.ewm(span=6).astype(int)
# df_id1["1-hour-EWMA"] = df_id1["freeSeats"].ewm(span=12).mean()
# df[use_case] = traffic
# df[use_case] = df[use_case].ewm(span=6).mean().astype(int)
# Append df to collection
# df_collection.append(df)

# return df_collection


def create_df_timestamp(start_ts: str, end_ts: str, freq_ts: str, device: dict, use_case: str):
    df_collection = []
    # Footfall statistics from device dict
    ff_mean = device["footfall"]["mean"]
    ff_std = device["footfall"]["std"]
    ff_min = device["footfall"]["min"]
    ff_max = device["footfall"]["max"]
    ff_peak = device["footfall"]["peak_times"]
    first_pk, second_pk = ff_peak[0], ff_peak[1]

    # Range of time series
    ts = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)
    df = pd.DataFrame(ts, columns=["timestamp"])

    # Mock traffic in normal distribution over time
    traffic_arr = normal_dist(ts, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case)

    df[use_case] = traffic_arr
    df[use_case] = df[use_case].ewm(span=8).mean().astype(int)
    # Append df to collection
    df_collection.append(df)

    return df_collection


# Event-based approach
def create_df_event(start_ts: str, end_ts: str, intervals: dict, device: dict):
    df_collection = []
    start_dt = pd.to_datetime(start_ts)
    end_dt = pd.to_datetime(end_ts)

    start_num = convert_to_ms(start_dt)
    end_num = convert_to_ms(end_dt)
    events = device["events"]
    for key, value in intervals.items():
        frequency = (end_num - start_num) // device["footfall"][key]["freq"]
        date_rng = pd.to_datetime(np.random.randint(start_num, end_num, frequency, dtype=np.int64), unit='ms')
        interval_filter = (date_rng.hour <= value[1]) & (date_rng.hour >= value[0])
        filtered_ts = date_rng[interval_filter]
        df_event = pd.DataFrame(filtered_ts, columns=["timestamp"])
        # Create event column with values
        event_weights = device["footfall"][key]["weights"]
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
            # date_rng = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)

            # Concatenate low and peak times
            stamp_frames = create_df_timestamp(start_ts, end_ts, freq_ts, device, use_case)
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
    df_total = pd.concat(device_lst, sort=True)

    # Convert floats to int
    df_total["queueing"] = df_total["queueing"].astype(pd.Int64Dtype())
    df_total["freeSeats"] = df_total["freeSeats"].astype(pd.Int64Dtype())

    df_total = df_total.sort_values(["timestamp", "deviceID"], ascending=(True, True))
    df_total = df_total.reset_index(drop=True)

    # Reorder dataframe
    df_total = df_total[attributes]

    return df_total.head(50000)


# Parameters

# Specify parameters

# Devices (venues) have different footfall means/stds.

# Target use cases
use_cases = {"1": "queueing",
             "2": "freeSeats",
             "3": "event"}

devices = [{"deviceID": "1",
            "useCase": "1",
            "footfall": {"peak_times": [10, 16],
                         "mean": 12,
                         "std": 4,
                         "min": 0,
                         "max": 50}},

           {"deviceID": "2",
            "useCase": "2",
            "footfall": {"peak_times": [10, 16],
                         "mean": 14,
                         "std": 6,
                         "min": 0,
                         "max": 20}},
           {"deviceID": "3",
            "useCase": "3",
            "events": ["personIn", "personOut"],
            "footfall": {"midnight": {"freq": 400000, "weights": [0.25, 0.75]},
                         "early_morning": {"freq": 60000, "weights": [0.75, 0.25]},
                         "morning": {"freq": 25000, "weights": [0.7, 0.3]},
                         "noon": {"freq": 17000, "weights": [0.6, 0.4]},
                         "early_evening": {"freq": 22000, "weights": [0.2, 0.8]},
                         "evening": {"freq": 80000, "weights": [0.1, 0.9]}}}
           ]

intervals = {"midnight": [0, 4],
             "early_morning": [5, 7],
             "morning": [8, 11],
             "noon": [12, 16],
             "early_evening": [17, 20],
             "evening": [21, 23]}

start_ts = "2020-06-28"
end_ts = "now"
interval_freq = "10S"

# Create the data set
total_df = synthesise_data(devices, use_cases, intervals, start_ts, end_ts, interval_freq)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

print(total_df.describe())
#print(total_df)
# Convert to JSON

#df_json = total_df.to_json(orient="records", date_format="iso")

# Pretty-print json file to check data.

#parsed = json.loads(df_json)
#json_file = json.dumps(parsed, indent=4)

# print(total_df)
# print(json_file)
# print(df_json)
## Test if realistic


# Compare number of personIn with personOut
person_in_df = total_df[total_df["event"] == "personIn"]
person_out_df = total_df[total_df["event"] == "personOut"]

# print(total_df)
# print(person_out_df)
# print(person_in_df)
