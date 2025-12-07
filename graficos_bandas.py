import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# CONFIGURACIÓN
csv_path = "pixeles_por_banda.csv"   # Cambiar si es necesario
plots_dir = "plots_pixeles"

sns.set(style="whitegrid")

# Crear carpeta si no existe
os.makedirs(plots_dir, exist_ok=True)

# CARGAR DATASET
df = pd.read_csv(csv_path)

# Convertir fecha
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", utc=True)
df = df.dropna(subset=["fecha"])
df["fecha"] = df["fecha"].dt.tz_convert(None)

# ESTADÍSTICAS DESCRIPTIVAS
stats = df.groupby("nombre_banda")["valor_pixel"].describe()

print("\n===== Estadísticas descriptivas por banda =====")
print(stats)

# Guardar estadísticas en CSV
stats.to_csv(os.path.join(plots_dir, "estadisticas_pixeles.csv"))

# 1) Serie temporal por banda
for banda in df["nombre_banda"].unique():
    sub = df[df["nombre_banda"] == banda]

    plt.figure(figsize=(12, 5))
    plt.plot(sub["fecha"], sub["valor_pixel"], label=banda)
    plt.xlabel("Fecha")
    plt.ylabel("Valor del píxel")
    plt.title(f"Evolución temporal — Banda {banda}")
    plt.legend()
    plt.tight_layout()

    save_path = os.path.join(plots_dir, f"serie_{banda}.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Guardado: {save_path}")

# 2) Histogramas por banda
for banda in df["nombre_banda"].unique():
    sub = df[df["nombre_banda"] == banda]

    plt.figure(figsize=(7, 5))
    sns.histplot(sub["valor_pixel"], kde=True, color="blue")
    plt.title(f"Histograma — Banda {banda}")
    plt.xlabel("Valor del píxel")
    plt.ylabel("Frecuencia")
    plt.tight_layout()

    save_path = os.path.join(plots_dir, f"hist_{banda}.png")
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"Guardado: {save_path}")

# 3) Correlación entre bandas
pivot = df.pivot_table(
    index="fecha",
    columns="nombre_banda",
    values="valor_pixel"
)

# Quitar columnas vacías
pivot = pivot.dropna(axis=1, how="all")

corr = pivot.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlación entre bandas")
plt.tight_layout()

save_path = os.path.join(plots_dir, "correlacion_bandas.png")
plt.savefig(save_path, dpi=300)
plt.close()

print(f"Guardado: {save_path}")

print("\nTodos los gráficos fueron guardados en /plots_pixeles")
