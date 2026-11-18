-- Estructura de la base de datos del Radar del empleo.
-- Cuatro tablas: ofertas, empresas, aptitudes y la tabla puente oferta_aptitud.

-- Cada empresa aparece una sola vez
CREATE TABLE IF NOT EXISTS empresas (
    id_empresa  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT UNIQUE NOT NULL
);

-- Una fila por oferta (el id viene de Jooble, así evitamos duplicados)
CREATE TABLE IF NOT EXISTS ofertas (
    id_oferta         TEXT PRIMARY KEY,
    titulo            TEXT,
    id_empresa        INTEGER REFERENCES empresas(id_empresa),
    ciudad            TEXT,
    sueldo_texto      TEXT,      -- tal cual lo publica la oferta
    sueldo_min_anual  REAL,      -- en euros brutos al año, si se pudo calcular
    sueldo_max_anual  REAL,
    jornada           TEXT,      -- completa, parcial...
    portal            TEXT,      -- web donde se publicó originalmente
    enlace            TEXT,
    fecha_publicacion DATE,
    fecha_recogida    DATE,      -- día en que la descargamos
    busqueda          TEXT,      -- búsqueda con la que la encontramos primero
    extracto          TEXT,      -- texto de la oferta (recortado por la API)
    nivel             TEXT,      -- junior / intermedio / senior (lo rellena la IA)
    modalidad         TEXT       -- remoto / híbrido / presencial (lo rellena la IA)
);

-- Catálogo de aptitudes (SQL, Python, Power BI, inglés...)
CREATE TABLE IF NOT EXISTS aptitudes (
    id_aptitud  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT UNIQUE NOT NULL,
    categoria   TEXT          -- herramienta, lenguaje, idioma, habilidad...
);

-- Qué aptitudes pide cada oferta (una oferta pide muchas; una aptitud sale en muchas ofertas)
CREATE TABLE IF NOT EXISTS oferta_aptitud (
    id_oferta   TEXT    REFERENCES ofertas(id_oferta),
    id_aptitud  INTEGER REFERENCES aptitudes(id_aptitud),
    PRIMARY KEY (id_oferta, id_aptitud)
);
