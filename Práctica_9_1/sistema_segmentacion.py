import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gradio as gr

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

datos = {
    "edad": [23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,57,59,61,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,22,27,32,37,42,47,52,57,63,65],
    "ingreso_mensual": [12000,13500,14500,16000,18000,19500,21000,22500,24000,26000,28000,30000,32000,35000,38000,41000,45000,48000,52000,56000,13000,15000,17000,19000,21500,23500,25500,27500,29500,31500,33000,36000,39000,42000,46000,50000,54000,58000,62000,68000,11000,17500,23000,31000,37000,43000,49000,55000,65000,72000],
    "vehiculos_comprados": [1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,1,1,1,1,1,2,2,2,2,2,2,2,2,3,3,3,3,3,3,4,1,1,2,2,2,3,3,3,4,4],
    "antiguedad_cliente": [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,1,3,4,5,6,7,8,9,10,12],
    "gasto_servicio": [1500,1700,1800,2000,2200,2400,2600,2800,3000,3200,3500,3700,3900,4200,4500,4800,5200,5600,6000,6500,1600,1900,2100,2300,2500,2700,2900,3100,3400,3600,3800,4100,4400,4700,5000,5400,5800,6200,6700,7200,1400,2000,2700,3500,4300,5100,5900,6700,7500,8500],
    "visitas_taller": [1,1,1,2,2,2,2,3,3,3,3,4,4,4,5,5,5,6,6,7,1,1,2,2,2,3,3,3,4,4,4,5,5,5,6,6,6,7,7,8,1,2,3,4,5,6,7,8,9,10],
    "km_mensuales": [500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,550,650,750,850,950,1050,1150,1250,1350,1450,1550,1650,1750,1850,1950,2050,2150,2250,2350,2500,450,800,1200,1600,2000,2400,2800,3200,3600,4000],
    "monto_compra": [180000,190000,200000,210000,220000,230000,240000,250000,260000,270000,280000,300000,320000,340000,360000,380000,400000,430000,460000,500000,185000,200000,215000,225000,235000,250000,265000,280000,295000,310000,330000,350000,370000,390000,420000,450000,480000,510000,550000,600000,175000,225000,275000,325000,375000,425000,475000,525000,575000,650000],
    "financiamiento": [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0]
}

df = pd.DataFrame(datos)
columnas = list(df.columns)

scaler = StandardScaler()
X = scaler.fit_transform(df)

modelo = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = modelo.fit_predict(X)

base = df.copy()
base["cluster"] = clusters

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)
pca_df = pd.DataFrame(X_pca, columns=["Componente_1", "Componente_2"])
pca_df["cluster"] = clusters

promedios = base.groupby("cluster").mean(numeric_only=True)
conteos = base["cluster"].value_counts().sort_index()

# Los nombres se construyen después de observar los promedios del clustering.
orden = promedios["ingreso_mensual"].sort_values().index.tolist()
nombres_segmento = {
    int(orden[0]): "Segmento de entrada",
    int(orden[1]): "Segmento intermedio",
    int(orden[2]): "Segmento de alto valor",
}

def interpretar(cluster):
    nombre = nombres_segmento[int(cluster)]
    if nombre == "Segmento de entrada":
        detalle = (
            "Perfil con menor ingreso y compra promedio, poca antigüedad y "
            "mayor presencia de financiamiento."
        )
        recomendacion = (
            "Estrategia ilustrativa: planes de financiamiento, mantenimiento accesible "
            "y seguimiento para desarrollar lealtad."
        )
    elif nombre == "Segmento intermedio":
        detalle = (
            "Perfil con niveles medios de ingreso, compra, antigüedad y actividad."
        )
        recomendacion = (
            "Estrategia ilustrativa: renovación de vehículo, paquetes de servicio "
            "y programas de fidelización."
        )
    else:
        detalle = (
            "Perfil con mayores ingresos, monto de compra, antigüedad, gasto en "
            "servicio y actividad."
        )
        recomendacion = (
            "Estrategia ilustrativa: atención premium, vehículos de mayor gama, "
            "servicios personalizados y retención."
        )
    return nombre, detalle, recomendacion

def segmentar_cliente(
    edad, ingreso, vehiculos, antiguedad, gasto,
    visitas, km, monto, financiamiento
):
    valores = [edad, ingreso, vehiculos, antiguedad, gasto, visitas, km, monto]
    if any(v is None for v in valores):
        raise gr.Error("Completa todos los campos.")

    cliente = pd.DataFrame([{
        "edad": edad,
        "ingreso_mensual": ingreso,
        "vehiculos_comprados": vehiculos,
        "antiguedad_cliente": antiguedad,
        "gasto_servicio": gasto,
        "visitas_taller": visitas,
        "km_mensuales": km,
        "monto_compra": monto,
        "financiamiento": 1 if financiamiento == "Sí" else 0,
    }], columns=columnas)

    cliente_x = scaler.transform(cliente)
    cluster = int(modelo.predict(cliente_x)[0])
    cliente_pca = pca.transform(cliente_x)[0]

    nombre, detalle, recomendacion = interpretar(cluster)

    fig, ax = plt.subplots(figsize=(8, 5))
    for c in sorted(pca_df["cluster"].unique()):
        grupo = pca_df[pca_df["cluster"] == c]
        ax.scatter(
            grupo["Componente_1"],
            grupo["Componente_2"],
            label=f"Cluster {c} · {nombres_segmento[int(c)]}",
            alpha=0.75,
        )

    ax.scatter(
        cliente_pca[0],
        cliente_pca[1],
        marker="*",
        s=280,
        edgecolors="black",
        label="Cliente nuevo",
    )
    ax.set_title("Cliente nuevo dentro de la segmentación PCA")
    ax.set_xlabel("Componente 1")
    ax.set_ylabel("Componente 2")
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()

    resumen = pd.DataFrame([{
        "Cluster asignado": cluster,
        "Perfil": nombre,
        "PC1": round(float(cliente_pca[0]), 3),
        "PC2": round(float(cliente_pca[1]), 3),
    }])

    return (
        f"Cluster {cluster}",
        nombre,
        detalle,
        recomendacion,
        resumen,
        fig,
    )

promedios_ui = promedios.copy().round(2)
promedios_ui.insert(0, "clientes", [int(conteos.get(i, 0)) for i in promedios_ui.index])
promedios_ui.insert(1, "perfil", [nombres_segmento[int(i)] for i in promedios_ui.index])
promedios_ui = promedios_ui.reset_index()

with gr.Blocks(title="AutoSegment AI") as demo:
    gr.Markdown(
        """
        # AutoSegment AI
        ### Segmentación de clientes de una agencia automotriz
        El sistema utiliza **StandardScaler + K-Means + PCA** para asignar un
        cliente nuevo a uno de los segmentos descubiertos.
        """
    )

    with gr.Row():
        with gr.Column():
            edad = gr.Number(value=48, label="Edad")
            ingreso = gr.Number(value=36000, label="Ingreso mensual ($)")
            vehiculos = gr.Number(value=2, label="Vehículos comprados")
            antiguedad = gr.Number(value=6, label="Antigüedad como cliente")
            gasto = gr.Number(value=4200, label="Gasto promedio en servicio ($)")

        with gr.Column():
            visitas = gr.Number(value=4, label="Visitas al taller")
            km = gr.Number(value=1700, label="Kilómetros mensuales")
            monto = gr.Number(value=350000, label="Monto promedio de compra ($)")
            financiamiento = gr.Radio(
                ["Sí", "No"], value="No", label="Usa financiamiento"
            )
            boton = gr.Button("Segmentar cliente", variant="primary")

    with gr.Row():
        cluster_out = gr.Textbox(label="Cluster")
        perfil_out = gr.Textbox(label="Perfil comercial")

    detalle_out = gr.Textbox(label="Interpretación del segmento", lines=2)
    recomendacion_out = gr.Textbox(label="Recomendación ilustrativa", lines=2)
    resumen_out = gr.Dataframe(label="Resultado", interactive=False)
    grafica_out = gr.Plot(label="Visualización PCA")

    with gr.Accordion("Resumen de los clusters", open=False):
        gr.Dataframe(value=promedios_ui, interactive=False)
        gr.Markdown(
            f"Las dos componentes PCA explican **{pca.explained_variance_ratio_.sum()*100:.2f}%** "
            "de la variabilidad del conjunto."
        )

    boton.click(
        fn=segmentar_cliente,
        inputs=[
            edad, ingreso, vehiculos, antiguedad, gasto,
            visitas, km, monto, financiamiento
        ],
        outputs=[
            cluster_out, perfil_out, detalle_out,
            recomendacion_out, resumen_out, grafica_out
        ],
    )

if __name__ == "__main__":
    demo.launch()
