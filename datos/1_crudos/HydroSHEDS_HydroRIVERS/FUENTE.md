# HydroRIVERS v1.0: red de ríos (HydroSHEDS)

**Qué es.** Red de ríos de Sudamérica recortada a la caja de estudio, con el área de cuenca aportante de cada tramo (`UPLAND_SKM`).

**De dónde.** https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_sa_shp.zip

**Cómo se bajó.** `scripts/04_descargar_historicos.py rios` (baja el shapefile de Sudamérica, lo recorta y borra el zip de 95 MB).

**Fecha de descarga.** 10-11-2026

**Archivos**

- `hydrorivers_costa_norte.geojson`: el recorte.

**Cómo citarla.** Lehner, B. y Grill, G. (2013). Global river hydrography and network routing: baseline data and new approaches to study the world's large river systems. Hydrological Processes, 27(15), 2171-2186.

**Condiciones de uso.** Licencia de HydroSHEDS: uso libre con cita.

**A tener en cuenta**

- Este archivo ya es un recorte, no el original; el script lo vuelve a generar desde el zip.

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
