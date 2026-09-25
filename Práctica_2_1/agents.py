from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PROFILE_HINTS = {
    "estudiante": ["Almacenamiento", "Periféricos", "Contenido digital", "Energía móvil"],
    "profesionista": ["Conectividad", "Contenido digital", "Periféricos", "Almacenamiento"],
    "creador": ["Contenido digital", "Audio", "Almacenamiento", "Periféricos"],
    "gamer": ["Periféricos", "Audio", "Almacenamiento", "Conectividad"],
}

NEED_HINTS = {
    "productividad": ["Periféricos", "Conectividad", "Almacenamiento"],
    "clases": ["Contenido digital", "Audio", "Almacenamiento", "Energía móvil"],
    "videollamadas": ["Contenido digital", "Audio", "Conectividad"],
    "movilidad": ["Energía móvil", "Almacenamiento", "Conectividad"],
    "gaming": ["Periféricos", "Audio", "Conectividad"],
    "almacenamiento": ["Almacenamiento"],
    "conectividad": ["Conectividad"],
}


@dataclass
class AgentOrchestrator:
    products: list[dict[str, Any]]

    def _market_agent(self, profile: str, need: str) -> dict[str, Any]:
        profile_key = profile if profile in PROFILE_HINTS else "estudiante"
        priorities = PROFILE_HINTS[profile_key]
        need_priorities = NEED_HINTS.get(need, [])
        categories = list(dict.fromkeys(need_priorities + priorities))
        return {
            "agent": "A1 · Mercado",
            "summary": f"Perfil {profile_key}: priorizar {need} con compatibilidad, precio y utilidad real.",
            "categories": categories,
        }

    def _catalog_agent(self, categories: list[str], budget: float) -> dict[str, Any]:
        ranked = []
        for product in self.products:
            score = 0
            if product["category"] in categories:
                score += max(1, len(categories) - categories.index(product["category"])) * 10
            if product["price"] <= budget:
                score += 7
            if product["featured"]:
                score += 2
            if product["stock"] > 0:
                score += 3
            ranked.append((score, product))
        ranked.sort(key=lambda item: (-item[0], item[1]["price"]))
        return {
            "agent": "A2 · Catálogo",
            "candidates": [product for score, product in ranked if score > 0][:5],
        }

    def _inventory_agent(self, candidates: list[dict[str, Any]], budget: float) -> dict[str, Any]:
        valid = [p for p in candidates if p["stock"] > 0 and p["price"] <= budget]
        rejected = [p["name"] for p in candidates if p["stock"] <= 0 or p["price"] > budget]
        return {
            "agent": "A3 · Inventario",
            "available": valid,
            "rejected": rejected,
            "summary": f"{len(valid)} opciones pasan stock y presupuesto de ${budget:,.0f} MXN.",
        }

    def _sales_agent(self, products: list[dict[str, Any]], profile: str, need: str) -> dict[str, Any]:
        recommendations = []
        for product in products[:3]:
            recommendations.append(
                {
                    **product,
                    "reason": f"Encaja con el perfil {profile} y la necesidad de {need}; está disponible y dentro del presupuesto.",
                }
            )
        return {
            "agent": "A5 · Ventas",
            "recommendations": recommendations,
        }

    def _quality_agent(self, recommendations: list[dict[str, Any]], budget: float) -> dict[str, Any]:
        checks = [
            "Precios tratados como datos simulados para fines académicos.",
            "Se excluyeron productos sin stock o fuera del presupuesto.",
            "No se prometen compatibilidades absolutas ni desempeño garantizado.",
        ]
        valid = all(p["stock"] > 0 and p["price"] <= budget for p in recommendations)
        return {
            "agent": "A6 · Calidad",
            "approved": valid and bool(recommendations),
            "checks": checks,
            "summary": "Recomendación aprobada." if valid and recommendations else "No hay una recomendación segura con los filtros actuales.",
        }

    def run(self, profile: str, need: str, budget: float) -> dict[str, Any]:
        market = self._market_agent(profile, need)
        catalog = self._catalog_agent(market["categories"], budget)
        inventory = self._inventory_agent(catalog["candidates"], budget)
        sales = self._sales_agent(inventory["available"], profile, need)
        quality = self._quality_agent(sales["recommendations"], budget)

        return {
            "orchestrator": "A0 · Orquestador",
            "profile": profile,
            "need": need,
            "budget": budget,
            "recommendations": sales["recommendations"],
            "agents": [
                {"name": market["agent"], "message": market["summary"]},
                {"name": catalog["agent"], "message": f"Evaluó {len(catalog['candidates'])} candidatos del catálogo."},
                {"name": inventory["agent"], "message": inventory["summary"]},
                {"name": sales["agent"], "message": f"Preparó {len(sales['recommendations'])} recomendaciones justificadas."},
                {"name": quality["agent"], "message": quality["summary"]},
            ],
            "quality": quality,
            "note": "Prototipo académico: precios, stock y recomendaciones son simulados.",
        }
