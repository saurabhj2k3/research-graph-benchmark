from pymongo import MongoClient
import time
import psutil
import threading
import os

# --- DEVICE MONITOR CLASS (Same as before) ---
class DeviceMonitor:
    def __init__(self):
        self.keep_monitoring = True
        self.peak_cpu = 0
        self.peak_ram = 0
        self.process = psutil.Process(os.getpid())

    def _track(self):
        while self.keep_monitoring:
            cpu = psutil.cpu_percent(interval=None)
            ram = self.process.memory_info().rss / (1024 * 1024)
            if cpu > self.peak_cpu: self.peak_cpu = cpu
            if ram > self.peak_ram: self.peak_ram = ram
            time.sleep(0.01)

    def start(self):
        self.peak_cpu = 0; self.peak_ram = 0
        self.keep_monitoring = True
        self.thread = threading.Thread(target=self._track); self.thread.start()

    def stop(self):
        self.keep_monitoring = False; self.thread.join()
        return round(self.peak_cpu, 2), round(self.peak_ram, 2)

def run_mongo_report():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["bank_db"]
    monitor = DeviceMonitor()
    
    start_node = 'ACC_000001'
    print(f"\n🍃 Generating Full 5-Hop MongoDB Report for {start_node}...")
    print("="*70)
    print(f"{'Depth':<8} | {'Time (ms)':<12} | {'Peak CPU %':<12} | {'Peak RAM (MB)':<15}")
    print("-" * 70)

    for depth in range(1, 6):
        monitor.start()
        
        # MongoDB GraphLookup (Equivalent to Joins)
        pipeline = [
            {"$match": {"from_acc": start_node}},
            {"$graphLookup": {
                "from": "transactions",
                "startWith": "$to_acc",
                "connectFromField": "to_acc",
                "connectToField": "from_acc",
                "as": "connections",
                "maxDepth": depth - 1
            }},
            {"$project": {"count": {"$size": "$connections"}}}
        ]
        
        t1 = time.time()
        list(db.transactions.aggregate(pipeline))
        t2 = time.time()
        
        cpu, ram = monitor.stop()
        print(f"{depth:<8} | {(t2-t1)*1000:<12.2f} | {cpu:<12.2f} | {ram:<15.2f}")

if __name__ == "__main__":
    run_mongo_report()