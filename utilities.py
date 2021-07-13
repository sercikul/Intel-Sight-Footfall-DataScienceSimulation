import datetime
import numpy as np

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



