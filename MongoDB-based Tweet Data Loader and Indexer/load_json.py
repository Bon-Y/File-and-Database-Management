'''
    python3 load-json.py your_input.json 61288
'''
# ref: https://stackoverflow.com/questions/12451431/loading-and-parsing-a-json-file-with-multiple-json-objects

import json
import pymongo
import argparse
import time

def load_json_to_mongo(json_file, port):
    # Connect to MongoDB server
    client = pymongo.MongoClient(f"mongodb://localhost:{port}/")
    
    # Create or get the database
    db = client["291db"]
    
    # Drop the tweets collection if it exists
    if "tweets" in db.list_collection_names():
        db["tweets"].drop()
    
    # Create the tweets collection
    tweets_collection = db["tweets"]

    # Read JSON file and insert data into MongoDB in batches
    batch_size = 1000
    data = []
    start = time.time()
    with open(json_file, 'r') as file:
        for line in file:
            data.append(json.loads(line))
        tweets = data

        for i in range(0, len(tweets), batch_size):
            batch = tweets[i:i+batch_size]
            tweets_collection.insert_many(batch)

    print("Collection 'tweets' created successfully.")
    print(f"Total time: {time.time() - start} seconds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load JSON file into MongoDB collection.")
    parser.add_argument("json_file", help="Input JSON file name in the current directory.")
    parser.add_argument("port", type=int, help="Port number of the MongoDB server.")

    args = parser.parse_args()
    json_file = args.json_file
    port = args.port

    load_json_to_mongo(json_file, port)

