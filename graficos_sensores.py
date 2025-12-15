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

# Seleccionar variables relevantes
data = df_sensor[[
    "time_sensor_tx_local",
    "Hum_SHT",
    "TempC_SHT"
]].copy()

print("\n===== Estadísticas descriptivas =====")
vars_numericas = data.drop(columns=["time_sensor_tx_local"])
print(vars_numericas.describe())

# 1) Gráfico humedad vs tiempo

plt.figure(figsize=(12, 5))
plt.plot(data["time_sensor_tx_local"], data["Hum_SHT"], label="Humedad (%)")
plt.xlabel("Tiempo")
plt.ylabel("Humedad relativa (%)")
plt.title(f"Humedad vs Tiempo — {sensor_id}")
plt.legend()
plt.tight_layout()

save_path = os.path.join(plots_dir, "humedad_tiempo.png")
plt.savefig(save_path, dpi=300)
plt.close()

print(f"Guardado: {save_path}")

# 2) Gráfico temperatura vs tiempo

plt.figure(figsize=(12, 5))
plt.plot(data["time_sensor_tx_local"], data["TempC_SHT"], label="TempC_SHT", color="orange")
plt.xlabel("Tiempo")
plt.ylabel("Temperatura (°C)")
plt.title(f"Temperatura vs Tiempo — {sensor_id}")
plt.legend()
plt.tight_layout()

save_path = os.path.join(plots_dir, "temperatura_tiempo.png")
plt.savefig(save_path, dpi=300)
plt.close()

print(f"Guardado: {save_path}")

# 3) Histogramas

variables = ["Hum_SHT", "TempC_SHT"]

for var in variables:
    plt.figure(figsize=(7, 5))
    sns.histplot(data[var], kde=True, color="blue")
    plt.title(f"Distribución de {var} — {sensor_id}")
    plt.xlabel(var)
    plt.ylabel("Frecuencia")
    plt.tight_layout()

    save_path = os.path.join(plots_dir, f"hist_{var}.png")
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"Guardado: {save_path}")

print("\nTodos los gráficos han sido guardados en la carpeta /plots")