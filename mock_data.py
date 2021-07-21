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


def create_df_timestamp(start_ts: str, end_ts: str, freq_ts: str, device: dict, anomalies: tuple, use_case: str):
    df_collection = []
    # Footfall statistics from device dict
    ff_mean = device["footfall"]["mean"]
    ff_std = device["footfall"]["std"]
    ff_min = device["footfall"]["min"]
    ff_max = device["footfall"]["max"]
    ff_peak = device["footfall"]["peak_times"]
    ff_anom = device["footfall"]["anom_freq"]
    first_pk, second_pk = ff_peak[0], ff_peak[1]

    # Range of time series
    ts = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)
    df = pd.DataFrame(ts, columns=["timestamp"])

    # Generate anomalies
    anom_dt, anom_arr = anomalies

    #print(anom_dt)
    # Remove anomaly datetimes from ts
    ts = ts[ts.isin(anom_dt) == False]


    # Mock traffic in normal distribution over time
    # Get hour as a float (e.g. 5:30:00 PM would be 5.5 h
    float_h = ts.hour + (ts.minute / 60) + (ts.second / 60 / 60)
    traffic_arr = normal_dist(float_h, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case)


    df.loc[df['timestamp'].isin(anom_dt) == False, use_case] = traffic_arr
    df.loc[df['timestamp'].isin(anom_dt), use_case] = anom_arr

    # Add anomaly datetimes back

    #df.loc[df['timestamp'].isin(anom_dt), use_case] = anom_arr
    df[use_case] = np.rint(df[use_case].ewm(span=8).mean())
    df[use_case] = df[use_case].clip(0)
    # Append df to collection
    df_collection.append(df)

    return df_collection


# Event-based approach
# Change event function:
# Create array with 0 to 24 for every day inside range
# Create normal dist of frequency for each hour


def create_df_event(start_ts: str, end_ts: str, device: dict, anomalies: list):
    # Initialise df list
    df_collection = []
    # Random seed for consistency
    np.random.seed(12)
    # Footfall statistics from device dict
    ff_mean = device["footfall"]["mean"]
    ff_std = device["footfall"]["std"]
    ff_min = device["footfall"]["min"]
    ff_max = device["footfall"]["max"]
    ff_peak = device["footfall"]["peak_times"]
    first_pk, second_pk = ff_peak[0], ff_peak[1]
    # Dwell data
    dwell_mean = device["footfall"]["dwell_mean"]
    dwell_sd = device["footfall"]["dwell_sd"]
    # Specify name of use case column
    use_case = "event"
    # Initalise start and end dates
    start = pd.to_datetime(start_ts)
    end = pd.to_datetime(end_ts)
    current = start
    dt_lst = []
    # Create random anomaly dates
    anom_rng = anomalies
    while current < end:
        #  anom = is_anomaly(anom_dt, current)
        # Initialise np array, after each iteration add current to array
        # Random int should depend on the hour or if in anomaly etc.

        current_h = current.hour + (current.minute / 60) + (current.second / 60 / 60)
        is_anom = is_anomaly(anom_rng, current)
        if is_anom:
            start, peak = is_anom
            weight = anomaly_weights_event(start, peak, current)
            freq_mean, freq_sd = normal_dist_anom(current_h, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case, weight)
        else:
            freq_mean, freq_sd = normal_dist(current_h, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case)
        # Returns random normal "In" occurrences of that hour
        current_ff = np.random.normal(freq_mean, freq_sd)
        # Returns passed time between two occurrences in ms.
        next_ff = 3_600_000 / current_ff
        # Increments current by adding next footfall.
        current += pd.to_timedelta(next_ff, unit="MS")
        dt_lst.append(current)

    person_in_ts = pd.to_datetime(dt_lst)
    df_event_in = pd.DataFrame(person_in_ts, columns=["timestamp"])
    df_event_in['event'] = "personIn"
    df_collection.append(df_event_in)

    # Average dwell statistics
    dw_hour_mean, dw_hour_sd = dwell_time(person_in_ts.hour, dwell_mean, dwell_sd, first_pk, second_pk)
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
        # Footfall stats
        ff_mean = device["footfall"]["mean"]
        ff_std = device["footfall"]["std"]
        ff_min = device["footfall"]["min"]
        ff_max = device["footfall"]["max"]
        ff_peak = device["footfall"]["peak_times"]
        ff_anom = device["footfall"]["anom_freq"]
        first_pk, second_pk = ff_peak[0], ff_peak[1]
        ####
        target_id = device["useCase"]
        device_id = device["deviceID"]
        use_case = use_cases[target_id]
        # Anomalies
        anomalies = random_anomaly_generator(ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case, start_ts, end_ts, ff_anom, unit="H")
        # If not event-based.
        if use_case != "event":
            # date_rng = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)

            # Concatenate low and peak times
            stamp_frames = create_df_timestamp(start_ts, end_ts, freq_ts, device, anomalies, use_case)
            df = pd.concat(stamp_frames)
        else:
            event_frames = create_df_event(start_ts, end_ts, device, anomalies)
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
            "footfall": {"peak_times": [11, 15],
                         "mean": 11,
                         "std": 3,
                         "min": -10,
                         "max": 100,
                         "anom_freq": 15}},

           {"deviceID": "2",
            "useCase": "2",
            "footfall": {"peak_times": [11, 14],
                         "mean": 4,
                         "std": 3,
                         "min": -10,
                         "max": 20,
                         "anom_freq": 15}},

           {"deviceID": "3",
            "useCase": "3",
            "footfall": {"peak_times": [10, 16],
                         "mean": 150,
                         "std": 15,
                         "min": 0,
                         "max": 20000,
                         "anom_freq": 15,
                         "dwell_mean": 1,
                         "dwell_sd": 0.3}}
           ]



start_ts = "2020-06-28"
end_ts = "now"
interval_freq = "10S"

# Create the data set
total_df = synthesise_data(devices, use_cases, start_ts, end_ts, interval_freq)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


#print(total_df.head(10000))


print(total_df.loc[(total_df["timestamp"] > "2021-05-02 08:00:00") & (total_df["timestamp"] < "2021-05-02 20:00:00")])
print(total_df.describe())

#print(total_df.query("20210607 < timestamp < 20210608"))

#print(total_df[total_df["queueing"] > 60])
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
