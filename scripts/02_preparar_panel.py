"""Limpia la base de INDECI y arma la tabla departamento-mes de la costa norte con ICEN y lluvia.

Entradas (datos/1_crudos/):
  INDECI_SINPAD/BD_2003-2025_EMERGENCIAS.csv, ENFEN_IGP_ICEN/ICEN.txt,
  UCSB_CHIRPS/chirps_costa_norte_1991_hoy.nc, INEI_limites_geojson/peru_departamentos.geojson

Salidas (datos/2_limpios/):
  emergencias/indeci_emergencias_2003_2025.csv    la base nacional limpia, columnas en snake_case
  lluvia/lluvia_chirps_anomalia_departamento.csv  lluvia mensual por departamento, con normal y anomalía
  modelo/panel_costa_norte_2003_2025.csv          la tabla que usa el modelo (4 departamentos x 276 meses)

Reglas de limpieza de INDECI:
  - Fechas: de 2003 a 2024 vienen como dd/mm/aaaa y las de 2025 como mm/dd/aa. Se comprueba
    que coincidan con AÑO y MES en todas las filas.
  - Números con coma decimal se pasan a punto.
  - Un registro (código 5420, 2004) tiene costo de ayuda negativo: queda vacío.
  - 7 códigos SINPAD aparecen dos veces con fecha, lugar o peligro distintos. Parecen emergencias
    distintas con el código reutilizado, así que no se borran: se marcan en codigo_sinpad_repetido.
  - Colegios: hasta 2018 se registraban centros educativos destruidos/afectados; desde 2019, aulas.
    Vacío en esas columnas significa "no se registraba en ese periodo", no cero.
  - ubigeo_mapa: el mapa de distritos no tiene los distritos creados hace poco. Dos de la zona de
    estudio se suman al distrito del que se separaron (ver UBIGEOS_NUEVOS); en el resto es igual a ubigeo.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import Point, shape
from shapely.prepared import prep

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import CHIRPS, ICEN, INDECI, L_EMERGENCIAS, L_LLUVIA, L_MODELO, LIMITES  # noqa: E402

NORTE = ["TUMBES", "PIURA", "LAMBAYEQUE", "LA LIBERTAD"]
# Peligros asociados a lluvias (nombres tal como vienen en la base 2003-2025, sin tildes)
LLUVIA = ["LLUVIA INTENSA", "INUNDACION", "HUAYCO", "DESLIZAMIENTO", "DERRUMBE DE CERRO", "EROSION"]
MESES = {"ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6, "JULIO": 7,
         "AGOSTO": 8, "SETIEMBRE": 9, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12}

# Distritos creados después del mapa de límites -> distrito del que se separaron.
# INDECI registra Veintiséis de Octubre desde 2015; antes sus emergencias iban a Piura.
UBIGEOS_NUEVOS = {
    "200115": "200101",  # Veintiséis de Octubre (2013) -> Piura
    "130112": "130102",  # Alto Trujillo (2021) -> El Porvenir
}

# Nombre original (sin espacios al borde) -> nombre limpio
COLUMNAS = {
    "CODIGO DE EMERGENCIA-SINPAD": "codigo_sinpad",
    "COD. DISTRITO": "ubigeo",
    "DPTO.": "departamento",
    "PROV.": "provincia",
    "DIST.": "distrito",
    "PELIGRO": "peligro",
    "TIPO DE PELIGRO": "tipo_peligro",
    "REGIÓN NATURAL": "region_natural",
    "FALLECIDOS": "fallecidos",
    "DESAPARECIDOS": "desaparecidos",
    "LESIONADOS": "lesionados",
    "DAMNIFICADOS": "damnificados",
    "AFECTADOS": "afectados",
    "VIVIENDAS DESTRUIDAS": "viviendas_destruidas",
    "VIVIENDAS AFECTADAS": "viviendas_afectadas",
    "CENTROS EDUCATIVOS DESTRUIDOS": "colegios_destruidos_hasta_2018",
    "CENTROS EDUCATIVOS AFECTADOS": "colegios_afectados_hasta_2018",
    "SCANT_CCEE": "colegios_cantidad_desde_2019",
    "SAFEC_AULA": "aulas_afectadas_desde_2019",
    "AULA_DES+INHA": "aulas_destruidas_o_inhabitables_2019_2024",
    "SDESTRU_AULA": "aulas_destruidas_desde_2019",
    "SINHAB_AULA": "aulas_inhabitables_desde_2019",
    "CENTROS SALUD DESTRUIDOS": "centros_salud_destruidos",
    "CENTROS SALUD AFECTADOS": "centros_salud_afectados",
    "HAS CULTIVO DESTRUIDO": "ha_cultivo_destruido",
    "HAS CULTIVO AFECTADO": "ha_cultivo_afectado",
    "PUENTE DESTRUIDO": "puentes_destruidos",
    "PUENTE AFECTADO": "puentes_afectados",
    "CARRETERA DESTRUIDA KM": "carretera_destruida_km",
    "CARRETERA AFECTADA KM": "carretera_afectada_km",
    "CAMINO RURAL DESTRUIDO KM": "camino_rural_destruido_km",
    "CAMINO RURAL AFECTADO KM": "camino_rural_afectado_km",
    "CANAL DE REGADIO COLAPSADO": "canal_riego_colapsado",
    "CANAL DE REGADIO AFECTADO": "canal_riego_afectado",
    "PERDIDA VACUNO": "vacunos_perdidos",
    "AFECTADOS VACUNO": "vacunos_afectados",
    "PERDIDA CAMELIDO": "camelidos_perdidos",
    "AFECTADOS CAMELIDO": "camelidos_afectados",
    "PERDIDA CAPRINO": "caprinos_perdidos",
    "AFECTADOS CAPRINO": "caprinos_afectados",
    "PERDIDA PORCINO": "porcinos_perdidos",
    "AFECTADOS PORCINO": "porcinos_afectados",
    "PERDIDA DE ANIMALES MENORES": "animales_menores_perdidos",
    "AFECTA DE ANIMALES MENORES": "animales_menores_afectados",
    "PESO DE LA AYUDA": "ayuda_peso",
    "COSTO DE LA AYUDA": "ayuda_costo",
}


def leer_emergencias():
    df = pd.read_csv(INDECI / "BD_2003-2025_EMERGENCIAS.csv", sep=";", encoding="latin1",
                     dtype={"COD. DISTRITO": str, "CODIGO DE EMERGENCIA-SINPAD": str}, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    numericas = list(df.columns[11:])
    assert set(df.columns) == set(COLUMNAS) | {"FECHA  DE LA EMER", "AÑO", "MES"}, "cambiaron las columnas de INDECI"

    # 2003-2024 vienen como dd/mm/aaaa; 2025 como mm/dd/aa
    texto = df["FECHA  DE LA EMER"].astype(str)
    larga = texto.str.match(r"^\d{2}/\d{2}/\d{4}$")
    fecha = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    fecha[larga] = pd.to_datetime(texto[larga], format="%d/%m/%Y")
    fecha[~larga] = pd.to_datetime(texto[~larga], format="%m/%d/%y")

    mes = df["MES"].str.strip().str.upper().map(MESES)
    assert (fecha.dt.year == df["AÑO"]).all() and (fecha.dt.month == mes).all(), "fechas incoherentes"

    for c in numericas:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    df.loc[df["COSTO DE LA AYUDA"] < 0, "COSTO DE LA AYUDA"] = np.nan

    limpio = df.rename(columns=COLUMNAS).drop(columns=["FECHA  DE LA EMER", "AÑO", "MES"])
    for c in ["departamento", "provincia", "distrito", "peligro", "tipo_peligro", "region_natural"]:
        limpio[c] = limpio[c].str.strip()
    limpio.insert(1, "fecha", fecha)
    limpio.insert(2, "anio", fecha.dt.year)
    limpio.insert(3, "mes_num", fecha.dt.month)
    limpio.insert(limpio.columns.get_loc("ubigeo") + 1, "ubigeo_mapa", limpio["ubigeo"].replace(UBIGEOS_NUEVOS))
    limpio.insert(limpio.columns.get_loc("peligro") + 1, "es_peligro_lluvias", limpio["peligro"].isin(LLUVIA))
    limpio["codigo_sinpad_repetido"] = limpio["codigo_sinpad"].duplicated(keep=False)
    return limpio


def armar_panel(df):
    n = df[df["es_peligro_lluvias"] & df["departamento"].isin(NORTE)].copy()
    n["mes"] = n["fecha"].dt.to_period("M")
    n["con_damnif"] = (n["damnificados"] > 0).astype(int)
    agg = n.groupby(["departamento", "mes"]).agg(
        emergencias=("peligro", "size"),
        emerg_con_damnificados=("con_damnif", "sum"),
        fallecidos=("fallecidos", "sum"),
        damnificados=("damnificados", "sum"),
        afectados=("afectados", "sum"),
        viviendas_destruidas=("viviendas_destruidas", "sum"),
        viviendas_afectadas=("viviendas_afectadas", "sum"),
        ha_cultivo_destruido=("ha_cultivo_destruido", "sum"),
        ha_cultivo_afectado=("ha_cultivo_afectado", "sum"),
    )
    idx = pd.MultiIndex.from_product([NORTE, pd.period_range("2003-01", "2025-12", freq="M")],
                                     names=["departamento", "mes"])
    agg = agg.reindex(idx, fill_value=0).reset_index()
    agg.insert(2, "anio", agg["mes"].dt.year)
    agg.insert(3, "mes_num", agg["mes"].dt.month)
    return agg


def leer_icen():
    ic = pd.read_csv(ICEN / "ICEN.txt", comment="%", sep=r"\s+", names=["a", "m", "icen"])
    ic["mes"] = [pd.Period(year=a, month=m, freq="M") for a, m in zip(ic["a"], ic["m"])]
    return ic.set_index("mes")["icen"]


def leer_lluvia():
    d = xr.open_dataset(CHIRPS / "chirps_costa_norte_1991_hoy.nc", decode_times=False)
    # T viene en "meses desde 1960-01" con calendario de 360 días
    meses = [pd.Period("1960-01", freq="M") + int(np.floor(t)) for t in d["T"].values]
    precip = d["precipitation"].values  # mm/mes
    X, Y = np.meshgrid(d["X"].values, d["Y"].values)
    puntos = [Point(x, y) for x, y in zip(X.ravel(), Y.ravel())]
    deptos = json.loads((LIMITES / "peru_departamentos.geojson").read_text())

    series = []
    for f in deptos["features"]:
        dep = f["properties"]["NOMBDEP"]
        if dep not in NORTE:
            continue
        pol = prep(shape(f["geometry"]))
        dentro = np.array([pol.contains(p) for p in puntos]).reshape(X.shape)
        media = np.nanmean(precip[:, dentro], axis=1).astype("float64")
        series.append(pd.DataFrame({"departamento": dep, "mes": meses, "lluvia_mm": media}))
    ll = pd.concat(series, ignore_index=True)

    ll["mes_num"] = ll["mes"].dt.month
    base = ll[ll["mes"].dt.year.between(1991, 2020)]
    normal = base.groupby(["departamento", "mes_num"])["lluvia_mm"].mean().rename("lluvia_normal_mm")
    ll = ll.join(normal, on=["departamento", "mes_num"])
    ll["lluvia_anomalia_mm"] = ll["lluvia_mm"] - ll["lluvia_normal_mm"]
    ll["lluvia_pct_normal"] = ll["lluvia_mm"] / ll["lluvia_normal_mm"] * 100
    ll = ll.drop(columns="mes_num")
    numericas = ll.select_dtypes("number").columns
    ll[numericas] = ll[numericas].round(1)
    return ll


if __name__ == "__main__":
    for carpeta in (L_EMERGENCIAS, L_LLUVIA, L_MODELO):
        carpeta.mkdir(parents=True, exist_ok=True)

    df = leer_emergencias()
    df.to_csv(L_EMERGENCIAS / "indeci_emergencias_2003_2025.csv", index=False, date_format="%Y-%m-%d")
    print("Emergencias:", len(df), "filas, de", df["fecha"].min().date(), "a", df["fecha"].max().date(),
          f"({df['codigo_sinpad_repetido'].sum()} filas con código repetido, marcadas)")

    panel = armar_panel(df)

    icen = leer_icen()
    panel["icen"] = panel["mes"].map(icen)
    panel["icen_lag1"] = (panel["mes"] - 1).map(icen)
    panel["icen_lag2"] = (panel["mes"] - 2).map(icen)
    # Umbrales del ENFEN para la condición del mes (un evento requiere además 3 meses seguidos)
    panel["icen_condicion"] = pd.cut(
        panel["icen"], [-99, -1.4, -1.2, -1.0, 0.4, 1.0, 1.7, 3.0, 99],
        labels=["Niña fuerte", "Niña moderada", "Niña débil", "Neutro",
                "Niño débil", "Niño moderado", "Niño fuerte", "Niño extraordinario"])

    lluvia = leer_lluvia()
    lluvia.to_csv(L_LLUVIA / "lluvia_chirps_anomalia_departamento.csv", index=False)
    panel = panel.merge(lluvia, on=["departamento", "mes"], how="left")

    assert panel.notna().all().all(), "hay vacíos en la tabla"
    panel.to_csv(L_MODELO / "panel_costa_norte_2003_2025.csv", index=False)
    print("Tabla:", len(panel), "filas,", len(panel.columns), "columnas")
