import psutil
import os
import time
import threading

class ResourceMonitor:
    def __init__(self):
        self.keep_running = True
        self.peak_cpu = 0
        self.peak_ram = 0
        self.process = psutil.Process(os.getpid())

    def _monitor(self):
        while self.keep_running:
            # Get CPU % and RAM in MB
            cpu = psutil.cpu_percent(interval=0.1)
            ram = self.process.memory_info().rss / (1024 * 1024)
            
            if cpu > self.peak_cpu: self.peak_cpu = cpu
            if ram > self.peak_ram: self.peak_ram = ram
            time.sleep(0.1)

    def start(self):
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()

    def stop(self):
        self.keep_running = False
        self.thread.join()
        return self.peak_cpu, self.peak_ram

# --- HOW TO USE IT IN YOUR BENCHMARKS ---
# monitor = ResourceMonitor()
# monitor.start()
# ... run your query ...
# cpu, ram = monitor.stop()