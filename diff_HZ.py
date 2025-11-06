import pandas as pd
import numpy as np

# Cargar archivo CSV
df = pd.read_csv('frecuencias_calculadas.csv')  # Reemplaza con el nombre real

# Suponiendo que los datos están en la primera columna
valores = df['frecuencia_fft'].sort_values().reset_index(drop=True)

# Calcular diferencias entre elementos consecutivos
diferencias = valores.diff().dropna()

# Ordenar diferencias
diferencias_ordenadas = diferencias.sort_values().reset_index(drop=True)

print(diferencias_ordenadas)

# Imprimir el valor mínimo
valor_minimo = diferencias_ordenadas.iloc[0]
print(f"Diferencia mínima ordenada: {valor_minimo}")
