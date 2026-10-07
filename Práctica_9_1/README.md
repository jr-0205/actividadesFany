# Práctica 9.1 — Segmentación de clientes de una agencia automotriz

**Semana #6 · Práctica 9 · Parcial 1**  
**Modalidad:** Individual  
**Plataforma principal:** Google Colab

## Objetivo

Aplicar aprendizaje no supervisado para descubrir segmentos de clientes de una agencia automotriz mediante:

- preparación y estandarización de datos;
- clustering con K-Means;
- método del codo;
- interpretación de grupos;
- reducción de dimensionalidad con PCA;
- análisis de complejidad y sobreajuste en clustering;
- generalización con clientes nuevos.

## Datos

La práctica utiliza **50 clientes** y **9 variables**:

- edad;
- ingreso mensual;
- vehículos comprados;
- antigüedad como cliente;
- gasto en servicio;
- visitas al taller;
- kilómetros mensuales;
- monto de compra;
- financiamiento.

No existe una etiqueta previa de cliente: los grupos son descubiertos por K-Means.

## Resultado principal

Con los datos del PDF y `random_state=42`, **3 clusters** es una elección razonable porque la inercia cae fuertemente de K=2 a K=3 y después la mejora se vuelve mucho menor.

Para K=3 se obtienen grupos de:

- **16 clientes** con valores promedio altos;
- **14 clientes** con valores promedio bajos y uso frecuente de financiamiento;
- **20 clientes** con valores intermedios.

Los números de cluster son identificadores arbitrarios. La interpretación comercial se asigna después de observar sus promedios.

## PCA

Las dos primeras componentes principales explican aproximadamente:

- Componente 1: **91.01 %**
- Componente 2: **6.30 %**
- Total: **97.31 %**

La primera componente resume principalmente variables relacionadas con nivel económico y actividad del cliente. La segunda está dominada especialmente por el uso de financiamiento.

## Sistema interactivo

El notebook incluye al final un pequeño sistema visual construido con **Gradio**.

Permite capturar un cliente nuevo con sus 9 características y mostrar:

- cluster asignado;
- perfil comercial interpretado;
- recomendación;
- ubicación del cliente en la proyección PCA;
- tabla de promedios de los clusters.

El sistema utiliza **el mismo StandardScaler, K-Means y PCA entrenados con los datos originales**.

## Abrir en Google Colab

[Práctica 9 en Google Colab](https://colab.research.google.com/github/jr-0205/actividadesFany/blob/main/Pr%C3%A1ctica_9_1/Practica_9_IA_Colab.ipynb)

Después selecciona:

**Entorno de ejecución → Ejecutar todas**

## Ejecutar localmente

En PowerShell:

```powershell
cd .\Práctica_9_1\
python -m pip install -r requirements.txt
python sistema_segmentacion.py
```

Después abre la dirección local que muestre Gradio, normalmente:

```text
http://127.0.0.1:7860
```

## Estructura

```text
Práctica_9_1/
├── Practica_9_IA_Colab.ipynb
├── sistema_segmentacion.py
├── requirements.txt
├── README.md
├── REPORTE.md
└── GUION_VIDEO.md
```

## Entrega

El archivo `REPORTE.md` contiene el análisis técnico completo y `GUION_VIDEO.md` un guion para demostrar la práctica en menos de 3 minutos.

La referencia a “funciones bancarias” en la consigna no coincide con el contenido de esta práctica. La demostración se enfoca en las funciones de segmentación de clientes, clustering, PCA y generalización.
