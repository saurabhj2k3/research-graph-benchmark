from neo4j import GraphDatabase
import time
import psutil
import threading
import os

class DeviceMonitor:
    def __init__(self):
        self.keep_monitoring = True
        self.peak_cpu = 0
        self.peak_ram = 0
        self.process = psutil.Process(os.getpid())

    def _track(self):
        while self.keep_monitoring:
            # interval=None is faster for catching spikes
            cpu = psutil.cpu_percent(interval=None)
            ram = self.process.memory_info().rss / (1024 * 1024)
            if cpu > self.peak_cpu: self.peak_cpu = cpu
            if ram > self.peak_ram: self.peak_ram = ram
            time.sleep(0.01)

    def start(self):
        self.peak_cpu = 0
        self.peak_ram = 0
        self.keep_monitoring = True
        self.thread = threading.Thread(target=self._track)
        self.thread.start()

    def stop(self):
        self.keep_monitoring = False
        self.thread.join()
        return round(self.peak_cpu, 2), round(self.peak_ram, 2)

def run_full_report():
    # Update with your actual password
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Saurabh@123"))
    monitor = DeviceMonitor()
    
    results_table = []

    with driver.session() as session:
        start_node = 'ACC_000001'
        print(f"\n🔬 Generating Full 5-Hop Performance Report for {start_node}...")
        print("="*70)
        print(f"{'Depth':<8} | {'Time (ms)':<12} | {'Peak CPU %':<12} | {'Peak RAM (MB)':<15} | {'Nodes Found'}")
        print("-" * 70)

        for depth in range(1, 6):
            # 1. Reset and Start Monitoring
            monitor.start()
            
            query = f"MATCH (a:Account {{id: '{start_node}'}})-[:SENDS*1..{depth}]->(c) RETURN count(DISTINCT c) as count"
            
            start_time = time.time()
            result = session.run(query).single()
            end_time = time.time()
            
            # 2. Stop Monitoring
            cpu, ram = monitor.stop()
            elapsed = (end_time - start_time) * 1000
            count = result['count']

            # 3. Print Row
            print(f"{depth:<8} | {elapsed:<12.2f} | {cpu:<12.2f} | {ram:<15.2f} | {count}")
            
            results_table.append([depth, elapsed, cpu, ram, count])

    driver.close()
    print("="*70)
    print("🏁 Research Data Collection Complete!")

if __name__ == "__main__":
    run_full_report()