import serial
import struct
import numpy as np
import csv
import tkinter as tk
from threading import Thread

# Variable global para acceder desde main()
color_display = None

class ColorDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Frecuencia Visual")
        self.root.geometry("255x255")
        self.frame = tk.Frame(self.root, width=255, height=255)
        self.frame.pack(fill="both", expand=True)
        self.running = True

        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Etiqueta de texto centrada
        self.label = tk.Label(self.frame, text="", font=("Arial", 12), bg="white")
        self.label.place(relx=0.5, rely=0.5, anchor="center")

    def on_close(self):
        self.running = False
        self.root.destroy()

    def set_color(self, color, text=""):
        self.frame.config(bg=color)
        self.label.config(text=text, bg=color)

    def start(self):
        self.root.mainloop()

# Cálculo de frecuencia dominante
def calcular_frecuencia_dominante(datos, fs):
    datos = np.array(datos, dtype=np.float64)
    N = len(datos)
    ventana = np.hamming(N)

    muestras = datos - np.mean(datos)
    muestras *= ventana

    fft_resultado = np.abs(np.fft.rfft(muestras))
    freqs = np.fft.rfftfreq(N, d=1/fs)

    idx_max = np.argmax(fft_resultado[5:]) + 5

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

# Procesamiento de datos desde el puerto serial
def main():
    global color_display
    port = 'COM5'  # Cambia esto a tu puerto
    baudrate = 115200
    fs = 118000 / 20  # Frecuencia de muestreo en Hz
    ventana_muestras = 1024

    ser = serial.Serial(port, baudrate, timeout=1)

    print("Esperando byte de inicio (0x00)...")
    while True:
        byte = ser.read(1)
        if byte == b'\x00':
            print("Byte de inicio recibido. Comenzando captura.")
            break

    with open('frecuencias_dominantes.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['FrecuenciaDominante_Hz', 'Color'])

        buffer = []
        try:
            while True:
                chunk = ser.read(200)
                for i in range(0, len(chunk), 2):
                    if i + 2 <= len(chunk):
                        sample = struct.unpack('<H', chunk[i:i+2])[0]
                        buffer.append(sample)

                        if len(buffer) >= ventana_muestras:
                            frecuencia = calcular_frecuencia_dominante(buffer[:ventana_muestras], fs)
                            
                            # Determinar color
                            if 59.9 <= frecuencia <= 60.1:
                                color = 'Verde'
                                color_display.set_color("green", f"{frecuencia:.2f} Hz - Verde")
                            elif frecuencia < 59.9:
                                color = 'Azul'
                                color_display.set_color("blue", f"{frecuencia:.2f} Hz - Azul")
                            else:
                                color = 'Rojo'
                                color_display.set_color("red", f"{frecuencia:.2f} Hz - Rojo")
                            
                            print(f"Frecuencia dominante: {frecuencia:.2f} Hz - {color}")
                            writer.writerow([frecuencia, color])
                            buffer = []  # Reiniciar ventana
        except KeyboardInterrupt:
            print("Captura detenida por el usuario.")
        finally:
            ser.close()

# Punto de entrada
if __name__ == '__main__':
    color_display = ColorDisplay()

    # Inicia el procesamiento de datos en segundo plano
    data_thread = Thread(target=main, daemon=True)
    data_thread.start()

    # Inicia la interfaz gráfica en el hilo principal
    color_display.start()
