import streamlit as st
from pathlib import Path
import base64, hashlib, re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime

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
AREAS={"Médica":{"icon":"🏥","secciones":["home","historial","estadisticas_medicas","evaluaciones","resumen_individual"]},"Rendimiento":{"icon":"⚡","secciones":["home","historial","evaluaciones","demandas_fisicas","control_partidos","resumen_individual"]},"Secretaría Técnica":{"icon":"📋","secciones":["home","historial","estadisticas_medicas","evaluaciones","demandas_fisicas","control_partidos","resumen_individual"]},"Administración":{"icon":"🔧","secciones":["home","historial","estadisticas_medicas","evaluaciones","demandas_fisicas","control_partidos","resumen_individual","admin"]},"Scout":{"icon":"🔍","secciones":["home","historial","control_partidos"]}}
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
SHEETS={"historial":"https://docs.google.com/spreadsheets/d/1Ppy3Mkz3ojqlcGAcxhNlqnGy5o2GmBHmdL9IZdRh9b0/edit?gid=0","lesiones":"https://docs.google.com/spreadsheets/d/1irSkXB8V_D_jZurEGUA9JMkLpE3e0_qad16_orjHDi8/edit?gid=0","cmj":"https://docs.google.com/spreadsheets/d/1VQLX1R1M0IW8j_TPXbVE8y5qaOA8-2qpj8cL-eGA1VY/edit?gid=1188054203","cmj1pp":"https://docs.google.com/spreadsheets/d/16ugXQ5hEnMa9bh_Ma1IDDaPq6gNq4QVPTRwQyVnz3oc/edit?gid=305963248","nordico":"https://docs.google.com/spreadsheets/d/1fhFajl9ckPYikfIKdBHTORcqQj0802JoNQ8-B3wEJWU/edit?gid=1994839095","vbt":"https://docs.google.com/spreadsheets/d/1NjVz_ivHKRrtai18ogjMQuQA6EYh3Q-WLDiNOErYO-Q/edit?gid=0","gps":"https://docs.google.com/spreadsheets/d/1W3hUX8zTPYXzDUSmdW7Nj2fXbEKlp1E2Us7kwNBhR6c/edit?gid=0","partidos":"https://docs.google.com/spreadsheets/d/17EiRiX-Tjlor0SfZvz-Wzfohz07calbA_26DKd4XL5g/edit?gid=2140450866"}

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

def pdf_btn():
    st.markdown('<div style="display:flex;justify-content:flex-end;margin-bottom:10px;"><button onclick="window.print()" style="background:linear-gradient(135deg,#c8102e,#8b0000);color:#fff;border:none;border-radius:8px;padding:7px 16px;font-weight:700;font-size:12px;cursor:pointer;">📄 Exportar PDF</button></div>',unsafe_allow_html=True)

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
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=20,b=0),height=h,font_color="#e2e8f0",
        legend=dict(bgcolor="rgba(0,0,0,0)",font_color="#e2e8f0"))
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)",color="#64748b")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)",color="#64748b")
    return fig


def html_table(df, highlight_cols=None, num_format=None, max_rows=20, height=420):
    """Tabla dark con headers coloreados, valores centrados, escala de color. Scroll si hay más de max_rows."""
    if df.empty:
        st.info("Sin datos."); return
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
            cells += f'<td style="text-align:center;padding:9px 12px;border-bottom:1px solid rgba(255,255,255,0.05);{style}">{display}</td>'
        rows_html += f"<tr>{cells}</tr>"

    headers = ""
    for col in df.columns:
        headers += f'<th style="text-align:center;padding:10px 12px;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#60a5fa;background:rgba(26,90,180,0.25);border-bottom:2px solid rgba(26,90,180,0.4);">{col}</th>'

    scroll_style = f"overflow-y:auto;max-height:{height}px;" if len(df) > max_rows else ""
    st.markdown(f'''
    <div style="background:#071428;border:1px solid rgba(26,90,180,0.3);border-radius:14px;overflow:hidden;margin-top:8px;">
        <div style="{scroll_style}">
        <table style="width:100%;border-collapse:collapse;">
            <thead><tr style="position:sticky;top:0;z-index:2;">{headers}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
    </div>''', unsafe_allow_html=True)

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
        for key,icon,label in [("home","🏠","Inicio"),("historial","👤","Historial Jugadores"),("estadisticas_medicas","🏥","Estadísticas Médicas"),("evaluaciones","⚡","Evaluaciones Físicas"),("demandas_fisicas","📡","Demandas Físicas"),("control_partidos","⚽","Control de Partidos"),("resumen_individual","📄","Resumen Individual")]:
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
    u=st.session_state.usuario; pdf_btn()
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

    # ── Fila 2: N° lesiones x estructura M-E  +  N° lesiones x región ──
    st.markdown("---")
    est_me_col=next((c for c in les_df.columns if any(x in c.lower() for x in ["est_m","estructura","musculo","isquio","cuad","adu"])),est_col)

    has_est = est_me_col is not None
    has_reg = region_col is not None

    if has_est and has_reg:
        b1, b2 = st.columns(2)
    elif has_est or has_reg:
        b1 = b2 = st  # solo uno, usar ancho completo

    if has_est:
        with b1:
            st.markdown('<div class="subsec">N° lesiones x est. M-E</div>',unsafe_allow_html=True)
            vc=les_df[est_me_col].value_counts().reset_index(); vc.columns=["Estructura","N°"]
            vc=vc.sort_values("N°",ascending=True)
            n_filas=len(vc)
            alto_est=max(280, n_filas*36)
            fig4=px.bar(vc,x="N°",y="Estructura",orientation="h",text="N°",
                       color_discrete_sequence=["#4299e1"],template="plotly_dark")
            fig4.update_traces(textposition="outside",textfont_color="#fff",
                              marker_color="#4299e1",texttemplate="%{text:.0f}")
            fig4.update_layout(yaxis=dict(autorange="reversed"))
            plotly_dark(fig4, alto_est)
            st.plotly_chart(fig4,use_container_width=True)

    if has_reg:
        with b2:
            st.markdown('<div class="subsec">N° lesiones x región</div>',unsafe_allow_html=True)
            vc_r=les_df[region_col].value_counts().reset_index(); vc_r.columns=["Región","N°"]
            vc_r=vc_r.sort_values("N°",ascending=True)
            n_filas_r=len(vc_r)
            alto_reg=max(280, n_filas_r*36)
            fig5=px.bar(vc_r,x="N°",y="Región",orientation="h",text="N°",
                       color_discrete_sequence=["#48bb78"],template="plotly_dark")
            fig5.update_traces(textposition="outside",textfont_color="#fff",
                              marker_color="#48bb78",texttemplate="%{text:.0f}")
            fig5.update_layout(yaxis=dict(autorange="reversed"))
            plotly_dark(fig5, alto_reg)
            st.plotly_chart(fig5,use_container_width=True)

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
def pagina_control_partidos():
    st.markdown('<div class="sec-title">⚽ Control de Partidos</div>',unsafe_allow_html=True)
    pdf_btn()
    df=cargar_sheet("partidos")
    if df.empty: no_data("Control de Partidos"); return

    jcol=jug_col_find(df)
    dff,_=filtro_anio_widget(df,"part")
    fc1,fc2=st.columns(2)
    with fc1: jsel=st.selectbox("Jugador",["Todos"]+sorted(dff[jcol].dropna().astype(str).unique().tolist()),key="part_jug")
    if jsel!="Todos": dff=dff[dff[jcol].astype(str)==jsel]

    c1,c2,c3=st.columns(3)
    c1.metric("📋 Registros",len(dff))
    min_col=next((c for c in dff.columns if "min" in c.lower()),None)
    if min_col:
        mvals=to_num_col(dff[min_col])
        c2.metric("⏱️ Min. totales",int(mvals.sum()) if not mvals.isna().all() else "—")
        c3.metric("⏱️ Min. promedio",round(mvals.mean(),1) if not mvals.isna().all() else "—")

    st.markdown('<div style="background:rgba(26,90,180,0.08);border:1px solid rgba(26,90,180,0.2);border-radius:12px;padding:14px;margin:12px 0;"><div style="font-size:12px;font-weight:700;color:#93c5fd;margin-bottom:4px;">🔌 API de Fútbol Argentino — Próximamente</div><div style="font-size:12px;color:#64748b;">Integración con <b style="color:#e2e8f0;">API-Football</b> para estadísticas de Liga Profesional en tiempo real.</div></div>',unsafe_allow_html=True)
    num_p=[c for c in dff.columns if to_num_col(dff[c]).notna().sum()>len(dff)*0.3 and c not in ["AÑO","_fecha"]]
    show_p=dff[[c for c in dff.columns if not c.startswith("_")]].reset_index(drop=True)
    html_table(show_p, highlight_cols=num_p)

# ══════════════════════════════════════════════════════════════
# RESUMEN INDIVIDUAL
# ══════════════════════════════════════════════════════════════
def pagina_resumen():
    st.markdown('<div class="sec-title">📄 Resumen Individual</div>',unsafe_allow_html=True)
    pdf_btn()
    hist=cargar_sheet("historial")
    if hist.empty: no_data("Historial"); return
    jcol=jug_col_find(hist)
    jugadores=sorted(hist[jcol].dropna().astype(str).unique().tolist())
    c1,c2=st.columns([2,1])
    with c1: jsel=st.selectbox("Jugador",jugadores,key="res_jug")
    with c2: secs=st.multiselect("Incluir",["GPS","CMJ","Nórdico","Lesiones","VBT"],default=["GPS","CMJ","Lesiones"],key="res_secs")

    row_df=hist[hist[jcol].astype(str)==jsel]
    if len(row_df)>0:
        row=row_df.iloc[0]
        pos_col=pos_col_find(hist)
        edad_col=next((c for c in hist.columns if "edad" in c.lower()),None)
        nacio_col=next((c for c in hist.columns if "nacion" in c.lower() or "pais" in c.lower()),None)
        foto_col=next((c for c in hist.columns if "foto" in c.lower() or "url" in c.lower()),None)
        pos=str(row[pos_col]) if pos_col else "—"
        edad=str(row[edad_col]) if edad_col else "—"
        nacio=str(row[nacio_col]) if nacio_col else "—"
        foto_url=str(row[foto_col]) if foto_col else "nan"
        avatar=f'<img src="{foto_url}" style="width:90px;height:90px;border-radius:50%;object-fit:cover;border:3px solid rgba(200,16,46,.5);">' if foto_url.startswith("http") else '<div style="width:90px;height:90px;border-radius:50%;background:rgba(200,16,46,.15);display:flex;align-items:center;justify-content:center;font-size:48px;">👤</div>'
        st.markdown(f'<div style="background:rgba(8,18,38,.95);border:1px solid rgba(200,16,46,.25);border-radius:20px;padding:24px;margin:12px 0;display:flex;align-items:center;gap:20px;">{avatar}<div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:32px;letter-spacing:2px;color:#fff;">{jsel}</div><div style="margin-top:8px;"><span class="chip">{pos}</span><span class="chip chip-blue">{nacio}</span><span class="chip chip-green">Edad: {edad}</span></div></div></div>',unsafe_allow_html=True)

    def mostrar_sec(key,label):
        d=cargar_sheet(key)
        if d.empty: return
        jc=jug_col_find(d)
        ds=d[d[jc].astype(str).str.lower()==jsel.lower()]
        if ds.empty: st.info(f"Sin datos de {label}."); return
        num_cols=[c for c in ds.columns if to_num_col(ds[c]).notna().sum()>len(ds)*0.2 and c not in ["AÑO","_fecha"]]
        cs=st.columns(min(4,len(num_cols)))
        for i,col in enumerate(num_cols[:4]):
            vals=to_num_col(ds[col]).dropna()
            cs[i].metric(col[:20],round(vals.mean(),2) if len(vals)>0 else "—")

    if "GPS" in secs: st.markdown('<div class="subsec">📡 GPS</div>',unsafe_allow_html=True); mostrar_sec("gps","GPS")
    if "CMJ" in secs: st.markdown('<div class="subsec">🦵 CMJ</div>',unsafe_allow_html=True); mostrar_sec("cmj","CMJ")
    if "Nórdico" in secs: st.markdown('<div class="subsec">💪 Nórdico</div>',unsafe_allow_html=True); mostrar_sec("nordico","Nórdico")
    if "VBT" in secs: st.markdown('<div class="subsec">⚡ VBT</div>',unsafe_allow_html=True); mostrar_sec("vbt","VBT")
    if "Lesiones" in secs:
        st.markdown('<div class="subsec">🏥 Historial médico</div>',unsafe_allow_html=True)
        les=cargar_sheet("lesiones")
        if not les.empty:
            jc=jug_col_find(les)
            dl=les[les[jc].astype(str).str.lower()==jsel.lower()]
            if not dl.empty: st.dataframe(dl,use_container_width=True,hide_index=True)
            else: st.info(f"Sin registros médicos para {jsel}.")

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
# ROUTER Y MAIN
# ══════════════════════════════════════════════════════════════
def render_pagina():
    u=st.session_state.usuario;p=st.session_state.pagina
    if not tiene_acceso(u,p) and p!="admin": st.error("🚫 No tenés acceso.");return
    {"home":pagina_home,"historial":pagina_historial,"estadisticas_medicas":pagina_estadisticas_medicas,"evaluaciones":pagina_evaluaciones,"demandas_fisicas":pagina_demandas,"control_partidos":pagina_control_partidos,"resumen_individual":pagina_resumen,"admin":pagina_admin}.get(p,lambda:st.error("Página no encontrada"))()

if not st.session_state.logged:
    pagina_login()
else:
    top_bar(logged=True,usuario=st.session_state.usuario)
    render_sidebar()
    render_pagina()
