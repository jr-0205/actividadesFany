# Guion de video — Práctica 9.1

Duración objetivo: **2:20 a 2:50 minutos**.

## 0:00–0:20

“Esta es mi Práctica 9 sobre segmentación de clientes de una agencia automotriz mediante aprendizaje no supervisado. Utilicé Python y Google Colab con K-Means, StandardScaler y PCA.”

## 0:20–0:45

“El conjunto contiene 50 clientes y nueve variables, como edad, ingreso, vehículos comprados, antigüedad, gasto en servicio, visitas al taller, kilómetros mensuales, monto de compra y financiamiento. Como las escalas son diferentes, primero se estandarizan con StandardScaler.”

## 0:45–1:10

“Después probé diferentes valores de K. En la gráfica del método del codo se observa una reducción importante hasta tres clusters y después las mejoras son menores, por lo que utilicé K igual a 3.”

## 1:10–1:35

“Al analizar los promedios aparecen tres perfiles. Un grupo tiene menor ingreso, menor compra y mayor uso de financiamiento; otro presenta valores intermedios; y el tercero tiene ingresos, compras, antigüedad y gasto en servicio más altos.”

## 1:35–1:58

“Para visualizar los grupos utilicé PCA y reduje las nueve variables a dos componentes. Las dos componentes explican aproximadamente 97.31 por ciento de la variabilidad, por lo que permiten observar gran parte de la estructura en una gráfica de dos dimensiones.”

## 1:58–2:20

“También analicé la complejidad aumentando la cantidad de clusters. La inercia disminuye, pero eso no significa que siempre sea mejor, porque demasiados grupos pueden representar casos particulares en lugar de patrones generales.”

## 2:20–2:45

“Finalmente, en el sistema interactivo capturo un cliente nuevo. Al presionar Segmentar cliente se aplica el mismo scaler y el modelo K-Means, se asigna un cluster y se muestra su ubicación en PCA. Esto demuestra la generalización a datos nuevos.”

## 2:45–2:55

“Con esto se cubren clustering, reducción de dimensionalidad, complejidad y generalización mediante aprendizaje no supervisado.”

## Qué mostrar en pantalla

1. Tabla inicial de los 50 registros.
2. Gráfica del método del codo.
3. Tabla de promedios de los tres clusters.
4. Gráfica PCA.
5. Gráfica de complejidad K=2 a K=10.
6. Sistema interactivo.
7. Capturar un cliente nuevo y presionar **Segmentar cliente**.
8. Mostrar cluster, perfil y gráfica PCA.
