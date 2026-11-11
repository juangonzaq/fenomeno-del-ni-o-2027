# GPCC Full Data v2018: lluvia de estaciones 1891-2016 (servicio meteorológico alemán)

**Qué es.** Grilla mensual de lluvia a 0,25° hecha solo con estaciones. Es la serie más larga disponible (incluye 1891, 1925 y 1983).

**De dónde.** https://iridl.ldeo.columbia.edu/SOURCES/.WCRP/.GCOS/.GPCC/.FDP/.version2018/.0p25/.prcp/ (vía IRI Data Library)

**Cómo se bajó.** `scripts/04_descargar_historicos.py lluvia`.

**Fecha de descarga.** 10-11-2026

**Archivos**

- `gpcc_v2018_0p25_mensual_1891_2016.nc`

**Cómo citarla.** Schneider, U. et al. GPCC Full Data Monthly Product Version 2018 at 0.25°. DOI: 10.5676/DWD_GPCC/FD_M_V2018_025.

**Condiciones de uso.** Libre uso con cita (Deutscher Wetterdienst).

**A tener en cuenta**

- Es muy gruesa para distritos: en la tabla limpia solo se usa por departamento.

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
