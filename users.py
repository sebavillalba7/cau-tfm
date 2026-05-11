# =============================================================
# backend/users.py
# Sistema de usuarios, áreas y autenticación — CAU TFM
# =============================================================
import hashlib
import json
import os
from pathlib import Path

# ------------------------------------------------------------------
# Áreas del club y sus permisos de secciones
# ------------------------------------------------------------------
AREAS = {
    "Médica": {
        "icon": "🏥",
        "secciones": ["home", "historial", "estadisticas_medicas", "evaluaciones", "resumen_individual"],
    },
    "Rendimiento": {
        "icon": "⚡",
        "secciones": ["home", "historial", "evaluaciones", "demandas_fisicas", "control_partidos", "resumen_individual"],
    },
    "Secretaría Técnica": {
        "icon": "📋",
        "secciones": ["home", "historial", "estadisticas_medicas", "evaluaciones", "demandas_fisicas", "control_partidos", "resumen_individual"],
    },
    "Administración": {
        "icon": "🔧",
        "secciones": ["home", "historial", "estadisticas_medicas", "evaluaciones", "demandas_fisicas", "control_partidos", "resumen_individual", "admin"],
    },
    "Scout": {
        "icon": "🔍",
        "secciones": ["home", "historial", "control_partidos"],
    },
}

# ------------------------------------------------------------------
# Usuarios iniciales del sistema (contraseñas en hash SHA-256)
# En producción esto vivirá en una base de datos o archivo JSON externo
# ------------------------------------------------------------------
def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

USUARIOS_INICIALES = {
    # ── Médica ────────────────────────────────────────────────
    "dr.garcia":    {"nombre": "Dr. García",      "area": "Médica",              "rol": "Médico",        "email": "dr.garcia@cauunion.com",    "pwd": _hash("medica123"), "activo": True},
    "dr.lopez":     {"nombre": "Dr. López",        "area": "Médica",              "rol": "Médico",        "email": "dr.lopez@cauunion.com",     "pwd": _hash("medica123"), "activo": True},
    "dr.martinez":  {"nombre": "Dr. Martínez",     "area": "Médica",              "rol": "Médico",        "email": "dr.martinez@cauunion.com",  "pwd": _hash("medica123"), "activo": True},
    "kine.perez":   {"nombre": "Lic. Pérez",       "area": "Médica",              "rol": "Kinesiólogo",   "email": "kine.perez@cauunion.com",   "pwd": _hash("kine123"),   "activo": True},
    "kine.gomez":   {"nombre": "Lic. Gómez",       "area": "Médica",              "rol": "Kinesiólogo",   "email": "kine.gomez@cauunion.com",   "pwd": _hash("kine123"),   "activo": True},
    "kine.diaz":    {"nombre": "Lic. Díaz",        "area": "Médica",              "rol": "Kinesiólogo",   "email": "kine.diaz@cauunion.com",    "pwd": _hash("kine123"),   "activo": True},
    "kine.silva":   {"nombre": "Lic. Silva",       "area": "Médica",              "rol": "Kinesiólogo",   "email": "kine.silva@cauunion.com",   "pwd": _hash("kine123"),   "activo": True},
    "kine.torres":  {"nombre": "Lic. Torres",      "area": "Médica",              "rol": "Kinesiólogo",   "email": "kine.torres@cauunion.com",  "pwd": _hash("kine123"),   "activo": True},
    # ── Rendimiento ───────────────────────────────────────────
    "pf.rodriguez": {"nombre": "Prof. Rodríguez",  "area": "Rendimiento",         "rol": "PF",            "email": "pf.rodriguez@cauunion.com", "pwd": _hash("rend123"),   "activo": True},
    "pf.fernandez": {"nombre": "Prof. Fernández",  "area": "Rendimiento",         "rol": "PF",            "email": "pf.fernandez@cauunion.com", "pwd": _hash("rend123"),   "activo": True},
    "pf.sanchez":   {"nombre": "Prof. Sánchez",    "area": "Rendimiento",         "rol": "PF",            "email": "pf.sanchez@cauunion.com",   "pwd": _hash("rend123"),   "activo": True},
    "nutri.ruiz":   {"nombre": "Lic. Ruiz",        "area": "Rendimiento",         "rol": "Nutricionista", "email": "nutri.ruiz@cauunion.com",   "pwd": _hash("rend123"),   "activo": True},
    "nutri.mora":   {"nombre": "Lic. Mora",        "area": "Rendimiento",         "rol": "Nutricionista", "email": "nutri.mora@cauunion.com",   "pwd": _hash("rend123"),   "activo": True},
    "nutri.vega":   {"nombre": "Lic. Vega",        "area": "Rendimiento",         "rol": "Nutricionista", "email": "nutri.vega@cauunion.com",   "pwd": _hash("rend123"),   "activo": True},
    "ct.ramirez":   {"nombre": "Prof. Ramírez",    "area": "Rendimiento",         "rol": "Cuerpo Técnico","email": "ct.ramirez@cauunion.com",   "pwd": _hash("rend123"),   "activo": True},
    "ct.jimenez":   {"nombre": "Prof. Jiménez",    "area": "Rendimiento",         "rol": "Cuerpo Técnico","email": "ct.jimenez@cauunion.com",   "pwd": _hash("rend123"),   "activo": True},
    "ct.herrera":   {"nombre": "Prof. Herrera",    "area": "Rendimiento",         "rol": "Cuerpo Técnico","email": "ct.herrera@cauunion.com",   "pwd": _hash("rend123"),   "activo": True},
    # ── Secretaría Técnica ────────────────────────────────────
    "st.castro":    {"nombre": "Lic. Castro",      "area": "Secretaría Técnica",  "rol": "Sec. Técnico",  "email": "st.castro@cauunion.com",    "pwd": _hash("sec123"),    "activo": True},
    "st.vargas":    {"nombre": "Lic. Vargas",      "area": "Secretaría Técnica",  "rol": "Sec. Técnico",  "email": "st.vargas@cauunion.com",    "pwd": _hash("sec123"),    "activo": True},
    "st.medina":    {"nombre": "Lic. Medina",      "area": "Secretaría Técnica",  "rol": "Sec. Técnico",  "email": "st.medina@cauunion.com",    "pwd": _hash("sec123"),    "activo": True},
    "st.guerrero":  {"nombre": "Lic. Guerrero",    "area": "Secretaría Técnica",  "rol": "Sec. Técnico",  "email": "st.guerrero@cauunion.com",  "pwd": _hash("sec123"),    "activo": True},
    # ── Administración ────────────────────────────────────────
    "admin":        {"nombre": "Administrador",    "area": "Administración",      "rol": "Admin",         "email": "admin@cauunion.com",        "pwd": _hash("admin123"),  "activo": True},
    # ── Scout ─────────────────────────────────────────────────
    "scout.blanco": {"nombre": "Lic. Blanco",      "area": "Scout",               "rol": "Scout",         "email": "scout.blanco@cauunion.com", "pwd": _hash("scout123"),  "activo": True},
    "scout.acosta": {"nombre": "Lic. Acosta",      "area": "Scout",               "rol": "Scout",         "email": "scout.acosta@cauunion.com", "pwd": _hash("scout123"),  "activo": True},
    "scout.rios":   {"nombre": "Lic. Ríos",        "area": "Scout",               "rol": "Scout",         "email": "scout.rios@cauunion.com",   "pwd": _hash("scout123"),  "activo": True},
}

# ------------------------------------------------------------------
# Registro de usuarios pendientes (simulado en archivo JSON local)
# En producción: reemplazar por base de datos real
# ------------------------------------------------------------------
PENDING_FILE = Path("backend/pending_users.json")

def cargar_pendientes() -> dict:
    if PENDING_FILE.exists():
        try:
            return json.loads(PENDING_FILE.read_text())
        except Exception:
            return {}
    return {}

def guardar_pendientes(data: dict):
    PENDING_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

# ------------------------------------------------------------------
# Funciones de autenticación
# ------------------------------------------------------------------
def verificar_login(username: str, password: str) -> dict | None:
    """Verifica credenciales. Devuelve el dict del usuario o None."""
    u = USUARIOS_INICIALES.get(username.lower().strip())
    if u and u["activo"] and u["pwd"] == _hash(password):
        return u
    # Buscar también en pendientes aprobados
    pendientes = cargar_pendientes()
    p = pendientes.get(username.lower().strip())
    if p and p.get("aprobado") and p.get("activo") and p["pwd"] == _hash(password):
        return p
    return None

def usuarios_por_area(area: str) -> list[str]:
    """Devuelve lista de usernames del área indicada."""
    result = [u for u, d in USUARIOS_INICIALES.items() if d["area"] == area]
    pendientes = cargar_pendientes()
    result += [u for u, d in pendientes.items() if d.get("area") == area and d.get("aprobado")]
    return result

def tiene_acceso(usuario: dict, seccion: str) -> bool:
    """Verifica si el usuario tiene acceso a una sección."""
    area = usuario.get("area", "")
    return seccion in AREAS.get(area, {}).get("secciones", [])

def registrar_usuario(username: str, nombre: str, area: str, rol: str, email: str, password: str) -> bool:
    """Registra un usuario pendiente de aprobación admin."""
    pendientes = cargar_pendientes()
    if username in USUARIOS_INICIALES or username in pendientes:
        return False  # Ya existe
    pendientes[username] = {
        "nombre": nombre,
        "area": area,
        "rol": rol,
        "email": email,
        "pwd": _hash(password),
        "activo": False,
        "aprobado": False,
    }
    guardar_pendientes(pendientes)
    return True

def aprobar_usuario(username: str) -> bool:
    """Admin aprueba un usuario pendiente."""
    pendientes = cargar_pendientes()
    if username in pendientes:
        pendientes[username]["aprobado"] = True
        pendientes[username]["activo"] = True
        guardar_pendientes(pendientes)
        return True
    return False
