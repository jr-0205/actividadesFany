# Práctica 5.1 — NexaTech Store

Prototipo web de una empresa que comercializa artículos tecnológicos, desarrollado a partir de la propuesta de **IA Agéntica** documentada previamente.

## Qué incluye

- Catálogo inicial de 8 productos tecnológicos.
- Buscador y filtros por categoría.
- Carrito de compra funcional.
- Registro de ventas.
- Descuento automático de existencias después de cada venta.
- Panel de inventario editable.
- Métricas de productos, unidades, ventas e ingresos.
- Base de datos **SQLite** creada automáticamente.
- Asistente multiagente local con las etapas:
  - A0 Orquestador
  - A1 Mercado
  - A2 Catálogo
  - A3 Inventario
  - A5 Ventas
  - A6 Calidad
- Diseño responsive para computadora y celular.

> Los precios, existencias, ventas y recomendaciones son datos simulados para la práctica académica.

## Tecnologías

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript

## Ejecutar el proyecto

Desde la carpeta `Práctica_5_1`:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Abre en el navegador:

```text
http://127.0.0.1:5000
```

La base de datos se crea automáticamente en `data/nexatech.db` la primera vez que se inicia el programa.

## Flujo de demostración recomendado

1. Mostrar el inicio y las métricas.
2. Entrar al catálogo y usar un filtro o la búsqueda.
3. Agregar uno o dos productos al carrito y registrar una venta.
4. Mostrar que el stock disminuyó y que apareció la venta reciente.
5. Cambiar un dato del inventario y guardarlo.
6. Ejecutar el Asistente IA con un perfil, necesidad y presupuesto.
7. Mostrar las etapas de los agentes y la validación final de A6.

El archivo `GUION_VIDEO.md` contiene un guion de menos de dos minutos.
