import datetime
from scipy.stats import truncnorm
import numpy as np


# Convert datetime object to milliseconds
def convert_to_ms(dt):
    # Start of utc epoch
    epoch = datetime.datetime.utcfromtimestamp(0)
    ms = (dt - epoch).total_seconds() * 1000
    return int(ms)


def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


def hour_weights(h, first_peak, second_peak):
    # We are assuming a sigma (standard deviation from the peak hours) of 2.
    sigma = 2
    # Gaussian normal distribution with weights for first peak (2) and second peak (1.7)
    # This simulates the so-called "bell" curve
    hour_weights = 2 * np.exp(-(h - first_peak) ** 2 / (2 * sigma ** 2)) + 1.7 * np.exp(
        -(h - second_peak) ** 2 / (2 * sigma ** 2)) + 0.05
    return hour_weights


# Create a normal distribution numpy array
def normal_dist(time_series, mean, sd, min, max, first_peak, second_peak):
    weights = hour_weights(time_series.hour, first_peak, second_peak)
    # More variance for low footfall times, less for high footfall times
    weighted_mean, weighted_sd = mean * weights, sd * np.sqrt(weights)
    traffic = get_truncated_normal(mean=weighted_mean, sd=weighted_sd, low=min, upp=max)
    traffic_arr = traffic.rvs(len(time_series))

    return traffic_arr
