# Práctica 7.1 — Predicción y clasificación de ventas

**Semana #5 · Práctica 7 · Parcial 1**  
**Modalidad:** Individual  
**Plataforma principal:** Google Colab

## Objetivo

Desarrollar un modelo predictivo sencillo mediante aprendizaje supervisado para analizar las ventas de una tienda ficticia de productos tecnológicos por internet.

La práctica resuelve dos problemas:

1. **Regresión:** predecir cuántas unidades se venderán.
2. **Clasificación:** determinar si la demanda será **Alta** o **Baja**.

## Caso: TechMarket Online

Se utiliza un conjunto de datos ficticio de **20 registros** con las variables:

- Producto
- Precio
- Visitas
- Publicidad
- Descuento
- Ventas
- Demanda

La demanda se define así:

- **Alta:** 50 unidades vendidas o más.
- **Baja:** menos de 50 unidades.

## Modelos utilizados

### Regresión lineal

Variables de entrada:

- Precio
- Visitas
- Publicidad
- Descuento

Variable objetivo:

- Ventas

Métricas:

- MAE
- MSE
- R²

### Árbol de decisión

Variables de entrada:

- Precio
- Visitas
- Publicidad
- Descuento

Variable objetivo:

- Demanda

Métricas:

- Exactitud
- Precisión
- Recall
- F1-score
- Matriz de confusión

## Resultados esperados con random_state=42

### Regresión

- MAE: aproximadamente **5.49**
- MSE: aproximadamente **69.61**
- R²: aproximadamente **0.854**

### Clasificación

En la partición de prueba de 5 registros:

- Exactitud: **1.00**
- Productos correctamente clasificados: **5 de 5**
- Productos de demanda alta identificados: **4 de 4**
- Matriz de confusión: **[[1, 0], [0, 4]]** usando el orden Baja, Alta.

Estos resultados son solamente académicos. El conjunto es pequeño y ficticio, por lo que no deben interpretarse como desempeño garantizado en datos reales.

## Simulación de producto nuevo

Para una laptop hipotética con:

- Precio: $13,500
- Visitas estimadas: 1,500
- Publicidad: $3,000
- Descuento: 15 %

El modelo produce aproximadamente:

- **Ventas estimadas: 82.35 unidades**
- **Demanda estimada: Alta**

## Abrir en Google Colab

Abre directamente el notebook:

[Práctica 7 en Google Colab](https://colab.research.google.com/github/jr-0205/actividadesFany/blob/main/Pr%C3%A1ctica_7_1/Practica_7_IA_1P.ipynb)

Después selecciona:

**Entorno de ejecución → Ejecutar todas**

No es necesario instalar software en Windows.

## Archivos

```text
Práctica_7_1/
├── Practica_7_IA_1P.ipynb
├── README.md
├── REPORTE.md
└── GUION_VIDEO.md
```

## Entrega

El PDF de la actividad solicita:

1. Reporte técnico breve.
2. Cuaderno de Google Colab con el código ejecutado.

El archivo `REPORTE.md` contiene el reporte redactado y puede copiarse a Word/Google Docs o exportarse a PDF. El notebook contiene el desarrollo completo, las métricas, las gráficas y la simulación final.
