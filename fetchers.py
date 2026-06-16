from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "anime-news-bot/1.0 (+https://github.com/)"
}
TIMEOUT_SEGUNDOS = 15
ORDEN_PRIORIDAD = {
    "alta": 1,
    "media": 2,
    "respaldo": 3,
}


def obtener_noticias(fuentes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    noticias: list[dict[str, Any]] = []

    for fuente in sorted(fuentes, key=ordenar_fuente):
        if not fuente.get("activo", True):
            continue

        try:
            tipo = fuente.get("tipo", "rss").lower()
            if tipo == "rss":
                noticias.extend(obtener_desde_rss(fuente))
            elif tipo == "web":
                noticias.extend(obtener_desde_web(fuente))
            else:
                print(f"Tipo de fuente no soportado: {tipo}")
        except Exception as error:
            nombre = fuente.get("nombre", "Fuente sin nombre")
            print(f"No se pudo leer la fuente {nombre}: {error}")

    return noticias


def ordenar_fuente(fuente: dict[str, Any]) -> tuple[int, int, str]:
    prioridad = str(fuente.get("prioridad", "media")).lower()
    orden = int(fuente.get("orden", 999))
    nombre = str(fuente.get("nombre", ""))
    return (ORDEN_PRIORIDAD.get(prioridad, 2), orden, nombre)


def obtener_desde_rss(fuente: dict[str, Any]) -> list[dict[str, Any]]:
    respuesta = requests.get(fuente["url"], headers=HEADERS, timeout=TIMEOUT_SEGUNDOS)
    respuesta.raise_for_status()
    feed = feedparser.parse(respuesta.content)

    noticias = []
    for entrada in feed.entries:
        link = entrada.get("link", "")
        titulo = limpiar_texto(entrada.get("title", "Sin título"))
        descripcion = limpiar_html(entrada.get("summary", entrada.get("description", "")))
        imagen = extraer_imagen_rss(entrada)

        if not link or not titulo:
            continue

        noticias.append(
            crear_noticia(
                titulo=titulo,
                descripcion=descripcion,
                link=link,
                imagen=imagen,
                fuente=fuente,
                publicado=entrada.get("published", entrada.get("updated", "")),
            )
        )

    return noticias


def obtener_desde_web(fuente: dict[str, Any]) -> list[dict[str, Any]]:
    respuesta = requests.get(fuente["url"], headers=HEADERS, timeout=TIMEOUT_SEGUNDOS)
    respuesta.raise_for_status()
    sopa = BeautifulSoup(respuesta.text, "html.parser")

    noticias = []
    selectores = fuente.get("selectores", {})
    selector_items = selectores.get("item", "article, .post, .entry, li")
    selector_titulo = selectores.get("titulo", "h1, h2, h3, a")
    selector_resumen = selectores.get("resumen", "p")
    selector_imagen = selectores.get("imagen", "img")

    for item in sopa.select(selector_items)[:20]:
        titulo_elemento = item.select_one(selector_titulo)
        enlace_elemento = item.select_one("a[href]")
        resumen_elemento = item.select_one(selector_resumen)
        imagen_elemento = item.select_one(selector_imagen)

        if not titulo_elemento or not enlace_elemento:
            continue

        titulo = limpiar_texto(titulo_elemento.get_text(" ", strip=True))
        link = urljoin(fuente["url"], enlace_elemento.get("href", ""))
        descripcion = limpiar_texto(resumen_elemento.get_text(" ", strip=True)) if resumen_elemento else ""
        imagen = None
        if imagen_elemento:
            imagen = imagen_elemento.get("src") or imagen_elemento.get("data-src")
            if imagen:
                imagen = urljoin(fuente["url"], imagen)

        if titulo and link:
            noticias.append(
                crear_noticia(
                    titulo=titulo,
                    descripcion=descripcion,
                    link=link,
                    imagen=imagen,
                    fuente=fuente,
                    publicado=datetime.now(timezone.utc).isoformat(),
                )
            )

    return noticias


def crear_noticia(
    titulo: str,
    descripcion: str,
    link: str,
    imagen: str | None,
    fuente: dict[str, Any],
    publicado: str,
) -> dict[str, Any]:
    return {
        "id": hashlib.sha256(link.encode("utf-8")).hexdigest(),
        "titulo": titulo,
        "descripcion": descripcion,
        "link": link,
        "imagen": imagen,
        "fuente": fuente.get("nombre", "Fuente desconocida"),
        "categoria": fuente.get("categoria", "Anime"),
        "publicado": publicado,
    }


def extraer_imagen_rss(entrada: Any) -> str | None:
    media_content = entrada.get("media_content", [])
    if media_content and media_content[0].get("url"):
        return media_content[0]["url"]

    media_thumbnail = entrada.get("media_thumbnail", [])
    if media_thumbnail and media_thumbnail[0].get("url"):
        return media_thumbnail[0]["url"]

    enlaces = entrada.get("links", [])
    for enlace in enlaces:
        if enlace.get("type", "").startswith("image/") and enlace.get("href"):
            return enlace["href"]

    return None


def limpiar_html(texto: str) -> str:
    return limpiar_texto(BeautifulSoup(texto or "", "html.parser").get_text(" ", strip=True))


def limpiar_texto(texto: str) -> str:
    return " ".join((texto or "").split())
