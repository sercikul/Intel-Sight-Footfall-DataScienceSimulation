from pymongo import MongoClient
from mock_data import *
from utilities import *







cluster = MongoClient("mongodb+srv://sightpp:UCLSightPP2021@sightcluster.ea126.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["sight"]
collection = db["footfall"]

# Preprocessing insert into database
ff_data = preprocess_for_mongo(total_df)
collection.insert_many(ff_data)


# Requires the PyMongo package.
# https://api.mongodb.com/python/current


collection.update_many({}, [{'$set': {'timestamp': {'$toDate': '$timestamp'}}}])

def insert_to_mongodb(total_df, collection):
    data = preprocess_for_mongo(total_df)
    collection.insert_many(data)
    collection.update_many({}, [{'$set': {'timestamp': {'$toDate': '$timestamp'}}}])
    return True
