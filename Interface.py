import serial
import time
import matplotlib.pyplot as plt
from collections import deque

# Connect to your serial port (change 'COM3' or '/dev/ttyUSB0' as needed)
arduino = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2)  # Allow Arduino to reset

# Store the last 1000 data points
data = deque([0.0]*100, maxlen=100)

# Set up plot
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(data)
ax.set_ylim(0, 5)  # Adjust based on your sensor range

while True:
    try:
        if arduino.in_waiting > 0:
            raw = arduino.readline().decode('utf-8', errors='ignore').strip()

            try:
                value = float(raw)
                data.append(value)

                # Update plot
                line.set_ydata(data)
                line.set_xdata(range(len(data)))
                ax.relim()
                #ax.autoscale_view()
                plt.draw()
                plt.pause(0.00001) 
            except ValueError:
                pass  # Ignore bad lines
    except KeyboardInterrupt:
        print("Stopped by user.")
        break
