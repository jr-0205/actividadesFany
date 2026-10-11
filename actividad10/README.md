# Práctica 10: Fábrica de calzado

Aplicación gráfica en Python + Gradio conectada a MySQL. Incluye inicio de sesión y módulos para Almacén de Insumos, Producción, Ventas, Recursos Humanos e Inventario de Producto Terminado.

## Requisitos
- Python 3.10 o superior
- MySQL Server 8.x (o compatible)
- Base de datos y usuario con permisos de creación/lectura/escritura

## Instalación
1. Abre una terminal dentro de `actividad10/`.
2. Instala dependencias:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Crea la base de datos en MySQL:
   ```sql
   CREATE DATABASE fabrica_calzado CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   También puedes ejecutar `schema.sql` desde MySQL Workbench. La aplicación crea las tablas automáticamente si no existen.
4. Configura la conexión mediante variables de entorno (no subas contraseñas al repositorio):
   - Windows PowerShell:
     ```powershell
     $env:DB_HOST="localhost"
     $env:DB_PORT="3306"
     $env:DB_USER="root"
     $env:DB_PASSWORD="TU_CONTRASEÑA"
     $env:DB_NAME="fabrica_calzado"
     ```
   - macOS/Linux:
     ```bash
     export DB_HOST=localhost DB_PORT=3306 DB_USER=root DB_PASSWORD='TU_CONTRASEÑA' DB_NAME=fabrica_calzado
     ```
5. Ejecuta:
   ```bash
   python app.py
   ```
6. Abre http://localhost:7860.

## Acceso de demostración
- Usuario: `admin`
- Contraseña: `calzado10`

Estas credenciales son únicamente para la demostración escolar; no usar en producción.

## Funciones
- Inicio de sesión.
- Alta, consulta/búsqueda, actualización y eliminación de registros por departamento.
- Tablas con datos almacenados en MySQL.
- Al iniciar, la aplicación agrega 20 registros de demostración por módulo solo si la tabla de insumos está vacía.
- Formularios con cajas de texto y campos numéricos, tabla de registros, botones y campo de contraseña.

## Departamentos y campos
- **Almacén de Insumos:** ID, Nombre, Marca, Composición, Existencias, Color, Tamaño.
- **Producción:** ID, Fecha, Hora, Modelo, Color, Talla, Cantidad, Tipo.
- **Ventas:** ID, Modelo, Cantidad, Nombre, Tipo, Talla, Color, Material, Precio.
- **Recursos Humanos:** ID empleado, Nombre, Apellido paterno, Apellido materno, Departamento, Puesto, Turno, Sueldo, Teléfono, Dirección.
- **Inventario de Producto Terminado:** ID, Modelo, Talla, Color, Material, Tipo, Precio de venta, Ubicación.

Los datos de demostración son ficticios y se generan automáticamente. Si la base de datos ya tiene insumos, la carga inicial no vuelve a ejecutarse.
