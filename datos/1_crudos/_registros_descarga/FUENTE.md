# Registros de las descargas

**Qué es.** Salida en pantalla de las corridas de `04_descargar_historicos.py`, para saber qué se bajó, qué falló y cuándo.

**De dónde.** —

**Cómo se bajó.** `.venv/bin/python -u scripts/04_descargar_historicos.py | tee datos/1_crudos/_registros_descarga/04_$(date +%F).log`

**Fecha de descarga.** 10-11-2026

**Archivos**

- `caudales.log`, `resto.log`, `resto2.log`: corridas del 10-11-2026.
