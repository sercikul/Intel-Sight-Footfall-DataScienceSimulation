from pymongo import MongoClient
from utilities import *
from predictions import *

cluster = MongoClient("mongodb+srv://sightpp:UCLSightPP2021@sightcluster.ea126.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["sight"]
collection_ff = db["footfall"]
collection_preds = db["predictions"]

# Import footfall data from database
data = collection_ff.find()


# Retrieve only in cases when the user has an existing source and does not need to create a synthetic data set
imported_df = retrieve_from_mongo(data)

# Predict future footfall
predictions = predict_future(imported_df)

# Insert predictions into predictions table
preds = preprocess_for_mongo(predictions)

# Delete existing forecasts to replace with incoming forecasts
collection_preds.delete_many({})

collection_preds.insert_many(preds)

collection_preds.update_many({},
    [{
        '$set': {
            'timestamp': {
                '$toDate': '$timestamp'
            }
        }
    }
    ])