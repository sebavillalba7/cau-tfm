# backend/data_loader.py
# Carga y normalización de datos desde Google Sheets
import re
import pandas as pd
import streamlit as st

# ── URLs de Google Sheets ─────────────────────────────────────────
SHEETS = {
    "gps":      "https://docs.google.com/spreadsheets/d/1W3hUX8zTPYXzDUSmdW7Nj2fXbEKlp1E2Us7kwNBhR6c/edit?gid=0",
    "lesiones": "https://docs.google.com/spreadsheets/d/1irSkXB8V_D_jZurEGUA9JMkLpE3e0_qad16_orjHDi8/edit?gid=0",
    "cmj":      "https://docs.google.com/spreadsheets/d/1VQLX1R1M0IW8j_TPXbVE8y5qaOA8-2qpj8cL-eGA1VY/edit?gid=1188054203",
    "nordico":  "https://docs.google.com/spreadsheets/d/1fhFajl9ckPYikfIKdBHTORcqQj0802JoNQ8-B3wEJWU/edit?gid=1994839095",
    "data_jug": "https://docs.google.com/spreadsheets/d/1aZ7yXUf3M4NA-7lNp9vlwUU_4tgU7Tecf5w-TrnelY8/edit?gid=0",
}

def gsheet_csv(url: str) -> str:
    """Convierte URL de Google Sheets a URL de exportación CSV."""
    sheet_id = re.search(r"/d/([^/]+)", url).group(1)
    gid = re.search(r"gid=(\d+)", url)
    gid = gid.group(1) if gid else "0"
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype(str).str.strip()
    return df

def renombrar(df: pd.DataFrame, candidatos: list, final: str) -> pd.DataFrame:
    lower = {c.lower().strip(): c for c in df.columns}
    for cand in candidatos:
        key = cand.lower().strip()
        if key in lower and lower[key] != final:
            return df.rename(columns={lower[key]: final})
    return df

def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar(df)
    mapeos = [
        (["JUGADOR","Jugador","NAME","Name","Player","PLAYER","Atleta"], "JUGADOR"),
        (["POSICION","Posicion","POSICIÓN","POS","Position","POSITION"], "POSICION"),
        (["FECHA","Fecha","fecha","DATE","Date"], "FECHA"),
        (["RIVAL","Rival","Opponent","OPPONENT"], "RIVAL"),
        (["MIN","Min","Minutes","MINUTES","Duration"], "MIN"),
        (["DISTANCIA TOTAL","Distancia Total","Total Distance","TOT DIST","TOT-DIST"], "TOT DIST"),
        (["MTS/MIN","M/MIN","Meters Per Min","MTS MIN"], "MTS/MIN"),
        (["HSD",">19","MTS>19","MTS >19","HSR","High Speed Running","MTS>19 KM/H",">19KM/H"], "HSD"),
        (["SPD",">24","MTS>24","MTS >24","SPRINT","Sprint Distance","MTS>24 KM/H",">24KM/H"], "SPD"),
        (["SPRINTS","Sprints","N SPRINTS","N° SPRINTS"], "SPRINTS"),
        (["ACEL","ACC","ACCEL","Aceleraciones"], "ACEL"),
        (["DES","DEC","DECEL","Desaceleraciones"], "DES"),
        (["V-MAX","VMAX","MAX SPEED","Velocidad Maxima","Velocidad Máxima"], "V-MAX"),
        (["SES","SESION","SESIÓN","Session","SESSION","Tipo Sesion","Tipo sesión"], "SESION"),
    ]
    for candidatos, final in mapeos:
        df = renombrar(df, candidatos, final)
    return df

@st.cache_data(ttl=300)
def cargar_datos():
    """Carga todos los datasets desde Google Sheets. Cache de 5 minutos."""
    # GPS
    gps = normalizar(pd.read_csv(gsheet_csv(SHEETS["gps"]), low_memory=False))

    # Lesiones
    lesiones = normalizar(pd.read_csv(gsheet_csv(SHEETS["lesiones"]), low_memory=False))

    # Data jugadores
    data_jug = normalizar(pd.read_csv(gsheet_csv(SHEETS["data_jug"]), low_memory=False))
    data_jug = renombrar(data_jug, ["FECHA_NAC","FECHA NAC","FECHA NACIMIENTO","Nacimiento"], "FECHA_NAC")
    data_jug = renombrar(data_jug, ["LADO_HABIL","PIERNA","Pierna","PERFIL","Perfil","Dominant Foot"], "LADO_HABIL")
    data_jug = renombrar(data_jug, ["ALTURA","Height","HEIGHT"], "ALTURA")
    data_jug = renombrar(data_jug, ["NACIONALIDAD","PAIS","País","Country"], "NACIONALIDAD")
    data_jug = renombrar(data_jug, ["FOTO","FOTO_URL","IMAGEN","Photo","URL_FOTO"], "FOTO_URL")

    # CMJ — manejo de decimales con coma
    cmj_raw = pd.read_csv(gsheet_csv(SHEETS["cmj"]), low_memory=False)
    cmj_raw.columns = cmj_raw.columns.astype(str).str.strip()
    cmj_raw = cmj_raw.replace({"None": pd.NA, "nan": pd.NA, "": pd.NA, "#N/A": pd.NA})
    for c in ["Jump Height (Imp-Mom) [cm]","Eccentric Peak Power / BM [W/kg]",
              "RSI-modified [m/s]","Concentric Mean Force / BM [N/kg]",
              "Concentric Peak Force / BM [N/kg]","BW [KG]"]:
        if c in cmj_raw.columns:
            cmj_raw[c] = pd.to_numeric(
                cmj_raw[c].astype(str).str.strip().str.replace(",", ".", regex=False),
                errors="coerce"
            )
    cmj = normalizar(cmj_raw)

    # Nórdico — mismo tratamiento
    nord_raw = pd.read_csv(gsheet_csv(SHEETS["nordico"]), low_memory=False)
    nord_raw.columns = nord_raw.columns.astype(str).str.strip()
    nord_raw = nord_raw.replace({"None": pd.NA, "nan": pd.NA, "": pd.NA, "#N/A": pd.NA})
    for c in ["R Max Force (N)", "L Max Force (N)", "Max Imbalance (%)"]:
        if c in nord_raw.columns:
            nord_raw[c] = pd.to_numeric(
                nord_raw[c].astype(str).str.strip().str.replace(",", ".", regex=False),
                errors="coerce"
            )
    nordico = normalizar(nord_raw)

    # Fechas y año
    for df in [gps, lesiones, cmj, nordico, data_jug]:
        if "FECHA" in df.columns:
            df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
        if "AÑO" not in df.columns and "FECHA" in df.columns:
            df["AÑO"] = df["FECHA"].dt.year

    return gps, lesiones, cmj, nordico, data_jug
