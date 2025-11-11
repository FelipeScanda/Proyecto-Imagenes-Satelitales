import rasterio
import os
import csv
import re
from datetime import datetime

# Carpeta donde tienes las imágenes descargadas
input_folder = "crops_TCI"
output_csv = "metadatos_imagenes.csv"

# Expresión regular para detectar fechas tipo 20250712T144611
fecha_regex = re.compile(r"(\d{8}T\d{6})")

rows = []

for filename in os.listdir(input_folder):
    if filename.endswith(".tif"):
        filepath = os.path.join(input_folder, filename)

        # Leer metadatos con rasterio
        with rasterio.open(filepath) as src:
            tags = src.tags()
            crs = src.crs
            res = src.res
            width = src.width
            height = src.height

        # Buscar fecha en los metadatos
        fecha = None
        for key, value in tags.items():
            if "DATE" in key.upper() or "TIME" in key.upper() or "SENSING" in key.upper():
                fecha = value
                break

        # Si no se encuentra en metadatos, buscar en el nombre del archivo
        if not fecha:
            match = fecha_regex.search(filename)
            if match:
                fecha = match.group(1)
                fecha = datetime.strptime(fecha, "%Y%m%dT%H%M%S").isoformat()
            else:
                fecha = "Desconocida"

        rows.append({
            "archivo": filename,
            "fecha": fecha,
            "crs": crs,
            "resolucion": res,
            "ancho": width,
            "alto": height
        })

# Guardar en CSV
with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["archivo", "fecha", "crs", "resolucion", "ancho", "alto"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Metadatos guardados en {output_csv}")
