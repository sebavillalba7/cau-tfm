import streamlit as st
from pathlib import Path
import base64, hashlib, re, time
import pandas as pd
from datetime import date, datetime

st.set_page_config(
    page_title="CAU · Rendimiento Físico",
    page_icon="⚽", layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp {
    background: linear-gradient(135deg, #0c1e3e 0%, #112347 50%, #0c1e3e 100%);
    color: #e8ecf4; font-family: 'Inter', sans-serif;
}
header[data-testid="stHeader"] { display: none !important; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #091528 0%, #0d1e38 100%) !important;
    border-right: 1px solid rgba(200,16,46,0.3) !important;
}
section[data-testid="stSidebar"] * { color: #e8ecf4 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: #e8ecf4 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important; font-weight: 500 !important;
    text-align: left !important; padding-left: 14px !important; transition: all .2s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg,#c8102e,#8b0000) !important;
    border-color: transparent !important; color: #fff !important;
}
.stButton > button {
    background: linear-gradient(135deg,#c8102e,#8b0000) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important; transition: all .2s !important;
}
.stButton > button:hover { opacity:.85 !important; transform:translateY(-1px) !important; }

input, textarea { background: #112040 !important; border: 1px solid rgba(200,16,46,0.4) !important;
    border-radius: 10px !important; color: #ffffff !important; caret-color:#fff !important; }
input::placeholder { color:#475569 !important; }
input:focus { border-color:#c8102e !important; color:#ffffff !important; }
.stTextInput label, .stSelectbox label { color:#94a3b8 !important; font-size:12px !important; font-weight:600 !important; }
.stSelectbox > div > div { background:#112040 !important; border:1px solid rgba(200,16,46,0.4) !important;
    border-radius:10px !important; color:#ffffff !important; }
[data-baseweb="select"] > div { background:#112040 !important; }
[data-baseweb="select"] span { color:#ffffff !important; }

.stTabs [data-baseweb="tab-list"] { background:rgba(15,30,60,0.8) !important;
    border-radius:12px !important; padding:4px !important; gap:4px !important; }
.stTabs [data-baseweb="tab"] { color:#64748b !important; border-radius:8px !important;
    font-weight:600 !important; font-size:13px !important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#c8102e,#8b0000) !important; color:#fff !important; }

.login-card { max-width:460px; margin:20px auto 0; padding:32px 28px; border-radius:24px;
    background:rgba(8,18,38,0.98); border:1px solid rgba(200,16,46,0.35);
    box-shadow:0 24px 64px rgba(0,0,0,0.7); text-align:center; }
.login-title { font-family:'Bebas Neue',sans-serif; font-size:44px; letter-spacing:5px; color:#fff; line-height:1; }
.login-sub { color:#c8102e; font-size:11px; font-weight:700; letter-spacing:3px; margin:6px 0 0; text-transform:uppercase; }

.top-bar { position:fixed; top:0; left:0; right:0; z-index:9999; height:52px;
    background:linear-gradient(90deg,#070f20 0%,#0d1e3c 40%,#1a0a14 60%,#070f20 100%);
    border-bottom:2px solid rgba(200,16,46,0.5);
    display:flex; align-items:center; justify-content:space-between; padding:0 24px; gap:12px; }
.top-bar-center { font-family:'Bebas Neue',sans-serif; font-size:22px; letter-spacing:5px;
    color:#fff; flex:1; text-align:center; }
.top-card { background:rgba(200,16,46,0.12); border:1px solid rgba(200,16,46,0.25);
    border-radius:8px; padding:4px 14px; font-size:12px; font-weight:700; color:#fff; white-space:nowrap; }
.top-card small { display:block; font-size:9px; color:#94a3b8; font-weight:400; letter-spacing:1px; text-transform:uppercase; }
.spacer-top { height:52px; }

.sec-title { color:#fff; font-size:18px; font-weight:900; border-left:4px solid #c8102e;
    padding-left:10px; margin:20px 0 12px; }
.subsec { color:#fff; font-size:15px; font-weight:700; border-left:3px solid rgba(200,16,46,0.5);
    padding-left:8px; margin:16px 0 8px; }

[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(12,28,56,.98),rgba(17,35,70,.9));
    border:1px solid rgba(200,16,46,.2); border-radius:16px; padding:14px; }
[data-testid="stMetricLabel"] p { color:#f87171 !important; font-weight:700 !important; font-size:11px !important; }
[data-testid="stMetricValue"]   { color:#fff !important; font-weight:900 !important; }

.user-table { width:100%; border-collapse:collapse; font-size:13px; }
.user-table th { background:rgba(200,16,46,0.15); color:#f87171; font-weight:700; font-size:10px;
    letter-spacing:2px; text-transform:uppercase; padding:10px 14px; text-align:left;
    border-bottom:1px solid rgba(200,16,46,0.3); }
.user-table td { padding:10px 14px; color:#e2e8f0; border-bottom:1px solid rgba(255,255,255,0.04); }
.user-table tr:hover td { background:rgba(200,16,46,0.05); }
.badge-activo   { background:rgba(34,197,94,0.15); color:#4ade80; border:1px solid rgba(34,197,94,0.3); border-radius:6px; padding:2px 10px; font-size:11px; font-weight:700; }
.badge-inactivo { background:rgba(239,68,68,0.15); color:#f87171; border:1px solid rgba(239,68,68,0.3); border-radius:6px; padding:2px 10px; font-size:11px; font-weight:700; }
.badge-area     { background:rgba(26,90,180,0.15); color:#93c5fd; border:1px solid rgba(26,90,180,0.3); border-radius:6px; padding:2px 10px; font-size:11px; }

.player-card { background:rgba(8,18,38,0.9); border:1px solid rgba(200,16,46,0.2);
    border-radius:16px; padding:20px; margin-bottom:12px; }
.chip { display:inline-block; background:rgba(200,16,46,0.12); border:1px solid rgba(200,16,46,0.25);
    color:#f87171; border-radius:6px; padding:3px 10px; font-size:11px; font-weight:700; margin:3px 3px 3px 0; }
.chip-blue { background:rgba(26,90,180,0.12); border-color:rgba(26,90,180,0.3); color:#93c5fd; }
.chip-green { background:rgba(34,197,94,0.1); border-color:rgba(34,197,94,0.3); color:#4ade80; }

.card-kpi { background:rgba(8,18,38,0.9); border:1px solid rgba(255,255,255,0.07);
    border-radius:14px; padding:16px 20px; }

@media (max-width:768px) {
    .login-card { margin:8px; padding:20px 14px; }
    .login-title { font-size:32px; }
    .top-bar-center { font-size:16px; letter-spacing:3px; }
    .top-card { display:none; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HORA LOCAL via JS (inyectada en el cliente)
# ══════════════════════════════════════════════════════════════
def inject_local_time():
    """Inyecta JS para obtener hora local del navegador."""
    st.markdown("""
    <script>
    function updateTime() {
        var now = new Date();
        var h = String(now.getHours()).padStart(2,'0');
        var m = String(now.getMinutes()).padStart(2,'0');
        var els = document.querySelectorAll('.local-time');
        els.forEach(el => el.textContent = h + ':' + m);
        // Fecha
        var d = String(now.getDate()).padStart(2,'0');
        var mo = String(now.getMonth()+1).padStart(2,'0');
        var y = now.getFullYear();
        var fels = document.querySelectorAll('.local-date');
        fels.forEach(el => el.textContent = d + '/' + mo + '/' + y);
    }
    updateTime();
    setInterval(updateTime, 30000);
    </script>
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

for k,v in [("logged",False),("usuario",None),("pagina","home"),
             ("usuarios_extra",{}),("usuarios_desactivados",set())]:
    if k not in st.session_state: st.session_state[k]=v

def todos_los_usuarios():
    u={}
    for k,d in USUARIOS_BASE.items():
        u[k]={**d,"activo":k not in st.session_state.usuarios_desactivados and d["activo"],"tipo":"base"}
    for k,d in st.session_state.usuarios_extra.items():
        if d.get("aprobado"):
            u[k]={**d,"activo":k not in st.session_state.usuarios_desactivados and d.get("activo",True),"tipo":"extra"}
    return u

def verificar_login(username,password):
    u=todos_los_usuarios().get(username.lower().strip())
    if u and u["activo"] and u["pwd"]==_hash(password): return u
    return None

def tiene_acceso(u,s): return s in AREAS.get(u.get("area",""),{}).get("secciones",[])
def usuarios_por_area(area): return [k for k,d in todos_los_usuarios().items() if d["area"]==area and d["activo"]]

# ══════════════════════════════════════════════════════════════
# GOOGLE SHEETS — URLS
# ══════════════════════════════════════════════════════════════
SHEETS = {
    "historial":  "https://docs.google.com/spreadsheets/d/1Ppy3Mkz3ojqlcGAcxhNlqnGy5o2GmBHmdL9IZdRh9b0/edit?gid=0",
    "lesiones":   "https://docs.google.com/spreadsheets/d/1irSkXB8V_D_jZurEGUA9JMkLpE3e0_qad16_orjHDi8/edit?gid=0",
    "cmj":        "https://docs.google.com/spreadsheets/d/1VQLX1R1M0IW8j_TPXbVE8y5qaOA8-2qpj8cL-eGA1VY/edit?gid=1188054203",
    "cmj1pp":     "https://docs.google.com/spreadsheets/d/16ugXQ5hEnMa9bh_Ma1IDDaPq6gNq4QVPTRwQyVnz3oc/edit?gid=305963248",
    "nordico":    "https://docs.google.com/spreadsheets/d/1fhFajl9ckPYikfIKdBHTORcqQj0802JoNQ8-B3wEJWU/edit?gid=1994839095",
    "vbt":        "https://docs.google.com/spreadsheets/d/1NjVz_ivHKRrtai18ogjMQuQA6EYh3Q-WLDiNOErYO-Q/edit?gid=0",
    "gps":        "https://docs.google.com/spreadsheets/d/1W3hUX8zTPYXzDUSmdW7Nj2fXbEKlp1E2Us7kwNBhR6c/edit?gid=0",
    "partidos":   "https://docs.google.com/spreadsheets/d/17EiRiX-Tjlor0SfZvz-Wzfohz07calbA_26DKd4XL5g/edit?gid=2140450866",
}
def gsheet_csv(url):
    sid=re.search(r"/d/([^/]+)",url).group(1)
    m=re.search(r"gid=(\d+)",url)
    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={m.group(1) if m else '0'}"

@st.cache_data(ttl=300,show_spinner=False)
def cargar_sheet(key):
    try:
        df=pd.read_csv(gsheet_csv(SHEETS[key]),low_memory=False)
        df.columns=df.columns.astype(str).str.strip()
        df=df.replace({"None":pd.NA,"nan":pd.NA,"":pd.NA,"#N/A":pd.NA,"N/A":pd.NA})
        return df
    except Exception as e:
        return pd.DataFrame()

def cargar_todos():
    return {k: cargar_sheet(k) for k in SHEETS}

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
ASSETS=Path("assets")
def img_b64(path):
    p=Path(path); return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

def escudo_tag(size=110):
    b64=img_b64(ASSETS/"escudo_union.png")
    return f'<img src="data:image/png;base64,{b64}" style="width:{size}px;height:{size}px;object-fit:contain;filter:drop-shadow(0 0 16px rgba(200,16,46,.4));">' if b64 else '<div style="font-size:80px;">⚽</div>'

def top_bar(logged=False,usuario=None):
    now=datetime.now()
    centro="CLUB A. UNIÓN · DATA INTELLIGENCE" if not logged else f"CLUB A. UNIÓN &nbsp;·&nbsp; {AREAS[usuario['area']]['icon']} {usuario['area'].upper()}"
    st.markdown(f"""
    <div class="top-bar">
        <div class="top-card"><small>Fecha</small><span class="local-date">{now.strftime('%d/%m/%Y')}</span></div>
        <div class="top-bar-center">{centro}</div>
        <div class="top-card"><small>Hora</small><span class="local-time">{now.strftime('%H:%M')}</span></div>
        <div class="top-card"><small>Sede</small>Santa Fe, ARG</div>
    </div>
    <div class="spacer-top"></div>
    <script>
    function updateLocalTime(){{
        var now=new Date();
        var h=String(now.getHours()).padStart(2,'0');
        var m=String(now.getMinutes()).padStart(2,'0');
        document.querySelectorAll('.local-time').forEach(el=>el.textContent=h+':'+m);
        var d=String(now.getDate()).padStart(2,'0');
        var mo=String(now.getMonth()+1).padStart(2,'0');
        var y=now.getFullYear();
        document.querySelectorAll('.local-date').forEach(el=>el.textContent=d+'/'+mo+'/'+y);
    }}
    updateLocalTime(); setInterval(updateLocalTime,10000);
    </script>
    """,unsafe_allow_html=True)

def exportar_pdf_btn(nombre_seccion):
    """Botón de exportar a PDF (requisito del TFM)."""
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;margin-bottom:12px;">
        <button onclick="window.print()" style="background:linear-gradient(135deg,#c8102e,#8b0000);
            color:#fff;border:none;border-radius:8px;padding:8px 18px;font-weight:700;
            font-size:13px;cursor:pointer;">📄 Exportar PDF</button>
    </div>""",unsafe_allow_html=True)

def no_data_msg(nombre):
    st.markdown(f"""
    <div style="background:rgba(200,16,46,0.07);border:1px dashed rgba(200,16,46,0.3);
         border-radius:12px;padding:24px;text-align:center;color:#64748b;">
        ⚠️ No se pudo cargar <b style="color:#f87171;">{nombre}</b>.<br>
        <small>Verificá que la hoja de Google Sheets sea pública (compartir → cualquiera con el vínculo).</small>
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════
def pagina_login():
    top_bar(logged=False)
    t1,t2,t3=st.tabs(["🔐  Iniciar sesión","📝  Registrarme","🔑  Recuperar contraseña"])
    with t1:
        st.markdown(f'<div class="login-card">{escudo_tag(100)}<div class="login-title">CLUB A. UNIÓN</div><div class="login-sub">Data Intelligence · Rendimiento Físico</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        _,col,_=st.columns([1,1.4,1])
        with col:
            area_sel=st.selectbox("Área",["— Seleccioná tu área —"]+list(AREAS.keys()),key="l_area")
            ua=usuarios_por_area(area_sel) if area_sel!="— Seleccioná tu área —" else []
            us=st.selectbox("Usuario",["— Seleccioná —"]+ua,key="l_user",disabled=(area_sel=="— Seleccioná tu área —"))
            pw=st.text_input("Contraseña",type="password",key="l_pwd",placeholder="Ingresá tu contraseña")
            if st.button("Ingresar →",use_container_width=True,key="btn_login"):
                if us=="— Seleccioná —": st.error("Seleccioná un usuario.")
                elif not pw: st.warning("Ingresá tu contraseña.")
                else:
                    u=verificar_login(us,pw)
                    if u:
                        st.session_state.logged=True; st.session_state.usuario={**u,"username":us}
                        st.session_state.pagina="home"; st.rerun()
                    else: st.error("Contraseña incorrecta o usuario inactivo.")
    with t2:
        st.markdown("### 📝 Solicitud de acceso")
        st.info("Tu solicitud quedará pendiente hasta que el administrador la apruebe.")
        c1,c2=st.columns(2)
        with c1:
            rn=st.text_input("Nombre completo",key="rn",placeholder="Ej: Juan Pérez")
            ra=st.selectbox("Área",list(AREAS.keys()),key="ra")
            ru=st.text_input("Usuario (sin espacios)",key="ru",placeholder="Ej: juan.perez")
        with c2:
            rr=st.text_input("Rol / Cargo",key="rr",placeholder="Ej: Kinesiólogo")
            re_=st.text_input("Email",key="re_",placeholder="tu@email.com")
            rp=st.text_input("Contraseña",type="password",key="rp",placeholder="Mínimo 6 caracteres")
            rp2=st.text_input("Repetir contraseña",type="password",key="rp2",placeholder="Repetí la contraseña")
        if st.button("Enviar solicitud",use_container_width=True,key="btn_reg"):
            if not all([rn,ra,ru,rr,re_,rp]): st.error("Completá todos los campos.")
            elif rp!=rp2: st.error("Las contraseñas no coinciden.")
            elif " " in ru: st.error("El usuario no puede tener espacios.")
            elif ru.lower() in USUARIOS_BASE or ru.lower() in st.session_state.usuarios_extra: st.error("Ese usuario ya existe.")
            else:
                st.session_state.usuarios_extra[ru.lower()]={"nombre":rn,"area":ra,"rol":rr,"email":re_,"pwd":_hash(rp),"activo":False,"aprobado":False}
                st.success(f"✅ Solicitud enviada para **{rn}**. El admin debe aprobarla desde el Panel Admin.")
    with t3:
        st.markdown("### 🔑 Recuperación de contraseña")
        st.info("⚠️ El envío automático de email requiere configuración SMTP. Por ahora, contactá al administrador directamente en **admin@cauunion.com** con tu usuario y se te enviará una contraseña temporal.")
        rm=st.text_input("Tu email registrado",key="rm",placeholder="tu@email.com")
        ru2=st.text_input("Tu nombre de usuario",key="ru2",placeholder="Ej: juan.perez")
        if st.button("Solicitar recuperación",use_container_width=True,key="btn_rec"):
            if rm and "@" in rm and ru2:
                st.success("✅ Solicitud registrada. El administrador te enviará una contraseña temporal a la brevedad.")
            else: st.error("Completá email y usuario.")

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def render_sidebar():
    u=st.session_state.usuario
    with st.sidebar:
        b64=img_b64(ASSETS/"escudo_union.png")
        esc=f'<img src="data:image/png;base64,{b64}" style="width:56px;height:56px;object-fit:contain;filter:drop-shadow(0 0 10px rgba(200,16,46,.5));">' if b64 else "⚽"
        st.markdown(f"""
        <div style="text-align:center;padding:14px 0 12px;border-bottom:1px solid rgba(200,16,46,.25);margin-bottom:14px;">
            {esc}
            <div style="font-family:'Bebas Neue',sans-serif;font-size:16px;letter-spacing:3px;margin-top:8px;color:#fff;">CAU · UNIÓN</div>
            <div style="font-size:12px;color:#f87171;margin-top:3px;">{AREAS[u["area"]]["icon"]} {u["nombre"]}</div>
            <div style="font-size:10px;color:#475569;margin-top:2px;">{u["rol"]} · {u["area"]}</div>
        </div>""",unsafe_allow_html=True)
        st.markdown('<p style="font-size:10px;letter-spacing:3px;color:#475569;text-transform:uppercase;margin:0 0 8px;">MENÚ</p>',unsafe_allow_html=True)
        nav=[("home","🏠","Inicio"),("historial","👤","Historial Jugadores"),("estadisticas_medicas","🏥","Estadísticas Médicas"),("evaluaciones","⚡","Evaluaciones Físicas"),("demandas_fisicas","📡","Demandas Físicas"),("control_partidos","⚽","Control de Partidos"),("resumen_individual","📄","Resumen Individual")]
        for key,icon,label in nav:
            if tiene_acceso(u,key):
                if st.button(f"{icon}  {label}",key=f"nav_{key}",use_container_width=True):
                    st.session_state.pagina=key; st.rerun()
        if tiene_acceso(u,"admin"):
            st.markdown("---")
            pend_n=sum(1 for d in st.session_state.usuarios_extra.values() if not d.get("aprobado"))
            if st.button(f"🔧  Panel Admin {'🔴' if pend_n else ''}",key="nav_admin",use_container_width=True):
                st.session_state.pagina="admin"; st.rerun()
        st.markdown("---")
        if st.button("🚪  Cerrar sesión",use_container_width=True,key="btn_out"):
            st.session_state.logged=False; st.session_state.usuario=None; st.session_state.pagina="home"; st.rerun()

# ══════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════
def pagina_home():
    u=st.session_state.usuario
    exportar_pdf_btn("Home")
    st.markdown(f"""
    <div style="text-align:center;padding:24px 20px 12px;">
        {escudo_tag(120)}
        <div style="font-family:'Bebas Neue',sans-serif;font-size:56px;letter-spacing:6px;color:#fff;line-height:1;margin-top:12px;">CLUB A. UNIÓN</div>
        <div style="color:#c8102e;font-size:12px;font-weight:700;letter-spacing:4px;text-transform:uppercase;margin-top:6px;">Data Intelligence · Rendimiento Físico</div>
    </div>""",unsafe_allow_html=True)
    st.markdown("---")
    cf,ct=st.columns([1,2],gap="large")
    with cf:
        foto=img_b64(ASSETS/"foto_home.jpg")
        if foto: st.markdown(f'<img src="data:image/jpeg;base64,{foto}" style="width:100%;border-radius:16px;border:2px solid rgba(200,16,46,.3);">',unsafe_allow_html=True)
        else: st.markdown('<div style="aspect-ratio:4/3;background:rgba(200,16,46,.06);border:2px dashed rgba(200,16,46,.25);border-radius:16px;display:flex;align-items:center;justify-content:center;color:#475569;font-size:13px;text-align:center;padding:20px;">📷 Subí la foto como<br><code>assets/foto_home.jpg</code></div>',unsafe_allow_html=True)
    with ct:
        st.markdown("""
        <div style="background:rgba(8,18,38,0.95);border:1px solid rgba(200,16,46,.2);border-radius:16px;padding:28px 32px;height:100%;box-sizing:border-box;">
            <div style="font-size:10px;color:#c8102e;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">Plataforma Tecnológica</div>
            <div style="font-size:26px;font-weight:900;color:#fff;margin-bottom:16px;line-height:1.2;">Data Intelligence aplicada al rendimiento deportivo</div>
            <div style="font-size:14px;color:#94a3b8;line-height:1.8;">
                Una plataforma centralizada que transforma datos físicos, médicos y tácticos en inteligencia accionable para el cuerpo técnico, el área médica y la secretaría técnica del Club A. Unión.<br><br>
                Desde el GPS en el campo hasta el modelo de riesgo de lesión con Machine Learning — toda la información del plantel en un solo lugar, en tiempo real, para quienes toman decisiones.
            </div>
            <div style="display:flex;gap:8px;margin-top:18px;flex-wrap:wrap;">
                <span class="chip">📡 GPS</span><span class="chip">🤖 Machine Learning</span>
                <span class="chip">🏥 Gestión médica</span><span class="chip">📊 Reportes PDF</span>
                <span class="chip">⚡ CMJ · Nórdico · VBT</span><span class="chip">⚽ API Fútbol</span>
            </div>
        </div>""",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sec-title">Resumen del plantel</div>',unsafe_allow_html=True)
    try:
        gps=cargar_sheet("gps"); les=cargar_sheet("lesiones"); jug=cargar_sheet("historial")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("👥 Jugadores",jug.shape[0] if not jug.empty else "—")
        c2.metric("🏥 Registros médicos",les.shape[0] if not les.empty else "—")
        c3.metric("📡 Sesiones GPS",gps.shape[0] if not gps.empty else "—")
        c4.metric("📅 Hoy",date.today().strftime("%d/%m/%Y"))
    except Exception:
        c1,c2,c3,c4=st.columns(4)
        for c,l in zip([c1,c2,c3,c4],["👥 Jugadores","🏥 Médicos","📡 GPS","📅 Hoy"]): c.metric(l,"—")
    st.markdown(f"""
    <div style="background:rgba(200,16,46,.07);border:1px solid rgba(200,16,46,.2);border-radius:14px;padding:18px 24px;margin-top:16px;">
        <div style="font-size:10px;color:#c8102e;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Sesión activa</div>
        <div style="font-size:20px;font-weight:800;color:#fff;margin:4px 0 4px;">{u["nombre"]} · {u["rol"]}</div>
        <div style="font-size:13px;color:#94a3b8;">Área: <b style="color:#e2e8f0;">{u["area"]}</b> | Acceso a <b style="color:#e2e8f0;">{len(AREAS[u["area"]]["secciones"])}</b> secciones</div>
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HISTORIAL JUGADORES
# ══════════════════════════════════════════════════════════════
def pagina_historial():
    st.markdown('<div class="sec-title">👤 Historial de Jugadores</div>',unsafe_allow_html=True)
    exportar_pdf_btn("Historial")
    df=cargar_sheet("historial")
    if df.empty: no_data_msg("Historial de Jugadores"); return

    # Filtros
    col1,col2,col3=st.columns(3)
    jugadores=sorted(df.iloc[:,0].dropna().unique().tolist()) if len(df.columns)>0 else []
    posiciones=sorted(df["POSICION"].dropna().unique().tolist()) if "POSICION" in df.columns else []
    with col1:
        buscar=st.text_input("🔍 Buscar jugador",placeholder="Nombre...",key="hist_buscar")
    with col2:
        pos_sel=st.selectbox("Posición",["Todas"]+posiciones,key="hist_pos")
    with col3:
        st.markdown("<br>",unsafe_allow_html=True)
        mostrar_tabla=st.toggle("Ver tabla completa",value=False,key="hist_tabla")

    dff=df.copy()
    if buscar:
        col_nombre=dff.columns[0]
        dff=dff[dff[col_nombre].astype(str).str.contains(buscar,case=False,na=False)]
    if pos_sel!="Todas" and "POSICION" in dff.columns:
        dff=dff[dff["POSICION"]==pos_sel]

    st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:12px;">{len(dff)} jugadores encontrados</div>',unsafe_allow_html=True)

    if mostrar_tabla:
        st.dataframe(dff,use_container_width=True,hide_index=True)
    else:
        # Cards por jugador
        cols=st.columns(2)
        for i,(_, row) in enumerate(dff.iterrows()):
            with cols[i%2]:
                nombre=str(row.iloc[0]) if len(row)>0 else "—"
                pos=str(row.get("POSICION","—")) if "POSICION" in row.index else "—"
                edad=str(row.get("EDAD","—")) if "EDAD" in row.index else (str(row.get("AGE","—")) if "AGE" in row.index else "—")
                nac=str(row.get("FECHA_NAC","—")) if "FECHA_NAC" in row.index else (str(row.get("FECHA NAC","—")) if "FECHA NAC" in row.index else "—")
                nacio=str(row.get("NACIONALIDAD","—")) if "NACIONALIDAD" in row.index else "—"
                pie=str(row.get("LADO_HABIL","—")) if "LADO_HABIL" in row.index else (str(row.get("PIERNA","—")) if "PIERNA" in row.index else "—")

                # Foto del jugador
                foto_cols=[c for c in row.index if "foto" in c.lower() or "url" in c.lower() or "imagen" in c.lower()]
                foto_url=str(row[foto_cols[0]]) if foto_cols and str(row[foto_cols[0]])!="nan" else None
                foto_html=""
                if foto_url and foto_url.startswith("http"):
                    foto_html=f'<img src="{foto_url}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid rgba(200,16,46,.4);">'
                else:
                    foto_html='<div style="width:64px;height:64px;border-radius:50%;background:rgba(200,16,46,.15);display:flex;align-items:center;justify-content:center;font-size:28px;">👤</div>'

                st.markdown(f"""
                <div class="player-card">
                    <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">
                        {foto_html}
                        <div>
                            <div style="font-size:16px;font-weight:800;color:#fff;">{nombre}</div>
                            <div><span class="chip">{pos}</span><span class="chip chip-blue">{nacio}</span></div>
                        </div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;color:#94a3b8;">
                        <div>🎂 <b style="color:#e2e8f0;">Nacimiento:</b> {nac}</div>
                        <div>🦵 <b style="color:#e2e8f0;">Pierna:</b> {pie}</div>
                        <div>📅 <b style="color:#e2e8f0;">Edad:</b> {edad}</div>
                    </div>
                </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ESTADÍSTICAS MÉDICAS
# ══════════════════════════════════════════════════════════════
def pagina_estadisticas_medicas():
    import plotly.express as px, plotly.graph_objects as go
    st.markdown('<div class="sec-title">🏥 Estadísticas Médicas</div>',unsafe_allow_html=True)
    exportar_pdf_btn("Estadísticas Médicas")
    df=cargar_sheet("lesiones")
    if df.empty: no_data_msg("Estadísticas Médicas"); return

    st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:8px;">{len(df)} registros cargados · Columnas: {", ".join(df.columns[:8].tolist())}</div>',unsafe_allow_html=True)

    # Filtros
    col1,col2=st.columns(2)
    jug_col=[c for c in df.columns if "jugador" in c.lower() or "name" in c.lower() or "player" in c.lower()]
    jug_col=jug_col[0] if jug_col else df.columns[0]
    jugadores=["Todos"]+sorted(df[jug_col].dropna().astype(str).unique().tolist())
    with col1: jug_sel=st.selectbox("Jugador",jugadores,key="med_jug")
    with col2:
        fecha_cols=[c for c in df.columns if "fecha" in c.lower() or "date" in c.lower()]
        if fecha_cols:
            anios=["Todos"]+sorted(df[fecha_cols[0]].dropna().astype(str).str[:4].unique().tolist(),reverse=True)
            anio_sel=st.selectbox("Año",anios,key="med_anio")
        else: anio_sel="Todos"

    dff=df.copy()
    if jug_sel!="Todos": dff=dff[dff[jug_col].astype(str)==jug_sel]

    # KPIs
    c1,c2,c3,c4=st.columns(4)
    c1.metric("📋 Total registros",len(dff))
    dias_col=[c for c in dff.columns if "day" in c.lower() or "dias" in c.lower() or "baja" in c.lower()]
    if dias_col:
        dias_num=pd.to_numeric(dff[dias_col[0]].astype(str).str.replace(",","."),errors="coerce")
        c2.metric("📅 Total días baja",int(dias_num.sum()) if not dias_num.isna().all() else "—")
        c3.metric("⏱️ Promedio días",round(dias_num.mean(),1) if not dias_num.isna().all() else "—")
    else:
        c2.metric("📅 Días baja","—"); c3.metric("⏱️ Promedio","—")
    c4.metric("👥 Jugadores afectados",dff[jug_col].nunique())

    st.markdown("---")
    # Gráficos
    g1,g2=st.columns(2)
    tipo_col=[c for c in dff.columns if "tipo" in c.lower() or "lesion" in c.lower() or "injury" in c.lower() or "estructura" in c.lower()]
    if tipo_col:
        with g1:
            st.markdown('<div class="subsec">Lesiones por tipo</div>',unsafe_allow_html=True)
            vc=dff[tipo_col[0]].value_counts().head(10)
            fig=px.bar(x=vc.values,y=vc.index,orientation="h",
                      color_discrete_sequence=["#c8102e"],template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                             margin=dict(l=0,r=0,t=10,b=0),height=280,
                             xaxis_title="",yaxis_title="",font_color="#e2e8f0")
            st.plotly_chart(fig,use_container_width=True)
    zona_col=[c for c in dff.columns if "zona" in c.lower() or "region" in c.lower() or "parte" in c.lower() or "area" in c.lower() or "body" in c.lower()]
    if zona_col:
        with g2:
            st.markdown('<div class="subsec">Lesiones por zona</div>',unsafe_allow_html=True)
            vc2=dff[zona_col[0]].value_counts().head(8)
            fig2=px.pie(values=vc2.values,names=vc2.index,
                       color_discrete_sequence=px.colors.sequential.Reds_r,template="plotly_dark")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=0,t=10,b=0),
                              height=280,font_color="#e2e8f0",showlegend=True)
            st.plotly_chart(fig2,use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="subsec">Registros completos</div>',unsafe_allow_html=True)
    st.dataframe(dff,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════
# EVALUACIONES FÍSICAS
# ══════════════════════════════════════════════════════════════
def pagina_evaluaciones():
    import plotly.express as px, plotly.graph_objects as go
    st.markdown('<div class="sec-title">⚡ Evaluaciones Físicas</div>',unsafe_allow_html=True)
    exportar_pdf_btn("Evaluaciones")

    tab1,tab2,tab3,tab4=st.tabs(["🦵 CMJ","🏋️ CMJ 1 Pierna","💪 Curl Nórdico","⚡ VBT"])

    def filtro_jugador(df,label):
        jug_col=[c for c in df.columns if "jugador" in c.lower() or "name" in c.lower() or "atleta" in c.lower() or "player" in c.lower()]
        jug_col=jug_col[0] if jug_col else df.columns[0]
        opts=["Todos"]+sorted(df[jug_col].dropna().astype(str).unique().tolist())
        sel=st.selectbox(f"Jugador ({label})",opts,key=f"eval_{label}_jug")
        return df if sel=="Todos" else df[df[jug_col].astype(str)==sel], jug_col

    with tab1:
        df=cargar_sheet("cmj")
        if df.empty: no_data_msg("CMJ")
        else:
            dff,jug_col=filtro_jugador(df,"CMJ")
            num_cols=[c for c in dff.columns if pd.to_numeric(dff[c].astype(str).str.replace(",","."),errors="coerce").notna().sum()>len(dff)*0.3]
            if num_cols:
                c1,c2,c3=st.columns(3)
                for col,met in zip(num_cols[:3],[c1,c2,c3]):
                    vals=pd.to_numeric(dff[col].astype(str).str.replace(",","."),errors="coerce").dropna()
                    met.metric(col[:25],round(vals.mean(),2) if len(vals)>0 else "—")
            st.markdown('<div class="subsec">Evolución temporal</div>',unsafe_allow_html=True)
            fecha_col=[c for c in dff.columns if "fecha" in c.lower() or "date" in c.lower()]
            altura_col=[c for c in dff.columns if "height" in c.lower() or "altura" in c.lower() or "jump" in c.lower()]
            if fecha_col and altura_col:
                dff2=dff.copy()
                dff2["_fecha"]=pd.to_datetime(dff2[fecha_col[0]],errors="coerce",dayfirst=True)
                dff2["_val"]=pd.to_numeric(dff2[altura_col[0]].astype(str).str.replace(",","."),errors="coerce")
                dff2=dff2.dropna(subset=["_fecha","_val"]).sort_values("_fecha")
                fig=px.line(dff2,x="_fecha",y="_val",color=jug_col if jug_col in dff2.columns else None,
                           template="plotly_dark",labels={"_fecha":"Fecha","_val":altura_col[0]})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                                 margin=dict(l=0,r=0,t=10,b=0),height=300,font_color="#e2e8f0")
                fig.update_traces(line_color="#c8102e")
                st.plotly_chart(fig,use_container_width=True)
            st.dataframe(dff,use_container_width=True,hide_index=True)

    with tab2:
        df=cargar_sheet("cmj1pp")
        if df.empty: no_data_msg("CMJ 1 Pierna")
        else:
            dff,jug_col=filtro_jugador(df,"CMJ1PP")
            st.dataframe(dff,use_container_width=True,hide_index=True)

    with tab3:
        df=cargar_sheet("nordico")
        if df.empty: no_data_msg("Curl Nórdico")
        else:
            dff,jug_col=filtro_jugador(df,"Nordico")
            r_col=[c for c in dff.columns if "r " in c.lower() or "right" in c.lower() or " r" in c.lower()]
            l_col=[c for c in dff.columns if "l " in c.lower() or "left" in c.lower() or " l" in c.lower()]
            if r_col and l_col:
                st.markdown('<div class="subsec">Comparativa Derecha vs Izquierda</div>',unsafe_allow_html=True)
                import plotly.graph_objects as go
                r_vals=pd.to_numeric(dff[r_col[0]].astype(str).str.replace(",","."),errors="coerce").dropna()
                l_vals=pd.to_numeric(dff[l_col[0]].astype(str).str.replace(",","."),errors="coerce").dropna()
                c1,c2=st.columns(2)
                c1.metric(f"Prom. Derecha ({r_col[0][:20]})",round(r_vals.mean(),1) if len(r_vals)>0 else "—")
                c2.metric(f"Prom. Izquierda ({l_col[0][:20]})",round(l_vals.mean(),1) if len(l_vals)>0 else "—")
            st.dataframe(dff,use_container_width=True,hide_index=True)

    with tab4:
        df=cargar_sheet("vbt")
        if df.empty: no_data_msg("VBT")
        else:
            dff,jug_col=filtro_jugador(df,"VBT")
            st.dataframe(dff,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════
# DEMANDAS FÍSICAS (GPS)
# ══════════════════════════════════════════════════════════════
def pagina_demandas():
    import plotly.express as px
    st.markdown('<div class="sec-title">📡 Demandas Físicas — GPS</div>',unsafe_allow_html=True)
    exportar_pdf_btn("Demandas Físicas")
    df=cargar_sheet("gps")
    if df.empty: no_data_msg("GPS"); return

    st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:8px;">{len(df)} sesiones · Columnas: {", ".join(df.columns[:10].tolist())}</div>',unsafe_allow_html=True)

    tab1,tab2,tab3=st.tabs(["📊 Resumen Microciclo","👤 Resumen Individual","📈 Ratio A:C"])

    jug_col=[c for c in df.columns if "jugador" in c.lower() or "name" in c.lower() or "player" in c.lower() or "atleta" in c.lower()]
    jug_col=jug_col[0] if jug_col else df.columns[0]
    fecha_col=[c for c in df.columns if "fecha" in c.lower() or "date" in c.lower()]
    fecha_col=fecha_col[0] if fecha_col else None
    dist_col=[c for c in df.columns if "dist" in c.lower() or "tot" in c.lower()]
    dist_col=dist_col[0] if dist_col else None

    with tab1:
        st.markdown('<div class="subsec">Carga semanal del equipo</div>',unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            if fecha_col:
                df["_fecha"]=pd.to_datetime(df[fecha_col],errors="coerce",dayfirst=True)
                df["_semana"]=df["_fecha"].dt.isocalendar().week
                df["_anio"]=df["_fecha"].dt.year
                anios=sorted(df["_anio"].dropna().unique().tolist(),reverse=True)
                anio=st.selectbox("Año",anios,key="gps_anio")
                semanas=sorted(df[df["_anio"]==anio]["_semana"].dropna().unique().tolist())
                sem=st.selectbox("Semana",semanas,key="gps_sem")
            else: anio,sem=None,None
        with col2:
            jugadores_gps=["Todos"]+sorted(df[jug_col].dropna().astype(str).unique().tolist())
            jug_sel=st.selectbox("Jugador",jugadores_gps,key="gps_jug")

        dff=df.copy()
        if anio and sem: dff=dff[(dff["_anio"]==anio)&(dff["_semana"]==sem)]
        if jug_sel!="Todos": dff=dff[dff[jug_col].astype(str)==jug_sel]

        c1,c2,c3,c4=st.columns(4)
        c1.metric("📋 Sesiones",len(dff))
        if dist_col:
            dvals=pd.to_numeric(dff[dist_col].astype(str).str.replace(",","."),errors="coerce")
            c2.metric("📏 Dist. Total (m)",f"{int(dvals.sum()):,}" if not dvals.isna().all() else "—")
            c3.metric("📏 Dist. Prom.",f"{int(dvals.mean()):,}" if not dvals.isna().all() else "—")
        c4.metric("👥 Jugadores",dff[jug_col].nunique())

        if dist_col and fecha_col:
            dff2=dff.dropna(subset=["_fecha"]).copy()
            dff2[dist_col]=pd.to_numeric(dff2[dist_col].astype(str).str.replace(",","."),errors="coerce")
            if not dff2.empty:
                fig=px.bar(dff2.sort_values("_fecha"),x="_fecha",y=dist_col,color=jug_col,
                          template="plotly_dark",labels={"_fecha":"Fecha",dist_col:"Distancia (m)"},
                          color_discrete_sequence=px.colors.sequential.Reds_r)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                                 margin=dict(l=0,r=0,t=10,b=0),height=320,font_color="#e2e8f0")
                st.plotly_chart(fig,use_container_width=True)

        st.dataframe(dff,use_container_width=True,hide_index=True)

    with tab2:
        st.markdown('<div class="subsec">Perfil individual</div>',unsafe_allow_html=True)
        jug_ind=st.selectbox("Seleccioná jugador",sorted(df[jug_col].dropna().astype(str).unique().tolist()),key="gps_ind")
        dfi=df[df[jug_col].astype(str)==jug_ind].copy()
        num_cols=[c for c in dfi.columns if pd.to_numeric(dfi[c].astype(str).str.replace(",","."),errors="coerce").notna().sum()>len(dfi)*0.3]
        cols=st.columns(min(4,len(num_cols)))
        for i,col in enumerate(num_cols[:4]):
            vals=pd.to_numeric(dfi[col].astype(str).str.replace(",","."),errors="coerce").dropna()
            cols[i].metric(col[:20],round(vals.mean(),1) if len(vals)>0 else "—")
        if fecha_col and dist_col:
            dfi["_fecha"]=pd.to_datetime(dfi[fecha_col],errors="coerce",dayfirst=True)
            dfi[dist_col]=pd.to_numeric(dfi[dist_col].astype(str).str.replace(",","."),errors="coerce")
            dfi=dfi.dropna(subset=["_fecha",dist_col]).sort_values("_fecha")
            fig=px.line(dfi,x="_fecha",y=dist_col,template="plotly_dark",markers=True,
                       labels={"_fecha":"Fecha",dist_col:"Distancia (m)"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                             margin=dict(l=0,r=0,t=10,b=0),height=300,font_color="#e2e8f0")
            fig.update_traces(line_color="#c8102e",marker_color="#fff")
            st.plotly_chart(fig,use_container_width=True)

    with tab3:
        st.markdown('<div class="subsec">Ratio Aguda:Crónica (A:C)</div>',unsafe_allow_html=True)
        if dist_col and fecha_col and jug_col:
            jug_ac=st.selectbox("Jugador A:C",sorted(df[jug_col].dropna().astype(str).unique().tolist()),key="gps_ac")
            dfac=df[df[jug_col].astype(str)==jug_ac].copy()
            dfac["_fecha"]=pd.to_datetime(dfac[fecha_col],errors="coerce",dayfirst=True)
            dfac[dist_col]=pd.to_numeric(dfac[dist_col].astype(str).str.replace(",","."),errors="coerce")
            dfac=dfac.dropna(subset=["_fecha",dist_col]).sort_values("_fecha").set_index("_fecha")
            dfac["aguda"]=dfac[dist_col].rolling("7D").sum()
            dfac["cronica"]=dfac[dist_col].rolling("28D").mean()*7
            dfac["ratio_ac"]=dfac["aguda"]/dfac["cronica"].replace(0,float("nan"))
            dfac=dfac.reset_index()
            if not dfac.empty:
                fig=px.line(dfac,x="_fecha",y="ratio_ac",template="plotly_dark",
                           labels={"_fecha":"Fecha","ratio_ac":"Ratio A:C"})
                fig.add_hline(y=0.8,line_dash="dot",line_color="#4ade80",annotation_text="Óptimo bajo 0.8")
                fig.add_hline(y=1.3,line_dash="dot",line_color="#f87171",annotation_text="Riesgo >1.3")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                                 margin=dict(l=0,r=0,t=10,b=0),height=320,font_color="#e2e8f0")
                fig.update_traces(line_color="#c8102e")
                st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("Se necesitan columnas de fecha, distancia y jugador para calcular A:C.")

# ══════════════════════════════════════════════════════════════
# CONTROL DE PARTIDOS
# ══════════════════════════════════════════════════════════════
def pagina_control_partidos():
    import plotly.express as px
    st.markdown('<div class="sec-title">⚽ Control de Partidos</div>',unsafe_allow_html=True)
    exportar_pdf_btn("Control Partidos")
    df=cargar_sheet("partidos")
    if df.empty: no_data_msg("Control de Partidos"); return

    st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:8px;">{len(df)} registros · Columnas: {", ".join(df.columns[:8].tolist())}</div>',unsafe_allow_html=True)

    jug_col=[c for c in df.columns if "jugador" in c.lower() or "name" in c.lower() or "player" in c.lower()]
    jug_col=jug_col[0] if jug_col else df.columns[0]

    col1,col2=st.columns(2)
    with col1: jug_sel=st.selectbox("Jugador",["Todos"]+sorted(df[jug_col].dropna().astype(str).unique().tolist()),key="part_jug")
    with col2:
        fecha_col=[c for c in df.columns if "fecha" in c.lower() or "date" in c.lower()]
        if fecha_col:
            anios=["Todos"]+sorted(df[fecha_col[0]].dropna().astype(str).str[:4].unique().tolist(),reverse=True)
            anio_sel=st.selectbox("Año",anios,key="part_anio")
        else: anio_sel="Todos"

    dff=df.copy()
    if jug_sel!="Todos": dff=dff[dff[jug_col].astype(str)==jug_sel]

    c1,c2,c3=st.columns(3)
    c1.metric("📋 Registros",len(dff))
    min_col=[c for c in dff.columns if "min" in c.lower() or "minute" in c.lower()]
    if min_col:
        mvals=pd.to_numeric(dff[min_col[0]].astype(str).str.replace(",","."),errors="coerce")
        c2.metric("⏱️ Min. totales",int(mvals.sum()) if not mvals.isna().all() else "—")
        c3.metric("⏱️ Min. promedio",round(mvals.mean(),1) if not mvals.isna().all() else "—")

    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(26,90,180,0.08);border:1px solid rgba(26,90,180,0.2);
         border-radius:12px;padding:16px;margin-bottom:16px;">
        <div style="font-size:12px;font-weight:700;color:#93c5fd;margin-bottom:6px;">🔌 API de Fútbol Argentino</div>
        <div style="font-size:13px;color:#64748b;">
            Integración con <b style="color:#e2e8f0;">API-Football</b> (plan gratuito · 100 req/día)
            para obtener estadísticas de la Liga Profesional Argentina en tiempo real.
            Requiere API key — se configura en Streamlit Secrets.
        </div>
    </div>""",unsafe_allow_html=True)

    st.dataframe(dff,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════
# RESUMEN INDIVIDUAL
# ══════════════════════════════════════════════════════════════
def pagina_resumen():
    import plotly.express as px, plotly.graph_objects as go
    st.markdown('<div class="sec-title">📄 Resumen Individual</div>',unsafe_allow_html=True)
    exportar_pdf_btn("Resumen Individual")

    # Selector de jugador desde historial
    hist=cargar_sheet("historial")
    if hist.empty: no_data_msg("Historial de Jugadores"); return

    jug_col_h=[c for c in hist.columns if "jugador" in c.lower() or "name" in c.lower() or "player" in c.lower()]
    jug_col_h=jug_col_h[0] if jug_col_h else hist.columns[0]
    jugadores=sorted(hist[jug_col_h].dropna().astype(str).unique().tolist())

    col1,col2=st.columns([2,1])
    with col1: jug_sel=st.selectbox("Seleccioná jugador",jugadores,key="res_jug")
    with col2:
        secciones_sel=st.multiselect("Incluir en reporte",
            ["GPS","CMJ","Nórdico","Lesiones","VBT"],
            default=["GPS","CMJ","Lesiones"],key="res_secs")

    row=hist[hist[jug_col_h].astype(str)==jug_sel].iloc[0] if len(hist[hist[jug_col_h].astype(str)==jug_sel])>0 else None

    if row is not None:
        pos=str(row.get("POSICION",row.get("POS","—")))
        edad=str(row.get("EDAD",row.get("AGE","—")))
        nac=str(row.get("NACIONALIDAD",row.get("PAIS","—")))
        foto_cols=[c for c in row.index if "foto" in c.lower() or "url" in c.lower()]
        foto_url=str(row[foto_cols[0]]) if foto_cols and str(row[foto_cols[0]])!="nan" else None
        foto_html=f'<img src="{foto_url}" style="width:90px;height:90px;border-radius:50%;object-fit:cover;border:3px solid rgba(200,16,46,.5);">' if foto_url and foto_url.startswith("http") else '<div style="width:90px;height:90px;border-radius:50%;background:rgba(200,16,46,.15);display:flex;align-items:center;justify-content:center;font-size:48px;">👤</div>'

        st.markdown(f"""
        <div style="background:rgba(8,18,38,0.95);border:1px solid rgba(200,16,46,.25);
             border-radius:20px;padding:24px;margin:12px 0;">
            <div style="display:flex;align-items:center;gap:20px;margin-bottom:16px;">
                {foto_html}
                <div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:2px;color:#fff;">{jug_sel}</div>
                    <div style="margin-top:6px;">
                        <span class="chip">{pos}</span>
                        <span class="chip chip-blue">{nac}</span>
                        <span class="chip chip-green">Edad: {edad}</span>
                    </div>
                </div>
            </div>
        </div>""",unsafe_allow_html=True)

    # Datos según selección
    if "GPS" in secciones_sel:
        st.markdown('<div class="subsec">📡 Demandas Físicas GPS</div>',unsafe_allow_html=True)
        gps=cargar_sheet("gps")
        if not gps.empty:
            jcol=[c for c in gps.columns if "jugador" in c.lower() or "name" in c.lower() or "player" in c.lower()]
            if jcol:
                dgps=gps[gps[jcol[0]].astype(str).str.lower()==jug_sel.lower()]
                num_cols=[c for c in dgps.columns if pd.to_numeric(dgps[c].astype(str).str.replace(",","."),errors="coerce").notna().sum()>len(dgps)*0.3]
                if num_cols:
                    cs=st.columns(min(4,len(num_cols)))
                    for i,col in enumerate(num_cols[:4]):
                        vals=pd.to_numeric(dgps[col].astype(str).str.replace(",","."),errors="coerce").dropna()
                        cs[i].metric(col[:20],round(vals.mean(),1) if len(vals)>0 else "—")

    if "CMJ" in secciones_sel:
        st.markdown('<div class="subsec">🦵 CMJ</div>',unsafe_allow_html=True)
        cmj=cargar_sheet("cmj")
        if not cmj.empty:
            jcol=[c for c in cmj.columns if "jugador" in c.lower() or "name" in c.lower() or "atleta" in c.lower()]
            if jcol:
                dcmj=cmj[cmj[jcol[0]].astype(str).str.lower()==jug_sel.lower()]
                num_cols=[c for c in dcmj.columns if pd.to_numeric(dcmj[c].astype(str).str.replace(",","."),errors="coerce").notna().sum()>len(dcmj)*0.3]
                cs=st.columns(min(4,len(num_cols)))
                for i,col in enumerate(num_cols[:4]):
                    vals=pd.to_numeric(dcmj[col].astype(str).str.replace(",","."),errors="coerce").dropna()
                    cs[i].metric(col[:20],round(vals.mean(),2) if len(vals)>0 else "—")

    if "Lesiones" in secciones_sel:
        st.markdown('<div class="subsec">🏥 Historial médico</div>',unsafe_allow_html=True)
        les=cargar_sheet("lesiones")
        if not les.empty:
            jcol=[c for c in les.columns if "jugador" in c.lower() or "name" in c.lower() or "player" in c.lower()]
            if jcol:
                dles=les[les[jcol[0]].astype(str).str.lower()==jug_sel.lower()]
                if not dles.empty: st.dataframe(dles,use_container_width=True,hide_index=True)
                else: st.info(f"Sin registros médicos para {jug_sel}.")

# ══════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════
def pagina_admin():
    st.markdown('<div class="sec-title">🔧 Panel de Administración</div>',unsafe_allow_html=True)
    pendientes={k:d for k,d in st.session_state.usuarios_extra.items() if not d.get("aprobado")}
    if pendientes:
        st.warning(f"⚠️ {len(pendientes)} solicitud(es) pendiente(s)")
        for username,datos in pendientes.items():
            with st.expander(f"👤 {datos['nombre']} — {datos['area']} · {datos['rol']}"):
                st.write(f"**Email:** {datos.get('email','—')} | **Usuario:** `{username}`")
                c1,c2=st.columns(2)
                with c1:
                    if st.button("✅ Aprobar",key=f"apr_{username}"):
                        st.session_state.usuarios_extra[username]["aprobado"]=True
                        st.session_state.usuarios_extra[username]["activo"]=True
                        st.success(f"✅ {datos['nombre']} aprobado. Usuario: `{username}`"); st.rerun()
                with c2:
                    if st.button("❌ Rechazar",key=f"rec_{username}"):
                        del st.session_state.usuarios_extra[username]
                        st.warning("Rechazado."); st.rerun()
    else: st.success("✅ No hay solicitudes pendientes.")
    st.markdown("---")
    st.markdown("#### 👥 Usuarios del sistema")
    fa=st.selectbox("Filtrar por área",["Todas"]+list(AREAS.keys()),key="fa_admin")
    todos=todos_los_usuarios()
    rows=[(k,d) for k,d in todos.items() if fa=="Todas" or d["area"]==fa]
    filas_html=""
    for username,d in rows:
        ba='<span class="badge-activo">Activo</span>' if d["activo"] else '<span class="badge-inactivo">Inactivo</span>'
        barea=f'<span class="badge-area">{d["area"]}</span>'
        filas_html+=f'<tr><td><code style="color:#60a5fa;">{username}</code></td><td><b>{d["nombre"]}</b></td><td>{barea}</td><td style="color:#94a3b8;">{d["rol"]}</td><td style="color:#64748b;font-size:12px;">{d.get("email","—")}</td><td>{ba}</td></tr>'
    st.markdown(f'<div style="background:rgba(8,18,38,.9);border:1px solid rgba(255,255,255,.06);border-radius:16px;overflow:hidden;margin-top:8px;"><table class="user-table"><thead><tr><th>Usuario</th><th>Nombre</th><th>Área</th><th>Rol</th><th>Email</th><th>Estado</th></tr></thead><tbody>{filas_html}</tbody></table></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### ⚙️ Gestión")
    sel=st.selectbox("Usuario",["— elegí —"]+list(todos.keys()),key="adm_sel")
    if sel!="— elegí —":
        d=todos[sel]
        st.write(f"**{d['nombre']}** · {d['area']} · {d['rol']} · `{sel}`")
        c1,c2,c3=st.columns(3)
        with c1:
            if d["activo"]:
                if st.button("🔴 Desactivar",key="btn_des"):
                    st.session_state.usuarios_desactivados.add(sel); st.warning(f"{d['nombre']} desactivado."); st.rerun()
            else:
                if st.button("🟢 Activar",key="btn_act"):
                    st.session_state.usuarios_desactivados.discard(sel); st.success(f"{d['nombre']} activado."); st.rerun()
        with c2:
            if sel in st.session_state.usuarios_extra:
                if st.button("🗑️ Eliminar",key="btn_del"):
                    del st.session_state.usuarios_extra[sel]; st.warning(f"{sel} eliminado."); st.rerun()
            else: st.caption("Usuarios base no eliminables")

# ══════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════
def render_pagina():
    u=st.session_state.usuario; p=st.session_state.pagina
    if not tiene_acceso(u,p) and p!="admin": st.error("🚫 No tenés acceso."); return
    {
        "home":                 pagina_home,
        "historial":            pagina_historial,
        "estadisticas_medicas": pagina_estadisticas_medicas,
        "evaluaciones":         pagina_evaluaciones,
        "demandas_fisicas":     pagina_demandas,
        "control_partidos":     pagina_control_partidos,
        "resumen_individual":   pagina_resumen,
        "admin":                pagina_admin,
    }.get(p,lambda:st.error("Página no encontrada"))()

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged:
    pagina_login()
else:
    top_bar(logged=True,usuario=st.session_state.usuario)
    render_sidebar()
    render_pagina()
