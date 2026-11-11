# Límites de departamentos, provincias y distritos (INEI, vía peru-geojson)

**Qué es.** Polígonos simplificados de los límites políticos del Perú, con ubigeo.

**De dónde.** https://github.com/juaneladio/peru-geojson

**Cómo se bajó.** `scripts/01_descargar_clima.py` (departamentos) y `scripts/04_descargar_historicos.py territorio` (provincias y distritos).

**Fecha de descarga.** 29-10-2026 (departamentos) y 10-11-2026 (provincias y distritos)

**Archivos**

- `peru_departamentos.geojson`, `peru_provincias.geojson`, `peru_distritos.geojson`

**Cómo citarla.** juaneladio/peru-geojson (GitHub), basado en límites del INEI.

**Condiciones de uso.** Revisa la licencia del repositorio antes de publicar.

**A tener en cuenta**

- Dos distritos vienen sin geometría: Bellavista (Sullana, 200602) y Acopampa (020602). La limpieza los toma del mapa de DesInventar.
- El mapa limpio de los 364 distritos está en `2_limpios/territorio/distritos_costa_norte.geojson`.

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
