import streamlit as st
from pathlib import Path
import base64, hashlib, json, re
import pandas as pd
from datetime import date

st.set_page_config(page_title="CAU · Rendimiento Físico", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800;900&display=swap');
.stApp{background:radial-gradient(circle at top left,rgba(200,16,46,.12),transparent 28%),linear-gradient(135deg,#07101f 0%,#0d1a2e 55%,#07101f 100%);color:#e8ecf4;font-family:'Inter',sans-serif;}
section[data-testid="stSidebar"]{background:#060e1c!important;border-right:1px solid rgba(200,16,46,0.25)!important;}
section[data-testid="stSidebar"] *{color:#e8ecf4!important;}
.stButton>button{background:linear-gradient(135deg,#c8102e,#8b0000)!important;color:#fff!important;border:none!important;border-radius:10px!important;font-weight:700!important;transition:opacity .2s!important;}
.stButton>button:hover{opacity:.85!important;}
.stTextInput input,.stSelectbox>div>div{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(200,16,46,0.4)!important;border-radius:10px!important;color:#e8ecf4!important;}
.login-card{max-width:480px;margin:30px auto 0;padding:36px 32px;border-radius:24px;background:rgba(10,20,38,0.97);border:1px solid rgba(200,16,46,0.3);box-shadow:0 24px 64px rgba(0,0,0,0.5);text-align:center;}
.login-title{font-family:'Bebas Neue',sans-serif;font-size:46px;letter-spacing:4px;color:#fff;line-height:1;}
.login-sub{color:#38bdf8;font-size:14px;font-weight:600;margin:6px 0 24px;}
.sec-title{color:#fff;font-size:18px;font-weight:900;border-left:4px solid #c8102e;padding-left:10px;margin:24px 0 12px;}
[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(13,26,46,.98),rgba(17,28,53,.92));border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:14px;}
</style>""", unsafe_allow_html=True)

AREAS = {
    "Médica":               {"icon":"🏥","secciones":["home","historial","estadisticas_medicas","evaluaciones","resumen_individual"]},
    "Rendimiento":          {"icon":"⚡","secciones":["home","historial","evaluaciones","demandas_fisicas","control_partidos","resumen_individual"]},
    "Secretaría Técnica":   {"icon":"📋","secciones":["home","historial","estadisticas_medicas","evaluaciones","demandas_fisicas","control_partidos","resumen_individual"]},
    "Administración":       {"icon":"🔧","secciones":["home","historial","estadisticas_medicas","evaluaciones","demandas_fisicas","control_partidos","resumen_individual","admin"]},
    "Scout":                {"icon":"🔍","secciones":["home","historial","control_partidos"]},
}

def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

USUARIOS = {
    "dr.garcia":    {"nombre":"Dr. García",     "area":"Médica",             "rol":"Médico",        "pwd":_hash("medica123"),"activo":True},
    "dr.lopez":     {"nombre":"Dr. López",       "area":"Médica",             "rol":"Médico",        "pwd":_hash("medica123"),"activo":True},
    "dr.martinez":  {"nombre":"Dr. Martínez",    "area":"Médica",             "rol":"Médico",        "pwd":_hash("medica123"),"activo":True},
    "kine.perez":   {"nombre":"Lic. Pérez",      "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),  "activo":True},
    "kine.gomez":   {"nombre":"Lic. Gómez",      "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),  "activo":True},
    "kine.diaz":    {"nombre":"Lic. Díaz",       "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),  "activo":True},
    "kine.silva":   {"nombre":"Lic. Silva",      "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),  "activo":True},
    "kine.torres":  {"nombre":"Lic. Torres",     "area":"Médica",             "rol":"Kinesiólogo",   "pwd":_hash("kine123"),  "activo":True},
    "pf.rodriguez": {"nombre":"Prof. Rodríguez", "area":"Rendimiento",        "rol":"PF",            "pwd":_hash("rend123"),  "activo":True},
    "pf.fernandez": {"nombre":"Prof. Fernández", "area":"Rendimiento",        "rol":"PF",            "pwd":_hash("rend123"),  "activo":True},
    "pf.sanchez":   {"nombre":"Prof. Sánchez",   "area":"Rendimiento",        "rol":"PF",            "pwd":_hash("rend123"),  "activo":True},
    "nutri.ruiz":   {"nombre":"Lic. Ruiz",       "area":"Rendimiento",        "rol":"Nutricionista", "pwd":_hash("rend123"),  "activo":True},
    "nutri.mora":   {"nombre":"Lic. Mora",       "area":"Rendimiento",        "rol":"Nutricionista", "pwd":_hash("rend123"),  "activo":True},
    "nutri.vega":   {"nombre":"Lic. Vega",       "area":"Rendimiento",        "rol":"Nutricionista", "pwd":_hash("rend123"),  "activo":True},
    "ct.ramirez":   {"nombre":"Prof. Ramírez",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","pwd":_hash("rend123"),  "activo":True},
    "ct.jimenez":   {"nombre":"Prof. Jiménez",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","pwd":_hash("rend123"),  "activo":True},
    "ct.herrera":   {"nombre":"Prof. Herrera",   "area":"Rendimiento",        "rol":"Cuerpo Técnico","pwd":_hash("rend123"),  "activo":True},
    "st.castro":    {"nombre":"Lic. Castro",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "pwd":_hash("sec123"),   "activo":True},
    "st.vargas":    {"nombre":"Lic. Vargas",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "pwd":_hash("sec123"),   "activo":True},
    "st.medina":    {"nombre":"Lic. Medina",     "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "pwd":_hash("sec123"),   "activo":True},
    "st.guerrero":  {"nombre":"Lic. Guerrero",   "area":"Secretaría Técnica", "rol":"Sec. Técnico",  "pwd":_hash("sec123"),   "activo":True},
    "admin":        {"nombre":"Administrador",   "area":"Administración",     "rol":"Admin",         "pwd":_hash("admin123"), "activo":True},
    "scout.blanco": {"nombre":"Lic. Blanco",     "area":"Scout",              "rol":"Scout",         "pwd":_hash("scout123"), "activo":True},
    "scout.acosta": {"nombre":"Lic. Acosta",     "area":"Scout",              "rol":"Scout",         "pwd":_hash("scout123"), "activo":True},
    "scout.rios":   {"nombre":"Lic. Ríos",       "area":"Scout",              "rol":"Scout",         "pwd":_hash("scout123"), "activo":True},
}

def verificar_login(u, p):
    usr = USUARIOS.get(u.lower().strip())
    if usr and usr["activo"] and usr["pwd"] == _hash(p): return usr
    return None

def tiene_acceso(u, s): return s in AREAS.get(u.get("area",""),{}).get("secciones",[])
def usuarios_por_area(a): return [u for u,d in USUARIOS.items() if d["area"]==a]

SHEETS = {
    "gps":      "https://docs.google.com/spreadsheets/d/1W3hUX8zTPYXzDUSmdW7Nj2fXbEKlp1E2Us7kwNBhR6c/edit?gid=0",
    "lesiones": "https://docs.google.com/spreadsheets/d/1irSkXB8V_D_jZurEGUA9JMkLpE3e0_qad16_orjHDi8/edit?gid=0",
    "cmj":      "https://docs.google.com/spreadsheets/d/1VQLX1R1M0IW8j_TPXbVE8y5qaOA8-2qpj8cL-eGA1VY/edit?gid=1188054203",
    "nordico":  "https://docs.google.com/spreadsheets/d/1fhFajl9ckPYikfIKdBHTORcqQj0802JoNQ8-B3wEJWU/edit?gid=1994839095",
    "data_jug": "https://docs.google.com/spreadsheets/d/1aZ7yXUf3M4NA-7lNp9vlwUU_4tgU7Tecf5w-TrnelY8/edit?gid=0",
}

def gsheet_csv(url):
    sid = re.search(r"/d/([^/]+)", url).group(1)
    gid = (re.search(r"gid=(\d+)", url) or type("",(),{"group":lambda s,x:"0"})()).group(1)
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

for k,v in [("logged",False),("usuario",None),("pagina","home")]:
    if k not in st.session_state: st.session_state[k]=v

ASSETS = Path("assets")
def img_b64(path):
    p=Path(path)
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

def escudo_tag(size=110):
    b64=img_b64(ASSETS/"escudo_union.png")
    return f'<img src="data:image/png;base64,{b64}" style="width:{size}px;height:{size}px;object-fit:contain;">' if b64 else '<div style="font-size:72px;">⚽</div>'

def pagina_login():
    t1,t2,t3=st.tabs(["🔐 Iniciar sesión","📝 Registrarme","🔑 Recuperar contraseña"])
    with t1:
        st.markdown(f'<div class="login-card">{escudo_tag(110)}<div class="login-title">CLUB A. UNIÓN</div><div class="login-sub">Sistema de Rendimiento Físico</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _,col,_=st.columns([1,1.2,1])
        with col:
            area_sel=st.selectbox("Área",["— Seleccioná tu área —"]+list(AREAS.keys()),key="l_area")
            ua=usuarios_por_area(area_sel) if area_sel!="— Seleccioná tu área —" else []
            us=st.selectbox("Usuario",["— Seleccioná usuario —"]+ua,key="l_user",disabled=(area_sel=="— Seleccioná tu área —"))
            pw=st.text_input("Contraseña",type="password",key="l_pwd")
            if st.button("Ingresar →",use_container_width=True):
                if us=="— Seleccioná usuario —": st.error("Seleccioná un usuario.")
                elif not pw: st.warning("Ingresá tu contraseña.")
                else:
                    u=verificar_login(us,pw)
                    if u:
                        st.session_state.logged=True
                        st.session_state.usuario={**u,"username":us}
                        st.session_state.pagina="home"
                        st.rerun()
                    else: st.error("Contraseña incorrecta o usuario inactivo.")
    with t2:
        st.markdown("### Solicitud de acceso")
        st.info("Completá el formulario. El administrador habilitará tu acceso.")
        c1,c2=st.columns(2)
        with c1:
            rn=st.text_input("Nombre completo",key="rn"); ra=st.selectbox("Área",list(AREAS.keys()),key="ra"); ru=st.text_input("Usuario",key="ru")
        with c2:
            rr=st.text_input("Rol / Cargo",key="rr"); re_=st.text_input("Email",key="re"); rp=st.text_input("Contraseña",type="password",key="rp"); rp2=st.text_input("Repetir",type="password",key="rp2")
        if st.button("Enviar solicitud",use_container_width=True):
            if not all([rn,ra,ru,rr,re_,rp]): st.error("Completá todos los campos.")
            elif rp!=rp2: st.error("Las contraseñas no coinciden.")
            else: st.success("✅ Solicitud enviada. El administrador te habilitará el acceso.")
    with t3:
        st.markdown("### Recuperación de contraseña")
        rm=st.text_input("Email institucional",key="rm")
        if st.button("Solicitar recuperación",use_container_width=True):
            if rm and "@" in rm: st.success("✅ Solicitud registrada. Te contactaremos a la brevedad.")
            else: st.error("Email inválido.")

def render_sidebar():
    u=st.session_state.usuario
    with st.sidebar:
        b64=img_b64(ASSETS/"escudo_union.png")
        esc=f'<img src="data:image/png;base64,{b64}" style="width:52px;height:52px;object-fit:contain;">' if b64 else "⚽"
        st.markdown(f'<div style="text-align:center;padding:12px 0;border-bottom:1px solid rgba(200,16,46,.2);margin-bottom:12px;">{esc}<div style="font-family:\'Bebas Neue\',sans-serif;font-size:15px;letter-spacing:3px;margin-top:6px;">CAU · UNIÓN</div><div style="font-size:11px;color:#94a3b8;">{AREAS[u["area"]]["icon"]} {u["nombre"]}</div><div style="font-size:10px;color:#64748b;">{u["rol"]} · {u["area"]}</div></div>', unsafe_allow_html=True)
        st.markdown("**MENÚ**")
        for key,icon,label in [("home","🏠","Inicio"),("historial","👤","Historial Jugadores"),("estadisticas_medicas","🏥","Estadísticas Médicas"),("evaluaciones","⚡","Evaluaciones Físicas"),("demandas_fisicas","📡","Demandas Físicas"),("control_partidos","⚽","Control de Partidos"),("resumen_individual","📄","Resumen Individual")]:
            if tiene_acceso(u,key):
                if st.button(f"{icon}  {label}",key=f"nav_{key}",use_container_width=True):
                    st.session_state.pagina=key; st.rerun()
        if tiene_acceso(u,"admin"):
            st.markdown("---")
            if st.button("🔧  Panel Admin",key="nav_admin",use_container_width=True):
                st.session_state.pagina="admin"; st.rerun()
        st.markdown("---")
        if st.button("🚪  Cerrar sesión",use_container_width=True):
            st.session_state.logged=False; st.session_state.usuario=None; st.rerun()

def pagina_home():
    u=st.session_state.usuario
    st.markdown(f'<div style="text-align:center;padding:32px 20px 16px;">{escudo_tag(140)}<div style="font-family:\'Bebas Neue\',sans-serif;font-size:60px;letter-spacing:6px;color:#fff;line-height:1;margin-top:12px;">CLUB A. UNIÓN</div><div style="color:#c8102e;font-size:15px;font-weight:700;letter-spacing:4px;text-transform:uppercase;margin-top:6px;">Sistema de Rendimiento Físico</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    cf,ct=st.columns([1,2],gap="large")
    with cf:
        foto=img_b64(ASSETS/"foto_home.jpg")
        if foto: st.markdown(f'<img src="data:image/jpeg;base64,{foto}" style="width:100%;border-radius:16px;border:2px solid rgba(200,16,46,.4);">', unsafe_allow_html=True)
        else: st.markdown('<div style="width:100%;aspect-ratio:4/3;background:rgba(200,16,46,.08);border:2px dashed rgba(200,16,46,.3);border-radius:16px;display:flex;align-items:center;justify-content:center;color:#64748b;font-size:13px;text-align:center;padding:20px;">📷 Agregá<br><code>assets/foto_home.jpg</code></div>', unsafe_allow_html=True)
    with ct:
        st.markdown('<div style="background:rgba(13,26,46,.8);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:28px;"><div style="font-size:11px;color:#c8102e;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Acerca del sistema</div><div style="font-size:22px;font-weight:800;color:#fff;margin-bottom:12px;line-height:1.2;">Plataforma integral de monitorización del rendimiento</div><div style="font-size:14px;color:#94a3b8;line-height:1.7;">Esta plataforma centraliza toda la información física, médica y deportiva del plantel profesional de Club A. Unión.</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sec-title">Resumen del plantel</div>', unsafe_allow_html=True)
    try:
        dfs=cargar_datos()
        c1,c2,c3,c4=st.columns(4)
        c1.metric("👥 Jugadores",dfs["data_jug"].shape[0] if not dfs["data_jug"].empty else "—")
        c2.metric("🏥 Registros médicos",dfs["lesiones"].shape[0] if not dfs["lesiones"].empty else "—")
        c3.metric("📡 Sesiones GPS",dfs["gps"].shape[0] if not dfs["gps"].empty else "—")
        c4.metric("📅 Hoy",date.today().strftime("%d/%m/%Y"))
    except Exception:
        c1,c2,c3,c4=st.columns(4)
        c1.metric("👥 Jugadores","—"); c2.metric("🏥 Registros","—"); c3.metric("📡 Sesiones","—"); c4.metric("📅 Hoy",date.today().strftime("%d/%m/%Y"))
    st.markdown(f'<div style="background:rgba(200,16,46,.07);border:1px solid rgba(200,16,46,.2);border-radius:14px;padding:20px 24px;margin-top:16px;"><div style="font-size:12px;color:#c8102e;font-weight:700;letter-spacing:2px;text-transform:uppercase;">Bienvenido/a</div><div style="font-size:20px;font-weight:800;color:#fff;margin:4px 0 6px;">{u["nombre"]} · {u["rol"]}</div><div style="font-size:13px;color:#94a3b8;">Área: <b style="color:#e2e8f0;">{u["area"]}</b></div></div>', unsafe_allow_html=True)

def pagina_construccion(nombre):
    st.markdown(f'<div class="sec-title">🚧 {nombre}</div>', unsafe_allow_html=True)
    st.info("Esta sección está siendo desarrollada. Volvé pronto.")

def pagina_admin():
    st.markdown('<div class="sec-title">🔧 Panel de Administración</div>', unsafe_allow_html=True)
    st.success("✅ No hay solicitudes pendientes.")
    rows=[{"Usuario":k,"Nombre":v["nombre"],"Área":v["area"],"Rol":v["rol"]} for k,v in USUARIOS.items()]
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

def render_pagina():
    u=st.session_state.usuario; p=st.session_state.pagina
    if not tiene_acceso(u,p) and p!="admin": st.error("🚫 No tenés acceso."); return
    pages={"home":pagina_home,"historial":lambda:pagina_construccion("Historial Jugadores"),"estadisticas_medicas":lambda:pagina_construccion("Estadísticas Médicas"),"evaluaciones":lambda:pagina_construccion("Evaluaciones Físicas"),"demandas_fisicas":lambda:pagina_construccion("Demandas Físicas"),"control_partidos":lambda:pagina_construccion("Control de Partidos"),"resumen_individual":lambda:pagina_construccion("Resumen Individual"),"admin":pagina_admin}
    pages.get(p, lambda: st.error("Página no encontrada"))()

if not st.session_state.logged:
    pagina_login()
else:
    render_sidebar()
    render_pagina()
