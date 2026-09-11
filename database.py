"""
database.py
Crea y gestiona la base de datos SQLite del gestor de finanzas.
Al ejecutarse por primera vez, crea finanzas.db con las tablas y catálogos.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "finanzas.db"


def get_connection():
    """Devuelve una conexión a la base de datos con claves foráneas activadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # permite acceder a columnas por nombre
    return conn


def crear_tablas():
    conn = get_connection()
    cur = conn.cursor()

    # ---------- Catálogos ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tipos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            moneda TEXT NOT NULL CHECK(moneda IN ('PEN', 'USD'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            tipo_id INTEGER,  -- opcional: a qué tipo de movimiento aplica típicamente
            FOREIGN KEY (tipo_id) REFERENCES tipos(id)
        )
    """)

    # ---------- Tabla principal ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,                -- formato YYYY-MM-DD
            tipo_id INTEGER NOT NULL,
            cuenta_origen_id INTEGER,           -- NULL si es Ingreso
            cuenta_destino_id INTEGER,          -- NULL si es Gasto
            persona_origen_id INTEGER,          -- quién envía (obligatorio si Ingreso)
            persona_destino_texto TEXT,         -- nombre libre (obligatorio si Gasto)
            medio_id INTEGER NOT NULL,
            categoria_id INTEGER NOT NULL,
            monto REAL NOT NULL CHECK(monto > 0),
            codigo_transaccion TEXT,
            nota TEXT,
            FOREIGN KEY (tipo_id) REFERENCES tipos(id),
            FOREIGN KEY (cuenta_origen_id) REFERENCES cuentas(id),
            FOREIGN KEY (cuenta_destino_id) REFERENCES cuentas(id),
            FOREIGN KEY (persona_origen_id) REFERENCES personas(id),
            FOREIGN KEY (medio_id) REFERENCES medios(id),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

    conn.commit()
    conn.close()


def poblar_catalogos():
    """Inserta los valores iniciales de los catálogos, solo si están vacíos."""
    conn = get_connection()
    cur = conn.cursor()

    def insertar_si_vacio(tabla, valores, columnas="id, nombre"):
        cur.execute(f"SELECT COUNT(*) FROM {tabla}")
        if cur.fetchone()[0] == 0:
            placeholders = ", ".join(["?"] * len(valores[0]))
            cur.executemany(
                f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})",
                valores
            )

    insertar_si_vacio("tipos", [
        (1, "Ingreso"),
        (2, "Gasto"),
        (3, "Traspaso"),
    ])

    insertar_si_vacio("cuentas", [
        (1, "Yape/BCP Soles", "PEN"),
        (2, "Dólares BCP", "USD"),
        (3, "Wardadito mío", "PEN"),
        (4, "Wardadito papá", "PEN"),
    ], columnas="id, nombre, moneda")

    insertar_si_vacio("personas", [
        (1, "Yo"),
        (2, "Papá"),
        (3, "Tercero"),
    ])

    insertar_si_vacio("medios", [
        (1, "Yape"),
        (2, "Plin"),
        (3, "Transferencia BCP"),
        (4, "Efectivo"),
        (5, "Otro"),
    ])

    insertar_si_vacio("categorias", [
        (1, "Comida callejera", 2),
        (2, "Restaurante", 2),
        (3, "Universidad", 2),
        (4, "Taxi", 2),
        (5, "Cine", 2),
        (6, "Juegos", 2),
        (7, "Cursos", 2),
        (8, "Otros gastos", 2),
        (9, "Trabajo/Taxi (ingreso)", 1),
        (10, "Otros ingresos", 1),
        (11, "Traspaso interno", 3),
    ], columnas="id, nombre, tipo_id")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    crear_tablas()
    poblar_catalogos()
    print(f"Base de datos lista en: {DB_PATH}")