from mock_data import *
import statsmodels.api as sm
import matplotlib.pyplot as plt
from arch import arch_model

# To Dos:
# 1. Find appropriate methods to predict free seats and queues (on a 10 sec basis)
# 2. Aggregate datasets (per hour). Predict footfall (events), count people per hour.
# 3. Bring some seasonality in dataset (summer months, week days etc.)


# Time Series Analysis - Tests
df_id1 = total_df[total_df["deviceID"] == "2"]
print(df_id1)
stats_cycle, stats_trend = sm.tsa.filters.hpfilter(df_id1["freeSeats"], lamb=1600000)

# result = sm.tsa.seasonal_decompose(df_id1["freeSeats"], model="additive")

# result.trend


df_id1 = df_id1.set_index("timestamp")
# result = sm.tsa.seasonal_decompose(df_id1["freeSeats"], model="additive")


# Simple moving average / EWMA
# Exponentially weighted moving averages
# EWMA puts more weight on values that occurred more recently

# SMA
df_id1["1-hour-SMA"] = df_id1["freeSeats"].rolling(window=3).mean()


# EMA
df_id1["1-hour-EWMA"] = df_id1["freeSeats"].ewm(span=12).mean()

#print(df_id1[["freeSeats", "1-hour-SMA", "1-hour-EWMA"]])


