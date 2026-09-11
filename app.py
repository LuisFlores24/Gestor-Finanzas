"""
app.py
App Taipy: por ahora solo el formulario de registro de movimientos.
El historial y el dashboard se agregan en pasos siguientes.
"""

from taipy.gui import Gui, notify
from datetime import date

from database import crear_tablas, poblar_catalogos
import logica as logica

# Asegurar que la BD y catálogos existan al arrancar
crear_tablas()
poblar_catalogos()

# ---------- Datos para los desplegables ----------
# Formato que Taipy espera para selector: lista de [id, etiqueta]
tipos = [[t[0], t[1]] for t in logica.obtener_tipos()]
cuentas = [[c[0], f"{c[1]} ({c[2]})"] for c in logica.obtener_cuentas()]
personas = [[p[0], p[1]] for p in logica.obtener_personas()]
medios = [[m[0], m[1]] for m in logica.obtener_medios()]
categorias_todas = [[c[0], c[1], c[2]] for c in logica.obtener_categorias()]

# Mapa de tipo_id -> nombre, para armar la etiqueta "Categoría (Tipo)"
_nombre_tipo_por_id = {t[0]: t[1] for t in tipos}
categorias_lov = [
    [c[0], f"{c[1]} ({_nombre_tipo_por_id.get(c[2], '?')})"]
    for c in categorias_todas
]

# ---------- Variables de estado del formulario ----------
fecha_mov = date.today()
tipo_sel = tipos[0][0]  # id del tipo seleccionado (arranca en "Ingreso")
cuenta_origen_sel = None
cuenta_destino_sel = None
persona_origen_sel = None
persona_destino_texto = ""
medio_sel = medios[0][0]
categoria_sel = None
monto_str = ""
codigo_transaccion = ""
nota = ""

categoria_sel = categorias_lov[0][0] if categorias_lov else None

mensaje_resultado = ""


def on_change_tipo(state, var_name, value):
    pass  # ya no se necesita filtrar categorías, se mantiene por si se agregan otros efectos a futuro


def limpiar_formulario(state):
    state.cuenta_origen_sel = None
    state.cuenta_destino_sel = None
    state.persona_origen_sel = None
    state.persona_destino_texto = ""
    state.monto_str = ""
    state.codigo_transaccion = ""
    state.nota = ""


def registrar_movimiento(state):
    try:
        monto = float(state.monto_str.replace(",", ".")) if state.monto_str else None
    except ValueError:
        notify(state, "error", "El monto debe ser un número válido.")
        return

    ok, msg = logica.insertar_movimiento(
        fecha=state.fecha_mov.isoformat(),
        tipo_id=state.tipo_sel,
        cuenta_origen_id=state.cuenta_origen_sel,
        cuenta_destino_id=state.cuenta_destino_sel,
        persona_origen_id=state.persona_origen_sel,
        persona_destino_texto=state.persona_destino_texto,
        medio_id=state.medio_sel,
        categoria_id=state.categoria_sel,
        monto=monto,
        codigo_transaccion=state.codigo_transaccion,
        nota=state.nota,
    )

    if ok:
        notify(state, "success", msg)
        limpiar_formulario(state)
    else:
        notify(state, "error", msg)


# ---------- Página del formulario ----------
pagina_formulario = """
# Registrar movimiento

<|layout|columns=1 1|

<|
**Fecha**
<|{fecha_mov}|date|>

**Tipo de movimiento**
<|{tipo_sel}|selector|lov={tipos}|dropdown|value_by_id=True|on_change=on_change_tipo|>

**Cuenta origen** (gasto / traspaso)
<|{cuenta_origen_sel}|selector|lov={cuentas}|dropdown|value_by_id=True|>

**Cuenta destino** (ingreso / traspaso)
<|{cuenta_destino_sel}|selector|lov={cuentas}|dropdown|value_by_id=True|>

**Quién envía** (solo ingreso)
<|{persona_origen_sel}|selector|lov={personas}|dropdown|value_by_id=True|>
|>

<|
**Persona/negocio destino** (solo gasto)
<|{persona_destino_texto}|input|>

**Medio**
<|{medio_sel}|selector|lov={medios}|dropdown|value_by_id=True|>

**Categoría**
<|{categoria_sel}|selector|lov={categorias_lov}|dropdown|value_by_id=True|>

**Monto (S/. o USD según cuenta)**
<|{monto_str}|input|>

**Código de transacción (opcional)**
<|{codigo_transaccion}|input|>

**Nota (opcional)**
<|{nota}|input|multiline|>
|>

|>

<|Registrar|button|on_action=registrar_movimiento|>
"""

if __name__ == "__main__":
    gui = Gui(page=pagina_formulario)
    gui.run(title="Gestor de Finanzas", dark_mode=False)