"""Descarga ofertas de empleo de datos y marketing en España desde la API de Jooble.

Cada búsqueda se guarda en su propio archivo: data/raw/AAAA-MM-DD/<busqueda>.json
Si la API corta por exceso de peticiones, basta con volver a ejecutar el script más tarde:
salta las búsquedas que ya están guardadas y sigue por donde iba."""

import json
import os
import time
from datetime import date, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()
URL = f"https://es.jooble.org/api/{os.getenv('JOOBLE_API_KEY')}"

# Puestos que buscamos (incluimos todos los niveles para poder comparar junior vs. senior)
BUSQUEDAS = [
    "data analyst", "analista de datos", "business analyst", "business intelligence",
    "data scientist", "marketing analyst", "analista marketing digital",
    "marketing digital", "SEO", "SEM", "growth marketing", "inteligencia artificial",
]
MAX_PAGINAS = 10   # 10 páginas x 30 ofertas = hasta 300 ofertas por búsqueda
DIAS = 30          # solo ofertas publicadas en el último mes

hoy = date.today().isoformat()
desde = (date.today() - timedelta(days=DIAS)).isoformat()
carpeta = f"data/raw/{hoy}"
os.makedirs(carpeta, exist_ok=True)
peticiones = 0


def pedir_pagina(busqueda, pagina):
    """Pide una página a la API. Devuelve la lista de ofertas o None si la API nos frena."""
    global peticiones
    cuerpo = {"keywords": busqueda, "location": "", "page": str(pagina), "datecreatedfrom": desde}
    respuesta = requests.post(URL, json=cuerpo, timeout=30)
    peticiones += 1
    if respuesta.status_code == 429:   # demasiadas peticiones
        return None
    respuesta.raise_for_status()
    return respuesta.json().get("jobs", [])


for busqueda in BUSQUEDAS:
    archivo = f"{carpeta}/{busqueda.replace(' ', '_')}.json"
    if os.path.exists(archivo):        # ya la teníamos de una ejecución anterior
        print(f"{busqueda:<28} -> ya guardada, la salto")
        continue

    ofertas = []
    for pagina in range(1, MAX_PAGINAS + 1):
        resultados = pedir_pagina(busqueda, pagina)
        if resultados is None:
            print(f"\nLa API nos ha frenado (error 429) en '{busqueda}'.")
            print("Lo ya guardado está a salvo. Vuelve a ejecutar el script dentro de un rato.")
            print(f"Peticiones gastadas en esta ejecución: {peticiones}")
            raise SystemExit
        if not resultados:             # no hay más páginas
            break
        ofertas += [{**oferta, "busqueda": busqueda} for oferta in resultados]
        time.sleep(2)                  # pausa para no saturar la API

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(ofertas, f, ensure_ascii=False, indent=2)
    print(f"{busqueda:<28} -> {len(ofertas)} ofertas guardadas")

print(f"\nRecogida completa en {carpeta}")
print(f"Peticiones gastadas en esta ejecución: {peticiones}")
