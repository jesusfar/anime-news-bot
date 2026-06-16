from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def cargar_cache(ruta: Path) -> dict[str, list[str]]:
    if not ruta.exists():
        return {"publicadas": []}

    try:
        with ruta.open("r", encoding="utf-8") as archivo:
            cache = json.load(archivo)
    except json.JSONDecodeError:
        return {"publicadas": []}

    if "publicadas" not in cache or not isinstance(cache["publicadas"], list):
        return {"publicadas": []}

    return cache


def guardar_cache(ruta: Path, cache: dict[str, list[str]]) -> None:
    publicadas = list(dict.fromkeys(cache.get("publicadas", [])))
    ruta.write_text(
        json.dumps({"publicadas": publicadas[-500:]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def filtrar_noticias(
    noticias: list[dict[str, Any]],
    palabras_clave: list[str],
    cache: dict[str, list[str]],
) -> list[dict[str, Any]]:
    publicadas = set(cache.get("publicadas", []))
    vistas: set[str] = set()
    resultado = []

    for noticia in noticias:
        noticia_id = noticia.get("id")
        if not noticia_id or noticia_id in publicadas or noticia_id in vistas:
            continue

        texto = f"{noticia.get('titulo', '')} {noticia.get('descripcion', '')}".lower()
        if coincide_con_palabras_clave(texto, palabras_clave):
            resultado.append(noticia)
            vistas.add(noticia_id)

    return resultado


def coincide_con_palabras_clave(texto: str, palabras_clave: list[str]) -> bool:
    if not palabras_clave:
        return True

    texto_normalizado = texto.lower()
    return any(palabra.lower() in texto_normalizado for palabra in palabras_clave)
