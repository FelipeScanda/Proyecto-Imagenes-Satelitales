import pandas as pd
import numpy as np

#Cargar dataset y agrupar por fecha
df = pd.read_csv("valores_pixeles.csv", parse_dates=["fecha"])

#Separar SCL de las demas bandas (quedan 2 dataframes separados)
df_scl = df[df["nombre_banda"] == "SCL"].copy()
df_bandas = df[df["nombre_banda"] != "SCL"].copy()

#Renombrar la columna de SCL
df_scl = df_scl.rename(columns={"valor_pixel": "SCL"})

#Unir los dataframes
df_merged = df_bandas.merge(
    df_scl[["fecha", "latitud", "longitud", "SCL"]],
    on=["fecha", "latitud", "longitud"],
    how="left"
)

#Filtrar los valores cuyo SCL sea 8 o 9 (prob. de nubes)
nube = [8, 9]

umbrales = {
    "B01": 2000,
    "B02": 2000,
    "B03": 2000,
    "B04": 2000,
    "B05": 2000,
    "B06": 2500,
    "B07": 2500,
    "B08": 2500,
    "B09": 2500,
    "B11": 3500,
    "B12": 3000
}

df_merged["valor_filtrado"] = df_merged.apply(
    lambda r: np.nan
    if (
        r["SCL"] in nube or
        (r["nombre_banda"] in umbrales and r["valor_pixel"] > umbrales[r["nombre_banda"]])
    )
    else r["valor_pixel"],
    axis=1
)

#Guardar en csv.
df_merged.to_csv("valores_pixeles_filtrados.csv", index=False)