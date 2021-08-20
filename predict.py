from utilities import *
from pymongo import MongoClient
from predictions import *


# Update data
# Further To-Dos:

# Try and test parameters for other use cases. Include 2 queueing for first use case.

# Configure task scheduler for optional automation

# Uncomment warnings in predictions


# Predict

def predict():
    # Predict future
    historical_data = retrieve_from_mongo(collection_ff, db)
    predictions = create_future_data(historical_data)
    insert_to_mongodb(predictions, collection_preds, db)
    return True


if __name__ == "__main__":
    cluster = MongoClient("mongodb+srv://sightpp:UCLSightPP2021@sightcluster.ea126.mongodb.net/myFirstDatabase"
                          "?retryWrites=true&w=majority")
    db = cluster["sight"]
    collection_ff = db["footfall"]
    collection_preds = db["predictions"]
    predict()