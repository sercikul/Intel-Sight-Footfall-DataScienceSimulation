import pandas as pd
import numpy as np
import calendar
from datetime import datetime
import random

# Event data
# Normal distribution per venue regarding time ?

# Do function where you can specify all deviceIDs.

# targets = {
#     '1':
#     '2':
#     '3':
#     '4':
# }

attributes = ['targetID', 'deviceID', 'timestamp', 'queueing', 'freeSeats', 'event']
#df = pd.DataFrame(columns = attributes)

#df['data'] = np.random.randint(0, 100, size=(len(date_rng)))

# Specify devices, start, end as well as frequency of time series
# Interval - timestamp approach.
def synthesise_data(devices, start_ts, end_ts, freq_ts):
    target_id = "1"
    device_lst = []
    # Devices for loop
    for i in devices:
        date_rng = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)
        filter_peak_time = (date_rng.hour < 20) & (date_rng.hour > 7)
        peak_times = date_rng[filter_peak_time]

        peak_times_df = pd.DataFrame(peak_times, columns=['timestamp'])
        high_traffic = np.random.normal(loc=20, scale=4, size=(len(peak_times_df)))
        peak_times_df['queueing'] = high_traffic.astype(int)

        # Non-peak time footfall
        filter_low_time = (date_rng.hour > 19) | (date_rng.hour < 8)
        low_times = date_rng[filter_low_time]

        low_times_df = pd.DataFrame(low_times, columns=['timestamp'])
        low_traffic = np.random.normal(loc=8, scale=1, size=(len(low_times_df)))
        low_times_df['queueing'] = low_traffic.astype(int)

        # Concatenate low and peak times
        frames = [low_times_df, peak_times_df]
        df = pd.concat(frames)

        # Bring in other attributes
        df['targetID'] = target_id
        df['deviceID'] = i

        # Append device-specific df to device_lst
        device_lst.append(df)

    # sort dataframe

    # Concat the df in the device_lst
    df_total = pd.concat(device_lst)

    df_total = df_total.sort_values(by = 'timestamp')

    return df_total.head(50)



print(synthesise_data(["1", "2", "3", "4"], '28/6/2020', 'now', "10S"))

#print(df)