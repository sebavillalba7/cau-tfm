# =============================================================
# backend/users.py
# Sistema de usuarios, áreas y autenticación — CAU TFM
#
# Centraliza TODAS las funciones de usuario (login, permisos por área,
# alta/aprobación) en un único archivo de backend, separado del frontend
# (app.py), tal como pide la consigna del TFM.
# =============================================================
import hashlib
import streamlit as st

# ------------------------------------------------------------------
# Áreas del club y qué páginas puede ver cada una
# ------------------------------------------------------------------
AREAS = {
    "Médica": {
        "icon": "🏥",
        "secciones": ["home", "historial", "estadisticas_medicas", "evaluaciones",
                      "riesgo_lesion", "nutricion", "resumen_individual"],
    },
    "Rendimiento": {
        "icon": "⚡",
        "secciones": ["home", "historial", "evaluaciones", "riesgo_lesion",
                      "demandas_fisicas", "control_partidos", "nutricion", "resumen_individual"],
    },
    "Secretaría Técnica": {
        "icon": "📋",
        "secciones": ["home", "historial", "estadisticas_medicas", "evaluaciones",
                      "riesgo_lesion", "demandas_fisicas", "control_partidos",
                      "nutricion", "resumen_individual"],
    },
    "Administración": {
        "icon": "🔧",
        "secciones": ["home", "historial", "estadisticas_medicas", "evaluaciones",
                      "riesgo_lesion", "demandas_fisicas", "control_partidos",
                      "nutricion", "resumen_individual", "admin"],
    },
    "Scout": {
        "icon": "🔍",
        "secciones": ["home", "historial", "control_partidos"],
    },
}


def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


def hash_password(pwd: str) -> str:
    """Versión pública de _hash, para que el frontend pueda hashear la
    contraseña de un usuario nuevo antes de guardarla (alta/registro)."""
    return _hash(pwd)


# ------------------------------------------------------------------
# Usuarios base del sistema (contraseñas en hash SHA-256, nunca en texto plano)
# ------------------------------------------------------------------
USUARIOS_BASE = {
    "dr.garcia":     {"nombre": "Dr. García",       "area": "Médica",              "rol": "Médico",         "email": "dr.garcia@cauunion.com",     "pwd": _hash("medica123"), "activo": True},
    "dr.lopez":      {"nombre": "Dr. López",        "area": "Médica",              "rol": "Médico",         "email": "dr.lopez@cauunion.com",      "pwd": _hash("medica123"), "activo": True},
    "dr.martinez":   {"nombre": "Dr. Martínez",     "area": "Médica",              "rol": "Médico",         "email": "dr.martinez@cauunion.com",   "pwd": _hash("medica123"), "activo": True},
    "kine.perez":    {"nombre": "Lic. Pérez",       "area": "Médica",              "rol": "Kinesiólogo",    "email": "kine.perez@cauunion.com",    "pwd": _hash("kine123"),   "activo": True},
    "kine.gomez":    {"nombre": "Lic. Gómez",       "area": "Médica",              "rol": "Kinesiólogo",    "email": "kine.gomez@cauunion.com",    "pwd": _hash("kine123"),   "activo": True},
    "kine.diaz":     {"nombre": "Lic. Díaz",        "area": "Médica",              "rol": "Kinesiólogo",    "email": "kine.diaz@cauunion.com",     "pwd": _hash("kine123"),   "activo": True},
    "kine.silva":    {"nombre": "Lic. Silva",       "area": "Médica",              "rol": "Kinesiólogo",    "email": "kine.silva@cauunion.com",    "pwd": _hash("kine123"),   "activo": True},
    "kine.torres":   {"nombre": "Lic. Torres",      "area": "Médica",              "rol": "Kinesiólogo",    "email": "kine.torres@cauunion.com",   "pwd": _hash("kine123"),   "activo": True},
    "pf.rodriguez":  {"nombre": "Prof. Rodríguez",  "area": "Rendimiento",         "rol": "PF",             "email": "pf.rodriguez@cauunion.com",  "pwd": _hash("rend123"),   "activo": True},
    "pf.fernandez":  {"nombre": "Prof. Fernández",  "area": "Rendimiento",         "rol": "PF",             "email": "pf.fernandez@cauunion.com",  "pwd": _hash("rend123"),   "activo": True},
    "pf.sanchez":    {"nombre": "Prof. Sánchez",    "area": "Rendimiento",         "rol": "PF",             "email": "pf.sanchez@cauunion.com",    "pwd": _hash("rend123"),   "activo": True},
    "nutri.ruiz":    {"nombre": "Lic. Ruiz",        "area": "Rendimiento",         "rol": "Nutricionista",  "email": "nutri.ruiz@cauunion.com",    "pwd": _hash("rend123"),   "activo": True},
    "nutri.mora":    {"nombre": "Lic. Mora",        "area": "Rendimiento",         "rol": "Nutricionista",  "email": "nutri.mora@cauunion.com",    "pwd": _hash("rend123"),   "activo": True},
    "nutri.vega":    {"nombre": "Lic. Vega",        "area": "Rendimiento",         "rol": "Nutricionista",  "email": "nutri.vega@cauunion.com",    "pwd": _hash("rend123"),   "activo": True},
    "ct.ramirez":    {"nombre": "Prof. Ramírez",    "area": "Rendimiento",         "rol": "Cuerpo Técnico", "email": "ct.ramirez@cauunion.com",    "pwd": _hash("rend123"),   "activo": True},
    "ct.jimenez":    {"nombre": "Prof. Jiménez",    "area": "Rendimiento",         "rol": "Cuerpo Técnico", "email": "ct.jimenez@cauunion.com",    "pwd": _hash("rend123"),   "activo": True},
    "ct.herrera":    {"nombre": "Prof. Herrera",    "area": "Rendimiento",         "rol": "Cuerpo Técnico", "email": "ct.herrera@cauunion.com",    "pwd": _hash("rend123"),   "activo": True},
    "st.castro":     {"nombre": "Lic. Castro",      "area": "Secretaría Técnica",  "rol": "Sec. Técnico",   "email": "st.castro@cauunion.com",     "pwd": _hash("sec123"),    "activo": True},
    "st.vargas":     {"nombre": "Lic. Vargas",      "area": "Secretaría Técnica",  "rol": "Sec. Técnico",   "email": "st.vargas@cauunion.com",     "pwd": _hash("sec123"),    "activo": True},
    "st.medina":     {"nombre": "Lic. Medina",      "area": "Secretaría Técnica",  "rol": "Sec. Técnico",   "email": "st.medina@cauunion.com",     "pwd": _hash("sec123"),    "activo": True},
    "st.guerrero":   {"nombre": "Lic. Guerrero",    "area": "Secretaría Técnica",  "rol": "Sec. Técnico",   "email": "st.guerrero@cauunion.com",   "pwd": _hash("sec123"),    "activo": True},
    "admin":         {"nombre": "Administrador",    "area": "Administración",     "rol": "Admin",          "email": "futbolprofesionalcau@gmail.com", "pwd": _hash("admin123"), "activo": True},
    "scout.blanco":  {"nombre": "Lic. Blanco",      "area": "Scout",               "rol": "Scout",          "email": "scout.blanco@cauunion.com",  "pwd": _hash("scout123"),  "activo": True},
    "scout.acosta":  {"nombre": "Lic. Acosta",      "area": "Scout",               "rol": "Scout",          "email": "scout.acosta@cauunion.com",  "pwd": _hash("scout123"),  "activo": True},
    "scout.rios":    {"nombre": "Lic. Ríos",        "area": "Scout",               "rol": "Scout",          "email": "scout.rios@cauunion.com",    "pwd": _hash("scout123"),  "activo": True},
}


def _init_session_state():
    """Inicializa las claves de sesión que este módulo necesita, si el
    frontend todavía no lo hizo."""
    defaults = {"usuarios_extra": {}, "usuarios_desactivados": set()}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def todos_los_usuarios() -> dict:
    """Usuarios base + usuarios registrados y aprobados en esta sesión,
    con el estado activo/inactivo ya resuelto."""
    _init_session_state()
    u = {}
    for k, d in USUARIOS_BASE.items():
        u[k] = {**d, "activo": k not in st.session_state.usuarios_desactivados and d["activo"], "tipo": "base"}
    for k, d in st.session_state.usuarios_extra.items():
        if d.get("aprobado"):
            u[k] = {**d, "activo": k not in st.session_state.usuarios_desactivados and d.get("activo", True), "tipo": "extra"}
    return u


def verificar_login(username: str, password: str) -> dict | None:
    """Verifica credenciales. Devuelve el dict del usuario o None."""
    u = todos_los_usuarios().get(username.lower().strip())
    if u and u["activo"] and u["pwd"] == _hash(password):
        return u
    return None


def tiene_acceso(usuario: dict, seccion: str) -> bool:
    """Verifica si el usuario tiene acceso a una sección/página."""
    return seccion in AREAS.get(usuario.get("area", ""), {}).get("secciones", [])


def usuarios_por_area(area: str) -> list:
    """Devuelve los usernames activos de un área."""
    return [k for k, d in todos_los_usuarios().items() if d["area"] == area and d["activo"]]
