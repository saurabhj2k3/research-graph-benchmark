import psycopg2
import time
import os

# --- 1. CONFIGURATION ---
DB_CONFIG = {
    "dbname": "bank_db",
    "user": "postgres",
    "password": "Saurabh@123",  # 👈 Update this!
    "host": "localhost",
    "port": "5432"
}

CSV_PATH = os.path.abspath("data/transactions.csv")

def run_benchmark():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # --- 2. CLEAN & LOAD DATA ---
        print("🧹 Cleaning old data and creating table...")
        cur.execute("DROP TABLE IF EXISTS transactions;")
        cur.execute("CREATE TABLE transactions (from_acc TEXT, to_acc TEXT, amount FLOAT);")
        
        print(f"🚀 Loading 1 Million rows from {CSV_PATH}...")
        start_load = time.time()
        with open(CSV_PATH, 'r') as f:
            next(f)  # Skip header
            cur.copy_from(f, 'transactions', sep=',')
        conn.commit()
        print(f"✅ Data Loaded in {time.time() - start_load:.2f} seconds.")

        # --- 3. THE 5-HOP CHALLENGE ---
        # We test depths 1 to 5
        start_node = 'ACC_000001' 
        results = []

        print(f"\n🏃 Starting 5-Hop Benchmark for {start_node}...")
        
        for depth in range(1, 6):
            # This is the Recursive CTE (The SQL way to do Graphs)
            query = f"""
            WITH RECURSIVE hops AS (
                SELECT to_acc, 1 as level FROM transactions WHERE from_acc = '{start_node}'
                UNION ALL
                SELECT t.to_acc, h.level + 1
                FROM transactions t
                JOIN hops h ON t.from_acc = h.to_acc
                WHERE h.level < {depth}
            )
            SELECT COUNT(*) FROM hops;
            """
            
            start_query = time.time()
            cur.execute(query)
            count = cur.fetchone()[0]
            elapsed = (time.time() - start_query) * 1000 # Convert to ms
            
            print(f"Depth {depth}: {elapsed:.2f} ms (Found {count} connections)")
            results.append({"Depth": depth, "Time_ms": elapsed})

        cur.close()
        conn.close()
        print("\n🏁 PostgreSQL Benchmark Finished!")

    except Exception as e:
        print(f"❌ Error during benchmark: {e}")

if __name__ == "__main__":
    run_benchmark()