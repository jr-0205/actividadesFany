# Guion de video — Práctica 7.1

Duración objetivo: **1:35 a 1:55 minutos**.

## 0:00–0:15

“Esta es mi Práctica 7 sobre predicción y clasificación de ventas de una tienda de productos tecnológicos. La desarrollé en Python para Google Colab utilizando Pandas, scikit-learn y Matplotlib.”

## 0:15–0:30

“El conjunto contiene 20 registros con producto, precio, visitas, publicidad, descuento y ventas. También se crea la variable Demanda: es Alta cuando se venden 50 unidades o más y Baja cuando se venden menos de 50.”

## 0:30–0:52

“El primer modelo es una regresión lineal. Utiliza precio, visitas, publicidad y descuento para predecir las unidades vendidas. Al ejecutar la evaluación obtengo las predicciones de prueba y las métricas MAE, MSE y R cuadrada. En esta ejecución el MAE es aproximadamente 5.49 y R cuadrada es 0.854.”

## 0:52–1:15

“El segundo modelo es un árbol de decisión que clasifica la demanda como Alta o Baja. La evaluación muestra la exactitud, el reporte de clasificación y la matriz de confusión. En los cinco registros de prueba clasificó correctamente los cinco, aunque este resultado debe tomarse con cautela porque el conjunto es pequeño y ficticio.”

## 1:15–1:38

“Finalmente pruebo una nueva laptop con precio de 13,500 pesos, 1,500 visitas, 3,000 pesos de publicidad y 15 por ciento de descuento. El modelo estima aproximadamente 82.35 unidades y clasifica la demanda como Alta.”

## 1:38–1:52

“Con la regresión se puede apoyar la planificación de inventario y con la clasificación se pueden identificar niveles de demanda. Los dos modelos son complementarios y sus predicciones no garantizan ventas futuras.”

## Qué mostrar en pantalla

1. Notebook abierto en Colab.
2. Tabla del conjunto de datos.
3. Celda de regresión y sus métricas.
4. Gráfica de valores reales contra predichos.
5. Celda de clasificación y matriz de confusión.
6. Celda final de la nueva laptop.
