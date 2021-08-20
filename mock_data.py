# import rapidjson as json
from numpy.random import choice
import time
from utilities import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
import sys
np.set_printoptions(threshold=sys.maxsize)



def create_df_timestamp(ts, device: dict, anom_weights, uk_holidays: list, use_case: str):
    # Footfall statistics from device dict
    ff_mean = device["footfall"]["mean"]
    ff_std = device["footfall"]["std"]
    ff_min = device["footfall"]["min"]
    ff_max = device["footfall"]["max"]
    ff_peak = device["footfall"]["peak_times"]
    first_pk, second_pk = ff_peak[0], ff_peak[1]
    # Seasonality statistcs
    first_seasonal_pk, second_seasonal_pk = device["footfall"]["high_season"][0], device["footfall"]["high_season"][1]
    # Initialise df
    df = pd.DataFrame(ts, columns=["timestamp"])

    # Get hour as a float (e.g. 5:30:00 PM would be 5.5 h
    float_h = ts.hour + (ts.minute / 60) + (ts.second / 60 / 60)
    float_m = ts.month + (ts.day / 31) + (float_h / 24 / 31)
    seasonal_factors = seasonality_factor(first_seasonal_pk, second_seasonal_pk, float_m, ts.year)
    we_holiday_factors = weekend_holiday_factor(ts, uk_holidays)
    traffic_arr = normal_dist(float_h, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk,
                              use_case, anom_weights, seasonal_factors, we_holiday_factors)

    df[use_case] = traffic_arr

    # Add anomaly datetimes back
    # Uncomment if timestamp frequencies very low
    df[use_case] = np.rint(df[use_case].ewm(span=3).mean())
    df[use_case] = df[use_case].clip(0)
    df[use_case] = df[use_case].astype(pd.Int64Dtype())


    return df


# Event-based approach
# Change event function:
# Create array with 0 to 24 for every day inside range
# Create normal dist of frequency for each hour

def create_df_event(dr, anom_weights, uk_holidays: list, device: dict):
    # Initialise df list
    st_time = time.time()
    # Random seed for consistency
    np.random.seed(12)
    # Footfall statistics from device dict
    ff_mean = device["footfall"]["mean"]
    ff_std = device["footfall"]["std"]
    ff_min = device["footfall"]["min"]
    ff_max = device["footfall"]["max"]
    ff_peak = device["footfall"]["peak_times"]
    first_pk, second_pk = ff_peak[0], ff_peak[1]
    # Seasonality statistics
    first_seasonal_pk, second_seasonal_pk  = device["footfall"]["high_season"][0], device["footfall"]["high_season"][1]
    # Dwell data
    dwell_mean = device["footfall"]["dwell_mean"]
    dwell_sd = device["footfall"]["dwell_sd"]
    # Specify name of use case column
    use_case = "event"
    dr_h = dr.hour + (dr.minute / 60)
    # Per Hour on one day
    dr_m = dr.month + (dr.day / 31) + (dr_h / 24 / 31)
    # Get hour as a float (e.g. 5:30:00 PM would be 5.5 h
    seasonal_factors = seasonality_factor(first_seasonal_pk, second_seasonal_pk, dr_m, dr.year)
    # Weekends and holidays
    we_holiday_factors = weekend_holiday_factor(dr, uk_holidays)
    # Normal distribution
    freq_mean, freq_sd = normal_dist(dr_h, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case,
                                     seasonal_factors, anom_weights, we_holiday_factors)
    dt_lst = []
    crowd_lst = []
    for i in range(len(dr) - 1):
        # Returns random normal "In" occurrences of that hour
        # Hourly Footfall weight given to date array
        current_ff = np.clip(np.random.normal(freq_mean[i], freq_sd[i]), 0, 100_000_000_000)
        # Bring to 10 minutes
        current_ff_min = int(round(current_ff / 6))
        dt_rng = get_n_dates(dr[i], dr[i + 1], n=current_ff_min)
        dt_lst.append(dt_rng)
        # Crowd
        crowd_arr = np.full(shape=current_ff_min, fill_value=current_ff_min)
        crowd_lst.append(crowd_arr)

    # DT
    dt_arr = np.array(dt_lst, dtype=object)
    dt_conc = np.concatenate(dt_arr)
    event_dt = pd.to_datetime(dt_conc, unit="ms").sort_values()

    person_in_ts = pd.to_datetime(event_dt)
    df_event_in = pd.DataFrame(person_in_ts, columns=["timestamp"])
    df_event_in['event'] = "personIn"

    # Crowd
    crowd_arr = np.array(crowd_lst, dtype=object)
    crowd = np.concatenate(crowd_arr)

    # Average dwell statistics
    dw_hour_mean, dw_hour_sd = dwell_time(person_in_ts, crowd, dwell_mean, dwell_sd, first_pk, second_pk)
    dwell_time_ms = dwell_normal(dw_hour_mean, dw_hour_sd, 1000, (100 * 3_600_000), size=len(person_in_ts))
    out_occurrences = person_in_ts + dwell_time_ms.astype('timedelta64[ms]')
    person_out_ts = pd.to_datetime(out_occurrences, unit='ms')
    df_event_out = pd.DataFrame(person_out_ts, columns=["timestamp"])
    df_event_out['event'] = "personOut"
    # Cut personOut events that were synthesised for future
    df_event = pd.concat([df_event_in, df_event_out])
    df_event = df_event.loc[(df_event["timestamp"] <= "now")]
    end_time = time.time()
    #print("events time: ", end_time-st_time)

    return df_event


# Specify devices, start, end as well as frequency of time series
# Interval - timestamp approach.

# Synthesise data for use cases 1 and 2.

# CLARIFY IF ONE DEVICEID FOR ONE TARGET
def synthesise_data(devices: list, use_cases: dict, start_ts: str, end_ts: str, update_ts=None):
    st_time = time.time()
    device_lst = []
    # English Bank Holidays
    uk_holidays = holidays_in_uk(start_ts, end_ts)
    # Devices for loop

    for device in devices:
        # Seasonality
        # Id's
        target_id = device["useCase"]
        device_id = device["deviceID"]
        use_case = use_cases[target_id]
        # FF anomalies
        ff_anom = device["footfall"]["anom_freq"]
        # Ts Freq
        freq_ts = device["freq_ts"]
        ts = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)
        # Create anomalies
        # Check what happens if you set anom to 0
        if ff_anom > 0:
            anom_weights = random_anomaly_generator(ts, start_ts, end_ts, ff_anom, freq_ts)
        else:
            anom_weights = 1
        # If not event-based.
        if use_case != "event":
            # Concatenate low and peak times
            df = create_df_timestamp(ts, device, anom_weights, uk_holidays, use_case)
        else:
            df = create_df_event(ts, anom_weights, uk_holidays, device)

        # Bring in other attributes
        df['targetID'] = target_id
        df['deviceID'] = device_id

        # Append device-specific df to device_lst
        df = df.sort_values(["timestamp", "deviceID"], ascending=(True, True))
        # If exisitng data is updated, then the most recently collected datetime 'updated_ts' is
        # passed as parameter and the updated mock data is filtered, such that it only contains
        # data from the most recent datetime onwards until now.
        if update_ts:
            df = df[df["timestamp"] > update_ts]
        device_lst += df.to_dict("records")

    df_total = device_lst
    end_time = time.time()
    #print("overall time: ", end_time - st_time)

    return df_total


# Parameters
# Execute

#if __name__ == "__main__":
 #   # Devices (venues) have different footfall means/stds.
  #  attributes = ['timestamp', 'deviceID', 'targetID', 'queueing', 'freeSeats', 'event']

    # Target use cases
  #  use_cases = {"1": "queueing",
   #              "2": "freeSeats",
 #                "3": "event"}
#
   # devices_hospital = [{"deviceID": "1",
  #                       "useCase": "1",
    #                    "freq_ts": "600S",
     #                   "footfall": {"peak_times": [11, 15],
      #                               "mean": 11,
       #                              "std": 3,
        #                             "min": -1000,
         #                            "max": 2_000,
          #                           "anom_freq": 15,
           #                          "high_season": [12, 2]}},
#
 #                       {"deviceID": "2",
  #                       "useCase": "2",
   #                      "freq_ts": "600S",
    #                     "footfall": {"peak_times": [11, 14],
     ##                                 "mean": 4,
       #                               "std": 3,
           #                           "min": -1000,
        #                              "max": 20,
         #                             "anom_freq": 15,
          #                            "high_season": [12, 2]}},

            #            {"deviceID": "3",
              #           "useCase": "3",
             #            "freq_ts": "600S",
                #         "footfall": {"peak_times": [10, 16],
               #                       "mean": 50,
                 #                     "std": 7,
                   #                   "min": 0,
                  #                    "max": 20_000,
                     #                 "anom_freq": 15,
                    #                  "high_season": [12, 2],
                      #                "dwell_mean": 1,
 #                                     "dwell_sd": 0.3}}]
#
  #  start_ts = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d")
   # end_ts = "now"

    # Create the data set
    #total_df = synthesise_data(devices_hospital, use_cases, start_ts, end_ts)

#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.width', None)
#pd.set_option('display.max_colwidth', -1)


#print(total_df)


#print(total_df.loc[(total_df["timestamp"] > "2020-11-11 11:00:00") & (total_df["timestamp"] < "2020-11-11 20:00:00")])
#print(total_df.describe())

#print(total_df.query("20210623 < timestamp < 20210624"))

#06/22-06/24
#print(total_df[total_df["queueing"] > 60])
# Convert to JSON

# df_json = total_df.to_json(orient="records", date_format="iso")

# Pretty-print json file to check data.

# parsed = json.loads(df_json)
# json_file = json.dumps(parsed, indent=4)

# print(total_df)
# print(json_file)
# print(df_json)
## Test if realistic


# Compare number of personIn with personOut
#person_in_df = total_df[total_df["event"] == "personIn"]
#person_out_df = total_df[total_df["event"] == "personOut"]

# print(total_df)
#print(person_out_df)
#print(person_in_df)
