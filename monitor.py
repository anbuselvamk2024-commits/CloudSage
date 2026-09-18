import psutil
import time

cpu = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory().percent
disk = psutil.disk_usage('/').percent

net1 = psutil.net_io_counters()
time.sleep(1)
net2 = psutil.net_io_counters()

upload_speed = (net2.bytes_sent - net1.bytes_sent) / 1024
download_speed = (net2.bytes_recv - net1.bytes_recv) / 1024

print("CPU Usage:", cpu, "%")
print("Memory Usage:", memory, "%")
print("Disk Usage:", disk, "%")
print("Upload Speed:", round(upload_speed, 2), "KB/s")
print("Download Speed:", round(download_speed, 2), "KB/s")