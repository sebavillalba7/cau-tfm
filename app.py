import streamlit as st
from pathlib import Path
import base64

# ── Configuración de página (DEBE ser lo primero) ──────────────────
st.set_page_config(
    page_title="CAU · Rendimiento Físico",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports internos ───────────────────────────────────────────────
from backend.users import (
    AREAS, verificar_login, tiene_acceso,
    registrar_usuario, cargar_pendientes, aprobar_usuario,
    usuarios_por_area
)

# ══════════════════════════════════════════════════════════════════
# CSS GLOBAL — responsivo, dark theme, colores del club
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Base ── */
.stApp {
    background: radial-gradient(circle at top left, rgba(200,16,46,.12), transparent 28%),
                linear-gradient(135deg, #07101f 0%, #0d1a2e 55%, #07101f 100%);
    color: #e8ecf4;
    font-family: 'Inter', sans-serif;
}

/* ── Header ── */
header[data-testid="stHeader"] {
    background: linear-gradient(90deg, #c8102e 0%, #8b0000 100%) !important;
    border-bottom: 2px solid rgba(255,255,255,0.12) !important;
}
header[data-testid="stHeader"]::after {
    content: 'CLUB A. UNIÓN · Sistema de Rendimiento';
    position: absolute; left: 50%; top: 50%;
    transform: translate(-50%,-50%);
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px; letter-spacing: 5px; color: #fff;
    pointer-events: none; white-space: nowrap;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #060e1c !important;
    border-right: 1px solid rgba(200,16,46,0.25) !important;
    min-width: 240px !important;
}
section[data-testid="stSidebar"] * { color: #e8ecf4 !important; }

/* ── Botones ── */
.stButton > button {
    background: linear-gradient(135deg, #c8102e, #8b0000) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── Inputs ── */
.stTextInput input, .stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(200,16,46,0.4) !important;
    border-radius: 10px !important;
    color: #e8ecf4 !important;
}

/* ── Login card ── */
.login-card {
    max-width: 480px; margin: 30px auto 0 auto;
    padding: 36px 32px; border-radius: 24px;
    background: rgba(10,20,38,0.97);
    border: 1px solid rgba(200,16,46,0.3);
    box-shadow: 0 24px 64px rgba(0,0,0,0.5);
    text-align: center;
}
.login-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 46px; letter-spacing: 4px; color: #fff; line-height: 1;
}
.login-sub { color: #38bdf8; font-size: 14px; font-weight: 600; margin: 6px 0 24px; }

/* ── Sidebar escudo ── */
.sb-escudo {
    display: flex; flex-direction: column; align-items: center;
    padding: 16px 0 12px; border-bottom: 1px solid rgba(200,16,46,0.2);
    margin-bottom: 12px;
}
.sb-club { font-family: 'Bebas Neue', sans-serif; font-size: 16px; letter-spacing: 3px; color: #fff; margin-top: 6px; }
.sb-user { font-size: 11px; color: #94a3b8; margin-top: 2px; }

/* ── Menú items ── */
.menu-area {
    font-size: 10px; font-weight: 700; letter-spacing: 2px;
    color: #c8102e; text-transform: uppercase;
    padding: 12px 0 4px; border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 8px;
}

/* ── Responsivo móvil ── */
@media (max-width: 768px) {
    .login-card { margin: 10px; padding: 24px 16px; }
    .login-title { font-size: 34px; }
    header[data-testid="stHeader"]::after { font-size: 13px; letter-spacing: 2px; }
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(13,26,46,.98), rgba(17,28,53,.92));
    border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 14px;
}
[data-testid="stMetricLabel"] p { color: #93c5fd !important; font-weight: 700 !important; font-size: 11px !important; }
[data-testid="stMetricValue"]  { color: #fff !important; font-weight: 900 !important; }

/* ── Section title ── */
.sec-title {
    color: #fff; font-size: 18px; font-weight: 900;
    border-left: 4px solid #c8102e; padding-left: 10px;
    margin: 24px 0 12px;
}

/* ── Dataframes ── */
.stDataFrame { border: 1px solid rgba(255,255,255,.1); border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
ASSETS = Path("assets")

def img_b64(path: Path) -> str | None:
    if path and path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return None

def escudo_html(css_class: str = "login-logo", size: int = 110) -> str:
    b64 = img_b64(ASSETS / "escudo_union.png")
    if b64:
        return f'<img src="data:image/png;base64,{b64}" style="width:{size}px;height:{size}px;object-fit:contain;">'
    return '<div style="font-size:72px;line-height:1;">⚽</div>'


# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
for key, val in [("logged", False), ("usuario", None), ("pagina", "home")]:
    if key not in st.session_state:
        st.session_state[key] = val


# ══════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════
def pagina_login():
    tab_login, tab_registro, tab_recovery = st.tabs(["🔐 Iniciar sesión", "📝 Registrarme", "🔑 Recuperar contraseña"])

    # ── TAB LOGIN ────────────────────────────────────────────────
    with tab_login:
        st.markdown(f"""
        <div class="login-card">
            {escudo_html(size=110)}
            <div class="login-title">CLUB A. UNIÓN</div>
            <div class="login-sub">Sistema de Rendimiento Físico</div>
        </div>
        """, unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 1.2, 1])
        with col_c:
            st.markdown("#### Acceso al sistema")

            # Paso 1: seleccionar área
            area_sel = st.selectbox(
                "Área",
                ["— Seleccioná tu área —"] + list(AREAS.keys()),
                key="login_area"
            )

            # Paso 2: usuario filtrado por área
            usuarios_area = usuarios_por_area(area_sel) if area_sel != "— Seleccioná tu área —" else []
            usuario_sel = st.selectbox(
                "Usuario",
                ["— Seleccioná usuario —"] + usuarios_area,
                key="login_user",
                disabled=(area_sel == "— Seleccioná tu área —")
            )

            pwd = st.text_input("Contraseña", type="password", key="login_pwd")

            if st.button("Ingresar →", use_container_width=True, key="btn_login"):
                if usuario_sel == "— Seleccioná usuario —":
                    st.error("Seleccioná un usuario.")
                elif not pwd:
                    st.warning("Ingresá tu contraseña.")
                else:
                    u = verificar_login(usuario_sel, pwd)
                    if u:
                        st.session_state.logged = True
                        st.session_state.usuario = {**u, "username": usuario_sel}
                        st.session_state.pagina = "home"
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta o usuario inactivo.")

    # ── TAB REGISTRO ─────────────────────────────────────────────
    with tab_registro:
        st.markdown("### Solicitud de acceso")
        st.info("Completá el formulario. El administrador recibirá tu solicitud y te habilitará el acceso.")

        col1, col2 = st.columns(2)
        with col1:
            r_nombre   = st.text_input("Nombre completo", key="r_nombre")
            r_area     = st.selectbox("Área", list(AREAS.keys()), key="r_area")
            r_username = st.text_input("Usuario (sin espacios)", key="r_user")
        with col2:
            r_rol      = st.text_input("Rol / Cargo", key="r_rol")
            r_email    = st.text_input("Email institucional", key="r_email")
            r_pwd      = st.text_input("Contraseña", type="password", key="r_pwd")
            r_pwd2     = st.text_input("Repetir contraseña", type="password", key="r_pwd2")

        if st.button("Enviar solicitud", use_container_width=True, key="btn_registro"):
            if not all([r_nombre, r_area, r_username, r_rol, r_email, r_pwd]):
                st.error("Completá todos los campos.")
            elif r_pwd != r_pwd2:
                st.error("Las contraseñas no coinciden.")
            elif " " in r_username:
                st.error("El usuario no puede tener espacios.")
            else:
                ok = registrar_usuario(r_username.lower(), r_nombre, r_area, r_rol, r_email, r_pwd)
                if ok:
                    st.success("✅ Solicitud enviada. El administrador te habilitará el acceso pronto.")
                else:
                    st.error("El nombre de usuario ya existe. Elegí otro.")

    # ── TAB RECOVERY ─────────────────────────────────────────────
    with tab_recovery:
        st.markdown("### Recuperación de contraseña")
        st.info("Ingresá tu email institucional y el administrador te enviará una nueva contraseña temporal.")
        r_mail = st.text_input("Email institucional", key="rec_mail")
        if st.button("Solicitar recuperación", use_container_width=True, key="btn_recovery"):
            if not r_mail:
                st.warning("Ingresá tu email.")
            elif "@" not in r_mail:
                st.error("Email inválido.")
            else:
                # En producción: envío automático de email con smtplib o SendGrid
                st.success("✅ Solicitud registrada. El administrador te contactará a la brevedad.")
                st.caption("En la próxima versión esto enviará un email automático.")


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
def render_sidebar():
    u = st.session_state.usuario
    area = u["area"]

    with st.sidebar:
        # Escudo + usuario
        b64 = img_b64(ASSETS / "escudo_union.png")
        escudo = f'<img src="data:image/png;base64,{b64}" style="width:54px;height:54px;object-fit:contain;">' if b64 else "⚽"
        st.markdown(f"""
        <div class="sb-escudo">
            {escudo}
            <div class="sb-club">CAU · UNIÓN</div>
            <div class="sb-user">{AREAS[area]['icon']} {u['nombre']} · {u['rol']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**MENÚ**")

        # ── Navegación por secciones permitidas ──────────────────
        secciones_visibles = {
            "home":               ("🏠", "Inicio"),
            "historial":          ("👤", "Historial Jugadores"),
            "estadisticas_medicas": ("🏥", "Estadísticas Médicas"),
            "evaluaciones":       ("⚡", "Evaluaciones Físicas"),
            "demandas_fisicas":   ("📡", "Demandas Físicas"),
            "control_partidos":   ("⚽", "Control de Partidos"),
            "resumen_individual": ("📄", "Resumen Individual"),
        }

        for key, (icon, label) in secciones_visibles.items():
            if tiene_acceso(u, key):
                activo = st.session_state.pagina == key
                estilo = "background:rgba(200,16,46,.15);border-radius:8px;padding:2px 0;" if activo else ""
                if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.pagina = key
                    st.rerun()

        # ── Admin: aprobar usuarios ───────────────────────────────
        if tiene_acceso(u, "admin"):
            st.markdown('<div class="menu-area">Administración</div>', unsafe_allow_html=True)
            if st.button("🔧  Panel Admin", key="nav_admin", use_container_width=True):
                st.session_state.pagina = "admin"
                st.rerun()

        st.markdown("---")
        if st.button("🚪  Cerrar sesión", use_container_width=True, key="btn_logout"):
            st.session_state.logged = False
            st.session_state.usuario = None
            st.session_state.pagina = "home"
            st.rerun()


# ══════════════════════════════════════════════════════════════════
# PÁGINAS (imports lazy para no cargar todo al inicio)
# ══════════════════════════════════════════════════════════════════
def render_pagina(pagina: str):
    u = st.session_state.usuario

    if pagina == "home":
        from frontend.home import render
        render(u)

    elif pagina == "historial":
        if tiene_acceso(u, "historial"):
            from frontend.historial import render
            render(u)
        else:
            st.error("🚫 No tenés acceso a esta sección.")

    elif pagina == "estadisticas_medicas":
        if tiene_acceso(u, "estadisticas_medicas"):
            from frontend.estadisticas_medicas import render
            render(u)
        else:
            st.error("🚫 No tenés acceso a esta sección.")

    elif pagina == "evaluaciones":
        if tiene_acceso(u, "evaluaciones"):
            from frontend.evaluaciones import render
            render(u)
        else:
            st.error("🚫 No tenés acceso a esta sección.")

    elif pagina == "demandas_fisicas":
        if tiene_acceso(u, "demandas_fisicas"):
            from frontend.demandas_fisicas import render
            render(u)
        else:
            st.error("🚫 No tenés acceso a esta sección.")

    elif pagina == "control_partidos":
        if tiene_acceso(u, "control_partidos"):
            from frontend.control_partidos import render
            render(u)
        else:
            st.error("🚫 No tenés acceso a esta sección.")

    elif pagina == "resumen_individual":
        if tiene_acceso(u, "resumen_individual"):
            from frontend.resumen_individual import render
            render(u)
        else:
            st.error("🚫 No tenés acceso a esta sección.")

    elif pagina == "admin":
        if tiene_acceso(u, "admin"):
            render_admin()
        else:
            st.error("🚫 No tenés acceso a esta sección.")


# ══════════════════════════════════════════════════════════════════
# PANEL ADMIN
# ══════════════════════════════════════════════════════════════════
def render_admin():
    st.markdown('<div class="sec-title">Panel de Administración</div>', unsafe_allow_html=True)
    pendientes = cargar_pendientes()
    sin_aprobar = {u: d for u, d in pendientes.items() if not d.get("aprobado")}

    if not sin_aprobar:
        st.success("✅ No hay solicitudes pendientes.")
    else:
        st.warning(f"⚠️ {len(sin_aprobar)} solicitud(es) pendiente(s) de aprobación.")
        for username, datos in sin_aprobar.items():
            with st.expander(f"👤 {datos['nombre']} — {datos['area']} · {datos['rol']}"):
                st.write(f"**Email:** {datos['email']}")
                st.write(f"**Usuario:** `{username}`")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Aprobar", key=f"apr_{username}"):
                        aprobar_usuario(username)
                        st.success(f"Usuario {username} aprobado.")
                        st.rerun()
                with col2:
                    if st.button("❌ Rechazar", key=f"rec_{username}"):
                        del pendientes[username]
                        from backend.users import guardar_pendientes
                        guardar_pendientes(pendientes)
                        st.warning(f"Usuario {username} rechazado.")
                        st.rerun()


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
if not st.session_state.logged:
    pagina_login()
else:
    render_sidebar()
    render_pagina(st.session_state.pagina)
