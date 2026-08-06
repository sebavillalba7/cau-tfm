# ════════════════════════════════════════════════════════════════════════
#  pdf_export.py  ·  TFM CAU — Exportación PDF real con fpdf2
#
#  Reemplaza el pdf_btn() anterior, que usaba onclick="window.print()".
#  Ese enfoque NO funcionaba: Streamlit sanitiza los atributos onclick del
#  HTML inyectado con unsafe_allow_html, así que el botón se dibujaba pero
#  el handler nunca se conectaba.
#
#  Acá generamos un PDF de verdad en el servidor con fpdf2 y lo servimos
#  con st.download_button (que sí es un widget nativo de Streamlit).
#
#  requirements.txt →  fpdf2>=2.7.0
# ════════════════════════════════════════════════════════════════════════
from datetime import datetime
from pathlib import Path

import pandas as pd
from fpdf import FPDF

__version__ = "2026.07.17"

ROJO = (200, 16, 46)
AZUL = (11, 31, 61)
GRIS = (100, 116, 139)
BLANCO = (255, 255, 255)
NEGRO = (15, 23, 42)


def _clean(txt):
    """
    fpdf2 con fuentes core (Helvetica) codifica en latin-1.
    Los emojis y símbolos fuera de latin-1 rompen output(). Los quitamos,
    conservando los acentos y la ñ (que sí son latin-1).
    """
    s = str(txt)
    out = []
    for ch in s:
        try:
            ch.encode("latin-1")
            out.append(ch)
        except UnicodeEncodeError:
            out.append("")
    return "".join(out).strip()


def _fmt_valor(v):
    """Formatea cualquier valor de celda para el PDF. Antes un NaN llegaba a
    tabla() como float y se imprimia literalmente 'nan' (o 'None' si venia de
    un str()). Aca todo eso se normaliza a '—', consistente en toda la app."""
    if v is None:
        return "-"
    if isinstance(v, float):
        if pd.isna(v):
            return "-"
        return f"{int(v):,}" if v == int(v) else f"{v:,.1f}"
    if isinstance(v, pd.Timestamp):
        return "-" if pd.isna(v) else v.strftime("%d/%m/%Y")
    try:
        if pd.isna(v):
            return "-"
    except (TypeError, ValueError):
        pass
    s = str(v).strip()
    if s.lower() in ("nan", "none", "<na>", "nat", ""):
        return "-"
    return s


# Paleta para color-codear columnas categoricas (TIPO, LESION, POS, etc.)
# en tablas simples, para que no se vean a planilla de Excel monocroma.
PALETA_CAT = [(200, 16, 46), (37, 99, 235), (22, 163, 74), (217, 119, 6),
              (124, 58, 237), (8, 145, 178), (219, 39, 119), (101, 163, 13)]


def _color_categoria(v):
    s = str(v).strip().upper()
    if not s or s in ("NAN", "NONE", "-"):
        return NEGRO
    return PALETA_CAT[sum(ord(c) for c in s) % len(PALETA_CAT)]


class ReportePDF(FPDF):
    """PDF con header/footer institucional del Club A. Unión."""

    def __init__(self, titulo="Informe", subtitulo="", escudo=None, orientacion="P"):
        super().__init__(orientation=orientacion, unit="mm", format="A4")
        self.orientacion = orientacion
        self.ancho_util = 273 if orientacion == "L" else 186
        self.titulo = _clean(titulo)
        self.subtitulo = _clean(subtitulo)
        self.escudo = escudo if escudo and Path(escudo).exists() else None
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(12, 12, 12)

    def header(self):
        w = 297 if self.orientacion == "L" else 210
        self.set_fill_color(*AZUL)
        self.rect(0, 0, w, 24, "F")
        self.set_fill_color(*ROJO)
        self.rect(0, 24, w, 1.2, "F")
        if self.escudo:
            try:
                self.image(str(self.escudo), x=12, y=3.5, h=17)
            except Exception:
                pass
        self.set_xy(34 if self.escudo else 12, 6)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*BLANCO)
        self.cell(0, 7, self.titulo, ln=1)
        self.set_xy(34 if self.escudo else 12, 14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(180, 190, 205)
        self.cell(0, 5, self.subtitulo or "Club A. Union - Data Intelligence", ln=1)
        self.set_y(31)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*GRIS)
        gen = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 5, _clean(f"Club A. Union - Area de Rendimiento Fisico  |  Generado {gen}"), 0, 0, "L")
        self.cell(0, 5, f"Pag. {self.page_no()}/{{nb}}", 0, 0, "R")

    # ── bloques reutilizables ────────────────────────────────────────
    def seccion(self, num, texto):
        self.ln(1)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*ROJO)
        self.cell(8, 6, _clean(str(num)), 0, 0)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*NEGRO)
        self.cell(0, 6, _clean(texto).upper(), ln=1)
        self.set_draw_color(225, 230, 238)
        self.line(12, self.get_y() + 0.5, 12 + self.ancho_util, self.get_y() + 0.5)
        self.ln(2.5)

    def parrafo(self, texto):
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(70, 85, 105)
        self.multi_cell(0, 4.4, _clean(texto))
        self.ln(1.5)

    def kpis(self, pares, por_fila=None):
        """pares: lista de (label, valor) o (label, valor, color_rgb)."""
        if not pares:
            return
        por_fila = por_fila or (9 if self.orientacion == "L" else 4)
        ancho = (self.ancho_util - (por_fila - 1) * 3) / por_fila
        for i in range(0, len(pares), por_fila):
            fila = pares[i:i + por_fila]
            y0 = self.get_y()
            for j, item in enumerate(fila):
                lab, val = item[0], item[1]
                col = item[2] if len(item) > 2 else NEGRO
                x = 12 + j * (ancho + 3)
                self.set_xy(x, y0)
                self.set_fill_color(246, 248, 251)
                self.set_draw_color(225, 230, 238)
                self.rect(x, y0, ancho, 15, "DF")
                self.set_fill_color(*ROJO)
                self.rect(x, y0, ancho, 0.9, "F")
                self.set_xy(x + 2, y0 + 2.2)
                self.set_font("Helvetica", "", 5.8)
                self.set_text_color(*GRIS)
                self.cell(ancho - 4, 3, _clean(str(lab)).upper()[:22], ln=2, align="C")
                self.set_x(x + 2)
                self.set_font("Helvetica", "B", 11)
                self.set_text_color(*col)
                self.cell(ancho - 4, 7, _clean(_fmt_valor(val))[:14], ln=2, align="C")
            self.set_y(y0 + 18)

    def tabla_color(self, df, estilos=None, max_filas=250):
        """
        Tabla con color por celda (replica el semaforo del Power BI).
        estilos: DataFrame de la misma forma con "bg_hex|fg_hex" o "" por celda.
        """
        if df is None or df.empty:
            self.parrafo("Sin datos para el periodo seleccionado.")
            return
        d = df.head(max_filas)
        est = estilos.head(max_filas) if estilos is not None else None
        cols = list(d.columns)
        # La 1a columna (jugador) mas ancha; el resto reparte.
        w0 = min(30, self.ancho_util * 0.13)
        wr = (self.ancho_util - w0) / max(1, len(cols) - 1)
        anchos = [w0] + [wr] * (len(cols) - 1)

        def _hdr():
            self.set_font("Helvetica", "B", 5.6)
            self.set_fill_color(*ROJO)
            self.set_text_color(*BLANCO)
            for c, w in zip(cols, anchos):
                self.cell(w, 5.5, _clean(str(c))[:13], 1, 0, "C", True)
            self.ln()

        _hdr()
        self.set_font("Helvetica", "", 5.4)
        for idx, (_, r) in enumerate(d.iterrows()):
            if self.get_y() > (185 if self.orientacion == "L" else 272):
                self.add_page(); _hdr(); self.set_font("Helvetica", "", 5.4)
            for c, w in zip(cols, anchos):
                v = _fmt_valor(r[c])
                sty = ""
                if est is not None and c in est.columns:
                    raw = est.iloc[idx][c]
                    if isinstance(raw, pd.Series):   # columnas duplicadas
                        raw = raw.iloc[0]
                    sty = "" if raw is None or pd.isna(raw) else str(raw)
                partes = sty.split("|") if "|" in sty else []
                if len(partes) == 2 and partes[0].strip() and partes[1].strip():
                    self.set_fill_color(*_hex(partes[0], (255, 255, 255)))
                    self.set_text_color(*_hex(partes[1], NEGRO))
                    self.set_font("Helvetica", "B", 5.4)
                else:
                    self.set_fill_color(255, 255, 255); self.set_text_color(*NEGRO)
                    self.set_font("Helvetica", "", 5.4)
                self.cell(w, 4.6, _clean(str(v))[:13], 1, 0, "C", True)
            self.ln()
        if len(df) > max_filas:
            self.ln(1)
            self.set_font("Helvetica", "I", 6)
            self.set_text_color(*GRIS)
            self.cell(0, 4, _clean(f"Mostrando {max_filas} de {len(df)} filas."), ln=1)

    ANCHO_MIN_COL = 15.5  # mm — por debajo de esto el texto se pisa y queda ilegible

    def tabla(self, df, max_filas=400, max_cols=None, color_cols=None):
        """Tabla compacta simple, con color por categoria opcional.
        max_cols YA NO es un numero fijo que el caller puede pasar sin limite:
        se acota SIEMPRE al maximo de columnas que entran legibles en el ancho
        real de la hoja (ANCHO_MIN_COL por columna). Antes un caller pidiendo
        max_cols=20 terminaba aplastando 20 columnas en 186mm -> texto pisado
        e ilegible, aunque el df tuviera menos filas de sobra."""
        if df is None or df.empty:
            self.parrafo("Sin datos para el periodo seleccionado.")
            return
        max_cols_fit = max(3, int(self.ancho_util // self.ANCHO_MIN_COL))
        max_cols = min(max_cols or max_cols_fit, max_cols_fit, len(df.columns))
        color_cols = color_cols or []

        d = df.head(max_filas).copy()
        cols = list(d.columns)[:max_cols]
        d = d[cols]
        ancho = self.ancho_util / len(cols)
        limite_chars = max(6, int(ancho / 1.7))

        def _hdr():
            self.set_font("Helvetica", "B", 6.8)
            self.set_fill_color(*ROJO)
            self.set_text_color(*BLANCO)
            for c in cols:
                self.cell(ancho, 6, _clean(str(c))[:limite_chars], 1, 0, "C", True)
            self.ln()

        _hdr()
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(*NEGRO)
        alt = True
        for _, r in d.iterrows():
            if self.get_y() > (180 if self.orientacion == "L" else 262):
                self.add_page(); _hdr()
                self.set_font("Helvetica", "", 6.5); self.set_text_color(*NEGRO)
            self.set_fill_color(*(245, 247, 250) if alt else (255, 255, 255))
            for c in cols:
                v = _fmt_valor(r[c])
                if c in color_cols:
                    self.set_font("Helvetica", "B", 6.5)
                    self.set_text_color(*_color_categoria(v))
                else:
                    self.set_font("Helvetica", "", 6.5)
                    self.set_text_color(*NEGRO)
                self.cell(ancho, 5, _clean(v)[:limite_chars], 1, 0, "C", True)
            self.ln()
            alt = not alt
        if len(df) > max_filas:
            self.ln(1)
            self.set_font("Helvetica", "I", 6.5)
            self.set_text_color(*GRIS)
            self.cell(0, 4, _clean(f"Mostrando {max_filas} de {len(df)} filas."), ln=1)
        if len(df.columns) > max_cols:
            self.set_font("Helvetica", "I", 6.5)
            self.set_text_color(*GRIS)
            self.cell(0, 4, _clean(f"Mostrando {max_cols} de {len(df.columns)} columnas "
                                   "(el resto no entra legible en la hoja; usa orientacion landscape "
                                   "o filtra columnas si necesitas verlas todas)."), ln=1)

    def tarjetas(self, df, campos, titulo_col=None, subtitulo_col=None, por_fila=3, alto_card=34):
        """Formato tarjetas: una card por registro (como las de pantalla), en vez
        de una fila de tabla. campos: lista de (columna, etiqueta) a mostrar."""
        if df is None or df.empty:
            self.parrafo("Sin datos para el periodo seleccionado.")
            return
        gap = 4
        ancho_card = (self.ancho_util - (por_fila - 1) * gap) / por_fila
        limite = 190 if self.orientacion == "L" else 275
        y = self.get_y()
        n = len(df)
        for i, (_, r) in enumerate(df.iterrows()):
            col_i = i % por_fila
            if col_i == 0 and y + alto_card > limite:
                self.add_page()
                y = self.get_y()
            x = 12 + col_i * (ancho_card + gap)
            self.set_fill_color(246, 248, 251)
            self.set_draw_color(225, 230, 238)
            self.rect(x, y, ancho_card, alto_card, "DF")
            self.set_fill_color(*ROJO)
            self.rect(x, y, 1.6, alto_card, "F")
            tx = x + 4.5
            self.set_xy(tx, y + 2.3)
            self.set_font("Helvetica", "B", 8.5)
            self.set_text_color(*NEGRO)
            titulo_txt = _fmt_valor(r[titulo_col]) if titulo_col and titulo_col in r.index else ""
            self.cell(ancho_card - 6, 4.5, _clean(titulo_txt)[:26], ln=2)
            self.set_x(tx)
            if subtitulo_col and subtitulo_col in r.index:
                self.set_font("Helvetica", "", 6.3)
                self.set_text_color(*ROJO)
                self.cell(ancho_card - 6, 3.8, _clean(_fmt_valor(r[subtitulo_col]))[:32], ln=2)
                self.set_x(tx)
            yy = self.get_y() + 1
            self.set_font("Helvetica", "", 6.1)
            for c, label in campos:
                if c not in r.index: continue
                self.set_xy(tx, yy)
                self.set_text_color(*GRIS)
                self.cell(17, 3.6, _clean(str(label)).upper()[:10] + ":", 0, 0)
                self.set_text_color(*NEGRO)
                self.set_font("Helvetica", "B", 6.1)
                self.cell(ancho_card - 6 - 17, 3.6, _clean(_fmt_valor(r[c]))[:24], 0, 2)
                self.set_font("Helvetica", "", 6.1)
                yy += 3.7
            if col_i == por_fila - 1 or i == n - 1:
                y += alto_card + gap
        self.set_y(y)


def _hex(h, default=(255, 255, 255)):
    """Hex -> RGB, tolerante: si el valor es invalido devuelve `default`
    en vez de romper la generacion entera del PDF."""
    try:
        h = str(h).strip().lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) != 6:
            return default
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return default


def generar_pdf(titulo, subtitulo="", kpis=None, tablas=None, notas=None, escudo=None,
                orientacion="P", matriz=None, estilos=None, matriz_titulo="Matriz",
                color_cols=None, tarjetas_df=None, tarjetas_campos=None, tarjetas_titulo_col=None,
                tarjetas_subtitulo_col=None, tarjetas_seccion="Fichas", tarjetas_por_fila=3,
                graficos=None):
    """
    kpis        : lista de (label, valor) o (label, valor, color_rgb)
    tablas      : lista de (titulo_seccion, DataFrame)   -> tabla simple
    color_cols  : columnas categoricas a color-codear en las tablas simples (TIPO, LESION, POS, etc.)
    matriz      : DataFrame ancho                        -> tabla con color por celda
    estilos     : DataFrame paralelo a `matriz` con "bg|fg" por celda
    orientacion : "P" vertical | "L" horizontal (para matrices anchas)
    tarjetas_df / tarjetas_campos / tarjetas_titulo_col / tarjetas_subtitulo_col :
                  si se pasa tarjetas_df, se agrega una seccion en formato tarjetas
                  (una card por fila, como en pantalla) en vez de tabla plana.
    graficos    : lista de (titulo, bytes_png) -> se embeben como imagen, para que
                  el reporte no sea solo texto/tablas.
    """
    pdf = ReportePDF(titulo=titulo, subtitulo=subtitulo, escudo=escudo, orientacion=orientacion)
    pdf.alias_nb_pages()
    pdf.add_page()

    tablas = [(t, d) for t, d in (tablas or []) if d is not None and not d.empty]
    graficos = [(t, b) for t, b in (graficos or []) if b]
    hay_tarjetas = tarjetas_df is not None and not tarjetas_df.empty
    hay = bool(kpis or tablas or notas or graficos or hay_tarjetas or (matriz is not None and not matriz.empty))

    n = 1
    if kpis:
        pdf.seccion(f"{n:02d}", "Resumen de indicadores"); pdf.kpis(kpis); n += 1
    if matriz is not None and not matriz.empty:
        pdf.seccion(f"{n:02d}", matriz_titulo); pdf.tabla_color(matriz, estilos); pdf.ln(2); n += 1
    if hay_tarjetas:
        pdf.seccion(f"{n:02d}", tarjetas_seccion)
        pdf.tarjetas(tarjetas_df, tarjetas_campos or [], titulo_col=tarjetas_titulo_col,
                     subtitulo_col=tarjetas_subtitulo_col, por_fila=tarjetas_por_fila)
        pdf.ln(2); n += 1
    for tit, df in tablas:
        pdf.seccion(f"{n:02d}", tit); pdf.tabla(df, color_cols=color_cols); pdf.ln(2); n += 1
    for tit, png_bytes in graficos:
        import io
        pdf.seccion(f"{n:02d}", tit)
        try:
            pdf.image(io.BytesIO(png_bytes), x=12, w=pdf.ancho_util)
        except Exception:
            pdf.parrafo("No se pudo incrustar el grafico.")
        pdf.ln(2); n += 1
    if notas:
        pdf.seccion(f"{n:02d}", "Notas"); pdf.parrafo(notas)
    if not hay:
        pdf.seccion("01", "Sin datos exportables")
        pdf.parrafo("Esta seccion no tiene datos tabulares configurados para exportar, o los filtros "
                    "activos no devolvieron resultados. Ajusta los filtros y volve a generar el informe.")

    out = pdf.output(dest="S")
    if isinstance(out, str):
        return out.encode("latin-1")
    return bytes(out)


# CSS del botón: por defecto Streamlit lo pinta blanco y el texto queda invisible
# sobre el fondo oscuro de la app. Lo forzamos al rojo institucional.
_CSS_BTN = """
<style>
div[data-testid="stDownloadButton"] button,
div[data-testid="stDownloadButton"] > button,
div[data-testid="stDownloadButton"] [data-testid="stBaseButton-secondary"],
div[data-testid="stDownloadButton"] [data-testid="baseButton-secondary"],
section[data-testid="stMain"] div[data-testid="stDownloadButton"] button,
.stDownloadButton button,
.stDownloadButton > button {
    background-image: linear-gradient(135deg,#c8102e,#8b0000) !important;
    background-color: #c8102e !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    font-size: 12px !important;
    letter-spacing: .5px !important;
    box-shadow: 0 2px 10px rgba(200,16,46,.4) !important;
    min-height: 34px !important;
}
div[data-testid="stDownloadButton"] button:hover,
.stDownloadButton button:hover {
    background-image: linear-gradient(135deg,#e01235,#a00000) !important;
    border-color: rgba(255,255,255,0.5) !important;
    color: #ffffff !important;
}
div[data-testid="stDownloadButton"] button *,
.stDownloadButton button * {
    color: #ffffff !important;
    fill: #ffffff !important;
    font-weight: 800 !important;
}
</style>
"""


# ────────────────────────────────────────────────────────────────────────
#  Botón para Streamlit  (reemplaza al pdf_btn() viejo)
# ────────────────────────────────────────────────────────────────────────
def pdf_btn(titulo="Informe", subtitulo="", kpis=None, tablas=None, notas=None,
            escudo=None, key=None, orientacion="P", matriz=None, estilos=None,
            matriz_titulo="Matriz", label="Exportar PDF", color_cols=None,
            tarjetas_df=None, tarjetas_campos=None, tarjetas_titulo_col=None,
            tarjetas_subtitulo_col=None, tarjetas_seccion="Fichas", tarjetas_por_fila=3,
            graficos=None, **kwargs):
    """Boton real de descarga PDF (st.download_button es un widget nativo:
    a diferencia del <button onclick> anterior, Streamlit no lo sanitiza).
    **kwargs absorbe cualquier parametro futuro para no romper por firma."""
    import streamlit as st

    st.markdown(_CSS_BTN, unsafe_allow_html=True)
    try:
        data = generar_pdf(titulo, subtitulo, kpis, tablas, notas, escudo,
                           orientacion, matriz, estilos, matriz_titulo,
                           color_cols=color_cols, tarjetas_df=tarjetas_df, tarjetas_campos=tarjetas_campos,
                           tarjetas_titulo_col=tarjetas_titulo_col, tarjetas_subtitulo_col=tarjetas_subtitulo_col,
                           tarjetas_seccion=tarjetas_seccion, tarjetas_por_fila=tarjetas_por_fila,
                           graficos=graficos)
    except Exception as e:
        st.warning(f"No se pudo generar el PDF: {e}")
        return

    fname = f"{_clean(titulo).lower().replace(' ', '_')}_{datetime.now():%Y%m%d_%H%M}.pdf"
    c1, c2 = st.columns([4, 1])
    with c2:
        st.download_button(label, data=data, file_name=fname, mime="application/pdf",
                           use_container_width=True, type="primary",
                           key=f"pdf_{key or titulo}")
