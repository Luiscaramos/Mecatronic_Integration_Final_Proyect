import numpy as np
import serial
import time
from collections import deque
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
import sys
import matplotlib as plt

# Prueba sin datos reales commentar cuando se conecte dispositivo
#with open('Datos_Reales.txt', 'r') as file:
#    datos = [float(line.strip()) for line in file]

datos = np.loadtxt('analog_readings_20.csv', delimiter=',', skiprows=1001, usecols=0, max_rows=1000)

def calcular_frecuencia_dominante(datos, fs):

    datos = np.array(datos, dtype=np.float64)
    N = len(datos)
    ventana = np.hamming(N)

    # Eliminar componente DC y aplicar ventana
    muestras = datos - np.mean(datos)
    muestras *= ventana

    # FFT
    fft_resultado = np.abs(np.fft.rfft(muestras))
    freqs = np.fft.rfftfreq(N, d=1/fs)

    # Ignorar primeros 5 bins para evitar DC o ruido bajo
    idx_max = np.argmax(fft_resultado[5:]) + 5

    # Interpolación parabólica del pico
    def peak_interpolate(freqs, fft_data, idx):
        if idx == 0 or idx == len(fft_data) - 1:
            return freqs[idx]
        vals = fft_data[idx - 1:idx + 2]
        xs = [-1, 0, 1]
        A = np.vstack([np.square(xs), xs, np.ones_like(xs)]).T
        try:
            a, b, _ = np.linalg.lstsq(A, vals, rcond=None)[0]
            peak_x = -b / (2 * a)
            return freqs[idx] + peak_x * (freqs[1] - freqs[0])
        except Exception:
            return freqs[idx]

    freq_dom = peak_interpolate(freqs, fft_resultado, idx_max)
    return freq_dom


s = calcular_frecuencia_dominante(datos, (118000/20))

print(s)