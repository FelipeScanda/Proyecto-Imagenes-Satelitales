import os
import re
import numpy as np
import pandas as pd
import rasterio
from rasterio import warp

# Función para cargar coordenadas de sensores desde CSV
def cargar_sensores(path_csv):
    """
    Carga el CSV de sensores y retorna un DataFrame con columnas:
    sensor_id, sensor_lat, sensor_lon.
    """
    df = pd.read_csv(path_csv)
    df = df.rename(columns={'sensor_device_id':'sensor_id',
                            'sensor_lat':'latitud',
                            'sensor_lon':'longitud'})
    return df

# Función para seleccionar el sensor más central (mínima distancia al centro promedio)
def seleccionar_sensor_central(df_sensores):
    """
    Calcula la ubicación geográfica media de los sensores y selecciona
    el sensor cuya lat/lon esté más cerca del centro (distancia euclidiana).
    """
    lat_media = df_sensores['latitud'].mean()
    lon_media = df_sensores['longitud'].mean()
    # Calcular distancia al punto medio
    distancias = np.sqrt((df_sensores['latitud'] - lat_media)**2 +
                         (df_sensores['longitud'] - lon_media)**2)
    idx_min = distancias.idxmin()
    return df_sensores.loc[idx_min]

# Función para obtener la lista de archivos de bandas para cada fecha
def listar_bandas_por_fecha(carpeta):
    """
    Escanea la carpeta dada y organiza los archivos .tif por fecha.
    Retorna un diccionario fecha -> lista de archivos de bandas.
    Asume que el nombre de archivo inicia con la fecha (YYYY-MM-DD).
    """
    archivos = [f for f in os.listdir(carpeta) if f.endswith(".tif")]
    bandas_por_fecha = {}
    for archivo in archivos:
        # Extraer fecha del nombre (antes del primer guión bajo)
        fecha = archivo.split('_')[0]
        # Filtrar archivos que son de bandas válidas (B01-B12, AOT, WVP, SCL, TCI)
        if re.search(r'_band_(B0[1-9]|B1[0-2]|AOT|WVP|SCL|TCI)\.tif$', archivo):
            bandas_por_fecha.setdefault(fecha, []).append(archivo)
    return bandas_por_fecha

# Función para extraer valor de píxel en coordenadas de un raster
def obtener_valor_pixel(ruta_raster, lat, lon):
    """
    Abre el raster en ruta_raster, convierte lat/lon (EPSG:4326) al CRS del raster,
    encuentra la fila y columna correspondiente y devuelve el valor de píxel.
    También extrae metadatos (CRS, resolución, ancho, alto).
    """
    with rasterio.open(ruta_raster) as src:
        # Transformar lat/lon (EPSG:4326) al CRS del dataset
        lon_img, lat_img = warp.transform('EPSG:4326', src.crs, [lon], [lat])
        # Obtener índice de fila, columna (index asume coordenadas en el CRS del raster:contentReference[oaicite:3]{index=3})
        fila, col = src.index(lon_img[0], lat_img[0])
        # Leer el valor de píxel (primera banda)
        valor = src.read(1)[fila, col]
        # Extraer metadatos
        crs = src.crs.to_string()
        resolucion = src.res  # tuple (xres, yres)
        ancho = src.width
        alto = src.height
    return valor, crs, resolucion, ancho, alto

# Función principal que recorre fechas y bandas, y genera el CSV de salida
def procesar_imagenes(carpeta, csv_sensores, output_csv):
    # Cargar y seleccionar sensor central
    sensores = cargar_sensores(csv_sensores)
    sensor_central = seleccionar_sensor_central(sensores)
    sensor_id = sensor_central['sensor_id']
    lat_sens = sensor_central['latitud']
    lon_sens = sensor_central['longitud']

    print(f"Sensor central seleccionado: {sensor_id} (lat {lat_sens}, lon {lon_sens})")

    # Obtener archivos de bandas organizados por fecha
    bandas_por_fecha = listar_bandas_por_fecha(carpeta)

    # Listado de filas para el DataFrame final
    filas = []
    for fecha, archivos in bandas_por_fecha.items():
        for archivo in archivos:
            ruta = os.path.join(carpeta, archivo)
            # Obtener nombre de banda del archivo (texto después de 'band_')
            nombre_banda = archivo.split('_band_')[-1].replace('.tif','')
            # Omitir banda 'CLD' si aparece
            if nombre_banda == 'CLD':
                continue
            # Obtener valor de píxel y metadatos
            valor, crs, resol, ancho, alto = obtener_valor_pixel(ruta, lat_sens, lon_sens)
            # Agregar fila con toda la información requerida
            filas.append({
                'fecha': fecha,
                'sensor_id': sensor_id,
                'latitud': lat_sens,
                'longitud': lon_sens,
                'nombre_banda': nombre_banda,
                'valor_pixel': valor,
                'crs': crs,
                'resolucion': resol,
                'ancho': ancho,
                'alto': alto,
                'nombre_archivo': archivo
            })

    # Crear DataFrame y guardar CSV
    df = pd.DataFrame(filas)
    df.to_csv(output_csv, index=False)
    print(f"Resultados guardados en {output_csv}")

# Ejecución del proceso (asumiendo carpeta 'crops' y que existe 'coordenadas sensores.csv')
if __name__ == "__main__":
    carpeta_imagenes = "crops"
    archivo_sensores = "coordenadas sensores.csv"
    archivo_salida = "valores_pixeles.csv"
    procesar_imagenes(carpeta_imagenes, archivo_sensores, archivo_salida)

# Nota sobre la banda CLD (máscara de nubes):
# Sentinel-2 L2A no incluye una banda CLD específica por defecto. Para obtener una máscara de nubes
# se puede usar la colección "COPERNICUS/S2_CLOUD_PROBABILITY" de Google Earth Engine
# o la banda de clasificación de escena (SCL) disponible, o descargar el producto de
# probabilidad de nube generado con s2cloudless:contentReference[oaicite:4]{index=4}.
