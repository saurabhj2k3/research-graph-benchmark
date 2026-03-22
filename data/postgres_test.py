import psycopg2
import time

# 1. Connection Details
DB_CONFIG = {
    "dbname": "bank_db",
    "user": "postgres",
    "password": "Saurabh@123",
    "host": "localhost"
}

def run_postgres_benchmark():
    # Connect
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 2. Load 1 Million Rows (The Fast Way)
    print("Loading data into Postgres...")
    cur.execute("DROP TABLE IF EXISTS transactions;")
    cur.execute("CREATE TABLE transactions (from_acc TEXT, to_acc TEXT, amount FLOAT);")
    
    # Use 'COPY' - it's 100x faster than 'INSERT'
    with open('data/transactions.csv', 'r') as f:
        next(f) # Skip header
        cur.copy_from(f, 'transactions', sep=',')
    conn.commit()
    print("✅ Data Loaded!")

    # 3. The 5-Hop Race (Recursive Query)
    print("Running 5-Hop Traversal...")
    start_node = 'ACC_000001' # Starting point
    
    query = f"""
    WITH RECURSIVE hops AS (
        SELECT to_acc, 1 as level FROM transactions WHERE from_acc = '{start_node}'
        UNION ALL
        SELECT t.to_acc, h.level + 1
        FROM transactions t
        JOIN hops h ON t.from_acc = h.to_acc
        WHERE h.level < 5
    )
    SELECT COUNT(*) FROM hops;
    """
    
    start_time = time.time()
    cur.execute(query)
    result = cur.fetchone()
    end_time = time.time()
    
    print(f"⏱️ Time taken: {(end_time - start_time) * 1000:.2f} ms")
    print(f"🔗 Connections found: {result[0]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    run_postgres_benchmark()