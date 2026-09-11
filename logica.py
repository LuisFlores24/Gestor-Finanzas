"""
logica.py
Funciones de negocio: obtener catálogos, validar e insertar movimientos.
"""

from database import get_connection

# IDs fijos de los catálogos (coinciden con database.py)
TIPO_INGRESO = 1
TIPO_GASTO = 2
TIPO_TRASPASO = 3


def obtener_catalogo(tabla, columnas="id, nombre"):
    """Devuelve una lista de tuplas (id, nombre) de un catálogo."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {columnas} FROM {tabla} ORDER BY id")
    filas = cur.fetchall()
    conn.close()
    return [tuple(f) for f in filas]


def obtener_tipos():
    return obtener_catalogo("tipos")


def obtener_cuentas():
    return obtener_catalogo("cuentas", "id, nombre, moneda")


def obtener_personas():
    return obtener_catalogo("personas")


def obtener_medios():
    return obtener_catalogo("medios")


def obtener_categorias():
    return obtener_catalogo("categorias", "id, nombre, tipo_id")


def _extraer_id(valor):
    """Si el valor viene como [id, etiqueta] o (id, etiqueta), devuelve solo el id."""
    if isinstance(valor, (list, tuple)):
        return valor[0] if len(valor) > 0 else None
    return valor


def validar_movimiento(tipo_id, cuenta_origen_id, cuenta_destino_id,
                        persona_origen_id, persona_destino_texto, monto):
    """
    Devuelve (True, "") si el movimiento es válido, o (False, "mensaje de error").
    Reglas:
    - Ingreso: requiere CuentaDestino y PersonaOrigen. No requiere CuentaOrigen.
    - Gasto: requiere CuentaOrigen y PersonaDestino (texto). No requiere CuentaDestino.
    - Traspaso: requiere CuentaOrigen y CuentaDestino, distintas entre sí.
    - Monto debe ser mayor a 0.
    """
    if monto is None or monto <= 0:
        return False, "El monto debe ser mayor a 0."

    if tipo_id == TIPO_INGRESO:
        if not cuenta_destino_id:
            return False, "Un ingreso requiere una cuenta destino."
        if not persona_origen_id:
            return False, "Un ingreso requiere indicar quién envió el dinero."

    elif tipo_id == TIPO_GASTO:
        if not cuenta_origen_id:
            return False, "Un gasto requiere una cuenta origen."
        if not persona_destino_texto or not persona_destino_texto.strip():
            return False, "Un gasto requiere el nombre de la persona/negocio destino."

    elif tipo_id == TIPO_TRASPASO:
        if not cuenta_origen_id or not cuenta_destino_id:
            return False, "Un traspaso requiere cuenta origen y cuenta destino."
        if cuenta_origen_id == cuenta_destino_id:
            return False, "La cuenta origen y destino no pueden ser la misma."

    else:
        return False, "Tipo de movimiento inválido."

    return True, ""


def insertar_movimiento(fecha, tipo_id, cuenta_origen_id, cuenta_destino_id,
                         persona_origen_id, persona_destino_texto, medio_id,
                         categoria_id, monto, codigo_transaccion, nota):
    """Valida e inserta un movimiento. Devuelve (True, "") o (False, "error")."""
    tipo_id = _extraer_id(tipo_id)
    cuenta_origen_id = _extraer_id(cuenta_origen_id)
    cuenta_destino_id = _extraer_id(cuenta_destino_id)
    persona_origen_id = _extraer_id(persona_origen_id)
    medio_id = _extraer_id(medio_id)
    categoria_id = _extraer_id(categoria_id)

    ok, msg = validar_movimiento(
        tipo_id, cuenta_origen_id, cuenta_destino_id,
        persona_origen_id, persona_destino_texto, monto
    )
    if not ok:
        return False, msg

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO movimientos (
            fecha, tipo_id, cuenta_origen_id, cuenta_destino_id,
            persona_origen_id, persona_destino_texto, medio_id,
            categoria_id, monto, codigo_transaccion, nota
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        fecha, tipo_id, cuenta_origen_id or None, cuenta_destino_id or None,
        persona_origen_id or None, persona_destino_texto or None, medio_id,
        categoria_id, monto, codigo_transaccion or None, nota or None
    ))
    conn.commit()
    conn.close()
    return True, "Movimiento registrado correctamente."