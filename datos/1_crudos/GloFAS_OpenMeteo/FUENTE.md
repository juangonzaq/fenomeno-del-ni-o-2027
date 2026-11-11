# GloFAS v4 vía Open-Meteo: caudales diarios y pronóstico

**Qué es.** Caudal simulado de 18 puntos de ríos de la costa norte: enero a abril de 1997 a 2026, más el pronóstico por ensamble a 210 días.

**De dónde.** https://flood-api.open-meteo.com/v1/flood

**Cómo se bajó.** `scripts/04_descargar_historicos.py caudales` y `caudales_resto`.

**Fecha de descarga.** 10-11-2026

**Archivos**

- `historico/<rio_punto>/<anio>.json`: caudal diario de enero a abril de cada año.
- `pronostico/<rio_punto>_pronostico_<fecha>.json`: pronóstico emitido ese día.

**Cómo citarla.** Open-Meteo Flood API, datos de GloFAS (Copernicus Emergency Management Service).

**Condiciones de uso.** Open-Meteo entrega los datos con licencia CC BY 4.0: hay que citar a Open-Meteo y a GloFAS.

**A tener en cuenta**

- Open-Meteo devuelve vacíos antes de 1997.
- El uso gratuito está limitado a 10 000 llamadas por día.
- Los últimos 3 días del pronóstico vienen vacíos.
- GloFAS acierta el orden de los años, pero no los valores (ver advertencia 2 del catálogo).

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
