import rasterio
from rasterio.warp import transform
import numpy as np
import matplotlib.pyplot as plt

# Rutas de las bandas
b2_path = "imagen/GRANULE/L1C_T19HCB_A054033_20251026T144508/IMG_DATA/T19HCB_20251026T143801_B02.jp2"  # Azul
b3_path = "imagen/GRANULE/L1C_T19HCB_A054033_20251026T144508/IMG_DATA/T19HCB_20251026T143801_B03.jp2"  # Verde
b4_path = "imagen/GRANULE/L1C_T19HCB_A054033_20251026T144508/IMG_DATA/T19HCB_20251026T143801_B04.jp2"  # Rojo

# Leer las tres bandas
with rasterio.open(b2_path) as b2, \
     rasterio.open(b3_path) as b3, \
     rasterio.open(b4_path) as b4:
    
    blue = b2.read(1).astype(float)
    green = b3.read(1).astype(float)
    red = b4.read(1).astype(float)

# Normalizar valores 
red /= np.percentile(red, 99)
green /= np.percentile(green, 99)
blue /= np.percentile(blue, 99)

# Combinar en RGB
rgb = np.dstack((red, green, blue))
rgb = np.clip(rgb, 0, 1)

# Mostrar imagen RGB
plt.figure(figsize=(10,10))
plt.imshow(rgb)
plt.title("Imagen Sentinel-2 RGB (B4-B3-B2)")
plt.axis("off")
plt.show()

#Guardar imagen
plt.imsave("imagen(1).png", rgb)