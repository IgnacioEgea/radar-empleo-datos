"""Carga en SQLite todas las ofertas descargadas en data/raw.

Limpia el texto, calcula el sueldo anual cuando se puede y quita duplicados.
Se puede ejecutar las veces que haga falta: las ofertas que ya están no se repiten."""

import glob
import html
import json
import os
import re
import sqlite3

BD = "data/processed/radar.db"


def limpiar_texto(texto):
    """Quita etiquetas HTML, saltos de línea y espacios de más."""
    texto = html.unescape(texto or "")
    texto = re.sub(r"<[^>]+>", " ", texto)
    return re.sub(r"\s+", " ", texto).replace("...", " ").strip()


def sueldo_anual(texto):
    """Convierte '20000 - 27000 €/año' o '1.500 €/mes' en (mínimo, máximo) anual en euros."""
    if not texto:
        return None, None
    t = texto.lower()
    numeros = [float(n.replace(".", "").replace(",", ".")) for n in re.findall(r"\d[\d.,]*", t)]
    if "k" in t:
        numeros = [n * 1000 if n < 1000 else n for n in numeros]
    if "mes" in t:
        numeros = [n * 12 for n in numeros]
    elif "hora" in t:
        numeros = [n * 1760 for n in numeros]   # 40 h x 44 semanas aprox.
    numeros = [n for n in numeros if 8_000 <= n <= 250_000]   # descartamos valores raros
    if not numeros:
        return None, None
    return min(numeros), max(numeros)


os.makedirs("data/processed", exist_ok=True)
conexion = sqlite3.connect(BD)
cursor = conexion.cursor()

# 1. Creamos las tablas a partir del archivo SQL
with open("sql/01_crear_tablas.sql", encoding="utf-8") as f:
    cursor.executescript(f.read())

# 2. Recorremos todos los archivos descargados (data/raw/AAAA-MM-DD/*.json)
nuevas = 0
for archivo in sorted(glob.glob("data/raw/*/*.json")):
    fecha_recogida = os.path.basename(os.path.dirname(archivo))
    with open(archivo, encoding="utf-8") as f:
        ofertas = json.load(f)
    if isinstance(ofertas, dict):   # respuesta completa de la API: las ofertas están en "jobs"
        ofertas = ofertas.get("jobs", [])

    for o in ofertas:
        empresa = limpiar_texto(o.get("company")) or "Sin especificar"
        cursor.execute("INSERT OR IGNORE INTO empresas (nombre) VALUES (?)", (empresa,))
        id_empresa = cursor.execute(
            "SELECT id_empresa FROM empresas WHERE nombre = ?", (empresa,)).fetchone()[0]

        minimo, maximo = sueldo_anual(o.get("salary"))
        ciudad = (o.get("location") or "").split(",")[0].strip() or None

        cursor.execute("""
            INSERT OR IGNORE INTO ofertas
            (id_oferta, titulo, id_empresa, ciudad, sueldo_texto, sueldo_min_anual,
             sueldo_max_anual, jornada, portal, enlace, fecha_publicacion,
             fecha_recogida, busqueda, extracto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(o["id"]), limpiar_texto(o.get("title")), id_empresa, ciudad,
             o.get("salary") or None, minimo, maximo, o.get("type") or None,
             o.get("source"), o.get("link"), (o.get("updated") or "")[:10] or None,
             fecha_recogida, o.get("busqueda"), limpiar_texto(o.get("snippet"))))
        nuevas += cursor.rowcount   # 1 si era nueva, 0 si ya estaba

conexion.commit()
total = cursor.execute("SELECT COUNT(*) FROM ofertas").fetchone()[0]
con_sueldo = cursor.execute(
    "SELECT COUNT(*) FROM ofertas WHERE sueldo_min_anual IS NOT NULL").fetchone()[0]
conexion.close()

print(f"Ofertas nuevas añadidas: {nuevas}")
print(f"Ofertas totales en la base de datos: {total}")
print(f"Con sueldo publicado: {con_sueldo} ({con_sueldo / max(total, 1):.0%})")
