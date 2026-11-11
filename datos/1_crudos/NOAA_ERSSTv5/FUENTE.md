# NOAA ERSST v5: temperatura del mar 1854-hoy (Pacífico tropical)

**Qué es.** Campo mensual de temperatura superficial del mar a 2° entre 120°E y 70°W, 20°S y 20°N. Sirve para reconstruir el ICEN antes de 1950.

**De dónde.** https://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCDC/.ERSST/.version5/.sst/ (vía IRI Data Library)

**Cómo se bajó.** `scripts/04_descargar_historicos.py enso`.

**Fecha de descarga.** 10-11-2026

**Archivos**

- `ersst5_pacifico_tropical_1854_hoy.nc`: NetCDF; tiempo en "months since 1960-01-01" (calendario de 360 días).

**Cómo citarla.** Huang, B. et al. (2017). Extended Reconstructed Sea Surface Temperature, Version 5 (ERSSTv5). Journal of Climate, 30, 8179-8205.

**Condiciones de uso.** Datos del gobierno de EE. UU., de libre uso; cita la fuente.

**A tener en cuenta**

- Antes de 1950 hay pocas mediciones y el ICEN reconstruido es poco confiable (ver advertencia 4 del catálogo).

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
