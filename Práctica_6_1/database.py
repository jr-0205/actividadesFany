from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "banco.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def query_one(sql: str, params: tuple = ()) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL UNIQUE,
                client_id INTEGER NOT NULL,
                balance REAL NOT NULL DEFAULT 0 CHECK (balance >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            );

            CREATE TABLE IF NOT EXISTS debit_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL UNIQUE,
                last4 TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                related_account TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS credit_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL UNIQUE,
                credit_limit REAL NOT NULL,
                balance REAL NOT NULL DEFAULT 0 CHECK (balance >= 0),
                cutoff_day INTEGER NOT NULL,
                due_day INTEGER NOT NULL,
                last4 TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS credit_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id)
            );

            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                loan_type TEXT NOT NULL,
                amount REAL NOT NULL,
                months INTEGER NOT NULL,
                annual_rate REAL NOT NULL,
                monthly_payment REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVO',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS insurance_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                insurance_type TEXT NOT NULL,
                monthly_premium REAL NOT NULL,
                coverage TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVA',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                operation TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        existing = conn.execute("SELECT COUNT(*) AS total FROM clients").fetchone()["total"]
        if existing:
            return

        cur = conn.execute(
            "INSERT INTO clients (full_name, email, phone) VALUES (?, ?, ?)",
            ("Mariana López García", "mariana.demo@bancolab.local", "5512345678"),
        )
        client_id = cur.lastrowid
        cur = conn.execute(
            "INSERT INTO accounts (account_number, client_id, balance) VALUES (?, ?, ?)",
            ("1002003001", client_id, 12500.00),
        )
        primary_account_id = cur.lastrowid
        conn.execute(
            "INSERT INTO debit_cards (account_id, last4) VALUES (?, ?)",
            (primary_account_id, "4832"),
        )
        cur = conn.execute(
            """
            INSERT INTO credit_cards
            (account_id, credit_limit, balance, cutoff_day, due_day, last4)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (primary_account_id, 30000.00, 8600.00, 15, 28, "9021"),
        )
        credit_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO credit_movements (credit_card_id, type, amount, description)
            VALUES (?, 'COMPRA', ?, ?)
            """,
            (credit_id, 8600.00, "Saldo inicial de demostración"),
        )
        conn.executemany(
            """
            INSERT INTO transactions (account_id, type, amount, description)
            VALUES (?, ?, ?, ?)
            """,
            [
                (primary_account_id, "DEPOSITO", 15000.00, "Depósito inicial"),
                (primary_account_id, "RETIRO", 2500.00, "Retiro de demostración"),
            ],
        )

        cur = conn.execute(
            "INSERT INTO clients (full_name, email, phone) VALUES (?, ?, ?)",
            ("Diego Hernández Ruiz", "diego.demo@bancolab.local", "5598765432"),
        )
        second_client_id = cur.lastrowid
        cur = conn.execute(
            "INSERT INTO accounts (account_number, client_id, balance) VALUES (?, ?, ?)",
            ("1002003002", second_client_id, 5000.00),
        )
        second_account_id = cur.lastrowid
        conn.execute(
            "INSERT INTO debit_cards (account_id, last4) VALUES (?, ?)",
            (second_account_id, "1120"),
        )


def reset_demo() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
