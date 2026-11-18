"""Prueba rápida: comprueba que la clave de Jooble funciona y muestra qué datos devuelve.
Gasta solo 1 petición de la API."""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()  # lee la clave del archivo .env
CLAVE = os.getenv("JOOBLE_API_KEY")
URL = f"https://es.jooble.org/api/{CLAVE}"  # buscador de Jooble para España

# Una búsqueda de ejemplo
busqueda = {"keywords": "data analyst junior", "location": "Madrid", "page": "1"}

respuesta = requests.post(URL, json=busqueda, timeout=30)
print("Código de respuesta:", respuesta.status_code)  # 200 = todo bien
respuesta.raise_for_status()

datos = respuesta.json()
ofertas = datos.get("jobs", [])
print("Ofertas totales para esta búsqueda:", datos.get("totalCount"))
print("Ofertas recibidas en esta página:", len(ofertas))

if ofertas:
    print("\nCampos de cada oferta:", list(ofertas[0].keys()))
    print("\nEjemplo:")
    print(json.dumps(ofertas[0], ensure_ascii=False, indent=2))

# Guardamos la respuesta para revisarla con calma
os.makedirs("data/raw", exist_ok=True)
with open("data/raw/prueba.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)
