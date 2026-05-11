import streamlit as st
from pathlib import Path
import base64, hashlib, re
import pandas as pd
from datetime import date, datetime

st.set_page_config(
    page_title="CAU · Rendimiento Físico",
    page_icon="⚽", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Base ── */
.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d2040 50%, #0a1628 100%);
    color: #e8ecf4; font-family: 'Inter', sans-serif;
}
/* Ocultar header nativo de Streamlit */
header[data-testid="stHeader"] { display: none !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060f22 0%, #0a1a38 100%) !important;
    border-right: 1px solid rgba(200,16,46,0.3) !important;
}
section[data-testid="stSidebar"] * { color: #e8ecf4 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: #e8ecf4 !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; font-weight: 500 !important;
    text-align: left !important; padding-left: 14px !important;
    transition: all .2s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #c8102e, #8b0000) !important;
    border-color: transparent !important;
    color: #fff !important;
}

/* ── Botones generales ── */
.stButton > button {
    background: linear-gradient(135deg, #c8102e, #8b0000) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    transition: all .2s !important;
}
.stButton > button:hover { opacity: .85 !important; transform: translateY(-1px) !important; }

/* ── Inputs con letras BLANCAS siempre ── */
input, textarea, [data-baseweb="input"] input {
    background: #0d1f3c !important;
    border: 1px solid rgba(200,16,46,0.4) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-size: 14px !important;
    caret-color: #fff !important;
}
input::placeholder { color: #475569 !important; }
input:focus {
    border-color: #c8102e !important;
    box-shadow: 0 0 0 2px rgba(200,16,46,0.2) !important;
    color: #ffffff !important;
}
/* Labels de inputs */
.stTextInput label, .stSelectbox label {
    color: #94a3b8 !important; font-size: 12px !important; font-weight: 600 !important;
}
/* Selectbox */
.stSelectbox > div > div {
    background: #0d1f3c !important;
    border: 1px solid rgba(200,16,46,0.4) !important;
    border-radius: 10px !important; color: #ffffff !important;
}
[data-baseweb="select"] > div { background: #0d1f3c !important; }
[data-baseweb="select"] span { color: #ffffff !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13,32,64,0.8) !important;
    border-radius: 12px !important; padding: 4px !important; gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#c8102e,#8b0000) !important; color: #fff !important;
}

/* ── Login card ── */
.login-card {
    max-width: 460px; margin: 20px auto 0;
    padding: 32px 28px; border-radius: 24px;
    background: rgba(6,15,34,0.98);
    border: 1px solid rgba(200,16,46,0.35);
    box-shadow: 0 24px 64px rgba(0,0,0,0.7); text-align: center;
}
.login-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 44px; letter-spacing: 5px; color: #fff; line-height: 1;
}
.login-sub {
    color: #c8102e; font-size: 11px; font-weight: 700;
    letter-spacing: 3px; margin: 6px 0 0; text-transform: uppercase;
}

/* ── Header bar fijo ── */
.top-bar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    height: 52px;
    background: linear-gradient(90deg, #060f22 0%, #0d1f3c 40%, #1a0a14 60%, #060f22 100%);
    border-bottom: 2px solid rgba(200,16,46,0.5);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 24px; gap: 12px;
}
.top-bar-center {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 22px; letter-spacing: 5px; color: #fff;
    flex: 1; text-align: center;
}
.top-card {
    background: rgba(200,16,46,0.12);
    border: 1px solid rgba(200,16,46,0.25);
    border-radius: 8px; padding: 4px 14px;
    font-size: 12px; font-weight: 700; color: #fff; white-space: nowrap;
}
.top-card small { display: block; font-size: 9px; color: #94a3b8; font-weight: 400; letter-spacing: 1px; text-transform: uppercase; }
.spacer-top { height: 52px; }

/* ── Sección título ── */
.sec-title {
    color: #fff; font-size: 18px; font-weight: 900;
    border-left: 4px solid #c8102e; padding-left: 10px; margin: 20px 0 12px;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(10,22,40,.98), rgba(13,32,64,.9));
    border: 1px solid rgba(200,16,46,.2); border-radius: 16px; padding: 14px;
}
[data-testid="stMetricLabel"] p { color: #f87171 !important; font-weight:700 !important; font-size:11px !important; }
[data-testid="stMetricValue"]   { color: #fff !important; font-weight: 900 !important; }

/* ── Tabla admin ── */
.user-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.user-table th {
    background: rgba(200,16,46,0.15); color: #f87171;
    font-weight: 700; font-size: 10px; letter-spacing: 2px;
    text-transform: uppercase; padding: 10px 14px; text-align: left;
    border-bottom: 1px solid rgba(200,16,46,0.3);
}
.user-table td {
    padding: 10px 14px; color: #e2e8f0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.user-table tr:hover td { background: rgba(200,16,46,0.05); }
.badge-activo   { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); border-radius: 6px; padding: 2px 10px; font-size: 11px; font-weight: 700; }
.badge-inactivo { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); border-radius: 6px; padding: 2px 10px; font-size: 11px; font-weight: 700; }
.badge-area { background: rgba(26,90,180,0.15); color: #93c5fd; border: 1px solid rgba(26,90,180,0.3); border-radius: 6px; padding: 2px 10px; font-size: 11px; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .login-card { margin: 8px; padding: 20px 14px; }
    .login-title { font-size: 32px; }
    .top-bar-center { font-size: 16px; letter-spacing: 3px; }
    .top-card { display: none; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ÁREAS Y USUARIOS
# ══════════════════════════════════════════════════════════════
AREAS = {
    "Médica":               {"icon":"🏥","secciones":["home","historial","estadisticas_medicas","evaluaciones","resumen_individual"]},
    "Rendimiento":          {"icon":"⚡","secciones":["home","historial","evaluaciones","demandas_fisicas","control_partidos","resumen_individual"]},
    "Secretaría Técnica":   {"icon":"📋","secciones":["home","historial","estadisticas_medicas","evaluaciones","demandas_fisicas","control_partidos","resumen_individual"]},
    "Administración":       {"icon":"🔧","secciones":["home","historial","estadisticas_medicas","evaluaciones","demandas_fisicas","control_partidos","resumen_individual","admin"]},
    "Scout":                {"icon":"🔍","secciones":["home","historial","control_partidos"]},
}

def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

USUARIOS_BASE = {
    "dr.garcia":    {"nombre":"Dr. García",     "area":"Médica",             "rol":"Médico",        "email":"dr.garcia@cauunion.com",    "pwd":_hash("medica123"), "activo":True},
    "dr.lopez":     {"nombre":"Dr. López",       "area":"Médica",             "rol":"Médico",        "email":"dr.lopez@cauunion.com",     "pwd":_hash("medica123"), "activo":True},
    "dr.martinez":  {"nombre":"Dr. Martínez",    "area":"Médica",             "rol":"Médico",        "email":"dr.martinez@cauunion.com",  "pwd":_hash("medica123"), "activo":True},
    "kine.perez":   {"nombre":"Lic. Pérez",      "area":"Médica",             "rol":"Kinesiólogo",   "email":"kine.perez@cauunion.com",   "pwd":_hash("kine123"),   "activo":True},
    "kine.gomez":   {"nombre":"Lic. Gómez",      "area":"Médica",             "rol":"Kinesiólogo",   "email":"kine.gomez@cauunion.com",   "pwd":_hash("kine123"),   "activo":True},
    "kine.diaz":    {"nombre":"Lic. Díaz",       "area":"Médica",             "rol":"Kinesiólogo",   "email":"kine.diaz@cauunion.com",    "pwd":_hash("kine123"),   "activo":True},
    "kine.silva":   {"nombre":"Lic. Silva",      "area":"Médica",             "rol":"Kinesiólogo",   "email":"kine.silva@cauunion.com",   "pwd":_hash("kine123"),   "activo":True},
    "kine.torres":  {"nombre":"Lic. Torres",     "area":"Médica",             "rol":"Kinesiólogo",   "email":"kine.torres@cauunion.com",  "pwd":_hash("kine123"),   "activo":True},
    "pf.rodriguez": {"nombre":"Prof. Rodríguez", "area":"Rendimiento",        "rol":"PF",            "email":"pf.rodriguez@cauunion.com", "pwd":_hash("rend123"),   "activo":True},
    "pf.fernandez": {"nombre":"Prof. Fernández", "area":"Rendimiento",        "rol":"PF",            "email":"pf.fernandez@cauunion.com", "pwd":_hash("rend123"),   "activo":True},
    "pf.sanchez":   {"nombre":"Prof. Sánchez",   "area":"Rendimiento",        "rol":"PF",            "email":"pf.sanchez@cauunion.com",   "pwd":_hash("rend123"),   "activo":True},
    "nutri.ruiz":   {"nombre":"Lic. Ruiz",       "area":"Rendimiento",        "rol":"Nutricionista", "email":"nutri.ruiz@cauunion.com",   "pwd":_hash("rend123"),   "activo":True},
    "nutri.mora":   {"nombre":"Lic. Mora",       "area":"Rendimiento",        "rol":"Nutricionista", "email":"nutri.mora@cauunion.com",   "pwd":_hash("rend123"),   "activo":True},
    "nutri.vega":   {"nombre":"Lic. Vega",       "area":"Rendimiento",        "rol":"Nutricionista", "email":"nutri.vega@cauunion.com",   "pwd":_hash("rend123"),   "activo":True},
    "ct.ramirez":   {"nombre":"Prof. Ramírez",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","email":"ct.ramirez@cauunion.com",   "pwd":_hash("rend123"),   "activo":True},
    "ct.jimenez":   {"nombre":"Prof. Jiménez",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","email":"ct.jimenez@cauunion.com",   "pwd":_hash("rend123"),   "activo":True},
    "ct.herrera":   {"nombre":"Prof. Herrera",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","email":"ct.herrera@cauunion.com",   "pwd":_hash("rend123"),   "activo":True},
    "st.castro":    {"nombre":"Lic. Castro",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "email":"st.castro@cauunion.com",    "pwd":_hash("sec123"),    "activo":True},
    "st.vargas":    {"nombre":"Lic. Vargas",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "email":"st.vargas@cauunion.com",    "pwd":_hash("sec123"),    "activo":True},
    "st.medina":    {"nombre":"Lic. Medina",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "email":"st.medina@cauunion.com",    "pwd":_hash("sec123"),    "activo":True},
    "st.guerrero":  {"nombre":"Lic. Guerrero",   "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "email":"st.guerrero@cauunion.com",  "pwd":_hash("sec123"),    "activo":True},
    "admin":        {"nombre":"Administrador",   "area":"Administración",     "rol":"Admin",         "email":"admin@cauunion.com",        "pwd":_hash("admin123"),  "activo":True},
    "scout.blanco": {"nombre":"Lic. Blanco",     "area":"Scout",              "rol":"Scout",         "email":"scout.blanco@cauunion.com", "pwd":_hash("scout123"),  "activo":True},
    "scout.acosta": {"nombre":"Lic. Acosta",     "area":"Scout",              "rol":"Scout",         "email":"scout.acosta@cauunion.com", "pwd":_hash("scout123"),  "activo":True},
    "scout.rios":   {"nombre":"Lic. Ríos",       "area":"Scout",              "rol":"Scout",         "email":"scout.rios@cauunion.com",   "pwd":_hash("scout123"),  "activo":True},
}

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
for k, v in [("logged",False),("usuario",None),("pagina","home"),
             ("usuarios_extra",{}),("usuarios_desactivados",set())]:
    if k not in st.session_state: st.session_state[k] = v

def todos_los_usuarios():
    """Une usuarios base con extras aprobados, aplica desactivaciones."""
    u = {}
    for k, d in USUARIOS_BASE.items():
        activo = k not in st.session_state.usuarios_desactivados and d["activo"]
        u[k] = {**d, "activo": activo, "tipo": "base"}
    for k, d in st.session_state.usuarios_extra.items():
        if d.get("aprobado"):
            activo = k not in st.session_state.usuarios_desactivados and d.get("activo", True)
            u[k] = {**d, "activo": activo, "tipo": "extra"}
    return u

def verificar_login(username, password):
    u = todos_los_usuarios().get(username.lower().strip())
    if u and u["activo"] and u["pwd"] == _hash(password): return u
    return None

def tiene_acceso(u, s): return s in AREAS.get(u.get("area",""),{}).get("secciones",[])
def usuarios_por_area(area): return [k for k,d in todos_los_usuarios().items() if d["area"]==area and d["activo"]]

# ══════════════════════════════════════════════════════════════
# GOOGLE SHEETS
# ══════════════════════════════════════════════════════════════
SHEETS = {
    "gps":      "https://docs.google.com/spreadsheets/d/1W3hUX8zTPYXzDUSmdW7Nj2fXbEKlp1E2Us7kwNBhR6c/edit?gid=0",
    "lesiones": "https://docs.google.com/spreadsheets/d/1irSkXB8V_D_jZurEGUA9JMkLpE3e0_qad16_orjHDi8/edit?gid=0",
    "cmj":      "https://docs.google.com/spreadsheets/d/1VQLX1R1M0IW8j_TPXbVE8y5qaOA8-2qpj8cL-eGA1VY/edit?gid=1188054203",
    "nordico":  "https://docs.google.com/spreadsheets/d/1fhFajl9ckPYikfIKdBHTORcqQj0802JoNQ8-B3wEJWU/edit?gid=1994839095",
    "data_jug": "https://docs.google.com/spreadsheets/d/1aZ7yXUf3M4NA-7lNp9vlwUU_4tgU7Tecf5w-TrnelY8/edit?gid=0",
}
def gsheet_csv(url):
    sid = re.search(r"/d/([^/]+)", url).group(1)
    m = re.search(r"gid=(\d+)", url)
    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={m.group(1) if m else '0'}"

@st.cache_data(ttl=300)
def cargar_datos():
    dfs = {}
    for k, url in SHEETS.items():
        try:
            df = pd.read_csv(gsheet_csv(url), low_memory=False)
            df.columns = df.columns.astype(str).str.strip()
            dfs[k] = df
        except Exception:
            dfs[k] = pd.DataFrame()
    return dfs

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
ASSETS = Path("assets")
def img_b64(path):
    p = Path(path)
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

def escudo_tag(size=110):
    b64 = img_b64(ASSETS / "escudo_union.png")
    if b64:
        return f'<img src="data:image/png;base64,{b64}" style="width:{size}px;height:{size}px;object-fit:contain;filter:drop-shadow(0 0 16px rgba(200,16,46,.4));">'
    return '<div style="font-size:80px;line-height:1;">⚽</div>'

def top_bar(logged=False, usuario=None):
    now = datetime.now()
    if logged and usuario:
        centro = f"CLUB A. UNIÓN &nbsp;·&nbsp; {AREAS[usuario['area']]['icon']} {usuario['area'].upper()}"
    else:
        centro = "CLUB A. UNIÓN · DATA INTELLIGENCE"
    st.markdown(f"""
    <div class="top-bar">
        <div class="top-card">
            <small>Fecha</small>
            {now.strftime("%d/%m/%Y")}
        </div>
        <div class="top-bar-center">{centro}</div>
        <div class="top-card">
            <small>Hora</small>
            {now.strftime("%H:%M")}
        </div>
        <div class="top-card">
            <small>Sede</small>
            Santa Fe, ARG
        </div>
    </div>
    <div class="spacer-top"></div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════
def pagina_login():
    top_bar(logged=False)
    t1, t2, t3 = st.tabs(["🔐  Iniciar sesión", "📝  Registrarme", "🔑  Recuperar contraseña"])

    with t1:
        st.markdown(f"""
        <div class="login-card">
            {escudo_tag(100)}
            <div class="login-title">CLUB A. UNIÓN</div>
            <div class="login-sub">Data Intelligence · Rendimiento Físico</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _, col, _ = st.columns([1, 1.4, 1])
        with col:
            area_sel = st.selectbox("Área", ["— Seleccioná tu área —"] + list(AREAS.keys()), key="l_area")
            ua = usuarios_por_area(area_sel) if area_sel != "— Seleccioná tu área —" else []
            us = st.selectbox("Usuario", ["— Seleccioná —"] + ua, key="l_user",
                              disabled=(area_sel == "— Seleccioná tu área —"))
            pw = st.text_input("Contraseña", type="password", key="l_pwd", placeholder="Ingresá tu contraseña")
            if st.button("Ingresar →", use_container_width=True, key="btn_login"):
                if us == "— Seleccioná —": st.error("Seleccioná un usuario.")
                elif not pw: st.warning("Ingresá tu contraseña.")
                else:
                    u = verificar_login(us, pw)
                    if u:
                        st.session_state.logged   = True
                        st.session_state.usuario  = {**u, "username": us}
                        st.session_state.pagina   = "home"
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta o usuario inactivo.")

    with t2:
        st.markdown("### 📝 Solicitud de acceso")
        st.info("Tu solicitud quedará pendiente hasta que el administrador la apruebe. Una vez aprobada, podrás iniciar sesión normalmente.")
        c1, c2 = st.columns(2)
        with c1:
            rn  = st.text_input("Nombre completo",       key="rn",  placeholder="Ej: Juan Pérez")
            ra  = st.selectbox("Área",  list(AREAS.keys()), key="ra")
            ru  = st.text_input("Usuario (sin espacios)", key="ru",  placeholder="Ej: juan.perez")
        with c2:
            rr  = st.text_input("Rol / Cargo",           key="rr",  placeholder="Ej: Kinesiólogo")
            re_ = st.text_input("Email",                 key="re_", placeholder="tu@email.com")
            rp  = st.text_input("Contraseña",  type="password", key="rp",  placeholder="Mínimo 6 caracteres")
            rp2 = st.text_input("Repetir contraseña", type="password", key="rp2", placeholder="Repetí la contraseña")
        if st.button("Enviar solicitud", use_container_width=True, key="btn_reg"):
            if not all([rn, ra, ru, rr, re_, rp]):
                st.error("Completá todos los campos.")
            elif rp != rp2:
                st.error("Las contraseñas no coinciden.")
            elif " " in ru:
                st.error("El usuario no puede tener espacios.")
            elif ru.lower() in USUARIOS_BASE or ru.lower() in st.session_state.usuarios_extra:
                st.error("Ese nombre de usuario ya existe. Elegí otro.")
            else:
                st.session_state.usuarios_extra[ru.lower()] = {
                    "nombre": rn, "area": ra, "rol": rr, "email": re_,
                    "pwd": _hash(rp), "activo": False, "aprobado": False
                }
                st.success(f"✅ Solicitud enviada para **{rn}**. El admin debe aprobarla desde el Panel Admin.")

    with t3:
        st.markdown("### 🔑 Recuperación de contraseña")
        st.info("Ingresá tu email y el administrador te enviará una contraseña temporal.")
        rm = st.text_input("Email institucional", key="rm", placeholder="tu@email.com")
        if st.button("Solicitar recuperación", use_container_width=True, key="btn_rec"):
            if rm and "@" in rm:
                st.success("✅ Solicitud registrada. El administrador te contactará a la brevedad.")
            else:
                st.error("Ingresá un email válido.")

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def render_sidebar():
    u = st.session_state.usuario
    with st.sidebar:
        b64 = img_b64(ASSETS / "escudo_union.png")
        esc = f'<img src="data:image/png;base64,{b64}" style="width:56px;height:56px;object-fit:contain;filter:drop-shadow(0 0 10px rgba(200,16,46,.5));">' if b64 else "⚽"
        st.markdown(f"""
        <div style="text-align:center;padding:14px 0 12px;
             border-bottom:1px solid rgba(200,16,46,.25);margin-bottom:14px;">
            {esc}
            <div style="font-family:'Bebas Neue',sans-serif;font-size:16px;
                 letter-spacing:3px;margin-top:8px;color:#fff;">CAU · UNIÓN</div>
            <div style="font-size:12px;color:#f87171;margin-top:3px;">
                {AREAS[u["area"]]["icon"]} {u["nombre"]}
            </div>
            <div style="font-size:10px;color:#475569;margin-top:2px;">
                {u["rol"]} · {u["area"]}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<p style="font-size:10px;letter-spacing:3px;color:#475569;text-transform:uppercase;margin:0 0 8px;">MENÚ</p>', unsafe_allow_html=True)
        nav = [
            ("home",                 "🏠", "Inicio"),
            ("historial",            "👤", "Historial Jugadores"),
            ("estadisticas_medicas", "🏥", "Estadísticas Médicas"),
            ("evaluaciones",         "⚡", "Evaluaciones Físicas"),
            ("demandas_fisicas",     "📡", "Demandas Físicas"),
            ("control_partidos",     "⚽", "Control de Partidos"),
            ("resumen_individual",   "📄", "Resumen Individual"),
        ]
        for key, icon, label in nav:
            if tiene_acceso(u, key):
                if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.pagina = key; st.rerun()

        if tiene_acceso(u, "admin"):
            st.markdown("---")
            pend_n = sum(1 for d in st.session_state.usuarios_extra.values() if not d.get("aprobado"))
            if st.button(f"🔧  Panel Admin {'🔴' if pend_n else ''}", key="nav_admin", use_container_width=True):
                st.session_state.pagina = "admin"; st.rerun()

        st.markdown("---")
        if st.button("🚪  Cerrar sesión", use_container_width=True, key="btn_out"):
            st.session_state.logged  = False
            st.session_state.usuario = None
            st.session_state.pagina  = "home"
            st.rerun()

# ══════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════
def pagina_home():
    u = st.session_state.usuario
    st.markdown(f"""
    <div style="text-align:center;padding:24px 20px 12px;">
        {escudo_tag(120)}
        <div style="font-family:'Bebas Neue',sans-serif;font-size:56px;
             letter-spacing:6px;color:#fff;line-height:1;margin-top:12px;">CLUB A. UNIÓN</div>
        <div style="color:#c8102e;font-size:12px;font-weight:700;letter-spacing:4px;
             text-transform:uppercase;margin-top:6px;">Data Intelligence · Rendimiento Físico</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    cf, ct = st.columns([1, 2], gap="large")
    with cf:
        foto = img_b64(ASSETS / "foto_home.jpg")
        if foto:
            st.markdown(f'<img src="data:image/jpeg;base64,{foto}" style="width:100%;border-radius:16px;border:2px solid rgba(200,16,46,.3);">', unsafe_allow_html=True)
        else:
            st.markdown("""<div style="aspect-ratio:4/3;background:rgba(200,16,46,.06);
                 border:2px dashed rgba(200,16,46,.25);border-radius:16px;
                 display:flex;align-items:center;justify-content:center;
                 color:#475569;font-size:13px;text-align:center;padding:20px;">
                📷 Subí la foto como<br><code>assets/foto_home.jpg</code></div>""", unsafe_allow_html=True)
    with ct:
        st.markdown("""
        <div style="background:rgba(6,15,34,.95);border:1px solid rgba(200,16,46,.2);
             border-radius:16px;padding:28px 32px;height:100%;box-sizing:border-box;">
            <div style="font-size:10px;color:#c8102e;font-weight:700;letter-spacing:3px;
                 text-transform:uppercase;margin-bottom:10px;">Plataforma Tecnológica</div>
            <div style="font-size:26px;font-weight:900;color:#fff;
                 margin-bottom:16px;line-height:1.2;">
                Data Intelligence aplicada al<br>rendimiento deportivo
            </div>
            <div style="font-size:14px;color:#94a3b8;line-height:1.8;">
                Una plataforma centralizada que transforma datos físicos, médicos y
                tácticos en inteligencia accionable para el cuerpo técnico, el área
                médica y la secretaría técnica del Club A. Unión.<br><br>
                Desde el GPS en el campo hasta el modelo de riesgo de lesión
                con Machine Learning — toda la información del plantel en un
                solo lugar, en tiempo real, accesible para quienes toman decisiones.
            </div>
            <div style="display:flex;gap:10px;margin-top:18px;flex-wrap:wrap;">
                <span style="background:rgba(200,16,46,.15);border:1px solid rgba(200,16,46,.3);
                      color:#f87171;border-radius:6px;padding:4px 12px;font-size:11px;font-weight:700;">
                    📡 GPS en tiempo real
                </span>
                <span style="background:rgba(200,16,46,.15);border:1px solid rgba(200,16,46,.3);
                      color:#f87171;border-radius:6px;padding:4px 12px;font-size:11px;font-weight:700;">
                    🤖 Machine Learning
                </span>
                <span style="background:rgba(200,16,46,.15);border:1px solid rgba(200,16,46,.3);
                      color:#f87171;border-radius:6px;padding:4px 12px;font-size:11px;font-weight:700;">
                    🏥 Gestión médica
                </span>
                <span style="background:rgba(200,16,46,.15);border:1px solid rgba(200,16,46,.3);
                      color:#f87171;border-radius:6px;padding:4px 12px;font-size:11px;font-weight:700;">
                    📊 Reportes PDF
                </span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sec-title">Resumen del plantel</div>', unsafe_allow_html=True)
    try:
        dfs = cargar_datos()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("👥 Jugadores",        dfs["data_jug"].shape[0] if not dfs["data_jug"].empty else "—")
        c2.metric("🏥 Registros médicos", dfs["lesiones"].shape[0] if not dfs["lesiones"].empty else "—")
        c3.metric("📡 Sesiones GPS",     dfs["gps"].shape[0]      if not dfs["gps"].empty      else "—")
        c4.metric("📅 Hoy",              date.today().strftime("%d/%m/%Y"))
    except Exception:
        c1,c2,c3,c4 = st.columns(4)
        for c,l in zip([c1,c2,c3,c4],["👥 Jugadores","🏥 Médicos","📡 GPS","📅 Hoy"]):
            c.metric(l,"—")

    st.markdown(f"""
    <div style="background:rgba(200,16,46,.07);border:1px solid rgba(200,16,46,.2);
         border-radius:14px;padding:18px 24px;margin-top:16px;">
        <div style="font-size:10px;color:#c8102e;font-weight:700;letter-spacing:2px;
             text-transform:uppercase;">Sesión activa</div>
        <div style="font-size:20px;font-weight:800;color:#fff;margin:4px 0 4px;">
            {u["nombre"]} &nbsp;·&nbsp; {u["rol"]}
        </div>
        <div style="font-size:13px;color:#94a3b8;">
            Área: <b style="color:#e2e8f0;">{u["area"]}</b>
            &nbsp;|&nbsp; Acceso a
            <b style="color:#e2e8f0;">{len(AREAS[u["area"]]["secciones"])}</b> secciones
        </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════
def pagina_admin():
    st.markdown('<div class="sec-title">🔧 Panel de Administración</div>', unsafe_allow_html=True)

    # ── Pendientes ──────────────────────────────────────────
    pendientes = {k:d for k,d in st.session_state.usuarios_extra.items() if not d.get("aprobado")}
    if pendientes:
        st.warning(f"⚠️ {len(pendientes)} solicitud(es) pendiente(s) de aprobación")
        for username, datos in pendientes.items():
            with st.expander(f"👤 {datos['nombre']} — {datos['area']} · {datos['rol']}"):
                st.write(f"**Email:** {datos.get('email','—')} &nbsp;|&nbsp; **Usuario:** `{username}`")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"✅ Aprobar", key=f"apr_{username}"):
                        st.session_state.usuarios_extra[username]["aprobado"] = True
                        st.session_state.usuarios_extra[username]["activo"]   = True
                        st.success(f"✅ {datos['nombre']} aprobado. Ya puede iniciar sesión con usuario `{username}`.")
                        st.rerun()
                with c2:
                    if st.button(f"❌ Rechazar", key=f"rec_{username}"):
                        del st.session_state.usuarios_extra[username]
                        st.warning("Usuario rechazado y eliminado."); st.rerun()
    else:
        st.success("✅ No hay solicitudes pendientes.")

    st.markdown("---")
    st.markdown("#### 👥 Usuarios del sistema")

    # Filtro por área
    areas_filtro = ["Todas"] + list(AREAS.keys())
    fa = st.selectbox("Filtrar por área", areas_filtro, key="filtro_area_admin")

    todos = todos_los_usuarios()
    rows = [(k, d) for k, d in todos.items() if fa == "Todas" or d["area"] == fa]

    # Construir tabla HTML
    filas_html = ""
    for username, d in rows:
        badge_activo = '<span class="badge-activo">Activo</span>' if d["activo"] else '<span class="badge-inactivo">Inactivo</span>'
        badge_area   = f'<span class="badge-area">{d["area"]}</span>'
        filas_html += f"""
        <tr>
            <td><code style="color:#60a5fa;">{username}</code></td>
            <td><b>{d["nombre"]}</b></td>
            <td>{badge_area}</td>
            <td style="color:#94a3b8;">{d["rol"]}</td>
            <td style="color:#64748b;font-size:12px;">{d.get("email","—")}</td>
            <td>{badge_activo}</td>
        </tr>"""

    st.markdown(f"""
    <div style="background:rgba(6,15,34,.9);border:1px solid rgba(255,255,255,.06);
         border-radius:16px;overflow:hidden;margin-top:8px;">
        <table class="user-table">
            <thead><tr>
                <th>Usuario</th><th>Nombre</th><th>Área</th>
                <th>Rol</th><th>Email</th><th>Estado</th>
            </tr></thead>
            <tbody>{filas_html}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)

    # ── Activar / Desactivar / Eliminar ─────────────────────
    st.markdown("---")
    st.markdown("#### ⚙️ Gestión de usuario")
    usernames_todos = list(todos.keys())
    sel = st.selectbox("Seleccioná un usuario", ["— elegí —"] + usernames_todos, key="admin_sel_user")
    if sel != "— elegí —":
        d = todos[sel]
        st.write(f"**{d['nombre']}** · {d['area']} · {d['rol']} · `{sel}`")
        col1, col2, col3 = st.columns(3)
        with col1:
            if d["activo"]:
                if st.button("🔴 Desactivar acceso", key="btn_desact"):
                    st.session_state.usuarios_desactivados.add(sel)
                    st.warning(f"{d['nombre']} desactivado."); st.rerun()
            else:
                if st.button("🟢 Activar acceso", key="btn_act"):
                    st.session_state.usuarios_desactivados.discard(sel)
                    st.success(f"{d['nombre']} activado."); st.rerun()
        with col2:
            if sel in st.session_state.usuarios_extra:
                if st.button("🗑️ Eliminar usuario", key="btn_del"):
                    del st.session_state.usuarios_extra[sel]
                    st.warning(f"Usuario {sel} eliminado."); st.rerun()
            else:
                st.caption("(Usuarios base no se pueden eliminar)")
        with col3:
            st.caption(f"Tipo: {'Registrado' if sel in st.session_state.usuarios_extra else 'Base'}")

# ══════════════════════════════════════════════════════════════
# PÁGINAS EN CONSTRUCCIÓN
# ══════════════════════════════════════════════════════════════
def pagina_construccion(nombre):
    st.markdown(f'<div class="sec-title">🚧 {nombre}</div>', unsafe_allow_html=True)
    st.info("Esta sección está siendo desarrollada. Volvé pronto.")

# ══════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════
def render_pagina():
    u = st.session_state.usuario
    p = st.session_state.pagina
    if not tiene_acceso(u, p) and p != "admin":
        st.error("🚫 No tenés acceso a esta sección."); return
    {
        "home":                  pagina_home,
        "historial":             lambda: pagina_construccion("Historial Jugadores"),
        "estadisticas_medicas":  lambda: pagina_construccion("Estadísticas Médicas"),
        "evaluaciones":          lambda: pagina_construccion("Evaluaciones Físicas"),
        "demandas_fisicas":      lambda: pagina_construccion("Demandas Físicas"),
        "control_partidos":      lambda: pagina_construccion("Control de Partidos"),
        "resumen_individual":    lambda: pagina_construccion("Resumen Individual"),
        "admin":                 pagina_admin,
    }.get(p, lambda: st.error("Página no encontrada"))()

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged:
    pagina_login()
else:
    top_bar(logged=True, usuario=st.session_state.usuario)
    render_sidebar()
    render_pagina()
