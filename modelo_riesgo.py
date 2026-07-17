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
def pagina_riesgo_lesion(cargar_sheet):
    """
    Página de la app. Recibe la función `cargar_sheet` de app.py.
    Uso en el router:  "riesgo_lesion": lambda: pagina_riesgo_lesion(cargar_sheet)
    """
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go

    st.markdown('<div class="sec-title">🤖 Riesgo de Lesión — Modelo FWF</div>', unsafe_allow_html=True)

    gps = cargar_sheet("gps")
    les = cargar_sheet("lesiones")
    if gps is None or gps.empty:
        st.warning("No se pudo cargar la hoja GPS."); return

    # Slider (cumple requisito del máster) → ventana de predicción
    cf1, cf2 = st.columns([2, 1])
    with cf1:
        ventana = st.slider("🪟 Ventana de predicción (días tras la sesión)",
                            min_value=5, max_value=21, value=10, step=1, key="riesgo_ventana",
                            help="Etiqueta como 'riesgo' una sesión si el jugador se lesiona dentro de esta ventana.")

    @st.cache_data(ttl=300, show_spinner="Entrenando modelo de riesgo…")
    def _pipeline(_gps, _les, vent):
        feat = construir_features(_gps)
        if feat.empty:
            return None
        feat = etiquetar(feat, _les if _les is not None else pd.DataFrame(), ventana_dias=vent)
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
        filas = ""
        for _, r in riesgo_jug.iterrows():
            niv, color = nivel_riesgo(r["Riesgo"])
            fecha = r["Última sesión"].strftime("%d/%m/%Y") if pd.notna(r["Última sesión"]) else "—"
            acwr = f'{r["ACWR"]:.2f}' if pd.notna(r["ACWR"]) else "—"
            filas += (
                f'<tr><td style="padding:9px 14px;color:#e2e8f0;">{r["Jugador"]}</td>'
                f'<td style="text-align:center;color:#94a3b8;">{fecha}</td>'
                f'<td style="text-align:center;font-weight:800;color:{color};">{r["Riesgo"]:.0f}</td>'
                f'<td style="text-align:center;"><span style="background:{color}22;color:{color};'
                f'border:1px solid {color}55;border-radius:6px;padding:2px 10px;font-size:11px;font-weight:700;">{niv}</span></td>'
                f'<td style="text-align:center;color:#cbd5e1;">{acwr}</td></tr>')
        st.markdown(
            f'<div style="background:#071428;border:1px solid rgba(26,90,180,0.3);border-radius:14px;overflow:hidden;">'
            f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
            f'<thead><tr>'
            + "".join(f'<th style="padding:10px 14px;text-align:{a};font-size:10px;letter-spacing:1.5px;'
                      f'text-transform:uppercase;color:#60a5fa;background:rgba(26,90,180,0.25);">{h}</th>'
                      for h, a in [("Jugador","left"),("Última sesión","center"),("Riesgo","center"),("Nivel","center"),("ACWR","center")])
            + f'</tr></thead><tbody>{filas}</tbody></table></div>', unsafe_allow_html=True)

        # ── Gráfico de barras de riesgo ──────────────────────────────
        fig = px.bar(riesgo_jug, x="Jugador", y="Riesgo", template="plotly_dark",
                     color="Riesgo", color_continuous_scale=["#4ade80", "#fbbf24", "#ef4444"],
                     range_color=[0, 100])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=0, r=0, t=20, b=0), height=320, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Importancia de features (solo ML) ────────────────────────────
    if modo == "ml" and res["importancias"] is not None:
        st.markdown('<div class="subsec">¿Qué pesa en la predicción?</div>', unsafe_allow_html=True)
        imp = res["importancias"]
        figi = px.bar(imp, x="peso", y="feature", orientation="h", template="plotly_dark",
                      color_discrete_sequence=["#c8102e"])
        figi.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           margin=dict(l=0, r=0, t=10, b=0), height=300,
                           yaxis=dict(categoryorder="total ascending"))
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
                           height=320, legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"))
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
