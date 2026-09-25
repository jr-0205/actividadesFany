from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "club_deportivo.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon TEXT NOT NULL,
                description TEXT NOT NULL,
                registration_fee REAL NOT NULL,
                monthly_fee REAL NOT NULL,
                min_age INTEGER NOT NULL DEFAULT 6,
                max_age INTEGER NOT NULL DEFAULT 99,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport_id INTEGER NOT NULL,
                label TEXT NOT NULL,
                days TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                min_age INTEGER NOT NULL,
                max_age INTEGER NOT NULL,
                capacity INTEGER NOT NULL DEFAULT 20,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (sport_id) REFERENCES sports(id)
            );

            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folio TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                category TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                guardian_name TEXT,
                guardian_phone TEXT,
                sport_id INTEGER NOT NULL,
                schedule_id INTEGER NOT NULL,
                registration_fee REAL NOT NULL,
                monthly_fee REAL NOT NULL,
                discount REAL NOT NULL,
                total_first_payment REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'CONFIRMADA',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sport_id) REFERENCES sports(id),
                FOREIGN KEY (schedule_id) REFERENCES schedules(id)
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER,
                agent_name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (registration_id) REFERENCES registrations(id)
            );
            """
        )

        sports_count = conn.execute("SELECT COUNT(*) AS total FROM sports").fetchone()["total"]
        if sports_count == 0:
            sports = [
                ("Fútbol", "FT", "Entrenamiento técnico, coordinación y trabajo en equipo.", 350, 550, 6, 99),
                ("Natación", "NT", "Sesiones por nivel enfocadas en técnica y resistencia.", 300, 500, 6, 99),
                ("Baloncesto", "BK", "Fundamentos, acondicionamiento y juego colectivo.", 300, 480, 8, 99),
                ("Voleibol", "VB", "Técnica de golpeo, movilidad y táctica de equipo.", 250, 450, 10, 99),
                ("Atletismo", "AT", "Velocidad, resistencia y coordinación motriz.", 250, 420, 6, 99),
                ("Tenis", "TN", "Técnica de golpe, desplazamientos y estrategia básica.", 400, 650, 12, 99),
            ]
            conn.executemany(
                """
                INSERT INTO sports
                (name, icon, description, registration_fee, monthly_fee, min_age, max_age)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                sports,
            )

        schedules_count = conn.execute("SELECT COUNT(*) AS total FROM schedules").fetchone()["total"]
        if schedules_count == 0:
            sport_ids = {
                row["name"]: row["id"]
                for row in conn.execute("SELECT id, name FROM sports").fetchall()
            }
            schedules = [
                (sport_ids["Fútbol"], "Infantil matutino", "Lun / Mié / Vie", "16:00", "17:30", 6, 12, 18),
                (sport_ids["Fútbol"], "Juvenil vespertino", "Mar / Jue", "17:30", "19:00", 13, 17, 20),
                (sport_ids["Fútbol"], "Adultos nocturno", "Mar / Jue", "19:00", "20:30", 18, 99, 24),
                (sport_ids["Natación"], "Infantil", "Lun / Mié / Vie", "15:30", "16:30", 6, 12, 12),
                (sport_ids["Natación"], "Juvenil", "Mar / Jue / Sáb", "17:00", "18:00", 13, 17, 12),
                (sport_ids["Natación"], "Adultos", "Lun / Mié / Vie", "19:00", "20:00", 18, 99, 14),
                (sport_ids["Baloncesto"], "Formativo", "Mar / Jue", "16:00", "17:30", 8, 13, 16),
                (sport_ids["Baloncesto"], "Juvenil", "Lun / Mié", "17:30", "19:00", 14, 17, 18),
                (sport_ids["Baloncesto"], "Adultos", "Mar / Jue", "19:00", "20:30", 18, 99, 20),
                (sport_ids["Voleibol"], "Juvenil", "Lun / Mié", "17:00", "18:30", 10, 17, 18),
                (sport_ids["Voleibol"], "Adultos", "Mar / Jue", "18:30", "20:00", 18, 99, 20),
                (sport_ids["Atletismo"], "Infantil y juvenil", "Lun / Mié / Vie", "16:30", "17:45", 6, 17, 25),
                (sport_ids["Atletismo"], "Adultos", "Mar / Jue / Sáb", "18:00", "19:15", 18, 99, 25),
                (sport_ids["Tenis"], "Juvenil", "Mar / Jue", "16:30", "17:30", 12, 17, 8),
                (sport_ids["Tenis"], "Adultos", "Lun / Mié", "18:00", "19:00", 18, 99, 10),
            ]
            conn.executemany(
                """
                INSERT INTO schedules
                (sport_id, label, days, start_time, end_time, min_age, max_age, capacity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                schedules,
            )


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    with get_connection() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def query_one(sql: str, params: tuple = ()) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
