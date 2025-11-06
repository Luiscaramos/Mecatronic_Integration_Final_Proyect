import numpy as np
import serial
import time
from collections import deque
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
import sys

# Prueba sin datos reales commentar cuando se conecte dispositivo
with open('Datos_Reales.txt', 'r') as file:
    datos = [float(line.strip()) for line in file]

print(datos)


# === Configuration ===
N = 1000  # Number of samples in window
offset = 2.5  # Midpoint of sensor signal (0V of AC)
show_voltage = True  # Change this to False to plot frequency

# === Data Buffers ===
voltajes = deque([0.0] * N, maxlen=N)
frecuencias = deque([0.0] * N, maxlen=N)
frecuencia_actual = 0.0
ultimo_cruce = None

# === PyQtGraph GUI Setup ===
app = QtWidgets.QApplication(sys.argv)
win = pg.GraphicsLayoutWidget(title="Voltaje o Frecuencia en Tiempo Real")
plot = win.addPlot(title="Señal")
curve = plot.plot()
plot.setYRange(-2.5, 2.5) if show_voltage else plot.setYRange(0, 100)
win.show()

# === Serial Setup ===
arduino = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2)  # Wait for Arduino to reset




def update():
    global voltajes, frecuencias, frecuencia_actual, ultimo_cruce

    while arduino.in_waiting:
        try:
            raw = arduino.readline().decode('utf-8', errors='ignore').strip()
            valor = float(raw)

            # Append voltage
            voltajes.append(valor)

            #variabl para probar
            voltajes = datos

            # Calcula la FFT
            fft_signal = np.fft.fft(datos)
            #frequency = np.fft.fftfreq(len(voltajes), d=voltajes[1]-voltajes[0])
            #print(frequency)
            
            print(fft_signal)
        except:
            pass
    
    curve.setData(list(datos.read()))
    plot.setYRange(-2.5, 2.5)
    plot.setTitle("Voltaje en Tiempo Real")

# === Timer to Refresh Plot ===
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)

# === Run Qt App ===
if __name__ == '__main__':
    sys.exit(app.exec_())