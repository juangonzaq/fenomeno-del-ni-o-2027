"""Descarga los datos de clima que usa el modelo en datos/1_crudos/<fuente>/.

- ICEN (Índice Costero El Niño), serie oficial del ENFEN publicada por el IGP.
- Lluvia mensual CHIRPS v2.0 para la costa norte, desde la IRI Data Library.
- Límites de departamentos del Perú (GeoJSON).

Si el ICEN ya existe, la versión anterior se guarda en
ENFEN_IGP_ICEN/versiones_anteriores/ antes de bajar la nueva (el ENFEN corrige
los últimos meses en cada comunicado).

La base de emergencias de INDECI no se descarga aquí: el portal de datos
abiertos bloquea las descargas automáticas. Bájala a mano desde
https://www.datosabiertos.gob.pe/dataset/emergencias-y-da%C3%B1os-nivel-nacional-por-departamento
y guárdala como datos/1_crudos/INDECI_SINPAD/BD_2003-2025_EMERGENCIAS.csv
"""
import shutil
import sys
import time
from pathlib import Path
from urllib.request import urlretrieve

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import CHIRPS, ICEN, INDECI, LIMITES  # noqa: E402

FUENTES = {
    ICEN / "ICEN.txt": "http://met.igp.gob.pe/datos/ICEN.txt",
    # Caja que cubre Tumbes, Piura, Lambayeque y La Libertad; desde 1991 para la normal 1991-2020
    CHIRPS / "chirps_costa_norte_1991_hoy.nc": (
        "https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.monthly/.global/.precipitation/"
        "X/-81.5/-76.8/RANGEEDGES/Y/-9.1/-3.3/RANGEEDGES/T/(Jan%201991)/(last)/RANGEEDGES/data.nc"
    ),
    LIMITES / "peru_departamentos.geojson": (
        "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_departamental_simple.geojson"
    ),
}

if __name__ == "__main__":
    for destino, url in FUENTES.items():
        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.name == "ICEN.txt" and destino.exists():
            copia = destino.parent / "versiones_anteriores" / f"ICEN_reemplazado_{time.strftime('%Y-%m-%d')}.txt"
            copia.parent.mkdir(exist_ok=True)
            shutil.copy2(destino, copia)
        print("Descargando", destino.relative_to(destino.parents[1]))
        urlretrieve(url, destino)
    if not (INDECI / "BD_2003-2025_EMERGENCIAS.csv").exists():
        print("Falta datos/1_crudos/INDECI_SINPAD/BD_2003-2025_EMERGENCIAS.csv: descárgala a mano (ver el inicio de este archivo).")
