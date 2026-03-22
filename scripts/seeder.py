import networkx as nx
import pandas as pd
import random
import os
import json

# --- CONFIGURATION ---
NUM_ACCOUNTS = 100000        # 1 Lakh Users
NUM_TRANSACTIONS = 1000000   # 10 Lakh Transactions (1 Million)
DATA_DIR = "data"

def generate_data():
    # Ensure the data folder exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 Created directory: {DATA_DIR}")

    print(f"🚀 Generating Graph Structure ({NUM_ACCOUNTS} nodes)...")
    # GNM model creates a graph with exactly M edges
    G = nx.gnm_random_graph(NUM_ACCOUNTS, NUM_TRANSACTIONS, directed=True)

    # 1. Generate Account Metadata (Nodes)
    print("👤 Generating Account details...")
    accounts = []
    for i in range(NUM_ACCOUNTS):
        accounts.append({
            "account_id": f"ACC_{i:06d}",
            "name": f"User_{i}",
            "balance": round(random.uniform(1000, 50000), 2)
        })

    # 2. Generate Transaction Data (Edges)
    print("💸 Generating 1 Million Transaction edges...")
    transactions = []
    for u, v in G.edges():
        transactions.append({
            "from_acc": f"ACC_{u:06d}",
            "to_acc": f"ACC_{v:06d}",
            "amount": round(random.uniform(10, 5000), 2)
        })

    # --- SAVE TO CSV (For Postgres & Neo4j) ---
    print("💾 Saving CSV files...")
    pd.DataFrame(accounts).to_csv(f"{DATA_DIR}/accounts.csv", index=False)
    pd.DataFrame(transactions).to_csv(f"{DATA_DIR}/transactions.csv", index=False)

    # --- SAVE TO JSON (For MongoDB & ArangoDB) ---
    print("💾 Saving JSON files (this may take a moment)...")
    with open(f"{DATA_DIR}/accounts.json", "w") as f:
        json.dump(accounts, f)
    with open(f"{DATA_DIR}/transactions.json", "w") as f:
        json.dump(transactions, f)

    print(f"\n✅ SUCCESS! Files created in '{DATA_DIR}/':")
    print(f"- accounts.csv / .json")
    print(f"- transactions.csv / .json")

if __name__ == "__main__":
    generate_data()