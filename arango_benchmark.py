from arango import ArangoClient
import time
import json

# --- 1. CONFIGURATION ---
client = ArangoClient(hosts='http://localhost:8529')
# Connect to system DB (Update password if you set one)
db = client.db('_system', username='root', password='test')

def run_arango_benchmark():
    try:
        # 2. Setup Collections
        print("🧹 Cleaning ArangoDB collections...")
        if db.has_collection('accounts'): db.delete_collection('accounts')
        if db.has_collection('transactions'): db.delete_collection('transactions')
        
        # 'transactions' must be an EDGE collection for Graph Traversal
        accounts = db.create_collection('accounts')
        transactions = db.create_collection('transactions', edge=True)

        # 3. Load Data from JSON
        print("🚀 Loading 1 Million records into ArangoDB...")
        with open('data/transactions.json', 'r') as f:
            data = json.load(f)
        
        # Build unique account vertices and edge fields ArangoDB expects.
        account_keys = set()
        for idx, doc in enumerate(data):
            account_keys.add(doc['from_acc'])
            account_keys.add(doc['to_acc'])
            doc['_from'] = f"accounts/{doc['from_acc']}"
            doc['_to'] = f"accounts/{doc['to_acc']}"
            # Avoid collisions when multiple transactions happen between same pair.
            doc['_key'] = f"{doc['from_acc']}_{doc['to_acc']}_{idx}"

        print(f"📦 Inserting {len(account_keys)} account vertices...")
        account_docs = [{'_key': key} for key in account_keys]
        accounts.import_bulk(account_docs)
        
        start_load = time.time()
        # Import in batches of 50k for speed
        batch_size = 50000
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            result = transactions.import_bulk(batch)
            if isinstance(result, dict) and result.get('errors', 0):
                print(f"⚠️ Batch {i//batch_size + 1}: {result.get('errors')} import errors")
            print(f"   Loaded {min(i + batch_size, len(data))}...")
            
        print(f"✅ Data Loaded in {time.time() - start_load:.2f}s")

        # 4. THE 5-HOP CHALLENGE
        start_node = f"accounts/{data[0]['from_acc']}" if data else 'accounts/ACC_000001'
        print(f"\n🏃 Starting ArangoDB AQL Traversal for {start_node}...")

        for depth in range(1, 6):
            # AQL Traversal Syntax
            query = f"""
            FOR v IN 1..{depth} OUTBOUND '{start_node}' transactions
                OPTIONS {{ uniqueVertices: 'global', bfs: true }}
                COLLECT WITH COUNT INTO total
                RETURN total
            """
            
            start_query = time.time()
            cursor = db.aql.execute(query)
            count = list(cursor)[0]
            elapsed = (time.time() - start_query) * 1000
            
            print(f"Depth {depth}: {elapsed:.2f} ms (Found {count} connections)")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_arango_benchmark()
