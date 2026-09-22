import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


# ============================================================
# PRÁCTICA 4.1
# Modelo supervisado de predicción con Regresión Lineal
# ============================================================

# 1. Datos de entrenamiento
# Tamaño de las casas en metros cuadrados.
X_tamano = np.array([50, 65, 80, 100, 120, 150]).reshape(-1, 1)

# Precio de las casas en miles de dólares.
y_precio = np.array([150, 185, 210, 260, 300, 380])


# 2. Crear y entrenar el modelo
modelo = LinearRegression()
modelo.fit(X_tamano, y_precio)

print("¡Modelo entrenado con éxito!")
print("-" * 50)


# 3. Realizar una predicción
# El modelo no recibió una casa de 90 m² durante el entrenamiento.
casa_nueva_m2 = 90
prediccion = modelo.predict([[casa_nueva_m2]])

print(f"Para una casa nueva de {casa_nueva_m2} m²:")
print(
    f"-> El precio estimado por el modelo es de: "
    f"${prediccion[0]:.2f} miles de dólares"
)
print("-" * 50)

# Información adicional del modelo.
print(f"Pendiente aprendida por el modelo: {modelo.coef_[0]:.4f}")
print(f"Intersección de la recta: {modelo.intercept_:.4f}")


# 4. Crear puntos para dibujar la línea de regresión
X_linea = np.linspace(40, 160, 100).reshape(-1, 1)
y_linea = modelo.predict(X_linea)


# 5. Crear la gráfica
plt.figure(figsize=(9, 6))

plt.scatter(
    X_tamano,
    y_precio,
    color="blue",
    label="Casas reales del mercado",
    s=100,
)

plt.plot(
    X_linea,
    y_linea,
    color="red",
    linestyle="--",
    linewidth=2,
    label="Línea de tendencia (Regresión Lineal)",
)

plt.scatter(
    casa_nueva_m2,
    prediccion[0],
    color="red",
    marker="*",
    s=250,
    label=f"Predicción casa {casa_nueva_m2} m²",
)

plt.annotate(
    f"${prediccion[0]:.2f}",
    (casa_nueva_m2, prediccion[0]),
    textcoords="offset points",
    xytext=(10, 10),
)

plt.title(
    "Predicción de Precios de Casas usando Machine Learning",
    fontsize=14,
)
plt.xlabel("Tamaño de la casa (m²)", fontsize=12)
plt.ylabel("Precio (miles de dólares)", fontsize=12)
plt.grid(True, linestyle=":", alpha=0.6)
plt.legend()
plt.tight_layout()

# Mostrar la gráfica en pantalla.
plt.show()
