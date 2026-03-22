import psutil
import time
import os
import threading

class DeviceMonitor:
    def __init__(self):
        self.keep_monitoring = True
        self.peak_cpu = 0
        self.peak_ram = 0
        self.process = psutil.Process(os.getpid())

    def _track(self):
        while self.keep_monitoring:
            cpu = psutil.cpu_percent(interval=0.1)
            # RSS is the actual physical memory being used in MB
            ram = self.process.memory_info().rss / (1024 * 1024) 
            
            if cpu > self.peak_cpu: self.peak_cpu = cpu
            if ram > self.peak_ram: self.peak_ram = ram
            time.sleep(0.05)

    def start(self):
        self.thread = threading.Thread(target=self._track)
        self.thread.start()

    def stop(self):
        self.keep_running = False
        self.keep_monitoring = False
        self.thread.join()
        return round(self.peak_cpu, 2), round(self.peak_ram, 2)

# This is the template you will use for EACH database
def run_test_sample(db_name):
    monitor = DeviceMonitor()
    print(f"📊 Monitoring Hardware for: {db_name}...")
    monitor.start()
    
    # --- INSERT YOUR DATABASE QUERY CODE HERE ---
    time.sleep(2) # Placeholder for the 5-Hop Query
    
    cpu, ram = monitor.stop()
    print(f"🏁 {db_name} Results -> Peak CPU: {cpu}% | Peak RAM: {ram} MB")
    return cpu, ram

if __name__ == "__main__":
    run_test_sample("Demo Test")