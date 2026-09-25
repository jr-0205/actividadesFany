from __future__ import annotations

import calendar
from datetime import date

from flask import Flask, jsonify, render_template, request

from agents import BankError, CreditoAgent, DebitoAgent, PrestamosAgent, SegurosAgent
from database import init_db, query_all, query_one, reset_demo

app = Flask(__name__)
init_db()

DEFAULT_ACCOUNT = "1002003001"

debit_agent = DebitoAgent()
credit_agent = CreditoAgent()
loans_agent = PrestamosAgent()
insurance_agent = SegurosAgent()


def _month_date(year: int, month: int, day: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last_day))


def _next_occurrence(day: int) -> date:
    today = date.today()
    candidate = _month_date(today.year, today.month, day)
    if candidate >= today:
        return candidate
    year = today.year + (1 if today.month == 12 else 0)
    month = 1 if today.month == 12 else today.month + 1
    return _month_date(year, month, day)


def _available_accounts() -> list[dict]:
    return query_all(
        """
        SELECT a.account_number, a.balance, c.full_name
        FROM accounts a
        JOIN clients c ON c.id = a.client_id
        ORDER BY a.account_number
        """
    )


def _validate_account_number(account_number: str | None) -> str:
    selected = str(account_number or DEFAULT_ACCOUNT).strip()
    exists = query_one(
        "SELECT account_number FROM accounts WHERE account_number = ?",
        (selected,),
    )
    if not exists:
        raise BankError("Cliente", "La cuenta seleccionada no existe.")
    return selected


def dashboard_data(account_number: str) -> dict:
    account = query_one(
        """
        SELECT
            a.id,
            a.account_number,
            a.balance,
            c.full_name,
            c.email,
            c.phone,
            dc.last4 AS debit_last4
        FROM accounts a
        JOIN clients c ON c.id = a.client_id
        LEFT JOIN debit_cards dc ON dc.account_id = a.id AND dc.active = 1
        WHERE a.account_number = ?
        """,
        (account_number,),
    )
    if not account:
        raise BankError("Cliente", "No se encontró la cuenta seleccionada.")

    credit = query_one(
        """
        SELECT cc.credit_limit, cc.balance, cc.cutoff_day, cc.due_day, cc.last4
        FROM credit_cards cc
        JOIN accounts a ON a.id = cc.account_id
        WHERE a.account_number = ? AND cc.active = 1
        """,
        (account_number,),
    )

    if credit:
        credit["available"] = round(
            float(credit["credit_limit"]) - float(credit["balance"]),
            2,
        )
        balance = float(credit["balance"])
        credit["minimum_payment"] = (
            round(min(balance, max(200.0, balance * 0.05)), 2)
            if balance > 0
            else 0
        )
        credit["total_payment"] = round(balance, 2)
        cutoff = _next_occurrence(int(credit["cutoff_day"]))
        due = _next_occurrence(int(credit["due_day"]))
        credit["cutoff_date"] = cutoff.isoformat()
        credit["due_date"] = due.isoformat()
        credit["days_until_due"] = (due - date.today()).days
        credit["alert"] = bool(
            balance > 0 and 0 <= credit["days_until_due"] <= 5
        )

    transactions = query_all(
        """
        SELECT type, amount, description, related_account, created_at
        FROM transactions
        WHERE account_id = ?
        ORDER BY id DESC
        LIMIT 12
        """,
        (account["id"],),
    )

    loans = query_all(
        """
        SELECT loan_type, amount, months, annual_rate, monthly_payment, status, created_at
        FROM loans
        WHERE account_id = ?
        ORDER BY id DESC
        LIMIT 6
        """,
        (account["id"],),
    )

    insurance = query_all(
        """
        SELECT insurance_type, monthly_premium, coverage, status, created_at
        FROM insurance_policies
        WHERE account_id = ?
        ORDER BY id DESC
        LIMIT 6
        """,
        (account["id"],),
    )

    transfer_targets = query_all(
        """
        SELECT a.account_number, a.balance, c.full_name
        FROM accounts a
        JOIN clients c ON c.id = a.client_id
        WHERE a.account_number <> ?
        ORDER BY a.account_number
        """,
        (account_number,),
    )

    logs = query_all(
        """
        SELECT agent_name, operation, message, created_at
        FROM agent_logs
        ORDER BY id DESC
        LIMIT 8
        """
    )

    return {
        "account": account,
        "credit": credit,
        "transactions": transactions,
        "loans": loans,
        "insurance": insurance,
        "transfer_targets": transfer_targets,
        "accounts": _available_accounts(),
        "logs": logs,
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/dashboard")
def dashboard():
    try:
        account_number = _validate_account_number(
            request.args.get("account", DEFAULT_ACCOUNT)
        )
        return jsonify({"ok": True, **dashboard_data(account_number)})
    except BankError as exc:
        return jsonify({"ok": False, "agent": exc.agent, "error": str(exc)}), 404


def _operation_payload() -> dict:
    payload = request.get_json(silent=True) or {}
    payload["account_number"] = _validate_account_number(
        payload.get("account_number")
    )
    return payload


@app.post("/api/debit")
def debit():
    try:
        return jsonify(debit_agent.process(_operation_payload()))
    except BankError as exc:
        return jsonify({"ok": False, "agent": exc.agent, "error": str(exc)}), 400


@app.post("/api/credit")
def credit():
    try:
        return jsonify(credit_agent.process(_operation_payload()))
    except BankError as exc:
        return jsonify({"ok": False, "agent": exc.agent, "error": str(exc)}), 400


@app.post("/api/loans")
def loans():
    try:
        return jsonify(loans_agent.process(_operation_payload()))
    except BankError as exc:
        return jsonify({"ok": False, "agent": exc.agent, "error": str(exc)}), 400


@app.post("/api/insurance")
def insurance():
    try:
        return jsonify(insurance_agent.process(_operation_payload()))
    except BankError as exc:
        return jsonify({"ok": False, "agent": exc.agent, "error": str(exc)}), 400


@app.post("/api/reset")
def reset():
    reset_demo()
    return jsonify(
        {
            "ok": True,
            "message": "Datos de demostración restaurados.",
            "default_account": DEFAULT_ACCOUNT,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
