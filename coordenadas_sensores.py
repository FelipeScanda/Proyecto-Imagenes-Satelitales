import pandas as pd

# Cargar el CSV
df = pd.read_csv("./agritorre_2_months.csv/agritorre_2_months.csv")

# Seleccionar columnas relevantes
coord_cols = ["sensor_device_id", "sensor_lat", "sensor_lon"]

# Extraer solo esas columnas
coords = df[coord_cols]

# Eliminar filas duplicadas
coords_unicos = coords.drop_duplicates()

# Guardar en un archivo CSV
coords_unicos.to_csv("coordenadas sensores.csv", index=False)