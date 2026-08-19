# ════════════════════════════════════════════════════════════════════════
#  demandas_fisicas.py  ·  TFM CAU
#
#  Reemplaza pagina_demandas(). Tres apartados:
#    1. Microciclo vs % de máximo de partido individual  (matriz tipo Power BI)
#    2. EWMA grupal por variable
#    3. EWMA individual
#
#  METODOLOGÍA (para el documento marco):
#  · Referencia individual (MD_IND) = promedio de los últimos N partidos
#    oficiales (SES = PARTIDO) en los que el jugador disputó > MIN_REF minutos.
#    Es la "demanda de competencia" propia de cada jugador.
#  · % IND = carga acumulada del microciclo / referencia individual × 100.
#    Si en los últimos 5 partidos promedia 10.000 m y en la semana lleva
#    20.000 m → 200%.
#  · EWMA (Williams et al., 2017): media móvil exponencial. Penaliza menos
#    el pasado lejano que el rolling simple del ACWR clásico.
#      EWMA_hoy = carga_hoy · λ + EWMA_ayer · (1 − λ),  λ = 2/(N+1)
#      Ratio = EWMA_agudo(7d) / EWMA_crónico(28d)
#
#  RENDIMIENTO: todo se agrega ANTES de mandar al browser y las tablas se
#  paginan. El bug de 249.8 MB venía de renderizar la hoja GPS completa
#  (miles de filas × 60 columnas) como HTML inline.
# ════════════════════════════════════════════════════════════════════════
import numpy as np
import pandas as pd

__version__ = "2026.07.17"

# ─────────────────────────────────────────────────────────────────────────
#  MÉTRICAS  ·  (clave lógica, etiqueta, candidatos de encabezado real)
# ─────────────────────────────────────────────────────────────────────────
METRICAS = [
    ("min",     "MIN",      ["MIN"]),
    ("td",      "TOT DIST", ["TOT DIST"]),
    ("mtsmin",  "MTS/MIN",  ["MTS/MIN"]),
    ("m19",     "MTS >19",  ["MTS>19 KM/H", "MTS >19 KM/H"]),
    ("m24",     "MTS >24",  ["MTS > 24 KM/H", "MTS >24 KM/H"]),
    ("sp24",    "#SP24",    ["#SP24"]),
    ("vi85",    "MTS 85VI", ["MTS >85% VEL IND"]),
    ("acel",    "ACEL",     ["ACEL"]),
    ("des",     "DES",      ["DES"]),
    ("vmax",    "V-MAX",    ["V-MAX"]),
]
# Métricas acumulables (sumatorias). El resto son promedio/máximo.
ACUMULABLES = {"min", "td", "m19", "m24", "sp24", "vi85", "acel", "des"}
# Las que se comparan contra la referencia de partido en la matriz.
COMPARABLES = ["td", "m19", "m24", "sp24", "vi85", "acel", "des"]
# Las que llevan tarjeta EWMA.
EWMA_METRICAS = ["td", "m19", "m24", "vi85", "acel", "des"]


# Sesiones que NO cuentan para carga del plantel principal ni para el EWMA.
# COMP_REC (compensatorio/recuperacion) sumado: es lo que excluye el filtro
# "SES no es ..." del Power BI de referencia (ahi solo quedan MIXTO y TACTICO).
SES_EXCLUIR_DEFAULT = ["RTT", "ENT RVA", "RESERVA", "PAR RVA", "ENT DIF", "HIIT", "COMP_REC"]


def _parse_fecha(serie):
    """
    Parseo tolerante. Antes se usaba solo dayfirst=True y las filas que no
    parseaban se borraban con dropna -> se perdian sesiones en silencio
    (por eso el conteo de N SES no coincidia con Power BI).
    """
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = pd.to_datetime(serie, dayfirst=True, errors="coerce")
        if f.isna().any():
            for kw in ({"format": "mixed", "dayfirst": True}, {"dayfirst": False}):
                try:
                    alt = pd.to_datetime(serie, errors="coerce", **kw)
                except Exception:
                    continue
                if alt.notna().sum() > f.notna().sum():
                    f = alt
    return f


def _find_exact(df, candidatos):
    """Match exacto (case-insensitive) — evita agarrar '#SP24 SEM' o 'MTS/MIN' por 'MIN'."""
    up = {str(c).upper().strip(): c for c in df.columns}
    for cand in candidatos:
        if cand.upper() in up:
            return up[cand.upper()]
    return None


def mapear(df):
    """Mapa clave lógica → columna real de la hoja GPS."""
    m = {k: _find_exact(df, cands) for k, _, cands in METRICAS}
    m["jugador"] = _find_exact(df, ["JUGADOR", "JUG"])
    m["fecha"]   = _find_exact(df, ["FECHA"])
    m["pos"]     = _find_exact(df, ["POS"])
    m["micro"]   = _find_exact(df, ["MICROCICLO", "MICRO"])
    m["semana"]  = _find_exact(df, ["SEMANA", "SEM"])
    m["ses"]     = _find_exact(df, ["SES"])
    m["temp"]    = _find_exact(df, ["TEMP"])
    m["ref"]     = _find_exact(df, ["REF"])
    m["ent"]     = _find_exact(df, ["ENT"])
    return m


def _num(s):
    """Serie → numérico. Tolera coma decimal y separador de miles."""
    return pd.to_numeric(
        s.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce")


def _num_simple(s):
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def preparar(df):
    """Normaliza la hoja GPS a un frame de trabajo liviano (solo lo necesario)."""
    m = mapear(df)
    if not m.get("jugador") or not m.get("fecha"):
        return None, m
    d = pd.DataFrame()
    d["_jug"] = df[m["jugador"]].astype(str).str.strip()
    d["_fecha"] = _parse_fecha(df[m["fecha"]])
    for campo in ["pos", "micro", "semana", "ses", "temp", "ref", "ent"]:
        d["_" + campo] = df[m[campo]].astype(str).str.strip() if m.get(campo) else ""
    for k, _, _ in METRICAS:
        col = m.get(k)
        if col:
            v = _num_simple(df[col])
            # Si quedó casi todo NaN, reintentar tratando el punto como miles.
            if v.notna().sum() < len(df) * 0.5:
                v2 = _num(df[col])
                if v2.notna().sum() > v.notna().sum():
                    v = v2
            d[k] = v
        else:
            d[k] = np.nan
    # NO se descartan filas con fecha invalida: la matriz agrupa por jugador y no
    # necesita la fecha. Solo EWMA y la referencia de partido la requieren, y ahi
    # se filtra localmente. El dropna global perdia sesiones en silencio.
    d.attrs["fechas_invalidas"] = int(d["_fecha"].isna().sum())
    d.attrs["filas_totales"] = len(d)
    return d, m


def es_partido(serie_ses):
    """SES que representa partido oficial."""
    s = serie_ses.astype(str).str.upper()
    return s.str.contains("PARTIDO|MATCH|MD|OFICIAL", regex=True, na=False)


# ─────────────────────────────────────────────────────────────────────────
#  REFERENCIA INDIVIDUAL DE PARTIDO  (últimos N partidos con > MIN_REF min)
# ─────────────────────────────────────────────────────────────────────────
def referencia_partido(d, n_partidos=5, min_ref=70, metrica_valida="m19"):
    """
    Replica el DAX del Power BI. Devuelve (ref_ind, ref_pos):

      ref_ind : MAXIMO por JUGADOR sobre sus ultimos `n_partidos` partidos
                oficiales con >= `min_ref` minutos y con la metrica de referencia
                no vacia  ->  MAXX(Ultimos5Partidos, ...).
      ref_pos : PROMEDIO por POSICION sobre TODOS los partidos validos de esa
                posicion  ->  fallback PromedioPorPosicion (PROM_JUG).

    Diferencias que estaban causando los '—':
      · el DAX usa MAX (no promedio) para la referencia individual;
      · el DAX ordena por fecha pero NO descarta partidos sin fecha: aca antes
        el dropna(_fecha) borraba partidos y dejaba jugadores sin referencia;
      · el promedio posicional se calcula sobre TODOS los partidos validos de la
        posicion, no solo los ultimos 5 de cada jugador.
    """
    cols = [k for k, _, _ in METRICAS]
    p = d[es_partido(d["_ses"]) & (d["min"] >= min_ref)].copy()
    # Exigir metrica de referencia no vacia (NOT ISBLANK del DAX).
    if metrica_valida in p.columns:
        p = p[p[metrica_valida].notna()]
    if p.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Orden por fecha DESC para el TOPN; los sin fecha van al final pero NO se descartan.
    p["_orden"] = p["_fecha"]
    p = p.sort_values("_orden", ascending=False, na_position="last")

    # ── ref_ind: MAX de los ultimos n_partidos por jugador ───────────
    ult = p.groupby("_jug").head(n_partidos)
    ref_ind = ult.groupby("_jug")[cols].max()
    ref_ind["_n_ref"] = ult.groupby("_jug").size()

    # ── ref_pos: PROMEDIO por posicion sobre TODOS los partidos validos ─
    ref_pos = p.groupby("_pos")[cols].mean()
    ref_pos["_n_ref"] = p.groupby("_pos").size()
    return ref_ind, ref_pos


def matriz_microciclo(d, ref_ind, ref_pos):
    """
    Carga acumulada del periodo filtrado por jugador + % vs su referencia.
    La posicion usada es la del MICROCICLO ACTUAL: si un jugador cambia de puesto,
    cambia su referencia posicional.
    """
    if d.empty:
        return pd.DataFrame()
    cols = [k for k, _, _ in METRICAS]
    agg = {k: ("sum" if k in ACUMULABLES else ("max" if k == "vmax" else "mean")) for k in cols}
    g = d.groupby("_jug").agg(agg)
    g["_n_ses"] = d.groupby("_jug").size()
    g["_pos"] = d.groupby("_jug")["_pos"].agg(lambda x: x.mode().iloc[0] if len(x.mode()) else "")

    origen, bases = [], {k: [] for k in COMPARABLES}
    for jug, pos in zip(g.index, g["_pos"]):
        usa_ind = (not ref_ind.empty) and (jug in ref_ind.index)
        usa_pos = (not ref_pos.empty) and (pos in ref_pos.index)
        origen.append("IND" if usa_ind else ("POS" if usa_pos else "-"))
        for k in COMPARABLES:
            if usa_ind:
                bases[k].append(ref_ind.loc[jug, k])
            elif usa_pos:
                bases[k].append(ref_pos.loc[pos, k])
            else:
                bases[k].append(np.nan)
    g["_base"] = origen
    for k in COMPARABLES:
        b = pd.Series(bases[k], index=g.index).replace(0, np.nan)
        g[f"pct_{k}"] = (g[k] / b * 100).round(0)
    return g.reset_index()


# ─────────────────────────────────────────────────────────────────────────
#  EWMA  ·  ratio agudo:crónico exponencial (Williams et al., 2017)
# ─────────────────────────────────────────────────────────────────────────
def ewma_serie(d, metrica, agudo=7, cronico=28):
    """
    Serie diaria por jugador con EWMA agudo, crónico y su ratio.
    Reindexa a días calendario (los días sin sesión cuentan como carga 0),
    que es lo correcto: el descanso baja la carga aguda.
    """
    if d.empty or metrica not in d.columns:
        return pd.DataFrame()
    base = d[["_jug", "_fecha", metrica]].dropna(subset=["_fecha"]).copy()
    if base.empty or base[metrica].notna().sum() == 0:
        return pd.DataFrame()
    diario = base.groupby(["_jug", "_fecha"])[metrica].sum().reset_index()

    salida = []
    for jug, g in diario.groupby("_jug"):
        g = g.set_index("_fecha").sort_index()
        idx = pd.date_range(g.index.min(), g.index.max(), freq="D")
        s = g[metrica].reindex(idx, fill_value=0)
        ag = s.ewm(alpha=2 / (agudo + 1), adjust=False).mean()
        cr = s.ewm(alpha=2 / (cronico + 1), adjust=False).mean()
        salida.append(pd.DataFrame({
            "_jug": jug, "_fecha": idx, "carga": s.values,
            "agudo": ag.values, "cronico": cr.values,
            "ratio": (ag / cr.replace(0, np.nan)).values,
        }))
    return pd.concat(salida, ignore_index=True) if salida else pd.DataFrame()


def ewma_resumen(d, metricas=None, agudo=7, cronico=28):
    """Último ratio EWMA por jugador y por métrica → DataFrame (jugadores × métricas)."""
    metricas = metricas or EWMA_METRICAS
    out = {}
    for k in metricas:
        s = ewma_serie(d, k, agudo, cronico)
        if s.empty:
            continue
        ult = s.sort_values("_fecha").groupby("_jug").tail(1).set_index("_jug")["ratio"]
        out[k] = ult
    return pd.DataFrame(out) if out else pd.DataFrame()


# ─────────────────────────────────────────────────────────────────────────
#  COLORES
# ─────────────────────────────────────────────────────────────────────────
def color_pct(v):
    """Escala tipo Power BI para % vs referencia de partido."""
    if pd.isna(v):
        return "#1e293b", "#64748b"
    if v >= 200: return "#dc2626", "#fff"
    if v >= 150: return "#f97316", "#0f172a"
    if v >= 100: return "#facc15", "#0f172a"
    if v >= 60:  return "#4ade80", "#0f172a"
    return "#86efac", "#0f172a"


def color_ewma(v):
    """Zona de seguridad EWMA: 0.8–1.3 verde."""
    if pd.isna(v):
        return "#64748b"
    if v >= 1.5: return "#dc2626"
    if v >= 1.3: return "#f97316"
    if v >= 0.8: return "#4ade80"
    return "#60a5fa"


# ════════════════════════════════════════════════════════════════════════
#  STREAMLIT
# ════════════════════════════════════════════════════════════════════════
def _tarjeta(label, valor, color="#fff", sub=""):
    return (f'<div style="flex:1;min-width:88px;background:rgba(8,18,38,.9);'
            f'border:1px solid rgba(26,90,180,.3);border-radius:10px;padding:9px 8px;text-align:center;">'
            f'<div style="font-size:20px;font-weight:900;color:{color};line-height:1.1;">{valor}</div>'
            f'<div style="font-size:8.5px;letter-spacing:1px;color:#94a3b8;text-transform:uppercase;'
            f'margin-top:3px;font-weight:700;">{label}</div>'
            + (f'<div style="font-size:8px;color:#64748b;margin-top:1px;">{sub}</div>' if sub else "")
            + '</div>')


def _fila_tarjetas(items):
    return ('<div style="display:flex;gap:7px;flex-wrap:wrap;margin:8px 0 14px;">'
            + "".join(items) + "</div>")


def pagina_demandas_fisicas(cargar_sheet, pdf_btn=None):
    """Página completa. Pasar cargar_sheet (y opcionalmente pdf_btn) desde app.py."""
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go

    st.markdown('<div class="sec-title">📡 Demandas Físicas — GPS</div>', unsafe_allow_html=True)

    raw = cargar_sheet("gps")
    if raw is None or raw.empty:
        st.warning("No se pudo cargar la hoja GPS."); return

    @st.cache_data(ttl=600, show_spinner="Procesando GPS…")
    def _prep(_raw):
        d, m = preparar(_raw)
        return d, m
    d, m = _prep(raw)
    if d is None or d.empty:
        st.error("No se encontraron las columnas JUGADOR / FECHA en la hoja GPS."); return

    # ── Exclusion de sesiones que no son del plantel principal ───────
    ses_todas = sorted([x for x in d["_ses"].unique() if x and x != "nan"])
    pre = [x for x in ses_todas if x.upper().strip() in [e.upper() for e in SES_EXCLUIR_DEFAULT]]
    with st.expander("⚙️ Sesiones excluidas del cálculo  ·  " + (", ".join(pre) if pre else "ninguna detectada"),
                     expanded=False):
        st.caption("Estas sesiones no cuentan para los promedios ni para el EWMA "
                   "(no son carga del plantel principal).")
        excl = st.multiselect("Excluir", ses_todas, default=pre, key="dem_excl")
    d = d[~d["_ses"].isin(excl)] if excl else d
    if d.empty:
        st.warning("Todas las sesiones quedaron excluidas."); return

    t1, t2, t3 = st.tabs(["📊 Microciclo vs Partido", "📈 EWMA grupal", "👤 EWMA individual"])

    # ═════════════════════════════════════════════════════════════════
    #  TAB 1 — MATRIZ MICROCICLO vs % MÁXIMO DE PARTIDO INDIVIDUAL
    # ═════════════════════════════════════════════════════════════════
    with t1:
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        f1, f2, f3, f4 = st.columns(4)
        dff = d.copy()
        with f1:
            temps = ["Todas"] + sorted([x for x in dff["_temp"].unique() if x and x != "nan"], reverse=True)
            tsel = st.selectbox("Año", temps, index=1 if len(temps) > 1 else 0, key="dem_temp")
            if tsel != "Todas": dff = dff[dff["_temp"] == tsel]
        with f2:
            mics = ["Todos"] + sorted([x for x in dff["_micro"].unique() if x and x != "nan"],
                                      key=lambda z: (len(z), z), reverse=True)
            msel = st.selectbox("Microciclo", mics, index=1 if len(mics) > 1 else 0, key="dem_mic")
            if msel != "Todos": dff = dff[dff["_micro"] == msel]
        with f3:
            sems = ["Todas"] + sorted([x for x in dff["_semana"].unique() if x and x != "nan"],
                                      key=lambda z: (len(z), z))
            semsel = st.selectbox("Semana", sems, key="dem_sem")
            if semsel != "Todas": dff = dff[dff["_semana"] == semsel]
        with f4:
            poss = sorted([x for x in dff["_pos"].unique() if x and x != "nan"])
            psel = st.multiselect("Posición", poss, default=[], key="dem_pos")
            if psel: dff = dff[dff["_pos"].isin(psel)]

        g1, g2, g3, g4 = st.columns(4)
        with g1:
            # FILTRO FECHA (faltaba)
            val = dff["_fecha"].dropna()
            if not val.empty:
                fmin, fmax = val.min().date(), val.max().date()
                rango = st.date_input("Rango de fechas", value=(fmin, fmax),
                                      min_value=fmin, max_value=fmax, key="dem_fecha")
                if isinstance(rango, (list, tuple)) and len(rango) == 2:
                    ini, fin = pd.Timestamp(rango[0]), pd.Timestamp(rango[1]) + pd.Timedelta(days=1)
                    dff = dff[dff["_fecha"].isna() | ((dff["_fecha"] >= ini) & (dff["_fecha"] < fin))]
        with g2:
            n_part = st.slider("Partidos de referencia", 3, 10, 5, key="dem_npart",
                               help="Cuántos partidos oficiales recientes definen la demanda de competencia.")
        with g3:
            min_ref = st.slider("Minutos mínimos por partido", 45, 90, 70, step=5, key="dem_minref")
        with g4:
            jugs = sorted(dff["_jug"].unique().tolist())
            jsel = st.multiselect("Jugador", jugs, default=[], key="dem_jug")
            if jsel: dff = dff[dff["_jug"].isin(jsel)]
        st.markdown('</div>', unsafe_allow_html=True)

        if dff.empty:
            st.info("Sin sesiones para los filtros seleccionados."); return

        # Referencia sobre el histórico completo (no sobre el micro filtrado).
        ref_ind, ref_pos = referencia_partido(d, n_part, min_ref)
        mat = matriz_microciclo(dff, ref_ind, ref_pos)

        # ── DIAGNÓSTICO (para cotejar contra Power BI) ───────────────
        with st.expander("🔎 Diagnóstico de datos — comparar con Power BI", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Filas hoja GPS", d.attrs.get("filas_totales", len(d)))
            c2.metric("Fechas inválidas", d.attrs.get("fechas_invalidas", 0),
                      help="Filas cuya FECHA no se pudo interpretar. Ya NO se descartan de la matriz.")
            c3.metric("Sesiones tras filtros", len(dff))
            c4.metric("Jugadores", dff["_jug"].nunique())
            st.caption("Si el N SES de un jugador no coincide con tu Power BI, mirá acá qué sesiones está tomando:")
            jd = st.selectbox("Ver sesiones de", sorted(dff["_jug"].unique()), key="dem_diag")
            det = dff[dff["_jug"] == jd][["_fecha", "_ses", "_micro", "_semana", "min", "td"]].sort_values("_fecha")
            det.columns = ["Fecha", "Sesión", "Micro", "Semana", "MIN", "TOT DIST"]
            st.dataframe(det, use_container_width=True, hide_index=True)

        # ── Tarjetas: PROMEDIO DEL ACUMULADO SEMANAL por jugador ─────
        labs = dict((a, b) for a, b, _ in METRICAS)
        proms = []
        for k, lab, _ in METRICAS:
            if k in dff.columns and dff[k].notna().any():
                if k in ACUMULABLES:
                    v = dff.groupby("_jug")[k].sum().mean()   # promedio del acumulado del microciclo
                elif k == "vmax":
                    v = dff.groupby("_jug")[k].max().mean()
                else:
                    v = dff[k].mean()
                if pd.notna(v):
                    proms.append(_tarjeta(f"PROM {lab}",
                                          f"{v:,.0f}".replace(",", ".") if abs(v) >= 100 else f"{v:.1f}"))
        st.markdown(_fila_tarjetas(proms), unsafe_allow_html=True)
        st.caption("Promedio del **acumulado del microciclo** por jugador (no el promedio por sesión).")

        # ── Tarjetas EWMA ────────────────────────────────────────────
        base_ew = d if not jsel else d[d["_jug"].isin(jsel)]
        ew = ewma_resumen(base_ew)
        if not ew.empty:
            cards = [_tarjeta(f"EWMA {labs[k]}", f"{ew[k].mean():.2f}", color_ewma(ew[k].mean()))
                     for k in EWMA_METRICAS if k in ew.columns and pd.notna(ew[k].mean())]
            st.markdown('<div class="subsec">Ratio agudo:crónico exponencial (EWMA 7:28)</div>',
                        unsafe_allow_html=True)
            st.markdown(_fila_tarjetas(cards), unsafe_allow_html=True)

        # ── Matriz ───────────────────────────────────────────────────
        st.markdown('<div class="subsec">Microciclo vs % de máximo de partido individual</div>',
                    unsafe_allow_html=True)
        if mat.empty:
            st.info("Sin datos."); return
        n_pos_base = int((mat["_base"] == "POS").sum())
        if n_pos_base:
            st.caption(f"⚠️ {n_pos_base} jugador(es) sin partidos oficiales de +{min_ref}' "
                       f"se comparan contra el promedio de su posición (marcados **POS**).")

        mat = mat.sort_values(["_pos", "_jug"])
        n_show = st.slider("Filas a mostrar", 5, max(10, len(mat)), min(10, len(mat)), key="dem_nrows")
        vista = mat.head(n_show)

        heads = ["JUGADOR", "N°SES", "POS", "BASE", "MIN", "TOT DIST"]
        for k in COMPARABLES:
            if k == "td": heads += ["% TD IND"]
            else: heads += [labs[k], f"% {labs[k].replace('MTS ','')} IND"]
        heads += ["V-MAX"]

        th = "".join(f'<th style="padding:6px 5px;font-size:8px;color:#fff;background:rgba(26,90,180,.4);'
                     f'text-transform:uppercase;white-space:nowrap;position:sticky;top:0;">{h}</th>' for h in heads)
        trs = ""
        for _, r in vista.iterrows():
            bcol = "#4ade80" if r["_base"] == "IND" else "#fbbf24"
            tds = (f'<td style="padding:5px 7px;color:#fff;white-space:nowrap;font-weight:600;">{r["_jug"]}</td>'
                   f'<td style="text-align:center;color:#cbd5e1;">{int(r["_n_ses"])}</td>'
                   f'<td style="text-align:center;color:#94a3b8;font-size:9px;">{r["_pos"]}</td>'
                   f'<td style="text-align:center;color:{bcol};font-size:9px;font-weight:700;">{r["_base"]}</td>'
                   f'<td style="text-align:center;color:#cbd5e1;">{0 if pd.isna(r["min"]) else int(r["min"])}</td>')
            for k in COMPARABLES:
                val, pct = r.get(k), r.get(f"pct_{k}")
                vtxt = "—" if pd.isna(val) else f"{val:,.0f}".replace(",", ".")
                bg, fg = color_pct(pct)
                ptxt = "—" if pd.isna(pct) else f"{pct:.0f}%"
                tds += f'<td style="text-align:center;color:#cbd5e1;">{vtxt}</td>'
                tds += (f'<td style="text-align:center;background:{bg};color:{fg};font-weight:800;'
                        f'font-size:10.5px;">{ptxt}</td>')
            vm = r.get("vmax")
            tds += f'<td style="text-align:center;color:#fff;font-weight:700;">{"—" if pd.isna(vm) else f"{vm:.1f}"}</td>'
            trs += f'<tr style="border-bottom:1px solid rgba(255,255,255,.05);">{tds}</tr>'
        st.markdown(f'<div style="background:#071428;border:1px solid rgba(26,90,180,.3);border-radius:12px;'
                    f'overflow:auto;max-height:480px;"><table style="width:max-content;min-width:100%;'
                    f'border-collapse:collapse;font-size:10.5px;"><thead><tr>{th}</tr></thead>'
                    f'<tbody>{trs}</tbody></table></div>', unsafe_allow_html=True)
        st.caption(f"Mostrando {len(vista)} de {len(mat)} jugadores · BASE **IND** = vs sus propios partidos · "
                   f"**POS** = vs promedio de su posición · % = carga microciclo ÷ referencia × 100")

        cd1, cd2 = st.columns([4, 1])
        with cd2:
            st.download_button("⬇️ CSV", mat.to_csv(index=False).encode("utf-8"),
                               "matriz_microciclo.csv", "text/csv", key="dem_csv",
                               use_container_width=True)

        # ── PDF: matriz COMPLETA, horizontal, con semáforo ───────────
        if pdf_btn:
            exp = pd.DataFrame({"JUGADOR": mat["_jug"], "N°SES": mat["_n_ses"], "POS": mat["_pos"],
                                "BASE": mat["_base"], "MIN": mat["min"], "TOT_DIST": mat["td"]})
            est = pd.DataFrame("", index=mat.index, columns=exp.columns)
            for k in COMPARABLES:
                cv, cp = labs[k], f"%{labs[k].replace('MTS ', '')}"
                if k != "td":
                    exp[cv] = mat[k]; est[cv] = ""
                exp[cp] = mat[f"pct_{k}"]
                est[cp] = [f"{color_pct(v)[0]}|{color_pct(v)[1]}" for v in mat[f"pct_{k}"]]
            exp["V-MAX"] = mat["vmax"]; est["V-MAX"] = ""
            est = est.reindex(columns=exp.columns, fill_value="")

            kp = []
            for k, lab, _ in METRICAS:
                if k in dff.columns and dff[k].notna().any():
                    v = dff.groupby("_jug")[k].sum().mean() if k in ACUMULABLES else dff[k].mean()
                    if pd.notna(v):
                        kp.append((f"PROM {lab}", f"{v:,.0f}" if abs(v) >= 100 else f"{v:.1f}"))
            for k in EWMA_METRICAS:
                if not ew.empty and k in ew.columns and pd.notna(ew[k].mean()):
                    vv = ew[k].mean()
                    rgb = (74, 222, 128) if 0.8 <= vv < 1.3 else ((249, 115, 22) if vv >= 1.3 else (96, 165, 250))
                    kp.append((f"EWMA {labs[k]}", f"{vv:.2f}", rgb))

            _nota=(f"% IND = carga acumulada del microciclo / referencia x 100. "
                   f"BASE IND: referencia = MAXIMO de los ultimos {n_part} partidos oficiales "
                   f"del jugador con mas de {min_ref} minutos. BASE POS: el jugador no tiene partidos "
                   f"que califiquen y se compara contra el promedio de su posicion. "
                   f"Sesiones excluidas del calculo: {', '.join(excl) if excl else 'ninguna'}. "
                   f"EWMA = ratio agudo(7d):cronico(28d) exponencial (Williams et al., 2017).")
            _kw=dict(subtitulo=f"Microciclo {msel} - Temporada {tsel} - Club A. Union",
                     kpis=kp, matriz=exp, estilos=est,
                     matriz_titulo="Microciclo vs % de max de partido individual",
                     orientacion="L", notas=_nota, key="dem1")
            try:
                pdf_btn("Demandas Fisicas - Microciclo", **_kw)
            except TypeError:
                # pdf_btn viejo (sin matriz/orientacion): degradar a export simple con la matriz como tabla.
                import streamlit as _st
                _st.info("El PDF avanzado requiere actualizar pdf_export.py y app.py. "
                         "Exporto la matriz en formato simple mientras tanto.")
                try:
                    pdf_btn("Demandas Fisicas - Microciclo", subtitulo=_kw["subtitulo"],
                            kpis=kp, tablas=[("Microciclo vs % de max de partido individual", exp)],
                            notas=_nota, key="dem1")
                except TypeError:
                    pdf_btn()  # ultimo recurso: firma original sin argumentos

    # ═════════════════════════════════════════════════════════════════
    #  TAB 2 — EWMA GRUPAL POR VARIABLE
    # ═════════════════════════════════════════════════════════════════
    with t2:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            temps2 = ["Todas"] + sorted([x for x in d["_temp"].unique() if x and x != "nan"], reverse=True)
            t2sel = st.selectbox("Año", temps2, index=1 if len(temps2) > 1 else 0, key="ew_temp")
        with c2:
            pos2 = sorted([x for x in d["_pos"].unique() if x and x != "nan"])
            p2sel = st.multiselect("Posición", pos2, default=[], key="ew_pos")
        with c3:
            mics2 = ["Todos"] + sorted([x for x in d["_micro"].unique() if x and x != "nan"],
                                       key=lambda z: (len(z), z), reverse=True)
            m2sel = st.selectbox("Microciclo", mics2, key="ew_micro")
        with c4:
            val2 = d["_fecha"].dropna()
            rango2 = None
            if not val2.empty:
                f2min, f2max = val2.min().date(), val2.max().date()
                rango2 = st.date_input("Rango de fechas", value=(f2min, f2max),
                                       min_value=f2min, max_value=f2max, key="ew_fecha")

        dg = d.copy()
        if t2sel != "Todas": dg = dg[dg["_temp"] == t2sel]
        if p2sel: dg = dg[dg["_pos"].isin(p2sel)]
        if m2sel != "Todos": dg = dg[dg["_micro"] == m2sel]
        if isinstance(rango2, (list, tuple)) and len(rango2) == 2:
            ini2, fin2 = pd.Timestamp(rango2[0]), pd.Timestamp(rango2[1]) + pd.Timedelta(days=1)
            dg = dg[dg["_fecha"].isna() | ((dg["_fecha"] >= ini2) & (dg["_fecha"] < fin2))]

        ew = ewma_resumen(dg)
        if ew.empty:
            st.info("Sin datos suficientes para EWMA."); return

        labs = dict((a, b) for a, b, _ in METRICAS)
        cards = [_tarjeta(f"EWMA {labs[k]}", f"{ew[k].mean():.2f}", color_ewma(ew[k].mean()))
                 for k in EWMA_METRICAS if k in ew.columns]
        st.markdown(_fila_tarjetas(cards), unsafe_allow_html=True)

        st.markdown('<div class="subsec">Ranking por variable (último ratio EWMA de cada jugador)</div>',
                    unsafe_allow_html=True)
        vsel = st.selectbox("Variable", [k for k in EWMA_METRICAS if k in ew.columns],
                            format_func=lambda k: labs[k], key="ew_var")
        rank = ew[[vsel]].dropna().sort_values(vsel, ascending=True).reset_index()
        rank.columns = ["Jugador", "Ratio"]
        fig = px.bar(rank, x="Ratio", y="Jugador", orientation="h", template="plotly_dark",
                     color="Ratio", color_continuous_scale=["#60a5fa", "#4ade80", "#facc15", "#dc2626"],
                     range_color=[0.5, 1.6], height=max(320, 22 * len(rank)))
        fig.add_vline(x=0.8, line_dash="dot", line_color="#4ade80")
        fig.add_vline(x=1.3, line_dash="dot", line_color="#f87171")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False,
                          font=dict(color="#fff"), legend=dict(font=dict(color="#fff")))
        fig.update_xaxes(color="#fff"); fig.update_yaxes(color="#fff")
        st.plotly_chart(fig, use_container_width=True)

        # Evolución del promedio del plantel (agregado, liviano)
        st.markdown('<div class="subsec">Evolución del ratio medio del plantel</div>', unsafe_allow_html=True)
        s = ewma_serie(dg, vsel)
        if not s.empty:
            med = s.groupby("_fecha")["ratio"].mean().reset_index().dropna()
            figm = px.line(med, x="_fecha", y="ratio", template="plotly_dark", height=280,
                           labels={"_fecha": "Fecha", "ratio": "Ratio EWMA"})
            figm.update_traces(line_color="#c8102e", line_width=2)
            figm.add_hrect(y0=0.8, y1=1.3, fillcolor="#4ade80", opacity=0.08, line_width=0)
            figm.add_hline(y=1.3, line_dash="dot", line_color="#f87171")
            figm.add_hline(y=0.8, line_dash="dot", line_color="#4ade80")
            figm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               margin=dict(l=0, r=0, t=10, b=0), font=dict(color="#fff"))
            figm.update_xaxes(color="#fff"); figm.update_yaxes(color="#fff")
            st.plotly_chart(figm, use_container_width=True)

        if pdf_btn:
            kp_ew = [(f"EWMA {labs[k]}", f"{ew[k].mean():.2f}") for k in EWMA_METRICAS if k in ew.columns]
            pdf_btn("Demandas Fisicas - EWMA Grupal", kpis=kp_ew,
                    tablas=[(f"Ranking EWMA {labs[vsel]}", rank)],
                    orientacion="L", key="ew_grupal",
                    notas=f"Ratio EWMA agudo(7d):cronico(28d). Año={t2sel}, Microciclo={m2sel}.")

    # ═════════════════════════════════════════════════════════════════
    #  TAB 3 — EWMA INDIVIDUAL
    # ═════════════════════════════════════════════════════════════════
    with t3:
        jsel3, msel3 = st.columns(2)
        with jsel3:
            jind = st.selectbox("Jugador", sorted(d["_jug"].unique().tolist()), key="ewi_jug")
        with msel3:
            mics3 = ["Todos"] + sorted([x for x in d["_micro"].unique() if x and x != "nan"],
                                       key=lambda z: (len(z), z), reverse=True)
            m3sel = st.selectbox("Microciclo", mics3, key="ewi_micro")
        di = d[d["_jug"] == jind]
        if m3sel != "Todos": di = di[di["_micro"] == m3sel]
        val3 = di["_fecha"].dropna()
        if not val3.empty:
            f3min, f3max = val3.min().date(), val3.max().date()
            rango3 = st.date_input("Rango de fechas", value=(f3min, f3max),
                                   min_value=f3min, max_value=f3max, key="ewi_fecha")
            if isinstance(rango3, (list, tuple)) and len(rango3) == 2:
                ini3, fin3 = pd.Timestamp(rango3[0]), pd.Timestamp(rango3[1]) + pd.Timedelta(days=1)
                di = di[di["_fecha"].isna() | ((di["_fecha"] >= ini3) & (di["_fecha"] < fin3))]
        labs = dict((a, b) for a, b, _ in METRICAS)

        ewi = ewma_resumen(di)
        if not ewi.empty:
            cards = [_tarjeta(f"EWMA {labs[k]}", f"{ewi[k].iloc[0]:.2f}", color_ewma(ewi[k].iloc[0]))
                     for k in EWMA_METRICAS if k in ewi.columns and pd.notna(ewi[k].iloc[0])]
            st.markdown(_fila_tarjetas(cards), unsafe_allow_html=True)

        vi = st.selectbox("Variable", [k for k, _, _ in METRICAS if di[k].notna().any()],
                          format_func=lambda k: labs[k], key="ewi_var")
        s = ewma_serie(di, vi)
        if s.empty:
            st.info("Sin datos."); return

        fig = go.Figure()
        fig.add_trace(go.Bar(x=s["_fecha"], y=s["carga"], name=f"Carga diaria ({labs[vi]})",
                             marker_color="rgba(96,165,250,.35)", yaxis="y2"))
        fig.add_trace(go.Scatter(x=s["_fecha"], y=s["agudo"], name="EWMA agudo (7d)",
                                 line=dict(color="#c8102e", width=2), yaxis="y2"))
        fig.add_trace(go.Scatter(x=s["_fecha"], y=s["cronico"], name="EWMA crónico (28d)",
                                 line=dict(color="#facc15", width=2, dash="dash"), yaxis="y2"))
        fig.add_trace(go.Scatter(x=s["_fecha"], y=s["ratio"], name="Ratio A:C",
                                 line=dict(color="#4ade80", width=2.5)))
        fig.add_hrect(y0=0.8, y1=1.3, fillcolor="#4ade80", opacity=0.07, line_width=0)
        fig.update_layout(
            template="plotly_dark", height=430,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=30, b=0),
            font=dict(color="#fff"),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(color="#fff")),
            yaxis=dict(title="Ratio A:C", color="#fff", side="left", range=[0, 2.2]),
            yaxis2=dict(title=labs[vi], color="#94a3b8", side="right", overlaying="y", showgrid=False),
            xaxis=dict(color="#fff"),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            '<div style="background:rgba(26,90,180,.08);border:1px solid rgba(26,90,180,.25);'
            'border-radius:10px;padding:11px 15px;font-size:11px;color:#94a3b8;margin-top:8px;">'
            '<b style="color:#93c5fd;">Lectura.</b> El EWMA pondera exponencialmente: la carga de ayer '
            'pesa más que la de hace tres semanas (a diferencia del ACWR clásico, donde todo el período '
            'pesa igual). Zona verde 0.8–1.3 = progresión de carga controlada. Por encima de 1.3, la carga '
            'aguda crece más rápido que la base crónica. Referencia: Williams et al. (2017), BJSM.</div>',
            unsafe_allow_html=True)

        if pdf_btn:
            kp_ewi = [(f"EWMA {labs[k]}", f"{ewi[k].iloc[0]:.2f}") for k in EWMA_METRICAS
                      if k in ewi.columns and pd.notna(ewi[k].iloc[0])] if not ewi.empty else []
            pdf_btn(f"Demandas Fisicas - EWMA {jind}", kpis=kp_ewi,
                    tablas=[(f"Evolucion diaria - {labs[vi]}", s)],
                    orientacion="L", key="ew_individual",
                    notas=f"Jugador={jind}, Microciclo={m3sel}, Variable={labs[vi]}.")
