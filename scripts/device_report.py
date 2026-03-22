import psutil
import time
import threading
import os

class PerformanceTracker:
    def __init__(self):
        self.stop_monitoring = False
        self.peak_cpu = 0
        self.peak_ram = 0
        self.process = psutil.Process(os.getpid())

    def _monitor(self):
        while not self.stop_monitoring:
            # Get current CPU and RAM (RSS = Resident Set Size)
            cpu = psutil.cpu_percent(interval=0.1)
            ram = self.process.memory_info().rss / (1024 * 1024) # Convert to MB
            
            if cpu > self.peak_cpu: self.peak_cpu = cpu
            if ram > self.peak_ram: self.peak_ram = ram
            time.sleep(0.05)

    def start(self):
        self.stop_monitoring = False
        self.monitor_thread = threading.Thread(target=self._monitor)
        self.monitor_thread.start()

    def stop(self):
        self.stop_monitoring = True
        self.monitor_thread.join()
        return round(self.peak_cpu, 2), round(self.peak_ram, 2)

# --- EXAMPLE TEST FOR YOUR REPORT ---
print("📊 Starting Device Performance Test...")
tracker = PerformanceTracker()
tracker.start()

# --- RUN YOUR DATABASE QUERY CODE HERE ---
# (Paste your Depth 5 Query for Neo4j or Postgres)
time.sleep(2) # Simulating a heavy query

cpu, ram = tracker.stop()
print(f"✅ Results -> Peak CPU: {cpu}% | Peak RAM: {ram} MB")