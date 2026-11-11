# NOAA PSL: MEI v2 (índice multivariado ENSO)

**Qué es.** Índice bimestral que combina presión, viento, temperatura del mar y radiación en el Pacífico tropical, desde 1979.

**De dónde.** https://psl.noaa.gov/enso/mei/data/meiv2.data

**Cómo se bajó.** `scripts/04_descargar_historicos.py enso`.

**Fecha de descarga.** 10-11-2026

**Archivos**

- `psl_mei_v2.txt`: una fila por año, 12 bimestres (DJ, JF, ...); -999 = sin dato.

**Cómo citarla.** NOAA Physical Sciences Laboratory, Multivariate ENSO Index Version 2 (MEI.v2).

**Condiciones de uso.** Datos del gobierno de EE. UU., de libre uso; cita la fuente.

**A tener en cuenta**

- En la tabla limpia cada bimestre se asigna a su segundo mes (DJ → enero).

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
