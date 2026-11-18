"""Descarga ofertas de empleo de datos y marketing en España desde la API de Jooble.

Guarda todo en data/raw/ofertas_AAAA-MM-DD.json (una lista de ofertas sin duplicados).
La API tiene un límite de peticiones, así que el script avisa de cuántas ha gastado."""

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

desde = (date.today() - timedelta(days=DIAS)).isoformat()
ofertas = {}       # usamos el id como clave para no repetir ofertas
peticiones = 0

for busqueda in BUSQUEDAS:
    for pagina in range(1, MAX_PAGINAS + 1):
        cuerpo = {"keywords": busqueda, "location": "", "page": str(pagina),
                  "datecreatedfrom": desde}
        respuesta = requests.post(URL, json=cuerpo, timeout=30)
        peticiones += 1
        respuesta.raise_for_status()
        resultados = respuesta.json().get("jobs", [])

        if not resultados:          # no hay más páginas: pasamos a la siguiente búsqueda
            break
        for oferta in resultados:
            oferta["busqueda"] = busqueda   # apuntamos con qué búsqueda la encontramos
            ofertas.setdefault(oferta["id"], oferta)

        time.sleep(1)               # una pausa para no saturar la API

    print(f"{busqueda:<28} -> {len(ofertas)} ofertas únicas acumuladas")

# Guardamos el resultado del día
archivo = f"data/raw/ofertas_{date.today().isoformat()}.json"
os.makedirs("data/raw", exist_ok=True)
with open(archivo, "w", encoding="utf-8") as f:
    json.dump(list(ofertas.values()), f, ensure_ascii=False, indent=2)

print(f"\nListo: {len(ofertas)} ofertas guardadas en {archivo}")
print(f"Peticiones gastadas en esta recogida: {peticiones}")
