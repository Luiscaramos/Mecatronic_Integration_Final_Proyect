import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuración serial
puerto = 'COM5'
baudios = 115200
arduino = serial.Serial(puerto, baudios, timeout=1)
time.sleep(2)

# Parámetros
N = 7500  # Número de muestras
ventana = np.hamming(N)
fs = 5000  # Frecuencia de muestreo fija en Hz

# Inicialización
tiempos = []
frecuencias_detectadas = []
t_inicio_global = time.time()

# Gráfica interactiva
plt.ion()
fig, ax = plt.subplots()

# Línea de frecuencia
linea, = ax.plot([], [], marker='o', linestyle='-', color='blue')

# Configurar gráfica
ax.set_title("Frecuencia Detectada vs Tiempo")
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Frecuencia (Hz)")
ax.grid()
ax.set_ylim(50, 70)
ax.set_xlim(0, 60)

# Crear recuadro para el indicador
indicador = fig.add_axes([0.8, 0.75, 0.12, 0.12])
indicador.set_xticks([])
indicador.set_yticks([])
indicador.set_title("Estado")

# Inicializar estado como gris
color_estado = 'grey'
rect = mpatches.Rectangle((0, 0.4), 1, 0.6, facecolor=color_estado)
indicador.add_patch(rect)

# Texto de estado
texto_estado = indicador.text(0.5, 0.1, "Esperando...",
                              fontsize=8, ha='center', va='center')

# Variables para conteo de tiempos anormales (en minutos)
tiempo_anormal_59_4 = 0
tiempo_anormal_60_6 = 0
tiempo_anormal_59_7 = 0
tiempo_anormal_60_3 = 0

# Duración total en segundos
duracion_total = 60
segundos_transcurridos = 0

def parabola(x, a, b, c):
    return a * x**2 + b * x + c

def peak_interpolate(freqs, fft_data, idx):
    if idx == 0 or idx == len(fft_data)-1:
        return freqs[idx]
    vals = fft_data[idx-1:idx+2]
    xs = [-1, 0, 1]
    A = np.vstack([xs**2, xs, np.ones_like(xs)]).T
    try:
        a, b, c = np.linalg.lstsq(A, vals, rcond=None)[0]
        peak_x = -b / (2*a)
        return freqs[idx] + peak_x * (freqs[1] - freqs[0])
    except:
        return freqs[idx]

# Bucle de adquisición por segundo
while segundos_transcurridos < duracion_total:
    t_inicio = time.time()
    datos = []

    # Leer N muestras
    while len(datos) < N:
        try:
            linea_serial = arduino.readline().decode().strip()
            if linea_serial:
                valor = int(linea_serial)
                datos.append(valor)
        except Exception as e:
            print(f"Error leyendo puerto serial: {e}")
            continue

    # Procesamiento
    muestras = np.array(datos, dtype=np.float64)
    muestras -= np.mean(muestras)
    muestras *= ventana

    # FFT y frecuencia dominante
    fft_resultado = np.abs(np.fft.rfft(muestras))
    freqs = np.fft.rfftfreq(N, d=1/fs)

    idx_max = np.argmax(fft_resultado[5:]) + 5
    freq_dom = peak_interpolate(freqs, fft_resultado, idx_max)

    tiempo_actual = time.time() - t_inicio_global

    # Determinar estado
    if max(muestras) < 50:
        color_estado = 'red'
    else:
        # Acumular tiempos anormales
        if freq_dom < 59.4:
            tiempo_anormal_59_4 += 1/60
        else:
            tiempo_anormal_59_4 = 0

        if freq_dom > 60.6:
            tiempo_anormal_60_6 += 1/60
        else:
            tiempo_anormal_60_6 = 0

        if freq_dom < 59.7:
            tiempo_anormal_59_7 += 1/60
        else:
            tiempo_anormal_59_7 = 0

        if freq_dom > 60.3:
            tiempo_anormal_60_3 += 1/60
        else:
            tiempo_anormal_60_3 = 0

        # Evaluar condiciones de estado
        if (freq_dom < 59 or freq_dom > 61 or
            tiempo_anormal_59_4 >= 9 or
            tiempo_anormal_60_6 >= 9 or
            tiempo_anormal_59_7 >= 20 or
            tiempo_anormal_60_3 >= 20):
            color_estado = 'yellow'
        else:
            color_estado = 'green'

    # Actualizar gráficas
    tiempos.append(tiempo_actual)
    frecuencias_detectadas.append(freq_dom)
    linea.set_xdata(tiempos)
    linea.set_ydata(frecuencias_detectadas)
    ax.relim()
    ax.autoscale_view(True, True, False)

    # Actualizar indicador de estado
    rect.set_facecolor(color_estado)

    if color_estado == 'red':
        texto_estado.set_text("Sensor not connected")
    elif color_estado == 'yellow':
        texto_estado.set_text("Abnormal grid detection")
    elif color_estado == 'green':
        texto_estado.set_text("Correct sensing")
    else:
        texto_estado.set_text("Esperando...")

    fig.canvas.draw()
    fig.canvas.flush_events()

    # Esperar hasta completar 1 segundo exacto
    t_duracion = time.time() - t_inicio
    if t_duracion < 1:
        time.sleep(1 - t_duracion)

    segundos_transcurridos += 1
    print(f"{freq_dom:.2f} Hz")

# Cerrar conexión y mostrar gráfica final
arduino.close()
plt.ioff()
plt.show()