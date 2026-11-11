# CHIRPS v2.0: lluvia satelital (UCSB Climate Hazards Center)

**Qué es.** Lluvia estimada por satélite y corregida con estaciones, a ~5 km, mensual y diaria.

**De dónde.** https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/ (vía IRI Data Library)

**Cómo se bajó.** `scripts/01_descargar_clima.py` (la grilla del modelo) y `scripts/04_descargar_historicos.py lluvia chirps_diario`.

**Fecha de descarga.** 29-10-2026 (`chirps_costa_norte_1991_hoy.nc`) y 10-11-2026 (el resto)

**Archivos**

- `chirps_costa_norte_1991_hoy.nc`: mensual desde 1991, Tumbes a La Libertad. Es la que usa el modelo.
- `chirps_mensual_1981_hoy_tumbes_ancash.nc`: mensual desde 1981, de Tumbes a Áncash.
- `chirps_diario_eventos/chirps_diario_AAAA_AA.nc`: diaria, de noviembre a mayo de 1982-83, 1997-98, 2015-16, 2016-17, 2022-23 y 2025-26.

**Cómo citarla.** Funk, C. et al. (2015). The climate hazards infrared precipitation with stations. Scientific Data, 2, 150066.

**Condiciones de uso.** Libre uso con cita.

**A tener en cuenta**

- El tiempo de los mensuales está en "months since 1960-01-01" y el de los diarios en **días julianos** (`julian_day`).
- **Subestima mucho las lluvias del Niño en el desierto costero de Piura** (ver advertencia 1 del catálogo).

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
