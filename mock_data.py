import pandas as pd
import numpy as np
#import rapidjson as json
from utilities import *
from scipy.stats import truncnorm
from datetime import date, timedelta, datetime
import random
from numpy.random import choice

import timeit

start = timeit.default_timer()

#Your statements here

stop = timeit.default_timer()


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
# Specify the use case/attribute


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
    traffic_arr = normal_dist(ts.hour, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case)

    df[use_case] = traffic_arr
    df[use_case] = np.rint(df[use_case].ewm(span=8).mean())
    df[use_case] = df[use_case].clip(0)
    # Append df to collection
    df_collection.append(df)

    return df_collection


# Event-based approach
def create_df_event(start_ts: str, end_ts: str, device: dict):
    df_collection = []
    # Footfall statistics from device dict
    ff_mean = device["footfall"]["mean"]
    ff_std = device["footfall"]["std"]
    ff_min = device["footfall"]["min"]
    ff_max = device["footfall"]["max"]
    ff_peak = device["footfall"]["peak_times"]
    first_pk, second_pk = ff_peak[0], ff_peak[1]

    # Dwell times
    dwell_mean = device["footfall"]["dwell_mean"]
    dwell_sd = device["footfall"]["dwell_sd"]

    # Normal distribution of people entering ("personIn")
    # Numpy array of average seconds of event occurence from 0 to 24
    use_case = "event"
    time_arr = np.arange(24)
    traffic_arr = normal_dist(time_arr, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case)

    # Start and end dates
    start_dt = pd.to_datetime(start_ts)
    end_dt = pd.to_datetime(end_ts)
    # Convert to ms
    start_num = convert_to_ms(start_dt)
    end_num = convert_to_ms(end_dt)

    for i in range(24):
        # Frequency per hour
        freq_h = traffic_arr[i]
        # Frequency per ms
        freq_ms = freq_h / 3_600_000
        # Duration in ms
        duration = end_num - start_num
        # Create personIn events
        freq = int(duration * freq_ms)
        in_occurrences = np.random.randint(start_num, end_num, freq, dtype=np.int64)
        date_rng = pd.to_datetime(in_occurrences, unit='ms')
        person_in_ts = date_rng[date_rng.hour == i]
        df_event_in = pd.DataFrame(person_in_ts, columns=["timestamp"])
        df_event_in['event'] = "personIn"
        df_collection.append(df_event_in)

        # Create personOut events. Assume that the average dwell time of a person is 3 hours and the std is 2 hours.
      #  # Normal distribution of dwell time in milliseconds (hence, h times 3.6 million)

        # Average dwell statistics of hour range
        dw_hour_mean, dw_hour_sd = dwell_time(i, dwell_mean, dwell_sd, first_pk, second_pk)
        dwell_time_ms = truncated_normal(dw_hour_mean, dw_hour_sd, 1000, (100 * 3_600_000), size=len(person_in_ts))
        out_occurrences = person_in_ts + dwell_time_ms.astype('timedelta64[ms]')
        person_out_ts = pd.to_datetime(out_occurrences, unit='ms')
        df_event_out = pd.DataFrame(person_out_ts, columns=["timestamp"])
        df_event_out['event'] = "personOut"
        df_collection.append(df_event_out)

    return df_collection


# Specify devices, start, end as well as frequency of time series
# Interval - timestamp approach.

# Synthesise data for use cases 1 and 2.

# CLARIFY IF ONE DEVICEID FOR ONE TARGET
def synthesise_data(devices: list, use_cases: dict, start_ts: str, end_ts: str, freq_ts: str):
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
            event_frames = create_df_event(start_ts, end_ts, device)
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

    return df_total


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
            "footfall": {"peak_times": [11, 14],
                         "mean": 4,
                         "std": 3,
                         "min": -10,
                         "max": 20}},

           {"deviceID": "3",
            "useCase": "3",
            "footfall": {"peak_times": [10, 16],
                         "mean": 150,
                         "std": 15,
                         "min": 0,
                         "max": 20000,
                         "dwell_mean": 1,
                         "dwell_sd": 0.3}}
           ]



start_ts = "2020-06-28"
end_ts = "now"
interval_freq = "10S"

# Create the data set
total_df = synthesise_data(devices, use_cases, start_ts, end_ts, interval_freq)

#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.width', None)
#pd.set_option('display.max_colwidth', -1)


#print(total_df.head(50))



print(total_df)
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
#print(person_out_df)
#print(person_in_df)
