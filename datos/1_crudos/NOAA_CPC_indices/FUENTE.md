# NOAA CPC: índices ENSO (ONI, RONI, SOI, Niño 1+2, 3, 4 y 3.4)

**Qué es.** Índices oficiales de NOAA para el Pacífico central y el lejano (ONI, RONI, SOI) y anomalías mensuales y semanales por región Niño.

**De dónde.** https://www.cpc.ncep.noaa.gov/data/indices/ (`oni.ascii.txt`, `RONI.ascii.txt`, `soi`, `ersst5.nino.mth.91-20.ascii`, `wksst9120.for`)

**Cómo se bajó.** `scripts/04_descargar_historicos.py enso`.

**Fecha de descarga.** 10-11-2026

**Archivos**

- `cpc_oni.txt`, `cpc_roni.txt`: trimestres móviles desde 1950.
- `cpc_soi.txt`: índice de oscilación del sur (se usa la tabla estandarizada).
- `cpc_ersst5_nino_mensual_1950_hoy.txt`: temperatura y anomalía mensual por región Niño (climatología 1991-2020).
- `cpc_oisst_nino_semanal_1990_hoy.txt`: lo mismo, semanal (no se usa todavía).

**Cómo citarla.** NOAA Climate Prediction Center.

**Condiciones de uso.** Datos del gobierno de EE. UU., de libre uso; cita la fuente.

**A tener en cuenta**

- Al 10-11-2026 el archivo mensual llega a jun-2026 y el SOI a dic-2025.

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
