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

# ══════════════════════════════════════════════════════════════
# CSS GLOBAL
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Base ── */
.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d2040 50%, #0a1628 100%);
    color: #e8ecf4;
    font-family: 'Inter', sans-serif;
}

/* ── Header bar → azul con tarjetas ── */
header[data-testid="stHeader"] {
    background: linear-gradient(90deg, #0d2040 0%, #1a3a6e 50%, #0d2040 100%) !important;
    border-bottom: 2px solid rgba(26,90,180,0.4) !important;
    height: 56px !important;
}

/* ── Sidebar → azul oscuro ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071428 0%, #0a1e3d 100%) !important;
    border-right: 1px solid rgba(26,90,180,0.3) !important;
}
section[data-testid="stSidebar"] * { color: #e8ecf4 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #1a5ab4, #0d3a7a) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    text-align: left !important; padding-left: 12px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #c8102e, #8b0000) !important;
}

/* ── Botones generales ── */
.stButton > button {
    background: linear-gradient(135deg, #1a5ab4, #0d3a7a) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #c8102e, #8b0000) !important;
    transform: translateY(-1px) !important;
}

/* ── Inputs — letras SIEMPRE visibles ── */
.stTextInput input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(26,90,180,0.5) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-size: 14px !important;
}
.stTextInput input::placeholder { color: #64748b !important; }
.stTextInput input:focus {
    border-color: #1a5ab4 !important;
    background: rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(26,90,180,0.5) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}
/* Opciones del dropdown */
[data-baseweb="select"] * { color: #1a1a2e !important; }
[data-baseweb="popover"] * { color: #1a1a2e !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13,32,64,0.8) !important;
    border-radius: 12px !important; padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #94a3b8 !important;
    border-radius: 8px !important;
    font-weight: 600 !important; font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#1a5ab4,#0d3a7a) !important;
    color: #fff !important;
}

/* ── Login card ── */
.login-card {
    max-width: 460px; margin: 20px auto 0;
    padding: 32px 28px; border-radius: 24px;
    background: rgba(7,20,40,0.97);
    border: 1px solid rgba(26,90,180,0.4);
    box-shadow: 0 24px 64px rgba(0,0,0,0.6);
    text-align: center;
}
.login-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 44px; letter-spacing: 5px; color: #fff; line-height: 1;
}
.login-sub { color: #60a5fa; font-size: 13px; font-weight: 600;
             letter-spacing: 2px; margin: 6px 0 20px; text-transform: uppercase; }

/* ── Header bar cards (bienvenida / info) ── */
.header-bar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 999;
    height: 56px;
    background: linear-gradient(90deg, #0d2040, #1a3a6e, #0d2040);
    border-bottom: 2px solid rgba(26,90,180,0.4);
    display: flex; align-items: center; justify-content: center; gap: 20px;
}
.hcard {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px; padding: 4px 16px;
    font-size: 13px; font-weight: 600; color: #e2e8f0;
    letter-spacing: 1px;
}
.hcard span { color: #60a5fa; font-size: 11px; display: block; font-weight: 400; }

/* ── Sección título ── */
.sec-title {
    color: #fff; font-size: 18px; font-weight: 900;
    border-left: 4px solid #1a5ab4;
    padding-left: 10px; margin: 20px 0 12px;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(10,22,40,.98), rgba(13,32,64,.92));
    border: 1px solid rgba(26,90,180,.25);
    border-radius: 16px; padding: 14px;
}
[data-testid="stMetricLabel"] p { color: #60a5fa !important; font-weight:700 !important; font-size:11px !important; }
[data-testid="stMetricValue"]   { color: #fff !important; font-weight: 900 !important; }

/* ── Formularios en tabs ── */
.stTabs .stTextInput input { color: #ffffff !important; }
.stTabs .stSelectbox > div > div { color: #ffffff !important; }

/* ── Responsive ── */
@media (max-width: 768px) {
    .login-card { margin: 8px; padding: 20px 14px; }
    .login-title { font-size: 32px; }
    .hcard { font-size: 11px; padding: 3px 10px; }
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

USUARIOS = {
    "dr.garcia":    {"nombre":"Dr. García",     "area":"Médica",             "rol":"Médico",        "pwd":_hash("medica123"), "activo":True},
    "dr.lopez":     {"nombre":"Dr. López",       "area":"Médica",             "rol":"Médico",        "pwd":_hash("medica123"), "activo":True},
    "dr.martinez":  {"nombre":"Dr. Martínez",    "area":"Médica",             "rol":"Médico",        "pwd":_hash("medica123"), "activo":True},
    "kine.perez":   {"nombre":"Lic. Pérez",      "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),   "activo":True},
    "kine.gomez":   {"nombre":"Lic. Gómez",      "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),   "activo":True},
    "kine.diaz":    {"nombre":"Lic. Díaz",       "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),   "activo":True},
    "kine.silva":   {"nombre":"Lic. Silva",      "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),   "activo":True},
    "kine.torres":  {"nombre":"Lic. Torres",     "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),   "activo":True},
    "pf.rodriguez": {"nombre":"Prof. Rodríguez", "area":"Rendimiento",        "rol":"PF",            "pwd":_hash("rend123"),   "activo":True},
    "pf.fernandez": {"nombre":"Prof. Fernández", "area":"Rendimiento",        "rol":"PF",            "pwd":_hash("rend123"),   "activo":True},
    "pf.sanchez":   {"nombre":"Prof. Sánchez",   "area":"Rendimiento",        "rol":"PF",            "pwd":_hash("rend123"),   "activo":True},
    "nutri.ruiz":   {"nombre":"Lic. Ruiz",       "area":"Rendimiento",        "rol":"Nutricionista", "pwd":_hash("rend123"),   "activo":True},
    "nutri.mora":   {"nombre":"Lic. Mora",       "area":"Rendimiento",        "rol":"Nutricionista", "pwd":_hash("rend123"),   "activo":True},
    "nutri.vega":   {"nombre":"Lic. Vega",       "area":"Rendimiento",        "rol":"Nutricionista", "pwd":_hash("rend123"),   "activo":True},
    "ct.ramirez":   {"nombre":"Prof. Ramírez",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","pwd":_hash("rend123"),   "activo":True},
    "ct.jimenez":   {"nombre":"Prof. Jiménez",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","pwd":_hash("rend123"),   "activo":True},
    "ct.herrera":   {"nombre":"Prof. Herrera",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","pwd":_hash("rend123"),   "activo":True},
    "st.castro":    {"nombre":"Lic. Castro",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "pwd":_hash("sec123"),    "activo":True},
    "st.vargas":    {"nombre":"Lic. Vargas",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "pwd":_hash("sec123"),    "activo":True},
    "st.medina":    {"nombre":"Lic. Medina",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "pwd":_hash("sec123"),    "activo":True},
    "st.guerrero":  {"nombre":"Lic. Guerrero",   "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "pwd":_hash("sec123"),    "activo":True},
    "admin":        {"nombre":"Administrador",   "area":"Administración",     "rol":"Admin",         "pwd":_hash("admin123"),  "activo":True},
    "scout.blanco": {"nombre":"Lic. Blanco",     "area":"Scout",              "rol":"Scout",         "pwd":_hash("scout123"),  "activo":True},
    "scout.acosta": {"nombre":"Lic. Acosta",     "area":"Scout",              "rol":"Scout",         "pwd":_hash("scout123"),  "activo":True},
    "scout.rios":   {"nombre":"Lic. Ríos",       "area":"Scout",              "rol":"Scout",         "pwd":_hash("scout123"),  "activo":True},
}

def verificar_login(u, p):
    usr = USUARIOS.get(u.lower().strip())
    if usr and usr["activo"] and usr["pwd"] == _hash(p): return usr
    # Pendientes en session_state
    for k, d in st.session_state.get("pendientes", {}).items():
        if k == u.lower().strip() and d.get("aprobado") and d["pwd"] == _hash(p): return d
    return None

def tiene_acceso(u, s): return s in AREAS.get(u.get("area",""), {}).get("secciones", [])
def usuarios_por_area(a): return [u for u,d in USUARIOS.items() if d["area"] == a]

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
    gid = m.group(1) if m else "0"
    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"

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
# SESSION STATE
# ══════════════════════════════════════════════════════════════
for k, v in [("logged",False),("usuario",None),("pagina","home"),("pendientes",{})]:
    if k not in st.session_state: st.session_state[k] = v

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
        return f'<img src="data:image/png;base64,{b64}" style="width:{size}px;height:{size}px;object-fit:contain;filter:drop-shadow(0 0 16px rgba(26,90,180,.5));">'
    return '<div style="font-size:80px;line-height:1;">⚽</div>'

def header_bar(logged=False, usuario=None):
    now = datetime.now()
    fecha = now.strftime("%d/%m/%Y")
    hora  = now.strftime("%H:%M")
    if logged and usuario:
        titulo = f"CLUB A. UNIÓN &nbsp;·&nbsp; {AREAS[usuario['area']]['icon']} {usuario['area']}"
    else:
        titulo = "BIENVENIDO · CLUB A. UNIÓN"
    st.markdown(f"""
    <div class="header-bar">
        <div class="hcard"><span>Fecha</span>{fecha}</div>
        <div class="hcard" style="font-size:15px;font-weight:800;letter-spacing:3px;color:#fff;
             font-family:'Bebas Neue',sans-serif;background:transparent;border:none;">
            {titulo}
        </div>
        <div class="hcard"><span>Hora</span>{hora}</div>
        <div class="hcard"><span>Sede</span>Santa Fe, ARG</div>
    </div>
    <div style="height:56px;"></div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════
def pagina_login():
    header_bar(logged=False)
    t1, t2, t3 = st.tabs(["🔐  Iniciar sesión", "📝  Registrarme", "🔑  Recuperar contraseña"])

    with t1:
        st.markdown(f"""
        <div class="login-card">
            {escudo_tag(100)}
            <div class="login-title">CLUB A. UNIÓN</div>
            <div class="login-sub">Sistema de Rendimiento Físico</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _, col, _ = st.columns([1, 1.4, 1])
        with col:
            area_sel = st.selectbox("Área", ["— Seleccioná tu área —"] + list(AREAS.keys()), key="l_area")
            ua = usuarios_por_area(area_sel) if area_sel != "— Seleccioná tu área —" else []
            us = st.selectbox("Usuario", ["— Seleccioná —"] + ua, key="l_user",
                              disabled=(area_sel == "— Seleccioná tu área —"))
            pw = st.text_input("Contraseña", type="password", key="l_pwd",
                               placeholder="Ingresá tu contraseña")
            if st.button("Ingresar →", use_container_width=True, key="btn_login"):
                if us == "— Seleccioná —":
                    st.error("Seleccioná un usuario.")
                elif not pw:
                    st.warning("Ingresá tu contraseña.")
                else:
                    u = verificar_login(us, pw)
                    if u:
                        st.session_state.logged = True
                        st.session_state.usuario = {**u, "username": us}
                        st.session_state.pagina = "home"
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta o usuario inactivo.")

    with t2:
        st.markdown("### 📝 Solicitud de acceso")
        st.info("Tu solicitud quedará pendiente hasta que el administrador la apruebe.")
        c1, c2 = st.columns(2)
        with c1:
            rn = st.text_input("Nombre completo", key="rn", placeholder="Ej: Juan Pérez")
            ra = st.selectbox("Área", list(AREAS.keys()), key="ra")
            ru = st.text_input("Usuario (sin espacios)", key="ru", placeholder="Ej: juan.perez")
        with c2:
            rr  = st.text_input("Rol / Cargo", key="rr", placeholder="Ej: Kinesiólogo")
            re_ = st.text_input("Email", key="re", placeholder="tu@email.com")
            rp  = st.text_input("Contraseña", type="password", key="rp", placeholder="Mínimo 6 caracteres")
            rp2 = st.text_input("Repetir contraseña", type="password", key="rp2", placeholder="Repetí la contraseña")
        if st.button("Enviar solicitud", use_container_width=True, key="btn_reg"):
            if not all([rn, ra, ru, rr, re_, rp]):
                st.error("Completá todos los campos.")
            elif rp != rp2:
                st.error("Las contraseñas no coinciden.")
            elif " " in ru:
                st.error("El usuario no puede tener espacios.")
            elif ru.lower() in USUARIOS:
                st.error("Ese usuario ya existe. Elegí otro.")
            else:
                st.session_state.pendientes[ru.lower()] = {
                    "nombre": rn, "area": ra, "rol": rr,
                    "email": re_, "pwd": _hash(rp),
                    "activo": False, "aprobado": False
                }
                st.success(f"✅ Solicitud enviada para **{rn}**. El administrador (`admin`) debe aprobarla desde el Panel Admin.")
                st.info("📧 El sistema de email automático estará disponible próximamente.")

    with t3:
        st.markdown("### 🔑 Recuperación de contraseña")
        st.info("Ingresá tu email y el administrador te enviará una contraseña temporal.")
        rm = st.text_input("Email institucional", key="rm", placeholder="tu@email.com")
        if st.button("Solicitar recuperación", use_container_width=True, key="btn_rec"):
            if rm and "@" in rm:
                st.success("✅ Solicitud registrada. El administrador te contactará a la brevedad.")
                st.info("ℹ️ Mientras tanto, podés contactar al administrador directamente.")
            else:
                st.error("Ingresá un email válido.")

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def render_sidebar():
    u = st.session_state.usuario
    with st.sidebar:
        b64 = img_b64(ASSETS / "escudo_union.png")
        esc = f'<img src="data:image/png;base64,{b64}" style="width:56px;height:56px;object-fit:contain;filter:drop-shadow(0 0 8px rgba(26,90,180,.6));">' if b64 else "⚽"
        st.markdown(f"""
        <div style="text-align:center;padding:14px 0 12px;
             border-bottom:1px solid rgba(26,90,180,.3);margin-bottom:14px;">
            {esc}
            <div style="font-family:'Bebas Neue',sans-serif;font-size:16px;
                 letter-spacing:3px;margin-top:8px;color:#fff;">CAU · UNIÓN</div>
            <div style="font-size:12px;color:#60a5fa;margin-top:2px;">
                {AREAS[u["area"]]["icon"]} {u["nombre"]}
            </div>
            <div style="font-size:10px;color:#475569;margin-top:2px;">
                {u["rol"]} · {u["area"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

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
            pendientes_n = sum(1 for d in st.session_state.pendientes.values() if not d.get("aprobado"))
            label_admin = f"🔧  Panel Admin {'🔴' if pendientes_n else ''}"
            if st.button(label_admin, key="nav_admin", use_container_width=True):
                st.session_state.pagina = "admin"; st.rerun()

        st.markdown("---")
        if st.button("🚪  Cerrar sesión", use_container_width=True, key="btn_out"):
            st.session_state.logged = False
            st.session_state.usuario = None
            st.session_state.pagina = "home"
            st.rerun()

# ══════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════
def pagina_home():
    u = st.session_state.usuario
    st.markdown(f"""
    <div style="text-align:center;padding:28px 20px 16px;">
        {escudo_tag(130)}
        <div style="font-family:'Bebas Neue',sans-serif;font-size:58px;
             letter-spacing:6px;color:#fff;line-height:1;margin-top:14px;">CLUB A. UNIÓN</div>
        <div style="color:#60a5fa;font-size:14px;font-weight:700;letter-spacing:4px;
             text-transform:uppercase;margin-top:6px;">Sistema de Rendimiento Físico</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    cf, ct = st.columns([1, 2], gap="large")
    with cf:
        foto = img_b64(ASSETS / "foto_home.jpg")
        if foto:
            st.markdown(f'<img src="data:image/jpeg;base64,{foto}" style="width:100%;border-radius:16px;border:2px solid rgba(26,90,180,.4);">', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="aspect-ratio:4/3;background:rgba(26,90,180,.08);
                 border:2px dashed rgba(26,90,180,.3);border-radius:16px;
                 display:flex;align-items:center;justify-content:center;
                 color:#475569;font-size:13px;text-align:center;padding:20px;">
                📷 Subí la foto del club como<br><code>assets/foto_home.jpg</code>
            </div>""", unsafe_allow_html=True)
    with ct:
        st.markdown("""
        <div style="background:rgba(10,22,40,.9);border:1px solid rgba(26,90,180,.2);
             border-radius:16px;padding:28px;">
            <div style="font-size:10px;color:#60a5fa;font-weight:700;letter-spacing:3px;
                 text-transform:uppercase;margin-bottom:8px;">Acerca del sistema</div>
            <div style="font-size:22px;font-weight:800;color:#fff;
                 margin-bottom:12px;line-height:1.2;">
                Plataforma integral de monitorización del rendimiento
            </div>
            <div style="font-size:14px;color:#94a3b8;line-height:1.7;">
                Esta plataforma centraliza toda la información física, médica y deportiva
                del plantel profesional de Club A. Unión, facilitando la toma de decisiones
                del cuerpo técnico, el área médica y la secretaría técnica.
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sec-title">Resumen del plantel</div>', unsafe_allow_html=True)
    try:
        dfs = cargar_datos()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("👥 Jugadores",       dfs["data_jug"].shape[0] if not dfs["data_jug"].empty else "—")
        c2.metric("🏥 Registros médicos",dfs["lesiones"].shape[0] if not dfs["lesiones"].empty else "—")
        c3.metric("📡 Sesiones GPS",    dfs["gps"].shape[0] if not dfs["gps"].empty else "—")
        c4.metric("📅 Hoy",             date.today().strftime("%d/%m/%Y"))
    except Exception:
        c1,c2,c3,c4 = st.columns(4)
        for c,l in zip([c1,c2,c3,c4],["👥 Jugadores","🏥 Médicos","📡 GPS","📅 Hoy"]):
            c.metric(l, "—")

    st.markdown(f"""
    <div style="background:rgba(26,90,180,.08);border:1px solid rgba(26,90,180,.2);
         border-radius:14px;padding:20px 24px;margin-top:16px;">
        <div style="font-size:11px;color:#60a5fa;font-weight:700;letter-spacing:2px;
             text-transform:uppercase;">Bienvenido/a al sistema</div>
        <div style="font-size:20px;font-weight:800;color:#fff;margin:4px 0 6px;">
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
    pendientes = {k:d for k,d in st.session_state.pendientes.items() if not d.get("aprobado")}

    if pendientes:
        st.warning(f"⚠️ {len(pendientes)} solicitud(es) pendiente(s) de aprobación")
        for username, datos in pendientes.items():
            with st.expander(f"👤 {datos['nombre']} — {datos['area']} · {datos['rol']} — {datos.get('email','')}"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Aprobar a {datos['nombre']}", key=f"apr_{username}"):
                        st.session_state.pendientes[username]["aprobado"] = True
                        st.session_state.pendientes[username]["activo"] = True
                        st.success(f"✅ {datos['nombre']} aprobado. Ya puede ingresar.")
                        st.rerun()
                with col2:
                    if st.button(f"❌ Rechazar", key=f"rec_{username}"):
                        del st.session_state.pendientes[username]
                        st.warning("Usuario rechazado."); st.rerun()
    else:
        st.success("✅ No hay solicitudes pendientes.")

    st.markdown("---")
    st.markdown("#### 👥 Usuarios del sistema")
    rows = [{"Usuario":k,"Nombre":v["nombre"],"Área":v["area"],"Rol":v["rol"]} for k,v in USUARIOS.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

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
        "home":                 pagina_home,
        "historial":            lambda: pagina_construccion("Historial Jugadores"),
        "estadisticas_medicas": lambda: pagina_construccion("Estadísticas Médicas"),
        "evaluaciones":         lambda: pagina_construccion("Evaluaciones Físicas"),
        "demandas_fisicas":     lambda: pagina_construccion("Demandas Físicas"),
        "control_partidos":     lambda: pagina_construccion("Control de Partidos"),
        "resumen_individual":   lambda: pagina_construccion("Resumen Individual"),
        "admin":                pagina_admin,
    }.get(p, lambda: st.error("Página no encontrada"))()

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged:
    pagina_login()
else:
    header_bar(logged=True, usuario=st.session_state.usuario)
    render_sidebar()
    render_pagina()
