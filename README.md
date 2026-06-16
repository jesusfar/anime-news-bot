# Anime News Bot

Bot en Python para buscar noticias importantes de anime y novedades de anime en Netflix, resumirlas en español y publicarlas en Discord usando `DISCORD_WEBHOOK_URL`.

## Funciones

- Lee fuentes configurables desde `sources.json`.
- Soporta RSS y scraping básico de páginas web.
- Filtra noticias por palabras clave desde `keywords.json`.
- Evita duplicados usando `cache.json`.
- Publica como máximo 5 noticias por ejecución.
- Incluye título, resumen corto, categoría, fuente, link e imagen si existe.
- Continúa con las demás fuentes si una fuente falla.
- Puede ejecutarse manualmente o con GitHub Actions dos veces al día.

## Requisitos

- Python 3.11 o superior.
- Un webhook de Discord.

## Instalación local

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuración

Define la variable de entorno con tu webhook:

```bash
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

Puedes editar `sources.json` para agregar, quitar o desactivar fuentes:

```json
{
  "nombre": "Crunchyroll Noticias ES",
  "url": "https://www.crunchyroll.com/es/news/rss",
  "tipo": "rss",
  "categoria": "Crunchyroll",
  "prioridad": "alta",
  "orden": 1,
  "activo": true
}
```

Tipos disponibles:

- `rss`: lee entradas RSS o Atom.
- `web`: hace scraping básico de enlaces en una página.

Puedes editar `keywords.json` para ajustar las palabras clave.

Las fuentes se procesan por `prioridad` en este orden: `alta`, `media` y `respaldo`. Dentro de cada prioridad se usa el campo `orden`.

## Ejecución

```bash
python bot.py
```

El bot publicará hasta 5 noticias nuevas que coincidan con las palabras clave.

## GitHub Actions

El workflow está en `.github/workflows/anime-news-bot.yml`.

Para usarlo:

1. En GitHub, abre `Settings > Secrets and variables > Actions`.
2. Crea un secreto llamado `DISCORD_WEBHOOK_URL`.
3. El bot se ejecutará dos veces al día y también podrá lanzarse manualmente desde `Actions`.

## Archivos principales

- `bot.py`: orquesta la ejecución.
- `fetchers.py`: obtiene noticias desde RSS o páginas web.
- `filters.py`: filtra palabras clave y duplicados.
- `summarizer.py`: genera resúmenes cortos en español.
- `discord_sender.py`: publica mensajes en Discord.
- `sources.json`: fuentes configurables.
- `keywords.json`: palabras clave.
- `cache.json`: historial de noticias publicadas.

## Notas

No se guardan secretos en el repositorio. El webhook siempre se lee desde la variable de entorno `DISCORD_WEBHOOK_URL`.
