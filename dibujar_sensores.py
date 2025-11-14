import rasterio
from rasterio import warp
from rasterio.plot import reshape_as_image
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def latlon_to_pixel(dataset, lat, lon):
    # Transformar lat/lon a sistema del raster
    lon_img, lat_img = rasterio.warp.transform('EPSG:4326', 'EPSG:32719', [lon], [lat])

    # Obtener fila y columna
    fila, col = dataset.index(lon_img[0], lat_img[0])
    return col, fila


# Cargar la imagen satelital
src = "./crops_TCI/2025-07-06_S2C_orbit_096_tile_19HCB_L2A_band_TCI.tif"
imagen = rasterio.open(src)

print(imagen.meta)

# Leer bandas
img = imagen.read([1, 2, 3])
img = reshape_as_image(img)

# Cargar coordenadas de sensores
sensores = pd.read_csv("coordenadas sensores.csv")

# Dibujar imagen
plt.figure(figsize=(10,10))
plt.imshow(img)
plt.title("Sensores sobre la imagen satelital")
plt.axis("off")

# Dibujar sensores
for _, row in sensores.iterrows():
    lat = row["sensor_lat"]
    lon = row["sensor_lon"]

    col, fila = latlon_to_pixel(imagen, lat, lon)

    # Dibujar punto
    plt.scatter(col, fila, s=10, facecolor="red")

plt.show()