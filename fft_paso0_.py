import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq

# CONFIGURA ESTO:
archivo_csv = "analog_readings.csv"           # Tu archivo de entrada
columna_datos = "AnalogValue"             # Nombre de la columna con los datos
duracion_total_segundos = 6000        # <-- Define el tiempo total de la medición
tamaño_ventana = 1000               # Número de muestras por ventana

# Cargar datos
data = pd.read_csv(archivo_csv)
valores = data[columna_datos].to_numpy()
n_total = len(valores)
Fs = n_total / duracion_total_segundos  # Frecuencia de muestreo

#Funcion de FFT para la frecuencia
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

# Procesar ventanas
frecs_fft = []
frecs_zero = []
indices = []

step = tamaño_ventana // 2  # Solapamiento del 50%

for i in range(0, n_total - tamaño_ventana + 1, step):
    ventana = valores[i:i + tamaño_ventana]
    #print(ventana[1:10])
    f_fft = calcular_frecuencia_dominante(ventana, Fs)


    frecs_fft.append(f_fft)

    indices.append(i // step)

# Guardar en CSV
resultado = pd.DataFrame({
    "ventana": indices,
    "frecuencia_fft": frecs_fft,
})
resultado.to_csv("frecuencias_calculadas.csv", index=False)

# Graficar
plt.plot(indices, frecs_fft, label="FFT", marker='o')
plt.xlabel("Ventana")
plt.ylabel("Frecuencia estimada (Hz)")
plt.title("Frecuencia principal por ventana")
plt.legend()
plt.grid(True)
plt.show()
