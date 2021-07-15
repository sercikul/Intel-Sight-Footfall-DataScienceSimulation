from datetime import timedelta
import numpy as np
import datetime
import pandas as pd
import random


# Convert datetime object to milliseconds
def convert_to_ms(dt):
    # Start of utc epoch
    epoch = datetime.datetime.utcfromtimestamp(0)
    ms = (dt - epoch).total_seconds() * 1000
    return int(ms)


def convert_arr_to_ms(dt):
    # Start of utc epoch
    epoch = datetime.datetime.utcfromtimestamp(0)
    ms = (dt - epoch).total_seconds() * 1000
    return ms.astype(int)

def truncated_normal(mean, stddev, minval, maxval, size):
    return np.clip(np.random.normal(mean, stddev, size=size), minval, maxval)


def ms_weights(ts):
    # We are assuming a sigma (standard deviation from the peak hours) of 2.
    # Convert to ms
    sigma = 2 * 3_600_000

    float_h = 3_600_000 * (ts.hour + (ts.minute / 60) + (ts.second / 60 / 60))
    start = float_h[0]
    end = float_h[-1]
    # Peak
    mu = (start + end) / 2
    ms_weights = np.exp(-(float_h - mu) ** 2 / (2 * sigma ** 2))

    return ms_weights


def hour_weights(h, first_peak, second_peak):
    # We are assuming a sigma (standard deviation from the peak hours) of 2.
    sigma = 2
    # Gaussian normal distribution with weights for first peak (first_mt) and second peak (second_mt)
    # This simulates the so-called "bell" curve
    hour_weights = 2 * np.exp(-(h - first_peak) ** 2 / (2 * sigma ** 2)) + 1.7 * np.exp(
        -(h - second_peak) ** 2 / (2 * sigma ** 2)) + 0.05

    return hour_weights

# Create a normal distribution numpy array
def normal_dist(hours, mean, sd, min, max, first_peak, second_peak, use_case):
    weights = hour_weights(hours, first_peak, second_peak)
    # More variance for low footfall times, less for high footfall times
    # The higher the footfall (weights) the more people are queueing, hence, we multiply
    if use_case != "freeSeats":
        weighted_mean, weighted_sd = mean * weights, sd * np.sqrt(weights)
    else:
        # The higher the footfall the lower the availability of free seats, hence, we divide
        weighted_mean, weighted_sd = mean / weights, sd * np.sqrt(weights)

    weighted_mean = np.asarray(weighted_mean)
    weighted_sd = np.asarray(weighted_sd)
    weighted_mean[weighted_mean > max] = max
    weighted_sd[weighted_sd < 1] = 1

    traffic_arr = truncated_normal(weighted_mean, weighted_sd, min, max, len(hours))

    return traffic_arr


def dwell_time(hour, overall_mean, overall_sd, first_peak, second_peak):
    # Increase weights compared to timestamp approach to allow for higher mean
    wghts = hour_weights(hour, first_peak, second_peak) + 0.5
    # dwell times and
    # Stats in ms
    mean = overall_mean * 3_600_000 * wghts
    sd = overall_sd * 3_600_000 * wghts

    return mean, sd


def anomaly_weights(float_h):
    # We are assuming a sigma (standard deviation from the peak hours) of 2.
    # Convert to ms
    sigma = 2 * 3_600_000

    # Difference between two timestamps is 10 seconds (10_000 ms)
    seq_start = float_h[0] * 3_600_000
    len_seq = len(float_h)
    seq = np.arange(seq_start, seq_start + (10_000 * len_seq), 10_000)

    # Anomaly peak pre-defined at center of time-series array
    arr_peak = len(seq) // 2

    # Peak
    mu = seq[arr_peak]
    mu_h = float_h[arr_peak]
    if mu_h < 5 or mu_h > 19:
        factor = 8
    else:
        factor = 2

    # If weight below 0, then bring it back to 1 by dividing
    weights = np.exp(-(seq - mu) ** 2 / (2 * sigma ** 2)) * factor

    return weights

def random_anomaly_generator(mean, sd, min, max, first_peak, second_peak, use_case, start, end, n, unit="H"):
    dr_lst = []
    anomaly_lst = []
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    days = (end - start).days + 1
    arr = start + pd.to_timedelta(np.random.randint(0, days * 24, n), unit=unit)
    sorted_arr = arr.sort_values()
    for i in sorted_arr:
        duration = float(truncated_normal(4, 1.5, 0.5, 10, 1))
        dr = pd.date_range(start=i, end=i + timedelta(hours=duration), freq="10S")
        dr_lst.append(dr)
        # Get hour of ts
        float_h = dr.hour + (dr.minute / 60) + (dr.second / 60 / 60)
        # Weights and normal dist
        anom_weights = anomaly_weights(float_h)
        anom_weights = np.clip(anom_weights, 1, 8)
        normal_dst = normal_dist(float_h, mean, sd, min, max, first_peak, second_peak, use_case)
        # Anomaly values
        # Bring negative values to 0 in order to avoid multiplication of negative values
        anomaly = anom_weights * np.clip(normal_dst, 0, max)
        # Append to anomaly lst
        anomaly_lst.append(anomaly)

    anom_dt = dr_lst[0].union_many(dr_lst[1:])

    # Turn anomaly lst to array
    anomalies = np.asarray(anomaly_lst)
    anom_arr = np.concatenate(anomalies)
    return anom_dt, anom_arr

