from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from database import (
    init_db,
    list_products,
    get_product,
    update_product,
    create_sale,
    list_sales,
    get_stats,
    save_agent_log,
)
from agents import AgentOrchestrator

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
init_db()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/products")
def api_products():
    category = request.args.get("category")
    search = request.args.get("search")
    return jsonify(list_products(category=category, search=search))


@app.patch("/api/products/<int:product_id>")
def api_update_product(product_id: int):
    payload = request.get_json(silent=True) or {}
    allowed = {"price", "stock", "featured"}
    changes = {k: payload[k] for k in allowed if k in payload}
    if not changes:
        return jsonify({"error": "No hay cambios válidos."}), 400

    try:
        product = update_product(product_id, **changes)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not product:
        return jsonify({"error": "Producto no encontrado."}), 404
    return jsonify(product)


@app.post("/api/sales")
def api_create_sale():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items") or []
    customer_name = (payload.get("customer_name") or "Cliente demo").strip()[:80]

    try:
        sale = create_sale(customer_name=customer_name, items=items)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(sale), 201


@app.get("/api/sales")
def api_sales():
    return jsonify(list_sales(limit=10))


@app.get("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.post("/api/agent/recommend")
def api_agent_recommend():
    payload = request.get_json(silent=True) or {}
    profile = (payload.get("profile") or "estudiante").strip().lower()
    need = (payload.get("need") or "productividad").strip().lower()
    try:
        budget = float(payload.get("budget") or 2500)
    except (TypeError, ValueError):
        return jsonify({"error": "El presupuesto debe ser numérico."}), 400

    orchestrator = AgentOrchestrator(products=list_products())
    result = orchestrator.run(profile=profile, need=need, budget=budget)
    save_agent_log(profile=profile, need=need, budget=budget, result=result)
    return jsonify(result)


@app.get("/api/product/<int:product_id>")
def api_product(product_id: int):
    product = get_product(product_id)
    if not product:
        return jsonify({"error": "Producto no encontrado."}), 404
    return jsonify(product)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
