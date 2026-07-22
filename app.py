import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64, hashlib, re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import modelo_riesgo as mr
import demandas_fisicas as dfx
import pdf_export

st.set_page_config(page_title="CAU · Rendimiento Físico", page_icon="⚽",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800;900&display=swap');
.stApp{background:linear-gradient(135deg,#0c1e3e 0%,#112347 50%,#0c1e3e 100%);color:#e8ecf4;font-family:'Inter',sans-serif;}
header[data-testid="stHeader"]{display:none!important;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#091528 0%,#0d1e38 100%)!important;border-right:1px solid rgba(200,16,46,0.3)!important;}
section[data-testid="stSidebar"] *{color:#e8ecf4!important;}
section[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,0.04)!important;color:#e8ecf4!important;border:1px solid rgba(255,255,255,0.07)!important;border-radius:10px!important;font-weight:500!important;text-align:left!important;padding-left:14px!important;transition:all .2s!important;}
section[data-testid="stSidebar"] .stButton>button:hover{background:linear-gradient(135deg,#c8102e,#8b0000)!important;border-color:transparent!important;}
.stButton>button{background:linear-gradient(135deg,#c8102e,#8b0000)!important;color:#fff!important;border:none!important;border-radius:10px!important;font-weight:700!important;transition:all .2s!important;}
.stButton>button:hover{opacity:.85!important;transform:translateY(-1px)!important;}
input,textarea{background:#112040!important;border:1px solid rgba(200,16,46,0.4)!important;border-radius:10px!important;color:#ffffff!important;}
input::placeholder{color:#475569!important;}
input:focus{border-color:#c8102e!important;color:#ffffff!important;}
.stTextInput label,.stSelectbox label,.stMultiSelect label{color:#94a3b8!important;font-size:12px!important;font-weight:600!important;}
.stSelectbox>div>div{background:#112040!important;border:1px solid rgba(200,16,46,0.4)!important;border-radius:10px!important;color:#ffffff!important;}
[data-baseweb="select"]>div{background:#112040!important;}
[data-baseweb="select"] span{color:#ffffff!important;}
.stTabs [data-baseweb="tab-list"]{background:rgba(15,30,60,0.8)!important;border-radius:12px!important;padding:4px!important;gap:4px!important;}
.stTabs [data-baseweb="tab"]{color:#64748b!important;border-radius:8px!important;font-weight:600!important;font-size:13px!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#c8102e,#8b0000)!important;color:#fff!important;}
.login-card{max-width:460px;margin:20px auto 0;padding:32px 28px;border-radius:24px;background:rgba(8,18,38,0.98);border:1px solid rgba(200,16,46,0.35);box-shadow:0 24px 64px rgba(0,0,0,0.7);text-align:center;}
.login-title{font-family:'Bebas Neue',sans-serif;font-size:44px;letter-spacing:5px;color:#fff;line-height:1;}
.login-sub{color:#c8102e;font-size:11px;font-weight:700;letter-spacing:3px;margin:6px 0 0;text-transform:uppercase;}
.top-bar{position:fixed;top:0;left:0;right:0;z-index:9999;height:52px;background:linear-gradient(90deg,#070f20 0%,#0d1e3c 40%,#1a0a14 60%,#070f20 100%);border-bottom:2px solid rgba(200,16,46,0.5);display:flex;align-items:center;justify-content:space-between;padding:0 24px;gap:12px;}
.top-bar-center{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:5px;color:#fff;flex:1;text-align:center;}
.top-card{background:rgba(200,16,46,0.12);border:1px solid rgba(200,16,46,0.25);border-radius:8px;padding:4px 14px;font-size:12px;font-weight:700;color:#fff;white-space:nowrap;}
.top-card small{display:block;font-size:9px;color:#94a3b8;font-weight:400;letter-spacing:1px;text-transform:uppercase;}
.spacer-top{height:52px;}
.sec-title{color:#fff;font-size:18px;font-weight:900;border-left:4px solid #c8102e;padding-left:10px;margin:20px 0 12px;}
.subsec{color:#fff;font-size:15px;font-weight:700;border-left:3px solid rgba(200,16,46,0.5);padding-left:8px;margin:14px 0 8px;}
[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(12,28,56,.98),rgba(17,35,70,.9));border:1px solid rgba(200,16,46,.2);border-radius:16px;padding:14px;}
[data-testid="stMetricLabel"] p{color:#f87171!important;font-weight:700!important;font-size:11px!important;}
[data-testid="stMetricValue"]{color:#fff!important;font-weight:900!important;}
.player-card{background:linear-gradient(135deg,rgba(12,28,56,.98),rgba(8,18,40,.95));border:1px solid rgba(200,16,46,0.2);border-radius:18px;padding:20px;margin-bottom:14px;transition:border-color .2s;}
.player-card:hover{border-color:rgba(200,16,46,0.5);}
.chip{display:inline-block;background:rgba(200,16,46,0.12);border:1px solid rgba(200,16,46,0.3);color:#f87171;border-radius:6px;padding:2px 9px;font-size:10px;font-weight:700;margin:2px 2px 2px 0;}
.chip-blue{background:rgba(26,90,180,0.15);border-color:rgba(26,90,180,0.35);color:#93c5fd;}
.chip-green{background:rgba(34,197,94,0.1);border-color:rgba(34,197,94,0.3);color:#4ade80;}
.kpi-card{background:linear-gradient(145deg,rgba(8,18,40,.98),rgba(12,28,56,.95));border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:20px;text-align:center;position:relative;}
.kpi-main{font-size:36px;font-weight:900;color:#fff;line-height:1;}
.kpi-label{font-size:10px;color:#c8102e;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;}
.kpi-ref{display:flex;justify-content:space-around;margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);}
.kpi-ref-item{text-align:center;}
.kpi-ref-val{font-size:16px;font-weight:800;}
.kpi-ref-label{font-size:9px;letter-spacing:1px;text-transform:uppercase;margin-top:2px;}
.user-table{width:100%;border-collapse:collapse;font-size:13px;}
.user-table th{background:rgba(200,16,46,0.15);color:#f87171;font-weight:700;font-size:10px;letter-spacing:2px;text-transform:uppercase;padding:10px 14px;text-align:left;border-bottom:1px solid rgba(200,16,46,0.3);}
.user-table td{padding:10px 14px;color:#e2e8f0;border-bottom:1px solid rgba(255,255,255,0.04);}
.user-table tr:hover td{background:rgba(200,16,46,0.05);}
.badge-activo{background:rgba(34,197,94,0.15);color:#4ade80;border:1px solid rgba(34,197,94,0.3);border-radius:6px;padding:2px 10px;font-size:11px;font-weight:700;}
.badge-inactivo{background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);border-radius:6px;padding:2px 10px;font-size:11px;font-weight:700;}
.badge-area{background:rgba(26,90,180,0.15);color:#93c5fd;border:1px solid rgba(26,90,180,0.3);border-radius:6px;padding:2px 10px;font-size:11px;}
.filter-bar{background:rgba(8,18,38,0.8);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:14px 18px;margin-bottom:16px;}
.styled-table-wrap{border-radius:14px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);}
@media(max-width:768px){.login-card{margin:8px;padding:20px 14px;}.login-title{font-size:32px;}.top-bar-center{font-size:16px;letter-spacing:3px;}.top-card{display:none;}}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ÁREAS Y USUARIOS
# ══════════════════════════════════════════════════════════════
AREAS={"Médica":{"icon":"🏥","secciones":["home","historial","estadisticas_medicas","evaluaciones","riesgo_lesion","nutricion","resumen_individual"]},"Rendimiento":{"icon":"⚡","secciones":["home","historial","evaluaciones","riesgo_lesion","demandas_fisicas","control_partidos","nutricion","resumen_individual"]},"Secretaría Técnica":{"icon":"📋","secciones":["home","historial","estadisticas_medicas","evaluaciones","riesgo_lesion","demandas_fisicas","control_partidos","nutricion","resumen_individual"]},"Administración":{"icon":"🔧","secciones":["home","historial","estadisticas_medicas","evaluaciones","riesgo_lesion","demandas_fisicas","control_partidos","nutricion","resumen_individual","admin"]},"Scout":{"icon":"🔍","secciones":["home","historial","control_partidos"]}}
def _hash(p): return hashlib.sha256(p.encode()).hexdigest()
USUARIOS_BASE={"dr.garcia":{"nombre":"Dr. García","area":"Médica","rol":"Médico","email":"dr.garcia@cauunion.com","pwd":_hash("medica123"),"activo":True},"dr.lopez":{"nombre":"Dr. López","area":"Médica","rol":"Médico","email":"dr.lopez@cauunion.com","pwd":_hash("medica123"),"activo":True},"dr.martinez":{"nombre":"Dr. Martínez","area":"Médica","rol":"Médico","email":"dr.martinez@cauunion.com","pwd":_hash("medica123"),"activo":True},"kine.perez":{"nombre":"Lic. Pérez","area":"Médica","rol":"Kinesiólogo","email":"kine.perez@cauunion.com","pwd":_hash("kine123"),"activo":True},"kine.gomez":{"nombre":"Lic. Gómez","area":"Médica","rol":"Kinesiólogo","email":"kine.gomez@cauunion.com","pwd":_hash("kine123"),"activo":True},"kine.diaz":{"nombre":"Lic. Díaz","area":"Médica","rol":"Kinesiólogo","email":"kine.diaz@cauunion.com","pwd":_hash("kine123"),"activo":True},"kine.silva":{"nombre":"Lic. Silva","area":"Médica","rol":"Kinesiólogo","email":"kine.silva@cauunion.com","pwd":_hash("kine123"),"activo":True},"kine.torres":{"nombre":"Lic. Torres","area":"Médica","rol":"Kinesiólogo","email":"kine.torres@cauunion.com","pwd":_hash("kine123"),"activo":True},"pf.rodriguez":{"nombre":"Prof. Rodríguez","area":"Rendimiento","rol":"PF","email":"pf.rodriguez@cauunion.com","pwd":_hash("rend123"),"activo":True},"pf.fernandez":{"nombre":"Prof. Fernández","area":"Rendimiento","rol":"PF","email":"pf.fernandez@cauunion.com","pwd":_hash("rend123"),"activo":True},"pf.sanchez":{"nombre":"Prof. Sánchez","area":"Rendimiento","rol":"PF","email":"pf.sanchez@cauunion.com","pwd":_hash("rend123"),"activo":True},"nutri.ruiz":{"nombre":"Lic. Ruiz","area":"Rendimiento","rol":"Nutricionista","email":"nutri.ruiz@cauunion.com","pwd":_hash("rend123"),"activo":True},"nutri.mora":{"nombre":"Lic. Mora","area":"Rendimiento","rol":"Nutricionista","email":"nutri.mora@cauunion.com","pwd":_hash("rend123"),"activo":True},"nutri.vega":{"nombre":"Lic. Vega","area":"Rendimiento","rol":"Nutricionista","email":"nutri.vega@cauunion.com","pwd":_hash("rend123"),"activo":True},"ct.ramirez":{"nombre":"Prof. Ramírez","area":"Rendimiento","rol":"Cuerpo Técnico","email":"ct.ramirez@cauunion.com","pwd":_hash("rend123"),"activo":True},"ct.jimenez":{"nombre":"Prof. Jiménez","area":"Rendimiento","rol":"Cuerpo Técnico","email":"ct.jimenez@cauunion.com","pwd":_hash("rend123"),"activo":True},"ct.herrera":{"nombre":"Prof. Herrera","area":"Rendimiento","rol":"Cuerpo Técnico","email":"ct.herrera@cauunion.com","pwd":_hash("rend123"),"activo":True},"st.castro":{"nombre":"Lic. Castro","area":"Secretaría Técnica","rol":"Sec. Técnico","email":"st.castro@cauunion.com","pwd":_hash("sec123"),"activo":True},"st.vargas":{"nombre":"Lic. Vargas","area":"Secretaría Técnica","rol":"Sec. Técnico","email":"st.vargas@cauunion.com","pwd":_hash("sec123"),"activo":True},"st.medina":{"nombre":"Lic. Medina","area":"Secretaría Técnica","rol":"Sec. Técnico","email":"st.medina@cauunion.com","pwd":_hash("sec123"),"activo":True},"st.guerrero":{"nombre":"Lic. Guerrero","area":"Secretaría Técnica","rol":"Sec. Técnico","email":"st.guerrero@cauunion.com","pwd":_hash("sec123"),"activo":True},"admin":{"nombre":"Administrador","area":"Administración","rol":"Admin","email":"futbolprofesionalcau@gmail.com","pwd":_hash("admin123"),"activo":True},"scout.blanco":{"nombre":"Lic. Blanco","area":"Scout","rol":"Scout","email":"scout.blanco@cauunion.com","pwd":_hash("scout123"),"activo":True},"scout.acosta":{"nombre":"Lic. Acosta","area":"Scout","rol":"Scout","email":"scout.acosta@cauunion.com","pwd":_hash("scout123"),"activo":True},"scout.rios":{"nombre":"Lic. Ríos","area":"Scout","rol":"Scout","email":"scout.rios@cauunion.com","pwd":_hash("scout123"),"activo":True}}

for k,v in [("logged",False),("usuario",None),("pagina","home"),("usuarios_extra",{}),("usuarios_desactivados",set())]:
    if k not in st.session_state: st.session_state[k]=v

def todos_los_usuarios():
    u={}
    for k,d in USUARIOS_BASE.items(): u[k]={**d,"activo":k not in st.session_state.usuarios_desactivados and d["activo"],"tipo":"base"}
    for k,d in st.session_state.usuarios_extra.items():
        if d.get("aprobado"): u[k]={**d,"activo":k not in st.session_state.usuarios_desactivados and d.get("activo",True),"tipo":"extra"}
    return u

def verificar_login(username,password):
    u=todos_los_usuarios().get(username.lower().strip())
    if u and u["activo"] and u["pwd"]==_hash(password): return u
    return None
def tiene_acceso(u,s): return s in AREAS.get(u.get("area",""),{}).get("secciones",[])
def usuarios_por_area(area): return [k for k,d in todos_los_usuarios().items() if d["area"]==area and d["activo"]]

# ══════════════════════════════════════════════════════════════
# SHEETS
# ══════════════════════════════════════════════════════════════
SHEETS={"historial":"https://docs.google.com/spreadsheets/d/1Ppy3Mkz3ojqlcGAcxhNlqnGy5o2GmBHmdL9IZdRh9b0/edit?gid=0","lesiones":"https://docs.google.com/spreadsheets/d/1irSkXB8V_D_jZurEGUA9JMkLpE3e0_qad16_orjHDi8/edit?gid=0","cmj":"https://docs.google.com/spreadsheets/d/1VQLX1R1M0IW8j_TPXbVE8y5qaOA8-2qpj8cL-eGA1VY/edit?gid=1188054203","cmj1pp":"https://docs.google.com/spreadsheets/d/16ugXQ5hEnMa9bh_Ma1IDDaPq6gNq4QVPTRwQyVnz3oc/edit?gid=305963248","nordico":"https://docs.google.com/spreadsheets/d/1fhFajl9ckPYikfIKdBHTORcqQj0802JoNQ8-B3wEJWU/edit?gid=1994839095","vbt":"https://docs.google.com/spreadsheets/d/1NjVz_ivHKRrtai18ogjMQuQA6EYh3Q-WLDiNOErYO-Q/edit?gid=0","gps":"https://docs.google.com/spreadsheets/d/1W3hUX8zTPYXzDUSmdW7Nj2fXbEKlp1E2Us7kwNBhR6c/edit?gid=0","partidos":"https://docs.google.com/spreadsheets/d/17EiRiX-Tjlor0SfZvz-Wzfohz07calbA_26DKd4XL5g/edit?gid=2140450866","nutricion":"https://docs.google.com/spreadsheets/d/1tUsVAxfdeNbwGgAhJ865E3Fgf4x1TENcbTgt1ROAG2s/edit?gid=738328335"}

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
        fecha_cols=[c for c in df.columns if ("fecha" in c.lower() or "date" in c.lower()) and "_" not in c.lower()]
        if fecha_cols:
            df["_fecha"]=pd.to_datetime(df[fecha_cols[0]],dayfirst=True,errors="coerce")
            df["AÑO"]=df["_fecha"].dt.year.astype("Int64")
        elif "AÑO" in df.columns:
            df["AÑO"]=pd.to_numeric(df["AÑO"],errors="coerce").astype("Int64")
        return df
    except Exception: return pd.DataFrame()

def to_num(s): return pd.to_numeric(str(s).replace(",","."),errors="coerce")
def to_num_col(series): return pd.to_numeric(series.astype(str).str.replace(",","."),errors="coerce")

# ══════════════════════════════════════════════════════════════
# HELPERS UI
# ══════════════════════════════════════════════════════════════
ASSETS=Path("assets")
def img_b64(path):
    p=Path(path); return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

def escudo_tag(size=110):
    b64=img_b64(ASSETS/"escudo_union.png")
    return f'<img src="data:image/png;base64,{b64}" style="width:{size}px;height:{size}px;object-fit:contain;filter:drop-shadow(0 0 16px rgba(200,16,46,.4));">' if b64 else '<div style="font-size:80px;">⚽</div>'

def top_bar(logged=False,usuario=None):
    now=datetime.now()
    centro="CLUB A. UNIÓN · DATA INTELLIGENCE" if not logged else f"CLUB A. UNIÓN · {AREAS[usuario['area']]['icon']} {usuario['area'].upper()}"
    st.markdown(f"""<div class="top-bar">
        <div class="top-card"><small>Fecha</small><span class="local-date">{now.strftime('%d/%m/%Y')}</span></div>
        <div class="top-bar-center">{centro}</div>
        <div class="top-card"><small>Hora</small><span class="local-time">{now.strftime('%H:%M')}</span></div>
        <div class="top-card"><small>Sede</small>Santa Fe, ARG</div>
    </div><div class="spacer-top"></div>
    <script>(function(){{function u(){{var n=new Date(),h=String(n.getHours()).padStart(2,'0'),m=String(n.getMinutes()).padStart(2,'0');document.querySelectorAll('.local-time').forEach(e=>e.textContent=h+':'+m);var d=String(n.getDate()).padStart(2,'0'),mo=String(n.getMonth()+1).padStart(2,'0'),y=n.getFullYear();document.querySelectorAll('.local-date').forEach(e=>e.textContent=d+'/'+mo+'/'+y);}}u();setInterval(u,10000);}})();</script>""",unsafe_allow_html=True)

def _pdf_ctx():
    return st.session_state.setdefault("_pdfc", {"kpis": [], "tablas": [], "notas": None,
                                                 "titulo": "Informe", "sub": "", "last": None})

def _pdf_title_track(body):
    """Guarda el ultimo titulo de seccion renderizado para nombrar las tablas del PDF."""
    try:
        if not isinstance(body, str) or "class=" not in body: return
        m = re.search(r'class="(?:sec-title|subsec)"[^>]*>(.*?)</div>', body, re.S)
        if m:
            txt = re.sub(r"<[^>]+>", "", m.group(1))
            txt = re.sub(r"[^\w\sáéíóúÁÉÍÓÚñÑ%/·.\-]", "", txt).strip()
            if txt: _pdf_ctx()["last"] = txt[:60]
    except Exception:
        pass

def pdf_add_tabla(titulo, df):
    """Registra una tabla para el PDF de la pagina actual."""
    try:
        if df is None or len(df) == 0: return
        c = _pdf_ctx()
        t = (titulo or c.get("last") or f"Detalle {len(c['tablas'])+1}")
        if any(t == x[0] for x in c["tablas"]):
            t = f"{t} ({len(c['tablas'])+1})"
        c["tablas"].append((t, df.copy()))
    except Exception:
        pass

def pdf_add_kpi(label, value):
    try:
        c = _pdf_ctx()
        lab = re.sub(r"[^\w\s%/.\-áéíóúÁÉÍÓÚñÑ]", "", str(label)).strip()
        if lab and not any(lab == k for k, _ in c["kpis"]):
            c["kpis"].append((lab, value))
    except Exception:
        pass

_PDF_PATCHED = False

def _pdf_patch_streamlit():
    """Intercepta st.metric / col.metric y st.markdown UNA sola vez por PROCESO
    (no por sesion: si no, una sesion nueva volveria a envolver lo ya envuelto y
    las metricas se registrarian duplicadas)."""
    global _PDF_PATCHED
    if _PDF_PATCHED: return
    try:
        from streamlit.delta_generator import DeltaGenerator
        _om = DeltaGenerator.metric
        def _metric(self, label, value, *a, **k):
            pdf_add_kpi(label, value)
            return _om(self, label, value, *a, **k)
        DeltaGenerator.metric = _metric
        _omd = DeltaGenerator.markdown
        def _md(self, body, *a, **k):
            _pdf_title_track(body)
            return _omd(self, body, *a, **k)
        DeltaGenerator.markdown = _md
        _st_metric = st.metric
        def _stm(label, value, *a, **k):
            pdf_add_kpi(label, value)
            return _st_metric(label, value, *a, **k)
        st.metric = _stm
        _st_md = st.markdown
        def _stmd(body, *a, **k):
            _pdf_title_track(body)
            return _st_md(body, *a, **k)
        st.markdown = _stmd
        _PDF_PATCHED = True
    except Exception:
        _PDF_PATCHED = True

def pdf_btn(titulo=None, subtitulo="", kpis=None, tablas=None, notas=None, key=None):
    """Coloca un placeholder arriba de la pagina. El PDF se arma al final del render
    (_pdf_flush) con TODAS las tablas y metricas que la pagina haya generado.
    Antes se llamaba pdf_btn() sin datos y el PDF salia 'SIN DATOS EXPORTABLES'."""
    nombres={"home":"Inicio","historial":"Historial de Jugadores","estadisticas_medicas":"Estadisticas Medicas",
             "evaluaciones":"Evaluaciones Fisicas","riesgo_lesion":"Riesgo de Lesion",
             "demandas_fisicas":"Demandas Fisicas","control_partidos":"Control de Partidos",
             "nutricion":"Control Nutricional","resumen_individual":"Resumen Individual","admin":"Panel Admin"}
    pag=st.session_state.get("pagina","home")
    u=st.session_state.get("usuario") or {}
    _pdf_patch_streamlit()
    st.session_state["_pdfc"] = {
        "kpis": list(kpis or []), "tablas": list(tablas or []), "notas": notas,
        "titulo": titulo or nombres.get(pag,"Informe"),
        "sub": subtitulo or f"Club A. Union - {u.get('area','')} - {u.get('nombre','')}",
        "last": None, "key": key or pag}
    st.session_state["_pdf_ph"] = st.empty()

def _pdf_flush():
    """Genera el PDF con lo recolectado y lo publica en el placeholder."""
    ph = st.session_state.get("_pdf_ph")
    c = st.session_state.get("_pdfc")
    if ph is None or not c: return
    try:
        data = pdf_export.generar_pdf(c["titulo"], c["sub"], c["kpis"], c["tablas"],
                                      c["notas"], escudo=ASSETS/"escudo_union.png")
        fname = f"{c['titulo'].lower().replace(' ','_')}_{datetime.now():%Y%m%d_%H%M}.pdf"
        with ph.container():
            st.markdown(pdf_export._CSS_BTN, unsafe_allow_html=True)
            _a, _b = st.columns([5, 1])
            with _b:
                st.download_button("📄 PDF", data=data, file_name=fname,
                                   mime="application/pdf", use_container_width=True,
                                   key=f"pdfdl_{c.get('key','p')}")
    except Exception as e:
        try: ph.warning(f"No se pudo generar el PDF: {e}")
        except Exception: pass
    finally:
        st.session_state["_pdf_ph"] = None

def no_data(n):
    st.markdown(f'<div style="background:rgba(200,16,46,0.07);border:1px dashed rgba(200,16,46,0.3);border-radius:12px;padding:24px;text-align:center;color:#64748b;">⚠️ No se pudo cargar <b style="color:#f87171;">{n}</b>.<br><small>Hacé la hoja pública: Compartir → Cualquiera con el vínculo → Lector.</small></div>',unsafe_allow_html=True)

def jug_col_find(df):
    for c in df.columns:
        if c.upper() in ["JUG","JUGADOR","NAME","PLAYER","ATLETA","NOMBRE"]: return c
    for c in df.columns:
        if any(x in c.lower() for x in ["jug","name","player","atleta"]): return c
    return df.columns[0]

def pos_col_find(df):
    for c in df.columns:
        if c.upper() in ["POS","POSICION","POSICIÓN","POSITION"]: return c
    return None

def plotly_dark(fig,h=300):
    # Leyendas y ejes en blanco: el gris #64748b era ilegible sobre el fondo azul.
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=20,b=0),height=h,font=dict(color="#ffffff",size=12),
        legend=dict(bgcolor="rgba(8,18,38,0.75)",bordercolor="rgba(255,255,255,0.15)",
                    borderwidth=1,font=dict(color="#ffffff",size=11)))
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)",color="#ffffff",
                     title_font=dict(color="#ffffff"),tickfont=dict(color="#e2e8f0"))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)",color="#ffffff",
                     title_font=dict(color="#ffffff"),tickfont=dict(color="#e2e8f0"))
    fig.update_annotations(font_color="#ffffff")
    return fig


def html_table(df, highlight_cols=None, num_format=None, max_rows=15, height=420, max_cols=14):
    """max_rows/max_cols RECORTAN de verdad los datos enviados al browser. Antes max_rows solo
    decidia el CSS de scroll pero se renderizaban TODAS las filas: con la hoja GPS completa
    (miles de filas x 60 cols) eso generaba ~250 MB de HTML -> MessageSizeError."""
    if df is None or df.empty:
        st.info("Sin datos."); return
    try: pdf_add_tabla(None, df)
    except Exception: pass
    _tf, _tc = len(df), len(df.columns)
    if _tc > max_cols: df = df[list(df.columns)[:max_cols]]
    if _tf > max_rows: df = df.head(max_rows)
    highlight_cols = highlight_cols or []
    num_format = num_format or {}
    
    # Calcular rangos para escala de color por columna
    col_ranges = {}
    for col in highlight_cols:
        if col in df.columns:
            vals = pd.to_numeric(df[col].astype(str).str.replace(",","."), errors="coerce").dropna()
            if len(vals) > 1:
                col_ranges[col] = (vals.min(), vals.max())

    def cell_color(col, val):
        if col not in col_ranges: return ""
        try:
            v = float(str(val).replace(",","."))
            mn, mx = col_ranges[col]
            if mx == mn: return "background:#1a3a6e;color:#fff"
            ratio = (v - mn) / (mx - mn)
            # Verde alto → Rojo bajo
            r = int(220 * (1 - ratio) + 20 * ratio)
            g = int(80 * (1 - ratio) + 180 * ratio)
            b = int(60 * (1 - ratio) + 60 * ratio)
            luminance = 0.299*r + 0.587*g + 0.114*b
            txt = "#fff" if luminance < 140 else "#000"
            return f"background:rgb({r},{g},{b});color:{txt};font-weight:700"
        except: return ""

    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col in df.columns:
            val = row[col]
            fmt = num_format.get(col, "")
            try:
                fval = float(str(val).replace(",","."))
                display = f"{fval:{fmt}}" if fmt else (f"{fval:.1f}" if fval != int(fval) else f"{int(fval)}")
            except:
                display = str(val) if str(val) not in ["nan","None","<NA>"] else "—"
            style = cell_color(col, val)
            cells += f'<td style="text-align:center;padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.05);white-space:nowrap;{style}">{display}</td>'
        rows_html += f"<tr>{cells}</tr>"

    headers = ""
    for col in df.columns:
        headers += f'<th style="text-align:center;padding:10px 14px;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#60a5fa;background:rgba(26,90,180,0.25);border-bottom:2px solid rgba(26,90,180,0.4);white-space:nowrap;">{col}</th>'

    scroll_y = f"overflow-y:auto;max-height:{height}px;" if len(df) > max_rows else "overflow-y:auto;"
    st.markdown(f'''
    <div style="background:#071428;border:1px solid rgba(26,90,180,0.3);border-radius:14px;overflow:hidden;margin-top:8px;">
        <div style="{scroll_y}overflow-x:auto;width:100%;">
        <table style="width:max-content;min-width:100%;border-collapse:collapse;">
            <thead><tr style="position:sticky;top:0;z-index:2;">{headers}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
    </div>''', unsafe_allow_html=True)
    if _tf > max_rows or _tc > max_cols:
        st.caption(f"Mostrando {min(max_rows,_tf)} de {_tf} filas y {min(max_cols,_tc)} de {_tc} columnas (vista optimizada).")

def filtro_anio_widget(df, key):
    """Filtro multiselect de año. Retorna df filtrado."""
    if "AÑO" not in df.columns: return df, []
    anios = sorted([int(a) for a in df["AÑO"].dropna().unique() if int(a) > 1900], reverse=True)
    sel = st.multiselect("📅 Año(s)", [str(a) for a in anios],
                         default=[], key=f"anio_{key}",
                         placeholder="Todos los años")
    if sel:
        sel_int = [int(s) for s in sel]
        return df[df["AÑO"].isin(sel_int)], sel
    return df, []


# ══════════════════════════════════════════════════════════════
# KPI CARD con máx/min/prom contextual
# ══════════════════════════════════════════════════════════════
def kpi_card_contextual(label, val_jug, ref_df, col, unidad=""):
    """
    Muestra tarjeta KPI con:
    - Grande: valor del jugador seleccionado (o promedio general si Todos)
    - Abajo: min (rojo) y promedio (amarillo) del grupo de referencia (posición o todos)
    """
    vals = to_num_col(ref_df[col]).dropna() if col in ref_df.columns else pd.Series(dtype=float)
    ref_min = f"{vals.min():.1f}{unidad}" if len(vals) > 0 else "—"
    ref_avg = f"{vals.mean():.1f}{unidad}" if len(vals) > 0 else "—"

    if val_jug is not None and not pd.isna(val_jug):
        main_val = f"{val_jug:.1f}{unidad}"
    elif len(vals) > 0:
        main_val = f"{vals.mean():.1f}{unidad}"
    else:
        main_val = "—"

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-main">{main_val}</div>
        <div class="kpi-ref">
            <div class="kpi-ref-item">
                <div class="kpi-ref-val" style="color:#f87171;">{ref_min}</div>
                <div class="kpi-ref-label" style="color:#f87171;">MIN POS</div>
            </div>
            <div class="kpi-ref-item">
                <div class="kpi-ref-val" style="color:#fbbf24;">{ref_avg}</div>
                <div class="kpi-ref-label" style="color:#fbbf24;">PROM POS</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

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
                    if u: st.session_state.logged=True;st.session_state.usuario={**u,"username":us};st.session_state.pagina="home";st.rerun()
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
                st.success(f"✅ Solicitud enviada para **{rn}**.")
    with t3:
        st.markdown("### 🔑 Recuperación de contraseña")
        st.info(f"Contactá al administrador en **futbolprofesionalcau@gmail.com**")
        rm=st.text_input("Email",key="rm",placeholder="tu@email.com")
        ru2=st.text_input("Usuario",key="ru2",placeholder="Ej: juan.perez")
        if st.button("Solicitar",use_container_width=True,key="btn_rec"):
            if rm and "@" in rm and ru2: st.success("✅ Solicitud registrada.")
            else: st.error("Completá email y usuario.")

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def render_sidebar():
    u=st.session_state.usuario
    with st.sidebar:
        b64=img_b64(ASSETS/"escudo_union.png")
        esc=f'<img src="data:image/png;base64,{b64}" style="width:56px;height:56px;object-fit:contain;filter:drop-shadow(0 0 10px rgba(200,16,46,.5));">' if b64 else "⚽"
        st.markdown(f'<div style="text-align:center;padding:14px 0 12px;border-bottom:1px solid rgba(200,16,46,.25);margin-bottom:14px;">{esc}<div style="font-family:\'Bebas Neue\',sans-serif;font-size:16px;letter-spacing:3px;margin-top:8px;color:#fff;">CAU · UNIÓN</div><div style="font-size:12px;color:#f87171;margin-top:3px;">{AREAS[u["area"]]["icon"]} {u["nombre"]}</div><div style="font-size:10px;color:#475569;margin-top:2px;">{u["rol"]} · {u["area"]}</div></div>',unsafe_allow_html=True)
        st.markdown('<p style="font-size:10px;letter-spacing:3px;color:#475569;text-transform:uppercase;margin:0 0 8px;">MENÚ</p>',unsafe_allow_html=True)
        for key,icon,label in [("home","🏠","Inicio"),("historial","👤","Historial Jugadores"),("estadisticas_medicas","🏥","Estadísticas Médicas"),("evaluaciones","⚡","Evaluaciones Físicas"),("riesgo_lesion","🤖","Riesgo de Lesión"),("demandas_fisicas","📡","Demandas Físicas"),("control_partidos","⚽","Control de Partidos"),("nutricion","🥗","Control Nutricional"),("resumen_individual","📄","Resumen Individual")]:
            if tiene_acceso(u,key):
                if st.button(f"{icon}  {label}",key=f"nav_{key}",use_container_width=True):
                    st.session_state.pagina=key;st.rerun()
        if tiene_acceso(u,"admin"):
            st.markdown("---")
            pn=sum(1 for d in st.session_state.usuarios_extra.values() if not d.get("aprobado"))
            if st.button(f"🔧  Panel Admin {'🔴' if pn else ''}",key="nav_admin",use_container_width=True):
                st.session_state.pagina="admin";st.rerun()
        st.markdown("---")
        if st.button("🚪  Cerrar sesión",use_container_width=True,key="btn_out"):
            st.session_state.logged=False;st.session_state.usuario=None;st.session_state.pagina="home";st.rerun()

# ══════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════
def pagina_home():
    u=st.session_state.usuario
    try:
        _g=cargar_sheet("gps");_l=cargar_sheet("lesiones");_j=cargar_sheet("historial")
        _kp=[("Jugadores",_j[jug_col_find(_j)].nunique() if not _j.empty else "-"),
             ("Registros medicos",len(_l) if not _l.empty else "-"),
             ("Sesiones GPS",len(_g) if not _g.empty else "-"),
             ("Fecha",date.today().strftime("%d/%m/%Y"))]
    except Exception:
        _kp=None
    pdf_btn(kpis=_kp,notas="Resumen general del plantel - Plataforma CAU Data Intelligence.")
    st.markdown(f'<div style="text-align:center;padding:24px 20px 12px;">{escudo_tag(120)}<div style="font-family:\'Bebas Neue\',sans-serif;font-size:56px;letter-spacing:6px;color:#fff;line-height:1;margin-top:12px;">CLUB A. UNIÓN</div><div style="color:#c8102e;font-size:12px;font-weight:700;letter-spacing:4px;text-transform:uppercase;margin-top:6px;">Data Intelligence · Rendimiento Físico</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    cf,ct=st.columns([1,2],gap="large")
    with cf:
        foto=img_b64(ASSETS/"foto_home.jpg")
        if foto: st.markdown(f'<img src="data:image/jpeg;base64,{foto}" style="width:100%;border-radius:16px;border:2px solid rgba(200,16,46,.3);">',unsafe_allow_html=True)
        else: st.markdown('<div style="aspect-ratio:4/3;background:rgba(200,16,46,.06);border:2px dashed rgba(200,16,46,.25);border-radius:16px;display:flex;align-items:center;justify-content:center;color:#475569;font-size:13px;text-align:center;padding:20px;">📷 Subí la foto como<br><code>assets/foto_home.jpg</code></div>',unsafe_allow_html=True)
    with ct:
        st.markdown('<div style="background:rgba(8,18,38,0.95);border:1px solid rgba(200,16,46,.2);border-radius:16px;padding:28px 32px;height:100%;box-sizing:border-box;"><div style="font-size:10px;color:#c8102e;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">Plataforma Tecnológica</div><div style="font-size:26px;font-weight:900;color:#fff;margin-bottom:16px;line-height:1.2;">Data Intelligence aplicada al rendimiento deportivo</div><div style="font-size:14px;color:#94a3b8;line-height:1.8;">Una plataforma centralizada que transforma datos físicos, médicos y tácticos en inteligencia accionable para el cuerpo técnico, el área médica y la secretaría técnica del Club A. Unión.<br><br>Desde el GPS en el campo hasta el modelo de riesgo de lesión con Machine Learning — toda la información del plantel en un solo lugar, en tiempo real.</div><div style="display:flex;gap:8px;margin-top:18px;flex-wrap:wrap;"><span class="chip">📡 GPS</span><span class="chip">🤖 Machine Learning</span><span class="chip">🏥 Gestión médica</span><span class="chip">📊 Reportes PDF</span><span class="chip">⚡ CMJ · Nórdico · VBT</span><span class="chip">⚽ API Fútbol</span></div></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sec-title">Resumen del plantel</div>',unsafe_allow_html=True)
    try:
        gps=cargar_sheet("gps");les=cargar_sheet("lesiones");jug=cargar_sheet("historial")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("👥 Jugadores",jug[jug_col_find(jug)].nunique() if not jug.empty else "—")
        c2.metric("🏥 Registros médicos",len(les) if not les.empty else "—")
        c3.metric("📡 Sesiones GPS",len(gps) if not gps.empty else "—")
        c4.metric("📅 Hoy",date.today().strftime("%d/%m/%Y"))
    except:
        c1,c2,c3,c4=st.columns(4)
        for c,l in zip([c1,c2,c3,c4],["👥 Jugadores","🏥 Médicos","📡 GPS","📅 Hoy"]): c.metric(l,"—")
    st.markdown(f'<div style="background:rgba(200,16,46,.07);border:1px solid rgba(200,16,46,.2);border-radius:14px;padding:18px 24px;margin-top:16px;"><div style="font-size:10px;color:#c8102e;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Sesión activa</div><div style="font-size:20px;font-weight:800;color:#fff;margin:4px 0 4px;">{u["nombre"]} · {u["rol"]}</div><div style="font-size:13px;color:#94a3b8;">Área: <b style="color:#e2e8f0;">{u["area"]}</b> | Acceso a <b style="color:#e2e8f0;">{len(AREAS[u["area"]]["secciones"])}</b> secciones</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HISTORIAL JUGADORES
# ══════════════════════════════════════════════════════════════
def pagina_historial():
    st.markdown('<div class="sec-title">👤 Historial de Jugadores</div>',unsafe_allow_html=True)
    pdf_btn()
    df=cargar_sheet("historial")
    if df.empty: no_data("Historial de Jugadores"); return

    jcol=jug_col_find(df)
    pos_col=pos_col_find(df)
    foto_col=next((c for c in df.columns if any(x in c.lower() for x in ["foto","url","imagen","photo"])),None)
    perfil_col=next((c for c in df.columns if any(x in c.lower() for x in ["perfil","pierna","lado"])),None)
    nac_col=next((c for c in df.columns if any(x in c.lower() for x in ["fecha_nac","fecha nac","nacimiento"])),None)
    edad_col=next((c for c in df.columns if "edad" in c.lower() or c.upper()=="AGE"),None)
    nacio_col=next((c for c in df.columns if any(x in c.lower() for x in ["nacion","pais","country"])),None)

    # Agrupar posiciones por jugador
    def agrupar(df):
        result=[]
        for nombre,grupo in df.groupby(jcol,as_index=False):
            row=grupo.iloc[0].copy()
            if pos_col: row["_posiciones"]=" / ".join(grupo[pos_col].dropna().astype(str).unique().tolist())
            else: row["_posiciones"]="—"
            result.append(row)
        return pd.DataFrame(result)

    df_agrup=agrupar(df)

    st.markdown('<div class="filter-bar">',unsafe_allow_html=True)
    fc1,fc2,fc3,fc4=st.columns(4)
    with fc1: buscar=st.text_input("🔍 Buscar",placeholder="Nombre...",key="hist_buscar")
    with fc2:
        todas_pos=["Todas"]+(sorted(df[pos_col].dropna().astype(str).unique().tolist()) if pos_col else [])
        pos_sel=st.selectbox("Posición",todas_pos,key="hist_pos")
    with fc3: dfa,_=filtro_anio_widget(df,"hist")
    with fc4: vista=st.radio("Vista",["🃏 Cards","📋 Tabla"],horizontal=True,key="hist_vista")
    st.markdown('</div>',unsafe_allow_html=True)

    dff=df_agrup.copy()
    if buscar: dff=dff[dff[jcol].astype(str).str.contains(buscar,case=False,na=False)]
    if pos_sel!="Todas" and pos_col: dff=dff[dff["_posiciones"].str.contains(pos_sel,case=False,na=False)]

    st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:12px;"><b style="color:#f87171;">{len(dff)}</b> jugadores</div>',unsafe_allow_html=True)

    if "📋 Tabla" in vista:
        cols_show=[jcol,"_posiciones"]+[c for c in [perfil_col,nac_col,edad_col,nacio_col] if c and c in dff.columns]
        tbl=dff[cols_show].rename(columns={"_posiciones":"Posiciones"}).reset_index(drop=True)
        # Estilo de tabla
        html_table(tbl)
    else:
        cols_grid=st.columns(3)
        for i,(_,row) in enumerate(dff.iterrows()):
            with cols_grid[i%3]:
                nombre=str(row[jcol])
                posiciones=str(row.get("_posiciones","—"))
                nac=str(row[nac_col]) if nac_col and nac_col in row.index and str(row[nac_col]) not in ["nan","None","<NA>"] else "—"
                edad=str(row[edad_col]) if edad_col and edad_col in row.index and str(row[edad_col]) not in ["nan","None","<NA>"] else "—"
                nacio=str(row[nacio_col]) if nacio_col and nacio_col in row.index and str(row[nacio_col]) not in ["nan","None","<NA>"] else "—"
                perfil=str(row[perfil_col]) if perfil_col and perfil_col in row.index and str(row[perfil_col]) not in ["nan","None","<NA>"] else "—"
                foto_url=str(row[foto_col]) if foto_col and foto_col in row.index else "nan"
                avatar=f'<img src="{foto_url}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;border:2px solid rgba(200,16,46,.4);">' if foto_url.startswith("http") else '<div style="width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,rgba(200,16,46,.2),rgba(200,16,46,.05));display:flex;align-items:center;justify-content:center;font-size:24px;border:2px solid rgba(200,16,46,.2);">👤</div>'
                pos_chips="".join([f'<span class="chip">{p.strip()}</span>' for p in posiciones.split("/")])
                perf_class="chip-blue" if "IZQ" in perfil.upper() else "chip-green"
                st.markdown(f'<div class="player-card"><div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">{avatar}<div style="flex:1;min-width:0;"><div style="font-size:15px;font-weight:800;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{nombre}</div><div style="margin-top:4px;">{pos_chips}</div></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px;"><div style="color:#64748b;">🎂 Nac: <b style="color:#94a3b8;">{nac}</b></div><div style="color:#64748b;">📅 Edad: <b style="color:#94a3b8;">{edad}</b></div><div style="color:#64748b;">🌍 País: <b style="color:#94a3b8;">{nacio}</b></div><div style="color:#64748b;">🦵 Perfil: <span class="{perf_class}" style="font-size:10px;padding:1px 7px;">{perfil}</span></div></div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ESTADÍSTICAS MÉDICAS
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# FIGURA HUMANA SVG — mapeo de lesiones
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# FIGURA HUMANA — imagen real con puntos superpuestos
# ══════════════════════════════════════════════════════════════
import re as _re

MUSCULO_A_ZONA = {
    "ISQUIOTIBIAL":              "muslo_post",
    "CUADRICEPS":                "muslo_ant",
    "RECTO ANTERIOR CUADRICEPS": "muslo_ant",
    "RECTO ANTERIOR":            "muslo_ant",
    "TENDON CUADRICIPITAL":      "rodilla",
    "TENDON ROTULIANO":          "rodilla",
    "ROTULA":                    "rodilla",
    "ADUCTOR":                   "muslo_int",
    "PECTINEO":                  "muslo_int",
    "OBTURADOR":                 "muslo_int",
    "TRAYECTO INGLE":            "muslo_int",
    "GLUTEO":                    "gluteo",
    "TFL":                       "gluteo",
    "ILIOPSOAS":                 "cadera",
    "MENISCO":                   "rodilla",
    "LCA":                       "rodilla",
    "LLI":                       "rodilla",
    "PATA DE GANZO":             "rodilla",
    "RODILLA":                   "rodilla",
    "GEMELO":                    "pierna",
    "GEMELOS":                   "pierna",
    "SOLEO":                     "pierna",
    "SARTORIO":                  "muslo_ant",
    "TIBIAL POSTERIOR":          "pierna",
    "TIBIAL ANT":                "pierna",
    "TIBIA":                     "pierna",
    "PERONEOS":                  "pierna",
    "TENDON PERONEO":            "pierna",
    "AQUILES":                   "tobillo",
    "LIGAMENTO EXTERNO":         "tobillo",
    "PIE":                       "pie",
    "SESAMOIDEO":                "pie",
    "PUBIS":                     "pubis",
    "TENDON DEL PUBIS":          "pubis",
    "PERINE":                    "pubis",
    "RECTO ABDOMEN":             "abdomen",
    "LUMBARES":                  "lumbar",
    "SUB ESCAPULAR":             "hombro",
    "HOMBRO":                    "hombro",
    "MUÑECA":                    "antebrazo",
    "PARPADO":                   "cabeza",
    "MAXILAR":                   "cabeza",
    "NARIZ":                     "cabeza",
    "CABEZA":                    "cabeza",
}

REGION_A_ZONA = {
    "MUSLO ANTERIOR":  "muslo_ant",
    "MUSLO POSTERIOR": "muslo_post",
    "MUSLO INTERNO":   "muslo_int",
    "MUSLO EXTERNO":   "muslo_ext",
    "RODILLA":         "rodilla",
    "PIERNA":          "pierna",
    "TOBILLO":         "tobillo",
    "TOBILLO Y PIE":   "tobillo",
    "PIE":             "pie",
    "PUBIS":           "pubis",
    "ABDOMEN":         "abdomen",
    "LUMBAR":          "lumbar",
    "GLUTEO":          "gluteo",
    "HOMBRO":          "hombro",
    "CADERA":          "cadera",
    "CABEZA":          "cabeza",
    "CARA":            "cabeza",
    "ANTE BRAZO":      "antebrazo",
}

# Coordenadas (x%, y%) sobre la imagen hb.png (400x350)
# Frontal: 0-50% del ancho | Posterior: 50-100% del ancho
# DER del cuerpo = izquierda de la figura frontal (~19-20%)
# IZQ del cuerpo = derecha de la figura frontal (~30-31%)
ZONA_COORDS = {
    "cabeza":         {"der": (25.0, 6.5),   "izq": (25.0, 6.5)},
    "hombro_der":     {"der": (14.5, 23.0),  "izq": None},
    "hombro_izq":     {"izq": (36.0, 23.0),  "der": None},
    "abdomen":        {"der": (25.0, 42.0),  "izq": (25.0, 42.0)},
    "pubis":          {"der": (25.0, 57.0),  "izq": (25.0, 57.0)},
    "cadera_der":     {"der": (17.5, 60.5),  "izq": None},
    "cadera_izq":     {"izq": (32.5, 60.5),  "der": None},
    "muslo_ant_der":  {"der": (19.5, 68.5),  "izq": None},
    "muslo_ant_izq":  {"izq": (30.5, 68.5),  "der": None},
    "muslo_int_der":  {"der": (23.0, 71.0),  "izq": None},
    "muslo_int_izq":  {"izq": (27.0, 71.0),  "der": None},
    "rodilla_der":    {"der": (19.5, 82.0),  "izq": None},
    "rodilla_izq":    {"izq": (30.5, 82.0),  "der": None},
    "pierna_der":     {"der": (19.0, 91.0),  "izq": None},
    "pierna_izq":     {"izq": (31.0, 91.0),  "der": None},
    "tobillo_der":    {"der": (18.5, 97.5),  "izq": None},
    "tobillo_izq":    {"izq": (31.5, 97.5),  "der": None},
    "pie_der":        {"der": (18.0, 99.5),  "izq": None},
    "pie_izq":        {"izq": (32.0, 99.5),  "der": None},
    "antebrazo_der":  {"der": (10.5, 51.0),  "izq": None},
    "antebrazo_izq":  {"izq": (39.5, 51.0),  "der": None},
    # POSTERIOR (columna derecha de la imagen)
    "lumbar":         {"der": (75.0, 43.0),  "izq": (75.0, 43.0)},
    "gluteo_der":     {"der": (71.5, 61.0),  "izq": None},
    "gluteo_izq":     {"izq": (78.5, 61.0),  "der": None},
    "muslo_post_der": {"der": (71.0, 70.5),  "izq": None},
    "muslo_post_izq": {"izq": (79.0, 70.5),  "der": None},
    "muslo_ext_der":  {"der": (68.0, 68.5),  "izq": None},
    "muslo_ext_izq":  {"izq": (82.0, 68.5),  "der": None},
}

def parsear_muscl_id(muscl_id: str) -> tuple:
    if not muscl_id or str(muscl_id).upper() in ["NO-MUSC","NO MUSC","NA","NAN","—",""]:
        return None, None
    s = str(muscl_id).strip().upper()
    lado = "bilat"
    if s.endswith(" DER"):   lado = "der"; s = s[:-4].strip()
    elif s.endswith(" IZQ"): lado = "izq"; s = s[:-4].strip()
    elif s.endswith(" BILAT"): lado = "bilat"; s = s[:-6].strip()
    zona = None
    for key, z in MUSCULO_A_ZONA.items():
        if s == key or s.startswith(key):
            zona = z; break
    if not zona:
        for key, z in MUSCULO_A_ZONA.items():
            if key in s:
                zona = z; break
    return zona, lado

def zonas_con_lado(zona_base: str, lado: str) -> list:
    if not zona_base: return []
    if lado == "der":   return [f"{zona_base}_der"]
    if lado == "izq":   return [f"{zona_base}_izq"]
    return [f"{zona_base}_der", f"{zona_base}_izq"]

def render_cuerpo_humano(df_jugador, region_col):
    """Figura Synoptic con zonas divididas por DER/IZQ coloreadas según lesiones."""
    if df_jugador.empty:
        return

    # ── Calcular zonas afectadas ─────────────────────────────
    zonas_intensidad = {}
    muscl_col = next((c for c in df_jugador.columns if "muscl" in c.lower() or "sist_m" in c.lower()), None)
    lado_col  = next((c for c in df_jugador.columns if c.upper() == "LADO"), None)

    for _, row in df_jugador.iterrows():
        zona, lado = None, None
        if muscl_col:
            zona, lado = parsear_muscl_id(str(row.get(muscl_col, "")))
        if not zona and region_col and region_col in row.index:
            reg = str(row[region_col]).strip().upper()
            zona = REGION_A_ZONA.get(reg)
            if lado_col and lado_col in row.index:
                l = str(row[lado_col]).strip().upper()
                if l in ["DER","DERECHO","R","RIGHT"]:    lado = "der"
                elif l in ["IZQ","IZQUIERDO","L","LEFT"]: lado = "izq"
                else: lado = "bilat"
            else: lado = "bilat"
        if not zona: continue
        for s in zonas_con_lado(zona, lado or "bilat"):
            zonas_intensidad[s] = zonas_intensidad.get(s, 0) + 1

    # ── Mapeo zona_lado → (svg_id, view, side) ───────────────
    # view: front/back | side: der/izq (perspectiva del cuerpo)
    ZONA_SVG_MAP = {
        # FRONTAL
        "muslo_ant_der":  ("Leg Upper",  "front", "der"),
        "muslo_ant_izq":  ("Leg Upper",  "front", "izq"),
        "muslo_int_der":  ("Leg Upper",  "front", "der"),
        "muslo_int_izq":  ("Leg Upper",  "front", "izq"),
        "muslo_ext_der":  ("Leg Upper",  "front", "der"),
        "muslo_ext_izq":  ("Leg Upper",  "front", "izq"),
        "rodilla_der":    ("Knee s ",    "front", "izq"),  # ojo: en SVG frontal rodilla DER está en lado izq imagen
        "rodilla_izq":    ("Knee s ",    "front", "der"),  # y viceversa — ajustado por centroide
        "pierna_der":     ("Leg Lower",  "front", "der"),
        "pierna_izq":     ("Leg Lower",  "front", "izq"),
        "tobillo_der":    ("Ankle",      "front", "der"),
        "tobillo_izq":    ("Ankle",      "front", "izq"),
        "pie_der":        ("Foot",       "front", "der"),
        "pie_izq":        ("Foot",       "front", "izq"),
        "cadera_der":     ("Hip",        "front", "der"),
        "cadera_izq":     ("Hip",        "front", "izq"),
        "abdomen":        ("Abdomen",    "front", "der"),
        "pubis":          ("Abdomen",    "front", "der"),
        "hombro_der":     ("Shoulder s", "front", "der"),
        "hombro_izq":     ("Shoulder s", "front", "izq"),
        "antebrazo_der":  ("Arm Lower",  "front", "der"),
        "antebrazo_izq":  ("Arm Lower",  "front", "izq"),
        "cabeza":         ("Head Soft Tissue", "front", "der"),
        # POSTERIOR
        "muslo_post_der": ("Leg Upper",  "back",  "der"),
        "muslo_post_izq": ("Leg Upper",  "back",  "izq"),
        "gluteo_der":     ("Buttocks",   "back",  "der"),
        "gluteo_izq":     ("Buttocks",   "back",  "izq"),
        "lumbar":         ("Back Lower", "back",  "der"),
        "pierna_post_der":("Leg Lower",  "back",  "der"),
        "pierna_post_izq":("Leg Lower",  "back",  "izq"),
    }

    # Acumular por (svg_id, view, side)
    svg_zonas = {}
    max_v = max(zonas_intensidad.values()) if zonas_intensidad else 1
    for zona, cnt in zonas_intensidad.items():
        mapping = ZONA_SVG_MAP.get(zona)
        if mapping:
            key = mapping  # (id, view, side)
            svg_zonas[key] = svg_zonas.get(key, 0) + cnt

    # ── Cargar SVG ────────────────────────────────────────────
    svg_path = ASSETS / "body_map.svg"
    if not svg_path.exists():
        st.warning("No se encontró assets/body_map.svg")
        return

    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()

    # ── Generar JS para colorear polígonos por id+view+side ──
    max_svg = max(svg_zonas.values()) if svg_zonas else 1
    
    js_coloring = ""
    for (svg_id, view, side), cnt in svg_zonas.items():
        ratio = min(cnt / max_svg, 1.0)
        if ratio < 0.33:
            cls = "lesion-low"
        elif ratio < 0.66:
            cls = "lesion-mid"
        else:
            cls = "lesion-high"
        # Escapar comillas para JS
        safe_id = svg_id.replace('"', '\"')
        js_coloring += f"""
        document.querySelectorAll('polygon[id="{safe_id}"][data-view="{view}"][data-side="{side}"]').forEach(function(el){{
            el.classList.add('{cls}');
        }});"""

    # ── Leyenda ───────────────────────────────────────────────
    leyenda_rows = ""
    if region_col and region_col in df_jugador.columns:
        reg_counts = df_jugador[region_col].dropna().astype(str).str.upper().value_counts().to_dict()
        max_reg = max(reg_counts.values()) if reg_counts else 1
        for region, cnt in sorted(reg_counts.items(), key=lambda x: -x[1]):
            if region not in ["NA","OTRA","NO-MUSC","NAN"]:
                bar_w = int(cnt / max_reg * 100)
                leyenda_rows += f"""
                <div style="margin-bottom:11px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="font-size:12px;color:#e2e8f0;font-weight:500;">{region.title()}</span>
                        <span style="font-size:12px;font-weight:800;color:#f87171;">{cnt}</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.07);border-radius:4px;height:6px;">
                        <div style="width:{bar_w}%;background:linear-gradient(90deg,#c8102e,#f87171);height:6px;border-radius:4px;"></div>
                    </div>
                </div>"""

    total_les = len(df_jugador)
    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#071428; font-family:Inter,sans-serif; padding:10px; }}
  .wrap {{ display:flex; gap:16px; align-items:flex-start; }}
  .svg-box {{ flex:0 0 60%; background:linear-gradient(135deg,#071428,#0d1e3c);
              border-radius:14px; border:1px solid rgba(26,90,180,0.3); padding:8px; overflow:hidden; }}
  .ley-box {{ flex:1; padding-top:4px; }}
  .ley-title {{ font-size:10px; color:#60a5fa; font-weight:700; letter-spacing:2px;
                text-transform:uppercase; margin-bottom:10px;
                border-bottom:1px solid rgba(26,90,180,0.3); padding-bottom:6px; }}
  .total-box {{ background:rgba(200,16,46,0.1); border:1px solid rgba(200,16,46,0.3);
                border-radius:10px; padding:10px 14px; margin-bottom:14px; }}
  .total-label {{ font-size:9px; color:#f87171; font-weight:700; letter-spacing:1px; text-transform:uppercase; }}
  .total-val {{ font-size:28px; font-weight:900; color:#fff; line-height:1.1; }}
  .no-lesion {{ color:#475569; font-size:13px; text-align:center; margin-top:20px; }}
  .legend-note {{ font-size:9px; color:#334155; margin-top:12px; letter-spacing:0.5px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="svg-box">
    {svg_content}
  </div>
  <div class="ley-box">
    <div class="ley-title">Regiones afectadas</div>
    {'<div class="total-box"><div class="total-label">Total registros</div><div class="total-val">' + str(total_les) + '</div></div>' if leyenda_rows else ''}
    {leyenda_rows if leyenda_rows else '<div class="no-lesion">Sin lesiones<br>registradas</div>'}
    <div class="legend-note">◀ FRONTAL &nbsp;&nbsp; POSTERIOR ▶</div>
  </div>
</div>
<script>
{js_coloring}
</script>
</body>
</html>"""

    components.html(html_body, height=540, scrolling=False)


def grafico_con_scroll(fig, height=380, max_items=15):
    """Envuelve un gráfico plotly en un div con scroll si tiene muchas categorías."""
    # Calcular altura real necesaria
    actual_height = height
    st.markdown(f'<div style="max-height:{actual_height+40}px;overflow-y:auto;border-radius:10px;">', unsafe_allow_html=True)
    plotly_dark(fig, actual_height)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def pagina_estadisticas_medicas():
    st.markdown('<div class="sec-title">🏥 Estadísticas Médicas</div>',unsafe_allow_html=True)
    pdf_btn()
    df=cargar_sheet("lesiones")
    if df.empty: no_data("Estadísticas Médicas"); return

    jcol=jug_col_find(df)
    pos_col=pos_col_find(df)
    tipo_col=next((c for c in df.columns if c.upper() in ["TIPO","ID_REGISTRO","TYPE"]),None)
    dxt_col=next((c for c in df.columns if "day_off" in c.lower() or ("dias" in c.lower() and "baja" in c.lower())),None) or next((c for c in df.columns if "day" in c.lower() and "off" in c.lower()),None)
    est_col=next((c for c in df.columns if any(x in c.upper() for x in ["CLASIF","EST_M","ESTRUCTURA","MUSCULAR"])),None)
    region_col=next((c for c in df.columns if any(x in c.lower() for x in ["region","zona","localiz","body","parte"])),None)
    lesion_tipo_col=next((c for c in df.columns if any(x in c.lower() for x in ["lesion","desgarro","tipo_les","tipo les"])),None)
    obs_col="OBSERVACIONES" if "OBSERVACIONES" in df.columns else None

    # Filtros — réplica Power BI
    st.markdown('<div class="filter-bar">',unsafe_allow_html=True)
    fc=st.columns(5)
    jugs=["Todas"]+sorted(df[jcol].dropna().astype(str).unique().tolist())
    poss=["Todas"]+(sorted(df[pos_col].dropna().astype(str).unique().tolist()) if pos_col else [])
    tipos=["Todas"]+(sorted(df[tipo_col].dropna().astype(str).unique().tolist()) if tipo_col else [])
    anios_med=sorted([str(int(a)) for a in df["AÑO"].dropna().unique() if int(a)>1900],reverse=True) if "AÑO" in df.columns else []
    obs_vals=["Todas"]+(sorted(df[obs_col].dropna().astype(str).unique().tolist()) if obs_col else [])
    with fc[0]: jsel=st.selectbox("JUG",jugs,key="med_jug")
    with fc[1]: psel=st.selectbox("POS",poss,key="med_pos")
    with fc[2]: tsel=st.selectbox("TIPO",tipos,key="med_tipo")
    with fc[3]: asel=st.multiselect("📅 Año(s)",anios_med,default=[],key="med_anio",placeholder="Todos")
    with fc[4]: osel=st.selectbox("OBS",obs_vals,key="med_obs")
    st.markdown('</div>',unsafe_allow_html=True)

    dff=df.copy()
    if jsel!="Todas": dff=dff[dff[jcol].astype(str)==jsel]
    if psel!="Todas" and pos_col: dff=dff[dff[pos_col].astype(str)==psel]
    if tsel!="Todas" and tipo_col: dff=dff[dff[tipo_col].astype(str)==tsel]
    if asel and "AÑO" in dff.columns: dff=dff[dff["AÑO"].isin([int(a) for a in asel])]
    if osel!="Todas" and obs_col: dff=dff[dff[obs_col].astype(str)==osel]
    les_df=dff[dff[tipo_col].astype(str).str.upper()=="LESION"].copy() if tipo_col else dff.copy()

    # ── Fila 1: tabla incidencias (col izq) + días x año + tipo lesión (col der) ──
    col_izq, col_der = st.columns([1.1, 1.9])

    with col_izq:
        st.markdown('<div class="subsec">Distribución de incidencias</div>',unsafe_allow_html=True)
        if dxt_col:
            dff["_dxt"]=to_num_col(dff[dxt_col])
            grp_cols={"DAY_OFF_DXT":("_dxt","sum"),"N° INC":(jcol,"count")}
            if "AÑO" in dff.columns: grp_cols["AÑOS"]=("AÑO","nunique")
            tabla=dff.groupby(jcol).agg(**grp_cols).reset_index().sort_values("DAY_OFF_DXT",ascending=False)
            html_table(tabla, highlight_cols=["DAY_OFF_DXT","N° INC"], max_rows=20, height=400)
        else:
            tbl=dff[jcol].value_counts().reset_index(); tbl.columns=[jcol,"N°"]
            html_table(tbl, highlight_cols=["N°"], max_rows=20, height=400)

    with col_der:
        # Días perdidos x año (barra horizontal)
        if dxt_col and "AÑO" in les_df.columns:
            st.markdown('<div class="subsec">Días perdidos x incidencias</div>',unsafe_allow_html=True)
            les_df["_dxt"]=to_num_col(les_df[dxt_col])
            por_anio=les_df.groupby("AÑO")["_dxt"].sum().reset_index().sort_values("AÑO")
            por_anio["AÑO"]=por_anio["AÑO"].astype(int).astype(str)
            fig=px.bar(por_anio,x="_dxt",y="AÑO",orientation="h",text="_dxt",
                      color_discrete_sequence=["#4299e1"],template="plotly_dark")
            fig.update_traces(textposition="outside",textfont_color="#fff",
                             texttemplate="%{text:.0f}",marker_color="#4299e1")
            plotly_dark(fig,180)
            st.plotly_chart(fig,use_container_width=True)

        # Días perdidos x tipo lesión (donut) — lado a lado con clasificación
        g1, g2 = st.columns(2)
        with g1:
            if lesion_tipo_col and dxt_col:
                st.markdown('<div class="subsec">Días perdidos x lesión</div>',unsafe_allow_html=True)
                les_df["_dxt"]=to_num_col(les_df[dxt_col])
                por_tipo=les_df.groupby(lesion_tipo_col)["_dxt"].sum().reset_index().sort_values("_dxt",ascending=False)
                total=por_tipo["_dxt"].sum()
                top5=por_tipo.head(5).copy()
                otros_sum=por_tipo.iloc[5:]["_dxt"].sum() if len(por_tipo)>5 else 0
                if otros_sum>0:
                    top5=pd.concat([top5,pd.DataFrame([{lesion_tipo_col:"Otros","_dxt":otros_sum}])],ignore_index=True)
                # Labels con valor y %
                top5["label"]=top5[lesion_tipo_col].astype(str).str[:20]
                top5["pct_str"]=(top5["_dxt"]/total*100).round(2).astype(str)+"%"
                COLORES_TIPO=["#4299e1","#805ad5","#ed8936","#48bb78","#f56565","#718096"]
                fig2=go.Figure(go.Pie(
                    labels=top5["label"],
                    values=top5["_dxt"],
                    hole=0.55,
                    marker_colors=COLORES_TIPO[:len(top5)],
                    texttemplate="%{value:.0f}<br>(%{percent:.2%})",
                    textposition="outside",
                    textfont_size=10,
                    hovertemplate="<b>%{label}</b><br>Días: %{value:.0f}<extra></extra>"
                ))
                fig2.update_layout(
                    title=dict(text="DÍAS PERDIDOS x LESIÓN",font_size=11,font_color="#94a3b8",x=0.5),
                    legend=dict(orientation="v",x=1.0,y=0.5,font_size=9,bgcolor="rgba(0,0,0,0)"),
                    template="plotly_dark",showlegend=True
                )
                plotly_dark(fig2,240)
                st.plotly_chart(fig2,use_container_width=True)

        with g2:
            if est_col and dxt_col:
                st.markdown('<div class="subsec">Días perdidos x clasificación</div>',unsafe_allow_html=True)
                les_df["_dxt"]=to_num_col(les_df[dxt_col])
                por_est=les_df.groupby(est_col)["_dxt"].sum().reset_index().sort_values("_dxt",ascending=False)
                total_est=por_est["_dxt"].sum()
                COLORS={"MUSCULAR":"#4299e1","ARTICULAR":"#805ad5","OSEA":"#ed8936",
                        "TENDINOSO":"#e53e3e","TENDINOSA":"#f6ad55","NA":"#718096"}
                colors=[COLORS.get(str(v).upper().strip(),"#64748b") for v in por_est[est_col]]
                fig3=go.Figure(go.Pie(
                    labels=por_est[est_col].astype(str),
                    values=por_est["_dxt"],
                    hole=0.55,
                    marker_colors=colors,
                    texttemplate="%{value:.0f}<br>(%{percent:.2%})",
                    textposition="outside",
                    textfont_size=10,
                    hovertemplate="<b>%{label}</b><br>Días: %{value:.0f}<extra></extra>"
                ))
                fig3.update_layout(
                    title=dict(text="DÍAS PERDIDOS x CLASIFICACIÓN LESIÓN",font_size=11,font_color="#94a3b8",x=0.5),
                    legend=dict(orientation="h",x=0.5,y=-0.15,xanchor="center",font_size=9,
                               bgcolor="rgba(0,0,0,0)"),
                    template="plotly_dark"
                )
                plotly_dark(fig3,240)
                st.plotly_chart(fig3,use_container_width=True)

    # ── Fila 2: SIST_M-E (barras verticales) + N° lesiones x región (barras horiz) ──
    st.markdown("---")

    # Columna MUSCL_ID / SIST_M-E
    sist_col = next((c for c in les_df.columns if any(x in c.upper() for x in ["MUSCL","SIST_M","MUSCUL_ID","MUSCL_ID"])), None)
    # Si no existe, buscamos columna que describe músculo
    if not sist_col:
        sist_col = next((c for c in les_df.columns if any(x in c.lower() for x in ["muscl","sist_m","musculo_id"])), None)

    b1, b2 = st.columns(2)

    with b1:
        st.markdown('<div class="subsec">N° lesiones x SIST M-E</div>',unsafe_allow_html=True)
        if sist_col:
            import re as _re
            def base_musculo(v):
                return _re.sub(r'\s+(DER|IZQ|BILAT)$', '', str(v).strip().upper())

            les_sist = les_df[sist_col].dropna().astype(str)
            les_sist = les_sist[~les_sist.str.upper().isin(["NO-MUSC","NO MUSC","NA","—","NAN"])]
            les_sist_base = les_sist.apply(base_musculo)
            vc_s = les_sist_base.value_counts().reset_index()
            vc_s.columns = ["Músculo","N°"]
            vc_s = vc_s.sort_values("N°", ascending=True)  # ascendente para horizontal
            n_s = len(vc_s)
            alto_s = max(300, n_s * 36)
            fig_s = px.bar(vc_s, x="N°", y="Músculo", orientation="h", text="N°",
                          color_discrete_sequence=["#4299e1"], template="plotly_dark")
            fig_s.update_traces(textposition="outside", textfont_color="#fff",
                               marker_color="#4299e1", texttemplate="%{text:.0f}")
            fig_s.update_layout(yaxis=dict(categoryorder="total ascending"),
                               xaxis_title="N°", yaxis_title="")
            # Mostrar solo primeras 15, resto con scroll
            alto_visible = min(alto_s, 500)
            st.markdown(f'<div style="max-height:{alto_visible}px;overflow-y:auto;border-radius:10px;">', unsafe_allow_html=True)
            plotly_dark(fig_s, alto_s)
            st.plotly_chart(fig_s, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No se encontró la columna MUSCL_ID / SIST M-E en los datos.")

    with b2:
        if region_col:
            st.markdown('<div class="subsec">N° lesiones x región</div>',unsafe_allow_html=True)
            vc_r = les_df[region_col].value_counts().reset_index(); vc_r.columns = ["Región","N°"]
            vc_r = vc_r.sort_values("N°", ascending=True)
            n_filas_r = len(vc_r)
            alto_reg = max(300, n_filas_r * 36)
            fig5 = px.bar(vc_r, x="N°", y="Región", orientation="h", text="N°",
                         color_discrete_sequence=["#48bb78"], template="plotly_dark")
            fig5.update_traces(textposition="outside", textfont_color="#fff",
                              marker_color="#48bb78", texttemplate="%{text:.0f}")
            fig5.update_layout(yaxis=dict(categoryorder="total ascending"),
                              xaxis_title="N°", yaxis_title="")
            alto_visible_r = min(alto_reg, 500)
            st.markdown(f'<div style="max-height:{alto_visible_r}px;overflow-y:auto;border-radius:10px;">', unsafe_allow_html=True)
            plotly_dark(fig5, alto_reg)
            st.plotly_chart(fig5, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Figura humana — solo cuando hay jugador seleccionado ──
    if jsel != "Todas" and region_col:
        st.markdown("---")
        st.markdown('<div class="subsec">🫀 Mapa corporal — lesiones de '  + jsel + '</div>',unsafe_allow_html=True)
        df_jug_les = dff[dff[jcol].astype(str) == jsel]
        render_cuerpo_humano(df_jug_les, region_col)

    st.markdown("---")
    st.markdown('<div class="subsec">Registros completos</div>',unsafe_allow_html=True)
    show_dff = dff[[c for c in dff.columns if not c.startswith("_")]].copy()
    hl_cols = [dxt_col] if dxt_col and dxt_col in show_dff.columns else []
    if dxt_col and dxt_col in show_dff.columns:
        show_dff[dxt_col] = to_num_col(show_dff[dxt_col])
    html_table(show_dff, highlight_cols=hl_cols)

# ══════════════════════════════════════════════════════════════
# EVALUACIONES FÍSICAS
# ══════════════════════════════════════════════════════════════
def pagina_evaluaciones():
    st.markdown('<div class="sec-title">⚡ Evaluaciones Físicas</div>',unsafe_allow_html=True)
    pdf_btn()

    tab1,tab2,tab3,tab4=st.tabs(["🦵 CMJ 2PP","🏃 CMJ 1PP","💪 Curl Nórdico","⚡ VBT"])

    # ──────────────────────────────────────────────────────────
    # CMJ 2PP
    # ──────────────────────────────────────────────────────────
    with tab1:
        cmj_img=img_b64(ASSETS/"CMJ.png")
        ci,cd=st.columns([1,3])
        with ci:
            if cmj_img: st.markdown(f'<img src="data:image/png;base64,{cmj_img}" style="width:100%;max-width:180px;border-radius:12px;filter:drop-shadow(0 0 12px rgba(200,16,46,.3));">',unsafe_allow_html=True)
        with cd:
            st.markdown('<div style="background:rgba(8,18,38,.9);border:1px solid rgba(200,16,46,.2);border-radius:12px;padding:16px;"><div style="font-size:14px;font-weight:800;color:#fff;margin-bottom:6px;">CMJ — Counter Movement Jump</div><div style="font-size:12px;color:#94a3b8;line-height:1.6;">Evalúa potencia explosiva del tren inferior. Variables: <b style="color:#e2e8f0;">Altura · ECC PP · RSI-m · Conc Peak Force</b></div></div>',unsafe_allow_html=True)

        df=cargar_sheet("cmj")
        if df.empty: no_data("CMJ")
        else:
            jcol=jug_col_find(df); pos_col=pos_col_find(df)
            # Columnas específicas CMJ
            ALT="Jump Height (Imp-Mom) [cm]"
            ECC="Eccentric Peak Power / BM [W/kg]"
            RSI="RSI-modified [m/s]"
            CPF="Concentric Peak Force / BM [N/kg]"
            BW=next((c for c in df.columns if "bw" in c.lower() and "kg" in c.lower()),None)
            fecha_col=next((c for c in df.columns if "fecha" in c.lower() and "_" not in c),None)

            for col in [ALT,ECC,RSI,CPF]:
                if col in df.columns: df[col]=to_num_col(df[col])

            # Filtros
            st.markdown('<div class="filter-bar">',unsafe_allow_html=True)
            fc1,fc2,fc3=st.columns(3)
            with fc1: dff,_=filtro_anio_widget(df,"cmj")
            with fc2:
                pos_opts=["Todas"]+(sorted(dff[pos_col].dropna().astype(str).unique().tolist()) if pos_col else [])
                pos_sel=st.selectbox("Posición",pos_opts,key="cmj_pos")
                if pos_sel!="Todas" and pos_col: dff=dff[dff[pos_col].astype(str)==pos_sel]
            with fc3:
                jugs=["Todos"]+sorted(dff[jcol].dropna().astype(str).unique().tolist())
                jsel=st.selectbox("Jugador",jugs,key="cmj_jug")
            st.markdown('</div>',unsafe_allow_html=True)

            # Grupo de referencia = posición seleccionada (o todos si no hay filtro)
            ref_df=dff.copy()
            jug_vals={}
            if jsel!="Todos":
                jug_df=dff[dff[jcol].astype(str)==jsel]
                for col in [ALT,ECC,RSI,CPF]:
                    if col in jug_df.columns:
                        vals=jug_df[col].dropna()
                        jug_vals[col]=vals.iloc[-1] if len(vals)>0 else None  # último registro

            # KPI Cards
            st.markdown('<div class="subsec">Métricas principales</div>',unsafe_allow_html=True)
            k1,k2,k3,k4=st.columns(4)
            with k1: kpi_card_contextual("ALTURA CMJ (cm)", jug_vals.get(ALT) if jug_vals else None, ref_df, ALT)
            with k2: kpi_card_contextual("ECC PEAK POWER (W/kg)", jug_vals.get(ECC) if jug_vals else None, ref_df, ECC)
            with k3: kpi_card_contextual("RSI-modified (m/s)", jug_vals.get(RSI) if jug_vals else None, ref_df, RSI)
            with k4: kpi_card_contextual("CONC PEAK FORCE (N/kg)", jug_vals.get(CPF) if jug_vals else None, ref_df, CPF)

            # Gráfico evolución temporal
            if fecha_col and ALT in dff.columns:
                st.markdown('<div class="subsec">Evolución temporal</div>',unsafe_allow_html=True)
                dff2=dff.copy()
                dff2["_f"]=pd.to_datetime(dff2[fecha_col],dayfirst=True,errors="coerce")
                dff2=dff2.dropna(subset=["_f",ALT]).sort_values("_f")
                plot_df=dff2[dff2[jcol].astype(str)==jsel] if jsel!="Todos" else dff2
                if not plot_df.empty:
                    fig=px.line(plot_df,x="_f",y=ALT,color=jcol if jsel=="Todos" else None,
                               markers=True,template="plotly_dark",
                               labels={"_f":"Fecha",ALT:"Altura CMJ (cm)"})
                    fig.update_traces(line_color="#c8102e",marker_color="#fff",marker_size=8)
                    plotly_dark(fig,300)
                    st.plotly_chart(fig,use_container_width=True)

            # Tabla con escala de colores
            st.markdown('<div class="subsec">Tabla de resultados</div>',unsafe_allow_html=True)
            show_cols=[jcol]+([pos_col] if pos_col else [])+[c for c in [ALT,ECC,RSI,CPF] if c in dff.columns]
            if fecha_col: show_cols=[fecha_col]+show_cols
            tbl=dff if jsel=="Todos" else dff[dff[jcol].astype(str)==jsel]
            tbl=tbl[[c for c in show_cols if c in tbl.columns]].sort_values(ALT,ascending=False) if ALT in tbl.columns else tbl
            num_cols_tbl=[c for c in [ALT,ECC,RSI,CPF] if c in tbl.columns]
            html_table(tbl.reset_index(drop=True), highlight_cols=num_cols_tbl)

            # Gráfico comparativo barras por jugador
            if ALT in dff.columns and len(dff[jcol].unique())>1:
                st.markdown('<div class="subsec">Comparativa entre jugadores</div>',unsafe_allow_html=True)
                comp=dff.groupby(jcol)[ALT].mean().reset_index().sort_values(ALT,ascending=False)
                fig_bar=px.bar(comp,x=jcol,y=ALT,text=ALT,
                              color=ALT,color_continuous_scale="RdYlGn",template="plotly_dark",
                              labels={jcol:"Jugador",ALT:"Altura promedio (cm)"})
                fig_bar.update_traces(texttemplate="%{text:.1f}",textposition="outside",textfont_color="#fff")
                fig_bar.update_coloraxes(showscale=False)
                fig_bar.update_layout(xaxis_tickangle=-45)
                plotly_dark(fig_bar,320)
                st.plotly_chart(fig_bar,use_container_width=True)

    # ──────────────────────────────────────────────────────────
    # CMJ 1PP
    # ──────────────────────────────────────────────────────────
    with tab2:
        cmj1_img=img_b64(ASSETS/"CMJ1PP.png")
        ci,cd=st.columns([1,3])
        with ci:
            if cmj1_img: st.markdown(f'<img src="data:image/png;base64,{cmj1_img}" style="width:100%;max-width:180px;border-radius:12px;filter:drop-shadow(0 0 12px rgba(200,16,46,.3));">',unsafe_allow_html=True)
        with cd:
            st.markdown('<div style="background:rgba(8,18,38,.9);border:1px solid rgba(200,16,46,.2);border-radius:12px;padding:16px;"><div style="font-size:14px;font-weight:800;color:#fff;margin-bottom:6px;">CMJ 1PP — Una Pierna</div><div style="font-size:12px;color:#94a3b8;line-height:1.6;">Evalúa asimetría entre piernas. Asym >10% indica riesgo. Variables: <b style="color:#e2e8f0;">ALT DER · ALT IZQ · ASYM%</b></div></div>',unsafe_allow_html=True)

        df=cargar_sheet("cmj1pp")
        if df.empty: no_data("CMJ 1 Pierna")
        else:
            jcol=jug_col_find(df); pos_col=pos_col_find(df)
            L_COL="Jump Height (Imp-Mom) [cm] (L)"
            R_COL="Jump Height (Imp-Mom) [cm] (R)"
            ASYM_COL="Jump Height (Imp-Mom) [cm] (Asym)(%)"
            LADO_COL=next((c for c in df.columns if "lado" in c.lower() or "debil" in c.lower() or "describe" in c.lower()),None)
            fecha_col=next((c for c in df.columns if "fecha" in c.lower() and "_" not in c),None)

            for col in [L_COL,R_COL,ASYM_COL]:
                if col in df.columns: df[col]=to_num_col(df[col])

            # Filtros
            st.markdown('<div class="filter-bar">',unsafe_allow_html=True)
            fc1,fc2,fc3=st.columns(3)
            with fc1: dff,_=filtro_anio_widget(df,"cmj1pp")
            with fc2:
                pos_opts=["Todas"]+(sorted(dff[pos_col].dropna().astype(str).unique().tolist()) if pos_col else [])
                pos_sel=st.selectbox("Posición",pos_opts,key="cmj1_pos")
                if pos_sel!="Todas" and pos_col: dff=dff[dff[pos_col].astype(str)==pos_sel]
            with fc3:
                jugs=["Todos"]+sorted(dff[jcol].dropna().astype(str).unique().tolist())
                jsel=st.selectbox("Jugador",jugs,key="cmj1_jug")
            st.markdown('</div>',unsafe_allow_html=True)

            ref_df=dff.copy()
            jug_vals={}
            if jsel!="Todos":
                jug_df=dff[dff[jcol].astype(str)==jsel]
                for col in [L_COL,R_COL,ASYM_COL]:
                    if col in jug_df.columns:
                        vals=jug_df[col].dropna()
                        jug_vals[col]=vals.iloc[-1] if len(vals)>0 else None

            # KPI Cards
            st.markdown('<div class="subsec">Métricas principales</div>',unsafe_allow_html=True)
            k1,k2,k3=st.columns(3)
            with k1: kpi_card_contextual("ALT IZQUIERDA (cm)", jug_vals.get(L_COL) if jug_vals else None, ref_df, L_COL)
            with k2: kpi_card_contextual("ALT DERECHA (cm)", jug_vals.get(R_COL) if jug_vals else None, ref_df, R_COL)
            with k3: kpi_card_contextual("ASIMETRÍA (%)", jug_vals.get(ASYM_COL) if jug_vals else None, ref_df, ASYM_COL)

            # Evolución asimetría temporal
            if fecha_col and ASYM_COL in dff.columns:
                st.markdown('<div class="subsec">Evolución de asimetría (%)</div>',unsafe_allow_html=True)
                dff2=dff.copy()
                dff2["_f"]=pd.to_datetime(dff2[fecha_col],dayfirst=True,errors="coerce")
                plot_df=dff2[dff2[jcol].astype(str)==jsel] if jsel!="Todos" else dff2
                plot_df=plot_df.dropna(subset=["_f",ASYM_COL]).sort_values("_f")
                if not plot_df.empty:
                    fig=px.line(plot_df,x="_f",y=ASYM_COL,color=jcol if jsel=="Todos" else None,
                               markers=True,template="plotly_dark",labels={"_f":"Fecha",ASYM_COL:"Asim. (%)"})
                    fig.add_hline(y=10,line_dash="dot",line_color="#fbbf24",annotation_text="Umbral 10%")
                    fig.add_hline(y=15,line_dash="dot",line_color="#f87171",annotation_text="Riesgo 15%")
                    fig.update_traces(line_color="#c8102e",marker_size=8)
                    plotly_dark(fig,280)
                    st.plotly_chart(fig,use_container_width=True)

            # Gráfico barras Der vs Izq
            if L_COL in dff.columns and R_COL in dff.columns:
                st.markdown('<div class="subsec">Comparativa Der vs Izq por jugador</div>',unsafe_allow_html=True)
                plot_df2=dff if jsel=="Todos" else dff[dff[jcol].astype(str)==jsel]
                comp=plot_df2.groupby(jcol)[[L_COL,R_COL]].mean().reset_index()
                fig2=go.Figure()
                fig2.add_trace(go.Bar(name="Izquierda",x=comp[jcol].astype(str),y=comp[L_COL],marker_color="#4299e1",text=comp[L_COL].round(1),textposition="outside"))
                fig2.add_trace(go.Bar(name="Derecha",x=comp[jcol].astype(str),y=comp[R_COL],marker_color="#c8102e",text=comp[R_COL].round(1),textposition="outside"))
                fig2.update_layout(barmode="group",template="plotly_dark",xaxis_tickangle=-45)
                plotly_dark(fig2,300)
                st.plotly_chart(fig2,use_container_width=True)

            # Tabla con escala de color en Asym
            st.markdown('<div class="subsec">Tabla de resultados</div>',unsafe_allow_html=True)
            tbl=dff if jsel=="Todos" else dff[dff[jcol].astype(str)==jsel]
            show=[jcol]+([pos_col] if pos_col else [])+[c for c in [L_COL,R_COL,ASYM_COL,LADO_COL] if c and c in tbl.columns]
            if fecha_col: show=[fecha_col]+show
            tbl=tbl[[c for c in show if c in tbl.columns]].reset_index(drop=True)
            num_c=[c for c in [L_COL,R_COL,ASYM_COL] if c in tbl.columns]
            html_table(tbl, highlight_cols=num_c)

    # ──────────────────────────────────────────────────────────
    # CURL NÓRDICO
    # ──────────────────────────────────────────────────────────
    with tab3:
        nord_img=img_b64(ASSETS/"NORDICO.png")
        ci,cd=st.columns([1,3])
        with ci:
            if nord_img: st.markdown(f'<img src="data:image/png;base64,{nord_img}" style="width:100%;max-width:180px;border-radius:12px;filter:drop-shadow(0 0 12px rgba(200,16,46,.3));">',unsafe_allow_html=True)
        with cd:
            st.markdown('<div style="background:rgba(8,18,38,.9);border:1px solid rgba(200,16,46,.2);border-radius:12px;padding:16px;"><div style="font-size:14px;font-weight:800;color:#fff;margin-bottom:6px;">Curl Nórdico — Nordic Hamstring</div><div style="font-size:12px;color:#94a3b8;line-height:1.6;">Fuerza excéntrica de isquiotibiales. Variables: <b style="color:#e2e8f0;">FZA DER (N) · FZA IZQ (N) · Asym% · Masa Alcanzada%</b>. Asym >15% = riesgo elevado.</div></div>',unsafe_allow_html=True)

        df_nord=cargar_sheet("nordico")
        df_cmj=cargar_sheet("cmj")  # Para calcular BW (PesoPorTestID)
        if df_nord.empty: no_data("Curl Nórdico")
        else:
            jcol=jug_col_find(df_nord); pos_col=pos_col_find(df_nord)
            L_N="L Max Force (N)"
            R_N="R Max Force (N)"
            ASYM_N="Max Imbalance (%)"
            fecha_col=next((c for c in df_nord.columns if "fecha" in c.lower() and "_" not in c),None)
            id_col=next((c for c in df_nord.columns if c.upper() in ["ID","TEST_ID","ID_TEST"]),None)

            for col in [L_N,R_N,ASYM_N]:
                if col in df_nord.columns: df_nord[col]=to_num_col(df_nord[col])

            # Calcular MasaAlcanzada% usando lógica DAX
            # PesoPorTestID = BW del CMJ con mismo jugador e ID
            bw_col_cmj=next((c for c in df_cmj.columns if "bw" in c.lower() and "kg" in c.lower()),None) if not df_cmj.empty else None
            id_col_cmj=next((c for c in df_cmj.columns if c.upper() in ["ID","TEST_ID","ID_TEST"]),None) if not df_cmj.empty else None
            jcol_cmj=jug_col_find(df_cmj) if not df_cmj.empty else None

            def calcular_masa(row):
                try:
                    if df_cmj.empty or not bw_col_cmj or not id_col_cmj: return np.nan
                    jug=str(row[jcol])
                    test_id=str(row[id_col]) if id_col else ""
                    mask=(df_cmj[jcol_cmj].astype(str)==jug)
                    if id_col and id_col_cmj and test_id:
                        mask_id=(df_cmj[id_col_cmj].astype(str)==test_id)
                        bw_vals=df_cmj[mask&mask_id][bw_col_cmj]
                        if len(bw_vals)==0: bw_vals=df_cmj[mask][bw_col_cmj]
                    else:
                        bw_vals=df_cmj[mask][bw_col_cmj]
                    bw_vals=to_num_col(bw_vals).dropna()
                    if len(bw_vals)==0: return np.nan
                    bw=bw_vals.max()
                    l=to_num(row[L_N]) if L_N in row.index else np.nan
                    r=to_num(row[R_N]) if R_N in row.index else np.nan
                    if pd.isna(l) or pd.isna(r) or pd.isna(bw) or bw==0: return np.nan
                    return (l+r)/(bw*10)
                except: return np.nan

            df_nord["MasaAlcanzada%"]=df_nord.apply(calcular_masa,axis=1)

            # Filtros
            st.markdown('<div class="filter-bar">',unsafe_allow_html=True)
            fc1,fc2,fc3=st.columns(3)
            with fc1: dff,_=filtro_anio_widget(df_nord,"nordico")
            with fc2:
                pos_opts=["Todas"]+(sorted(dff[pos_col].dropna().astype(str).unique().tolist()) if pos_col else [])
                pos_sel=st.selectbox("Posición",pos_opts,key="nord_pos")
                if pos_sel!="Todas" and pos_col: dff=dff[dff[pos_col].astype(str)==pos_sel]
            with fc3:
                jugs=["Todos"]+sorted(dff[jcol].dropna().astype(str).unique().tolist())
                jsel=st.selectbox("Jugador",jugs,key="nord_jug")
            st.markdown('</div>',unsafe_allow_html=True)

            ref_df=dff.copy()
            jug_vals={}
            if jsel!="Todos":
                jug_df=dff[dff[jcol].astype(str)==jsel]
                for col in [L_N,R_N,ASYM_N,"MasaAlcanzada%"]:
                    if col in jug_df.columns:
                        vals=jug_df[col].dropna()
                        jug_vals[col]=vals.iloc[-1] if len(vals)>0 else None

            # KPI Cards
            st.markdown('<div class="subsec">Métricas principales</div>',unsafe_allow_html=True)
            k1,k2,k3,k4=st.columns(4)
            with k1: kpi_card_contextual("FZA IZQUIERDA (N)", jug_vals.get(L_N) if jug_vals else None, ref_df, L_N)
            with k2: kpi_card_contextual("FZA DERECHA (N)", jug_vals.get(R_N) if jug_vals else None, ref_df, R_N)
            with k3: kpi_card_contextual("DIF. ASIMETRÍA (%)", jug_vals.get(ASYM_N) if jug_vals else None, ref_df, ASYM_N)
            with k4: kpi_card_contextual("MASA ALCANZADA (%)", jug_vals.get("MasaAlcanzada%") if jug_vals else None, ref_df, "MasaAlcanzada%")

            # Gráfico Der vs Izq
            if L_N in dff.columns and R_N in dff.columns:
                st.markdown('<div class="subsec">Comparativa FZA Der vs Izq</div>',unsafe_allow_html=True)
                plot_df=dff if jsel=="Todos" else dff[dff[jcol].astype(str)==jsel]
                comp=plot_df.groupby(jcol)[[L_N,R_N]].mean().reset_index().sort_values(L_N,ascending=False)
                fig=go.Figure()
                fig.add_trace(go.Bar(name="FZA IZQ",x=comp[jcol].astype(str),y=comp[L_N],marker_color="#4299e1",text=comp[L_N].round(0),textposition="outside"))
                fig.add_trace(go.Bar(name="FZA DER",x=comp[jcol].astype(str),y=comp[R_N],marker_color="#c8102e",text=comp[R_N].round(0),textposition="outside"))
                fig.update_layout(barmode="group",template="plotly_dark",xaxis_tickangle=-45)
                plotly_dark(fig,300)
                st.plotly_chart(fig,use_container_width=True)

            # Gráfico asimetría
            if ASYM_N in dff.columns:
                st.markdown('<div class="subsec">Asimetría por jugador</div>',unsafe_allow_html=True)
                plot_df=dff if jsel=="Todos" else dff[dff[jcol].astype(str)==jsel]
                asym_comp=plot_df.groupby(jcol)[ASYM_N].mean().reset_index().sort_values(ASYM_N,ascending=False)
                fig2=px.bar(asym_comp,x=jcol,y=ASYM_N,text=ASYM_N,
                           color=ASYM_N,color_continuous_scale="RdYlGn_r",template="plotly_dark")
                fig2.add_hline(y=15,line_dash="dot",line_color="#f87171",annotation_text="Riesgo >15%")
                fig2.add_hline(y=10,line_dash="dot",line_color="#fbbf24",annotation_text="Atención >10%")
                fig2.update_traces(texttemplate="%{text:.1f}%",textposition="outside",textfont_color="#fff")
                fig2.update_coloraxes(showscale=False)
                fig2.update_layout(xaxis_tickangle=-45)
                plotly_dark(fig2,300)
                st.plotly_chart(fig2,use_container_width=True)

            # Tabla
            st.markdown('<div class="subsec">Tabla de resultados</div>',unsafe_allow_html=True)
            tbl=dff if jsel=="Todos" else dff[dff[jcol].astype(str)==jsel]
            show=[jcol]+([pos_col] if pos_col else [])+[c for c in [L_N,R_N,ASYM_N,"MasaAlcanzada%"] if c in tbl.columns]
            if fecha_col: show=[fecha_col]+show
            tbl=tbl[[c for c in show if c in tbl.columns]].reset_index(drop=True)
            num_c=[c for c in [L_N,R_N,ASYM_N,"MasaAlcanzada%"] if c in tbl.columns]
            html_table(tbl, highlight_cols=num_c)

    # ──────────────────────────────────────────────────────────
    # VBT
    # ──────────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div style="background:rgba(8,18,38,.9);border:1px solid rgba(200,16,46,.2);border-radius:12px;padding:16px;margin-bottom:12px;"><div style="font-size:14px;font-weight:800;color:#fff;margin-bottom:6px;">⚡ VBT — Velocity Based Training</div><div style="font-size:12px;color:#94a3b8;line-height:1.6;">Entrenamiento basado en velocidad. Monitorea la pérdida de velocidad para controlar fatiga y carga de fuerza.</div></div>',unsafe_allow_html=True)
        df=cargar_sheet("vbt")
        if df.empty: no_data("VBT")
        else:
            jcol=jug_col_find(df); pos_col=pos_col_find(df)
            st.markdown('<div class="filter-bar">',unsafe_allow_html=True)
            fc1,fc2,fc3=st.columns(3)
            with fc1: dff,_=filtro_anio_widget(df,"vbt")
            with fc2:
                pos_opts=["Todas"]+(sorted(dff[pos_col].dropna().astype(str).unique().tolist()) if pos_col else [])
                pos_sel=st.selectbox("Posición",pos_opts,key="vbt_pos")
                if pos_sel!="Todas" and pos_col: dff=dff[dff[pos_col].astype(str)==pos_sel]
            with fc3:
                jugs=["Todos"]+sorted(dff[jcol].dropna().astype(str).unique().tolist())
                jsel=st.selectbox("Jugador",jugs,key="vbt_jug")
                if jsel!="Todos": dff=dff[dff[jcol].astype(str)==jsel]
            st.markdown('</div>',unsafe_allow_html=True)
            num_cols=[c for c in dff.columns if to_num_col(dff[c]).notna().sum()>len(dff)*0.3 and c not in ["AÑO","_fecha"]]
            html_table(dff.reset_index(drop=True), highlight_cols=num_cols[:4] if len(num_cols)>4 else num_cols)

# ══════════════════════════════════════════════════════════════
# DEMANDAS FÍSICAS
# ══════════════════════════════════════════════════════════════
def pagina_demandas():
    st.markdown('<div class="sec-title">📡 Demandas Físicas — GPS</div>',unsafe_allow_html=True)
    pdf_btn()
    df=cargar_sheet("gps")
    if df.empty: no_data("GPS"); return

    jcol=jug_col_find(df); pos_col=pos_col_find(df)
    fecha_col=next((c for c in df.columns if "fecha" in c.lower() and "_" not in c.lower()),None)
    dist_col=next((c for c in df.columns if "dist" in c.lower() or "tot" in c.lower()),None)

    tab1,tab2,tab3=st.tabs(["📊 Microciclo","👤 Individual","📈 Ratio A:C"])

    with tab1:
        st.markdown('<div class="filter-bar">',unsafe_allow_html=True)
        fc1,fc2,fc3=st.columns(3)
        with fc1: dff,_=filtro_anio_widget(df,"gps_mic")
        with fc2:
            if fecha_col and "AÑO" in dff.columns:
                dff["_f"]=pd.to_datetime(dff[fecha_col],dayfirst=True,errors="coerce")
                dff["_sem"]=dff["_f"].dt.isocalendar().week
                sems=["Todas"]+sorted(dff["_sem"].dropna().unique().astype(int).tolist())
                ssel=st.selectbox("Semana",sems,key="gps_sem")
                if ssel!="Todas": dff=dff[dff["_sem"]==int(ssel)]
        with fc3:
            jugs=["Todos"]+sorted(dff[jcol].dropna().astype(str).unique().tolist())
            jsel=st.selectbox("Jugador",jugs,key="gps_mic_jug")
            if jsel!="Todos": dff=dff[dff[jcol].astype(str)==jsel]
        st.markdown('</div>',unsafe_allow_html=True)

        c1,c2,c3,c4=st.columns(4)
        c1.metric("📋 Sesiones",len(dff)); c2.metric("👥 Jugadores",dff[jcol].nunique())
        if dist_col:
            dvals=to_num_col(dff[dist_col])
            c3.metric("📏 Dist. Total",f"{int(dvals.sum()):,}m" if not dvals.isna().all() else "—")
            c4.metric("📏 Dist. Prom.",f"{int(dvals.mean()):,}m" if not dvals.isna().all() else "—")

        if dist_col and fecha_col:
            dff2=dff.copy()
            dff2["_f"]=pd.to_datetime(dff2[fecha_col],dayfirst=True,errors="coerce")
            dff2[dist_col]=to_num_col(dff2[dist_col])
            dff2=dff2.dropna(subset=["_f",dist_col]).sort_values("_f")
            if not dff2.empty:
                fig=px.bar(dff2,x="_f",y=dist_col,color=jcol,template="plotly_dark",
                          labels={"_f":"Fecha",dist_col:"Distancia (m)"},
                          color_discrete_sequence=px.colors.sequential.Reds_r)
                plotly_dark(fig,320)
                st.plotly_chart(fig,use_container_width=True)
        num_cols=[c for c in dff.columns if to_num_col(dff[c]).notna().sum()>len(dff)*0.3 and c not in ["AÑO","_fecha","_sem","_f"]]
        show_gps=dff[[c for c in dff.columns if not c.startswith("_")]].reset_index(drop=True)
        html_table(show_gps, highlight_cols=num_cols[:5])

    with tab2:
        jug_ind=st.selectbox("Jugador",sorted(df[jcol].dropna().astype(str).unique().tolist()),key="gps_ind")
        dfi=df[df[jcol].astype(str)==jug_ind].copy()
        num_cols=[c for c in dfi.columns if to_num_col(dfi[c]).notna().sum()>len(dfi)*0.3 and c not in ["AÑO","_fecha"]]
        cs=st.columns(min(4,len(num_cols)))
        for i,col in enumerate(num_cols[:4]):
            vals=to_num_col(dfi[col]).dropna()
            cs[i].metric(col[:20],round(vals.mean(),1) if len(vals)>0 else "—")
        if fecha_col and dist_col:
            dfi["_f"]=pd.to_datetime(dfi[fecha_col],dayfirst=True,errors="coerce")
            dfi[dist_col]=to_num_col(dfi[dist_col])
            dfi=dfi.dropna(subset=["_f",dist_col]).sort_values("_f")
            fig=px.line(dfi,x="_f",y=dist_col,template="plotly_dark",markers=True,labels={"_f":"Fecha",dist_col:"Distancia (m)"})
            fig.update_traces(line_color="#c8102e",marker_color="#fff")
            plotly_dark(fig,300)
            st.plotly_chart(fig,use_container_width=True)

    with tab3:
        if dist_col and fecha_col:
            jug_ac=st.selectbox("Jugador",sorted(df[jcol].dropna().astype(str).unique().tolist()),key="gps_ac")
            dfac=df[df[jcol].astype(str)==jug_ac].copy()
            dfac["_f"]=pd.to_datetime(dfac[fecha_col],dayfirst=True,errors="coerce")
            dfac[dist_col]=to_num_col(dfac[dist_col])
            dfac=dfac.dropna(subset=["_f",dist_col]).sort_values("_f").set_index("_f")
            dfac["aguda"]=dfac[dist_col].rolling("7D").sum()
            dfac["cronica"]=dfac[dist_col].rolling("28D").mean()*7
            dfac["ratio_ac"]=(dfac["aguda"]/dfac["cronica"].replace(0,float("nan"))).round(2)
            dfac=dfac.reset_index()
            fig=px.line(dfac,x="_f",y="ratio_ac",template="plotly_dark",labels={"_f":"Fecha","ratio_ac":"Ratio A:C"})
            fig.add_hline(y=0.8,line_dash="dot",line_color="#4ade80",annotation_text="Óptimo 0.8")
            fig.add_hline(y=1.3,line_dash="dot",line_color="#f87171",annotation_text="Riesgo 1.3")
            fig.update_traces(line_color="#c8102e")
            plotly_dark(fig,320)
            st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════════════════════
# CONTROL DE PARTIDOS
# ══════════════════════════════════════════════════════════════
# ── Resolucion flexible de columnas GPS/partidos ──────────────────────────
GPS_COLS = [
    ("MIN",       ["MIN", "MINUTOS", "MINS"],                                  0),
    ("DIST TOT",  ["TOT DIST", "DIST TOT", "DISTANCIA TOTAL", "DIST TOTAL"],   0),
    ("MTS/MIN",   ["MTS/MIN", "MTS MIN", "M/MIN"],                             1),
    ("MTS>19",    ["MTS>19 KM/H", "MTS >19 KM/H", "MTS >19", "MTS>19"],        0),
    ("MTS>24",    ["MTS > 24 KM/H", "MTS >24 KM/H", "MTS >24", "MTS>24"],      0),
    ("#SPRINT",   ["#SP24", "SP24", "SPRINTS", "#SPRINT", "N SPRINT"],         0),
    ("VEL MAX",   ["V-MAX", "VMAX", "V MAX", "VEL MAX", "VELOCIDAD MAXIMA"],   1),
    ("ACEL",      ["ACEL", "ACELERACIONES", "ACC"],                            0),
    ("DES",       ["DES", "DESACELERACIONES", "DEC"],                          0),
]
META_COLS = [
    ("JUGADOR", ["JUGADOR", "JUG", "NOMBRE", "PLAYER", "ATLETA"]),
    ("RIVAL",   ["RIVAL", "OPONENTE", "VS"]),
    ("RES",     ["RES", "RESULTADO"]),
    ("FECHA",   ["FECHA", "DATE"]),
    ("MICRO",   ["MICROCICLO", "MICRO", "MC"]),
    ("POS",     ["POS", "POSICION", "POSICIÓN"]),
]

def _find_col(df, cands):
    """Match EXACTO primero. El difuso solo con tokens de 4+ letras: antes 'ID'
    cazaba cualquier columna que contuviera 'id' (SALIDA, MEDIDA...) y 'PG' igual,
    por eso la tabla mostraba VOL/SUP en esas columnas."""
    up = {str(c).upper().strip(): c for c in df.columns}
    for cand in cands:
        if cand.upper().strip() in up: return up[cand.upper().strip()]
    for cand in cands:
        k = cand.upper().replace(" ", "")
        if len(k) < 4: continue
        for c in df.columns:
            if k in str(c).upper().replace(" ", ""): return c
    return None

def _norm_nom(serie):
    return (serie.astype(str).str.upper().str.strip()
            .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
            .str.replace(r"\s+", " ", regex=True))

def enriquecer_con_gps(df, gps):
    """GPS_LONG es la fuente autoritativa de MICROCICLO y POS.
    Cruza por JUGADOR + FECHA y agrega/corrige esas dos columnas: la hoja de
    partidos no trae microciclo y su POS estaba desactualizada."""
    if df is None or df.empty or gps is None or gps.empty: return df
    fd = _find_col(df, ["FECHA", "DATE"]); fg = _find_col(gps, ["FECHA", "DATE"])
    if fd is None or fg is None: return df
    mg = _find_col(gps, ["MICROCICLO", "MICRO", "MC"])
    pg = _find_col(gps, ["POS", "POSICION", "POSICIÓN"])
    if mg is None and pg is None: return df
    try:
        g = pd.DataFrame({"_j": _norm_nom(gps[jug_col_find(gps)]),
                          "_f": pd.to_datetime(gps[fg], dayfirst=True, errors="coerce").dt.date})
        if mg is not None: g["_MICRO"] = gps[mg].astype(str)
        if pg is not None: g["_POS"] = gps[pg].astype(str)
        g = g.dropna(subset=["_f"]).drop_duplicates(subset=["_j", "_f"], keep="first")

        out = df.copy().reset_index(drop=True)
        out["_j"] = _norm_nom(out[jug_col_find(out)])
        out["_f"] = pd.to_datetime(out[fd], dayfirst=True, errors="coerce").dt.date
        out = out.merge(g, on=["_j", "_f"], how="left")

        if "_MICRO" in out.columns:
            ok = out["_MICRO"].notna() & (out["_MICRO"].astype(str).str.lower() != "nan")
            out["MICROCICLO"] = out["_MICRO"].where(ok, None)
        if "_POS" in out.columns:
            pcol = _find_col(df, ["POS", "POSICION", "POSICIÓN"])
            ok = out["_POS"].notna() & (out["_POS"].astype(str).str.lower() != "nan")
            out[pcol or "POS"] = out["_POS"].where(ok, out[pcol]) if pcol else out["_POS"]
        return out.drop(columns=[c for c in ["_j", "_f", "_MICRO", "_POS"] if c in out.columns])
    except Exception:
        return df

def construir_tabla_gps(df, meta=META_COLS, metrics=GPS_COLS):
    """Devuelve (df_normalizado, mapa_decimales) con los nombres pedidos."""
    out = pd.DataFrame(index=df.index)
    dec = {}
    for nombre, cands in meta:
        c = _find_col(df, cands)
        if c is not None:
            v = df[c]
            if nombre == "FECHA":
                v = pd.to_datetime(v, dayfirst=True, errors="coerce").dt.strftime("%d/%m/%Y")
            out[nombre] = v.astype(str).replace({"nan": "—", "NaT": "—"})
    for nombre, cands, d in metrics:
        c = _find_col(df, cands)
        if c is not None:
            out[nombre] = to_num_col(df[c]).round(d)
            dec[nombre] = d
    return out, dec


def pagina_control_partidos():
    st.markdown('<div class="sec-title">⚽ Control de Partidos</div>',unsafe_allow_html=True)
    pdf_btn()
    df=cargar_sheet("partidos")
    if df.empty: no_data("Control de Partidos"); return
    df=enriquecer_con_gps(df, cargar_sheet("gps"))   # MICROCICLO + POS reales

    jcol=jug_col_find(df)
    dff,_=filtro_anio_widget(df,"part")

    rcol=_find_col(dff,["RIVAL","OPONENTE","VS"])
    fc1,fc2=st.columns(2)
    with fc1:
        jsel=st.selectbox("Jugador",["Todos"]+sorted(dff[jcol].dropna().astype(str).unique().tolist()),key="part_jug")
    with fc2:
        rsel=st.multiselect("Rival",sorted(dff[rcol].dropna().astype(str).unique().tolist()) if rcol else [],
                            default=[],key="part_riv",placeholder="Todos los rivales")
    base=dff.copy()
    if rsel and rcol: base=base[base[rcol].astype(str).isin(rsel)]
    dsel=base[base[jcol].astype(str)==jsel] if jsel!="Todos" else base

    c1,c2,c3=st.columns(3)
    c1.metric("📋 Registros",len(dsel))
    min_col=_find_col(dsel,["MIN","MINUTOS"])
    if min_col is not None:
        mvals=to_num_col(dsel[min_col])
        c2.metric("⏱️ Min. totales",int(mvals.sum()) if not mvals.isna().all() else "—")
        c3.metric("⏱️ Min. promedio",round(mvals.mean(),1) if not mvals.isna().all() else "—")

    # ── Tabla con las variables solicitadas ──────────────────────────────
    st.markdown('<div class="subsec">Detalle de partidos</div>',unsafe_allow_html=True)
    tabla,_dec=construir_tabla_gps(dsel)
    num_p=[c for c in tabla.columns if c in dict((m[0],1) for m in GPS_COLS)]
    html_table(tabla.reset_index(drop=True), highlight_cols=num_p, max_rows=25, max_cols=18)

    # ── Scatter MTS/MIN vs MTS>19 ────────────────────────────────────────
    st.markdown('<div class="subsec">Intensidad vs. volumen de alta velocidad</div>',unsafe_allow_html=True)
    st.caption("Eje X: MTS/MIN (intensidad) · Eje Y: MTS>19 (volumen de alta velocidad). "
               "Cada burbuja es un partido, etiquetada con el rival y el resultado.")
    tb_all,_ = construir_tabla_gps(base)
    if "MTS/MIN" not in tb_all.columns or "MTS>19" not in tb_all.columns:
        st.info("No se encontraron las columnas MTS/MIN y MTS>19 en la hoja de partidos.")
    else:
        sc=tb_all.dropna(subset=["MTS/MIN","MTS>19"]).copy()
        if sc.empty:
            st.info("Sin datos suficientes para el gráfico.")
        else:
            for _c in ("RIVAL","RES","JUGADOR"):
                if _c not in sc.columns: sc[_c]="—"
            sc["etq"]=sc["RIVAL"].astype(str)+" ("+sc["RES"].astype(str)+")"
            sc["_sz"]=to_num_col(sc["MIN"]).fillna(30) if "MIN" in sc.columns else 30
            fig=go.Figure()
            if jsel!="Todos":
                otros=sc[sc["JUGADOR"].astype(str)!=jsel]
                propio=sc[sc["JUGADOR"].astype(str)==jsel]
                if not otros.empty:
                    fig.add_trace(go.Scatter(x=otros["MTS/MIN"],y=otros["MTS>19"],mode="markers",
                        name="Resto del plantel",marker=dict(size=9,color="rgba(148,163,184,0.45)"),
                        hovertext=otros["JUGADOR"].astype(str)+" · "+otros["etq"],hoverinfo="text+x+y"))
                if not propio.empty:
                    fig.add_trace(go.Scatter(x=propio["MTS/MIN"],y=propio["MTS>19"],mode="markers+text",
                        name=jsel,text=propio["etq"],textposition="top center",
                        textfont=dict(color="#ffffff",size=10),
                        marker=dict(size=propio["_sz"],sizemode="area",
                                    sizeref=2.*propio["_sz"].max()/(38.**2) if propio["_sz"].max()>0 else 1,
                                    sizemin=8,color="#c8102e",line=dict(color="#fff",width=1)),
                        hovertext=propio["etq"],hoverinfo="text+x+y"))
                    fig.add_vline(x=float(sc["MTS/MIN"].mean()),line_dash="dot",line_color="rgba(255,255,255,.35)")
                    fig.add_hline(y=float(sc["MTS>19"].mean()),line_dash="dot",line_color="rgba(255,255,255,.35)")
            else:
                fig.add_trace(go.Scatter(x=sc["MTS/MIN"],y=sc["MTS>19"],mode="markers",
                    name="Partidos",marker=dict(size=10,color="#c8102e",opacity=.75,
                                                line=dict(color="#fff",width=.5)),
                    hovertext=sc["JUGADOR"].astype(str)+" · "+sc["etq"],hoverinfo="text+x+y"))
                fig.add_vline(x=float(sc["MTS/MIN"].mean()),line_dash="dot",line_color="rgba(255,255,255,.35)")
                fig.add_hline(y=float(sc["MTS>19"].mean()),line_dash="dot",line_color="rgba(255,255,255,.35)")
            fig.update_xaxes(title_text="MTS/MIN (intensidad)")
            fig.update_yaxes(title_text="MTS>19 (volumen alta velocidad)")
            plotly_dark(fig,430)
            st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════════════════════
# RESUMEN INDIVIDUAL
# ══════════════════════════════════════════════════════════════
# ── Helpers Resumen Individual ────────────────────────────────────────────
CMJ_SPECS = [("ALTURA","cm",["Jump Height (Imp-Mom)[cm]","Jump Height","ALTURA","ALTURAcm"],1),
             ("RSI-M","m/s",["RSI-modified[m/s]","RSI-modified","RSI-M","RSI"],2),
             ("ECC PP","W/kg",["Eccentric Peak Power/BM[W/kg]","Eccentric Peak Power","ECC PP"],1)]
NORD_SPECS = [("FZA IZQ","N",["L Max Force(N)","L Max Force","FZA MAX IZQ","FZA IZQ"],0),
              ("FZA DER","N",["R Max Force(N)","R Max Force","FZA MAX DER","FZA DER"],0),
              ("DIF %","%",["Max Imbalance(%)","Max Imbalance","DIF %","ASIMETRIA"],1),
              ("MASA ALCANZADA","%",["Masa Alcanzada","MASA ALCANZADA","Mass Reached"],1)]

def _mcol(df):
    if "MICROCICLO" in df.columns: return "MICROCICLO"
    for c in df.columns:
        if str(c).upper() in ["MICROCICLO","MICRO","MC","MICRO Nº"]: return c
    for c in df.columns:
        if "micro" in str(c).lower(): return c
    return None

def _sub_jug(df, jsel):
    if df is None or df.empty: return pd.DataFrame()
    jc = jug_col_find(df)
    n = lambda x: str(x).upper().strip()
    return df[df[jc].astype(str).map(n) == n(jsel)]

def _cards(df, specs, cols_por_fila=4, modo="max"):
    """Tarjetas: valor principal = max del jugador; abajo el promedio."""
    if df.empty: st.info("Sin registros."); return
    vals=[]
    for lab,uni,cands,dec in specs:
        c=_find_col(df,cands)
        if c is None: continue
        v=to_num_col(df[c]).dropna()
        if v.empty: continue
        vals.append((lab,uni,round(v.max(),dec),round(v.mean(),dec)))
    if not vals: st.info("No se encontraron las columnas esperadas."); return
    for i in range(0,len(vals),cols_por_fila):
        fila=vals[i:i+cols_por_fila]; cs=st.columns(len(fila))
        for col,(lab,uni,mx,pr) in zip(cs,fila):
            col.metric(f"{lab} ({uni})", mx, help=f"Promedio: {pr}")
            col.caption(f"PROM · {pr}")

def _matriz_micros(dfj, n_micros=10):
    """Sumatoria por microciclo; VEL MAX = maximo, MTS/MIN = promedio."""
    mc=_mcol(dfj)
    if mc is None: return pd.DataFrame()
    t,_=construir_tabla_gps(dfj)
    t["MICRO"]=dfj[mc].astype(str).values
    _fc=_find_col(dfj,["FECHA","DATE"])
    if _fc is not None:
        t["_ord"]=pd.to_datetime(dfj[_fc],dayfirst=True,errors="coerce").values
    agg={}
    for nombre,_c,_d in GPS_COLS:
        if nombre not in t.columns: continue
        agg[nombre]="max" if nombre=="VEL MAX" else ("mean" if nombre=="MTS/MIN" else "sum")
    if not agg: return pd.DataFrame()
    g=t.groupby("MICRO").agg(agg).round(1)
    g.insert(0,"SES",t.groupby("MICRO").size())
    if "_ord" in t.columns:
        orden=t.groupby("MICRO")["_ord"].max().sort_values(ascending=False)
        g=g.reindex(orden.index)
    else:
        g=g.iloc[::-1]
    return g.head(n_micros).reset_index()

def pagina_resumen():
    st.markdown('<div class="sec-title">📄 Resumen Individual</div>',unsafe_allow_html=True)
    pdf_btn()
    hist=cargar_sheet("historial")
    if hist.empty: no_data("Historial"); return
    jcol=jug_col_find(hist)
    jugadores=sorted(hist[jcol].dropna().astype(str).unique().tolist())

    gps=cargar_sheet("gps"); part=cargar_sheet("partidos")
    fuente = enriquecer_con_gps(part, gps) if not part.empty else gps

    # ── FILTROS DE LA HOJA ────────────────────────────────────────────────
    f1,f2,f3=st.columns([2,1,2])
    with f1: jsel=st.selectbox("Jugador",jugadores,key="res_jug")
    with f2:
        anios=sorted([int(a) for a in fuente.get("AÑO",pd.Series(dtype=float)).dropna().unique()],reverse=True) if "AÑO" in fuente.columns else []
        asel=st.multiselect("Año",[str(a) for a in anios],default=[str(anios[0])] if anios else [],key="res_anio",placeholder="Todos")
    with f3:
        incluir=st.multiselect("Qué incluir",["GPS","CMJ","Nórdico","VBT","Historial médico","Nutrición"],
                               default=["GPS","CMJ","Nórdico","Historial médico"],key="res_inc")

    dj=_sub_jug(fuente,jsel)
    if asel and "AÑO" in dj.columns: dj=dj[dj["AÑO"].astype(str).isin(asel)]

    g1,g2,g3=st.columns(3)
    mc=_mcol(dj); rc=_find_col(dj,["RIVAL","OPONENTE"]); refc=_find_col(dj,["REF","LIGA","TORNEO","COMPETENCIA"])
    with g1:
        msel=st.multiselect("Microciclo",sorted(dj[mc].dropna().astype(str).unique().tolist()) if mc else [],
                            default=[],key="res_mic",placeholder="Todos")
    with g2:
        rsel=st.multiselect("Rival",sorted(dj[rc].dropna().astype(str).unique().tolist()) if rc else [],
                            default=[],key="res_riv",placeholder="Todos")
    with g3:
        refsel=st.multiselect("Ref. (liga)",sorted(dj[refc].dropna().astype(str).unique().tolist()) if refc else [],
                              default=[],key="res_ref",placeholder="Todas")
    if msel and mc: dj=dj[dj[mc].astype(str).isin(msel)]
    if rsel and rc: dj=dj[dj[rc].astype(str).isin(rsel)]
    if refsel and refc: dj=dj[dj[refc].astype(str).isin(refsel)]

    fcol=_find_col(dj,["FECHA","DATE"])
    if fcol is not None:
        fechas=pd.to_datetime(dj[fcol],dayfirst=True,errors="coerce").dropna()
        if not fechas.empty:
            d1,d2=st.columns(2)
            with d1: desde=st.date_input("Desde",fechas.min().date(),key="res_d1")
            with d2: hasta=st.date_input("Hasta",fechas.max().date(),key="res_d2")
            mask=pd.to_datetime(dj[fcol],dayfirst=True,errors="coerce")
            dj=dj[(mask.dt.date>=desde)&(mask.dt.date<=hasta)]

    st.markdown(f'<div style="background:rgba(8,18,38,.9);border:1px solid rgba(200,16,46,.25);border-radius:14px;padding:14px 18px;margin:10px 0;"><span style="font-family:\'Bebas Neue\',sans-serif;font-size:26px;letter-spacing:2px;color:#fff;">{jsel}</span><span style="color:#94a3b8;font-size:12px;margin-left:12px;">{len(dj)} sesiones en el período</span></div>',unsafe_allow_html=True)

    # ── GPS ───────────────────────────────────────────────────────────────
    if "GPS" in incluir:
        st.markdown('<div class="subsec">📡 GPS · Máximos y promedios</div>',unsafe_allow_html=True)
        _cards(dj,[(n,("m" if "MTS" in n or "DIST" in n else ("min" if n=="MIN" else ("km/h" if n=="VEL MAX" else ("m/min" if n=="MTS/MIN" else "n")))),c,d)
                   for n,c,d in GPS_COLS if n in ["MIN","DIST TOT","MTS/MIN","MTS>19","MTS>24","#SPRINT","VEL MAX"]],
               cols_por_fila=4)

        st.markdown('<div class="subsec">Matriz · últimos 10 microciclos</div>',unsafe_allow_html=True)
        st.caption("Sumatoria por microciclo · VEL MAX = máximo registrado · MTS/MIN = promedio.")
        mm=_matriz_micros(dj,10)
        if mm.empty: st.info("No se encontró columna de microciclo en la hoja.")
        else: html_table(mm,highlight_cols=[c for c in mm.columns if c not in ["MICRO","SES"]],max_rows=12,max_cols=14)

        st.markdown('<div class="subsec">Matriz · partidos jugados</div>',unsafe_allow_html=True)
        tp,_=construir_tabla_gps(dj)
        if "MIN" in tp.columns: tp=tp[to_num_col(tp["MIN"]).fillna(0)>0]
        html_table(tp.reset_index(drop=True),
                   highlight_cols=[n for n,_c,_d in GPS_COLS if n in tp.columns],max_rows=20,max_cols=18)

        st.markdown('<div class="subsec">Dispersión de partidos · MTS/MIN vs MTS>19</div>',unsafe_allow_html=True)
        if {"MTS/MIN","MTS>19"}.issubset(tp.columns):
            sc=tp.dropna(subset=["MTS/MIN","MTS>19"]).copy()
            if sc.empty: st.info("Sin datos suficientes.")
            else:
                for _c in ("RIVAL","RES"):
                    if _c not in sc.columns: sc[_c]="—"
                sc["etq"]=sc["RIVAL"].astype(str)+" ("+sc["RES"].astype(str)+")"
                fig=go.Figure(go.Scatter(x=sc["MTS/MIN"],y=sc["MTS>19"],mode="markers+text",
                    text=sc["etq"],textposition="top center",textfont=dict(color="#e2e8f0",size=10),
                    marker=dict(size=13,color="#c8102e",line=dict(color="#fff",width=1)),
                    hovertext=sc["etq"],hoverinfo="text+x+y"))
                fig.add_vline(x=float(sc["MTS/MIN"].mean()),line_dash="dot",line_color="rgba(255,255,255,.35)")
                fig.add_hline(y=float(sc["MTS>19"].mean()),line_dash="dot",line_color="rgba(255,255,255,.35)")
                fig.update_xaxes(title_text="MTS/MIN (intensidad)")
                fig.update_yaxes(title_text="MTS>19 (volumen alta velocidad)")
                plotly_dark(fig,400); st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("No se encontraron MTS/MIN y MTS>19.")

    # ── CMJ / NORDICO / VBT ───────────────────────────────────────────────
    if "CMJ" in incluir:
        st.markdown('<div class="subsec">🦵 CMJ · Salto contramovimiento</div>',unsafe_allow_html=True)
        dc=_sub_jug(cargar_sheet("cmj"),jsel)
        _cards(dc,CMJ_SPECS,3)
        if not dc.empty:
            html_table(dc[[c for c in dc.columns if not str(c).startswith("_")]].reset_index(drop=True),max_rows=10)
    if "Nórdico" in incluir:
        st.markdown('<div class="subsec">💪 Nórdico · Fuerza isquiosural</div>',unsafe_allow_html=True)
        dn=_sub_jug(cargar_sheet("nordico"),jsel)
        _cards(dn,NORD_SPECS,4)
        if not dn.empty:
            html_table(dn[[c for c in dn.columns if not str(c).startswith("_")]].reset_index(drop=True),max_rows=10)
    if "VBT" in incluir:
        st.markdown('<div class="subsec">⚡ VBT</div>',unsafe_allow_html=True)
        dv=_sub_jug(cargar_sheet("vbt"),jsel)
        if dv.empty: st.info("Sin registros de VBT.")
        else:
            numv=[c for c in dv.columns if to_num_col(dv[c]).notna().sum()>len(dv)*0.3 and c not in ["AÑO","_fecha"]]
            _cards(dv,[(str(c)[:14],"",[c],1) for c in numv[:4]],4)
            html_table(dv[[c for c in dv.columns if not str(c).startswith("_")]].reset_index(drop=True),max_rows=10)

    # ── HISTORIAL MEDICO (matriz con colores) ─────────────────────────────
    if "Historial médico" in incluir:
        st.markdown('<div class="subsec">🏥 Historial médico</div>',unsafe_allow_html=True)
        dl=_sub_jug(cargar_sheet("lesiones"),jsel)
        if dl.empty: st.success(f"Sin lesiones registradas para {jsel} en la base.")
        else:
            show=dl[[c for c in dl.columns if not str(c).startswith("_")]].reset_index(drop=True)
            numl=[c for c in show.columns if to_num_col(show[c]).notna().sum()>len(show)*0.3 and c!="AÑO"]
            html_table(show,highlight_cols=numl,max_rows=20,max_cols=14)

    if "Nutrición" in incluir:
        st.markdown('<div class="subsec">🥗 Control nutricional</div>',unsafe_allow_html=True)
        dnu=_sub_jug(cargar_sheet("nutricion"),jsel)
        if dnu.empty: st.info("Sin registros de nutrición.")
        else:
            numn=[c for c in dnu.columns if to_num_col(dnu[c]).notna().sum()>len(dnu)*0.3 and c not in ["AÑO","_fecha"]]
            _cards(dnu,[(str(c)[:14],"",[c],1) for c in numn[:4]],4)
            html_table(dnu[[c for c in dnu.columns if not str(c).startswith("_")]].reset_index(drop=True),max_rows=15)

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
                        st.session_state.usuarios_extra[username]["aprobado"]=True;st.session_state.usuarios_extra[username]["activo"]=True
                        st.success(f"✅ {datos['nombre']} aprobado.");st.rerun()
                with c2:
                    if st.button("❌ Rechazar",key=f"rec_{username}"):
                        del st.session_state.usuarios_extra[username];st.warning("Rechazado.");st.rerun()
    else: st.success("✅ No hay solicitudes pendientes.")
    st.markdown("---")
    fa=st.selectbox("Filtrar por área",["Todas"]+list(AREAS.keys()),key="fa_admin")
    todos=todos_los_usuarios()
    rows=[(k,d) for k,d in todos.items() if fa=="Todas" or d["area"]==fa]
    filas="".join([f'<tr><td><code style="color:#60a5fa;">{u}</code></td><td><b>{d["nombre"]}</b></td><td><span class="badge-area">{d["area"]}</span></td><td style="color:#94a3b8;">{d["rol"]}</td><td style="color:#64748b;font-size:12px;">{d.get("email","—")}</td><td>{"<span class=\"badge-activo\">Activo</span>" if d["activo"] else "<span class=\"badge-inactivo\">Inactivo</span>"}</td></tr>' for u,d in rows])
    st.markdown(f'<div style="background:rgba(8,18,38,.9);border:1px solid rgba(255,255,255,.06);border-radius:16px;overflow:hidden;"><table class="user-table"><thead><tr><th>Usuario</th><th>Nombre</th><th>Área</th><th>Rol</th><th>Email</th><th>Estado</th></tr></thead><tbody>{filas}</tbody></table></div>',unsafe_allow_html=True)
    st.markdown("---")
    sel=st.selectbox("Gestionar",["— elegí —"]+list(todos.keys()),key="adm_sel")
    if sel!="— elegí —":
        d=todos[sel];st.write(f"**{d['nombre']}** · {d['area']} · `{sel}`")
        c1,c2=st.columns(2)
        with c1:
            if d["activo"]:
                if st.button("🔴 Desactivar",key="btn_des"): st.session_state.usuarios_desactivados.add(sel);st.rerun()
            else:
                if st.button("🟢 Activar",key="btn_act"): st.session_state.usuarios_desactivados.discard(sel);st.rerun()
        with c2:
            if sel in st.session_state.usuarios_extra:
                if st.button("🗑️ Eliminar",key="btn_del"): del st.session_state.usuarios_extra[sel];st.rerun()
            else: st.caption("Usuarios base no eliminables")


# ══════════════════════════════════════════════════════════════
# CONTROL NUTRICIONAL
# ══════════════════════════════════════════════════════════════
def pagina_nutricion():
    st.markdown('<div class="sec-title">🥗 Control Nutricional — Control Semanal</div>',unsafe_allow_html=True)
    pdf_btn()
    df=cargar_sheet("nutricion")
    if df.empty: no_data("Control Nutricional"); return

    jcol=jug_col_find(df)
    pos_col=pos_col_find(df)
    fecha_col=next((c for c in df.columns if "fecha" in c.lower() and "_" not in c),None)
    micro_col=next((c for c in df.columns if "micro" in c.lower() or "semana" in c.lower() or "week" in c.lower()),None)
    peso_col=next((c for c in df.columns if "peso" in c.lower() or "weight" in c.lower() or "bw" in c.lower()),None)
    pliegue_col=next((c for c in df.columns if "pliegue" in c.lower() or "skinfold" in c.lower() or "grasa" in c.lower() or "fat" in c.lower()),None)

    st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:8px;">Columnas disponibles: {", ".join(df.columns[:10].tolist())}</div>',unsafe_allow_html=True)

    # ── Filtros ──────────────────────────────────────────────
    st.markdown('<div class="filter-bar">',unsafe_allow_html=True)
    fc1,fc2,fc3,fc4,fc5=st.columns(5)
    with fc1: dff,_=filtro_anio_widget(df,"nutri")
    with fc2:
        pos_opts=["Todas"]+(sorted(dff[pos_col].dropna().astype(str).unique().tolist()) if pos_col else [])
        pos_sel=st.selectbox("Posición",pos_opts,key="nutri_pos")
        if pos_sel!="Todas" and pos_col: dff=dff[dff[pos_col].astype(str)==pos_sel]
    with fc3:
        jugs=["Todos"]+sorted(dff[jcol].dropna().astype(str).unique().tolist())
        jsel=st.selectbox("Jugador",jugs,key="nutri_jug")
        if jsel!="Todos": dff=dff[dff[jcol].astype(str)==jsel]
    with fc4:
        if micro_col:
            micros=["Todos"]+sorted(dff[micro_col].dropna().astype(str).unique().tolist())
            msel=st.selectbox("Microciclo",micros,key="nutri_micro")
            if msel!="Todos": dff=dff[dff[micro_col].astype(str)==msel]
        else: msel="Todos"
    with fc5:
        if fecha_col:
            fechas_unicas=sorted(dff[fecha_col].dropna().astype(str).unique().tolist(),reverse=True)
            fsel=st.selectbox("Fecha",["Todas"]+fechas_unicas,key="nutri_fecha")
            if fsel!="Todas": dff=dff[dff[fecha_col].astype(str)==fsel]
    st.markdown('</div>',unsafe_allow_html=True)

    # ── KPIs ─────────────────────────────────────────────────
    c1,c2,c3,c4=st.columns(4)
    c1.metric("👥 Registros",len(dff))
    c2.metric("👤 Jugadores",dff[jcol].nunique())
    if peso_col:
        pvals=to_num_col(dff[peso_col]).dropna()
        c3.metric("⚖️ Peso prom.",f"{pvals.mean():.1f} kg" if len(pvals)>0 else "—")
    if pliegue_col:
        plvals=to_num_col(dff[pliegue_col]).dropna()
        c4.metric("📏 Pliegue prom.",f"{plvals.mean():.1f}" if len(plvals)>0 else "—")

    # ── Tabla con scroll ─────────────────────────────────────
    st.markdown('<div class="subsec">Registros</div>',unsafe_allow_html=True)
    show_cols=[c for c in dff.columns if not c.startswith("_")]
    num_cols_hl=[c for c in [peso_col,pliegue_col] if c and c in dff.columns]
    for c in num_cols_hl:
        dff[c]=to_num_col(dff[c])
    html_table(dff[show_cols].reset_index(drop=True), highlight_cols=num_cols_hl, max_rows=20, height=420)

    if not fecha_col or (not peso_col and not pliegue_col):
        st.info("Se necesitan columnas de fecha, peso y/o pliegue para mostrar gráficos de evolución.")
        return

    # Preparar datos temporales
    dff2=dff.copy()
    dff2["_f"]=pd.to_datetime(dff2[fecha_col],dayfirst=True,errors="coerce")
    if peso_col: dff2[peso_col]=to_num_col(dff2[peso_col])
    if pliegue_col: dff2[pliegue_col]=to_num_col(dff2[pliegue_col])
    dff2=dff2.dropna(subset=["_f"]).sort_values("_f")

    st.markdown("---")

    # ── Gráfico 1 y 2: evolución peso y pliegue ──────────────
    g1,g2=st.columns(2)
    with g1:
        if peso_col and peso_col in dff2.columns:
            st.markdown('<div class="subsec">Evolución del Peso (kg)</div>',unsafe_allow_html=True)
            dff_p=dff2.dropna(subset=[peso_col])
            fig1=px.line(dff_p,x="_f",y=peso_col,
                        color=jcol if jsel=="Todos" else None,
                        markers=True,template="plotly_dark",
                        labels={"_f":"Fecha",peso_col:"Peso (kg)"})
            fig1.update_traces(line_width=2,marker_size=7)
            if jsel!="Todos":
                fig1.update_traces(line_color="#c8102e",marker_color="#fff")
            plotly_dark(fig1,300)
            st.plotly_chart(fig1,use_container_width=True)

    with g2:
        if pliegue_col and pliegue_col in dff2.columns:
            st.markdown('<div class="subsec">Evolución del Pliegue</div>',unsafe_allow_html=True)
            dff_pl=dff2.dropna(subset=[pliegue_col])
            fig2=px.line(dff_pl,x="_f",y=pliegue_col,
                        color=jcol if jsel=="Todos" else None,
                        markers=True,template="plotly_dark",
                        labels={"_f":"Fecha",pliegue_col:"Pliegue"})
            fig2.update_traces(line_width=2,marker_size=7)
            if jsel!="Todos":
                fig2.update_traces(line_color="#4299e1",marker_color="#fff")
            plotly_dark(fig2,300)
            st.plotly_chart(fig2,use_container_width=True)

    # ── Gráfico 3: variación % por microciclo ─────────────────
    st.markdown("---")
    st.markdown('<div class="subsec">Variación % por microciclo (peso y pliegue)</div>',unsafe_allow_html=True)

    if micro_col and micro_col in dff2.columns:
        # Calcular variación % respecto al microciclo anterior por jugador
        dff3=dff2.copy()
        dff3=dff3.sort_values([jcol,micro_col])

        resultados=[]
        for jugador,grupo in dff3.groupby(jcol):
            grupo=grupo.sort_values("_f").reset_index(drop=True)
            for i in range(1,len(grupo)):
                fila={"jugador":jugador,micro_col:grupo.loc[i,micro_col],"_f":grupo.loc[i,"_f"]}
                if peso_col and peso_col in grupo.columns:
                    p_actual=grupo.loc[i,peso_col]; p_prev=grupo.loc[i-1,peso_col]
                    if pd.notna(p_actual) and pd.notna(p_prev) and p_prev!=0:
                        fila["var_peso_%"]=(p_actual-p_prev)/p_prev*100
                if pliegue_col and pliegue_col in grupo.columns:
                    pl_actual=grupo.loc[i,pliegue_col]; pl_prev=grupo.loc[i-1,pliegue_col]
                    if pd.notna(pl_actual) and pd.notna(pl_prev) and pl_prev!=0:
                        fila["var_pliegue_%"]=(pl_actual-pl_prev)/pl_prev*100
                resultados.append(fila)

        if resultados:
            df_var=pd.DataFrame(resultados)
            fig3=go.Figure()
            if "var_peso_%" in df_var.columns:
                if jsel!="Todos":
                    df_jug=df_var[df_var["jugador"]==jsel]
                    fig3.add_trace(go.Scatter(
                        x=df_jug[micro_col].astype(str),y=df_jug["var_peso_%"],
                        name="Var% Peso",mode="lines+markers",
                        line=dict(color="#c8102e",width=2),marker=dict(size=8,color="#fff")
                    ))
                else:
                    agg_peso=df_var.groupby(micro_col)["var_peso_%"].mean().reset_index()
                    fig3.add_trace(go.Scatter(
                        x=agg_peso[micro_col].astype(str),y=agg_peso["var_peso_%"],
                        name="Var% Peso (prom)",mode="lines+markers",
                        line=dict(color="#c8102e",width=2),marker=dict(size=8)
                    ))
            if "var_pliegue_%" in df_var.columns:
                if jsel!="Todos":
                    df_jug=df_var[df_var["jugador"]==jsel]
                    fig3.add_trace(go.Scatter(
                        x=df_jug[micro_col].astype(str),y=df_jug["var_pliegue_%"],
                        name="Var% Pliegue",mode="lines+markers",
                        line=dict(color="#4299e1",width=2),marker=dict(size=8,color="#60a5fa")
                    ))
                else:
                    agg_pl=df_var.groupby(micro_col)["var_pliegue_%"].mean().reset_index()
                    fig3.add_trace(go.Scatter(
                        x=agg_pl[micro_col].astype(str),y=agg_pl["var_pliegue_%"],
                        name="Var% Pliegue (prom)",mode="lines+markers",
                        line=dict(color="#4299e1",width=2),marker=dict(size=8)
                    ))
            fig3.add_hline(y=0,line_dash="dot",line_color="#64748b",line_width=1)
            fig3.update_layout(
                template="plotly_dark",
                xaxis_title="Microciclo",
                yaxis_title="Variación %",
                legend=dict(orientation="h",x=0.5,y=1.1,xanchor="center",bgcolor="rgba(0,0,0,0)"),
                hovermode="x unified"
            )
            plotly_dark(fig3,340)
            st.plotly_chart(fig3,use_container_width=True)
        else:
            st.info("No hay suficientes datos para calcular variación entre microciclos.")
    else:
        st.info("Se necesita una columna de microciclo para el gráfico de variación %.")

# ══════════════════════════════════════════════════════════════
# ROUTER Y MAIN
# ══════════════════════════════════════════════════════════════
def render_pagina():
    u=st.session_state.usuario;p=st.session_state.pagina
    if not tiene_acceso(u,p) and p!="admin": st.error("🚫 No tenés acceso.");return
    {"home":pagina_home,"historial":pagina_historial,"estadisticas_medicas":pagina_estadisticas_medicas,"evaluaciones":pagina_evaluaciones,"riesgo_lesion":lambda:mr.pagina_riesgo_lesion(cargar_sheet),"demandas_fisicas":lambda:dfx.pagina_demandas_fisicas(cargar_sheet,pdf_btn),"control_partidos":pagina_control_partidos,"nutricion":pagina_nutricion,"resumen_individual":pagina_resumen,"admin":pagina_admin}.get(p,lambda:st.error("Página no encontrada"))()
    _pdf_flush()

if not st.session_state.logged:
    pagina_login()
else:
    top_bar(logged=True,usuario=st.session_state.usuario)
    render_sidebar()
    render_pagina()
