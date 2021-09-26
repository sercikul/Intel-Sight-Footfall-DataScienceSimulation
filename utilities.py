from datetime import timedelta
import numpy as np
import pandas as pd
from itertools import cycle
import holidays
import json


def truncated_normal(mean, stddev, minval, maxval, size):
    """Returns truncated random normal distributed array around given mean and std"""
    return np.clip(np.random.normal(mean, stddev, size=size), minval, maxval)


def dwell_normal(mean, stddev, minval, maxval, size):
    """Returns truncated random normal distributed array around given mean and std.
    Incorporates random seed for consistent dwell statistics."""
    np.random.seed(12)
    return np.clip(np.random.normal(mean, stddev, size=size), minval, maxval)


def get_n_dates(start, end, n):
    """Randomly selects n dates within given start and end date."""
    start_u = start.value // (10 ** 9 // 1_000)
    end_u = end.value // (10 ** 9 // 1_000)
    return np.random.randint(start_u, end_u, n, dtype=np.int64)


def dwell_time(event_ts, crowd, overall_mean, overall_sd, first_peak, second_peak):
    """Returns dwell time statistics for each fake visitor as a two-tuple array."""
    # Retrieve and place weight on hours from time series.
    hour = event_ts.hour
    h_wghts = hour_weights(hour, first_peak, second_peak) + 0.5
    # Logarithmic function to depict influence of crowd on footfall
    crowdedness_wght = 1 + np.log10(crowd + 1) / 5
    # Overall dwell weight array, influenced by current crowd and hour of timestamp
    wghts = h_wghts * crowdedness_wght
    # Calculate rigorous dwell statistics in milliseconds
    mean = overall_mean * 3_600_000 * wghts
    sd = overall_sd * 3_600_000 * wghts
    return mean, sd


def hour_weights(h, first_peak, second_peak):
    """Exponential function to assign weights to the hours based on their proximity
    to the 2 scenario peaks."""
    # We are assuming a Sigma (standard deviation from the peak hours) of 2.
    sigma = 2
    # Gaussian normal distribution with factors for first peak and second peak
    hour_weights = 2 * np.exp(-(h - first_peak) ** 2 / (2 * sigma ** 2)) \
                   + 1.7 * np.exp(-(h - second_peak) ** 2 / (2 * sigma ** 2)) + 0.05
    return hour_weights


def normal_dist(hours, mean, sd, min, max, first_peak, second_peak, use_case,
                anom_weights, seasonal_factors, we_holiday_factor):
    """Embodies weights for various real-world phenomena and applies them to synthesise normal distributed
    footfall for each scenario."""
    weights = hour_weights(hours, first_peak, second_peak) * anom_weights * seasonal_factors * we_holiday_factor
    # The higher the footfall (weights) the more people are queueing, hence, we multiply.
    if use_case != "freeSeats":
        weighted_mean, weighted_sd = mean * weights, sd * np.sqrt(weights)
    else:
        # The higher the footfall the lower the availability of free seats, hence, we divide.
        weighted_mean, weighted_sd = mean / weights, sd * np.sqrt(weights)
    if use_case == "event":
        # These statistics will be used later by 'create_df_event' to construct visitor arrivals.
        return weighted_mean, weighted_sd
    else:
        # Draw a traffic array for interval-based scenarios.
        weighted_mean = np.asarray(weighted_mean)
        weighted_sd = np.asarray(weighted_sd)
        weighted_mean[weighted_mean > max] = max
        weighted_sd[weighted_sd < 1] = 1
        traffic_arr = truncated_normal(weighted_mean, weighted_sd, min, max, len(hours))
        return traffic_arr


def random_dates(start, end, n, freq, unit):
    """Creates random anomaly periods within time intervals"""
    np.random.seed(12)
    dr_lst = []
    days = (end - start).days
    # Get array of n anomaly start dates
    arr = start + pd.to_timedelta(np.random.randint(0, days * 24, n), unit=unit)
    sorted_arr = arr.sort_values()
    len_arr = len(sorted_arr)
    # Cycle through 'sorted_arr' to assign a period to each anomaly start
    start_dt = cycle(sorted_arr)
    next_dt = next(start_dt)
    step = 0
    while step < len_arr:
        step += 1
        if step < n:
            current_dt, next_dt = next_dt, next(start_dt)
        else:
            current_dt, next_dt = next_dt, end
        # Create a date range (=period) for current cycle
        dr = create_date_range(current_dt, next_dt, freq)
        dr_lst.append(dr)
    return dr_lst


def create_date_range(start_dt, next_dt, freq):
    """Creates a period within a given range of dates."""
    seconds = int(freq[:-1])
    duration = float(truncated_normal(10, 3, 1, 20, 1))
    # Adds random duration to anomaly start time to get end time,
    # and makes sure that the end time does not exceed given range.
    end_dt = min(start_dt + timedelta(hours=duration), next_dt - timedelta(seconds=seconds))
    dr = pd.date_range(start=start_dt, end=end_dt, freq=freq)
    return dr


def random_anomaly_generator(dr, start, end, n, freq, unit="H"):
    """Returns weights for all anomalies."""
    # Gets time series with random anomaly periods.
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    ts = random_dates(start, end, n, freq, unit)
    # Assigns random normal distributed weights
    weights_h = anom_weight_arr(ts, dr)
    # Caps the weights. (Max=50, Min=1)
    anom_weights = np.clip(weights_h, 1, 50)
    return anom_weights


def anomaly_weights(start, peak, dt):
    """Generates anomaly weights on normal distribution"""
    # We are assuming a sigma (hourly standard deviation from the peaks) of 2.
    # Convert to ms.
    sigma = 2 * 3_600_000
    # Peak of anomaly after anomaly start date in ms.
    peak_h = peak.hour + (peak.minute / 60) + (peak.second / 60 / 60)
    peak_ms = (peak - start).total_seconds() * 1_000
    # Difference of anomalous timestamps from anomaly start date in ms.
    anom_dt_ms = (dt - start).total_seconds() * 1_000
    # Assign higher weights if anomaly taking place in low-traffic times.
    if peak_h < 5 or peak_h > 19:
        factor = np.random.uniform(10, 20)
    else:
        factor = np.random.uniform(2, 4)
    # Normal distributed weights around anomaly peak.
    weight = np.exp(-(anom_dt_ms - peak_ms) ** 2 / (2 * sigma ** 2)) * factor
    return weight


def anom_weight_arr(anom_dt, dt):
    """Checks for all points in time series, whether it is an anomaly and weights them
    accordingly by applying 'anomaly_weights'. The outcome is an array covering the entire
    observation period, with a heavy weights on anomalies and a factor of 1 for the rest."""
    # Initialise an array of factor 1 for all timestamps
    weight_arr = np.ones(len(dt))
    # Marks all distinct anomaly sequences in entire observation window and weights
    # the affected timestamps iteratively.
    for anom_seq in anom_dt:
        start = anom_seq[0]
        end = anom_seq[-1]
        peak = start + (end - start) / 2
        in_seq = dt.isin(anom_seq)
        selected_anoms = dt[in_seq]
        anom_weights = anomaly_weights(start, peak, selected_anoms)
        not_in_seq = ~dt.isin(anom_seq)
        weight_mask = not_in_seq.astype(float)
        weight_mask[weight_mask < 1] = anom_weights
        weight_arr *= weight_mask
    return weight_arr


def get_month_diff(prev_year, current_year, next_year, current_month, month_peak):
    """Takes timestamp and retrieves the next/previous monthly peak that is closest to that
    timestamp, while taking into account yearly differences. This is important to correctly place the
    weights, when calculating proximity to peak times.

    Example: Take 08/2020 as timestamp and 01/2020 (prev) as well as 01/2021 (next) as peak months.
    Result: August 2020 is closer to January 2021 and should be weighted correspondingly. """
    # Peak of last year
    prev_year_diff = (current_year - prev_year) * 12 + (current_month - month_peak)
    # Peak of this year
    this_year_diff = current_month - month_peak
    # Peak of next year
    next_year_diff = (current_year - next_year) * 12 + (current_month - month_peak)
    return np.minimum.reduce([np.absolute(prev_year_diff),
                              np.absolute(this_year_diff),
                              np.absolute(next_year_diff)])


def seasonality_factor(first_peak, second_peak, current_month, current_year):
    """Exponential function to assign weights to the months based on their proximity
    to the 2 scenario peaks."""
    # We are assuming a Sigma (standard deviation from the peak month) of 2.
    sigma = 2
    next_year = current_year + 1
    prev_year = current_year - 1
    # Depicts monthly difference between timestamp and peak.
    month_diff_1 = get_month_diff(prev_year, current_year, next_year, current_month, first_peak)
    month_diff_2 = get_month_diff(prev_year, current_year, next_year, current_month, second_peak)
    factor = 0.65 * np.exp(-(month_diff_1) ** 2 / (2 * sigma ** 2)) + \
             0.45 * np.exp(-(month_diff_2) ** 2 / (2 * sigma ** 2)) + 0.7
    return factor


def holidays_in_uk(start_ts, end_ts):
    """Retrieves a list of UK Bank holidays within specified observation range."""
    start, end = pd.to_datetime(start_ts), pd.to_datetime(end_ts)
    n_dates = end - start
    uk_holidays = holidays.England()
    holiday_lst = [(start + timedelta(days=day)).date() for day in range(n_dates.days + 1) if
                   (start + timedelta(days=day)) in uk_holidays]
    return holiday_lst


def greedy_split(arr, n, axis=0):
    """Greedily splits an array into n blocks.
    Splits array arr along axis into n blocks such that:
        - blocks 1 through n-1 are all the same size
        - the sum of all block sizes is equal to arr.shape[axis]
        - the last block is nonempty, and not bigger than the other blocks
    Intuitively, this "greedily" splits the array along the axis by making
    the first blocks as big as possible, then putting the leftovers in the
    last block.
    Modified from: https://stackoverflow.com/questions/27609499/numpy-array-split-odd-behavior
    """
    length = arr.shape[axis]
    # compute the size of each of the first n-1 blocks
    block_size = np.ceil(length / float(n))
    # the indices at which the splits will occur
    ix = np.arange(block_size, length, block_size).astype(int)
    return np.split(arr, ix, axis)


def weekend_holiday_factor(dt, holidays, higher_weekdays):
    """Checks for each timestamp if it is a weekend/holiday and weighs them accordingly.
    All other days, i.e. business days, are unaffected and have the factor 1"""
    dt = np.array(dt, dtype="datetime64[D]")
    is_busday = np.is_busday(dt, holidays=holidays)
    holiday_dt = dt[is_busday == False]
    n_holidays = len(np.unique(holiday_dt))
    hol_arr = greedy_split(holiday_dt, n_holidays)
    # Initialise weight array
    weight_arr = np.ones(len(dt))
    # Assign random weight per date
    for i in range(len(hol_arr)):
        day_seq = hol_arr[i]
        mask = np.isin(dt, day_seq[0])
        if higher_weekdays:
            random_weight = truncated_normal(0.75, 0.05, 0.5, 0.8, size=1)
        else:
            random_weight = truncated_normal(1.25, 0.05, 1.1, 1.5, size=1)
        day_factor = np.where(mask, random_weight, 1)
        weight_arr *= day_factor
    we_hol_factor = np.where(is_busday, 1, weight_arr)
    return we_hol_factor


def weekends(start, end):
    """Retrieves all non-business dates."""
    df = pd.DataFrame({'Dates': pd.date_range(start, end)})
    busines_dates = pd.bdate_range(start, end)
    answer = df.loc[~df['Dates'].isin(busines_dates)]
    weekends = answer["Dates"].astype(str)
    return weekends.tolist()


# DATABASE UTILITIES
class CustomEncoder(json.JSONEncoder):
    """Encodes the data types and makes it JSON-compatible, allowing data to be transferred into MongoDB. Modified
    from: https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(CustomEncoder, self).default(obj)


def preprocess_for_mongo(data):
    """Pre-processes timestamp data type for MongoDB."""
    for rec in data:
        if "timestamp" in rec:
            rec["timestamp"] = rec["timestamp"].to_pydatetime().isoformat()
    data_dict = json.dumps(data, cls=CustomEncoder)
    data = json.loads(data_dict)
    return data


def retrieve_from_mongo(collection, db):
    """Fetch data from the database (for ML).
    Convert the 'footfall' collection into a Pandas format so
    that the Analytics unit can work with it."""
    if collection != db["scenario"]:
        data = collection.find()
        df = pd.DataFrame.from_records(data)
        df = df.drop(columns="_id")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    else:
        df = collection.find()
    return df


def yes_no(question):
    """Function for user to answer a yes/no question.
    Modified from: https://github.com/mitrotasios/COMP0066"""
    # Outputs 'y' or 'n' as a string, or prompts the user for another choice.
    while True:
        choice = str(input(
            f"{str(question)} Yes or No? Please type y for yes, n for No: ").strip().lower())
        acceptable_inputs = ['yes', 'no', 'nah',
                             'yeh', 'nope', 'yeah', 'y', 'n']
        if choice in acceptable_inputs:
            choice = choice[:1]
            return choice
        else:
            print(f'{choice} is an invalid input! Please enter either y or n')
            continue


def exception_handler_id(user_input: str, dataframe):
    """Function to handle user input, when user needs to input an integer index of the user menu.
    Modified from: https://github.com/mitrotasios/COMP0066"""
    try:
        if int(user_input) not in dataframe.index:
            raise ValueError
        return int(user_input)
    except ValueError:
        retry = yes_no("\nYou did not enter a valid number. You must select a number that appears in the list, "
                       "would you like to try again?")
        if retry == 'y':
            new_input = input(
                "\nPlease select one number from the left hand side of the overview: ")
            return exception_handler_id(new_input, dataframe)
        else:
            return "Invalid"


def insert_to_mongodb(total_df, collection, db, update=None):
    """Insert data into MongoDB. If new mock data is generated, all
    collections are emptied first."""
    data = preprocess_for_mongo(total_df)
    if not update:
        collection.delete_many({})
    collection.insert_many(data)
    if collection != db["scenario"] and collection != db["devices"]:
        collection.update_many({}, [{'$set': {'timestamp': {'$toDate': '$timestamp'}}}])
    return True


def cum_visitor_count(collection):
    """Python version of MongoDB query to calculate cumulative footfall."""
    collection.aggregate([
        {
            '$match': {
                'recordType': '3'
            }
        }, {
            '$addFields': {
                'value': {
                    '$cond': {
                        'if': {
                            '$eq': [
                                '$event', 'personIn'
                            ]
                        },
                        'then': 1,
                        'else': -1
                    }
                }
            }
        }, {
            '$group': {
                '_id': {
                    'time': {
                        '$toDate': {
                            '$dateToString': {
                                'format': '%Y-%m-%d %H:00:00',
                                'date': '$timestamp',
                            }
                        }
                    }},
                'value': {
                    '$sum': '$value'
                }
            }
        }, {
            '$addFields': {
                '_id': '$_id.time'
            }
        }, {
            '$sort': {
                '_id': 1
            }
        }, {
            '$group': {
                '_id': None,
                'data': {
                    '$push': '$$ROOT'
                }
            }
        }, {
            '$addFields': {
                'data': {
                    '$reduce': {
                        'input': '$data',
                        'initialValue': {
                            'total': 0,
                            'd': []
                        },
                        'in': {
                            'total': {
                                '$sum': [
                                    '$$this.value', '$$value.total'
                                ]
                            },
                            'd': {
                                '$concatArrays': [
                                    '$$value.d', [
                                        {
                                            '_id': '$$this._id',
                                            'value': '$$this.value',
                                            'runningTotal': {
                                                '$sum': [
                                                    '$$value.total', '$$this.value'
                                                ]
                                            }
                                        }
                                    ]
                                ]
                            }
                        }
                    }
                }
            }
        }, {
            '$unwind': '$data.d'
        }, {
            '$replaceRoot': {
                'newRoot': '$data.d'
            }
        }, {
            '$out': 'cumVisitorCount'
        }
    ])
    return True
