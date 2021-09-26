from numpy.random import choice
from utilities import *


def create_df_timestamp(ts, scenario: dict, anom_weights, uk_holidays: list, use_case: str):
    """Creates synthetic data for interval-based scenarios (queueing, free seats)"""
    # Retrieve footfall statistics from scenario dict
    ff_mean = scenario["footfall"]["mean"]
    ff_std = scenario["footfall"]["std"]
    ff_min = scenario["footfall"]["min"]
    ff_max = scenario["footfall"]["max"]
    ff_peak = scenario["footfall"]["peak_times"]
    ff_higher_wd = scenario["footfall"]["higher_weekdays"]
    # First and Second Hourly Peak
    first_pk, second_pk = ff_peak[0], ff_peak[1]
    # First and Second Monthly Peak
    first_seasonal_pk, second_seasonal_pk = scenario["footfall"]["high_season"][0], scenario["footfall"]["high_season"][1]
    # Initialise the data frame
    df = pd.DataFrame(ts, columns=["timestamp"])
    # Get hour as a float number to calc. with (e.g. 5:30:00 PM would be 5.5 h)
    float_h = ts.hour + (ts.minute / 60) + (ts.second / 60 / 60)
    float_m = ts.month + (ts.day / 31) + (float_h / 24 / 31)
    seasonal_factors = seasonality_factor(first_seasonal_pk, second_seasonal_pk, float_m, ts.year)
    we_holiday_factors = weekend_holiday_factor(ts, uk_holidays, ff_higher_wd)
    traffic_arr = normal_dist(float_h, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk,
                              use_case, anom_weights, seasonal_factors, we_holiday_factors)
    # Assign traffic array to use case - specific column
    df[use_case] = traffic_arr
    df[use_case] = np.rint(df[use_case].ewm(span=3).mean())
    df[use_case] = df[use_case].clip(0)
    df[use_case] = df[use_case].astype(pd.Int64Dtype())
    return df


def create_df_event(dr, anom_weights, uk_holidays: list, scenario: dict, update_ts: dict):
    """Creates synthetic data for event-based scenarios (event)"""
    # Random seed for consistent randomisation
    np.random.seed(12)
    # Retrieve footfall statistics from scenario dict
    ff_mean = scenario["footfall"]["mean"]
    ff_std = scenario["footfall"]["std"]
    ff_min = scenario["footfall"]["min"]
    ff_max = scenario["footfall"]["max"]
    ff_peak = scenario["footfall"]["peak_times"]
    ff_higher_wd = scenario["footfall"]["higher_weekdays"]
    # First and Second Hourly Peak
    first_pk, second_pk = ff_peak[0], ff_peak[1]
    # First and Second Monthly Peak
    first_seasonal_pk, second_seasonal_pk = scenario["footfall"]["high_season"][0], scenario["footfall"]["high_season"][1]
    # Dwell-Time Statistics: Determines each visitor's duration of stay
    dwell_mean = scenario["footfall"]["dwell_mean"]
    dwell_sd = scenario["footfall"]["dwell_sd"]
    use_case = "event"
    dr_h = dr.hour + (dr.minute / 60)
    # Per Hour on one day
    dr_m = dr.month + (dr.day / 31) + (dr_h / 24 / 31)
    # Get hour as a float (e.g. 5:30:00 PM would be 5.5 h)
    seasonal_factors = seasonality_factor(first_seasonal_pk, second_seasonal_pk, dr_m, dr.year)
    # Weekend and holiday factors
    we_holiday_factors = weekend_holiday_factor(dr, uk_holidays, ff_higher_wd)
    # Normal-distributed visitor traffic
    freq_mean, freq_sd = normal_dist(dr_h, ff_mean, ff_std, ff_min, ff_max, first_pk, second_pk, use_case,
                                     seasonal_factors, anom_weights, we_holiday_factors)
    dt_lst = []
    crowd_lst = []
    for i in range(len(dr) - 1):
        # Assigns a random crowd to each iteration (time interval)
        current_ff = np.clip(np.random.normal(freq_mean[i], freq_sd[i]), 0, 100_000_000_000)
        # Divide hourly time series by 6 to make 10-minute intervals (more dynamics within hour)
        current_ff_min = int(round(current_ff / 6))
        dt_rng = get_n_dates(dr[i], dr[i + 1], n=current_ff_min)
        dt_lst.append(dt_rng)
        # Make an array with crowd statistics
        crowd_arr = np.full(shape=current_ff_min, fill_value=current_ff_min)
        crowd_lst.append(crowd_arr)
    # Processing of time series data
    dt_arr = np.array(dt_lst, dtype=object)
    # If time series is empty, then return empty data frame
    if not dt_arr.any():
        return pd.DataFrame(columns=["timestamp", "event"])
    dt_conc = np.concatenate(dt_arr)
    event_dt = pd.to_datetime(dt_conc, unit="ms").sort_values()
    # Assign "personIn" text variable to each timestamp in series
    person_in_ts = pd.to_datetime(event_dt)
    df_event_in = pd.DataFrame(person_in_ts, columns=["timestamp"])
    if update_ts:
        last_event_dt = update_ts["last_n_person_in"]
        df_last_event_in = pd.DataFrame(last_event_dt, columns=["timestamp"])
        df_event_in = pd.concat([df_last_event_in, df_event_in])
        df_event_in = df_event_in.reset_index(drop=True)
        df_event_in = df_event_in.sort_values("timestamp", ascending=True)
        person_in_ts = pd.concat([last_event_dt, pd.Series(person_in_ts)])
        person_in_ts = pd.DatetimeIndex(person_in_ts.values)
        last_n = np.ones(len(last_event_dt))
        crowd_lst.insert(0, last_n)

    df_event_in['event'] = "personIn"
    # Concatenate the crowd arrays of each iteration (interval) into one general array
    crowd_arr = np.array(crowd_lst, dtype=object)
    crowd = np.concatenate(crowd_arr)
    # Get average dwell-time for each visitor
    dw_hour_mean, dw_hour_sd = dwell_time(person_in_ts, crowd, dwell_mean, dwell_sd, first_pk, second_pk)
    dwell_time_ms = dwell_normal(dw_hour_mean, dw_hour_sd, 1000, (100 * 3_600_000), size=len(person_in_ts))
    out_occurrences = person_in_ts + dwell_time_ms.astype('timedelta64[ms]')
    person_out_ts = pd.to_datetime(out_occurrences, unit='ms')
    df_event_out = pd.DataFrame(person_out_ts, columns=["timestamp"])
    df_event_out['event'] = "personOut"
    # Cut 'personOut' events that were synthesised for future
    df_event = pd.concat([df_event_in, df_event_out])
    df_event = df_event.loc[(df_event["timestamp"] <= "now")]

    return df_event


def synthesise_data(scenarios: list, use_cases: dict, start_ts: str, end_ts: str, update_ts=None):
    """Creates synthetic data for each scenario by wrapping the helper functions for interval-based
    and event-based recording type"""
    scenario_lst = []
    # Gets English Bank Holidays
    uk_holidays = holidays_in_uk(start_ts, end_ts)
    for scenario in scenarios:
        # Assign deviceID and recordType
        record_type = scenario["useCase"]
        device_id = scenario["_id"]
        use_case = use_cases[record_type]
        # Get number of anomalies in observation period
        ff_anom = scenario["footfall"]["anom_freq"]
        # Time-series frequency and range of scenario
        freq_ts = scenario["freq_ts"]
        ts = pd.date_range(start=start_ts, end=end_ts, freq=freq_ts)
        # Generate random anomalies for new mock data. Anomalies are not portrayed in updates.
        if ff_anom > 0 and update_ts is None:
            anom_weights = random_anomaly_generator(ts, start_ts, end_ts, ff_anom, freq_ts)
        else:
            anom_weights = 1
        if use_case != "event":
            df = create_df_timestamp(ts, scenario, anom_weights, uk_holidays, use_case)
        else:
            df = create_df_event(ts, anom_weights, uk_holidays, scenario, update_ts)
        # Assign remaining collection attributes
        df['recordType'] = record_type
        df['deviceID'] = device_id
        # Append device-specific data frame to scenario_lst
        df = df.sort_values(["timestamp", "deviceID"], ascending=(True, True))
        # Update Functionality
        if update_ts:
            df = df[df["timestamp"] > update_ts["last_ts"]]
        scenario_lst += df.to_dict("records")
    df_total = scenario_lst
    return df_total
