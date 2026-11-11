"""Descarga datos históricos complementarios en datos/1_crudos/<fuente>/.

Completa lo que ya baja 01_descargar_clima.py (ICEN, CHIRPS 1991+; INDECI se baja a mano)
con series más largas, para poder incluir los Niños extraordinarios de 1972-73,
1982-83 y 1997-98, que la base de INDECI no cubre.

Uso:
    .venv/bin/python scripts/04_descargar_historicos.py            # todo
    .venv/bin/python scripts/04_descargar_historicos.py enso lluvia # solo algunos grupos

Grupos: enso, lluvia, pisco_diario, chirps_diario, caudales, caudales_resto,
        estaciones, desastres, territorio, relieve, rios

Si un archivo ya existe no se vuelve a bajar, así que se puede volver a correr
para completar lo que falló. Cada fuente está documentada en datos/CATALOGO_DATOS.md
y en el FUENTE.md de su carpeta. Para guardar el registro de la descarga:
    .venv/bin/python -u scripts/04_descargar_historicos.py | tee datos/1_crudos/_registros_descarga/04_$(date +%F).log
"""
from __future__ import annotations

import gzip
import json
import shutil

import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import (CHIRPS, CPC, DEM, DESINVENTAR, ERSST, GHCN, GLOFAS, GPCC, INDICADORES,  # noqa: E402
                   LIMITES, MEI, PISCO, RAIZ, RIOS)

UA = {"User-Agent": "Mozilla/5.0 (curso-analitica-datos; python-urllib)"}

# Caja que cubre Tumbes, Piura, Lambayeque, La Libertad y Áncash
X0, X1, Y0, Y1 = -81.5, -76.6, -10.9, -3.3
IRIDL = "https://iridl.ldeo.columbia.edu/SOURCES"
CAJA = f"X/{X0}/{X1}/RANGEEDGES/Y/{Y0}/{Y1}/RANGEEDGES"

# Celdas GloFAS ya "ajustadas" al cauce: se buscó, en un radio de ~10 km del punto
# nominal, la celda con mayor caudal en marzo de 2017 (ver CATALOGO_DATOS.md).
RIOS_PRIORITARIOS = {
    "tumbes_el_tigre": (-3.675, -80.475),
    "zarumilla": (-3.475, -80.275),
    "chira_ardilla": (-4.525, -80.475),
    "chira_sullana": (-4.775, -80.625),
    "piura_tambogrande": (-4.925, -80.425),
    "piura_bajo_piura_catacaos": (-5.275, -80.725),
    "la_leche_illimo": (-6.425, -79.975),
    "chancay_lambayeque_racarrumi": (-6.625, -79.425),
    "jequetepeque_ventanillas": (-7.275, -79.325),
    "santa_condorcerro": (-8.675, -78.375),
    "huarmey": (-10.025, -78.125),
}
RIOS_RESTO = {
    "motupe": (-6.225, -79.775),
    "zana": (-6.875, -79.475),
    "chicama_salinar": (-7.725, -79.075),
    "moche_quirihuac": (-8.025, -78.875),
    "viru": (-8.375, -78.775),
    "nepena": (-9.175, -78.375),
    "casma": (-9.475, -78.325),
}

# Ventanas diarias de eventos (nov-may) para CHIRPS diario
VENTANAS_EVENTO = {
    "1982_83": ("1 Nov 1982", "31 May 1983"),
    "1997_98": ("1 Nov 1997", "31 May 1998"),
    "2015_16": ("1 Nov 2015", "31 May 2016"),
    "2016_17": ("1 Nov 2016", "31 May 2017"),
    "2022_23": ("1 Nov 2022", "31 May 2023"),
    "2025_26": ("1 Nov 2025", "last"),
}


# ----------------------------------------------------------------------------- utilidades
def bajar(url: str, destino: Path, intentos: int = 4, timeout: int = 300) -> bool:
    """Descarga url a destino (si no existe). Devuelve True si quedó el archivo."""
    if destino.exists() and destino.stat().st_size > 0:
        return True
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".part")
    for i in range(intentos):
        try:
            req = urllib.request.Request(url.replace(" ", "%20"), headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
            tmp.rename(destino)
            print(f"  ok  {destino.relative_to(RAIZ)}  ({destino.stat().st_size/1e6:.1f} MB)")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"  404 {url}")
                tmp.unlink(missing_ok=True)
                return False
            espera = 60 if e.code == 429 else 5 * (i + 1)
            print(f"  HTTP {e.code}, reintento en {espera}s: {destino.name}")
            time.sleep(espera)
        except Exception as e:  # noqa: BLE001
            print(f"  error ({e}), reintento: {destino.name}")
            time.sleep(5 * (i + 1))
    tmp.unlink(missing_ok=True)
    print(f"  FALLÓ {destino.name}")
    return False


def es_netcdf(p: Path) -> bool:
    with open(p, "rb") as f:
        cab = f.read(4)
    return cab[:3] == b"CDF" or cab == b"\x89HDF"


def bajar_iridl(ruta: str, destino: Path) -> None:
    if bajar(f"{IRIDL}/{ruta}/data.nc", destino) and not es_netcdf(destino):
        print(f"  ! {destino.name} no es NetCDF (la IRI Data Library devolvió otra cosa); se borra")
        destino.unlink()


# ----------------------------------------------------------------------------- grupos
def enso() -> None:
    print("ENSO: índices oceánicos y atmosféricos (el ICEN oficial lo baja 01_descargar_clima.py)")
    fuentes = {
        CPC / "cpc_ersst5_nino_mensual_1950_hoy.txt": "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii",
        CPC / "cpc_oni.txt": "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
        CPC / "cpc_roni.txt": "https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt",
        CPC / "cpc_oisst_nino_semanal_1990_hoy.txt": "https://www.cpc.ncep.noaa.gov/data/indices/wksst9120.for",
        CPC / "cpc_soi.txt": "https://www.cpc.ncep.noaa.gov/data/indices/soi",
        MEI / "psl_mei_v2.txt": "https://psl.noaa.gov/enso/mei/data/meiv2.data",
    }
    for destino, url in fuentes.items():
        bajar(url, destino)
    # Campo de TSM ERSST v5 del Pacífico tropical (120E-70W, 20S-20N), mensual desde 1854.
    # Sirve para reconstruir el ICEN desde 1854 y como insumo de modelos tipo CNN.
    bajar_iridl(
        ".NOAA/.NCDC/.ERSST/.version5/.sst/X/120/290/RANGEEDGES/Y/-20/20/RANGEEDGES/"
        "T/(Jan%201854)/(last)/RANGEEDGES",
        ERSST / "ersst5_pacifico_tropical_1854_hoy.nc",
    )


def lluvia() -> None:
    print("Lluvia: CHIRPS, PISCO y GPCC (mensual, grilla)")
    bajar_iridl(
        f".UCSB/.CHIRPS/.v2p0/.monthly/.global/.precipitation/{CAJA}/T/(Jan%201981)/(last)/RANGEEDGES",
        CHIRPS / "chirps_mensual_1981_hoy_tumbes_ancash.nc",
    )
    bajar_iridl(
        f".SENAMHI/.HSR/.PISCO/.Prec/.v2p1/.stable/.monthly/.Prec/{CAJA}",
        PISCO / "pisco_v2p1_estable_mensual_1981_2016.nc",
    )
    bajar_iridl(
        f".SENAMHI/.HSR/.PISCO/.Prec/.v2p1/.unstable/.monthly/.Prec/{CAJA}",
        PISCO / "pisco_v2p1_inestable_mensual_reciente.nc",
    )
    bajar_iridl(
        f".WCRP/.GCOS/.GPCC/.FDP/.version2018/.0p25/.prcp/{CAJA}",
        GPCC / "gpcc_v2018_0p25_mensual_1891_2016.nc",
    )


def pisco_diario() -> None:
    d = PISCO / "pisco_diario"
    print("Lluvia: PISCO diario estable 1981-2016 (un archivo por año)")
    for anio in range(1981, 2017):
        bajar_iridl(
            f".SENAMHI/.HSR/.PISCO/.Prec/.v2p1/.stable/.daily/.Prec/{CAJA}/"
            f"T/(1%20Jan%20{anio})/(31%20Dec%20{anio})/RANGEEDGES",
            d / f"pisco_diario_{anio}.nc",
        )


def chirps_diario() -> None:
    d = CHIRPS / "chirps_diario_eventos"
    print("Lluvia: CHIRPS diario en ventanas de eventos (nov-may)")
    for nombre, (ini, fin) in VENTANAS_EVENTO.items():
        t = f"T/({ini.replace(' ', '%20')})/({fin.replace(' ', '%20')})/RANGEEDGES"
        bajar_iridl(
            f".UCSB/.CHIRPS/.v2p0/.daily-improved/.global/.0p05/.prcp/{CAJA}/{t}",
            d / f"chirps_diario_{nombre}.nc",
        )


def _glofas(puntos: dict[str, tuple[float, float]], carpeta: Path) -> None:
    """Caudal diario GloFAS (Open-Meteo) de enero a abril de cada año desde 1997,
    más el pronóstico vigente. Se limita a ene-abr por el límite gratuito de
    Open-Meteo (cada 2 semanas de datos por punto cuentan como una llamada).
    Open-Meteo devuelve solo nulos antes de 1997 (probado el 10-nov-2026), por eso
    no se pide 1984-1996 aunque la reanálisis GloFAS original sí lo cubre."""
    hoy = time.strftime("%Y-%m-%d")
    anio_actual = int(hoy[:4])
    for nombre, (la, lo) in puntos.items():
        for anio in range(1997, anio_actual + 1):
            fin = f"{anio}-04-30" if f"{anio}-04-30" < hoy else hoy
            if f"{anio}-01-01" > hoy:
                continue
            url = (
                "https://flood-api.open-meteo.com/v1/flood?"
                f"latitude={la}&longitude={lo}&daily=river_discharge"
                f"&start_date={anio}-01-01&end_date={fin}"
            )
            destino = carpeta / "historico" / nombre / f"{anio}.json"
            ya = destino.exists()
            bajar(url, destino, timeout=120)
            if not ya:
                time.sleep(1.0)
        url = (
            "https://flood-api.open-meteo.com/v1/flood?"
            f"latitude={la}&longitude={lo}&forecast_days=210"
            "&daily=river_discharge,river_discharge_mean,river_discharge_median,"
            "river_discharge_max,river_discharge_min,river_discharge_p25,river_discharge_p75"
        )
        bajar(url, carpeta / "pronostico" / f"{nombre}_pronostico_{hoy}.json", timeout=120)


def caudales() -> None:
    print("Caudales: GloFAS (Open-Meteo), ríos prioritarios")
    _glofas(RIOS_PRIORITARIOS, GLOFAS)


def caudales_resto() -> None:
    print("Caudales: GloFAS (Open-Meteo), resto de ríos")
    _glofas(RIOS_RESTO, GLOFAS)


def estaciones() -> None:
    d = GHCN
    print("Estaciones: GHCN-Daily (NOAA) en la costa norte")
    inv = d / "ghcnd-stations.txt"
    bajar("https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt", inv)
    elegidas = []
    for linea in inv.read_text().splitlines():
        sid, lat, lon = linea[0:11], float(linea[12:20]), float(linea[21:30])
        if sid.startswith("PE") and Y0 <= lat <= Y1 and X0 <= lon <= X1:
            elegidas.append(linea)
    (d / "estaciones_costa_norte.txt").write_text("\n".join(elegidas) + "\n")
    print(f"  {len(elegidas)} estaciones GHCN en la caja")
    for linea in elegidas:
        sid = linea[0:11]
        bajar(f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/{sid}.csv.gz",
              d / "ghcn" / f"{sid}.csv.gz")


def desastres() -> None:
    d = DESINVENTAR
    print("Desastres: DesInventar Perú (1970 en adelante, por distrito)")
    z = d / "DI_export_per.zip"
    if bajar("https://www.desinventar.net/DesInventar/download/DI_export_per.zip", z):
        destino = d / "DI_export_per"
        if not (destino / "DI_export_per.xml").exists():
            with zipfile.ZipFile(z) as zf:
                zf.extractall(destino)


def territorio() -> None:
    print("Territorio: distritos, provincias e indicadores sociales")
    gh = "https://raw.githubusercontent.com"
    bajar(f"{gh}/juaneladio/peru-geojson/master/peru_distrital_simple.geojson", LIMITES / "peru_distritos.geojson")
    bajar(f"{gh}/juaneladio/peru-geojson/master/peru_provincial_simple.geojson", LIMITES / "peru_provincias.geojson")
    bajar(f"{gh}/jmcastagnetto/ubigeo-peru-aumentado/main/ubigeo_distrito.csv", INDICADORES / "ubigeo_distrito_indicadores.csv")


def relieve() -> None:
    d = DEM / "teselas"
    print("Relieve: Copernicus DEM GLO-90 (90 m), teselas de 1 grado")
    for lat in range(4, 12):  # S04 ... S11
        for lon in range(77, 83):  # W077 ... W082
            n = f"Copernicus_DSM_COG_30_S{lat:02d}_00_W{lon:03d}_00_DEM"
            bajar(f"https://copernicus-dem-90m.s3.amazonaws.com/{n}/{n}.tif", d / f"{n}.tif")
    # El mosaico y las pendientes se calculan en 05_preparar_historicos.py con tifffile
    # (sin GDAL), así que aquí solo se bajan las teselas.


def rios() -> None:
    """HydroRIVERS recortado a la caja, guardado como GeoJSON. Usa pyshp (sin GDAL)."""
    import shapefile  # pyshp

    d = RIOS
    print("Ríos: HydroRIVERS v1.0 (Sudamérica), recortado a la costa norte")
    salida = d / "hydrorivers_costa_norte.geojson"
    if salida.exists():
        return
    z = d / "HydroRIVERS_v10_sa_shp.zip"
    if not bajar("https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_sa_shp.zip", z, timeout=900):
        return
    with zipfile.ZipFile(z) as zf:
        base = next(n for n in zf.namelist() if n.endswith(".shp"))[:-4]
        lector = shapefile.Reader(
            shp=zf.open(base + ".shp"), shx=zf.open(base + ".shx"), dbf=zf.open(base + ".dbf")
        )
        campos = [f[0] for f in lector.fields[1:]]
        feats = []
        for sr in lector.iterShapeRecords():
            bx = sr.shape.bbox
            if bx[2] < X0 or bx[0] > X1 or bx[3] < Y0 or bx[1] > Y1:
                continue
            feats.append({
                "type": "Feature",
                "properties": dict(zip(campos, sr.record)),
                "geometry": sr.shape.__geo_interface__,
            })
    salida.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    z.unlink()  # 95 MB; el recorte basta y el script lo puede volver a bajar
    print(f"  ok  {salida.relative_to(RAIZ)}  ({len(feats)} tramos de río)")


GRUPOS = {
    "enso": enso, "lluvia": lluvia, "pisco_diario": pisco_diario, "chirps_diario": chirps_diario,
    "caudales": caudales, "caudales_resto": caudales_resto, "estaciones": estaciones,
    "desastres": desastres, "territorio": territorio, "relieve": relieve, "rios": rios,
}
POR_DEFECTO = [g for g in GRUPOS if g != "caudales_resto"]  # el resto, otro día (límite diario)

if __name__ == "__main__":
    pedidos = sys.argv[1:] or POR_DEFECTO
    for g in pedidos:
        if g not in GRUPOS:
            sys.exit(f"Grupo desconocido: {g}. Opciones: {', '.join(GRUPOS)}")
    for g in pedidos:
        GRUPOS[g]()
    print("Listo.")
