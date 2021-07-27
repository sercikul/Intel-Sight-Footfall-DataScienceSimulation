from datetime import timedelta
import numpy as np
import datetime
from datetime import date
import pandas as pd
from itertools import cycle
import holidays
import time


def truncated_normal(mean, stddev, minval, maxval, size):
    st_time = time.time()
    a = np.clip(np.random.normal(mean, stddev, size=size), minval, maxval)
    end_time = time.time()
    return a

def get_n_dates(start, end, n):
    start_u = start.value// (10**9 // 1_000)
    end_u = end.value// (10**9 // 1_000)
    return np.random.randint(start_u, end_u, n, dtype=np.int64)


def hour_weights(h, first_peak, second_peak):
    # We are assuming a sigma (standard deviation from the peak hours) of 2.
    st_time = time.time()
    sigma = 2
    # Gaussian normal distribution with weights for first peak (first_mt) and second peak (second_mt)
    # This simulates the so-called "bell" curve
    hour_weights = 2 * np.exp(-(h - first_peak) ** 2 / (2 * sigma ** 2)) + 1.7 * np.exp(
        -(h - second_peak) ** 2 / (2 * sigma ** 2)) + 0.05
    end_time = time.time()
    return hour_weights


def dwell_time(hour, overall_mean, overall_sd, first_peak, second_peak):
    # Increase weights compared to timestamp approach to allow for higher mean
    st_time = time.time()
    wghts = hour_weights(hour, first_peak, second_peak) + 0.5
    # dwell times and
    # Stats in ms
    mean = overall_mean * 3_600_000 * wghts
    sd = overall_sd * 3_600_000 * wghts
    end_time = time.time()
    return mean, sd


def normal_dist(hours, mean, sd, min, max, first_peak, second_peak, use_case, anom_weights,
                seasonal_factors, we_holiday_factor):
    # np.random.seed(12)
    st_time = time.time()
    weights = hour_weights(hours, first_peak, second_peak) * anom_weights * seasonal_factors * we_holiday_factor
    # More variance for low footfall times, less for high footfall times
    # The higher the footfall (weights) the more people are queueing, hence, we multiply
    if use_case != "freeSeats":
        weighted_mean, weighted_sd = mean * weights, sd * np.sqrt(weights)
    else:
        # The higher the footfall the lower the availability of free seats, hence, we divide
        weighted_mean, weighted_sd = mean / weights, sd * np.sqrt(weights)

    if use_case == "event":
        end_time = time.time()
        return weighted_mean, weighted_sd

    else:
        weighted_mean = np.asarray(weighted_mean)
        weighted_sd = np.asarray(weighted_sd)
        weighted_mean[weighted_mean > max] = max
        weighted_sd[weighted_sd < 1] = 1
        traffic_arr = truncated_normal(weighted_mean, weighted_sd, min, max, len(hours))
        end_time = time.time()
        return traffic_arr


def anomaly_weights(float_h):
    # We are assuming a sigma (standard deviation from the peak hours) of 2.
    # Convert to ms
    st_time = time.time()
    sigma = 2 * 3_600_000

    # Difference between two timestamps is 10 seconds (10_000 ms)
    seq_start = 0
    len_seq = len(float_h)
    seq = np.arange(seq_start, seq_start + (10_000 * len_seq), 10_000)

    # Anomaly peak pre-defined at center of time-series array
    arr_peak = len(seq) // 2

    # Peak
    mu = seq[arr_peak]
    mu_h = float_h[arr_peak]
    if mu_h < 5 or mu_h > 19:
        factor = np.random.uniform(10, 20)
    else:
        factor = np.random.uniform(2, 4)

    # If weight below 0, then bring it back to 1 by dividing
    weights = np.exp(-(seq - mu) ** 2 / (2 * sigma ** 2)) * factor

    end_time = time.time()
    return weights


# Generate n random dates within time range
def random_dates(start, end, n, unit):
    st_time = time.time()
    np.random.seed(12)
    dr_lst = []
    float_ts_lst = []
    start_end_lst = []
    days = (end - start).days
    arr = start + pd.to_timedelta(np.random.randint(0, days * 24, n), unit=unit)
    sorted_arr = arr.sort_values()
    len_arr = len(sorted_arr)
    # get start date of anomaly
    start_dt = cycle(sorted_arr)
    next_dt = next(start_dt)
    step = 0
    while step < len_arr:
        step += 1
        if step < 15:
            current_dt, next_dt = next_dt, next(start_dt)
        else:
            current_dt, next_dt = next_dt, end
        dr = create_date_range(current_dt, next_dt, "10S")
        dr_lst.append(dr)

    end_time = time.time()
    return dr_lst


# Generate range from random date
def create_date_range(start_dt, next_dt, freq):
    st_time = time.time()
    duration = float(truncated_normal(10, 3, 1, 20, 1))
    end_dt = min(start_dt + timedelta(hours=duration), next_dt - timedelta(seconds=10))
    dr = pd.date_range(start=start_dt, end=end_dt, freq=freq)
    end_time = time.time()
    return dr


# Generate mean and std in case there is an anomaly in footfall going on.
# Generates an array for timestamp, and tuple (mean, std) for event data.


def random_anomaly_generator(dr, start, end, n, unit="H"):
    st_time = time.time()
    # Regel das mit random seed 10
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    ts = random_dates(start, end, n, unit)
    # Weights and normal dist
    weights_h = anom_weight_arr(ts, dr)
    anom_weights = np.clip(weights_h, 1, 50)
    end_time = time.time()
    return anom_weights


def anomaly_weights_event(start, peak, event_dt):
    # We are assuming a sigma (standard deviation from the peak hours) of 2.
    # Convert to ms
    st_time = time.time()
    sigma = 2 * 3_600_000
    # Peak
    peak_h = peak.hour + (peak.minute / 60) + (peak.second / 60 / 60)
    # Start - Peak difference
    # Time starts at 0 ms
    # peak ms
    peak_ms = (peak - start).total_seconds() * 1_000

    # Event date time
    #  print(event_dt)
    event_ms = (event_dt - start).total_seconds() * 1_000

    if peak_h < 5 or peak_h > 19:
        factor = np.random.uniform(10, 20)
    else:
        factor = np.random.uniform(2, 4)

    # If weight below 0, then bring it back to 1 by dividing
    weight = np.exp(-(event_ms - peak_ms) ** 2 / (2 * sigma ** 2)) * factor
    end_time = time.time()
    return weight


def anom_weight_arr(anom_dt, dt):
    # Returns np array indicating whether index is an anomaly
    # Concat list to one array and use as mask for whole range
    weight_arr = np.ones(len(dt))
    for anom_seq in anom_dt:
        start = anom_seq[0]
        end = anom_seq[-1]
        peak = start + (end - start) / 2
        in_seq = dt.isin(anom_seq)
        selected_anoms = dt[in_seq]
        anom_weights = anomaly_weights_event(start, peak, selected_anoms)
        # Returns True for anomalies that are NOT in the current sequence, False otherwise
        not_in_seq = ~dt.isin(anom_seq)
        # Turn to int
        weight_mask = not_in_seq.astype(float)
        weight_mask[weight_mask < 1] = anom_weights
        weight_arr *= weight_mask

    return weight_arr


def seasonality_factor(first_peak, second_peak, current_month, current_year):
    st_time = time.time()
    # In months
    sigma = 2
    # To depict correct month difference in case events are in different years
    month_diff_1 = (current_year - first_peak[0]) * 12 + (current_month - first_peak[1])
    month_diff_2 = (current_year - second_peak[0]) * 12 + (current_month - second_peak[1])
    factor = 0.65 * np.exp(-(month_diff_1) ** 2 / (2 * sigma ** 2)) + \
             0.45 * np.exp(-(month_diff_2) ** 2 / (2 * sigma ** 2)) + 0.7
    end_time = time.time()
    return factor


def holidays_in_uk(start_ts, end_ts):
    st_time = time.time()
    start, end = pd.to_datetime(start_ts), pd.to_datetime(end_ts)
    n_dates = end - start
    uk_holidays = holidays.England()
    holiday_lst = [(start + timedelta(days=day)).date() for day in range(n_dates.days + 1) if
                   (start + timedelta(days=day)) in uk_holidays]
    end_time = time.time()
    return holiday_lst


def weekend_holiday_factor(dt, holidays):
    dt = np.array(dt, dtype="M8[D]")
    st_time = time.time()
    is_busday = np.is_busday(dt, holidays=holidays)
    # Non-working days
    # Make customisable when introducing inputs to program
    we_hol_factor = np.where(is_busday, 1, truncated_normal(0.7, 0.2, 0.4, 1, size=len(is_busday)))
    return we_hol_factor
