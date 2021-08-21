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
                                  "higher_weekdays": True,
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
                                  "higher_weekdays": True,
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
                                  "higher_weekdays": True,
                                  "high_season": [12, 2],
                                  "dwell_mean": 1,
                                  "dwell_sd": 0.3}},
                    {"deviceID": "4",
                     "useCase": "1",
                     "freq_ts": "600S",
                     "footfall": {"peak_times": [12, 16],
                                  "mean": 8,
                                  "std": 2.7,
                                  "min": -1000,
                                  "max": 2_000,
                                  "anom_freq": 15,
                                  "higher_weekdays": True,
                                  "high_season": [12, 2]}}]

devices_bank = [{"deviceID": "1",
                 "useCase": "1",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [10, 14],
                              "mean": 7,
                              "std": 2,
                              "min": -1000,
                              "max": 2_000,
                              "anom_freq": 10,
                              "higher_weekdays": True,
                              "high_season": [12, 6]}},

                {"deviceID": "2",
                 "useCase": "2",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [11, 14],
                              "mean": 2,
                              "std": 1.2,
                              "min": -1000,
                              "max": 14,
                              "anom_freq": 10,
                              "higher_weekdays": True,
                              "high_season": [12, 6]}},

                {"deviceID": "3",
                 "useCase": "3",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [10, 16],
                              "mean": 35,
                              "std": 4.5,
                              "min": 0,
                              "max": 20_000,
                              "anom_freq": 12,
                              "higher_weekdays": True,
                              "high_season": [12, 6],
                              "dwell_mean": 0.6,
                              "dwell_sd": 0.15}}]

devices_park = [{"deviceID": "1",
                 "useCase": "1",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [12, 16],
                              "mean": 5,
                              "std": 1.2,
                              "min": -1000,
                              "max": 2_000,
                              "anom_freq": 5,
                              "higher_weekdays": False,
                              "high_season": [7, 6]}},

                {"deviceID": "2",
                 "useCase": "2",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [11, 16],
                              "mean": 6,
                              "std": 3.5,
                              "min": -1000,
                              "max": 30,
                              "anom_freq": 5,
                              "higher_weekdays": False,
                              "high_season": [7, 6]}},

                {"deviceID": "3",
                 "useCase": "3",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [10, 16],
                              "mean": 70,
                              "std": 9,
                              "min": 0,
                              "max": 20_000,
                              "anom_freq": 8,
                              "higher_weekdays": False,
                              "high_season": [7, 6],
                              "dwell_mean": 0.75,
                              "dwell_sd": 0.22}},
                {"deviceID": "4",
                 "useCase": "1",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [11, 15],
                              "mean": 8,
                              "std": 2.4,
                              "min": -1000,
                              "max": 2_000,
                              "anom_freq": 5,
                              "higher_weekdays": False,
                              "high_season": [7, 6]}}]

devices_mall = [{"deviceID": "1",
                 "useCase": "1",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [14, 17],
                              "mean": 13,
                              "std": 4.7,
                              "min": -1000,
                              "max": 2_000,
                              "anom_freq": 4,
                              "higher_weekdays": False,
                              "high_season": [12, 7]}},

                {"deviceID": "2",
                 "useCase": "2",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [15, 18],
                              "mean": 8,
                              "std": 4.5,
                              "min": -1000,
                              "max": 50,
                              "anom_freq": 5,
                              "higher_weekdays": False,
                              "high_season": [12, 7]}},

                {"deviceID": "3",
                 "useCase": "3",
                 "freq_ts": "600S",
                 "footfall": {"peak_times": [12, 16],
                              "mean": 90,
                              "std": 13,
                              "min": 0,
                              "max": 20_000,
                              "anom_freq": 6,
                              "higher_weekdays": False,
                              "high_season": [12, 7],
                              "dwell_mean": 2.5,
                              "dwell_sd": 0.66}}]


devices_airport = [{"deviceID": "1",
                    "useCase": "1",
                    "freq_ts": "600S",
                    "footfall": {"peak_times": [9, 16],
                                 "mean": 22,
                                 "std": 5.2,
                                 "min": -1000,
                                 "max": 2_000,
                                 "anom_freq": 20,
                                 "higher_weekdays": True,
                                 "high_season": [8, 12]}},

                   {"deviceID": "2",
                    "useCase": "2",
                    "freq_ts": "600S",
                    "footfall": {"peak_times": [11, 17],
                                 "mean": 7,
                                 "std": 4.5,
                                 "min": -1000,
                                 "max": 50,
                                 "anom_freq": 20,
                                 "higher_weekdays": True,
                                 "high_season": [8, 12]}},

                   {"deviceID": "3",
                    "useCase": "3",
                    "freq_ts": "600S",
                    "footfall": {"peak_times": [9, 16],
                                 "mean": 100,
                                 "std": 12,
                                 "min": 0,
                                 "max": 20_000,
                                 "anom_freq": 20,
                                 "higher_weekdays": True,
                                 "high_season": [8, 12],
                                 "dwell_mean": 3,
                                 "dwell_sd": 1.2}}]

# General properties

hospital_scenario = {"Yearly Seasonality": "Winter peaks, lower summers",
                     "Weekly Seasonality": "Higher weekdays, lower weekends",
                     "Daily Seasonality": "Peaks during daylight, much lower nights"}

park_scenario = {"Yearly Seasonality": "Summer peaks, lower winters",
                 "Weekly Seasonality": "Higher weekends, lower weekdays",
                 "Daily Seasonality": "Peaks during daylight, much lower nights"}

bank_scenario = {"Yearly Seasonality": "Peaks before christmas and summer holidays",
                 "Weekly Seasonality": "Higher weekdays, lower weekends",
                 "Daily Seasonality": "Peaks during daylight, much lower nights"}

mall_scenario = {"Yearly Seasonality": "Peaks before christmas and summer holidays",
                 "Weekly Seasonality": "Higher weekends, lower weekdays",
                 "Daily Seasonality": "Peaks during daylight, much lower nights"}

airport_scenario = {"Yearly Seasonality": "Peaks from summer to christmas, lower start of year",
                    "Weekly Seasonality": "Higher weekdays, lower weekends",
                    "Daily Seasonality": "Peaks during daylight, much lower nights"}

# Scenarios
scenarios = {"Sight Hospital": hospital_scenario,
             "Syde Park": park_scenario,
             "Sight National Bank": bank_scenario,
             "Sight City Mall": mall_scenario,
             "Sight International Airport": airport_scenario}

# Default data sets
scenario_devices = {"Sight Hospital": devices_hospital,
                    "Syde Park": devices_park,
                    "Sight National Bank": devices_bank,
                    "Sight City Mall": devices_mall,
                    "Sight International Airport": devices_airport}

# ADD MALL, BANK 24 hours
