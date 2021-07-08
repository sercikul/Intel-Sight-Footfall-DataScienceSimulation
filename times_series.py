from mock_data import *
import statsmodels.api as sm
import matplotlib.pyplot as plt



# To Dos:
# 1. Find appropriate methods to predict free seats and queues (on a 10 sec basis)
# 2. Aggregate datasets (per hour). Predict footfall (events), count people per hour.
# 3. Bring some seasonality in dataset (summer months, week days etc.)


# Time Series Analysis - Tests
df_id1 = total_df[total_df["deviceID"] == "2"]
#print(df_id1)
stats_cycle, stats_trend = sm.tsa.filters.hpfilter(df_id1["freeSeats"], lamb=1600000)

#result = sm.tsa.seasonal_decompose(df_id1["freeSeats"], model="additive")

#result.trend



df_id1 = df_id1.set_index("timestamp")
print(df_id1)
result = sm.tsa.seasonal_decompose(df_id1["freeSeats"], model="additive")