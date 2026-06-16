from __future__ import annotations

from typing import Any


MAX_CARACTERES_RESUMEN = 260


def resumir_noticia(noticia: dict[str, Any]) -> str:
    descripcion = limpiar_espacios(noticia.get("descripcion", ""))
    titulo = limpiar_espacios(noticia.get("titulo", ""))

    if descripcion:
        base = descripcion
    else:
        base = f"Novedad destacada sobre {titulo}."

    resumen = recortar_texto(base, MAX_CARACTERES_RESUMEN)
    return asegurar_espanol_visible(resumen)


def recortar_texto(texto: str, max_caracteres: int) -> str:
    if len(texto) <= max_caracteres:
        return texto

    recorte = texto[: max_caracteres - 1].rsplit(" ", 1)[0]
    if not recorte:
        recorte = texto[: max_caracteres - 1]

    return f"{recorte}..."


def limpiar_espacios(texto: str) -> str:
    return " ".join((texto or "").split())


def asegurar_espanol_visible(texto: str) -> str:
    if not texto:
        return "Resumen no disponible por ahora."

    return texto
