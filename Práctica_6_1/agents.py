from __future__ import annotations

from dataclasses import asdict, dataclass
from math import pow

from database import get_connection, query_one


class BankError(ValueError):
    def __init__(self, agent: str, message: str):
        self.agent = agent
        super().__init__(message)


@dataclass
class AgentStep:
    agent: str
    status: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


def _amount(value) -> float:
    try:
        result = round(float(value), 2)
    except (TypeError, ValueError):
        raise BankError("Validación", "Captura un monto numérico válido.")
    if result <= 0:
        raise BankError("Validación", "El monto debe ser mayor a cero.")
    return result


def _log(agent: str, operation: str, message: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO agent_logs (agent_name, operation, message) VALUES (?, ?, ?)",
            (agent, operation, message),
        )


class ClienteAgent:
    name = "Cliente"

    def validate_account(self, account_number: str) -> dict:
        account = query_one(
            """
            SELECT a.id, a.account_number, a.balance, c.full_name, c.email, c.phone
            FROM accounts a
            JOIN clients c ON c.id = a.client_id
            WHERE a.account_number = ?
            """,
            (account_number,),
        )
        if not account:
            raise BankError(self.name, "La cuenta indicada no existe.")
        return account


class DebitoAgent:
    name = "Débito"

    def process(self, payload: dict) -> dict:
        action = str(payload.get("action", "")).strip().lower()
        source_number = str(payload.get("account_number", "")).strip()
        amount = _amount(payload.get("amount"))
        trace = [AgentStep("Coordinador", "ok", "Operación de débito recibida.")]

        if action not in {"deposit", "withdraw", "transfer"}:
            raise BankError(self.name, "Selecciona depósito, retiro o transferencia.")

        with get_connection() as conn:
            source = conn.execute(
                "SELECT id, account_number, balance FROM accounts WHERE account_number = ?",
                (source_number,),
            ).fetchone()
            if not source:
                raise BankError(self.name, "La cuenta origen no existe.")

            if action == "deposit":
                conn.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                    (amount, source["id"]),
                )
                conn.execute(
                    """
                    INSERT INTO transactions (account_id, type, amount, description)
                    VALUES (?, 'DEPOSITO', ?, ?)
                    """,
                    (source["id"], amount, "Depósito a tarjeta de débito"),
                )
                message = f"Depósito aplicado por ${amount:,.2f} MXN."

            elif action == "withdraw":
                if float(source["balance"]) < amount:
                    raise BankError(self.name, "Saldo insuficiente para realizar el retiro.")
                conn.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                    (amount, source["id"]),
                )
                conn.execute(
                    """
                    INSERT INTO transactions (account_id, type, amount, description)
                    VALUES (?, 'RETIRO', ?, ?)
                    """,
                    (source["id"], amount, "Retiro desde tarjeta de débito"),
                )
                message = f"Retiro aplicado por ${amount:,.2f} MXN."

            else:
                target_number = str(payload.get("target_account", "")).strip()
                if not target_number:
                    raise BankError(self.name, "Escribe la cuenta destino.")
                if target_number == source_number:
                    raise BankError(self.name, "La cuenta destino debe ser distinta a la cuenta origen.")

                target = conn.execute(
                    "SELECT id, account_number FROM accounts WHERE account_number = ?",
                    (target_number,),
                ).fetchone()
                if not target:
                    raise BankError(self.name, "La cuenta destino no existe.")
                if float(source["balance"]) < amount:
                    raise BankError(self.name, "Saldo insuficiente para realizar la transferencia.")

                conn.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                    (amount, source["id"]),
                )
                conn.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                    (amount, target["id"]),
                )
                conn.execute(
                    """
                    INSERT INTO transactions
                    (account_id, type, amount, description, related_account)
                    VALUES (?, 'TRANSFERENCIA_SALIDA', ?, ?, ?)
                    """,
                    (source["id"], amount, "Transferencia enviada", target_number),
                )
                conn.execute(
                    """
                    INSERT INTO transactions
                    (account_id, type, amount, description, related_account)
                    VALUES (?, 'TRANSFERENCIA_ENTRADA', ?, ?, ?)
                    """,
                    (target["id"], amount, "Transferencia recibida", source_number),
                )
                message = f"Transferencia de ${amount:,.2f} MXN enviada a {target_number}."

            new_balance = conn.execute(
                "SELECT balance FROM accounts WHERE id = ?", (source["id"],)
            ).fetchone()["balance"]

        trace.append(AgentStep(self.name, "ok", message))
        trace.append(AgentStep("Coordinador", "ok", "Operación completada y guardada en la base de datos."))
        _log(self.name, action, message)
        return {"ok": True, "balance": round(float(new_balance), 2), "trace": [x.to_dict() for x in trace]}


class CreditoAgent:
    name = "Crédito"

    def process(self, payload: dict) -> dict:
        account_number = str(payload.get("account_number", "")).strip()
        action = str(payload.get("action", "")).strip().lower()
        amount = _amount(payload.get("amount"))
        if action not in {"purchase", "payment"}:
            raise BankError(self.name, "Selecciona compra o pago de tarjeta.")

        trace = [AgentStep("Coordinador", "ok", "Operación de crédito recibida.")]

        with get_connection() as conn:
            card = conn.execute(
                """
                SELECT cc.id, cc.credit_limit, cc.balance
                FROM credit_cards cc
                JOIN accounts a ON a.id = cc.account_id
                WHERE a.account_number = ? AND cc.active = 1
                """,
                (account_number,),
            ).fetchone()
            if not card:
                raise BankError(self.name, "La cuenta no tiene una tarjeta de crédito activa.")

            if action == "purchase":
                available = float(card["credit_limit"]) - float(card["balance"])
                if amount > available:
                    raise BankError(self.name, "La compra supera el crédito disponible.")
                conn.execute(
                    "UPDATE credit_cards SET balance = balance + ? WHERE id = ?",
                    (amount, card["id"]),
                )
                conn.execute(
                    """
                    INSERT INTO credit_movements (credit_card_id, type, amount, description)
                    VALUES (?, 'COMPRA', ?, ?)
                    """,
                    (card["id"], amount, "Compra con tarjeta de crédito"),
                )
                message = f"Compra autorizada por ${amount:,.2f} MXN."
            else:
                current = float(card["balance"])
                if current <= 0:
                    raise BankError(self.name, "La tarjeta no tiene saldo pendiente.")
                applied = min(amount, current)
                conn.execute(
                    "UPDATE credit_cards SET balance = balance - ? WHERE id = ?",
                    (applied, card["id"]),
                )
                conn.execute(
                    """
                    INSERT INTO credit_movements (credit_card_id, type, amount, description)
                    VALUES (?, 'PAGO', ?, ?)
                    """,
                    (card["id"], applied, "Pago a tarjeta de crédito"),
                )
                message = f"Pago aplicado por ${applied:,.2f} MXN."

            new_balance = conn.execute(
                "SELECT balance FROM credit_cards WHERE id = ?", (card["id"],)
            ).fetchone()["balance"]

        trace.append(AgentStep(self.name, "ok", message))
        trace.append(AgentStep("Coordinador", "ok", "El estado de la tarjeta fue actualizado."))
        _log(self.name, action, message)
        return {"ok": True, "credit_balance": round(float(new_balance), 2), "trace": [x.to_dict() for x in trace]}


class PrestamosAgent:
    name = "Préstamos"
    rates = {
        "bancario": 18.5,
        "hipotecario": 10.5,
        "vehicular": 14.0,
    }

    def process(self, payload: dict) -> dict:
        account_number = str(payload.get("account_number", "")).strip()
        loan_type = str(payload.get("loan_type", "")).strip().lower()
        amount = _amount(payload.get("amount"))
        try:
            months = int(payload.get("months", 0))
        except (TypeError, ValueError):
            raise BankError(self.name, "El plazo debe ser un número entero.")

        if loan_type not in self.rates:
            raise BankError(self.name, "Selecciona un préstamo bancario, hipotecario o vehicular.")
        if amount < 1000:
            raise BankError(self.name, "El monto mínimo del préstamo es de $1,000 MXN.")
        if months < 6 or months > 360:
            raise BankError(self.name, "El plazo permitido es de 6 a 360 meses.")

        with get_connection() as conn:
            account = conn.execute(
                "SELECT id FROM accounts WHERE account_number = ?", (account_number,)
            ).fetchone()
            if not account:
                raise BankError(self.name, "La cuenta asociada no existe.")

            annual_rate = self.rates[loan_type]
            monthly_rate = annual_rate / 100 / 12
            if monthly_rate == 0:
                payment = amount / months
            else:
                payment = amount * monthly_rate / (1 - pow(1 + monthly_rate, -months))
            payment = round(payment, 2)

            conn.execute(
                """
                INSERT INTO loans
                (account_id, loan_type, amount, months, annual_rate, monthly_payment)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (account["id"], loan_type, amount, months, annual_rate, payment),
            )

        message = f"Solicitud {loan_type} registrada: ${amount:,.2f} MXN a {months} meses."
        _log(self.name, "solicitud", message)
        trace = [
            AgentStep("Coordinador", "ok", "Solicitud de préstamo recibida."),
            AgentStep(self.name, "ok", f"Tasa anual de demostración: {annual_rate:.1f}%."),
            AgentStep(self.name, "ok", f"Pago mensual estimado: ${payment:,.2f} MXN."),
        ]
        return {"ok": True, "monthly_payment": payment, "annual_rate": annual_rate, "trace": [x.to_dict() for x in trace]}


class SegurosAgent:
    name = "Seguros"
    products = {
        "vida": (420.00, "Protección de vida por $500,000 MXN"),
        "auto": (780.00, "Daños, robo y responsabilidad civil"),
        "patrimonio_casa": (650.00, "Protección de vivienda y contenidos"),
        "patrimonio_empresa": (1200.00, "Protección básica para negocio y activos"),
        "medico": (980.00, "Cobertura médica hospitalaria básica"),
    }

    def process(self, payload: dict) -> dict:
        account_number = str(payload.get("account_number", "")).strip()
        insurance_type = str(payload.get("insurance_type", "")).strip().lower()
        if insurance_type not in self.products:
            raise BankError(self.name, "Selecciona un seguro válido.")

        premium, coverage = self.products[insurance_type]
        with get_connection() as conn:
            account = conn.execute(
                "SELECT id FROM accounts WHERE account_number = ?", (account_number,)
            ).fetchone()
            if not account:
                raise BankError(self.name, "La cuenta asociada no existe.")

            conn.execute(
                """
                INSERT INTO insurance_policies
                (account_id, insurance_type, monthly_premium, coverage)
                VALUES (?, ?, ?, ?)
                """,
                (account["id"], insurance_type, premium, coverage),
            )

        label = insurance_type.replace("_", " ").title()
        message = f"Seguro {label} contratado por ${premium:,.2f} MXN al mes."
        _log(self.name, "contratacion", message)
        trace = [
            AgentStep("Coordinador", "ok", "Solicitud de seguro recibida."),
            AgentStep(self.name, "ok", coverage),
            AgentStep(self.name, "ok", message),
        ]
        return {"ok": True, "premium": premium, "coverage": coverage, "trace": [x.to_dict() for x in trace]}
