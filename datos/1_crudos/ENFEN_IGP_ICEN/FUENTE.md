# ICEN: Índice Costero El Niño (ENFEN / IGP)

**Qué es.** Serie oficial mensual del ICEN desde 1950: media móvil de 3 meses de la anomalía de temperatura del mar en la región Niño 1+2. Define si hay El Niño Costero y su magnitud.

**De dónde.** http://met.igp.gob.pe/datos/ICEN.txt

**Cómo se bajó.** `scripts/01_descargar_clima.py`. Si ya existe, guarda la versión anterior en `versiones_anteriores/` antes de reemplazarla.

**Fecha de descarga.** 10-11-2026 (versión anterior: 29-10-2026)

**Archivos**

- `ICEN.txt`: la versión vigente (hasta set-2026). Columnas año, mes, ICEN; las líneas con `%` son comentarios.
- `versiones_anteriores/ICEN_descargado_2026-10-29.txt`: la que usó el modelo original (hasta ago-2026).

**Cómo citarla.** ENFEN (2024). Definición operacional de los eventos El Niño Costero y La Niña Costera en el Perú. Nota Técnica (referencia que trae el propio archivo).

**Condiciones de uso.** Dato oficial público; cita al ENFEN.

**A tener en cuenta**

- El ENFEN corrige los últimos meses en cada comunicado: por eso se guardan las versiones anteriores.
- Set-2026 = 4,50, ya en magnitud extraordinaria.

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
