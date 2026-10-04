## Respuestas de la actividad
1. **¿Por qué es aprendizaje no supervisado?** No se entregan etiquetas de perfil ni respuestas correctas. K-Means agrupa según similitud entre las variables.
2. **¿Qué información utiliza?** Gasto mensual y número de compras, estandarizados. El identificador del cliente solo sirve para mostrar los resultados.
3. **¿Categorías previas o grupos descubiertos?** En aprendizaje supervisado, etiquetas conocidas orientan el entrenamiento; aquí se fija cuántos grupos buscar, pero sus integrantes se descubren mediante distancias. Los nombres se asignan después.
4. **¿Cuántos clusters se generaron?** Tres en el ejercicio principal.
5. **¿Qué comparten?** C01–C05 tienen gasto y frecuencia bajos; C06–C10, intermedios; C11–C15, altos. Cada grupo contiene cinco clientes.
6. **¿Qué diferencias hay?** Compra ocasional: $700 y 1.8 compras mensuales en promedio. Compra frecuente: $4,900 y 8.4 compras. Alto consumo: $10,600 y 16 compras. Son promedios del grupo, no valores de cada cliente.
7. **¿Qué cambia con dos clusters?** Se pierde uno de los tres perfiles visibles y se fusionan clientes con comportamientos diferentes. Los integrantes exactos aparecen en la tabla del experimento.
8. **Ejecutar con cuatro clusters.** La celda de experimentación ya entrena con `n_clusters=4` y muestra su gráfica e integrantes.
9. **Comparación.** Dos grupos resumen demasiado; tres separan los niveles bajo, medio y alto; cuatro subdividen uno de los perfiles. Consulta las tablas para ver la subdivisión obtenida. Las etiquetas numéricas son arbitrarias.
10. **¿Cuál describe mejor los patrones?** Tres grupos: coincide con las tres concentraciones visibles y tiene la mayor silueta entre los valores probados en esta ejecución. La inercia disminuye al aumentar k, por eso una inercia menor por sí sola no justifica elegir cuatro grupos.

## Interpretación comercial y conclusión
Para compra ocasional se podrían proponer promociones de entrada; para compra frecuente, recompensas de fidelidad; para alto consumo, atención personalizada. Son propuestas basadas en datos ficticios, no efectos comerciales comprobados.

K-Means descubrió similitudes sin recibir perfiles previos. Estandarizar permitió considerar ambas variables. Estos resultados describen esta pequeña muestra educativa y no se deben generalizar a clientes reales sin más datos.
