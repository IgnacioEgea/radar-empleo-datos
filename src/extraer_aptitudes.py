"""Usa IA (Gemini, plan gratuito) para leer cada oferta y sacar:
- las aptitudes que pide (SQL, Python, Power BI, inglés...),
- el nivel (junior / intermedio / senior),
- la modalidad (remoto / híbrido / presencial).

Manda las ofertas en lotes para gastar pocas peticiones y guarda el resultado en SQLite.
Solo procesa ofertas que aún no tienen nivel, así que se puede cortar y retomar."""

import json
import os
import sqlite3
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELO = "gemini-4-hydrogen"
LOTE = 25          # ofertas por petición
PAUSA = 5          # segundos entre peticiones (el plan gratuito limita por minuto)

INSTRUCCIONES = """Eres un analista del mercado laboral. Te paso ofertas de empleo de España
(título y un extracto del texto). Para cada una devuelve:

- "id": el mismo id que te paso.
- "nivel": "junior", "intermedio", "senior" o "sin_datos".
  Junior = prácticas, becario, sin experiencia o hasta 2 años. Senior = 5+ años, lead, manager, head.
- "modalidad": "remoto", "hibrido", "presencial" o "sin_datos". Solo si la oferta lo dice o lo deja claro.
- "aptitudes": lista de lo que pide, con "nombre" y "categoria".
  Categorías: "lenguaje", "herramienta", "idioma", "habilidad", "conocimiento".
  Usa nombres normalizados y cortos: "SQL", "Python", "R", "Excel", "Power BI", "Tableau",
  "Looker Studio", "Google Analytics" (también GA4), "Google Ads", "Meta Ads", "SEO", "SEM",
  "IA generativa", "Machine Learning", "Estadística", "Inglés", "Comunicación", "Trabajo en equipo".
  No inventes: si el extracto no menciona nada, devuelve una lista vacía.

Responde SOLO con una lista JSON, sin texto adicional."""


def analizar_lote(ofertas):
    """Envía un lote de ofertas a Gemini y devuelve la lista de resultados."""
    texto = "\n\n".join(f"id: {o[0]}\ntítulo: {o[1]}\nextracto: {o[2]}" for o in ofertas)
    for intento in range(3):
        try:
            respuesta = cliente.models.generate_content(
                model=MODELO,
                contents=texto,
                config=types.GenerateContentConfig(
                    system_instruction=INSTRUCCIONES,
                    response_mime_type="application/json",
                    temperature=0,   # respuestas lo más estables posible
                ),
            )
            return json.loads(respuesta.text)
        except Exception as error:   # límite por minuto, respuesta mal formada...
            print(f"  Aviso: {str(error)[:120]}. Reintento en 60 s...")
            time.sleep(60)
    return None


conexion = sqlite3.connect("data/processed/radar.db")
cursor = conexion.cursor()
pendientes = cursor.execute(
    "SELECT id_oferta, titulo, extracto FROM ofertas WHERE nivel IS NULL").fetchall()
print(f"Ofertas por analizar: {len(pendientes)}")

for inicio in range(0, len(pendientes), LOTE):
    lote = pendientes[inicio:inicio + LOTE]
    resultados = analizar_lote(lote)
    if resultados is None:
        print("La IA no responde. Lo hecho está guardado: vuelve a ejecutar más tarde.")
        break

    for r in resultados:
        cursor.execute("UPDATE ofertas SET nivel = ?, modalidad = ? WHERE id_oferta = ?",
                       (r.get("nivel"), r.get("modalidad"), str(r.get("id"))))
        for apt in r.get("aptitudes", []):
            nombre = apt.get("nombre", "").strip()
            if not nombre:
                continue
            cursor.execute("INSERT OR IGNORE INTO aptitudes (nombre, categoria) VALUES (?, ?)",
                           (nombre, apt.get("categoria")))
            cursor.execute("""INSERT OR IGNORE INTO oferta_aptitud (id_oferta, id_aptitud)
                              SELECT ?, id_aptitud FROM aptitudes WHERE nombre = ?""",
                           (str(r.get("id")), nombre))

    conexion.commit()   # guardamos después de cada lote
    print(f"  Analizadas {min(inicio + LOTE, len(pendientes))} de {len(pendientes)}")
    time.sleep(PAUSA)

# Resumen rápido: las 10 aptitudes más pedidas
print("\nTop 10 aptitudes:")
for nombre, veces in cursor.execute("""
        SELECT a.nombre, COUNT(*) FROM oferta_aptitud oa
        JOIN aptitudes a ON a.id_aptitud = oa.id_aptitud
        GROUP BY a.nombre ORDER BY COUNT(*) DESC LIMIT 10"""):
    print(f"  {nombre:<20} {veces}")
conexion.close()
