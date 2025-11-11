import rasterio
import numpy as np
from rasterio.windows import Window
from rasterio.warp import transform
import matplotlib.pyplot as plt
from PIL import Image

# Coordenadas del punto central en lat/lon
lat, lon = -34.392585, -70.810322

# Tamaño del recorte
ventana = 500  

# Rutas de las bandas
b_path = "imagen/GRANULE/L1C_T19HCB_A054033_20251026T144508/IMG_DATA/T19HCB_20251026T143801_B02.jp2"  # Azul
g_path = "imagen/GRANULE/L1C_T19HCB_A054033_20251026T144508/IMG_DATA/T19HCB_20251026T143801_B03.jp2"  # Verde
r_path = "imagen/GRANULE/L1C_T19HCB_A054033_20251026T144508/IMG_DATA/T19HCB_20251026T143801_B04.jp2"  # Rojo

# Función para recortar una banda dado un punto
def recortar_banda(path, lat, lon, ventana):
    with rasterio.open(path) as src:
        # Convertir coordenadas geográficas a sistema de la imagen
        lon_img, lat_img = transform('EPSG:4326', src.crs, [lon], [lat])
        fila, col = src.index(lon_img[0], lat_img[0])

        # Crear ventana centrada en el punto
        window = Window(col - ventana, fila - ventana, 2*ventana, 2*ventana)

        # Leer solo la región
        banda = src.read(1, window=window)
        return banda

#  Recortar las tres bandas 
red = recortar_banda(r_path, lat, lon, ventana)
green = recortar_banda(g_path, lat, lon, ventana)
blue = recortar_banda(b_path, lat, lon, ventana)

# Combinar 
rgb = np.dstack((red, green, blue))

# Normalizar para visualización
rgb_norm = rgb / np.percentile(rgb, 99)
rgb_norm = np.clip(rgb_norm, 0, 1)

# Guardar como imagen PNG
plt.imsave("campo.png", rgb_norm)
print(f" Imagen guardada correctamente: campo.png")
