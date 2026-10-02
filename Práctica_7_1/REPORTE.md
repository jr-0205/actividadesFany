# Reporte técnico — Práctica 7.1

## 1. Introducción

TechMarket Online es una empresa ficticia dedicada a la venta de productos tecnológicos por internet. Para analizar su información comercial se construyeron dos modelos de aprendizaje supervisado: una regresión lineal para estimar unidades vendidas y un árbol de decisión para clasificar la demanda como alta o baja.

El ejercicio utiliza datos ficticios y tiene fines académicos. Su propósito es comprender el proceso de preparación de datos, entrenamiento, evaluación e interpretación de modelos supervisados.

## 2. Datos

El conjunto contiene **20 registros comerciales**. Cada registro representa las estadísticas de comercialización de un producto durante un periodo.

| Variable | Descripción | Tipo |
|---|---|---|
| Producto | Nombre del producto | Categórica |
| Precio | Precio de venta en pesos mexicanos | Numérica |
| Visitas | Visitas a la página del producto | Numérica |
| Publicidad | Inversión publicitaria en pesos | Numérica |
| Descuento | Porcentaje de descuento aplicado | Numérica |
| Ventas | Unidades vendidas | Numérica |
| Demanda | Alta o Baja | Categórica |

La variable **Ventas** es el objetivo del modelo de regresión. La variable **Demanda** es el objetivo del modelo de clasificación.

La demanda se construyó con la regla:

- Alta: ventas mayores o iguales a 50.
- Baja: ventas menores a 50.

En total existen **14 registros de demanda Alta** y **6 de demanda Baja**.

### Respuestas de la Actividad 1

1. El conjunto contiene **20 registros**.
2. Las variables numéricas son **Precio, Visitas, Publicidad, Descuento y Ventas**.
3. Para predecir las ventas se utiliza la variable objetivo **Ventas**.
4. Para clasificar la demanda se utiliza la variable objetivo **Demanda**.
5. Es aprendizaje supervisado porque los datos de entrenamiento contienen variables de entrada y resultados conocidos que funcionan como etiquetas u objetivos.

## 3. Modelo de regresión

Se utilizó `LinearRegression` de scikit-learn.

Variables de entrada:

- Precio.
- Visitas.
- Publicidad.
- Descuento.

Variable objetivo:

- Ventas.

Los datos se dividieron en 75 % para entrenamiento y 25 % para prueba con `random_state=42`.

### Predicciones de prueba

| Ventas reales | Ventas predichas |
|---:|---:|
| 65 | 65.21 |
| 42 | 59.32 |
| 95 | 89.01 |
| 90 | 89.55 |
| 100 | 103.46 |

### Métricas

- **MAE:** 5.49
- **MSE:** 69.61
- **R²:** 0.854

El MAE indica que, en este pequeño conjunto de prueba, las predicciones se alejaron en promedio alrededor de 5.49 unidades de los valores reales. El R² obtenido indica que el modelo explicó aproximadamente el 85.4 % de la variación observada en esos datos de prueba. Debido a que solamente se evaluaron cinco registros ficticios, este valor no debe generalizarse.

### Respuestas de análisis

1. Las unidades predichas para los registros de prueba fueron aproximadamente **65.21, 59.32, 89.01, 89.55 y 103.46**.
2. El error absoluto medio fue aproximadamente **5.49 unidades**.
3. Un R² de 0.854 indica un ajuste alto dentro de esta pequeña muestra de prueba, pero no garantiza el mismo resultado con datos reales.
4. El modelo utiliza precio, visitas, publicidad y descuento como variables relacionadas con la predicción. El ejercicio no demuestra causalidad.
5. La empresa podría usar las estimaciones como una referencia inicial para planear inventario, complementándolas con existencias, tiempos de reposición, estacionalidad y un margen de seguridad.

## 4. Modelo de clasificación

Se utilizó `DecisionTreeClassifier` con profundidad máxima de 3 y `random_state=42`.

Las variables de entrada fueron Precio, Visitas, Publicidad y Descuento. La variable objetivo fue Demanda.

La división se realizó con 75 % de entrenamiento y 25 % de prueba, utilizando `stratify=y`.

### Resultados

- **Exactitud:** 1.00
- Registros de prueba: 5
- Clasificaciones correctas: 5
- Casos reales de demanda Alta: 4
- Casos de demanda Alta identificados correctamente: 4

Matriz de confusión con orden Baja, Alta:

```text
[[1, 0],
 [0, 4]]
```

El reporte de clasificación entrega precisión, recall y F1-score de 1.00 en este subconjunto. Este resultado perfecto se debe interpretar con cautela porque la prueba utiliza solamente cinco registros y los datos son ficticios.

### Respuestas de análisis

1. Se clasificaron correctamente **5 productos de 5**.
2. Se identificaron **4 productos de demanda Alta de 4 existentes en prueba**.
3. Un falso positivo sería clasificar como **Alta** la demanda de un producto cuya clase real es **Baja**.
4. Esto podría provocar sobreinventario o destinar más publicidad de la necesaria a un producto.
5. La clasificación puede ayudar a priorizar campañas, pero debe complementarse con presupuesto, margen, inventario y datos históricos más amplios.

## 5. Comparación de modelos

| Aspecto | Regresión | Clasificación |
|---|---|---|
| Objetivo | Predecir unidades vendidas | Predecir nivel de demanda |
| Variable objetivo | Ventas | Demanda |
| Resultado | Numérico | Categórico |
| Algoritmo | Regresión lineal | Árbol de decisión |
| Métricas | MAE, MSE, R² | Accuracy, precisión, recall, F1 |
| Aplicación | Planificación de inventario | Identificación de demanda Alta/Baja |

Los dos modelos son complementarios. La regresión ayuda cuando interesa una cantidad aproximada de unidades, mientras que la clasificación ayuda cuando se necesita una categoría sencilla para priorizar productos. Uno no sustituye al otro.

## 6. Simulación de una decisión comercial

Producto hipotético:

| Variable | Valor |
|---|---:|
| Precio | $13,500 |
| Visitas | 1,500 |
| Publicidad | $3,000 |
| Descuento | 15 % |

Resultados del modelo:

- **Ventas estimadas:** 82.35 unidades.
- **Demanda estimada:** Alta.

A partir de esta simulación, la empresa podría preparar inventario tomando la predicción como referencia, mantener la campaña publicitaria propuesta y monitorear las ventas reales para corregir las siguientes estimaciones.

Antes de una inversión comercial real también serían necesarios más registros históricos, estacionalidad, costos, margen de ganancia, inventario disponible, tiempos de entrega, comportamiento de competidores y cambios de mercado.

Las predicciones no son garantías porque el modelo aprende solamente de los datos proporcionados. En este ejercicio existen apenas 20 registros ficticios, por lo que la muestra es demasiado pequeña para representar un mercado real.

## 7. Interpretación y limitaciones

Principales limitaciones:

1. El conjunto contiene solamente 20 observaciones.
2. Los datos son ficticios.
3. La prueba de regresión usa solamente cinco registros.
4. La prueba de clasificación también usa cinco registros.
5. Una exactitud del 100 % en una muestra tan pequeña no demuestra que el modelo funcione igual con nuevos datos reales.
6. Pueden existir variables importantes no incluidas, como temporada, categoría detallada, competencia, disponibilidad, reseñas o tiempo de entrega.

Los resultados observados describen el comportamiento de este ejercicio. Cualquier decisión real requeriría validación con datos históricos más amplios y representativos.

## 8. Propuesta comercial

1. **Planificar inventario con predicciones numéricas:** usar la regresión como referencia para estimar unidades y agregar un margen de seguridad definido por la empresa.
2. **Priorizar productos según nivel de demanda:** utilizar la clasificación Alta/Baja como una señal adicional para organizar campañas e inventario.
3. **Mejorar los datos antes de automatizar decisiones:** recopilar más periodos, incorporar estacionalidad, márgenes, existencias y otras variables antes de confiar en el modelo para decisiones comerciales.

## 9. Recursos agénticos

La práctica puede interpretarse mediante dos roles de apoyo, sin programar agentes autónomos:

- **Analista de datos:** revisa variables, estructura, calidad y limitaciones del conjunto.
- **Analista predictivo/comercial:** interpreta regresión, clasificación, errores y posibles acciones comerciales.

## 10. Conclusión

La práctica demuestra que el aprendizaje supervisado permite resolver distintos tipos de problemas comerciales. La regresión produce una estimación numérica de ventas y la clasificación transforma las características comerciales en una categoría de demanda.

También se comprobó que evaluar un modelo es tan importante como entrenarlo. Métricas como MAE, MSE, R², accuracy, precisión, recall, F1-score y la matriz de confusión permiten interpretar el desempeño, aunque siempre deben analizarse considerando el tamaño y la calidad de los datos.

En conclusión, ambos modelos ofrecen perspectivas complementarias, pero los resultados de este ejercicio son ilustrativos y no deben considerarse predicciones comerciales definitivas.
