from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from agents import CoordinadorAgent, DeportesAgent, HorariosAgent, classify_user, AgentError
from database import init_db, query_all

app = Flask(__name__)
init_db()

coordinator = CoordinadorAgent()
sports_agent = DeportesAgent()
schedules_agent = HorariosAgent()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/catalogo")
def catalog():
    try:
        age = int(request.args.get("edad", 0))
        gender = request.args.get("genero", "").strip().lower()
        category = classify_user(age, gender)
        sports = sports_agent.available_for(age)
        return jsonify({"ok": True, "category": category, "sports": sports})
    except (ValueError, AgentError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/horarios")
def schedules():
    try:
        sport_id = int(request.args.get("deporte_id", 0))
        age = int(request.args.get("edad", 0))
        if sport_id <= 0:
            raise ValueError("Selecciona una disciplina.")
        rows = schedules_agent.available_for(sport_id, age)
        return jsonify({"ok": True, "schedules": rows})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/inscripciones")
def register():
    payload = request.get_json(silent=True) or {}
    result = coordinator.process(payload)
    return jsonify(result), 201 if result["ok"] else 400


@app.get("/api/inscripciones")
def recent_registrations():
    rows = query_all(
        """
        SELECT r.folio, r.full_name, r.category, s.name AS sport,
               h.label AS schedule, r.total_first_payment, r.created_at
        FROM registrations r
        JOIN sports s ON s.id = r.sport_id
        JOIN schedules h ON h.id = r.schedule_id
        ORDER BY r.id DESC
        LIMIT 8
        """
    )
    return jsonify({"ok": True, "registrations": rows})


@app.get("/api/estado")
def status():
    count = query_all("SELECT COUNT(*) AS total FROM registrations")[0]["total"]
    return jsonify({"ok": True, "database": "SQLite", "registrations": count, "agents": 7})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
