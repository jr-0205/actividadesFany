# Práctica 8_1P · Segmentación de clientes

Trabajo individual de aprendizaje no supervisado con Python y Google Colab.

## Ejecutar en Google Colab

[Abre el cuaderno en Colab](https://colab.research.google.com/github/jr-0205/actividadesFany/blob/main/Pr%C3%A1ctica_8_1/Practica_8_Clustering_Colab.ipynb).

Selecciona **Entorno de ejecución → Ejecutar todas**. También puedes descargar el archivo y usar **Archivo → Subir cuaderno** en Colab.

## Contenido

- Los 15 clientes ficticios del PDF.
- Estandarización con StandardScaler y K-Means con 3 clusters.
- Gráficas, centroides y resumen de perfiles.
- Comparación de 2, 3 y 4 clusters con silueta e inercia.
- Respuestas de la actividad en REPORTE.md y en el cuaderno.
- Guion para un video de aproximadamente 1:45 en GUION_VIDEO.md.

## Resultados verificados

| Perfil | Clientes | Gasto promedio MXN | Compras promedio |
|---|---:|---:|---:|
| Compra ocasional | 5 | 700 | 1.8 |
| Compra frecuente | 5 | 4900 | 8.4 |
| Alto consumo | 5 | 10600 | 16 |

Tres clusters obtuvieron la mayor silueta entre las opciones probadas (0.8177). Las etiquetas numéricas de los grupos son arbitrarias. Los nombres se asignan después de entrenar.

Al ejecutar se generan dos imágenes PNG y tres tablas CSV en el entorno de Colab; pueden descargarse desde su panel Archivos.

La entrega indicada en el PDF es un video de máximo 2 minutos mostrando datos, gráficas y explicación de viva voz.
