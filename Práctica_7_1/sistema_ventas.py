import pandas as pd
import gradio as gr

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score

# Datos ficticios indicados en la práctica.
datos = {
    "Producto": [
        "Laptop", "Smartphone", "Audifonos", "Teclado", "Monitor",
        "Tablet", "Mouse", "Laptop", "Smartphone", "Audifonos",
        "Teclado", "Monitor", "Tablet", "Mouse", "Laptop",
        "Smartphone", "Audifonos", "Teclado", "Monitor", "Tablet"
    ],
    "Precio": [
        15000, 9000, 1200, 800, 4500, 6000, 400, 14000, 8500, 1500,
        900, 5000, 6500, 350, 16000, 9500, 1000, 750, 4800, 5800
    ],
    "Visitas": [
        1200, 1800, 2500, 1300, 900, 1100, 3000, 1000, 2000, 2800,
        1500, 1000, 900, 3200, 1300, 1700, 2600, 1400, 1100, 1000
    ],
    "Publicidad": [
        3000, 2500, 1200, 800, 1500, 1800, 700, 2800, 3000, 1000,
        900, 1300, 1600, 600, 3200, 2700, 1100, 850, 1400, 1700
    ],
    "Descuento": [
        10, 15, 20, 10, 5, 12, 15, 8, 20, 25,
        10, 10, 15, 20, 12, 18, 20, 15, 8, 10
    ],
    "Ventas": [
        65, 90, 120, 45, 35, 55, 140, 50, 100, 130,
        48, 40, 52, 150, 70, 95, 115, 42, 38, 50
    ]
}

df = pd.DataFrame(datos)
df["Demanda"] = df["Ventas"].apply(lambda x: "Alta" if x >= 50 else "Baja")

variables = ["Precio", "Visitas", "Publicidad", "Descuento"]

# Modelo de regresión.
X_reg = df[variables]
y_reg = df["Ventas"]
X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X_reg, y_reg, test_size=0.25, random_state=42
)

modelo_regresion = LinearRegression()
modelo_regresion.fit(X_train_reg, y_train_reg)
pred_reg = modelo_regresion.predict(X_test_reg)

mae = mean_absolute_error(y_test_reg, pred_reg)
mse = mean_squared_error(y_test_reg, pred_reg)
r2 = r2_score(y_test_reg, pred_reg)

# Modelo de clasificación.
X_clf = df[variables]
y_clf = df["Demanda"]
X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
    X_clf,
    y_clf,
    test_size=0.25,
    random_state=42,
    stratify=y_clf
)

modelo_clasificacion = DecisionTreeClassifier(max_depth=3, random_state=42)
modelo_clasificacion.fit(X_train_clf, y_train_clf)
pred_clf = modelo_clasificacion.predict(X_test_clf)
exactitud = accuracy_score(y_test_clf, pred_clf)


def analizar_producto(producto, precio, visitas, publicidad, descuento):
    """Genera una simulación comercial utilizando los dos modelos."""
    if not producto:
        return "Falta producto", "-", "-", "-", pd.DataFrame()

    if precio is None or visitas is None or publicidad is None or descuento is None:
        return "Faltan datos", "-", "-", "-", pd.DataFrame()

    if precio <= 0 or visitas < 0 or publicidad < 0 or descuento < 0 or descuento > 100:
        return "Revisa los valores", "-", "-", "-", pd.DataFrame()

    nuevo = pd.DataFrame({
        "Precio": [float(precio)],
        "Visitas": [float(visitas)],
        "Publicidad": [float(publicidad)],
        "Descuento": [float(descuento)]
    })

    ventas = max(0.0, float(modelo_regresion.predict(nuevo)[0]))
    demanda = str(modelo_clasificacion.predict(nuevo)[0])

    precio_final = float(precio) * (1 - float(descuento) / 100)
    ingreso_estimado = ventas * precio_final

    if demanda == "Alta":
        recomendacion = (
            "Demanda ALTA: considerar mayor disponibilidad de inventario y "
            "mantener seguimiento de la campaña."
        )
    else:
        recomendacion = (
            "Demanda BAJA: revisar inventario, precio, promoción y comportamiento "
            "real antes de aumentar la inversión."
        )

    resumen = pd.DataFrame([{
        "Producto": producto,
        "Precio": f"$ {float(precio):,.2f}",
        "Visitas": int(visitas),
        "Publicidad": f"$ {float(publicidad):,.2f}",
        "Descuento": f"{float(descuento):.1f} %",
        "Ventas estimadas": round(ventas, 2),
        "Demanda": demanda,
        "Precio con descuento": f"$ {precio_final:,.2f}",
        "Ingreso bruto estimado": f"$ {ingreso_estimado:,.2f}"
    }])

    return (
        f"{ventas:.2f} unidades",
        demanda,
        f"$ {precio_final:,.2f}",
        f"$ {ingreso_estimado:,.2f}",
        resumen,
        recomendacion
    )


with gr.Blocks(title="TechMarket AI - Sistema de Ventas") as demo:
    gr.Markdown(
        """
        # TechMarket AI
        ### Sistema de predicción y clasificación de ventas
        Captura los datos comerciales del producto y el sistema utilizará los modelos
        de aprendizaje supervisado para estimar ventas y clasificar la demanda.
        """
    )

    with gr.Row():
        with gr.Column():
            producto = gr.Dropdown(
                choices=[
                    "Laptop", "Smartphone", "Audifonos",
                    "Teclado", "Monitor", "Tablet", "Mouse", "Otro"
                ],
                value="Laptop",
                label="Producto"
            )
            precio = gr.Number(value=13500, label="Precio de venta ($)")
            visitas = gr.Number(value=1500, label="Visitas estimadas")
            publicidad = gr.Number(value=3000, label="Publicidad ($)")
            descuento = gr.Slider(
                minimum=0,
                maximum=50,
                value=15,
                step=1,
                label="Descuento (%)"
            )
            boton = gr.Button("Analizar producto", variant="primary")

        with gr.Column():
            ventas_salida = gr.Textbox(label="Ventas estimadas")
            demanda_salida = gr.Textbox(label="Demanda estimada")
            precio_final_salida = gr.Textbox(label="Precio después del descuento")
            ingreso_salida = gr.Textbox(label="Ingreso bruto estimado")
            recomendacion_salida = gr.Textbox(
                label="Interpretación comercial",
                lines=3
            )

    gr.Markdown("### Resultado de la simulación")
    tabla_resultado = gr.Dataframe(interactive=False)

    with gr.Accordion("Información del modelo", open=False):
        gr.Markdown(
            f"""
            **Datos de entrenamiento:** 20 registros ficticios

            **Regresión lineal**
            - MAE: {mae:.2f}
            - MSE: {mse:.2f}
            - R²: {r2:.3f}

            **Árbol de decisión**
            - Exactitud en la partición de prueba: {exactitud:.2f}

            Los resultados son educativos y no garantizan ventas futuras.
            """
        )
        gr.Dataframe(
            value=df,
            label="Conjunto de datos de la práctica",
            interactive=False
        )

    boton.click(
        fn=analizar_producto,
        inputs=[producto, precio, visitas, publicidad, descuento],
        outputs=[
            ventas_salida,
            demanda_salida,
            precio_final_salida,
            ingreso_salida,
            tabla_resultado,
            recomendacion_salida
        ]
    )

if __name__ == "__main__":
    demo.launch(share=True)
