"""Arma la tabla distrito × temporada para modelar DÓNDE habrá emergencias por lluvias.

Una fila = un distrito de Tumbes, Piura, Lambayeque, La Libertad o Áncash (364) en la
temporada de lluvias de un año (enero a mayo), de 1970 a 2025: 364 × 56 = 20 384 filas.

Salida: datos/2_limpios/modelo/panel_distrito_temporada_1970_2025.csv

Variable objetivo (enero-mayo del año):
  - 1970-2002 desde DesInventar (solo fichas registradas a nivel distrito), 2003-2025 desde INDECI.
    La columna fuente_objetivo dice cuál. No se mezclan años: DesInventar llega a 2015, pero desde
    2003 se usa solo INDECI.
  - tuvo_damnificados (0/1) es la variable principal: los conteos de las dos fuentes no son
    comparables (DesInventar registra muchos menos eventos), pero "hubo daño o no" sí.

Columnas según cuándo se conocen (lo que importa para no hacer trampa al validar):
  *_previo   se conoce antes de que empiece la temporada (hasta noviembre del año anterior)
  *_ene_may  pasa durante la temporada: solo sirve como escenario ("¿y si llueve como en 2017?")
  hist_*     historial del distrito en temporadas ANTERIORES (nunca incluye la del año)
  el resto   atributos fijos del distrito (relieve, ríos, población, pobreza)

Necesita las tablas que arman 02_preparar_panel.py y 05_preparar_historicos.py.
Uso:  .venv/bin/python scripts/07_panel_distrito_temporada.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import L_EMERGENCIAS, L_ENSO, L_LLUVIA, L_MODELO, L_TERRITORIO  # noqa: E402

DEPTOS = {"24": "TUMBES", "20": "PIURA", "14": "LAMBAYEQUE", "13": "LA LIBERTAD", "02": "ANCASH"}
ANIOS = range(1970, 2026)
TEMPORADA = [1, 2, 3, 4, 5]          # enero a mayo
ULTIMO_ANIO_DESINVENTAR = 2002       # desde 2003 la variable objetivo sale de INDECI
NORMAL = (1991, 2020)                # periodo de la lluvia normal

ATRIBUTOS = ["superficie_km2", "poblacion_2020_estimada", "pob_densidad_2020", "idh_2019", "pct_pobreza_total",
             "pct_pobreza_extrema", "indice_vulnerabilidad_alimentaria", "altitud_capital_m", "lat_centroide",
             "lon_centroide", "elev_media_m", "elev_min_m", "elev_p10_m", "pct_area_bajo_50m", "pct_area_bajo_200m",
             "pendiente_media_grados", "pct_area_pendiente_menor_2", "dist_centroide_a_rio_mayor_km",
             "cuenca_max_que_cruza_km2"]


def objetivo() -> pd.DataFrame:
    """Conteos de enero-mayo por distrito y año, de DesInventar (1970-2002) e INDECI (2003-2025)."""
    di = pd.read_csv(L_EMERGENCIAS / "desinventar_fichas_costa_norte.csv", dtype={"ubigeo": str}, low_memory=False)
    di = di[di.hidrometeorologico & (di.nivel_geografico == "distrito") & di.mes_num.isin(TEMPORADA)
            & (di.anio <= ULTIMO_ANIO_DESINVENTAR)]
    di = pd.DataFrame({"ubigeo": di.ubigeo, "anio": di.anio, "damnificados": di.damnificados.fillna(0),
                       "fallecidos": di.fallecidos.fillna(0), "viviendas_destruidas": di.viviendas_destruidas.fillna(0),
                       # mismo criterio que desinventar_panel_departamento_mes.csv
                       "con_damnificados": (di.damnificados > 0) | (di.viviendas_destruidas > 0)})
    ind = pd.read_csv(L_EMERGENCIAS / "indeci_emergencias_2003_2025.csv", dtype={"ubigeo_mapa": str}, low_memory=False,
                      usecols=["ubigeo_mapa", "anio", "mes_num", "es_peligro_lluvias", "damnificados", "fallecidos",
                               "viviendas_destruidas"])
    ind = ind[ind.es_peligro_lluvias & ind.mes_num.isin(TEMPORADA) & ind.ubigeo_mapa.str[:2].isin(DEPTOS)]
    ind = pd.DataFrame({"ubigeo": ind.ubigeo_mapa, "anio": ind.anio, "damnificados": ind.damnificados,
                        "fallecidos": ind.fallecidos, "viviendas_destruidas": ind.viviendas_destruidas,
                        "con_damnificados": ind.damnificados > 0})  # mismo criterio que el panel del modelo
    todo = pd.concat([di, ind])
    return todo.groupby(["ubigeo", "anio"]).agg(
        emergencias_lluvias=("damnificados", "size"), emerg_con_damnificados=("con_damnificados", "sum"),
        damnificados=("damnificados", "sum"), fallecidos=("fallecidos", "sum"),
        viviendas_destruidas=("viviendas_destruidas", "sum")).reset_index()


def enso() -> pd.DataFrame:
    """Un valor por temporada (igual para todos los distritos)."""
    e = pd.read_csv(L_ENSO / "enso_mensual_1854_hoy.csv")
    e = e.set_index(["anio", "mes_num"])
    filas = []
    for a in ANIOS:
        prev = e.loc[a - 1]
        dur = e.loc[a].loc[TEMPORADA]
        filas.append({
            "anio": a,
            "icen_nov_previo": prev.loc[11, "icen"],
            "icen_max_jun_nov_previo": prev.loc[6:11, "icen"].max(),
            "icen_cambio_ago_nov_previo": round(prev.loc[11, "icen"] - prev.loc[8, "icen"], 2),
            "nino34_anom_nov_previo": prev.loc[11, "nino34_anom"],
            "icen_max_ene_may": dur["icen"].max(),
            "icen_medio_ene_may": round(dur["icen"].mean(), 2),
        })
    return pd.DataFrame(filas)


def lluvia() -> pd.DataFrame:
    m = pd.read_csv(L_LLUVIA / "lluvia_mensual_distrito.csv", dtype={"ubigeo": str})
    m["anio"], m["mes_num"] = m.fecha.str[:4].astype(int), m.fecha.str[5:7].astype(int)
    t = m[m.mes_num.isin(TEMPORADA)]
    # min_count=5: si falta algún mes de la temporada, el total queda vacío
    g = t.groupby(["ubigeo", "anio"])
    ll = pd.DataFrame({
        "lluvia_ene_may_pisco_reciente_mm": g.lluvia_pisco_reciente_mm.sum(min_count=5),
        "lluvia_ene_may_chirps_mm": g.lluvia_chirps_mm.sum(min_count=5),
        "lluvia_ene_may_pisco_estable_mm": g.lluvia_pisco_estable_mm.sum(min_count=5),
        "lluvia_mes_max_ene_may_pisco_reciente_mm": g.lluvia_pisco_reciente_mm.max(),
    }).reset_index()
    # Lluvia relativa a lo normal del distrito, como en el modelo B: log((lluvia + 10) / (normal + 10))
    for f in ["pisco_reciente", "chirps"]:
        col = f"lluvia_ene_may_{f}_mm"
        normal = ll[ll.anio.between(*NORMAL)].groupby("ubigeo")[col].mean()
        ll[f"lluvia_ene_may_{f}_relativa"] = np.log((ll[col] + 10) / (ll.ubigeo.map(normal) + 10)).round(3)
    # Lluvia de noviembre-diciembre del año anterior (se conoce antes de la temporada)
    nd = m[m.mes_num.isin([11, 12])].groupby(["ubigeo", "anio"]).lluvia_pisco_reciente_mm.sum(min_count=2)
    nd = nd.rename("lluvia_nov_dic_previo_pisco_reciente_mm").reset_index()
    nd["anio"] += 1
    ll = ll.merge(nd, on=["ubigeo", "anio"], how="outer")
    # Intensidad diaria (PISCO diario, 1981-2016)
    d = pd.read_csv(L_LLUVIA / "lluvia_intensidad_pisco_distrito_mes.csv", dtype={"ubigeo": str})
    d["anio"], d["mes_num"] = d.fecha.str[:4].astype(int), d.fecha.str[5:7].astype(int)
    gd = d[d.mes_num.isin(TEMPORADA)].groupby(["ubigeo", "anio"])
    inten = pd.DataFrame({
        "lluvia_max_diaria_ene_may_pisco_mm": gd.lluvia_max_diaria_mm.max(),
        "dias_mayor_20mm_ene_may_pisco": gd.dias_mayor_20mm.sum(),
        "max_acum_3dias_ene_may_pisco_mm": gd.max_acum_3dias_mm.max(),
    }).reset_index()
    return ll.merge(inten, on=["ubigeo", "anio"], how="left")


def armar() -> pd.DataFrame:
    attr = pd.read_csv(L_TERRITORIO / "distritos_costa_norte_atributos.csv", dtype={"ubigeo": str})
    base = attr[["ubigeo", "distrito", "provincia", "departamento"]].merge(pd.DataFrame({"anio": ANIOS}), how="cross")
    base.insert(5, "fuente_objetivo", np.where(base.anio <= ULTIMO_ANIO_DESINVENTAR, "DesInventar", "INDECI"))

    obj = objetivo()
    sin_mapa = set(obj.ubigeo) - set(attr.ubigeo)
    assert not sin_mapa, f"ubigeos sin distrito en el mapa: {sorted(sin_mapa)}"
    df = base.merge(obj, on=["ubigeo", "anio"], how="left")
    conteos = ["emergencias_lluvias", "emerg_con_damnificados", "damnificados", "fallecidos", "viviendas_destruidas"]
    df[conteos] = df[conteos].fillna(0).astype(int)  # sin registros = 0
    df["tuvo_damnificados"] = (df.emerg_con_damnificados > 0).astype(int)

    # Historial: solo temporadas anteriores a la del año (nunca la misma)
    df = df.sort_values(["ubigeo", "anio"]).reset_index(drop=True)
    g = df.groupby("ubigeo")["tuvo_damnificados"]
    df["hist_tuvo_damnificados_temporada_anterior"] = g.shift(1)
    previas = g.cumsum() - df["tuvo_damnificados"]
    n_previas = df.groupby("ubigeo").cumcount()
    df["hist_temporadas_con_damnificados"] = previas.where(n_previas > 0)
    df["hist_pct_temporadas_con_damnificados"] = (100 * previas / n_previas.replace(0, np.nan)).round(1)

    df = df.merge(enso(), on="anio", how="left").merge(lluvia(), on=["ubigeo", "anio"], how="left")
    df = df.merge(attr[["ubigeo"] + ATRIBUTOS], on="ubigeo", how="left")
    return df


if __name__ == "__main__":
    df = armar()
    L_MODELO.mkdir(parents=True, exist_ok=True)
    df.to_csv(L_MODELO / "panel_distrito_temporada_1970_2025.csv", index=False)
    print(f"-> modelo/panel_distrito_temporada_1970_2025.csv: {len(df):,} filas × {df.shape[1]} columnas")
    r = df.groupby("anio").agg(pct_distritos_con_damnificados=("tuvo_damnificados", "mean"),
                               icen_max_ene_may=("icen_max_ene_may", "first"))
    r["pct_distritos_con_damnificados"] = (100 * r.pct_distritos_con_damnificados).round(1)
    print("Temporadas con más distritos con damnificados:")
    print(r.sort_values("pct_distritos_con_damnificados", ascending=False).head(10).to_string())
    print("Por fuente:", df.groupby("fuente_objetivo").tuvo_damnificados.mean().mul(100).round(1).to_dict(), "% de filas con 1")
