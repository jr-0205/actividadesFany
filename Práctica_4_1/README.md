# Práctica 4.1 — Modelo supervisado de predicción

## Objetivo

Desarrollar en Python un modelo supervisado de predicción mediante **Regresión Lineal**. El modelo aprende la relación entre el tamaño de una casa y su precio para después estimar el precio de una casa nueva de **90 m²**.

## Datos utilizados

| Tamaño de la casa (m²) | Precio (miles de dólares) |
|---:|---:|
| 50 | 150 |
| 65 | 185 |
| 80 | 210 |
| 100 | 260 |
| 120 | 300 |
| 150 | 380 |

La variable independiente es el tamaño de la casa y la variable objetivo es el precio.

## Tecnologías

- Python
- NumPy
- scikit-learn
- Matplotlib

## Instalación

Abre una terminal dentro de esta carpeta y ejecuta:

```bash
pip install -r requirements.txt
```

También se pueden instalar manualmente:

```bash
pip install scikit-learn numpy matplotlib
```

## Ejecución

```bash
python main.py
```

Al ejecutar el programa:

1. Se crean los datos ficticios del mercado inmobiliario.
2. Se entrena un modelo de `LinearRegression`.
3. Se predice el precio de una casa de 90 m², dato que no aparece en el entrenamiento.
4. Se imprime el resultado en la terminal.
5. Se abre una gráfica con los datos reales, la línea de tendencia y la predicción.

Con estos datos, la estimación esperada para la casa de 90 m² es aproximadamente **238.04 miles de dólares**.

## Elementos de la gráfica

- **Puntos azules:** datos conocidos usados para entrenar el modelo.
- **Línea roja punteada:** tendencia aprendida mediante regresión lineal.
- **Estrella roja:** predicción correspondiente a la casa de 90 m².

## Guion sugerido para el video de entrega

La demostración puede realizarse en menos de 2 minutos:

1. Mostrar brevemente los datos de entrenamiento en `main.py`.
2. Explicar que `LinearRegression` aprende la relación entre tamaño y precio.
3. Ejecutar `python main.py`.
4. Mostrar en terminal la predicción de la casa de 90 m².
5. Mostrar la gráfica y señalar los puntos, la línea de tendencia y la estrella de predicción.

## Estructura

```text
Práctica_4_1/
├── main.py
├── requirements.txt
└── README.md
```
