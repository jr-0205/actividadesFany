import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import gradio as gr

# Configuración por variables de entorno: no guardes contraseñas en el repositorio.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "fabrica_calzado"),
}

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
    """Crea tablas y carga 20 registros de demostración por departamento una sola vez."""
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
        return [fields] + [list(map(lambda v: str(v) if v is not None else "", row)) for row in data]
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

def build_department_tab(department):
    spec = DEPARTMENTS[department]
    fields = spec["fields"]
    with gr.Tab(department):
        gr.Markdown(f"### Gestión de {department}\nUsa **Agregar**, **Actualizar** o **Eliminar**. Para actualizar o eliminar, indica el ID actual.")
        search = gr.Textbox(label="Buscar", placeholder="Buscar por nombre, modelo, color, talla…")
        table = gr.Dataframe(value=rows_for(department), label="Registros (máximo 500)", interactive=False)
        inputs = []
        with gr.Row():
            for field, label, kind in fields:
                if kind == "number":
                    component = gr.Number(label=label, precision=0 if field in ("id", "id_emp", "existencias", "cantidad") else 2)
                else:
                    component = gr.Textbox(label=label)
                inputs.append(component)
        record_id = gr.Textbox(label="ID actual para actualizar/eliminar", placeholder="Ej. 1")
        status = gr.Markdown()
        with gr.Row():
            add_btn = gr.Button("Agregar registro", variant="primary")
            update_btn = gr.Button("Actualizar registro")
            delete_btn = gr.Button("Eliminar registro", variant="stop")
            refresh_btn = gr.Button("Actualizar tabla")
        search.change(lambda q: rows_for(department, q), search, table)
        add_btn.click(lambda *v: save_record(department, "Agregar", v[:-1], v[-1]), inputs=inputs + [record_id], outputs=[status, table])
        update_btn.click(lambda *v: save_record(department, "Actualizar", v[:-1], v[-1]), inputs=inputs + [record_id], outputs=[status, table])
        delete_btn.click(lambda rid: save_record(department, "Eliminar", [], rid), inputs=record_id, outputs=[status, table])
        refresh_btn.click(lambda: rows_for(department), outputs=table)

try:
    initialize_database()
    DB_STATUS = "✅ Conexión con MySQL establecida. Se verificaron las tablas y los registros de demostración."
except Error as exc:
    DB_STATUS = f"⚠️ No se pudo conectar a MySQL: {exc}. Revisa README.md y las variables DB_HOST, DB_USER, DB_PASSWORD y DB_NAME."

with gr.Blocks(title="Práctica 10 · Fábrica de calzado", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 👞 Práctica 10: Fábrica de calzado\nSistema de gestión con interfaz gráfica y base de datos MySQL.")
    gr.Markdown(DB_STATUS)
    with gr.Group():
        gr.Markdown("## Log In")
        with gr.Row():
            username = gr.Textbox(label="Usuario", value="", placeholder="Usuario")
            password = gr.Textbox(label="Contraseña", type="password", placeholder="Contraseña")
        login_btn = gr.Button("Iniciar sesión", variant="primary")
        login_status = gr.Markdown()
    workspace = gr.Column(visible=False)
    with workspace:
        gr.Markdown("## Panel de departamentos")
        with gr.Tabs():
            for dept in DEPARTMENTS:
                build_department_tab(dept)
    login_btn.click(login, inputs=[username, password], outputs=[login_status, workspace])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")))
