from __future__ import annotations

from typing import Any

import requests


COLOR_ANIME = 0xE83E8C
TIMEOUT_SEGUNDOS = 15


def publicar_noticias(webhook_url: str, noticias: list[dict[str, Any]]) -> None:
    for noticia in noticias:
        payload = crear_payload(noticia)
        respuesta = requests.post(webhook_url, json=payload, timeout=TIMEOUT_SEGUNDOS)
        respuesta.raise_for_status()


def crear_payload(noticia: dict[str, Any]) -> dict[str, Any]:
    embed: dict[str, Any] = {
        "title": noticia.get("titulo", "Noticia de anime"),
        "url": noticia.get("link"),
        "description": noticia.get("resumen", "Resumen no disponible."),
        "color": COLOR_ANIME,
        "fields": [
            {
                "name": "Categoría",
                "value": noticia.get("categoria", "Anime"),
                "inline": True,
            },
            {
                "name": "Fuente",
                "value": noticia.get("fuente", "Fuente desconocida"),
                "inline": True,
            },
        ],
        "footer": {
            "text": "Anime News Bot"
        },
    }

    imagen = noticia.get("imagen")
    if imagen:
        embed["image"] = {"url": imagen}

    return {
        "username": "Anime News Bot",
        "content": "Nueva noticia de anime",
        "embeds": [embed],
    }
