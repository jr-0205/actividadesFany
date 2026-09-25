from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "nexatech.db"

SEED_PRODUCTS = [
    ("NT-001", "SSD externo 1 TB USB-C", "Almacenamiento", "1 TB, USB-C, uso portátil", 1499.0, 18, "ssd", 1),
    ("NT-002", "Teclado mecánico compacto", "Periféricos", "Formato 75 %, conexión USB", 1099.0, 24, "keyboard", 1),
    ("NT-003", "Mouse inalámbrico ergonómico", "Periféricos", "2.4 GHz/Bluetooth, batería recargable", 699.0, 31, "mouse", 0),
    ("NT-004", "Webcam Full HD", "Contenido digital", "1080p, micrófono integrado", 899.0, 17, "webcam", 0),
    ("NT-005", "Hub USB-C 6 en 1", "Conectividad", "HDMI, USB, SD y alimentación", 1199.0, 20, "hub", 1),
    ("NT-006", "Power bank 20,000 mAh", "Energía móvil", "USB-C, carga rápida compatible", 899.0, 27, "battery", 0),
    ("NT-007", "Audífonos USB con micrófono", "Audio", "Diadema, control de volumen", 749.0, 22, "headphones", 0),
    ("NT-008", "Router Wi-Fi 6 de entrada", "Conectividad", "Doble banda, uso doméstico", 1399.0, 14, "router", 1),
]


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL CHECK(stock >= 0),
                icon TEXT NOT NULL DEFAULT 'chip',
                featured INTEGER NOT NULL DEFAULT 0 CHECK(featured IN (0,1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                total REAL NOT NULL CHECK(total >= 0),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile TEXT NOT NULL,
                need TEXT NOT NULL,
                budget REAL NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO products (sku, name, category, description, price, stock, icon, featured)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                SEED_PRODUCTS,
            )


def _product_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "sku": row["sku"],
        "name": row["name"],
        "category": row["category"],
        "description": row["description"],
        "price": float(row["price"]),
        "stock": int(row["stock"]),
        "icon": row["icon"],
        "featured": bool(row["featured"]),
    }


def list_products(category: str | None = None, search: str | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM products WHERE 1=1"
    params: list[Any] = []
    if category and category.lower() != "todos":
        sql += " AND category = ?"
        params.append(category)
    if search:
        sql += " AND (name LIKE ? OR sku LIKE ? OR description LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    sql += " ORDER BY featured DESC, id ASC"
    with _connect() as conn:
        return [_product_dict(row) for row in conn.execute(sql, params).fetchall()]


def get_product(product_id: int) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return _product_dict(row) if row else None


def update_product(product_id: int, **changes: Any) -> dict[str, Any] | None:
    normalized: dict[str, Any] = {}
    if "price" in changes:
        price = float(changes["price"])
        if price < 0:
            raise ValueError("El precio no puede ser negativo.")
        normalized["price"] = price
    if "stock" in changes:
        stock = int(changes["stock"])
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")
        normalized["stock"] = stock
    if "featured" in changes:
        normalized["featured"] = 1 if bool(changes["featured"]) else 0

    if not normalized:
        return get_product(product_id)

    set_clause = ", ".join(f"{key} = ?" for key in normalized)
    values = list(normalized.values()) + [product_id]
    with _connect() as conn:
        cursor = conn.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
        if cursor.rowcount == 0:
            return None
    return get_product(product_id)


def create_sale(customer_name: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    if not items:
        raise ValueError("El carrito está vacío.")

    quantities: dict[int, int] = {}
    for item in items:
        try:
            product_id = int(item["product_id"])
            quantity = int(item.get("quantity", 1))
        except (KeyError, TypeError, ValueError):
            raise ValueError("Hay un artículo inválido en el carrito.")
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        quantities[product_id] = quantities.get(product_id, 0) + quantity

    now = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        prepared: list[tuple[sqlite3.Row, int, float]] = []
        total = 0.0

        for product_id, quantity in quantities.items():
            row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if not row:
                raise ValueError(f"El producto {product_id} no existe.")
            if row["stock"] < quantity:
                raise ValueError(f"Stock insuficiente para {row['name']}. Disponibles: {row['stock']}.")
            subtotal = float(row["price"]) * quantity
            total += subtotal
            prepared.append((row, quantity, subtotal))

        cursor = conn.execute(
            "INSERT INTO sales (customer_name, total, created_at) VALUES (?, ?, ?)",
            (customer_name or "Cliente demo", total, now),
        )
        sale_id = cursor.lastrowid

        output_items = []
        for row, quantity, subtotal in prepared:
            conn.execute(
                """
                INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
                """,
                (sale_id, row["id"], quantity, row["price"], subtotal),
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (quantity, row["id"]),
            )
            output_items.append(
                {
                    "product_id": row["id"],
                    "name": row["name"],
                    "quantity": quantity,
                    "unit_price": float(row["price"]),
                    "subtotal": subtotal,
                }
            )

        return {
            "id": sale_id,
            "customer_name": customer_name or "Cliente demo",
            "total": total,
            "created_at": now,
            "items": output_items,
        }


def list_sales(limit: int = 10) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, customer_name, total, created_at FROM sales ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_stats() -> dict[str, Any]:
    with _connect() as conn:
        product_stats = conn.execute(
            "SELECT COUNT(*) products, COALESCE(SUM(stock),0) units, COALESCE(SUM(price * stock),0) inventory_value FROM products"
        ).fetchone()
        sales_stats = conn.execute(
            "SELECT COUNT(*) sales_count, COALESCE(SUM(total),0) revenue FROM sales"
        ).fetchone()
        low_stock = conn.execute("SELECT COUNT(*) c FROM products WHERE stock <= 15").fetchone()["c"]
        return {
            "products": product_stats["products"],
            "units": product_stats["units"],
            "inventory_value": float(product_stats["inventory_value"]),
            "sales_count": sales_stats["sales_count"],
            "revenue": float(sales_stats["revenue"]),
            "low_stock": low_stock,
        }


def save_agent_log(profile: str, need: str, budget: float, result: dict[str, Any]) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO agent_logs (profile, need, budget, result_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (profile, need, budget, json.dumps(result, ensure_ascii=False), datetime.now().isoformat(timespec="seconds")),
        )
