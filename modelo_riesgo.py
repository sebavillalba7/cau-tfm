# ══════════════════════════════════════════════════════════════════════════
# modelo_riesgo.py · Club A. Unión — TFM
# Footballer Workload Footprint (FWF) + Modelo de riesgo de lesión
# ----------------------------------------------------------------------------
# Capa de CÁLCULO (pura: pandas / numpy / sklearn) + capa de RENDER (streamlit).
# La capa de cálculo es testeable sin streamlit.
#
# Base conceptual:
#   - FWF: índice de carga compuesto (dist, alta velocidad, sprints, acel, des).
#   - Predictores de riesgo basados en literatura de monitoreo de carga:
#       · ACWR (Acute:Chronic Workload Ratio) — ventana 7d:28d.
#       · Monotonía y Strain (Foster).
#       · FWF agudo / crónico.
#   - Clasificador RandomForest: P(lesión en próximos N días).
# ══════════════════════════════════════════════════════════════════════════
from __future__ import annotations
import numpy as np
import pandas as pd

# ── Pesos FWF (fórmula del máster) ──────────────────────────────────────────
FWF_WEIGHTS = {
    "dist":    0.30,   # distancia total
    "hsd":     0.25,   # high-speed distance (metros > umbral)
    "sprints": 0.20,   # nº de sprints
    "acel":    0.15,   # aceleraciones
    "des":     0.10,   # desaceleraciones
}

HORIZONTE_DEFAULT = 7   # días de ventana para etiquetar lesión


# ── 1. Detección flexible de columnas (robusta a nombres reales) ────────────
def _find_col(df: pd.DataFrame, candidatos, contiene=None):
    """Busca columna por nombre exacto (case-insensitive) o subcadena."""
    cols = {c.upper().strip(): c for c in df.columns}
    for cand in candidatos:
        if cand.upper() in cols:
            return cols[cand.upper()]
    if contiene:
        for c in df.columns:
            cl = c.lower()
            if all(tok in cl for tok in contiene):
                return c
    return None


def detectar_columnas_gps(df: pd.DataFrame) -> dict:
    """Mapea las columnas GPS reales a roles lógicos del modelo."""
    return {
        "jugador": _find_col(df, ["JUGADOR", "JUG", "NOMBRE", "PLAYER", "ATLETA"],
                             contiene=["jug"]),
        "fecha":   _find_col(df, ["FECHA", "DATE"], contiene=["fecha"]),
        "pos":     _find_col(df, ["POS", "POSICION", "POSICIÓN"]),
        "min":     _find_col(df, ["MIN", "MINUTOS"], contiene=["min"]),
        "dist":    _find_col(df, ["TOT DIST", "DIST TOTAL", "DISTANCIA"],
                             contiene=["tot", "dist"]),
        # high-speed distance: preferimos >19 km/h; si no, >16
        "hsd":     (_find_col(df, ["MTS>19 KM/H", "MTS >19 KM/H", "MTS 19-24 KM/H"],
                              contiene=["mts", "19"])
                    or _find_col(df, ["> 16 KM/H", ">16 KM/H"], contiene=["16", "km"])),
        "sprints": _find_col(df, ["#SP24", "SPRINTS", "SP24"], contiene=["sp"]),
        "acel":    _find_col(df, ["ACEL", "ACC", "ACELERACIONES"]),
        "des":     _find_col(df, ["DES", "DEC", "DESACELERACIONES"]),
    }


def detectar_columnas_lesiones(df: pd.DataFrame) -> dict:
    return {
        "jugador": _find_col(df, ["JUG", "JUGADOR", "NOMBRE", "PLAYER"], contiene=["jug"]),
        "fecha":   _find_col(df, ["FECHA", "DATE"], contiene=["fecha"]),
        "region":  _find_col(df, ["REGION", "REGIÓN", "ZONA"]),
        "dias_baja": _find_col(df, ["DAY_OFF_DXT", "DIAS_BAJA", "DAYS_OFF"],
                               contiene=["day", "off"]),
    }


# ── 2. Utilidades numéricas ─────────────────────────────────────────────────
def _to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False),
                         errors="coerce")


def _norm_nombre(s: pd.Series) -> pd.Series:
    """Normaliza nombres de jugador para hacer match entre hojas."""
    return (s.astype(str).str.upper().str.strip()
            .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
            .str.replace(r"\s+", " ", regex=True))


# ── 3. Cálculo del FWF por sesión ───────────────────────────────────────────
def calcular_fwf(df_gps: pd.DataFrame, cols: dict | None = None) -> pd.DataFrame:
    """
    Devuelve df con columnas: jugador, fecha, pos, min, y FWF + FWF_min.

    FWF (0-100): cada componente se escala min-max sobre el dataset, se combina
    con los pesos del máster y se lleva a 0-100. FWF_min = intensidad por minuto
    (FWF normalizado por minutos jugados), como pide la consigna.
    """
    cols = cols or detectar_columnas_gps(df_gps)
    df = df_gps.copy()

    # Numerizar componentes
    comp = {}
    for rol in ["dist", "hsd", "sprints", "acel", "des"]:
        c = cols.get(rol)
        comp[rol] = _to_num(df[c]) if c and c in df.columns else pd.Series(0.0, index=df.index)

    # Escalado min-max por componente (poblacional)
    def _mm(x: pd.Series) -> pd.Series:
        x = x.fillna(0.0)
        rng = x.max() - x.min()
        return (x - x.min()) / rng if rng > 0 else pd.Series(0.0, index=x.index)

    fwf_raw = sum(_mm(comp[r]) * FWF_WEIGHTS[r] for r in FWF_WEIGHTS)
    df["FWF"] = (fwf_raw * 100).round(1)

    # Minutos para normalización por minuto
    cmin = cols.get("min")
    minutos = _to_num(df[cmin]) if cmin and cmin in df.columns else pd.Series(np.nan, index=df.index)
    df["MIN_JUG"] = minutos
    df["FWF_min"] = (df["FWF"] / minutos.replace(0, np.nan)).round(3)

    # Columnas lógicas renombradas para uso posterior
    out = pd.DataFrame({
        "jugador": df[cols["jugador"]].astype(str) if cols.get("jugador") else "—",
        "_fecha":  pd.to_datetime(df[cols["fecha"]], dayfirst=True, errors="coerce")
                   if cols.get("fecha") else pd.NaT,
        "pos":     df[cols["pos"]].astype(str) if cols.get("pos") else "—",
        "min":     df["MIN_JUG"],
        "FWF":     df["FWF"],
        "FWF_min": df["FWF_min"],
    })
    return out.dropna(subset=["_fecha"]).sort_values(["jugador", "_fecha"])


# ── 4. Features de carga por jugador (rolling) ──────────────────────────────
def construir_features(fwf_df: pd.DataFrame) -> pd.DataFrame:
    """
    A partir del FWF por sesión, calcula por jugador y fecha:
      - carga_aguda (7d), carga_cronica (28d)
      - ACWR = aguda / cronica
      - monotonia, strain (7d)
      - fwf_7d, sesiones_7d
    """
    filas = []
    for jug, g in fwf_df.groupby("jugador"):
        g = g.set_index("_fecha").sort_index()
        carga = g["FWF"]
        aguda   = carga.rolling("7D").mean()
        cronica = carga.rolling("28D").mean()
        acwr    = (aguda / cronica.replace(0, np.nan)).round(2)
        media7  = carga.rolling("7D").mean()
        std7    = carga.rolling("7D").std()
        monoton = (media7 / std7.replace(0, np.nan)).round(2)
        carga7  = carga.rolling("7D").sum()
        strain  = (carga7 * monoton).round(1)
        sesiones7 = carga.rolling("7D").count()

        f = pd.DataFrame({
            "jugador": jug,
            "_fecha": g.index,
            "pos": g["pos"].values,
            "FWF": carga.values,
            "carga_aguda": aguda.values,
            "carga_cronica": cronica.values,
            "ACWR": acwr.values,
            "monotonia": monoton.values,
            "strain": strain.values,
            "fwf_7d": carga7.values,
            "sesiones_7d": sesiones7.values,
        })
        filas.append(f)
    if not filas:
        return pd.DataFrame()
    return pd.concat(filas, ignore_index=True)


# ── 5. Etiquetado de lesiones ───────────────────────────────────────────────
def etiquetar_lesiones(feat_df: pd.DataFrame, df_les: pd.DataFrame,
                       horizonte: int = HORIZONTE_DEFAULT,
                       cols_les: dict | None = None) -> pd.DataFrame:
    """
    Marca lesion_proxima=1 si el jugador sufre una lesión dentro de `horizonte`
    días posteriores a la fecha de la fila.
    """
    feat = feat_df.copy()
    feat["lesion_proxima"] = 0
    if df_les is None or df_les.empty:
        return feat

    cols_les = cols_les or detectar_columnas_lesiones(df_les)
    jc, fc = cols_les.get("jugador"), cols_les.get("fecha")
    if not jc or not fc:
        return feat

    les = pd.DataFrame({
        "jugador": _norm_nombre(df_les[jc]),
        "_fles": pd.to_datetime(df_les[fc], dayfirst=True, errors="coerce"),
    }).dropna(subset=["_fles"])

    feat["_jnorm"] = _norm_nombre(feat["jugador"])
    h = pd.Timedelta(days=horizonte)
    for i, row in feat.iterrows():
        ev = les[(les["jugador"] == row["_jnorm"]) &
                 (les["_fles"] > row["_fecha"]) &
                 (les["_fles"] <= row["_fecha"] + h)]
        if len(ev) > 0:
            feat.at[i, "lesion_proxima"] = 1
    return feat.drop(columns=["_jnorm"])


# ── 6. Entrenamiento del modelo ─────────────────────────────────────────────
FEATURES_ML = ["FWF", "carga_aguda", "carga_cronica", "ACWR",
               "monotonia", "strain", "fwf_7d", "sesiones_7d"]


def entrenar_modelo(feat_etiq: pd.DataFrame):
    """
    Entrena RandomForest. Devuelve dict con modelo, métricas, importancias
    y el dataframe con la probabilidad de riesgo predicha (riesgo_pred).
    Degrada con elegancia si hay pocos positivos.
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score

    df = feat_etiq.dropna(subset=FEATURES_ML).copy()
    res = {"ok": False, "modelo": None, "auc": None, "n": len(df),
           "n_lesiones": int(df["lesion_proxima"].sum()) if "lesion_proxima" in df else 0,
           "importancias": None, "df": df, "motivo": ""}

    if len(df) < 30:
        res["motivo"] = "Datos insuficientes (<30 registros)."
        return res

    X, y = df[FEATURES_ML], df["lesion_proxima"]
    pos = int(y.sum())

    modelo = RandomForestClassifier(
        n_estimators=300, max_depth=6, min_samples_leaf=5,
        class_weight="balanced", random_state=42, n_jobs=-1)

    # Si hay muy pocos positivos, no se puede hacer split estratificado fiable:
    # entrenamos sobre todo y reportamos como modelo descriptivo.
    if pos < 8 or (len(df) - pos) < 8:
        modelo.fit(X, y)
        df["riesgo_pred"] = modelo.predict_proba(X)[:, 1]
        res.update(ok=True, modelo=modelo, df=df,
                   importancias=dict(zip(FEATURES_ML, modelo.feature_importances_)),
                   motivo=("Modelo entrenado en modo descriptivo "
                           f"(solo {pos} eventos de lesión; sin validación hold-out)."))
        return res

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y)
    modelo.fit(Xtr, ytr)
    try:
        auc = roc_auc_score(yte, modelo.predict_proba(Xte)[:, 1])
    except ValueError:
        auc = None
    df["riesgo_pred"] = modelo.predict_proba(X)[:, 1]
    res.update(ok=True, modelo=modelo, auc=auc, df=df,
               importancias=dict(zip(FEATURES_ML, modelo.feature_importances_)),
               motivo="Modelo entrenado con validación hold-out (25%).")
    return res


# ── 7. Clasificación de riesgo legible ──────────────────────────────────────
def nivel_riesgo(p: float) -> tuple[str, str]:
    """Devuelve (etiqueta, color_hex) según probabilidad."""
    if p is None or np.isnan(p):
        return "—", "#475569"
    if p < 0.33:
        return "BAJO", "#22c55e"
    if p < 0.66:
        return "MEDIO", "#f59e0b"
    return "ALTO", "#ef4444"


def zona_acwr(acwr: float) -> tuple[str, str]:
    if acwr is None or np.isnan(acwr):
        return "—", "#475569"
    if acwr < 0.8:
        return "Subcarga", "#60a5fa"
    if acwr <= 1.3:
        return "Óptimo", "#22c55e"
    if acwr <= 1.5:
        return "Precaución", "#f59e0b"
    return "Riesgo", "#ef4444"


# ── 8. Pipeline completo (una llamada) ──────────────────────────────────────
def pipeline_riesgo(df_gps: pd.DataFrame, df_les: pd.DataFrame,
                    horizonte: int = HORIZONTE_DEFAULT) -> dict:
    fwf = calcular_fwf(df_gps)
    feat = construir_features(fwf)
    feat = etiquetar_lesiones(feat, df_les, horizonte=horizonte)
    modelo = entrenar_modelo(feat)
    modelo["fwf"] = fwf
    return modelo
