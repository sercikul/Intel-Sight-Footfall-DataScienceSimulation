from datetime import datetime
from dateutil.relativedelta import relativedelta

# Devices (venues) have different footfall means/stds.
attributes = ['timestamp', 'deviceID', 'targetID', 'queueing', 'freeSeats', 'event']

# Target use cases
use_cases = {"1": "queueing", "2": "freeSeats", "3": "event"}

# Time Range
start_ts = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d")
end_ts = "now"

# Default device parameters
devices_hospital = [{"deviceID": "1",
                     "useCase": "1",
                     "freq_ts": "600S",
                     "footfall": {"peak_times": [11, 15],
                                  "mean": 11,
                                  "std": 3,
                                  "min": -1000,
                                  "max": 2_000,
                                  "anom_freq": 15,
                                  "high_season": [12, 2]}},

                    {"deviceID": "2",
                     "useCase": "2",
                     "freq_ts": "600S",
                     "footfall": {"peak_times": [11, 14],
                                  "mean": 4,
                                  "std": 3,
                                  "min": -1000,
                                  "max": 20,
                                  "anom_freq": 15,
                                  "high_season": [12, 2]}},

                    {"deviceID": "3",
                     "useCase": "3",
                     "freq_ts": "600S",
                     "footfall": {"peak_times": [10, 16],
                                  "mean": 50,
                                  "std": 7,
                                  "min": 0,
                                  "max": 20_000,
                                  "anom_freq": 15,
                                  "high_season": [12, 2],
                                  "dwell_mean": 1,
                                  "dwell_sd": 0.3}}]

devices_bank = [{"deviceID": "1",
                 "useCase": "1",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [11, 15],
                              "mean": 11,
                              "std": 3,
                              "min": -1000,
                              "max": 2_000,
                              "anom_freq": 15,
                              "high_season": [12, 2]}},

                {"deviceID": "2",
                 "useCase": "2",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [11, 14],
                              "mean": 4,
                              "std": 3,
                              "min": -1000,
                              "max": 20,
                              "anom_freq": 15,
                              "high_season": [12, 2]}},

                {"deviceID": "3",
                 "useCase": "3",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [10, 16],
                              "mean": 50,
                              "std": 7,
                              "min": 0,
                              "max": 20_000,
                              "anom_freq": 15,
                              "high_season": [12, 2],
                              "dwell_mean": 1,
                              "dwell_sd": 0.3}}]

devices_park = [{"deviceID": "1",
                 "useCase": "1",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [11, 15],
                              "mean": 11,
                              "std": 3,
                              "min": -1000,
                              "max": 2_000,
                              "anom_freq": 15,
                              "high_season": [12, 2]}},

                {"deviceID": "2",
                 "useCase": "2",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [11, 14],
                              "mean": 4,
                              "std": 3,
                              "min": -1000,
                              "max": 20,
                              "anom_freq": 15,
                              "high_season": [12, 2]}},

                {"deviceID": "3",
                 "useCase": "3",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [10, 16],
                              "mean": 50,
                              "std": 7,
                              "min": 0,
                              "max": 20_000,
                              "anom_freq": 15,
                              "high_season": [12, 2],
                              "dwell_mean": 1,
                              "dwell_sd": 0.3}}]

# General properties

hospital_scenario = {"Yearly Seasonality": "Higher in winter, lower in summer",
                     "Weekly Seasonality": "Higher on weekdays, lower on weekends",
                     "Daily Seasonality": "Peaks during daylight, much less in night",
                     "Only Business Days": False}

bank_scenario = {"Yearly Seasonality": "No seasonal differences",
                 "Weekly Seasonality": "Only weekdays",
                 "Daily Seasonality": "Only on working hours",
                 "Only Business Days": True}

park_scenario = {"Yearly Seasonality": "Higher in summer, lower in winter",
                 "Weekly Seasonality": "Higher on weekends, lower on weekdays",
                 "Daily Seasonality": "Peaks during daylight, much less in night",
                 "Only Business Days": False}


# Scenarios
scenarios = {"Sight Hospital": hospital_scenario,
             "Sight Central Bank": bank_scenario,
             "Syde Park": park_scenario}

# Default data sets
scenario_devices = {"Sight Hospital": devices_hospital,
                   "Sight Central Bank": devices_bank,
                   "Syde Park": devices_park}
