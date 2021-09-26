from utilities import *
from pymongo import MongoClient
from predictions import *
import warnings

warnings.filterwarnings("ignore")


def predict():
    """Predictions in a productive environment. No mock data
    creation involved."""
    historical_data = retrieve_from_mongo(collection_ff, db)
    predictions = create_future_data(historical_data)
    insert_to_mongodb(predictions, collection_preds, db)
    return True


if __name__ == "__main__":
    # Connect to MongoDB before running predict().
    cluster = MongoClient("mongodb+srv://sightpp:UCLSightPP2021@sightcluster.ea126.mongodb.net/myFirstDatabase"
                          "?retryWrites=true&w=majority")
    db = cluster["sight"]
    collection_ff = db["footfall"]
    collection_preds = db["predictions"]
    predict()
