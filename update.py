from mock_data import *
from default_scenarios import *
from utilities import *
from tabulate import tabulate
from pymongo import MongoClient
from predictions import *


# Update data
# Further To-Dos:

# Try and test parameters for other use cases. Include 2 queueing for first use case.

# Take data from mongodb and build new data on top of it and insert it back into database
# Retrieve from mongodb and do forecast. standard procedure

# Configure task scheduler for optional automation

# Uncomment warnings in predictions


# Update

def update():
    # Retrieve data and saved device settings of selected scenario from mongodb
    data = retrieve_from_mongo(collection_ff, db)
    scenario = retrieve_from_mongo(collection_scenario, db)
    # Get last interval-based timestamp
    start_ts = data["timestamp"].min()
    # Most recent timestamp in data set
    last_ts = data["timestamp"].max()
    end_ts = "now"
    update_df = synthesise_data(scenario, use_cases, start_ts, end_ts, update_ts=last_ts)
    insert_to_mongodb(update_df, collection_ff, db, update=True)
    # Get updated historical data
    historical_data = retrieve_from_mongo(collection_ff, db)
    predictions = create_future_data(historical_data)
    insert_to_mongodb(predictions, collection_preds, db)
    print("You have successfully updated your mock data. Have a look into your MongoDB dashboard!")
    return True


if __name__ == "__main__":
    cluster = MongoClient("mongodb+srv://sightpp:UCLSightPP2021@sightcluster.ea126.mongodb.net/myFirstDatabase"
                          "?retryWrites=true&w=majority")
    db = cluster["sight"]
    collection_ff = db["footfall"]
    collection_preds = db["predictions"]
    collection_scenario = db["scenario"]
    update()
