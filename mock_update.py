from mock_data import *
from default_scenarios import *
from utilities import *
from pymongo import MongoClient
from predictions import *
import warnings
warnings.filterwarnings("ignore")


def update():
    """Updates existing synthetic data"""
    # Retrieve data and device settings of selected scenario from mongodb
    data = retrieve_from_mongo(collection_ff, db)
    scenario = retrieve_from_mongo(collection_scenario, db)
    # Retrieve most recent timestamp in historical data set
    last_ts = data["timestamp"].max()
    end_ts = "now"
    # Calculate the current visitor count, i.e. how many visitors were in the venue on last data collection
    n_visitors = len(data[data["event"] == "personIn"]) - len(data[data["event"] == "personOut"])
    last_n_person_in = data["timestamp"][data["event"] == "personIn"].tail(n_visitors)
    # Update database by creating new mock data starting from 'last_ts'
    update = {"last_ts": last_ts, "last_n_person_in": last_n_person_in}
    update_df = synthesise_data(scenario, use_cases, last_ts, end_ts, update_ts=update)
    insert_to_mongodb(update_df, collection_ff, db, update=True)
    cum_visitor_count(collection_ff)
    # Retrieve updated historical data and make new predictions
    historical_data = retrieve_from_mongo(collection_ff, db)
    predictions = create_future_data(historical_data)
    insert_to_mongodb(predictions, collection_preds, db)
    print("You have successfully updated your mock data. Have a look into your MongoDB dashboard!")
    return True


if __name__ == "__main__":
    # Connect to MongoDB, before executing update().
    cluster = MongoClient("mongodb+srv://sightpp:UCLSightPP2021@sightcluster.ea126.mongodb.net/myFirstDatabase"
                          "?retryWrites=true&w=majority")
    db = cluster["sight"]
    collection_ff = db["footfall"]
    collection_preds = db["predictions"]
    collection_scenario = db["scenario"]
    update()


