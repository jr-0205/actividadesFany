import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import gradio as gr

# Configuración por variables de entorno: no guardes contraseñas en el repositorio.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    # En XAMPP, root normalmente no tiene contraseña por defecto.
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "fabrica_calzado"),
}

def ensure_database_exists():
    """Crea la base de datos si no existe (requiere permisos CREATE DATABASE)."""
    server_config = {key: value for key, value in DB_CONFIG.items() if key != "database"}
    conn = mysql.connector.connect(**server_config)
    try:
        cur = conn.cursor()
        db_name = DB_CONFIG["database"]
        # El nombre viene de la configuración local, no de una entrada del usuario.
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cur.close()
    finally:
        conn.close()

DEPARTMENTS = {
    "Almacén de Insumos": {
        "table": "insumos",
        "fields": [("id", "ID", "number"), ("nombre", "Nombre", "text"), ("marca", "Marca", "text"),
                   ("composicion", "Composición", "text"), ("existencias", "Existencias", "number"),
                   ("color", "Color", "text"), ("tamano", "Tamaño", "text")],
    },
    "Producción": {
        "table": "produccion",
        "fields": [("id", "ID", "number"), ("fecha", "Fecha (AAAA-MM-DD)", "text"), ("hora", "Hora (HH:MM)", "text"),
                   ("modelo", "Modelo", "text"), ("color", "Color", "text"), ("talla", "Talla", "text"),
                   ("cantidad", "Cantidad", "number"), ("tipo", "Tipo", "text")],
    },
    "Ventas": {
        "table": "ventas",
        "fields": [("id", "ID", "number"), ("modelo", "Modelo", "text"), ("cantidad", "Cantidad", "number"),
                   ("nombre", "Nombre del cliente", "text"), ("tipo", "Tipo", "text"), ("talla", "Talla", "text"),
                   ("color", "Color", "text"), ("material", "Material", "text"), ("precio", "Precio ($)", "number")],
    },
    "Recursos Humanos": {
        "table": "recursos_humanos",
        "fields": [("id_emp", "ID empleado", "number"), ("nombre", "Nombre", "text"), ("a_pat", "Apellido paterno", "text"),
                   ("a_mat", "Apellido materno", "text"), ("depto", "Departamento", "text"), ("puesto", "Puesto", "text"),
                   ("turno", "Turno", "text"), ("sueldo", "Sueldo ($)", "number"), ("telefono", "Teléfono", "text"),
                   ("direccion", "Dirección", "text")],
    },
    "Inventario de Producto Terminado": {
        "table": "producto_terminado",
        "fields": [("id", "ID", "number"), ("modelo", "Modelo", "text"), ("talla", "Talla", "text"),
                   ("color", "Color", "text"), ("material", "Material", "text"), ("tipo", "Tipo", "text"),
                   ("precio_venta", "Precio de venta ($)", "number"), ("ubicacion", "Ubicación", "text")],
    },
}

def connect():
    return mysql.connector.connect(**DB_CONFIG)

def initialize_database():
    """Crea la base, las tablas y carga datos de demostración cuando corresponde."""
    ensure_database_exists()
    definitions = {
        "insumos": "id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL, marca VARCHAR(80), composicion VARCHAR(120), existencias INT DEFAULT 0, color VARCHAR(40), tamano VARCHAR(40)",
        "produccion": "id INT AUTO_INCREMENT PRIMARY KEY, fecha DATE, hora VARCHAR(10), modelo VARCHAR(80), color VARCHAR(40), talla VARCHAR(10), cantidad INT DEFAULT 0, tipo VARCHAR(50)",
        "ventas": "id INT AUTO_INCREMENT PRIMARY KEY, modelo VARCHAR(80), cantidad INT DEFAULT 0, nombre VARCHAR(100), tipo VARCHAR(50), talla VARCHAR(10), color VARCHAR(40), material VARCHAR(80), precio DECIMAL(10,2) DEFAULT 0",
        "recursos_humanos": "id_emp INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(80), a_pat VARCHAR(80), a_mat VARCHAR(80), depto VARCHAR(80), puesto VARCHAR(80), turno VARCHAR(30), sueldo DECIMAL(10,2) DEFAULT 0, telefono VARCHAR(30), direccion VARCHAR(160)",
        "producto_terminado": "id INT AUTO_INCREMENT PRIMARY KEY, modelo VARCHAR(80), talla VARCHAR(10), color VARCHAR(40), material VARCHAR(80), tipo VARCHAR(50), precio_venta DECIMAL(10,2) DEFAULT 0, ubicacion VARCHAR(60)",
    }
    conn = connect()
    try:
        cur = conn.cursor()
        for table, columns in definitions.items():
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns})")
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM insumos")
        if cur.fetchone()[0] == 0:
            seed = {
                "insumos": [
                    (f"Material {i}", ["Flexi", "PielMax", "SuelaPro"][i % 3], ["Piel", "Sintético", "Textil"][i % 3], 50 + i * 5, ["Negro", "Café", "Blanco", "Rojo"][i % 4], ["Chico", "Mediano", "Grande"][i % 3])
                    for i in range(1, 21)
                ],
                "produccion": [
                    (f"2026-10-{(i % 28) + 1:02d}", f"{8 + i % 9:02d}:{(i * 3) % 60:02d}", f"Modelo-{i:02d}", ["Negro", "Café", "Blanco"][i % 3], str(22 + i % 8), 20 + i * 2, ["Casual", "Deportivo", "Formal"][i % 3])
                    for i in range(1, 21)
                ],
                "ventas": [
                    (f"Modelo-{i:02d}", 1 + i % 5, f"Cliente {i:02d}", ["Casual", "Deportivo", "Formal"][i % 3], str(22 + i % 8), ["Negro", "Café", "Blanco"][i % 3], ["Piel", "Sintético", "Textil"][i % 3], 399 + i * 15)
                    for i in range(1, 21)
                ],
                "recursos_humanos": [
                    (f"Empleado{i:02d}", f"Apellido{i:02d}", f"Materno{i:02d}", ["Producción", "Ventas", "Almacén", "Administración"][i % 4], ["Operador", "Vendedor", "Almacenista", "Supervisor"][i % 4], ["Matutino", "Vespertino", "Nocturno"][i % 3], 8500 + i * 250, f"555100{i:04d}", f"Calle {i}, Colonia Industrial")
                    for i in range(1, 21)
                ],
                "producto_terminado": [
                    (f"Modelo-{i:02d}", str(22 + i % 8), ["Negro", "Café", "Blanco"][i % 3], ["Piel", "Sintético", "Textil"][i % 3], ["Casual", "Deportivo", "Formal"][i % 3], 499 + i * 20, f"Estante {1 + i % 5}-Nivel {1 + i % 4}")
                    for i in range(1, 21)
                ],
            }
            for table, rows in seed.items():
                cols = [x[0] for x in DEPARTMENTS[next(name for name, spec in DEPARTMENTS.items() if spec["table"] == table)]["fields"]][1:]  # la PK AUTO_INCREMENT se genera en MySQL
                placeholders = ",".join(["%s"] * len(cols))
                cur.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})", rows)
            conn.commit()
        cur.close()
    finally:
        conn.close()

def rows_for(department, search_term=""):
    spec = DEPARTMENTS[department]
    conn = connect()
    try:
        cur = conn.cursor()
        fields = [f[0] for f in spec["fields"]]
        if search_term and search_term.strip():
            searchable = [f for f in fields if f != fields[0]]
            where = " OR ".join([f"CAST({field} AS CHAR) LIKE %s" for field in searchable])
            params = tuple([f"%{search_term.strip()}%"] * len(searchable))
            cur.execute(f"SELECT {','.join(fields)} FROM {spec['table']} WHERE {where} ORDER BY {fields[0]} DESC LIMIT 500", params)
        else:
            cur.execute(f"SELECT {','.join(fields)} FROM {spec['table']} ORDER BY {fields[0]} DESC LIMIT 500")
        data = cur.fetchall()
        cur.close()
        return [list(map(lambda v: str(v) if v is not None else "", row)) for row in data]
    finally:
        conn.close()

def parse_value(field, value):
    value = "" if value is None else str(value).strip()
    if field in ("id", "id_emp", "existencias", "cantidad"):
        return int(value) if value else None
    if field in ("precio", "precio_venta", "sueldo"):
        return float(value) if value else 0
    return value or None

def save_record(department, action, values, record_id):
    spec = DEPARTMENTS[department]
    fields = [f[0] for f in spec["fields"]]
    pk = fields[0]
    try:
        if action == "Eliminar":
            if not str(record_id or "").strip():
                return "Escribe el ID del registro que deseas eliminar.", rows_for(department)
            conn = connect()
            try:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM {spec['table']} WHERE {pk}=%s", (int(record_id),))
                affected = cur.rowcount
                conn.commit()
                cur.close()
            finally:
                conn.close()
            return (f"Registro eliminado (filas afectadas: {affected})." if affected else "No se encontró ese ID."), rows_for(department)
        raw = list(values or [])
        if len(raw) != len(fields):
            return "Completa los campos del formulario.", rows_for(department)
        data = {field: parse_value(field, val) for field, val in zip(fields, raw)}
        if action == "Actualizar":
            if not str(record_id or "").strip():
                return "Para actualizar, escribe el ID actual en el campo ID del registro.", rows_for(department)
            data.pop(pk, None)
            assignments = ",".join([f"{f}=%s" for f in data])
            conn = connect()
            try:
                cur = conn.cursor()
                cur.execute(f"UPDATE {spec['table']} SET {assignments} WHERE {pk}=%s", tuple(data.values()) + (int(record_id),))
                affected = cur.rowcount
                conn.commit()
                cur.close()
            finally:
                conn.close()
            return (f"Registro actualizado (filas afectadas: {affected})." if affected else "No se encontró el ID o no hubo cambios."), rows_for(department)
        # Crear: se ignora un ID vacío para que MySQL asigne el siguiente automáticamente.
        if data.get(pk) is None:
            data.pop(pk, None)
        cols = list(data)
        conn = connect()
        try:
            cur = conn.cursor()
            cur.execute(f"INSERT INTO {spec['table']} ({','.join(cols)}) VALUES ({','.join(['%s'] * len(cols))})", tuple(data.values()))
            new_id = cur.lastrowid
            conn.commit()
            cur.close()
        finally:
            conn.close()
        return f"Registro agregado correctamente. ID: {new_id}", rows_for(department)
    except (ValueError, Error) as exc:
        return f"No se pudo completar la operación: {exc}", rows_for(department)

def login(user, password):
    # Credenciales de demostración; reemplázalas por usuarios almacenados de forma segura en producción.
    if user == "admin" and password == "calzado10":
        return "Acceso concedido. Selecciona un departamento en las pestañas.", gr.update(visible=True)
    return "Usuario o contraseña incorrectos. Prueba admin / calzado10.", gr.update(visible=False)

def safe_rows_for(department, search_term=""):
    """Evita que un error temporal de BD impida cargar toda la interfaz."""
    try:
        return rows_for(department, search_term)
    except Error:
        return []

def build_department_tab(department):
    spec = DEPARTMENTS[department]
    fields = spec["fields"]
    descriptions = {
        "Almacén de Insumos": "Controla las materias primas y materiales disponibles para fabricar calzado.",
        "Producción": "Registra cada lote fabricado, con fecha, modelo, talla y cantidad.",
        "Ventas": "Guarda las ventas realizadas y los datos básicos del cliente y del calzado.",
        "Recursos Humanos": "Administra la información de contacto, puesto y turno del personal.",
        "Inventario de Producto Terminado": "Controla los pares listos para vender y su ubicación en el almacén.",
    }
    with gr.Tab(department):
        gr.Markdown(f"## {department}")
        gr.Markdown(descriptions.get(department, "Administra los registros de este departamento."))
        with gr.Row():
            search = gr.Textbox(label="🔎 Buscar registros", placeholder="Escribe modelo, nombre, color, talla…", scale=4)
            refresh_btn = gr.Button("↻ Actualizar lista", scale=1)
        table = gr.Dataframe(
            value=safe_rows_for(department),
            headers=[f[1] for f in fields],
            label="Registros guardados",
            interactive=False,
            wrap=True,
            max_height=320,
        )
        with gr.Accordion("➕ Agregar un registro nuevo", open=True):
            gr.Markdown("Completa los datos y pulsa **Guardar registro**. Puedes dejar el ID vacío para que MySQL lo asigne automáticamente.")
            inputs = []
            for row_start in range(0, len(fields), 3):
                with gr.Row():
                    for field, label, kind in fields[row_start:row_start + 3]:
                        if field in ("id", "id_emp"):
                            component = gr.Number(label=f"{label} (opcional)", precision=0, value=None)
                        elif kind == "number":
                            component = gr.Number(label=label, precision=0 if field in ("existencias", "cantidad") else 2, value=None)
                        else:
                            component = gr.Textbox(label=label, placeholder=f"Escribe {label.lower()}")
                        inputs.append(component)
            add_btn = gr.Button("💾 Guardar registro", variant="primary")
        with gr.Accordion("✏️ Editar o eliminar un registro", open=False):
            gr.Markdown("1. Escribe el **ID actual** del registro. 2. Para editar, completa los campos de arriba con los nuevos valores y pulsa **Guardar cambios**. 3. Para borrar, pulsa **Eliminar registro**. Esta acción no se puede deshacer.")
            with gr.Row():
                record_id = gr.Textbox(label="ID del registro que deseas modificar", placeholder="Ejemplo: 3")
                update_btn = gr.Button("Guardar cambios", variant="primary")
                delete_btn = gr.Button("Eliminar registro", variant="stop")
        status = gr.Markdown("Selecciona una acción para ver aquí el resultado.")
        search.change(lambda q: safe_rows_for(department, q), inputs=search, outputs=table)
        refresh_btn.click(lambda q: safe_rows_for(department, q), inputs=search, outputs=table)
        add_btn.click(
            lambda *v: save_record(department, "Agregar", v, ""),
            inputs=inputs,
            outputs=[status, table],
        )
        update_btn.click(
            lambda rid, *v: save_record(department, "Actualizar", v, rid),
            inputs=[record_id] + inputs,
            outputs=[status, table],
        )
        delete_btn.click(
            lambda rid: save_record(department, "Eliminar", [], rid),
            inputs=record_id,
            outputs=[status, table],
        )

try:
    initialize_database()
    DB_STATUS = "🟢 **Base de datos conectada.** MySQL está listo y las tablas se revisaron correctamente."
except Error as exc:
    DB_STATUS = f"🔴 **No se pudo conectar con MySQL.** {exc}\n\nAbre XAMPP, inicia MySQL y revisa la configuración de conexión en `app.py`."

with gr.Blocks(title="Fábrica de Calzado | Práctica 10", theme=gr.themes.Soft(), css="""
    .main-title {text-align:center}
    .subtle {opacity:.82}
    footer {visibility:hidden}
""") as demo:
    gr.Markdown("# 👞 Fábrica de Calzado", elem_classes=["main-title"])
    gr.Markdown("### Sistema de control de materiales, producción, ventas y personal", elem_classes=["main-title"])
    gr.Markdown("**Bienvenido.** Inicia sesión y elige un departamento en las pestañas. Puedes buscar, agregar, editar y eliminar registros.")
    with gr.Accordion("Estado de conexión con la base de datos", open=False):
        gr.Markdown(DB_STATUS)
        gr.Markdown("**¿Usas XAMPP?** Asegúrate de que el módulo MySQL esté iniciado antes de abrir esta página.")
    gr.Markdown("---")
    with gr.Group():
        gr.Markdown("## 🔐 Inicio de sesión")
        gr.Markdown("Introduce las credenciales de demostración para entrar al panel.")
        with gr.Row():
            username = gr.Textbox(label="Usuario", placeholder="Ej. admin", scale=1)
            password = gr.Textbox(label="Contraseña", type="password", placeholder="Escribe tu contraseña", scale=1)
        login_btn = gr.Button("Entrar al sistema", variant="primary")
        login_status = gr.Markdown()
    workspace = gr.Column(visible=False)
    with workspace:
        gr.Markdown("---")
        gr.Markdown("# 📋 Panel de departamentos")
        gr.Markdown("**Cómo usarlo:** selecciona una pestaña, busca un registro o abre el formulario para agregar, editar o eliminar.")
        with gr.Tabs():
            for dept in DEPARTMENTS:
                build_department_tab(dept)
    login_btn.click(login, inputs=[username, password], outputs=[login_status, workspace])


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=int(os.getenv("PORT", "7860")))
