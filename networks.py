import os
import subprocess
import re
import time
import tkinter.messagebox as mb
from tkinter import *
from ttkbootstrap.widgets import Meter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import psutil
import speedtest

def clear_log_directory(log_directory):
    try:
        files = os.listdir(log_directory)
        for file in files:
            file_path = os.path.join(log_directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        pass
def run_snort(duration):
    try:
        
        snort_process = subprocess.Popen(['C:\\snort\\bin\\snort.exe','-i','4','-c','C:\\snort\\etc\\snort.conf'])
        time.sleep(duration)
        snort_process.terminate()
    except Exception as e:
        pass

def check_alerts(file_path):
    try:
        with open(file_path, 'r') as file:
            alerts = file.read()

        match = re.search(r'(\d{2}/\d{2}-\d{2}:\d{2}:\d{2}.\d{6}) (\d+\.\d+\.\d+\.\d+) -> (\d+\.\d+\.\d+\.\d+)', alerts)
        if match:
            timestamp = match.group(1)
            attacker_ip = match.group(2)
            mb.showwarning("ICMP Flood Attack Detected", f"Timestamp: {timestamp}\nAttacker IP: {attacker_ip}")
    except FileNotFoundError:
        pass
    except Exception as e:
        pass

def clear_log_directory_periodically(log_directory):
    while True:
        clear_log_directory(log_directory)
        time.sleep(5)

def run_snort_periodically(duration):
    while True:
        run_snort(duration)
        time.sleep(5)

def check_alerts_periodically(file_path):
    while True:
        check_alerts(file_path)
        time.sleep(5)

def measure_cpu_utilization():
    cpu_percent = psutil.cpu_percent(interval=1)
    return cpu_percent

def update_cpu_graph():
    while True:
        cpu_percent = measure_cpu_utilization()
        cpu_data.append(cpu_percent)
        if len(cpu_data) > 50:  
            cpu_data.pop(0)
        cpu_line.set_ydata(cpu_data)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw()
        try:
            cpu_label.config(text=f"CPU Utilization: {cpu_percent} %")
        except TclError:
            pass
        time.sleep(1)

def measure_network():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        latency = st.results.ping
        download_speed = st.download() / 1e+6  
        upload_speed = st.upload() / 1e+6  
        return latency, download_speed, upload_speed
    except:
        pass
        return None, None, None

def update_latency_meter(latency):

    latency_meter.configure(amountused=latency)

def update_download_meter(download_speed):
    download_meter.configure(amountused=download_speed)

def update_upload_meter(upload_speed):
    upload_meter.configure(amountused=upload_speed)
    
def update_network_parameters():
    while True:
        latency, download_speed, upload_speed = measure_network()
        if latency is not None:
            try:
                update_latency_meter(round(latency))
                update_download_meter(round(download_speed))
                update_upload_meter(round(upload_speed))
                latency_label.config(text=f"Latency: {round(latency)} ms")
                download_label.config(text=f"Download Speed: {round(download_speed)} Mbps")
                upload_label.config(text=f"Upload Speed: {round(upload_speed)} Mbps")
            except:
                pass
        else:
            try:
                latency_label.config(text="Latency: N/A")
                download_label.config(text="Download Speed: N/A")
                upload_label.config(text="Upload Speed: N/A")
            except:
                pass
        time.sleep(3)

def measure_network_utilization():
    total_bytes_sent = psutil.net_io_counters().bytes_sent
    total_bytes_received = psutil.net_io_counters().bytes_recv
    time.sleep(1)
    new_bytes_sent = psutil.net_io_counters().bytes_sent
    new_bytes_received = psutil.net_io_counters().bytes_recv
    
    bytes_sent = new_bytes_sent - total_bytes_sent
    bytes_received = new_bytes_received - total_bytes_received
    
    utilization_sent = (bytes_sent * 8) / 1  
    utilization_received = (bytes_received * 8) / 1  
    
    return utilization_sent, utilization_received


def update_graph():
    while True:
        utilization_sent, utilization_received = measure_network_utilization()
        x.append(len(x))
        y_sent.append(utilization_sent / (1024 * 1024))  
        y_received.append(utilization_received / (1024 * 1024))
        ax_network.clear()
        ax_network.plot(x, y_sent, label='Sent')
        ax_network.plot(x, y_received, label='Received')
        ax_network.legend()
        ax_network.set_xlabel('Time (s)')
        ax_network.set_ylabel('Megabytes (sent/received)') 
        ax_network.set_title('Network Utilization')
        canvas_network.draw()
        time.sleep(1)


main = Tk()
main.title("Network Performance and Security")
main.configure(bg="white")
main.geometry(f"1660x960")

fig, ax = plt.subplots(figsize=(4,5))
cpu_data = [0] * 50  
cpu_line, = ax.plot(cpu_data, 'b-')
fig.tight_layout()
ax.set_xlabel('Time (s)')
ax.set_ylabel('CPU Usage (%)')
ax.set_ylim(0, 100)

fig_network, ax_network = plt.subplots(figsize=(6,3))  
ax_network.set_ylim(0, 100000) 
fig_network.tight_layout()
canvas_network = FigureCanvasTkAgg(fig_network, master=main)
canvas_network_widget = canvas_network.get_tk_widget()

x = []
y_sent = []
y_received = []

cpu_label = Label(main, text="CPU Usage: N/A%", bg="white", font=('Times New Roman', 16))
cpu_label.place(x=700, y=100)

latency_label = Label(main, text="Latency: N/A ms", bg="white", font=('Times New Roman', 16))
latency_label.place(x=40, y=100)

download_label = Label(main, text="Download Speed: N/A Mbps", bg="white", font=('Times New Roman', 16))
download_label.place(x=180, y=100)

upload_label = Label(main, text="Upload Speed: N/A Mbps", bg="white", font=('Times New Roman', 16))
upload_label.place(x=420, y=100)

latency_canvas = Canvas(main, width=300, height=100, bg="white")
latency_canvas.place(x=30, y=150)

download_canvas = Canvas(main, width=300, height=100, bg="white")
download_canvas.place(x=210, y=150)

upload_canvas = Canvas(main, width=300, height=100, bg="white")
upload_canvas.place(x=410, y=150)

latency_meter = Meter(
    latency_canvas,
    metersize=160,
    padding=5,
    amountused=0,
    metertype="semi",
    subtext="ms",
    interactive=False,
)
latency_meter.pack()

download_meter = Meter(
    download_canvas,
    metersize=160,
    padding=5,
    amountused=0,
    metertype="semi",
    subtext="Mbps",
    interactive=False,
)
download_meter.pack()

upload_meter = Meter(
    upload_canvas,
    metersize=160,
    padding=5,
    amountused=0,
    metertype="semi",
    subtext="Mbps",
    interactive=False,
)
upload_meter.pack()

canvas_network_widget.place(x=20, y=350)
canvas = FigureCanvasTkAgg(fig, master=main)
canvas_widget = canvas.get_tk_widget()
canvas_widget.place(x=600, y=150)

threading.Thread(target=update_cpu_graph, daemon=True).start()
threading.Thread(target=update_network_parameters, daemon=True).start()
threading.Thread(target=update_graph, daemon=True).start()
threading.Thread(target=clear_log_directory_periodically, args=('C:/snort/log',), daemon=True).start()
threading.Thread(target=run_snort_periodically, args=(5,), daemon=True).start()
threading.Thread(target=check_alerts_periodically, args=('C:/snort/log/alert.ids',), daemon=True).start()

label_network = Label(main, text="Network Performance Monitoring", font=('Times New Roman', 24, 'bold'))
label_network.place(x=300, y=10)

main.mainloop()
