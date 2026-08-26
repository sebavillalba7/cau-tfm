# ════════════════════════════════════════════════════════════════════════
#  modelo_riesgo.py  ·  TFM CAU — Footballer Workload Footprint (FWF)
#  Modelo de riesgo de lesión basado en carga GPS + historial de lesiones.
#
#  Diseño (CRISP-DM):
#   1. FWF  : huella de carga compuesta por sesión, normalizada por minutos.
#   2. Features de carga acumulada: ACWR, monotonía, strain, FWF agudo/crónico.
#   3. Etiqueta: ¿lesión en los próximos N días tras la sesión?  (supervisado)
#   4. Modelo: RandomForest con split temporal (sin fuga de datos) +
#              class_weight balanceado. Si no hay suficientes lesiones
#              etiquetadas, cae a un score basado en reglas (híbrido honesto).
#
#  El núcleo (todo lo de arriba de la línea STREAMLIT) NO depende de Streamlit:
#  se puede importar y testear de forma aislada.
# ════════════════════════════════════════════════════════════════════════
import numpy as np
import pandas as pd

__version__ = "2026.07.17"

# ─────────────────────────────────────────────────────────────────────────
#  1. LOCALIZACIÓN ROBUSTA DE COLUMNAS  (tolera variaciones de encabezado)
# ─────────────────────────────────────────────────────────────────────────
def _find(df, candidates, contains=None):
    """Devuelve el nombre real de la 1ª columna que matchea (exacta o por substring)."""
    up = {c.upper().strip(): c for c in df.columns}
    for cand in candidates:
        if cand.upper() in up:
            return up[cand.upper()]
    keys = contains if contains is not None else candidates
    for c in df.columns:
        cl = c.lower()
        if any(k.lower() in cl for k in keys):
            return c
    return None


def mapear_columnas_gps(df):
    """Mapa lógico → real para la hoja GPS. Devuelve dict (valores pueden ser None)."""
    return {
        "jugador": _find(df, ["JUGADOR", "JUG", "NOMBRE", "PLAYER", "ATLETA"], contains=["jug", "player", "atleta", "nombre"]),
        "fecha":   _find(df, ["FECHA", "DATE"], contains=["fecha", "date"]),
        "dist":    _find(df, ["TOT DIST", "TOTAL DIST", "DIST TOTAL", "DISTANCIA"], contains=["tot dist", "dist total"]),
        "mtsmin":  _find(df, ["MTS/MIN", "MTS_MIN", "M/MIN", "MTSMIN"], contains=["mts/min", "m/min"]),
        # HSD: en la hoja real no hay "HSD" → equivale a la distancia en alta velocidad (>19 km/h).
        "hsd":     _find(df, ["MTS>19 KM/H", "MTS >19 KM/H", "HSD", "HIGH SPEED"], contains=[]),
        # Sprints: en la hoja real es el conteo de sprints >24 km/h.
        "sprints": _find(df, ["#SP24", "SPRINTS", "SPRINT", "N SPRINTS"], contains=[]),
        "acel":    _find(df, ["ACEL", "ACC", "ACELERACIONES"], contains=[]),
        "des":     _find(df, ["DES", "DEC", "DESACEL"], contains=[]),
        "vmax":    _find(df, ["V-MAX", "VMAX", "V MAX", "MAX SPEED"], contains=["v-max", "vmax"]),
        # Minutos reales (columna MIN). Exact-only para no confundir con MTS/MIN o PL/MIN.
        "minutos": _find(df, ["MIN", "MINUTOS", "MINUTES", "MIN JUGADOS"], contains=[]),
    }


def mapear_columnas_lesiones(df):
    return {
        "jugador": _find(df, ["JUG", "JUGADOR", "NOMBRE", "PLAYER"], contains=["jug", "player", "nombre"]),
        "fecha":   _find(df, ["FECHA", "DATE"], contains=["fecha", "date"]),
        "region":  _find(df, ["REGION", "REGIÓN", "ZONA"], contains=["region", "zona"]),
        "lado":    _find(df, ["LADO", "SIDE"], contains=["lado", "side"]),
        "tipo":    _find(df, ["TIPO", "TYPE"], contains=["tipo"]),
        "dias_baja": _find(df, ["DAY_OFF_DXT", "DIAS_BAJA", "DAYS_OFF"], contains=["day_off", "dias_baja", "days_off"]),
    }


def _to_num(s):
    """Serie → numérico, tolerando coma decimal."""
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def _norm_nombre(x):
    """
    Clave de nombre robusta para cruzar GPS ↔ lesiones.
    Neutraliza: acentos, mayúsculas, puntuación, espacios extra y ORDEN de tokens
    ("García, Juan" == "Juan Garcia" == "JUAN  GARCÍA").
    """
    import unicodedata, re as _re
    s = str(x)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")  # quita acentos
    s = _re.sub(r"[^a-zA-Z\s]", " ", s).lower()        # solo letras y espacios
    toks = [t for t in s.split() if t]
    return " ".join(sorted(toks))                       # orden-independiente


# ─────────────────────────────────────────────────────────────────────────
#  2. FWF — FOOTBALLER WORKLOAD FOOTPRINT  (por sesión, normalizado por min)
# ─────────────────────────────────────────────────────────────────────────
#  Pesos del compuesto (suman 1.0). Cada componente se normaliza min-max
#  dentro del dataset para que ninguna unidad (metros vs nº sprints) domine.
FWF_PESOS = {"dist": 0.30, "hsd": 0.25, "sprints": 0.20, "acel": 0.15, "des": 0.10}


def _minmax(s):
    s = pd.to_numeric(s, errors="coerce")
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - lo) / (hi - lo)


def calcular_fwf(df_gps, cols=None):
    """
    Agrega columnas: FWF_raw, FWF (0-100), _min (minutos estimados), _fecha.
    Minutos estimados = TOT DIST / (MTS/MIN) cuando no hay columna de minutos.
    """
    df = df_gps.copy()
    cols = cols or mapear_columnas_gps(df)

    # Componentes numéricos (los ausentes quedan en 0 → no aportan).
    comp = {}
    for k in FWF_PESOS:
        c = cols.get(k)
        comp[k] = _to_num(df[c]).fillna(0) if c and c in df.columns else pd.Series(np.zeros(len(df)), index=df.index)

    # FWF crudo = suma ponderada de componentes normalizados (0-1).
    fwf_raw = sum(FWF_PESOS[k] * _minmax(comp[k]) for k in FWF_PESOS)

    # Minutos: 1) columna MIN real → 2) estimar dist/(mts/min) → 3) fallback 90'.
    minutos = None
    if cols.get("minutos") and cols["minutos"] in df.columns:
        minutos = _to_num(df[cols["minutos"]])
    if (minutos is None or minutos.isna().all()) and cols.get("dist") and cols.get("mtsmin"):
        dist = _to_num(df[cols["dist"]])
        mm = _to_num(df[cols["mtsmin"]]).replace(0, np.nan)
        minutos = (dist / mm)
    if minutos is None or minutos.isna().all():
        minutos = pd.Series(np.full(len(df), 90.0), index=df.index)  # fallback 90'
    minutos = minutos.clip(lower=10, upper=130).fillna(minutos.median() if minutos.notna().any() else 90)

    # Normalizar por minutos (carga por minuto) y reescalar a 0-100.
    fwf_pm = fwf_raw / (minutos / 90.0)          # referencia: partido de 90'
    df["_min"] = minutos.round(1)
    df["FWF_raw"] = fwf_raw.round(4)
    df["FWF"] = (_minmax(fwf_pm) * 100).round(1)

    if cols.get("fecha"):
        df["_fecha"] = pd.to_datetime(df[cols["fecha"]], dayfirst=True, errors="coerce")
    return df


# ─────────────────────────────────────────────────────────────────────────
#  3. FEATURES DE CARGA ACUMULADA  (por jugador, orden temporal, sin fuga)
# ─────────────────────────────────────────────────────────────────────────
def construir_features(df_gps, cols=None):
    """
    Para cada (jugador, fecha) calcula features que usan SOLO el pasado:
      - carga_dia (FWF_raw del día)
      - aguda_7d, cronica_28d, ACWR
      - monotonia (Foster), strain
      - fwf_7d, dist_7d, hsd_7d, sprints_7d
    """
    cols = cols or mapear_columnas_gps(df_gps)
    df = calcular_fwf(df_gps, cols)
    jcol = cols.get("jugador")
    if not jcol or "_fecha" not in df.columns:
        return pd.DataFrame()

    df = df.dropna(subset=["_fecha"]).copy()
    df["_jug"] = df[jcol].astype(str).str.strip()
    df["_key"] = df["_jug"].map(_norm_nombre)

    dist = _to_num(df[cols["dist"]]) if cols.get("dist") else pd.Series(0.0, index=df.index)
    hsd  = _to_num(df[cols["hsd"]])  if cols.get("hsd")  else pd.Series(0.0, index=df.index)
    spr  = _to_num(df[cols["sprints"]]) if cols.get("sprints") else pd.Series(0.0, index=df.index)
    df["_dist"] = dist.fillna(0)
    df["_hsd"] = hsd.fillna(0)
    df["_spr"] = spr.fillna(0)
    df["_carga"] = df["FWF_raw"].fillna(0)

    filas = []
    for jug, g in df.groupby("_jug"):
        g = g.sort_values("_fecha").set_index("_fecha")
        key = _norm_nombre(jug)
        agu = g["_carga"].rolling("7D").sum()
        cro = g["_carga"].rolling("28D").mean() * 7
        acwr = (agu / cro.replace(0, np.nan))
        sd7 = g["_carga"].rolling("7D").std()
        mean7 = g["_carga"].rolling("7D").mean()
        monotonia = (mean7 / sd7.replace(0, np.nan))
        strain = agu * monotonia
        out = pd.DataFrame({
            "_jug": jug, "_key": key, "_fecha": g.index,
            "carga_dia": g["_carga"].values,
            "aguda_7d": agu.values, "cronica_28d": cro.values,
            "ACWR": acwr.values, "monotonia": monotonia.values, "strain": strain.values,
            "fwf_7d": g["_carga"].rolling("7D").sum().values,
            "dist_7d": g["_dist"].rolling("7D").sum().values,
            "hsd_7d": g["_hsd"].rolling("7D").sum().values,
            "sprints_7d": g["_spr"].rolling("7D").sum().values,
            "FWF": g["FWF"].values,
        })
        filas.append(out)
    feat = pd.concat(filas, ignore_index=True) if filas else pd.DataFrame()
    return feat.replace([np.inf, -np.inf], np.nan)


FEATURES_ML = ["carga_dia", "aguda_7d", "cronica_28d", "ACWR",
               "monotonia", "strain", "fwf_7d", "dist_7d", "hsd_7d", "sprints_7d"]


# ─────────────────────────────────────────────────────────────────────────
#  4. ETIQUETADO  ·  ¿lesión en los próximos N días?
# ─────────────────────────────────────────────────────────────────────────
def etiquetar(feat, df_les, ventana_dias=10, cols_les=None):
    """Marca lesion_proxima=1 si el jugador se lesionó dentro de `ventana_dias`."""
    feat = feat.copy()
    feat["lesion_proxima"] = 0
    if df_les is None or df_les.empty:
        return feat
    cl = cols_les or mapear_columnas_lesiones(df_les)
    jc, fc = cl.get("jugador"), cl.get("fecha")
    if not jc or not fc:
        return feat
    les = df_les[[jc, fc]].copy()
    les["_key"] = les[jc].map(_norm_nombre)
    les["_fles"] = pd.to_datetime(les[fc], dayfirst=True, errors="coerce")
    les = les.dropna(subset=["_fles"])

    by_jug = {j: g["_fles"].sort_values().values for j, g in les.groupby("_key")}
    vd = np.timedelta64(ventana_dias, "D")
    z = np.timedelta64(0, "D")
    lab = np.zeros(len(feat), dtype=int)
    fechas = feat["_fecha"].values
    jugs = feat["_key"].values if "_key" in feat.columns else feat["_jug"].map(_norm_nombre).values
    for i in range(len(feat)):
        fechas_les = by_jug.get(jugs[i])
        if fechas_les is None:
            continue
        d = fechas_les - fechas[i]
        if np.any((d >= z) & (d <= vd)):
            lab[i] = 1
    feat["lesion_proxima"] = lab
    return feat


# ─────────────────────────────────────────────────────────────────────────
#  5. ENTRENAMIENTO  ·  RandomForest (split temporal) o fallback por reglas
# ─────────────────────────────────────────────────────────────────────────
MIN_POSITIVOS = 12   # mínimo de lesiones etiquetadas para entrenar RF con sentido


def _score_reglas(feat):
    """Score 0-100 por reglas (cuando no hay datos para ML). Basado en literatura ACWR."""
    f = feat.copy()
    acwr = f["ACWR"].fillna(1.0)
    mono = f["monotonia"].fillna(1.0)
    riesgo = np.zeros(len(f))
    riesgo += np.clip((acwr - 1.3) / 0.7, 0, 1) * 55      # ACWR sobre 1.3 (zona riesgo)
    riesgo += np.clip((acwr.rsub(0.8)) / 0.8, 0, 1) * 15  # ACWR muy bajo (destraining)
    riesgo += np.clip((mono - 2.0) / 1.5, 0, 1) * 30      # monotonía alta (Foster)
    f["riesgo"] = pd.Series(riesgo, index=f.index).round(1).clip(0, 100)  # ya está en escala 0-100
    return f, "reglas"


def entrenar_modelo(feat_etiquetado):
    """
    Devuelve dict:
      modo: 'ml' | 'reglas'
      feat: DataFrame con columna 'riesgo' (0-100)
      modelo, metricas, importancias  (solo en modo 'ml')
    """
    f = feat_etiquetado.dropna(subset=FEATURES_ML).copy()
    n_pos = int(f["lesion_proxima"].sum()) if "lesion_proxima" in f.columns else 0

    if n_pos < MIN_POSITIVOS or len(f) < 40:
        feat_r, _ = _score_reglas(feat_etiquetado)
        return {"modo": "reglas", "feat": feat_r, "n_pos": n_pos,
                "metricas": None, "importancias": None, "modelo": None}

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

    f = f.sort_values("_fecha").reset_index(drop=True)
    corte = int(len(f) * 0.75)                     # split TEMPORAL: pasado→train, futuro→test
    tr, te = f.iloc[:corte], f.iloc[corte:]
    Xtr, ytr = tr[FEATURES_ML], tr["lesion_proxima"]
    Xte, yte = te[FEATURES_ML], te["lesion_proxima"]

    clf = RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=5,
                                 class_weight="balanced", random_state=42, n_jobs=-1)
    clf.fit(Xtr, ytr)

    metricas = None
    if yte.nunique() > 1:
        proba_te = clf.predict_proba(Xte)[:, 1]
        pred_te = (proba_te >= 0.5).astype(int)
        metricas = {
            "auc": round(float(roc_auc_score(yte, proba_te)), 3),
            "precision": round(float(precision_score(yte, pred_te, zero_division=0)), 3),
            "recall": round(float(recall_score(yte, pred_te, zero_division=0)), 3),
            "f1": round(float(f1_score(yte, pred_te, zero_division=0)), 3),
            "n_train": len(tr), "n_test": len(te), "n_pos": n_pos,
        }

    # Re-entrenar con todo y puntuar el dataset completo (probabilidad → 0-100).
    clf.fit(f[FEATURES_ML], f["lesion_proxima"])
    f["riesgo"] = (clf.predict_proba(f[FEATURES_ML])[:, 1] * 100).round(1)
    importancias = (pd.DataFrame({"feature": FEATURES_ML, "peso": clf.feature_importances_})
                    .sort_values("peso", ascending=False).reset_index(drop=True))
    return {"modo": "ml", "feat": f, "modelo": clf, "metricas": metricas,
            "importancias": importancias, "n_pos": n_pos}


def nivel_riesgo(score):
    if score >= 66: return "ALTO", "#ef4444"
    if score >= 33: return "MEDIO", "#fbbf24"
    return "BAJO", "#4ade80"


def riesgo_actual_por_jugador(res):
    """Último score de riesgo por jugador (la foto 'hoy')."""
    f = res["feat"]
    if f.empty or "riesgo" not in f.columns:
        return pd.DataFrame()
    ult = (f.sort_values("_fecha").groupby("_jug").tail(1)
           .sort_values("riesgo", ascending=False)
           [["_jug", "_fecha", "riesgo", "ACWR", "monotonia", "FWF"]]
           .reset_index(drop=True))
    ult.columns = ["Jugador", "Última sesión", "Riesgo", "ACWR", "Monotonía", "FWF"]
    return ult


# ════════════════════════════════════════════════════════════════════════
#  STREAMLIT  ·  Página integrable en la app (imports perezosos)
# ════════════════════════════════════════════════════════════════════════
def pagina_riesgo_lesion(cargar_sheet, pdf_btn=None, html_table=None):
    """
    Página de la app. Recibe la función `cargar_sheet` de app.py y,
    opcionalmente, `pdf_btn` y `html_table` de app.py para exportar el
    informe y renderizar la tabla ordenable con el mismo estilo del resto.
    Uso en el router:  "riesgo_lesion": lambda: pagina_riesgo_lesion(cargar_sheet, pdf_btn, html_table)
    """
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go

    st.markdown('<div class="sec-title">🤖 Riesgo de Lesión — Modelo FWF</div>', unsafe_allow_html=True)

    # ── ¿Qué es el FWF? — explicación en lenguaje simple para quien no
    # maneja el detalle técnico (cuerpo médico, cuerpo técnico). ──────
    with st.expander("ℹ️ ¿Qué es el FWF y cómo se calcula el riesgo?", expanded=False):
        st.markdown(
            '<div style="font-size:13px;color:#cbd5e1;line-height:1.7;">'
            '<b style="color:#93c5fd;">Footballer Workload Footprint (FWF)</b> es un índice propio, '
            'de <b>0 a 100</b>, que resume en un solo número cuánto exigió físicamente una sesión de '
            'entrenamiento o partido a un jugador. No es un dato de GPS más — es la combinación '
            'ponderada de las cinco variables de carga que más se asocian con fatiga y sobrecarga:'
            '<ul style="margin:10px 0 10px 18px;padding:0;">'
            '<li><b>Distancia total</b> — 30% del índice</li>'
            '<li><b>Distancia a alta velocidad (HSD)</b> — 25%</li>'
            '<li><b>Cantidad de sprints</b> — 20%</li>'
            '<li><b>Aceleraciones</b> — 15%</li>'
            '<li><b>Desaceleraciones</b> — 10%</li>'
            '</ul>'
            'El resultado se ajusta además por los minutos jugados, para que una sesión de 45\' y '
            'una de 90\' sean comparables sin penalizar al jugador que estuvo menos tiempo en cancha.'
            '<br><br>'
            '<b style="color:#93c5fd;">¿Y el score de Riesgo?</b> Se calcula sobre el <i>historial</i> '
            'de FWF de cada jugador, no sobre una sola sesión: mira cuánta carga acumuló en los '
            'últimos 7 días frente a su promedio de 28 días (ACWR), qué tan pareja o irregular fue '
            'esa carga semana a semana (monotonía), y combina eso con un modelo entrenado sobre el '
            'historial de lesiones del club (o, si todavía no hay lesiones suficientes cargadas, con '
            'un modo basado en reglas y umbrales de la literatura científica del deporte).'
            '<br><br>'
            '<b style="color:#f87171;">Importante:</b> el score es una herramienta de apoyo — nunca '
            'reemplaza el criterio del cuerpo médico. Un jugador en "Riesgo Alto" no está lesionado '
            'ni va a lesionarse necesariamente: significa que su patrón de carga reciente se parece '
            'al de jugadores que, históricamente, terminaron lesionándose. Vale la pena mirarlo con '
            'más atención, no sacarlo de la cancha automáticamente.'
            '</div>', unsafe_allow_html=True)

    gps = cargar_sheet("gps")
    les = cargar_sheet("lesiones")
    if gps is None or gps.empty:
        st.warning("No se pudo cargar la hoja GPS."); return

    # ── Filtros (mismo criterio que el resto de la app) ──────────────
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    cg = mapear_columnas_gps(gps)
    col_temp = _find(gps, ["TEMP", "AÑO", "ANIO"], contains=[])
    col_pos = _find(gps, ["POS"], contains=[])
    with f1:
        if col_temp:
            ts = ["Todas"] + sorted([str(x) for x in gps[col_temp].dropna().unique() if str(x) != "nan"], reverse=True)
            tsel = st.selectbox("Año", ts, index=1 if len(ts) > 1 else 0, key="rl_temp")
            if tsel != "Todas":
                gps = gps[gps[col_temp].astype(str) == tsel]
    with f2:
        if col_pos:
            ps = sorted([str(x) for x in gps[col_pos].dropna().unique() if str(x) != "nan"])
            psel = st.multiselect("Posición", ps, default=[], key="rl_pos")
            if psel:
                gps = gps[gps[col_pos].astype(str).isin(psel)]
    with f3:
        if cg.get("jugador"):
            js = sorted([str(x) for x in gps[cg["jugador"]].dropna().unique()])
            jsel = st.multiselect("Jugador", js, default=[], key="rl_jug")
            if jsel:
                gps = gps[gps[cg["jugador"]].astype(str).isin(jsel)]
    with f4:
        ventana = st.slider("Ventana de predicción (días)", 5, 21, 10, 1, key="riesgo_ventana",
                            help="Etiqueta como 'riesgo' una sesión si el jugador se lesiona dentro de esta ventana.")
    st.markdown('</div>', unsafe_allow_html=True)

    if gps.empty:
        st.info("Sin sesiones para los filtros seleccionados."); return

    @st.cache_data(ttl=300, show_spinner="Entrenando modelo de riesgo…")
    def _pipeline(gps_in, les_in, vent):
        # OJO: los parámetros NO llevan guion bajo a propósito. Streamlit
        # excluye del hash de cache_data cualquier parámetro que empiece con
        # "_" — con _gps/_les el cache quedaba fijo la primera vez y jamás
        # se recalculaba al cambiar el filtro de Año (que sí cambia el
        # contenido de gps). Sin el guion bajo, Streamlit hashea el
        # DataFrame filtrado y el cache se invalida correctamente.
        feat = construir_features(gps_in)
        if feat.empty:
            return None
        feat = etiquetar(feat, les_in if les_in is not None else pd.DataFrame(), ventana_dias=vent)
        return entrenar_modelo(feat)

    res = _pipeline(gps, les, ventana)
    if res is None:
        st.warning("No hay columnas suficientes (jugador/fecha) en la hoja GPS."); return

    riesgo_jug = riesgo_actual_por_jugador(res)
    modo = res["modo"]

    # ── Banner explicativo ───────────────────────────────────────────
    if modo == "ml":
        m = res["metricas"]
        sub = f"RandomForest entrenado · {res['n_pos']} eventos de lesión etiquetados"
        if m: sub += f" · AUC test={m['auc']} · Recall={m['recall']}"
    else:
        sub = f"Modo basado en reglas (ACWR/monotonía) · solo {res['n_pos']} lesiones etiquetadas, insuficiente para entrenar ML fiable"
    st.markdown(
        f'<div style="background:rgba(26,90,180,0.08);border:1px solid rgba(26,90,180,0.25);'
        f'border-radius:12px;padding:14px 18px;margin:8px 0 14px;">'
        f'<div style="font-weight:700;color:#93c5fd;font-size:13px;">Footballer Workload Footprint (FWF)</div>'
        f'<div style="color:#94a3b8;font-size:12px;margin-top:4px;">{sub}</div></div>',
        unsafe_allow_html=True)

    # ── KPIs ─────────────────────────────────────────────────────────
    if not riesgo_jug.empty:
        n_alto = int((riesgo_jug["Riesgo"] >= 66).sum())
        n_medio = int(((riesgo_jug["Riesgo"] >= 33) & (riesgo_jug["Riesgo"] < 66)).sum())
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🔴 Riesgo alto", n_alto)
        k2.metric("🟡 Riesgo medio", n_medio)
        k3.metric("👥 Jugadores", len(riesgo_jug))
        k4.metric("🧠 Modo", "ML" if modo == "ml" else "Reglas")

    # ── Tabla de riesgo actual con semáforo ──────────────────────────
    st.markdown('<div class="subsec">Riesgo actual por jugador</div>', unsafe_allow_html=True)
    if riesgo_jug.empty:
        st.info("Sin datos de riesgo para mostrar.")
    else:
        hoy = pd.Timestamp.now().normalize()
        activos_mes = riesgo_jug[riesgo_jug["Última sesión"] >= (hoy - pd.Timedelta(days=30))]
        solo_activos = st.checkbox("Mostrar solo jugadores con registros en el último mes",
                                   value=True, key="rl_solo_activos",
                                   help="Desmarcá para ver también jugadores que ya no están sumando cargas (se fueron, lesión larga, etc.)")
        base_rj = activos_mes if solo_activos else riesgo_jug
        if base_rj.empty:
            st.warning("Nadie tiene registros en el último mes. Desmarcá el filtro para ver el histórico completo.")
        else:
            # Orden por defecto: alfabético. El usuario puede reordenar por
            # cualquier columna haciendo click en el encabezado de la tabla.
            vista_rj = base_rj.sort_values("Jugador").copy()
            vista_rj["Riesgo"] = vista_rj["Riesgo"].round(0)
            vista_rj["Nivel"] = vista_rj["Riesgo"].apply(lambda v: nivel_riesgo(v)[0])
            vista_rj["ACWR"] = vista_rj["ACWR"].round(2)
            # OJO: "Última sesión" queda como Timestamp real, NO como string
            # dd/mm/aaaa — así el click-para-ordenar de html_table ordena por
            # fecha real y no por texto (donde "22/07" quedaba antes que
            # "25/06" por orden alfabético de dígitos).
            cols_tabla = [c for c in ["Jugador","Última sesión","Riesgo","Nivel","ACWR"] if c in vista_rj.columns]
            vista_rj = vista_rj[cols_tabla].reset_index(drop=True)

            def _color_riesgo(v):
                try:
                    _, color = nivel_riesgo(float(v))
                    return f"background:{color}33;color:{color};font-weight:800"
                except Exception:
                    return None
            def _color_nivel(v):
                colores = {"BAJO":"#4ade80","MEDIO":"#fbbf24","ALTO":"#ef4444"}
                c = colores.get(str(v).upper())
                return f"background:{c}22;color:{c};font-weight:700" if c else None

            if html_table:
                html_table(vista_rj, custom_colors={"Riesgo":_color_riesgo,"Nivel":_color_nivel},
                          max_rows=max(len(vista_rj),10), height=min(60+38*len(vista_rj),460))
            else:
                st.dataframe(vista_rj, use_container_width=True, hide_index=True)
            st.caption(f"Mostrando {len(vista_rj)} jugadores"
                      f"{' con registros en el último mes' if solo_activos else ' (histórico completo)'}, "
                      f"orden alfabético por defecto — click en cualquier encabezado para ordenar por esa columna.")

        # ── Gráfico de barras de riesgo — filtro propio (últimos 2 meses)
        # y selector de orden. Independiente del filtro de la tabla de
        # arriba (que es de 1 mes) porque lo pediste distinto para cada uno. ──
        activos_2m = riesgo_jug[riesgo_jug["Última sesión"] >= (hoy - pd.Timedelta(days=60))]
        if not activos_2m.empty:
            orden_g = st.selectbox("Ordenar gráfico por", 
                                   ["Riesgo (mayor a menor)", "Alfabético", "Última sesión (más reciente)"],
                                   key="rl_orden_grafico")
            vista_g = activos_2m.copy()
            if orden_g == "Riesgo (mayor a menor)":
                vista_g = vista_g.sort_values("Riesgo", ascending=False)
            elif orden_g == "Alfabético":
                vista_g = vista_g.sort_values("Jugador")
            else:
                vista_g = vista_g.sort_values("Última sesión", ascending=False)

            fig = px.bar(vista_g, x="Jugador", y="Riesgo", template="plotly_dark",
                         color="Riesgo", color_continuous_scale=["#4ade80", "#fbbf24", "#ef4444"],
                         range_color=[0, 100])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(l=0, r=0, t=20, b=0), height=320, coloraxis_showscale=False,
                              font=dict(color="#ffffff"),
                              xaxis=dict(categoryorder="array", categoryarray=vista_g["Jugador"].tolist()))
            fig.update_xaxes(color="#ffffff"); fig.update_yaxes(color="#ffffff")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"{len(vista_g)} jugadores con registros en los últimos 2 meses.")
        else:
            st.info("Nadie tiene registros en los últimos 2 meses.")

    # ── Importancia de features (solo ML) ────────────────────────────
    if modo == "ml" and res["importancias"] is not None:
        st.markdown('<div class="subsec">¿Qué pesa en la predicción?</div>', unsafe_allow_html=True)
        imp = res["importancias"]
        figi = px.bar(imp, x="peso", y="feature", orientation="h", template="plotly_dark",
                      color_discrete_sequence=["#c8102e"])
        figi.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           margin=dict(l=0, r=0, t=10, b=0), height=300,
                           font=dict(color="#ffffff"),
                           yaxis=dict(categoryorder="total ascending", color="#ffffff"),
                           xaxis=dict(color="#ffffff"))
        st.plotly_chart(figi, use_container_width=True)

    # ── Evolución individual (riesgo + ACWR) ─────────────────────────
    feat = res["feat"]
    if not feat.empty:
        st.markdown('<div class="subsec">Evolución individual</div>', unsafe_allow_html=True)
        jugs = sorted(feat["_jug"].dropna().unique().tolist())
        jsel = st.selectbox("Jugador", jugs, key="riesgo_jug_sel")
        g = feat[feat["_jug"] == jsel].sort_values("_fecha")
        figt = go.Figure()
        figt.add_trace(go.Scatter(x=g["_fecha"], y=g["riesgo"], name="Riesgo",
                                  line=dict(color="#c8102e", width=2), mode="lines"))
        if "ACWR" in g.columns:
            figt.add_trace(go.Scatter(x=g["_fecha"], y=g["ACWR"] * 50, name="ACWR (×50)",
                                      line=dict(color="#60a5fa", width=1.5, dash="dot"), mode="lines"))
        figt.add_hline(y=66, line_dash="dot", line_color="#ef4444", annotation_text="Alto")
        figt.add_hline(y=33, line_dash="dot", line_color="#fbbf24", annotation_text="Medio")
        figt.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=20, b=0),
                           height=320, font=dict(color="#ffffff"),
                           xaxis=dict(color="#ffffff"), yaxis=dict(color="#ffffff"),
                           legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center",
                                       bgcolor="rgba(8,18,38,0.75)", bordercolor="rgba(255,255,255,0.15)",
                                       borderwidth=1, font=dict(color="#ffffff", size=11)))
        figt.update_annotations(font_color="#ffffff")
        st.plotly_chart(figt, use_container_width=True)

    # ── Nota metodológica (honestidad académica) ─────────────────────
    st.markdown(
        '<div style="background:rgba(200,16,46,0.06);border:1px dashed rgba(200,16,46,0.3);'
        'border-radius:12px;padding:12px 16px;margin-top:14px;font-size:11.5px;color:#94a3b8;">'
        '<b style="color:#f87171;">Nota metodológica.</b> El score es una herramienta de '
        '<b>apoyo a la decisión</b>, no un diagnóstico. Con datos de un solo club las lesiones '
        'son eventos escasos: el modelo se valida con <b>split temporal</b> (entrena con el pasado, '
        'evalúa sobre el futuro) para evitar fuga de datos, y reporta AUC/recall honestos. '
        'La métrica FWF y el ACWR aportan contexto de carga; la decisión final es del cuerpo médico.</div>',
        unsafe_allow_html=True)

    # ── Exportar PDF con semaforo de color (igual criterio que pantalla) ──
    if pdf_btn and not riesgo_jug.empty:
        exp_r = riesgo_jug.copy()
        exp_r["Última sesión"] = exp_r["Última sesión"].apply(
            lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else "—")
        exp_r["ACWR"] = exp_r["ACWR"].round(2)
        if "Monotonía" in exp_r.columns:
            exp_r["Monotonía"] = exp_r["Monotonía"].round(2)
        if "FWF" in exp_r.columns:
            exp_r["FWF"] = exp_r["FWF"].round(1)
        exp_r["Nivel"] = exp_r["Riesgo"].apply(lambda v: nivel_riesgo(v)[0])
        exp_r["Riesgo"] = exp_r["Riesgo"].round(1)
        cols_finales = [c for c in ["Jugador", "Última sesión", "Riesgo", "Nivel",
                                     "ACWR", "Monotonía", "FWF"] if c in exp_r.columns]
        exp_r = exp_r[cols_finales].reset_index(drop=True)
        est_r = pd.DataFrame("", index=exp_r.index, columns=exp_r.columns)
        for i, row in exp_r.iterrows():
            _, color = nivel_riesgo(row["Riesgo"])
            if "Riesgo" in est_r.columns:
                est_r.loc[i, "Riesgo"] = f"{color}|#ffffff"
            if "Nivel" in est_r.columns:
                est_r.loc[i, "Nivel"] = f"{color}|#ffffff"

        n_alto_pdf = int((riesgo_jug["Riesgo"] >= 66).sum())
        n_medio_pdf = int(((riesgo_jug["Riesgo"] >= 33) & (riesgo_jug["Riesgo"] < 66)).sum())
        k_pdf = [("Riesgo alto", n_alto_pdf), ("Riesgo medio", n_medio_pdf),
                 ("Jugadores", len(riesgo_jug)), ("Modo", "ML" if modo == "ml" else "Reglas")]
        pdf_btn("Riesgo de Lesion", kpis=k_pdf, matriz=exp_r, estilos=est_r,
                matriz_titulo="Riesgo actual por jugador", orientacion="L", key="riesgo",
                notas=f"Modelo FWF (RandomForest), ventana de prediccion {ventana} dias.")
