from __future__ import annotations

import re
import secrets
from dataclasses import dataclass, asdict
from datetime import datetime

from database import get_connection, query_all, query_one


class AgentError(ValueError):
    """Error de negocio detectado por uno de los agentes."""

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


def classify_user(age: int, gender: str) -> str:
    if age < 6:
        raise AgentError("Validación", "La edad mínima para inscribirse es de 6 años.")
    if gender == "femenino":
        return "Mujer" if age >= 18 else "Niña"
    if gender == "masculino":
        return "Hombre" if age >= 18 else "Niño"
    raise AgentError("Validación", "Selecciona una categoría de sexo válida para esta práctica.")


class RegistroAgent:
    name = "Registro"

    def process(self, payload: dict) -> dict:
        data = {
            "full_name": str(payload.get("full_name", "")).strip(),
            "age": int(payload.get("age", 0) or 0),
            "gender": str(payload.get("gender", "")).strip().lower(),
            "email": str(payload.get("email", "")).strip().lower(),
            "phone": re.sub(r"\D", "", str(payload.get("phone", ""))),
            "guardian_name": str(payload.get("guardian_name", "")).strip(),
            "guardian_phone": re.sub(r"\D", "", str(payload.get("guardian_phone", ""))),
            "sport_id": int(payload.get("sport_id", 0) or 0),
            "schedule_id": int(payload.get("schedule_id", 0) or 0),
        }
        return data


class ValidacionAgent:
    name = "Validación"
    email_re = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    def process(self, data: dict) -> dict:
        if len(data["full_name"]) < 5:
            raise AgentError(self.name, "Escribe el nombre completo del usuario.")
        if data["age"] < 6 or data["age"] > 99:
            raise AgentError(self.name, "La edad permitida en el sistema es de 6 a 99 años.")
        if not self.email_re.match(data["email"]):
            raise AgentError(self.name, "El correo electrónico no tiene un formato válido.")
        if len(data["phone"]) != 10:
            raise AgentError(self.name, "El teléfono debe contener 10 dígitos.")
        if data["sport_id"] <= 0 or data["schedule_id"] <= 0:
            raise AgentError(self.name, "Selecciona disciplina y horario antes de continuar.")

        data["category"] = classify_user(data["age"], data["gender"])

        if data["age"] < 18:
            if len(data["guardian_name"]) < 5:
                raise AgentError(self.name, "Para menores de edad se requiere nombre del tutor.")
            if len(data["guardian_phone"]) != 10:
                raise AgentError(self.name, "El teléfono del tutor debe contener 10 dígitos.")

        duplicate = query_one(
            """
            SELECT id FROM registrations
            WHERE email = ? AND sport_id = ? AND status = 'CONFIRMADA'
            """,
            (data["email"], data["sport_id"]),
        )
        if duplicate:
            raise AgentError(self.name, "Ese correo ya tiene una inscripción activa en la disciplina seleccionada.")
        return data


class DeportesAgent:
    name = "Deportes"

    def available_for(self, age: int) -> list[dict]:
        return query_all(
            """
            SELECT id, name, icon, description, registration_fee, monthly_fee, min_age, max_age
            FROM sports
            WHERE active = 1 AND ? BETWEEN min_age AND max_age
            ORDER BY name
            """,
            (age,),
        )

    def process(self, data: dict) -> dict:
        sport = query_one(
            """
            SELECT id, name, icon, description, registration_fee, monthly_fee, min_age, max_age
            FROM sports WHERE id = ? AND active = 1
            """,
            (data["sport_id"],),
        )
        if not sport:
            raise AgentError(self.name, "La disciplina seleccionada no existe o está inactiva.")
        if not sport["min_age"] <= data["age"] <= sport["max_age"]:
            raise AgentError(self.name, "La disciplina seleccionada no está disponible para esa edad.")
        data["sport"] = sport
        return data


class HorariosAgent:
    name = "Horarios"

    def available_for(self, sport_id: int, age: int) -> list[dict]:
        return query_all(
            """
            SELECT s.id, s.label, s.days, s.start_time, s.end_time, s.capacity,
                   s.capacity - COUNT(r.id) AS available_spots
            FROM schedules s
            LEFT JOIN registrations r
              ON r.schedule_id = s.id AND r.status = 'CONFIRMADA'
            WHERE s.sport_id = ? AND s.active = 1 AND ? BETWEEN s.min_age AND s.max_age
            GROUP BY s.id
            HAVING available_spots > 0
            ORDER BY s.start_time
            """,
            (sport_id, age),
        )

    def process(self, data: dict) -> dict:
        schedule = query_one(
            """
            SELECT s.id, s.sport_id, s.label, s.days, s.start_time, s.end_time,
                   s.min_age, s.max_age, s.capacity,
                   s.capacity - COUNT(r.id) AS available_spots
            FROM schedules s
            LEFT JOIN registrations r
              ON r.schedule_id = s.id AND r.status = 'CONFIRMADA'
            WHERE s.id = ? AND s.active = 1
            GROUP BY s.id
            """,
            (data["schedule_id"],),
        )
        if not schedule:
            raise AgentError(self.name, "El horario seleccionado no existe o está inactivo.")
        if schedule["sport_id"] != data["sport_id"]:
            raise AgentError(self.name, "El horario no corresponde a la disciplina elegida.")
        if not schedule["min_age"] <= data["age"] <= schedule["max_age"]:
            raise AgentError(self.name, "El horario no corresponde al rango de edad del usuario.")
        if schedule["available_spots"] <= 0:
            raise AgentError(self.name, "Ese horario ya no tiene lugares disponibles.")
        data["schedule"] = schedule
        return data


class CostosAgent:
    name = "Costos"

    def process(self, data: dict) -> dict:
        registration_fee = float(data["sport"]["registration_fee"])
        monthly_fee = float(data["sport"]["monthly_fee"])
        discount_rate = 0.15 if data["age"] < 18 else 0.0
        discount = round(monthly_fee * discount_rate, 2)
        total = round(registration_fee + monthly_fee - discount, 2)
        data["costs"] = {
            "registration_fee": registration_fee,
            "monthly_fee": monthly_fee,
            "discount_rate": int(discount_rate * 100),
            "discount": discount,
            "total_first_payment": total,
        }
        return data


class ConfirmacionAgent:
    name = "Confirmación"

    def process(self, data: dict) -> dict:
        folio = f"CD-{datetime.now():%Y%m%d}-{secrets.token_hex(3).upper()}"
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO registrations (
                    folio, full_name, age, gender, category, email, phone,
                    guardian_name, guardian_phone, sport_id, schedule_id,
                    registration_fee, monthly_fee, discount, total_first_payment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    folio,
                    data["full_name"],
                    data["age"],
                    data["gender"],
                    data["category"],
                    data["email"],
                    data["phone"],
                    data["guardian_name"] or None,
                    data["guardian_phone"] or None,
                    data["sport_id"],
                    data["schedule_id"],
                    data["costs"]["registration_fee"],
                    data["costs"]["monthly_fee"],
                    data["costs"]["discount"],
                    data["costs"]["total_first_payment"],
                ),
            )
            registration_id = cursor.lastrowid
        data["registration_id"] = registration_id
        data["folio"] = folio
        return data


class CoordinadorAgent:
    name = "Coordinador"

    def __init__(self):
        self.registro = RegistroAgent()
        self.validacion = ValidacionAgent()
        self.deportes = DeportesAgent()
        self.horarios = HorariosAgent()
        self.costos = CostosAgent()
        self.confirmacion = ConfirmacionAgent()

    def process(self, payload: dict) -> dict:
        trace: list[AgentStep] = [
            AgentStep(self.name, "ok", "Solicitud recibida. Coordinando agentes especializados."),
        ]
        data: dict = {}
        try:
            data = self.registro.process(payload)
            trace.append(AgentStep("Registro", "ok", "Datos capturados y normalizados."))

            data = self.validacion.process(data)
            trace.append(AgentStep("Validación", "ok", f"Datos correctos. Categoría detectada: {data['category']}."))

            data = self.deportes.process(data)
            trace.append(AgentStep("Deportes", "ok", f"Disciplina disponible: {data['sport']['name']}."))

            data = self.horarios.process(data)
            trace.append(AgentStep("Horarios", "ok", f"Horario con {data['schedule']['available_spots']} lugar(es) disponible(s)."))

            data = self.costos.process(data)
            trace.append(
                AgentStep(
                    "Costos",
                    "ok",
                    f"Primer pago calculado: ${data['costs']['total_first_payment']:.2f} MXN.",
                )
            )

            data = self.confirmacion.process(data)
            trace.append(AgentStep("Confirmación", "ok", f"Inscripción confirmada con folio {data['folio']}."))
            trace.append(AgentStep(self.name, "ok", "Proceso finalizado correctamente."))

            self._save_logs(data.get("registration_id"), trace)
            return {
                "ok": True,
                "trace": [step.to_dict() for step in trace],
                "registration": self._public_result(data),
            }
        except AgentError as exc:
            trace.append(AgentStep(exc.agent, "error", str(exc)))
            trace.append(AgentStep(self.name, "error", "Proceso detenido para evitar guardar datos incorrectos."))
            return {
                "ok": False,
                "trace": [step.to_dict() for step in trace],
                "error": str(exc),
                "agent": exc.agent,
            }
        except (TypeError, ValueError):
            message = "Hay un dato con formato inválido. Revisa edad, disciplina y horario."
            trace.append(AgentStep("Registro", "error", message))
            trace.append(AgentStep(self.name, "error", "Proceso detenido."))
            return {"ok": False, "trace": [step.to_dict() for step in trace], "error": message, "agent": "Registro"}

    @staticmethod
    def _save_logs(registration_id: int | None, trace: list[AgentStep]) -> None:
        if not registration_id:
            return
        with get_connection() as conn:
            conn.executemany(
                "INSERT INTO agent_logs (registration_id, agent_name, message) VALUES (?, ?, ?)",
                [(registration_id, step.agent, step.message) for step in trace],
            )

    @staticmethod
    def _public_result(data: dict) -> dict:
        return {
            "folio": data["folio"],
            "full_name": data["full_name"],
            "age": data["age"],
            "category": data["category"],
            "sport": data["sport"]["name"],
            "schedule": {
                "label": data["schedule"]["label"],
                "days": data["schedule"]["days"],
                "time": f"{data['schedule']['start_time']} - {data['schedule']['end_time']}",
            },
            "costs": data["costs"],
        }
