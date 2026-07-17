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


class ReportePDF(FPDF):
    """PDF con header/footer institucional del Club A. Unión."""

    def __init__(self, titulo="Informe", subtitulo="", escudo=None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.titulo = _clean(titulo)
        self.subtitulo = _clean(subtitulo)
        self.escudo = escudo if escudo and Path(escudo).exists() else None
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(12, 12, 12)

    def header(self):
        self.set_fill_color(*AZUL)
        self.rect(0, 0, 210, 26, "F")
        self.set_fill_color(*ROJO)
        self.rect(0, 26, 210, 1.2, "F")
        if self.escudo:
            try:
                self.image(str(self.escudo), x=12, y=4, h=18)
            except Exception:
                pass
        self.set_xy(34 if self.escudo else 12, 7)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*BLANCO)
        self.cell(0, 7, self.titulo, ln=1)
        self.set_xy(34 if self.escudo else 12, 15)
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(180, 190, 205)
        self.cell(0, 5, self.subtitulo or "Club A. Union - Data Intelligence", ln=1)
        self.set_y(34)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*GRIS)
        gen = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 5, _clean(f"Club A. Union - Area de Rendimiento Fisico  |  Generado {gen}"), 0, 0, "L")
        self.cell(0, 5, f"Pag. {self.page_no()}/{{nb}}", 0, 0, "R")

    # ── bloques reutilizables ────────────────────────────────────────
    def seccion(self, num, texto):
        self.ln(2)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*ROJO)
        self.cell(8, 6, _clean(str(num)), 0, 0)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*NEGRO)
        self.cell(0, 6, _clean(texto).upper(), ln=1)
        self.set_draw_color(225, 230, 238)
        self.line(12, self.get_y() + 0.5, 198, self.get_y() + 0.5)
        self.ln(3)

    def parrafo(self, texto):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(70, 85, 105)
        self.multi_cell(0, 4.6, _clean(texto))
        self.ln(2)

    def kpis(self, pares, por_fila=4):
        """pares: lista de (label, valor). Dibuja tarjetas."""
        if not pares:
            return
        ancho = (186 - (por_fila - 1) * 4) / por_fila
        for i in range(0, len(pares), por_fila):
            fila = pares[i:i + por_fila]
            y0 = self.get_y()
            if y0 > 240:
                self.add_page(); y0 = self.get_y()
            for j, (lab, val) in enumerate(fila):
                x = 12 + j * (ancho + 4)
                self.set_xy(x, y0)
                self.set_fill_color(246, 248, 251)
                self.set_draw_color(225, 230, 238)
                self.rect(x, y0, ancho, 16, "DF")
                self.set_fill_color(*ROJO)
                self.rect(x, y0, ancho, 1, "F")
                self.set_xy(x + 3, y0 + 2.5)
                self.set_font("Helvetica", "", 6.5)
                self.set_text_color(*GRIS)
                self.cell(ancho - 6, 3, _clean(str(lab)).upper()[:28], ln=2)
                self.set_x(x + 3)
                self.set_font("Helvetica", "B", 12)
                self.set_text_color(*NEGRO)
                self.cell(ancho - 6, 7, _clean(str(val))[:18], ln=2)
            self.set_y(y0 + 20)

    def tabla(self, df, max_filas=28, max_cols=9):
        """Tabla compacta. Recorta filas/columnas para que entre en A4."""
        if df is None or df.empty:
            self.parrafo("Sin datos para el periodo seleccionado.")
            return
        d = df.head(max_filas).copy()
        cols = list(d.columns)[:max_cols]
        d = d[cols]
        ancho = 186 / len(cols)

        self.set_font("Helvetica", "B", 6.8)
        self.set_fill_color(*ROJO)
        self.set_text_color(*BLANCO)
        for c in cols:
            self.cell(ancho, 6, _clean(str(c))[:16], 1, 0, "C", True)
        self.ln()

        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(*NEGRO)
        alt = True
        for _, r in d.iterrows():
            if self.get_y() > 262:
                self.add_page()
                self.set_font("Helvetica", "B", 6.8)
                self.set_fill_color(*ROJO); self.set_text_color(*BLANCO)
                for c in cols:
                    self.cell(ancho, 6, _clean(str(c))[:16], 1, 0, "C", True)
                self.ln()
                self.set_font("Helvetica", "", 6.5); self.set_text_color(*NEGRO)
            self.set_fill_color(*(245, 247, 250) if alt else (255, 255, 255))
            for c in cols:
                v = r[c]
                if isinstance(v, float):
                    v = f"{v:,.1f}"
                elif isinstance(v, pd.Timestamp):
                    v = v.strftime("%d/%m/%Y")
                self.cell(ancho, 5, _clean(str(v))[:16], 1, 0, "C", True)
            self.ln()
            alt = not alt
        if len(df) > max_filas:
            self.ln(1)
            self.set_font("Helvetica", "I", 6.5)
            self.set_text_color(*GRIS)
            self.cell(0, 4, _clean(f"Mostrando {max_filas} de {len(df)} filas. Export completo disponible en CSV."), ln=1)


def generar_pdf(titulo, subtitulo="", kpis=None, tablas=None, notas=None, escudo=None):
    """
    Construye el PDF y devuelve bytes listos para st.download_button.
      kpis   : lista de (label, valor)
      tablas : lista de (titulo_seccion, DataFrame)
      notas  : texto libre al final
    """
    pdf = ReportePDF(titulo=titulo, subtitulo=subtitulo, escudo=escudo)
    pdf.alias_nb_pages()
    pdf.add_page()

    n = 1
    if kpis:
        pdf.seccion(f"{n:02d}", "Resumen de indicadores")
        pdf.kpis(kpis)
        n += 1
    for tit, df in (tablas or []):
        pdf.seccion(f"{n:02d}", tit)
        pdf.tabla(df)
        pdf.ln(3)
        n += 1
    if notas:
        pdf.seccion(f"{n:02d}", "Notas")
        pdf.parrafo(notas)

    out = pdf.output(dest="S")
    # fpdf2 devuelve bytearray (>=2.7) o str (legacy). Normalizamos a bytes.
    if isinstance(out, str):
        return out.encode("latin-1")
    return bytes(out)


# ────────────────────────────────────────────────────────────────────────
#  Botón para Streamlit  (reemplaza al pdf_btn() viejo)
# ────────────────────────────────────────────────────────────────────────
def pdf_btn(titulo="Informe", subtitulo="", kpis=None, tablas=None, notas=None,
            escudo=None, key=None):
    """
    Botón real de descarga PDF. Uso en cada página:

        pdf_btn("Demandas Fisicas", kpis=[("Sesiones", 120)],
                tablas=[("Matriz microciclo", df)], key="dem")

    Si no se pasan datos, igual genera un PDF de portada válido.
    """
    import streamlit as st

    try:
        data = generar_pdf(titulo, subtitulo, kpis, tablas, notas, escudo)
    except Exception as e:
        st.warning(f"No se pudo generar el PDF: {e}")
        return

    fname = f"{_clean(titulo).lower().replace(' ', '_')}_{datetime.now():%Y%m%d_%H%M}.pdf"
    c1, c2 = st.columns([5, 1])
    with c2:
        st.download_button("PDF", data=data, file_name=fname, mime="application/pdf",
                           use_container_width=True, key=f"pdf_{key or titulo}")
