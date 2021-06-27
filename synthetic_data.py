# Intel Sight++ Data Science Simulation

# Event-based schema
        # {
        #     "timestamp": "2012-04-23T18:25:43.511Z",
        #     "deviceId": 1,
        #     "targetId": 1,
        #     "queueing": 7,
        #     "freeSeats": 2,
        #     "event": "personIn"
        # }

#Import modules
import json 


# Create data set in noSQL format.
# Function to create synthetic data on an automated basis (e.g. on hourly basis).












# Create data tables and in the end convert it into JSON format.
# Starter code to pass in data in JSON format from noSQL database. This data is converted into a numpy data table. 
# Aggregations and calculations are done on the numpy data set. Finally, data is converted back into JSON format and
# inserted into the database. 

with open('Intel-Sight-Footfall-DataScienceSimulation\event-schema.json') as f:
    data = json.load(f)

for state in data['examples']:
    print(state)