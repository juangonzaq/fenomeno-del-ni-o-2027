# NOAA GHCN-Daily: lluvia diaria de estaciones

**Qué es.** Lluvia diaria de las 10 estaciones GHCN de la caja de estudio, casi todas en aeropuertos (Tumbes, Talara, Piura, Chiclayo, Trujillo, Chimbote...).

**De dónde.** https://www.ncei.noaa.gov/pub/data/ghcn/daily/ (`ghcnd-stations.txt` y `by_station/`)

**Cómo se bajó.** `scripts/04_descargar_historicos.py estaciones`.

**Fecha de descarga.** 10-11-2026

**Archivos**

- `ghcnd-stations.txt`: inventario mundial de estaciones.
- `estaciones_costa_norte.txt`: las 10 estaciones de la caja.
- `ghcn/<estacion>.csv.gz`: datos diarios (lluvia en décimas de mm).

**Cómo citarla.** Menne, M. J. et al. (2012). An overview of the Global Historical Climatology Network-Daily database. Journal of Atmospheric and Oceanic Technology, 29, 897-910.

**Condiciones de uso.** Datos del gobierno de EE. UU., de libre uso; cita la fuente.

**A tener en cuenta**

- 3 estaciones están fuera de los 5 departamentos (Chachapoyas, Cajamarca y Juanjuí).
- Hay 17 días con más de 200 mm; la limpieza los marca para revisar (por ejemplo, Talara el 11-05-1994 con 436 mm).

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
