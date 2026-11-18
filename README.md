# Radar del empleo en datos y marketing en España

> 🚧 Proyecto en construcción. Iré actualizando este README a medida que avance.

## La pregunta

**¿Qué piden las empresas a un perfil junior de datos y marketing digital en España, cuánto pagan y dónde está el teletrabajo?**

Estoy buscando mi primer puesto como analista de datos, y en vez de fiarme de listas genéricas de "las 10 herramientas que tienes que saber", he preferido mirar los datos: ofertas reales, publicadas ahora, en España.

## Qué voy a responder

- Qué herramientas y aptitudes aparecen más (SQL, Python, Power BI, GA4, IA…).
- Sueldos por puesto y ciudad, cuando la oferta los publica.
- Teletrabajo, híbrido o presencial según la ciudad.
- Cómo cambia la demanda con el tiempo, repitiendo la recogida.

## Cómo lo hago

| Fase | Herramienta |
|---|---|
| Datos | API oficial de [Jooble](https://es.jooble.org/api/about) (gratuita) |
| Almacenamiento | SQLite |
| Consultas | SQL (carpeta [`/sql`](sql)) |
| Extracción de aptitudes | IA generativa (Gemini, plan gratuito), validada a mano con una muestra |
| Análisis | Python y pandas |
| Visualización | Looker Studio (y Power BI como extra) |

## Estructura

```
radar-empleo-datos/
├── src/          # scripts de Python (recogida, carga, IA)
├── sql/          # consultas comentadas
├── data/
│   ├── raw/        # respuestas de la API tal cual
│   └── processed/  # base de datos y tablas limpias
├── notebooks/    # análisis exploratorio
└── dashboard/    # capturas y enlace al dashboard
```

## Cómo ejecutarlo

1. Clona el repositorio e instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Copia `.env.example` como `.env` y pon tu clave de la API de Jooble.

*(Los siguientes pasos llegarán con los scripts.)*

## Autor

**Ignacio Egea Villalba** · [Portfolio](https://web-portfolio-psi-eosin.vercel.app) · [LinkedIn](https://www.linkedin.com/in/nacho-egea)
