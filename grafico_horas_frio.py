import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# CONFIGURACIÓN
csv_path = "./agritorre_2_months.csv/agritorre_2_months.csv"
sensor_id = "eui-a8404173735a97b9"
plots_dir = "plots"

# Crear carpeta si no existe
os.makedirs(plots_dir, exist_ok=True)

# CARGAR DATASET
df = pd.read_csv(csv_path)

# Filtrar sensor
df_sensor = df[df["sensor_device_id"] == sensor_id].copy()

# PROCESAR FECHA
df_sensor["time_sensor_tx_local"] = pd.to_datetime(
    df_sensor["time_sensor_tx_local"], errors="coerce", utc=True
)

df_sensor = df_sensor.dropna(subset=["time_sensor_tx_local"])

# Quitar timezone -> formato compatible con Matplotlib
df_sensor["time_sensor_tx_local"] = df_sensor["time_sensor_tx_local"].dt.tz_convert(None)

#Cambio de nombre
df_sensor["fecha"] = df_sensor["time_sensor_tx_local"]

#Eliminar datos vacios
df_sensor = df_sensor.dropna(subset=["fecha", "TempC_SHT"])

#Ordenar por hora
df_sensor = df_sensor.sort_values("fecha")

#Valor para calcular horas frio (cada dato contribuye 1/3 de hora frio)
delta_horas = 20/60

#Calcular horas frio (todas las temperaturas menores a 7.2˚C)
df_sensor["hora_frio"] = (df_sensor["TempC_SHT"] <= 7.2) * delta_horas

# Horas frío acumuladas
df_sensor["horas_frio_acum"] = df_sensor["hora_frio"].cumsum()

#Cargar dataset bandas
df_bandas = pd.read_csv("valores_pixeles.csv")

df_bandas["fecha"] = pd.to_datetime(
    df_bandas["fecha"],
    errors="coerce",
    utc=True
).dt.tz_convert(None)

#Eliminar datos vacios y ordenar por fecha
df_bandas = df_bandas.dropna(subset=["fecha", "valor_pixel"])
df_bandas = df_bandas.sort_values("fecha")

output_dir = "graficos_bandas_vs_horas_frio"
os.makedirs(output_dir, exist_ok=True)

#Graficas horas frio vs valores bandas
for banda, df_b in df_bandas.groupby("nombre_banda"):

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # --- Banda (eje izquierdo) ---
    ax1.plot(
        df_b["fecha"],
        df_b["valor_pixel"],
        marker="o",
        linestyle="-",
        label=f"Banda {banda}"
    )

    ax1.set_xlabel("Fecha")
    ax1.set_ylabel("Valor del píxel")
    ax1.tick_params(axis="x", rotation=45)

    # --- Horas frío (eje derecho) ---
    ax2 = ax1.twinx()
    ax2.plot(
        df_sensor["time_sensor_tx_local"],
        df_sensor["horas_frio_acum"],
        linestyle="--",
        linewidth=2,
        label="Horas frío acumuladas"
    )

    ax2.set_ylabel("Horas frío acumuladas")

    # --- Leyenda combinada ---
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title(f"Evolución temporal – Banda {banda} vs Horas Frío")
    plt.tight_layout()

    # --- Guardar figura ---
    filename = f"banda_{banda}_horas_frio.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300)
    plt.close()

    print(f"Guardado: {filepath}")

#Graficar temperatura vs valores bandas
output_dir = "graficos_bandas_vs_temperatura"
os.makedirs(output_dir, exist_ok=True)

for banda, df_b in df_bandas.groupby("nombre_banda"):

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # --- Banda (eje izquierdo) ---
    ax1.plot(
        df_b["fecha"],
        df_b["valor_pixel"],
        marker="o",
        linestyle="-",
        label=f"Banda {banda}"
    )

    ax1.set_xlabel("Fecha")
    ax1.set_ylabel("Valor del píxel")
    ax1.tick_params(axis="x", rotation=45)

    # --- Temperatura (eje derecho) ---
    ax2 = ax1.twinx()
    ax2.plot(
        df_sensor["time_sensor_tx_local"],
        df_sensor["TempC_SHT"],
        linestyle="-",
        linewidth=2,
        label="Temperatura",
        color = "green"
    )

    ax2.set_ylabel("Temperatura ˚C")

    # --- Leyenda combinada ---
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title(f"Evolución temporal – Banda {banda} vs Temperatura")
    plt.tight_layout()

    # --- Guardar figura ---
    filename = f"banda_{banda}_temperatura.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300)
    plt.close()

    print(f"Guardado: {filepath}")