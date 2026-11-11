"""Convierte lo bajado por 04_descargar_historicos.py (datos/1_crudos/) en tablas limpias
(datos/2_limpios/<tema>/). El diccionario de cada tabla está en datos/CATALOGO_DATOS.md.

  enso/        enso_mensual_1854_hoy.csv, enso_eventos_nino_costero.csv
  lluvia/      lluvia_mensual_departamento.csv, lluvia_mensual_distrito.csv,
               lluvia_intensidad_pisco_distrito_mes.csv, lluvia_intensidad_chirps_eventos_distrito_mes.csv,
               lluvia_diaria_chirps_eventos_distrito.csv, estaciones_ghcn_lluvia_diaria.csv,
               estaciones_ghcn_resumen.csv
  caudales/    caudales_glofas_diario.csv, caudales_glofas_mensual.csv, caudales_glofas_puntos.csv,
               caudales_glofas_pronostico.csv, caudales_pico_rio_piura_observados.csv
  emergencias/ desinventar_fichas_costa_norte.csv, desinventar_panel_departamento_mes.csv,
               desinventar_distrito_anio.csv, indeci_distrito_anio_lluvias.csv,
               impactos_eventos_nino_compilados.csv
  territorio/  distritos_costa_norte_atributos.csv, distritos_costa_norte.geojson

Reglas de limpieza (además de las de cada sección):
  - Lluvia: en el mar las grillas no tienen datos. Si un distrito costero chico no tiene ninguna
    celda con datos adentro, se usa la celda con datos más cercana.
  - DesInventar: la clave es id_desinventar (uu_id); serial se repite entre departamentos.
    Latitud/longitud 0 (99 % de las fichas) y mes o día 0 pasan a vacío. Las fichas sin distrito
    se quedan en las tablas por departamento, pero no en la tabla por distrito (nivel_geografico).
  - GloFAS: se quitan los últimos días del pronóstico, que vienen vacíos.
  - GHCN: se usan solo datos sin bandera de calidad. Los días con más de 200 mm se marcan para
    revisar (no se borran) y se marca si la estación está dentro de los 5 departamentos.

Uso:  .venv/bin/python scripts/05_preparar_historicos.py [seccion ...]
Secciones: enso lluvia pisco_diario chirps_diario caudales estaciones desinventar territorio compilados
"territorio" usa la base limpia de INDECI, así que corre antes 02_preparar_panel.py.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
import xarray as xr
from shapely.geometry import mapping, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import (CHIRPS, CPC, DEM, DESINVENTAR, ERSST, GHCN, GLOFAS, GPCC, ICEN, INDICADORES,  # noqa: E402
                   L_CAUDALES, L_EMERGENCIAS, L_ENSO, L_LLUVIA, L_TERRITORIO, LIMITES, MANUAL, MEI,
                   PISCO, RIOS)

DEPTOS = {"24": "TUMBES", "20": "PIURA", "14": "LAMBAYEQUE", "13": "LA LIBERTAD", "02": "ANCASH"}

# Umbrales clásicos de magnitud del ICEN (ENFEN 2012). La Nota Técnica ENFEN 2024
# podría haberlos cambiado: no se pudo verificar. Edítalos aquí si tienes la nota.
UMBRALES_ICEN = [("debil", 0.4), ("moderado", 1.0), ("fuerte", 1.7), ("extraordinario", 3.0)]


def guardar(df: pd.DataFrame, carpeta: Path, nombre: str) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    df.to_csv(carpeta / nombre, index=False)
    print(f"  -> {carpeta.name}/{nombre}: {len(df):,} filas")


# ----------------------------------------------------------------------------- distritos
_DIST = None
# Erratas del GeoJSON del INEI (el crudo no se toca: se corrigen aquí)
PROVINCIA_CORREGIDA = {"PUIRA": "PIURA"}  # distrito 200110 La Unión


def distritos() -> pd.DataFrame:
    """Distritos de los 5 departamentos con su geometría (shapely)."""
    global _DIST
    if _DIST is None:
        gj = json.loads((LIMITES / "peru_distritos.geojson").read_text())
        filas = []
        for f in gj["features"]:
            p = f["properties"]
            if p["IDDPTO"] in DEPTOS and f.get("geometry"):
                filas.append({
                    "ubigeo": p["IDDIST"], "distrito": p["NOMBDIST"],
                    "provincia": PROVINCIA_CORREGIDA.get(p["NOMBPROV"], p["NOMBPROV"]),
                    "departamento": DEPTOS[p["IDDPTO"]], "geom": shape(f["geometry"]),
                    "geometria_fuente": "peru-geojson",
                })
        # Dos distritos vienen sin geometría en el GeoJSON (200602 Bellavista-Sullana y
        # 020602 Acopampa): se toman del mapa distrital que trae DesInventar.
        shp = DESINVENTAR / "DI_export_per" / "Distritos_region"
        if shp.with_suffix(".shp").exists():
            import shapefile  # pyshp

            ya = {f["ubigeo"] for f in filas}
            prov = {f["ubigeo"][:4]: f["provincia"] for f in filas}
            for sr in shapefile.Reader(str(shp), encoding="latin1").iterShapeRecords():
                cod = sr.record["CODIGO"]
                if cod[:2] in DEPTOS and cod not in ya:
                    filas.append({"ubigeo": cod, "distrito": sr.record["NOMDIS"].strip(), "provincia": prov.get(cod[:4], ""),
                                  "departamento": DEPTOS[cod[:2]], "geom": shape(sr.shape.__geo_interface__).buffer(0),
                                  "geometria_fuente": "DesInventar"})
                    print(f"  distrito {cod} {sr.record['NOMDIS'].strip()}: geometría tomada de DesInventar")
        _DIST = pd.DataFrame(filas).sort_values("ubigeo").reset_index(drop=True)
    return _DIST


def celdas_por_distrito(lon: np.ndarray, lat: np.ndarray, valida: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """Para una grilla regular, índices planos (fila*nx+col) de las celdas cuyo centro
    cae en cada distrito. `valida` (ny, nx) marca las celdas que tienen datos; en el mar
    las grillas de lluvia están vacías. Si ninguna celda válida cae dentro (distritos chicos
    o pegados al mar), se usa la celda válida más cercana a un punto interior del distrito."""
    LON, LAT = np.meshgrid(lon, lat)
    lonf, latf = LON.ravel(), LAT.ravel()
    okf = np.ones(lonf.size, dtype=bool) if valida is None else valida.ravel()
    res = {}
    for _, r in distritos().iterrows():
        g = r["geom"]
        x0, y0, x1, y1 = g.bounds
        cand = np.where((lonf >= x0) & (lonf <= x1) & (latf >= y0) & (latf <= y1) & okf)[0]
        dentro = cand[shapely.contains_xy(g, lonf[cand], latf[cand])] if len(cand) else cand
        if len(dentro) == 0:
            pt = g.representative_point()
            dist = (lonf - pt.x) ** 2 + (latf - pt.y) ** 2
            dist[~okf] = np.inf
            dentro = np.array([np.argmin(dist)])
        res[r["ubigeo"]] = dentro
    return res


def celdas_con_datos(arr: np.ndarray) -> np.ndarray:
    """Celdas con datos en al menos la mitad de los tiempos. En el PISCO reciente hay celdas
    del mar que solo traen dato en el último mes, y no deben contar como tierra."""
    return np.isfinite(arr).mean(axis=0) >= 0.5


def meses_iridl(t: np.ndarray, unidades: str) -> list[pd.Period]:
    assert unidades.startswith("months since 1960-01-01"), f"unidad de tiempo inesperada: {unidades}"
    return [pd.Period("1960-01", freq="M") + int(np.floor(v)) for v in t]


def dias_iridl(t: np.ndarray, unidades: str) -> pd.DatetimeIndex:
    """La IRI Data Library usa "days since 1960-01-01" (PISCO) o días julianos (CHIRPS diario)."""
    if unidades == "julian_day":  # el día juliano 2440587.5 es el 1-ene-1970 a las 00:00
        return pd.Timestamp("1970-01-01") + pd.to_timedelta(np.floor(t - 2440587.5).astype(int), unit="D")
    assert unidades.startswith("days since 1960-01-01"), f"unidad de tiempo inesperada: {unidades}"
    return pd.Timestamp("1960-01-01") + pd.to_timedelta(np.floor(t).astype(int), unit="D")


def abrir_grilla(p: Path):
    ds = xr.open_dataset(p, decode_times=False)
    var = list(ds.data_vars)[0]
    da = ds[var]
    for dim in list(da.dims):
        if dim not in ("T", "Y", "X"):
            da = da.isel({dim: 0})
    da = da.transpose("T", "Y", "X")
    return (da["X"].values, da["Y"].values, da["T"].values, da.values.astype("float32"), da.attrs.get("units"),
            da["T"].attrs.get("units", ""))


def promediar(arr: np.ndarray, mapa: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    plano = arr.reshape(arr.shape[0], -1)
    with np.errstate(invalid="ignore"):
        return {u: np.nanmean(plano[:, idx], axis=1) for u, idx in mapa.items()}


# ----------------------------------------------------------------------------- ENSO
def enso() -> None:
    print("ENSO")
    lon, lat, t, sst, _, ut = abrir_grilla(ERSST / "ersst5_pacifico_tropical_1854_hoy.nc")
    meses = meses_iridl(t, ut)
    LON, LAT = np.meshgrid(lon, lat)
    w = np.cos(np.deg2rad(LAT))

    def caja(x0, x1, y0, y1):
        m = (LON >= x0) & (LON <= x1) & (LAT >= y0) & (LAT <= y1)
        ww = np.where(m, w, 0.0)
        return np.nansum(sst * ww, axis=(1, 2)) / np.nansum(np.where(np.isnan(sst), 0, ww), axis=(1, 2))

    df = pd.DataFrame({"mes": meses, "nino12_sst": caja(270, 280, -10, 0), "nino34_sst": caja(190, 240, -5, 5)})
    df["anio"], df["mes_num"] = df["mes"].dt.year, df["mes"].dt.month

    def anomalia(col, a0, a1):
        clim = df[(df.anio >= a0) & (df.anio <= a1)].groupby("mes_num")[col].mean()
        return df[col] - df["mes_num"].map(clim)

    oficial = pd.read_csv(ICEN / "ICEN.txt", comment="%", sep=r"\s+", names=["anio", "mes_num", "icen_oficial"])
    df = df.merge(oficial, on=["anio", "mes_num"], how="left")
    # Probar dos climatologías y quedarse con la que mejor reproduce el ICEN oficial
    mejor = None
    for a0, a1 in [(1981, 2010), (1991, 2020)]:
        an = anomalia("nino12_sst", a0, a1)
        icen = an.rolling(3, center=True).mean()
        ok = df["icen_oficial"].notna() & icen.notna()
        rmse = float(np.sqrt(((icen[ok] - df.loc[ok, "icen_oficial"]) ** 2).mean()))
        r = float(np.corrcoef(icen[ok], df.loc[ok, "icen_oficial"])[0, 1])
        print(f"  ICEN reconstruido con climatología {a0}-{a1}: r={r:.3f}, RMSE={rmse:.3f} °C (n={ok.sum()})")
        if mejor is None or rmse < mejor[0]:
            mejor = (rmse, a0, a1, an, icen, r)
    rmse, a0, a1, an, icen, r = mejor
    df["nino12_anom"] = an.round(3)
    df["icen_reconstruido"] = icen.round(3)
    df["nino34_anom"] = anomalia("nino34_sst", 1991, 2020).round(3)
    df["icen"] = df["icen_oficial"].fillna(df["icen_reconstruido"])
    df["icen_fuente"] = np.where(df["icen_oficial"].notna(), "oficial_ENFEN", np.where(df["icen"].notna(), "reconstruido_ERSSTv5", ""))
    print(f"  se usa {a0}-{a1} (r={r:.3f}, RMSE={rmse:.3f}); antes de 1950 el ICEN es el reconstruido")

    # Índices de NOAA
    oni = pd.read_csv(CPC / "cpc_oni.txt", sep=r"\s+")
    centro = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}
    oni = oni.assign(mes_num=oni["SEAS"].map(centro), anio=oni["YR"]).rename(columns={"ANOM": "oni"})[["anio", "mes_num", "oni"]]
    roni = pd.read_csv(CPC / "cpc_roni.txt", sep=r"\s+")
    roni = roni.assign(mes_num=roni["SEAS"].map(centro), anio=roni["YR"]).rename(columns={"ANOM": "roni"})[["anio", "mes_num", "roni"]]
    cpc = pd.read_csv(CPC / "cpc_ersst5_nino_mensual_1950_hoy.txt", sep=r"\s+", header=0,
                      names=["anio", "mes_num", "n12", "cpc_nino12_anom", "n3", "cpc_nino3_anom", "n4", "cpc_nino4_anom", "n34", "cpc_nino34_anom"])
    cpc = cpc[["anio", "mes_num", "cpc_nino12_anom", "cpc_nino3_anom", "cpc_nino4_anom", "cpc_nino34_anom"]]
    # SOI estandarizado (segunda tabla del archivo)
    lineas = (CPC / "cpc_soi.txt").read_text().splitlines()
    ini = next(i for i, l in enumerate(lineas) if "STANDARDIZED" in l)
    filas = []
    for l in lineas[ini + 1:]:
        p = l.split()
        if len(p) == 13 and p[0].isdigit():
            for m, v in enumerate(p[1:], 1):
                filas.append((int(p[0]), m, float(v) if v not in ("-999.9", "-999.0") else np.nan))
    soi = pd.DataFrame(filas, columns=["anio", "mes_num", "soi"])
    # MEI v2 (bimestral; se asigna al segundo mes del bimestre: DJ->ene)
    filas = []
    for l in (MEI / "psl_mei_v2.txt").read_text().splitlines()[1:]:
        p = l.split()
        if len(p) == 13 and p[0].isdigit():
            for m, v in enumerate(p[1:], 1):
                filas.append((int(p[0]), m, np.nan if float(v) <= -999 else float(v)))
    mei = pd.DataFrame(filas, columns=["anio", "mes_num", "mei_v2"])
    for x in (oni, roni, cpc, soi, mei):
        df = df.merge(x, on=["anio", "mes_num"], how="left")
    df["fecha"] = df["mes"].astype(str)
    cols = ["fecha", "anio", "mes_num", "icen", "icen_fuente", "icen_oficial", "icen_reconstruido", "nino12_anom",
            "nino34_anom", "nino12_sst", "nino34_sst", "cpc_nino12_anom", "cpc_nino3_anom", "cpc_nino4_anom",
            "cpc_nino34_anom", "oni", "roni", "soi", "mei_v2"]
    df = df[cols].round({"nino12_sst": 2, "nino34_sst": 2})
    guardar(df, L_ENSO, "enso_mensual_1854_hoy.csv")

    # Eventos El Niño costero: ICEN >= 0.4 al menos 3 meses seguidos
    s = df[["fecha", "icen", "icen_fuente"]].dropna(subset=["icen"]).reset_index(drop=True)
    calido = (s["icen"] >= UMBRALES_ICEN[0][1]).to_numpy()
    eventos, i = [], 0
    while i < len(s):
        if calido[i]:
            j = i
            while j + 1 < len(s) and calido[j + 1]:
                j += 1
            if j - i + 1 >= 3:
                tramo = s.iloc[i:j + 1]
                pico = tramo["icen"].max()
                mag = [n for n, u in UMBRALES_ICEN if pico >= u][-1]
                eventos.append({
                    "inicio": tramo["fecha"].iloc[0], "fin": tramo["fecha"].iloc[-1], "meses": j - i + 1,
                    "icen_max": round(pico, 2), "mes_pico": tramo.loc[tramo["icen"].idxmax(), "fecha"],
                    "magnitud": mag, "fuente_icen": "/".join(sorted(set(tramo["icen_fuente"]))),
                    "en_curso": j == len(s) - 1,
                })
            i = j + 1
        else:
            i += 1
    ev = pd.DataFrame(eventos)
    guardar(ev, L_ENSO, "enso_eventos_nino_costero.csv")
    print(ev[ev.magnitud.isin(["fuerte", "extraordinario"])].to_string(index=False))


# ----------------------------------------------------------------------------- lluvia mensual
def lluvia() -> None:
    print("Lluvia mensual")
    d = distritos()
    fuentes = {
        "chirps": CHIRPS / "chirps_mensual_1981_hoy_tumbes_ancash.nc",
        "pisco_estable": PISCO / "pisco_v2p1_estable_mensual_1981_2016.nc",
        "pisco_reciente": PISCO / "pisco_v2p1_inestable_mensual_reciente.nc",
        "gpcc": GPCC / "gpcc_v2018_0p25_mensual_1891_2016.nc",
    }
    largo_dist, largo_dep = [], []
    for nombre, p in fuentes.items():
        if not p.exists():
            print(f"  falta {p.name}")
            continue
        lon, lat, t, arr, unid, ut = abrir_grilla(p)
        meses = [str(m) for m in meses_iridl(t, ut)]
        if unid and "day" in unid:
            dias = np.array([pd.Period(m).days_in_month for m in meses], dtype="float32")
            arr = arr * dias[:, None, None]
        arr[arr < 0] = np.nan
        mapa = celdas_por_distrito(lon, lat, valida=celdas_con_datos(arr))
        print(f"  {nombre}: {len(meses)} meses ({meses[0]} a {meses[-1]}), unidades {unid}")
        if nombre != "gpcc":  # GPCC (0.25°) es muy grueso para distritos
            por = promediar(arr, mapa)
            for u, v in por.items():
                largo_dist.append(pd.DataFrame({"ubigeo": u, "fecha": meses, "fuente": nombre, "lluvia_mm": np.round(v, 1)}))
        # Departamento: todas las celdas de sus distritos
        for dep in DEPTOS.values():
            idx = np.unique(np.concatenate([mapa[u] for u in d.loc[d.departamento == dep, "ubigeo"]]))
            plano = arr.reshape(arr.shape[0], -1)[:, idx]
            with np.errstate(invalid="ignore"):
                v = np.nanmean(plano, axis=1)
            largo_dep.append(pd.DataFrame({"departamento": dep, "fecha": meses, "fuente": nombre, "lluvia_mm": np.round(v, 1)}))
    dep = pd.concat(largo_dep).pivot_table(index=["departamento", "fecha"], columns="fuente", values="lluvia_mm").reset_index()
    dep.columns.name = None
    dep = dep.rename(columns={c: f"lluvia_{c}_mm" for c in fuentes})
    guardar(dep, L_LLUVIA, "lluvia_mensual_departamento.csv")
    dist = pd.concat(largo_dist).pivot_table(index=["ubigeo", "fecha"], columns="fuente", values="lluvia_mm").reset_index()
    dist.columns.name = None
    dist = dist.rename(columns={c: f"lluvia_{c}_mm" for c in fuentes})
    dist = d[["ubigeo", "distrito", "provincia", "departamento"]].merge(dist, on="ubigeo")
    guardar(dist, L_LLUVIA, "lluvia_mensual_distrito.csv")


def _intensidad_diaria(archivos: list[Path], etiqueta: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    mapa, filas_mes, filas_dia = None, [], []
    for p in archivos:
        lon, lat, t, arr, _, ut = abrir_grilla(p)
        arr[arr < 0] = np.nan
        if mapa is None:
            mapa = celdas_por_distrito(lon, lat, valida=celdas_con_datos(arr))
        dias = dias_iridl(t, ut)
        plano = arr.reshape(arr.shape[0], -1)
        for u, idx in mapa.items():
            sub = plano[:, idx]
            with np.errstate(invalid="ignore"):
                media = np.nanmean(sub, axis=1)
                maxcel = np.nanmax(sub, axis=1)
            s = pd.DataFrame({"fecha": dias, "media": media, "maxcel": maxcel})
            if etiqueta == "chirps":  # la serie diaria solo se guarda para las ventanas de eventos
                filas_dia.append(pd.DataFrame({"ubigeo": u, "fecha": dias.strftime("%Y-%m-%d"),
                                               "evento": "_".join(p.stem.split("_")[-2:]),
                                               "lluvia_mm": np.round(media, 1), "lluvia_max_celda_mm": np.round(maxcel, 1)}))
            g = s.groupby(s["fecha"].dt.to_period("M"))
            filas_mes.append(pd.DataFrame({
                "ubigeo": u, "fecha": g.size().index.astype(str),
                "lluvia_total_mm": g["media"].sum().round(1).values,
                "lluvia_max_diaria_mm": g["media"].max().round(1).values,
                "lluvia_max_diaria_celda_mm": g["maxcel"].max().round(1).values,
                "dias_mayor_10mm": g["media"].apply(lambda x: int((x >= 10).sum())).values,
                "dias_mayor_20mm": g["media"].apply(lambda x: int((x >= 20).sum())).values,
                "max_acum_3dias_mm": g["media"].apply(lambda x: x.rolling(3).sum().max()).round(1).values,
            }))
        print(f"  {p.name}")
    return pd.concat(filas_mes), (pd.concat(filas_dia) if filas_dia else pd.DataFrame())


def pisco_diario() -> None:
    print("Lluvia diaria PISCO -> intensidad mensual por distrito")
    archivos = sorted((PISCO / "pisco_diario").glob("pisco_diario_*.nc"))
    if not archivos:
        print("  no hay archivos")
        return
    mes, _ = _intensidad_diaria(archivos, "pisco")
    mes = distritos()[["ubigeo", "distrito", "provincia", "departamento"]].merge(mes, on="ubigeo")
    guardar(mes, L_LLUVIA, "lluvia_intensidad_pisco_distrito_mes.csv")


def chirps_diario() -> None:
    print("Lluvia diaria CHIRPS en ventanas de eventos")
    archivos = sorted((CHIRPS / "chirps_diario_eventos").glob("chirps_diario_*.nc"))
    if not archivos:
        print("  no hay archivos")
        return
    mes, dia = _intensidad_diaria(archivos, "chirps")
    base = distritos()[["ubigeo", "distrito", "provincia", "departamento"]]
    guardar(base.merge(mes, on="ubigeo"), L_LLUVIA, "lluvia_intensidad_chirps_eventos_distrito_mes.csv")
    guardar(base.merge(dia, on="ubigeo"), L_LLUVIA, "lluvia_diaria_chirps_eventos_distrito.csv")


# ----------------------------------------------------------------------------- caudales
def caudales() -> None:
    print("Caudales GloFAS")
    filas, meta = [], []
    for carpeta in sorted((GLOFAS / "historico").glob("*")):
        for f in sorted(carpeta.glob("*.json")):
            j = json.loads(f.read_text())
            filas.append(pd.DataFrame({"rio_punto": carpeta.name, "fecha": j["daily"]["time"], "caudal_m3s": j["daily"]["river_discharge"]}))
        meta.append({"rio_punto": carpeta.name, "lat_celda": j["latitude"], "lon_celda": j["longitude"]})
    if not filas:
        print("  no hay archivos")
        return
    df = pd.concat(filas).dropna(subset=["caudal_m3s"])
    guardar(df, L_CAUDALES, "caudales_glofas_diario.csv")
    df["mes"] = df["fecha"].str[:7]
    m = df.groupby(["rio_punto", "mes"])["caudal_m3s"].agg(caudal_medio_m3s="mean", caudal_max_m3s="max").round(1).reset_index()
    guardar(m, L_CAUDALES, "caudales_glofas_mensual.csv")
    guardar(pd.DataFrame(meta), L_CAUDALES, "caudales_glofas_puntos.csv")
    pron = []
    for f in sorted((GLOFAS / "pronostico").glob("*.json")):
        j = json.loads(f.read_text())
        x = pd.DataFrame(j["daily"]).rename(columns={"time": "fecha"})
        x.insert(0, "rio_punto", f.stem.split("_pronostico_")[0])
        x.insert(1, "emitido", f.stem.split("_pronostico_")[1])
        pron.append(x)
    if pron:
        pron = pd.concat(pron)
        valores = [c for c in pron.columns if c.startswith("river_discharge")]
        vacias = pron[valores].isna().all(axis=1)
        print(f"  pronóstico: se quitan {vacias.sum()} filas vacías (últimos días del horizonte)")
        guardar(pron[~vacias], L_CAUDALES, "caudales_glofas_pronostico.csv")
    pico = df.groupby(["rio_punto", df["fecha"].str[:4]])["caudal_m3s"].max().unstack(0)
    print("  caudal máximo ene-abr (m³/s) en años clave:")
    print(pico.loc[[a for a in ["1998", "2017", "2023", "2026"] if a in pico.index]].round(0).T.to_string())


# ----------------------------------------------------------------------------- estaciones
UMBRAL_REVISAR_MM = 200  # lluvia diaria a partir de la cual el dato se marca para revisar


def estaciones() -> None:
    print("Estaciones GHCN-Daily")
    inv = (GHCN / "estaciones_costa_norte.txt").read_text().splitlines() if (GHCN / "estaciones_costa_norte.txt").exists() else []
    meta = {l[0:11]: {"estacion": l[0:11], "lat": float(l[12:20]), "lon": float(l[21:30]), "altitud_m": float(l[31:37]), "nombre": l[41:71].strip()} for l in inv}
    filas = []
    for f in sorted((GHCN / "ghcn").glob("*.csv.gz")):
        x = pd.read_csv(f, header=None, names=["estacion", "fecha", "elemento", "valor", "mflag", "qflag", "sflag", "hora"], dtype=str)
        x = x[(x.elemento == "PRCP") & (x.qflag.isna())]
        if len(x):
            filas.append(pd.DataFrame({"estacion": x.estacion, "fecha": pd.to_datetime(x.fecha, format="%Y%m%d").dt.strftime("%Y-%m-%d"),
                                       "lluvia_mm": x.valor.astype(float) / 10}))
    if not filas:
        print("  no hay datos")
        return
    df = pd.concat(filas)
    df["revisar_mayor_200mm"] = df["lluvia_mm"] > UMBRAL_REVISAR_MM
    print(f"  {df['revisar_mayor_200mm'].sum()} días con más de {UMBRAL_REVISAR_MM} mm marcados para revisar:")
    print(df[df.revisar_mayor_200mm].assign(nombre=lambda z: z.estacion.map(lambda s: meta.get(s, {}).get("nombre", "")))
          .to_string(index=False))
    guardar(df, L_LLUVIA, "estaciones_ghcn_lluvia_diaria.csv")
    res = df.groupby("estacion").agg(primer_dia=("fecha", "min"), ultimo_dia=("fecha", "max"), dias_con_dato=("fecha", "size"),
                                     lluvia_max_diaria_mm=("lluvia_mm", "max"),
                                     dias_para_revisar=("revisar_mayor_200mm", "sum")).reset_index()
    for anio in ["1983", "1998", "2017", "2023"]:
        res[f"tiene_{anio}"] = res.estacion.map(df[df.fecha.str.startswith(anio)].groupby("estacion").size()).fillna(0).astype(int)
    res = pd.DataFrame(meta.values()).merge(res, on="estacion", how="right")
    # ¿En qué distrito de los 5 departamentos cae cada estación?
    d = distritos()
    ubi = []
    for _, r in res.iterrows():
        dentro = d[[g.contains(shapely.Point(r.lon, r.lat)) for g in d.geom]]
        ubi.append(dentro.ubigeo.iloc[0] if len(dentro) else None)
    res.insert(5, "ubigeo", ubi)
    res.insert(6, "dentro_area_estudio", res["ubigeo"].notna())
    guardar(res, L_LLUVIA, "estaciones_ghcn_resumen.csv")


# ----------------------------------------------------------------------------- DesInventar
# Equivalente al filtro de peligros por lluvias de INDECI que usa 02_preparar_panel.py
# (lluvia intensa, inundación, huayco, deslizamiento, derrumbe, erosión). No incluye marejadas.
HIDRO = {"Inundación", "Lluvias", "Aluvión (Huayco)", "Avenida torrencial", "Deslizamiento", "Derrumbe", "Erosión"}

# Nombre en el XML -> nombre limpio (alineado con los de INDECI cuando miden lo mismo)
CAMPOS_DI = {
    "uu_id": "id_desinventar", "serial": "serial", "level0": "level0", "level1": "level1", "level2": "ubigeo",
    "name1": "provincia", "name2": "distrito", "evento": "evento", "lugar": "lugar", "fechano": "anio",
    "fechames": "mes_num", "fechadia": "dia", "muertos": "fallecidos", "desaparece": "desaparecidos",
    "heridos": "heridos", "afectados": "afectados", "damnificados": "damnificados", "evacuados": "evacuados",
    "reubicados": "reubicados", "vivdest": "viviendas_destruidas", "vivafec": "viviendas_afectadas",
    "nhectareas": "ha_cultivos_bosques", "kmvias": "vias_km", "nescuelas": "centros_educativos",
    "nhospitales": "centros_salud", "valorloc": "perdidas_moneda_local", "valorus": "perdidas_usd",
    "causa": "causa", "descausa": "descripcion_causa", "duracion": "duracion_dias", "fuentes": "fuentes",
    "latitude": "lat", "longitude": "lon",
}


def desinventar() -> None:
    print("DesInventar")
    xmlp = DESINVENTAR / "DI_export_per" / "DI_export_per.xml"
    filas, en_fichas = [], False
    for ev, el in ET.iterparse(xmlp, events=("start", "end")):
        if ev == "start" and el.tag == "fichas":
            en_fichas = True
        elif ev == "end" and el.tag == "fichas":
            break
        elif ev == "end" and el.tag == "TR" and en_fichas:
            filas.append({c: (el.findtext(c) or "").strip() for c in CAMPOS_DI})
            el.clear()
    df = pd.DataFrame(filas).rename(columns=CAMPOS_DI)
    print(f"  {len(df):,} fichas en todo el Perú")
    df = df[df.level0.isin(DEPTOS)].copy()
    assert df.id_desinventar.is_unique, "id_desinventar repetido"
    repetidas = df.drop(columns="id_desinventar").duplicated()
    print(f"  fichas idénticas (salvo el id) que se quitan: {repetidas.sum()}")
    df = df[~repetidas]
    num = ["anio", "mes_num", "dia", "fallecidos", "desaparecidos", "heridos", "afectados", "damnificados", "evacuados",
           "reubicados", "viviendas_destruidas", "viviendas_afectadas", "ha_cultivos_bosques", "vias_km",
           "centros_educativos", "centros_salud", "perdidas_moneda_local", "perdidas_usd", "duracion_dias", "lat", "lon"]
    for c in num:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # 0 en estas columnas significa "sin dato"
    df.loc[~df.mes_num.between(1, 12), "mes_num"] = np.nan
    df.loc[~df.dia.between(1, 31), "dia"] = np.nan
    sin_coord = (df.lat == 0) | (df.lon == 0)
    df.loc[sin_coord, ["lat", "lon"]] = np.nan
    print(f"  coordenadas 0 -> vacío: {sin_coord.sum():,} de {len(df):,}")
    df["anio"] = df["anio"].astype(int)
    for c in ["mes_num", "dia"]:
        df[c] = df[c].astype("Int64")
    # Fecha completa solo cuando hay año, mes y día válidos
    txt = (df.anio.astype(str) + "-" + df.mes_num.astype("string").str.zfill(2) + "-"
           + df.dia.astype("string").str.zfill(2))
    fecha = pd.to_datetime(txt, format="%Y-%m-%d", errors="coerce")
    df.insert(df.columns.get_loc("dia") + 1, "fecha", fecha.dt.strftime("%Y-%m-%d"))
    df["departamento"] = df.level0.map(DEPTOS)
    df["nivel_geografico"] = np.where(df.ubigeo.str.len() == 6, "distrito",
                                      np.where(df.level1.str.len() == 4, "provincia", "departamento"))
    for c in ["ubigeo", "provincia", "distrito"]:
        df[c] = df[c].replace("", np.nan)
    df["hidrometeorologico"] = df.evento.isin(HIDRO)
    df["causa_el_nino"] = (df.causa.str.contains("Niño|Nino|NIÑO", case=False, regex=True)
                           | df.descripcion_causa.str.contains("Niño|Nino|NIÑO", case=False, regex=True))
    print("  nivel geográfico:", df.nivel_geografico.value_counts().to_dict())
    print(f"  años {df.anio.min()}-{df.anio.max()}; fichas hidrometeorológicas: {df.hidrometeorologico.sum():,}")
    orden = ["id_desinventar", "serial", "departamento", "provincia", "distrito", "ubigeo", "nivel_geografico"]
    df = df[orden + [c for c in df.columns if c not in orden + ["level0", "level1"]]]
    guardar(df, L_EMERGENCIAS, "desinventar_fichas_costa_norte.csv")

    h = df[df.hidrometeorologico].copy()
    h["con_damnificados"] = ((h.damnificados > 0) | (h.viviendas_destruidas > 0)).astype(int)
    agg = dict(fichas=("id_desinventar", "size"), fichas_con_damnificados=("con_damnificados", "sum"),
               fallecidos=("fallecidos", "sum"), damnificados=("damnificados", "sum"), afectados=("afectados", "sum"),
               viviendas_destruidas=("viviendas_destruidas", "sum"), viviendas_afectadas=("viviendas_afectadas", "sum"),
               ha_cultivos_bosques=("ha_cultivos_bosques", "sum"))
    hm = h[h.mes_num.notna()].astype({"mes_num": int})
    panel = hm.groupby(["departamento", "anio", "mes_num"]).agg(**agg).reset_index()
    # Completar meses sin registros con ceros
    a0, a1 = int(df.anio.min()), int(df.anio.max())
    completo = pd.MultiIndex.from_product([list(DEPTOS.values()), range(a0, a1 + 1), range(1, 13)], names=["departamento", "anio", "mes_num"])
    panel = panel.set_index(["departamento", "anio", "mes_num"]).reindex(completo, fill_value=0).reset_index()
    panel.insert(1, "fecha", panel.anio.astype(str) + "-" + panel.mes_num.astype(str).str.zfill(2))
    guardar(panel, L_EMERGENCIAS, "desinventar_panel_departamento_mes.csv")
    print(f"  fichas de lluvias sin mes (fuera del panel mensual): {h.mes_num.isna().sum()}")

    # Por distrito y año: solo las fichas registradas a nivel distrito
    hd = h[h.nivel_geografico == "distrito"]
    da = hd.groupby(["ubigeo", "anio"]).agg(**agg).reset_index()
    nombres = distritos()[["ubigeo", "departamento", "provincia", "distrito"]]
    da = nombres.merge(da, on="ubigeo", how="right")
    sin_mapa = da.distrito.isna()
    if sin_mapa.any():  # ubigeos que ya no existen en el mapa actual
        print(f"  ubigeos de DesInventar que no están en el mapa de distritos: {sorted(da.loc[sin_mapa, 'ubigeo'].unique())}")
        alt = hd.drop_duplicates("ubigeo").set_index("ubigeo")
        for c in ["departamento", "provincia", "distrito"]:
            da.loc[sin_mapa, c] = da.loc[sin_mapa, "ubigeo"].map(alt[c])
    guardar(da, L_EMERGENCIAS, "desinventar_distrito_anio.csv")
    print(f"  fichas de lluvias sin distrito (solo en el panel por departamento): {(h.nivel_geografico != 'distrito').sum()}")
    tope = h.groupby("anio").agg(fichas=("id_desinventar", "size"), damnificados=("damnificados", "sum"))
    print("  años con más damnificados (lluvias, 5 deptos):")
    print(tope.sort_values("damnificados", ascending=False).head(8).to_string())


# ----------------------------------------------------------------------------- territorio
def _dem_mosaico(paso: int = 3):
    """Mosaico GLO-90 (1200 px por grado) submuestreado cada `paso` px (~270 m) y su pendiente."""
    import tifffile

    carpeta = DEM / "teselas"
    lat_s = range(4, 12)  # S04..S11 cubre de -3 a -11
    lon_w = range(77, 83)  # W077..W082 cubre de -83 a -76
    n = 1200
    alto, ancho = len(lat_s) * n, len(lon_w) * n
    dem = np.full((alto, ancho), np.nan, dtype="float32")
    for i, la in enumerate(sorted(lat_s)):  # fila 0 = la tesela más al norte (S04)
        for k, lo in enumerate(sorted(lon_w, reverse=True)):  # col 0 = la más al oeste (W082)
            f = carpeta / f"Copernicus_DSM_COG_30_S{la:02d}_00_W{lo:03d}_00_DEM.tif"
            if f.exists():
                a = tifffile.imread(f).astype("float32")
                if a.shape != (n, n):
                    a = a[:n, :n]
                dem[i * n:(i + 1) * n, k * n:(k + 1) * n] = a
    # Coordenadas del centro de cada píxel. Tesela SXX cubre de -XX a -XX+1 (borde norte = -XX+1)
    norte, oeste = -min(lat_s) + 1, -max(lon_w)
    res = 1 / n
    lat = norte - (np.arange(alto) + 0.5) * res
    lon = oeste + (np.arange(ancho) + 0.5) * res
    # Pendiente (grados) a resolución completa
    dy = 111320 * res
    dx = 111320 * res * np.cos(np.deg2rad(lat))[:, None]
    gy, gx = np.gradient(dem)
    pend = np.degrees(np.arctan(np.hypot(gx / dx, gy / dy))).astype("float32")
    return dem[::paso, ::paso], pend[::paso, ::paso], lon[::paso], lat[::paso]


def territorio() -> None:
    print("Territorio: atributos por distrito")
    d = distritos().copy()
    ind = pd.read_csv(INDICADORES / "ubigeo_distrito_indicadores.csv", dtype={"inei": str})
    ind = ind.rename(columns={"inei": "ubigeo", "superficie": "superficie_km2", "altitude": "altitud_capital_m",
                              "latitude": "lat_capital", "longitude": "lon_capital"})
    for c in ["superficie_km2", "pob_densidad_2020", "altitud_capital_m", "lat_capital", "lon_capital", "idh_2019",
              "pct_pobreza_total", "pct_pobreza_extrema", "indice_vulnerabilidad_alimentaria"]:
        ind[c] = pd.to_numeric(ind[c], errors="coerce")  # algunas celdas vienen como "NA"
    ind["poblacion_2020_estimada"] = (ind["pob_densidad_2020"] * ind["superficie_km2"]).round(0)
    cols = ["ubigeo", "capital", "superficie_km2", "pob_densidad_2020", "poblacion_2020_estimada", "altitud_capital_m",
            "lat_capital", "lon_capital", "idh_2019", "pct_pobreza_total", "pct_pobreza_extrema", "indice_vulnerabilidad_alimentaria"]
    d = d.merge(ind[cols], on="ubigeo", how="left")
    d["lon_centroide"] = d.geom.apply(lambda g: g.centroid.x).round(4)
    d["lat_centroide"] = d.geom.apply(lambda g: g.centroid.y).round(4)

    # Relieve
    try:
        dem, pend, lon, lat = _dem_mosaico()
        LON, LAT = np.meshgrid(lon, lat)
        lonf, latf, demf, penf = LON.ravel(), LAT.ravel(), dem.ravel(), pend.ravel()
        stats = []
        for _, r in d.iterrows():
            g = r.geom
            x0, y0, x1, y1 = g.bounds
            c = np.where((lonf >= x0) & (lonf <= x1) & (latf >= y0) & (latf <= y1))[0]
            c = c[shapely.contains_xy(g, lonf[c], latf[c])]
            z, s = demf[c], penf[c]
            ok = ~np.isnan(z)
            z, s = z[ok], s[ok]
            if len(z) == 0:
                stats.append({})
                continue
            stats.append({"elev_media_m": round(float(z.mean()), 1), "elev_min_m": round(float(z.min()), 1),
                          "elev_p10_m": round(float(np.percentile(z, 10)), 1),
                          "pct_area_bajo_50m": round(100 * float((z < 50).mean()), 1),
                          "pct_area_bajo_200m": round(100 * float((z < 200).mean()), 1),
                          "pendiente_media_grados": round(float(s.mean()), 2),
                          "pct_area_pendiente_menor_2": round(100 * float((s < 2).mean()), 1)})
        d = pd.concat([d.reset_index(drop=True), pd.DataFrame(stats)], axis=1)
        print("  relieve listo (Copernicus GLO-90 a ~270 m)")
    except Exception as e:  # noqa: BLE001
        print(f"  sin relieve: {e}")

    # Ríos mayores (HydroRIVERS, cuenca aportante >= 1000 km²)
    rp = RIOS / "hydrorivers_costa_norte.geojson"
    if rp.exists():
        gj = json.loads(rp.read_text())
        mayores = [shape(f["geometry"]) for f in gj["features"] if f["properties"].get("UPLAND_SKM", 0) >= 1000]
        arbol = shapely.STRtree(mayores)
        props = [f["properties"] for f in gj["features"] if f["properties"].get("UPLAND_SKM", 0) >= 1000]
        dist_km, upl = [], []
        for _, r in d.iterrows():
            pt = shapely.Point(r.lon_centroide, r.lat_centroide)
            i = arbol.nearest(pt)
            dist_km.append(round(mayores[i].distance(pt) * 111.32, 2))  # aproximado (grados -> km)
            cruza = arbol.query(r.geom, predicate="intersects")
            upl.append(max([props[k]["UPLAND_SKM"] for k in cruza], default=0))
        d["dist_centroide_a_rio_mayor_km"] = dist_km
        d["cuenca_max_que_cruza_km2"] = upl
        print(f"  ríos: {len(mayores)} tramos con cuenca >= 1000 km²")

    # Historial de desastres por distrito (DesInventar + INDECI)
    di = L_EMERGENCIAS / "desinventar_distrito_anio.csv"
    if di.exists():
        x = pd.read_csv(di, dtype={"ubigeo": str})
        d["desinventar_fichas_lluvias_1970_2015"] = d.ubigeo.map(x.groupby("ubigeo")["fichas"].sum()).fillna(0).astype(int)
        for a in (1983, 1998):
            d[f"desinventar_damnificados_{a}"] = d.ubigeo.map(x[x.anio == a].groupby("ubigeo")["damnificados"].sum()).fillna(0).astype(int)
    indeci = L_EMERGENCIAS / "indeci_emergencias_2003_2025.csv"
    if indeci.exists():
        # Mismo filtro de peligros por lluvias que usa 02_preparar_panel.py (columna es_peligro_lluvias).
        # Se usa ubigeo_mapa: los distritos creados después del mapa se suman a su distrito de origen.
        y = pd.read_csv(indeci, dtype={"ubigeo_mapa": str},
                        usecols=["ubigeo_mapa", "anio", "peligro", "es_peligro_lluvias", "damnificados"])
        y = y[y.es_peligro_lluvias].rename(columns={"ubigeo_mapa": "ubigeo"})
        g = y.groupby("ubigeo")
        d["indeci_emergencias_lluvias_2003_2025"] = d.ubigeo.map(g.size()).fillna(0).astype(int)
        d["indeci_emerg_con_damnificados_2003_2025"] = d.ubigeo.map(y[y.damnificados > 0].groupby("ubigeo").size()).fillna(0).astype(int)
        for a in (2017, 2023):
            d[f"indeci_damnificados_{a}"] = d.ubigeo.map(y[y.anio == a].groupby("ubigeo")["damnificados"].sum()).fillna(0).astype(int)
        # Tabla distrito x año (para usar como variable objetivo a nivel distrito)
        yy = y.assign(con_damnificados=(y.damnificados > 0).astype(int)).groupby(["ubigeo", "anio"]).agg(
            emergencias_lluvias=("peligro", "size"), emerg_con_damnificados=("con_damnificados", "sum"),
            damnificados=("damnificados", "sum")).reset_index()
        yy = d[["ubigeo", "distrito", "provincia", "departamento"]].merge(yy, on="ubigeo")
        guardar(yy, L_EMERGENCIAS, "indeci_distrito_anio_lluvias.csv")
    else:
        print("  falta la base limpia de INDECI: corre antes 02_preparar_panel.py")
    guardar(d.drop(columns=["geom"]), L_TERRITORIO, "distritos_costa_norte_atributos.csv")

    # Mapa de los 364 distritos (para dibujar resultados del modelo)
    feats = [{"type": "Feature", "geometry": mapping(r.geom),
              "properties": {"ubigeo": r.ubigeo, "distrito": r.distrito, "provincia": r.provincia,
                             "departamento": r.departamento}} for r in distritos().itertuples()]
    L_TERRITORIO.mkdir(parents=True, exist_ok=True)
    (L_TERRITORIO / "distritos_costa_norte.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    print(f"  -> territorio/distritos_costa_norte.geojson: {len(feats)} distritos")


# ----------------------------------------------------------------------------- compilados
def compilados() -> None:
    """Cifras copiadas a mano de informes y noticias: se validan los tipos y se copian."""
    print("Datos compilados a mano")
    c = pd.read_csv(MANUAL / "caudales_pico_rio_piura_observados.csv")
    c["caudal_pico_m3s"] = pd.to_numeric(c["caudal_pico_m3s"], errors="raise")
    guardar(c, L_CAUDALES, "caudales_pico_rio_piura_observados.csv")
    i = pd.read_csv(MANUAL / "impactos_eventos_nino_compilados.csv")
    i["valor"] = pd.to_numeric(i["valor"], errors="raise")
    guardar(i, L_EMERGENCIAS, "impactos_eventos_nino_compilados.csv")


SECCIONES = {"enso": enso, "lluvia": lluvia, "pisco_diario": pisco_diario, "chirps_diario": chirps_diario,
             "caudales": caudales, "estaciones": estaciones, "desinventar": desinventar, "territorio": territorio,
             "compilados": compilados}

if __name__ == "__main__":
    pedidas = sys.argv[1:] or list(SECCIONES)
    fallas = []
    for s in pedidas:
        try:
            SECCIONES[s]()
        except Exception as e:  # noqa: BLE001
            print(f"!! {s} falló: {type(e).__name__}: {e}")
            fallas.append(s)
    print("Listo." if not fallas else f"Terminó con fallas en: {', '.join(fallas)}")
    sys.exit(1 if fallas else 0)
