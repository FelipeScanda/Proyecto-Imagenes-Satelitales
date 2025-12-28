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

df_merged["valor_filtrado"] = np.where(
    df_merged["SCL"].isin(nube),
    np.nan,
    df_merged["valor_pixel"]
)

#Guardar en csv.
df_merged.to_csv("valores_pixeles_filtrados.csv", index=False)