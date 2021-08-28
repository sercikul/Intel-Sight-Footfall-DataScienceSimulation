from datetime import datetime
from dateutil.relativedelta import relativedelta

# Devices (venues) have different footfall means/stds.
#attributes = ['timestamp', 'deviceID', 'recordType', 'queueing', 'freeSeats', 'event']

# Target use cases
use_cases = {"1": "queueing", "2": "freeSeats", "3": "event"}

# Time Range
start_ts = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d")
end_ts = "2021-08-23 20:00:00"

# Default device parameters
# HOSPITAL

# Seasonality
hospital = {"Yearly Seasonality": "Winter peaks, lower summers",
            "Weekly Seasonality": "Higher weekdays, lower weekends",
            "Daily Seasonality": "Peaks during daylight, much lower nights"}

# General device info
hospital_devices = [{"_id": "1",
                     "deviceType": "Depth Camera",
                     "deviceLocation": "Main Reception",
                     "site": "Sight Hospital",
                     "isIndoor": True,
                     "floor": "Ground Floor"},
                    {"_id": "2",
                     "deviceType": "RFID Sensors",
                     "deviceLocation": "Radiology Unit",
                     "site": "Sight Hospital",
                     "isIndoor": True,
                     "floor": "7",
                     "maxOccupancy": 20},
                    {"_id": "3",
                     "deviceType": "Depth Camera",
                     "deviceLocation": "Main Entrance",
                     "site": "Sight Hospital",
                     "isIndoor": True,
                     "floor": "Ground Floor"},
                    {"_id": "4",
                     "deviceType": "Depth Camera",
                     "deviceLocation": "Emergency Reception",
                     "site": "Sight Hospital",
                     "isIndoor": True,
                     "floor": "3"}]

# Scenario Statistics
scenario_hospital = [{"_id": "1",
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

                     {"_id": "2",
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

                     {"_id": "3",
                      "useCase": "3",
                      "freq_ts": "600S",
                      "footfall": {"peak_times": [10, 16],
                                   "mean": 40,
                                   "std": 5.5,
                                   "min": 0,
                                   "max": 20_000,
                                   "anom_freq": 15,
                                   "higher_weekdays": True,
                                   "high_season": [12, 2],
                                   "dwell_mean": 1,
                                   "dwell_sd": 0.3}},
                     {"_id": "4",
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


# BANK
# Seasonality
bank = {"Yearly Seasonality": "Peaks before christmas and summer holidays",
        "Weekly Seasonality": "Higher weekdays, lower weekends",
        "Daily Seasonality": "Peaks during daylight, much lower nights"}

# General Device Info
bank_devices = [{"_id": "1",
                 "deviceType": "Depth Camera",
                 "deviceLocation": "Sight ATM",
                 "site": "Sight National Bank",
                 "isIndoor": True,
                 "floor": "1"},
                {"_id": "2",
                 "deviceType": "RFID Sensors",
                 "deviceLocation": "Banking Service - Waiting Room",
                 "site": "Sight National Bank",
                 "isIndoor": True,
                 "floor": "2",
                 "maxOccupancy": 14},
                {"_id": "3",
                 "deviceType": "RFID Sensors",
                 "deviceLocation": "Main Entrance",
                 "site": "Sight National Bank",
                 "isIndoor": True,
                 "floor": "Ground Floor"}]

# Scenario Statistics
scenario_bank = [{"_id": "1",
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

                 {"_id": "2",
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

                 {"_id": "3",
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

# PARK
# Seasonality
park = {"Yearly Seasonality": "Summer peaks, lower winters",
        "Weekly Seasonality": "Higher weekends, lower weekdays",
        "Daily Seasonality": "Peaks during daylight, much lower nights"}

# General Device Info
park_devices = [{"_id": "1",
                 "deviceType": "Depth Camera",
                 "deviceLocation": "Sight Ice Cream Shop",
                 "site": "Syde Park",
                 "isIndoor": False},
                {"_id": "2",
                 "deviceType": "RFID Sensors",
                 "deviceLocation": "Syde Park Lake",
                 "site": "Syde Park",
                 "isIndoor": False,
                 "maxOccupancy": 30},
                {"_id": "3",
                 "deviceType": "Depth Camera",
                 "deviceLocation": "Syde Park Main Gate",
                 "site": "Syde Park",
                 "isIndoor": False},
                {"_id": "4",
                 "deviceType": "Depth Camera",
                 "deviceLocation": "Sight Waffle Shop",
                 "site": "Syde Park",
                 "isIndoor": False}]

# Scenario Statistics
scenario_park = [{"_id": "1",
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

                 {"_id": "2",
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

                 {"_id": "3",
                  "useCase": "3",
                  "freq_ts": "600S",
                  "footfall": {"peak_times": [10, 16],
                               "mean": 45,
                               "std": 6,
                               "min": 0,
                               "max": 20_000,
                               "anom_freq": 8,
                               "higher_weekdays": False,
                               "high_season": [7, 6],
                               "dwell_mean": 0.75,
                               "dwell_sd": 0.22}},
                 {"_id": "4",
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

# MALL
# Seasonality
mall = {"Yearly Seasonality": "Peaks before christmas and summer holidays",
        "Weekly Seasonality": "Higher weekends, lower weekdays",
        "Daily Seasonality": "Peaks during daylight, much lower nights"}

# General Device Info
mall_devices = [{"_id": "1",
                 "deviceType": "Depth Camera",
                 "deviceLocation": "Sight Book Shop",
                 "site": "Sight City Mall",
                 "isIndoor": True},
                {"_id": "2",
                 "deviceType": "RFID Sensors",
                 "deviceLocation": "Sight Food Court",
                 "site": "Sight City Mall",
                 "isIndoor": True,
                 "maxOccupancy": 50},
                {"_id": "3",
                 "deviceType": "Depth Camera",
                 "deviceLocation": "Main Entrance",
                 "site": "Sight City Mall",
                 "isIndoor": True}]

# Scenario Statistics
scenario_mall = [{"_id": "1",
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

                 {"_id": "2",
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

                 {"_id": "3",
                  "useCase": "3",
                  "freq_ts": "600S",
                  "footfall": {"peak_times": [12, 15],
                               "mean": 60,
                               "std": 8,
                               "min": 0,
                               "max": 20_000,
                               "anom_freq": 6,
                               "higher_weekdays": False,
                               "high_season": [12, 7],
                               "dwell_mean": 1.75,
                               "dwell_sd": 0.5}}]


# Scenarios all in one dictionary
scenario_seasonality = {"Sight Hospital": hospital,
                        "Syde Park": park,
                        "Sight National Bank": bank,
                        "Sight City Mall": mall}

# Default data set scenario parameters all in one dictionary
scenarios = {"Sight Hospital": scenario_hospital,
             "Syde Park": scenario_park,
             "Sight National Bank": scenario_bank,
             "Sight City Mall": scenario_mall}

# General info about the devices for each scenario all in one dictionary
device_info = {"Sight Hospital": hospital_devices,
               "Syde Park": park_devices,
               "Sight National Bank": bank_devices,
               "Sight City Mall": mall_devices}
