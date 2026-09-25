from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "banco.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def query_one(sql: str, params: tuple = ()) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def _seed_demo_data(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO clients (full_name, email, phone)
        VALUES (?, ?, ?)
        """,
        ("Mariana López García", "mariana.demo@bancolab.local", "5512345678"),
    )
    client_id = conn.execute(
        "SELECT id FROM clients WHERE email = ?",
        ("mariana.demo@bancolab.local",),
    ).fetchone()["id"]

    conn.execute(
        """
        INSERT OR IGNORE INTO accounts (account_number, client_id, balance)
        VALUES (?, ?, ?)
        """,
        ("1002003001", client_id, 12500.00),
    )
    primary_id = conn.execute(
        "SELECT id FROM accounts WHERE account_number = ?",
        ("1002003001",),
    ).fetchone()["id"]

    conn.execute(
        "INSERT OR IGNORE INTO debit_cards (account_id, last4) VALUES (?, ?)",
        (primary_id, "4832"),
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO credit_cards
        (account_id, credit_limit, balance, cutoff_day, due_day, last4)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (primary_id, 30000.00, 8600.00, 15, 28, "9021"),
    )

    primary_tx_count = conn.execute(
        "SELECT COUNT(*) AS total FROM transactions WHERE account_id = ?",
        (primary_id,),
    ).fetchone()["total"]
    if primary_tx_count == 0:
        conn.executemany(
            """
            INSERT INTO transactions (account_id, type, amount, description)
            VALUES (?, ?, ?, ?)
            """,
            [
                (primary_id, "DEPOSITO", 15000.00, "Depósito inicial"),
                (primary_id, "RETIRO", 2500.00, "Retiro de demostración"),
            ],
        )

    primary_credit_id = conn.execute(
        "SELECT id FROM credit_cards WHERE account_id = ?",
        (primary_id,),
    ).fetchone()["id"]
    primary_credit_count = conn.execute(
        "SELECT COUNT(*) AS total FROM credit_movements WHERE credit_card_id = ?",
        (primary_credit_id,),
    ).fetchone()["total"]
    if primary_credit_count == 0:
        conn.execute(
            """
            INSERT INTO credit_movements (credit_card_id, type, amount, description)
            VALUES (?, 'COMPRA', ?, ?)
            """,
            (primary_credit_id, 8600.00, "Saldo inicial de demostración"),
        )

    conn.execute(
        """
        INSERT OR IGNORE INTO clients (full_name, email, phone)
        VALUES (?, ?, ?)
        """,
        ("Diego Hernández Ruiz", "diego.demo@bancolab.local", "5598765432"),
    )
    second_client_id = conn.execute(
        "SELECT id FROM clients WHERE email = ?",
        ("diego.demo@bancolab.local",),
    ).fetchone()["id"]

    conn.execute(
        """
        INSERT OR IGNORE INTO accounts (account_number, client_id, balance)
        VALUES (?, ?, ?)
        """,
        ("1002003002", second_client_id, 5000.00),
    )
    second_id = conn.execute(
        "SELECT id FROM accounts WHERE account_number = ?",
        ("1002003002",),
    ).fetchone()["id"]

    conn.execute(
        "INSERT OR IGNORE INTO debit_cards (account_id, last4) VALUES (?, ?)",
        (second_id, "1120"),
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO credit_cards
        (account_id, credit_limit, balance, cutoff_day, due_day, last4)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (second_id, 15000.00, 2500.00, 10, 23, "4418"),
    )

    second_tx_count = conn.execute(
        "SELECT COUNT(*) AS total FROM transactions WHERE account_id = ?",
        (second_id,),
    ).fetchone()["total"]
    if second_tx_count == 0:
        current_balance = float(
            conn.execute(
                "SELECT balance FROM accounts WHERE id = ?",
                (second_id,),
            ).fetchone()["balance"]
        )
        conn.execute(
            """
            INSERT INTO transactions (account_id, type, amount, description)
            VALUES (?, 'DEPOSITO', ?, ?)
            """,
            (second_id, current_balance, "Depósito inicial"),
        )

    second_credit_id = conn.execute(
        "SELECT id FROM credit_cards WHERE account_id = ?",
        (second_id,),
    ).fetchone()["id"]
    second_credit_count = conn.execute(
        "SELECT COUNT(*) AS total FROM credit_movements WHERE credit_card_id = ?",
        (second_credit_id,),
    ).fetchone()["total"]
    if second_credit_count == 0:
        conn.execute(
            """
            INSERT INTO credit_movements (credit_card_id, type, amount, description)
            VALUES (?, 'COMPRA', ?, ?)
            """,
            (second_credit_id, 2500.00, "Saldo inicial de demostración"),
        )


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
                amount REAL NOT NULL CHECK (amount > 0),
                description TEXT NOT NULL,
                related_account TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS credit_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL UNIQUE,
                credit_limit REAL NOT NULL CHECK (credit_limit >= 0),
                balance REAL NOT NULL DEFAULT 0 CHECK (balance >= 0 AND balance <= credit_limit),
                cutoff_day INTEGER NOT NULL CHECK (cutoff_day BETWEEN 1 AND 31),
                due_day INTEGER NOT NULL CHECK (due_day BETWEEN 1 AND 31),
                last4 TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS credit_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                description TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id)
            );

            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                loan_type TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                months INTEGER NOT NULL CHECK (months > 0),
                annual_rate REAL NOT NULL CHECK (annual_rate >= 0),
                monthly_payment REAL NOT NULL CHECK (monthly_payment >= 0),
                status TEXT NOT NULL DEFAULT 'ACTIVO',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS insurance_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                insurance_type TEXT NOT NULL,
                monthly_premium REAL NOT NULL CHECK (monthly_premium >= 0),
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
        _seed_demo_data(conn)


def reset_demo() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
