import psycopg2
import time
import psutil
import threading
import os

# --- DEVICE MONITOR CLASS ---
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
        self.peak_cpu = 0
        self.peak_ram = 0
        self.keep_monitoring = True
        self.thread = threading.Thread(target=self._track)
        self.thread.start()

    def stop(self):
        self.keep_monitoring = False
        self.thread.join()
        return round(self.peak_cpu, 2), round(self.peak_ram, 2)

def run_postgres_full_report():
    conn = psycopg2.connect(dbname="bank_db", user="postgres", password="Saurabh@123", host="localhost")
    cur = conn.cursor()
    monitor = DeviceMonitor()
    
    start_node = 'ACC_000001'
    print(f"\n🐘 Generating Full 5-Hop PostgreSQL Report for {start_node}...")
    print("="*70)
    print(f"{'Depth':<8} | {'Time (ms)':<12} | {'Peak CPU %':<12} | {'Peak RAM (MB)':<15}")
    print("-" * 70)

    for depth in range(1, 6):
        monitor.start()
        
        # Recursive CTE for Postgres
        query = f"""
        WITH RECURSIVE hops AS (
            SELECT to_acc, 1 as level FROM transactions WHERE from_acc = '{start_node}'
            UNION ALL
            SELECT t.to_acc, h.level + 1
            FROM transactions t
            JOIN hops h ON t.from_acc = h.to_acc
            WHERE h.level < {depth}
        )
        SELECT COUNT(DISTINCT to_acc) FROM hops;
        """
        
        t1 = time.time()
        cur.execute(query)
        cur.fetchone()
        t2 = time.time()
        
        cpu, ram = monitor.stop()
        print(f"{depth:<8} | {(t2-t1)*1000:<12.2f} | {cpu:<12.2f} | {ram:<15.2f}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    run_postgres_full_report()