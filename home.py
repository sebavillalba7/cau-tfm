# frontend/home.py
import streamlit as st
from pathlib import Path
import base64
from datetime import date

ASSETS = Path("assets")

def img_b64(path):
    if path and path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return None

def render(usuario: dict):
    u = usuario
    b64 = img_b64(ASSETS / "escudo_union.png")
    escudo = f'<img src="data:image/png;base64,{b64}" style="width:160px;height:160px;object-fit:contain;filter:drop-shadow(0 0 24px rgba(200,16,46,.4));">' if b64 else '<div style="font-size:120px;">⚽</div>'

    # ── Banner principal ────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:40px 20px 20px;">
        {escudo}
        <div style="font-family:'Bebas Neue',sans-serif;font-size:64px;letter-spacing:6px;
                    color:#fff;line-height:1;margin-top:16px;">CLUB A. UNIÓN</div>
        <div style="color:#c8102e;font-size:16px;font-weight:700;letter-spacing:4px;
                    text-transform:uppercase;margin-top:8px;">Sistema de Rendimiento Físico</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Foto + texto institucional ──────────────────────────────
    st.markdown("---")
    col_foto, col_texto = st.columns([1, 2], gap="large")

    with col_foto:
        foto_path = ASSETS / "foto_home.jpg"
        if foto_path.exists():
            b64f = img_b64(foto_path)
            st.markdown(f'<img src="data:image/jpeg;base64,{b64f}" style="width:100%;border-radius:16px;border:2px solid rgba(200,16,46,.4);">', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="width:100%;aspect-ratio:4/3;background:rgba(200,16,46,.08);
                        border:2px dashed rgba(200,16,46,.3);border-radius:16px;
                        display:flex;align-items:center;justify-content:center;
                        color:#64748b;font-size:13px;text-align:center;padding:20px;">
                📷 Subí una foto como<br><code>assets/foto_home.jpg</code>
            </div>
            """, unsafe_allow_html=True)

    with col_texto:
        st.markdown("""
        <div style="background:rgba(13,26,46,.8);border:1px solid rgba(255,255,255,.08);
                    border-radius:16px;padding:28px;">
            <div style="font-size:11px;color:#c8102e;font-weight:700;letter-spacing:3px;
                        text-transform:uppercase;margin-bottom:8px;">Acerca del sistema</div>
            <div style="font-size:22px;font-weight:800;color:#fff;margin-bottom:12px;line-height:1.2;">
                Plataforma integral de monitorización del rendimiento
            </div>
            <div style="font-size:14px;color:#94a3b8;line-height:1.7;">
                Esta plataforma centraliza toda la información física, médica y deportiva
                del plantel profesional de Club A. Unión, facilitando la toma de decisiones
                del cuerpo técnico, el área médica y la secretaría técnica.<br><br>
                <em>Podés editar este texto desde <code>assets/texto_home.txt</code></em>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── KPIs del día ───────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sec-title">Resumen del día</div>', unsafe_allow_html=True)

    # Intentar cargar datos para mostrar KPIs reales
    try:
        from backend.data_loader import cargar_datos
        gps, lesiones, cmj, nordico, data_jug = cargar_datos()

        total_jugadores = data_jug["JUGADOR"].nunique() if "JUGADOR" in data_jug.columns else 0
        lesiones_activas = lesiones[lesiones["DAY_OFF_DXT"].apply(
            lambda x: float(str(x).replace(",",".")) if str(x).replace(",","").replace(".","").isdigit() else 0
        ) > 0].shape[0] if not lesiones.empty else 0
        anio_actual = date.today().year
        sesiones_anio = gps[gps["AÑO"] == anio_actual].shape[0] if "AÑO" in gps.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 Jugadores", total_jugadores)
        c2.metric("🏥 Lesiones registradas", len(lesiones))
        c3.metric("📡 Sesiones GPS este año", sesiones_anio)
        c4.metric("📅 Hoy", date.today().strftime("%d/%m/%Y"))

    except Exception:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 Jugadores", "—")
        c2.metric("🏥 Lesiones", "—")
        c3.metric("📡 Sesiones GPS", "—")
        c4.metric("📅 Hoy", date.today().strftime("%d/%m/%Y"))

    # ── Bienvenida personalizada ────────────────────────────────
    st.markdown("---")
    from backend.users import AREAS
    area_info = AREAS.get(u["area"], {})
    secciones = area_info.get("secciones", [])

    st.markdown(f"""
    <div style="background:rgba(200,16,46,.07);border:1px solid rgba(200,16,46,.2);
                border-radius:14px;padding:20px 24px;">
        <div style="font-size:13px;color:#c8102e;font-weight:700;letter-spacing:2px;
                    text-transform:uppercase;">Bienvenido/a</div>
        <div style="font-size:20px;font-weight:800;color:#fff;margin:4px 0 8px;">
            {u['nombre']} &nbsp;·&nbsp; {u['rol']}
        </div>
        <div style="font-size:13px;color:#94a3b8;">
            Área: <b style="color:#e2e8f0;">{u['area']}</b> &nbsp;|&nbsp;
            Acceso a <b style="color:#e2e8f0;">{len(secciones)}</b> secciones
        </div>
    </div>
    """, unsafe_allow_html=True)
