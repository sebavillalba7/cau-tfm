# =============================================================
# backend/data_loader.py
# Adquisición y limpieza de datos — CAU TFM
#
# Backend de datos: acá vive TODO lo que tiene que ver con traer la
# información de Google Sheets y dejarla lista para usar (tipos de dato,
# fechas parseadas, columna AÑO). El frontend (app.py) sólo CONSUME
# cargar_sheet(), nunca construye URLs ni parsea CSVs por su cuenta.
# =============================================================
import re
import pandas as pd
import streamlit as st

# ------------------------------------------------------------------
# Fuentes de datos (Google Sheets, una hoja por dominio)
# ------------------------------------------------------------------
SHEETS = {
    "historial":  "https://docs.google.com/spreadsheets/d/1Ppy3Mkz3ojqlcGAcxhNlqnGy5o2GmBHmdL9IZdRh9b0/edit?gid=0",
    "lesiones":   "https://docs.google.com/spreadsheets/d/1irSkXB8V_D_jZurEGUA9JMkLpE3e0_qad16_orjHDi8/edit?gid=0",
    "cmj":        "https://docs.google.com/spreadsheets/d/1VQLX1R1M0IW8j_TPXbVE8y5qaOA8-2qpj8cL-eGA1VY/edit?gid=1188054203",
    "cmj1pp":     "https://docs.google.com/spreadsheets/d/16ugXQ5hEnMa9bh_Ma1IDDaPq6gNq4QVPTRwQyVnz3oc/edit?gid=305963248",
    "nordico":    "https://docs.google.com/spreadsheets/d/1fhFajl9ckPYikfIKdBHTORcqQj0802JoNQ8-B3wEJWU/edit?gid=1994839095",
    "vbt":        "https://docs.google.com/spreadsheets/d/1NjVz_ivHKRrtai18ogjMQuQA6EYh3Q-WLDiNOErYO-Q/edit?gid=0",
    "gps":        "https://docs.google.com/spreadsheets/d/1W3hUX8zTPYXzDUSmdW7Nj2fXbEKlp1E2Us7kwNBhR6c/edit?gid=0",
    "partidos":   "https://docs.google.com/spreadsheets/d/17EiRiX-Tjlor0SfZvz-Wzfohz07calbA_26DKd4XL5g/edit?gid=2140450866",
    "nutricion":  "https://docs.google.com/spreadsheets/d/1tUsVAxfdeNbwGgAhJ865E3Fgf4x1TENcbTgt1ROAG2s/edit?gid=738328335",
}


def gsheet_csv(url: str) -> str:
    """Convierte el link de edición de un Google Sheet en su URL de
    exportación CSV directa (adquisición de datos)."""
    sid = re.search(r"/d/([^/]+)", url).group(1)
    m = re.search(r"gid=(\d+)", url)
    gid = m.group(1) if m else "0"
    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza básica: normaliza encabezados y valores nulos disfrazados
    de texto ('None', 'nan', '#N/A', etc.)."""
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    df = df.replace({"None": pd.NA, "nan": pd.NA, "": pd.NA, "#N/A": pd.NA, "N/A": pd.NA})
    return df


def normalizar_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta la columna de fecha (si existe) y genera _fecha (datetime
    real) y AÑO (para los filtros de año en toda la app)."""
    df = df.copy()
    fecha_cols = [c for c in df.columns if ("fecha" in c.lower() or "date" in c.lower()) and "_" not in c.lower()]
    if fecha_cols:
        df["_fecha"] = pd.to_datetime(df[fecha_cols[0]], dayfirst=True, errors="coerce")
        df["AÑO"] = df["_fecha"].dt.year.astype("Int64")
    elif "AÑO" in df.columns:
        df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce").astype("Int64")
    return df


@st.cache_data(ttl=300, show_spinner=False)
def cargar_sheet(key: str) -> pd.DataFrame:
    """Punto único de entrada para el frontend: adquisición + limpieza +
    normalización de fechas, cacheado 5 minutos. Devuelve DataFrame vacío
    si la hoja no existe o falla la carga (nunca rompe la página)."""
    try:
        df = pd.read_csv(gsheet_csv(SHEETS[key]), low_memory=False)
        df = limpiar(df)
        df = normalizar_fechas(df)
        return df
    except Exception:
        return pd.DataFrame()
