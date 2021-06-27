import pandas as pd
import numpy as np
import datetime
import random

from pandas.core.frame import DataFrame 

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

date_rng = pd.date_range(start='1/1/2018', end='now', freq='0.2H')

df = pd.DataFrame(columns = attributes)

# for i in range(len(date_rng)):
#     df.loc[i] = [i, i, date_rng[i], 10, 4, 'personIn']

#df = pd.DataFrame(date_rng, columns=['date'])
#df['data'] = np.random.randint(0, 100, size=(len(date_rng)))

print(df)