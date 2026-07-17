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
    d["_fecha"] = pd.to_datetime(df[m["fecha"]], dayfirst=True, errors="coerce")
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
    d = d.dropna(subset=["_fecha"])
    return d, m


def es_partido(serie_ses):
    """SES que representa partido oficial."""
    s = serie_ses.astype(str).str.upper()
    return s.str.contains("PARTIDO|MATCH|MD|OFICIAL", regex=True, na=False)


# ─────────────────────────────────────────────────────────────────────────
#  REFERENCIA INDIVIDUAL DE PARTIDO  (últimos N partidos con > MIN_REF min)
# ─────────────────────────────────────────────────────────────────────────
def referencia_partido(d, n_partidos=5, min_ref=70):
    """
    Promedio por jugador de sus últimos `n_partidos` partidos oficiales
    con más de `min_ref` minutos. Devuelve DataFrame indexado por jugador.
    """
    p = d[es_partido(d["_ses"]) & (d["min"] > min_ref)].copy()
    if p.empty:
        return pd.DataFrame()
    p = p.sort_values("_fecha")
    ult = p.groupby("_jug").tail(n_partidos)
    cols = [k for k, _, _ in METRICAS]
    ref = ult.groupby("_jug")[cols].mean()
    ref["_n_ref"] = ult.groupby("_jug").size()
    return ref


def matriz_microciclo(d, ref, n_partidos=5, min_ref=70):
    """
    Carga acumulada del período filtrado por jugador + % vs referencia individual.
    """
    if d.empty:
        return pd.DataFrame()
    cols = [k for k, _, _ in METRICAS]
    agg = {}
    for k in cols:
        agg[k] = "sum" if k in ACUMULABLES else ("max" if k == "vmax" else "mean")
    g = d.groupby("_jug").agg(agg)
    g["_n_ses"] = d.groupby("_jug").size()
    g["_pos"] = d.groupby("_jug")["_pos"].agg(lambda s: s.mode().iloc[0] if len(s.mode()) else "")

    for k in COMPARABLES:
        if not ref.empty and k in ref.columns:
            base = ref[k].reindex(g.index)
            g[f"pct_{k}"] = (g[k] / base.replace(0, np.nan) * 100).round(0)
        else:
            g[f"pct_{k}"] = np.nan
    g["_n_ref"] = ref["_n_ref"].reindex(g.index) if not ref.empty else np.nan
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
            poss = ["Todas"] + sorted([x for x in dff["_pos"].unique() if x and x != "nan"])
            psel = st.multiselect("Posición", poss[1:], default=[], key="dem_pos")
            if psel: dff = dff[dff["_pos"].isin(psel)]
        with f4:
            sess = ["Todas"] + sorted([x for x in dff["_ses"].unique() if x and x != "nan"])
            ssel = st.multiselect("Sesión", sess[1:], default=[], key="dem_ses")
            if ssel: dff = dff[dff["_ses"].isin(ssel)]

        g1, g2, g3 = st.columns(3)
        with g1:
            n_part = st.slider("Partidos de referencia", 3, 10, 5, key="dem_npart",
                               help="Cuántos partidos oficiales recientes definen la demanda de competencia de cada jugador.")
        with g2:
            min_ref = st.slider("Minutos mínimos por partido", 45, 90, 70, step=5, key="dem_minref",
                                help="Solo cuentan como referencia los partidos con más de estos minutos.")
        with g3:
            jugs = sorted(dff["_jug"].unique().tolist())
            jsel = st.multiselect("Jugador", jugs, default=[], key="dem_jug")
            if jsel: dff = dff[dff["_jug"].isin(jsel)]
        st.markdown('</div>', unsafe_allow_html=True)

        if dff.empty:
            st.info("Sin sesiones para los filtros seleccionados."); return

        # Referencia SIEMPRE sobre el histórico completo (no sobre el micro filtrado).
        ref = referencia_partido(d, n_part, min_ref)
        mat = matriz_microciclo(dff, ref, n_part, min_ref)

        # ── Tarjetas promedio del microciclo ─────────────────────────
        proms = []
        for k, lab, _ in METRICAS:
            if k in dff.columns and dff[k].notna().any():
                v = dff.groupby("_jug")[k].sum().mean() if k in ACUMULABLES else dff[k].mean()
                proms.append(_tarjeta(f"PROM {lab}", f"{v:,.0f}".replace(",", ".") if abs(v) >= 100 else f"{v:.1f}"))
        st.markdown(_fila_tarjetas(proms), unsafe_allow_html=True)

        # ── Tarjetas EWMA ────────────────────────────────────────────
        ew = ewma_resumen(d if not jsel else d[d["_jug"].isin(jsel)])
        if not ew.empty:
            cards = []
            for k in EWMA_METRICAS:
                if k in ew.columns:
                    v = ew[k].mean()
                    lab = dict((a, b) for a, b, _ in METRICAS)[k]
                    cards.append(_tarjeta(f"EWMA {lab}", f"{v:.2f}" if pd.notna(v) else "—", color_ewma(v)))
            st.markdown('<div class="subsec">Ratio agudo:crónico exponencial (EWMA 7:28)</div>', unsafe_allow_html=True)
            st.markdown(_fila_tarjetas(cards), unsafe_allow_html=True)

        # ── Matriz ───────────────────────────────────────────────────
        st.markdown('<div class="subsec">Microciclo vs % de máximo de partido individual</div>', unsafe_allow_html=True)
        if mat.empty:
            st.info("Sin datos."); return
        if ref.empty:
            st.warning(f"Ningún jugador tiene partidos oficiales con más de {min_ref}' "
                       f"(columna SES debe contener 'PARTIDO'). Los % no se pueden calcular.")

        mat = mat.sort_values("_pos")
        n_show = st.slider("Filas a mostrar", 5, max(10, len(mat)), min(10, len(mat)), key="dem_nrows")
        vista = mat.head(n_show)

        labs = dict((a, b) for a, b, _ in METRICAS)
        heads = ["JUGADOR", "POS", "SES", "MIN"]
        for k in COMPARABLES:
            heads += [labs[k], "% IND"]
        heads += ["V-MAX"]

        th = "".join(f'<th style="padding:7px 6px;font-size:8.5px;letter-spacing:.5px;color:#fff;'
                     f'background:rgba(26,90,180,.35);text-transform:uppercase;white-space:nowrap;'
                     f'position:sticky;top:0;">{h}</th>' for h in heads)
        trs = ""
        for _, r in vista.iterrows():
            tds = (f'<td style="padding:6px 8px;color:#fff;white-space:nowrap;font-weight:600;">{r["_jug"]}</td>'
                   f'<td style="text-align:center;color:#94a3b8;font-size:10px;">{r["_pos"]}</td>'
                   f'<td style="text-align:center;color:#cbd5e1;">{int(r["_n_ses"])}</td>'
                   f'<td style="text-align:center;color:#cbd5e1;">{0 if pd.isna(r["min"]) else int(r["min"])}</td>')
            for k in COMPARABLES:
                val = r.get(k); pct = r.get(f"pct_{k}")
                vtxt = "—" if pd.isna(val) else f"{val:,.0f}".replace(",", ".")
                bg, fg = color_pct(pct)
                ptxt = "—" if pd.isna(pct) else f"{pct:.0f}%"
                tds += (f'<td style="text-align:center;color:#cbd5e1;">{vtxt}</td>'
                        f'<td style="text-align:center;background:{bg};color:{fg};font-weight:800;'
                        f'font-size:11px;">{ptxt}</td>')
            vm = r.get("vmax")
            tds += f'<td style="text-align:center;color:#fff;font-weight:700;">{"—" if pd.isna(vm) else f"{vm:.1f}"}</td>'
            trs += f'<tr style="border-bottom:1px solid rgba(255,255,255,.05);">{tds}</tr>'

        st.markdown(
            f'<div style="background:#071428;border:1px solid rgba(26,90,180,.3);border-radius:12px;'
            f'overflow:auto;max-height:460px;"><table style="width:max-content;min-width:100%;'
            f'border-collapse:collapse;font-size:11px;"><thead><tr>{th}</tr></thead>'
            f'<tbody>{trs}</tbody></table></div>', unsafe_allow_html=True)
        st.caption(f"Mostrando {len(vista)} de {len(mat)} jugadores · "
                   f"% IND = carga del microciclo ÷ promedio de sus últimos {n_part} partidos con >{min_ref}' × 100")

        st.download_button("⬇️ CSV de la matriz completa",
                           mat.to_csv(index=False).encode("utf-8"),
                           "matriz_microciclo.csv", "text/csv", key="dem_csv")

        if pdf_btn:
            exp = vista[["_jug", "_pos", "_n_ses", "min"] + COMPARABLES].copy()
            exp.columns = ["Jugador", "Pos", "Ses", "Min"] + [labs[k] for k in COMPARABLES]
            pdf_btn("Demandas Fisicas - Microciclo",
                    subtitulo=f"Microciclo {msel} - Temporada {tsel}",
                    kpis=[(f"PROM {labs[k]}", f"{dff[k].sum()/max(1,dff['_jug'].nunique()):,.0f}")
                          for k in ["min", "td", "m19"] if k in dff.columns],
                    tablas=[("Matriz microciclo vs partido individual", exp)],
                    notas=f"% IND = carga del microciclo / promedio de los ultimos {n_part} partidos "
                          f"oficiales con mas de {min_ref} minutos, por jugador.",
                    key="dem1")

    # ═════════════════════════════════════════════════════════════════
    #  TAB 2 — EWMA GRUPAL POR VARIABLE
    # ═════════════════════════════════════════════════════════════════
    with t2:
        c1, c2 = st.columns([1, 2])
        with c1:
            temps2 = ["Todas"] + sorted([x for x in d["_temp"].unique() if x and x != "nan"], reverse=True)
            t2sel = st.selectbox("Año", temps2, index=1 if len(temps2) > 1 else 0, key="ew_temp")
        with c2:
            pos2 = sorted([x for x in d["_pos"].unique() if x and x != "nan"])
            p2sel = st.multiselect("Posición", pos2, default=[], key="ew_pos")
        dg = d.copy()
        if t2sel != "Todas": dg = dg[dg["_temp"] == t2sel]
        if p2sel: dg = dg[dg["_pos"].isin(p2sel)]

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

    # ═════════════════════════════════════════════════════════════════
    #  TAB 3 — EWMA INDIVIDUAL
    # ═════════════════════════════════════════════════════════════════
    with t3:
        jind = st.selectbox("Jugador", sorted(d["_jug"].unique().tolist()), key="ewi_jug")
        di = d[d["_jug"] == jind]
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
