import pymongo
import time
import json
import os

# --- 1. CONFIGURATION ---
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "bank_db"
COLLECTION_NAME = "transactions"
JSON_PATH = "data/transactions.json"

def run_mongo_benchmark():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db["transactions"]

        # --- 2. CLEAN & LOAD DATA ---
        print("🧹 Cleaning old MongoDB data...")
        collection.drop()

        print(f"🚀 Loading 1 Million rows from {JSON_PATH}...")
        with open(JSON_PATH, 'r') as f:
            data = json.load(f)
        
        start_load = time.time()
        # Insert in batches for speed
        collection.insert_many(data)
        print(f"✅ Data Loaded in {time.time() - start_load:.2f} seconds.")

        # Create Index (Crucial for performance!)
        print("🔍 Creating Index on 'from_acc'...")
        collection.create_index("from_acc")

        # --- 3. THE 5-HOP CHALLENGE ---
        start_node = 'ACC_000001'
        print(f"\n🏃 Starting MongoDB $graphLookup Benchmark for {start_node}...")

        for depth in range(1, 6):
            # MongoDB's way of doing Graph Traversal
            pipeline = [
                { "$match": { "from_acc": start_node } },
                {
                    "$graphLookup": {
                        "from": "transactions",
                        "startWith": "$to_acc",
                        "connectFromField": "to_acc",
                        "connectToField": "from_acc",
                        "maxDepth": depth - 1, # Mongo depth is 0-indexed
                        "as": "connections"
                    }
                },
                { "$project": { "count": { "$size": "$connections" } } }
            ]

            start_query = time.time()
            result = list(collection.aggregate(pipeline))
            elapsed = (time.time() - start_query) * 1000
            
            count = result[0]['count'] if result else 0
            print(f"Depth {depth}: {elapsed:.2f} ms (Found {count} connections)")

        client.close()
        print("\n🏁 MongoDB Benchmark Finished!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_mongo_benchmark()