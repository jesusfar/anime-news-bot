from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from discord_sender import publicar_noticias
from fetchers import obtener_noticias
from filters import filtrar_noticias, cargar_cache, guardar_cache
from summarizer import resumir_noticia


RUTA_BASE = Path(__file__).resolve().parent
RUTA_FUENTES = RUTA_BASE / "sources.json"
RUTA_PALABRAS_CLAVE = RUTA_BASE / "keywords.json"
RUTA_CACHE = RUTA_BASE / "cache.json"
MAX_NOTICIAS = 5


def cargar_json(ruta: Path, valor_por_defecto: Any) -> Any:
    if not ruta.exists():
        return valor_por_defecto

    with ruta.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def preparar_noticias() -> list[dict[str, Any]]:
    fuentes = cargar_json(RUTA_FUENTES, [])
    palabras_clave = cargar_json(RUTA_PALABRAS_CLAVE, {}).get("palabras_clave", [])
    cache = cargar_cache(RUTA_CACHE)

    noticias = obtener_noticias(fuentes)
    noticias_filtradas = filtrar_noticias(noticias, palabras_clave, cache)

    noticias_finales = []
    for noticia in noticias_filtradas[:MAX_NOTICIAS]:
        noticia["resumen"] = resumir_noticia(noticia)
        noticias_finales.append(noticia)

    return noticias_finales


def main() -> None:
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("No se encontró DISCORD_WEBHOOK_URL. Configura la variable de entorno antes de ejecutar el bot.")
        return

    cache = cargar_cache(RUTA_CACHE)
    noticias = preparar_noticias()

    if not noticias:
        print("No se encontraron noticias nuevas para publicar.")
        return

    publicar_noticias(webhook_url, noticias)

    for noticia in noticias:
        cache["publicadas"].append(noticia["id"])

    guardar_cache(RUTA_CACHE, cache)
    print(f"Se publicaron {len(noticias)} noticia(s) en Discord.")


if __name__ == "__main__":
    main()
