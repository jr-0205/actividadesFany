# Reporte técnico — Práctica 9.1

## 1. Introducción

Una agencia automotriz desea conocer mejor el comportamiento de sus clientes para diseñar estrategias comerciales diferenciadas. Como no existe una clasificación previa, se aplica aprendizaje no supervisado para descubrir automáticamente grupos con características similares.

La práctica utiliza K-Means para clustering, StandardScaler para normalizar escalas y PCA para reducir nueve variables a dos componentes que facilitan la visualización.

## 2. Exploración de los datos

El conjunto contiene **50 registros** y **9 variables**.

### Variables

| Variable | Interpretación |
|---|---|
| edad | Edad del cliente |
| ingreso_mensual | Ingreso mensual |
| vehiculos_comprados | Número de vehículos adquiridos |
| antiguedad_cliente | Años como cliente |
| gasto_servicio | Gasto promedio en servicios |
| visitas_taller | Visitas al taller |
| km_mensuales | Kilómetros recorridos mensualmente |
| monto_compra | Monto promedio de compra |
| financiamiento | Uso de financiamiento (1 sí, 0 no) |

### Respuestas — Actividad 1

1. **¿Cuántos registros tiene?** 50.
2. **¿Cuántas variables contiene?** 9.
3. **¿Existen valores nulos?** No.
4. **¿Qué variables representan características económicas?** Principalmente ingreso_mensual, gasto_servicio y monto_compra; financiamiento también aporta información económica.
5. **¿Qué variables representan comportamiento del cliente?** vehiculos_comprados, antiguedad_cliente, visitas_taller, km_mensuales y financiamiento.
6. **¿Qué variables tienen escalas muy diferentes?** edad y variables de conteo están en decenas o unidades; ingreso y gasto están en miles; monto_compra está en cientos de miles; km_mensuales también está en cientos o miles.

## 3. Estandarización

Se utilizó `StandardScaler`.

Aplicar K-Means directamente a las variables originales sería problemático porque el algoritmo utiliza distancias. Una variable como monto_compra, medida en cientos de miles, dominaría la distancia sobre variables como edad o visitas_taller aunque no necesariamente sea más importante.

La estandarización coloca las variables en una escala comparable.

## 4. Determinación del número de clusters

Inercias obtenidas:

| K | Inercia |
|---:|---:|
| 2 | 158.43 |
| 3 | 82.61 |
| 4 | 58.73 |
| 5 | 42.88 |
| 6 | 31.96 |
| 7 | 25.57 |
| 8 | 21.18 |
| 9 | 18.21 |
| 10 | 15.44 |

Una elección razonable es **K=3**. La reducción de inercia de K=2 a K=3 es muy grande, mientras que después de K=3 las mejoras son progresivamente menores. Esto produce un punto de equilibrio entre simplicidad e identificación de patrones.

No se considera que exista una única respuesta obligatoria; K=3 se justifica por el comportamiento de la curva y por la interpretación posterior de los grupos.

## 5. Interpretación de los tres clusters

Resultados promedio con K=3:

| Cluster | Clientes | Edad | Ingreso | Vehículos | Antigüedad | Gasto servicio | Visitas | Km/mes | Monto compra | Financiamiento |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 16 | 56.75 | 54,062.50 | 3.19 | 9.31 | 6,125.00 | 6.81 | 2,506.25 | 490,000.00 | 0.00 |
| 1 | 14 | 27.86 | 16,750.00 | 1.14 | 2.29 | 2,028.57 | 1.71 | 767.86 | 213,214.29 | 1.00 |
| 2 | 20 | 42.30 | 30,350.00 | 1.75 | 5.70 | 3,585.00 | 3.75 | 1,512.50 | 306,500.00 | 0.10 |

La interpretación se realiza **después** de observar los promedios:

- **Cluster 1 — segmento de entrada:** clientes más jóvenes, menor ingreso y compra promedio, poca antigüedad y uso frecuente de financiamiento.
- **Cluster 2 — segmento intermedio:** clientes con niveles medios de ingreso, antigüedad, gasto y compras.
- **Cluster 0 — segmento de alto valor:** clientes con mayores ingresos, compras, antigüedad, gasto en servicio y actividad.

Los números 0, 1 y 2 no tienen significado ordinal por sí mismos; solamente identifican los grupos encontrados por el algoritmo.

## 6. Reducción de dimensionalidad con PCA

Las nueve variables estandarizadas se redujeron a dos componentes.

Varianza explicada:

- **Componente 1:** 0.9101 → 91.01 %.
- **Componente 2:** 0.0630 → 6.30 %.
- **Total:** 0.9731 → **97.31 %**.

### Preguntas de análisis

1. **¿Los clusters parecen estar claramente separados?** En la proyección PCA existe una separación general clara, especialmente entre los extremos de menor y mayor valor. Los grupos intermedios pueden acercarse a los límites de otros clusters.
2. **¿Existen puntos cercanos entre clusters?** Sí. Los límites entre el segmento intermedio y los otros grupos pueden presentar clientes próximos en el plano PCA.
3. **¿Qué se pierde al reducir 9 dimensiones a 2?** Se pierde aproximadamente 2.69 % de la variabilidad total y también detalle de relaciones que existen en dimensiones no visibles.
4. **¿Qué porcentaje explican las dos componentes?** Aproximadamente **97.31 %**.

## 7. Variables importantes en PCA

Las mayores cargas absolutas de la Componente 1 son aproximadamente:

- gasto_servicio: 0.347;
- ingreso_mensual: 0.346;
- visitas_taller: 0.344;
- monto_compra: 0.344;
- edad: 0.344.

La Componente 1 resume principalmente un eje general de nivel económico, antigüedad y actividad.

En la Componente 2 domina:

- financiamiento: 0.914.

Después aparecen variables como vehículos comprados y monto de compra con menor peso.

Esto indica que el uso de financiamiento ayuda a diferenciar clientes en una dirección distinta al patrón general económico y de actividad.

## 8. Complejidad y sobreajuste en clustering

### ¿Qué ocurre con la inercia conforme aumenta K?

La inercia siempre disminuye o se mantiene, porque al aumentar el número de centroides cada punto puede quedar más cerca de alguno de ellos.

### ¿Más clusters siempre significa un mejor modelo?

No. Una inercia menor no garantiza grupos más útiles o generalizables. Demasiados clusters pueden fragmentar patrones que deberían analizarse juntos.

### ¿Qué ocurre si cada cliente termina prácticamente en su propio grupo?

La inercia sería muy baja, pero la segmentación dejaría de resumir patrones generales y se convertiría casi en una memorización de los registros.

### Relación con sobreajuste

En clustering no existe una variable objetivo para comparar entrenamiento y validación como en aprendizaje supervisado. Sin embargo, una complejidad excesiva puede producir grupos que representan particularidades o ruido de la muestra en lugar de estructuras generales.

Por ello, K debe equilibrar ajuste e interpretabilidad.

## 9. Generalización

Se aplicó el mismo scaler y el modelo K-Means de tres clusters a cinco clientes nuevos.

Resultados:

| Cliente nuevo | Edad | Ingreso | Vehículos | Monto compra | Cluster |
|---:|---:|---:|---:|---:|---:|
| 1 | 26 | 14,000 | 1 | 195,000 | 1 |
| 2 | 35 | 23,000 | 1 | 240,000 | 1 |
| 3 | 48 | 36,000 | 2 | 350,000 | 2 |
| 4 | 55 | 48,000 | 3 | 480,000 | 0 |
| 5 | 62 | 65,000 | 4 | 620,000 | 0 |

### Preguntas de generalización

1. **¿Los nuevos clientes pudieron asignarse?** Sí. K-Means puede asignar nuevos registros al centroide existente más cercano.
2. **¿Qué significa esto?** El modelo puede aplicar la estructura aprendida a observaciones que no participaron en el ajuste original.
3. **¿Por qué usar el mismo StandardScaler?** Porque los centroides fueron aprendidos en el espacio definido por la transformación original. Los nuevos datos deben representarse en esa misma escala.
4. **¿Qué pasaría si se reentrena el scaler solo con los nuevos clientes?** Cambiarían medias y desviaciones, por lo que sus coordenadas dejarían de ser comparables con las usadas para entrenar K-Means y las asignaciones podrían volverse inconsistentes.
5. **¿Qué características probablemente determinan el cluster?** La combinación de ingreso, monto de compra, gasto en servicio, visitas, antigüedad, vehículos adquiridos, kilómetros, edad y financiamiento. PCA muestra que muchas de estas variables contribuyen conjuntamente, mientras financiamiento tiene una influencia muy marcada en la segunda componente.

## 10. Sistema interactivo

Se agregó un sistema visual que recibe las nueve características de un cliente nuevo.

El sistema:

1. construye el registro;
2. aplica el StandardScaler entrenado originalmente;
3. asigna el cluster mediante K-Means;
4. transforma el cliente con el mismo PCA;
5. muestra su posición respecto a los clientes originales;
6. interpreta el segmento según los promedios observados;
7. presenta una recomendación comercial ilustrativa.

El sistema no utiliza etiquetas predefinidas para entrenar. Los nombres comerciales de los segmentos se construyen después de analizar las características promedio de cada cluster.

## 11. Conclusión

La práctica demuestra cómo el aprendizaje no supervisado permite descubrir patrones sin disponer de categorías conocidas previamente.

K-Means separó los clientes en tres grupos interpretables, StandardScaler evitó que las variables de gran magnitud dominaran las distancias y PCA permitió representar la mayor parte de la variabilidad en solo dos componentes.

El análisis de complejidad mostró que reducir la inercia no es suficiente para justificar un modelo más complejo. Finalmente, la asignación de clientes nuevos demostró el concepto de generalización: la estructura aprendida puede utilizarse con observaciones posteriores siempre que se mantenga el mismo proceso de transformación.
