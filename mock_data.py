import pandas as pd
import numpy as np
import datetime
import random 

# Event data
# Normal distribution per venue regarding time ?

targets = {

}

attributes = ['targetID', 'deviceID', 'timestamp', 'queueing', 'freeSeats', 'event']

date_rng = pd.date_range(start='1/1/2018', end='now', freq='H')

#df = pd.DataFrame(columns = attributes)

df = pd.DataFrame(date_rng, columns=['date'])

df['data'] = np.random.randint(0, 100, size=(len(date_rng)))

print(df)