import serial
import time
from collections import deque
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
import sys

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

# === Main Update Loop ===
def update():
    global voltajes, frecuencias, frecuencia_actual, ultimo_cruce

    while arduino.in_waiting:
        try:
            raw = arduino.readline().decode('utf-8', errors='ignore').strip()
            valor = float(raw)
            t_actual = time.time()

            # Append voltage
            voltajes.append(valor)

            # Detect zero crossing (at 2.5V)
            if len(voltajes) >= 2:
                v1, v2 = voltajes[-2], voltajes[-1]
                if (v1 - offset) < 0 and (v2 - offset) >= 0:
                    if ultimo_cruce is not None:
                        periodo = t_actual - ultimo_cruce
                        if periodo > 0:
                            frecuencia_actual = 1.0 / periodo
                    ultimo_cruce = t_actual

            # Append frequency value
            frecuencias.append(frecuencia_actual)

        except:
            pass

    # Update plot
    if show_voltage:
        curve.setData(list(voltajes))
        plot.setYRange(-2.5, 2.5)
        plot.setTitle("Voltaje en Tiempo Real")
    else:
        curve.setData(list(frecuencias))
        plot.setYRange(0, 100)
        plot.setTitle("Frecuencia Instantánea")

# === Timer to Refresh Plot ===
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)

# === Run Qt App ===
if __name__ == '__main__':
    sys.exit(app.exec_())
