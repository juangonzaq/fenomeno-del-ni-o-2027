# Copernicus DEM GLO-90: relieve a 90 m

**Qué es.** Modelo digital de superficie global a 3 segundos de arco (~90 m), en teselas de 1°×1°.

**De dónde.** https://copernicus-dem-90m.s3.amazonaws.com/ (registro de datos abiertos de AWS)

**Cómo se bajó.** `scripts/04_descargar_historicos.py relieve`.

**Fecha de descarga.** 10-11-2026

**Archivos**

- `teselas/Copernicus_DSM_COG_30_SXX_00_WXXX_00_DEM.tif`: 37 teselas (S04-S11 × W077-W082). Cada una se nombra por su esquina suroeste.

**Cómo citarla.** © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.

**Condiciones de uso.** Licencia libre de Copernicus DEM, con la atribución de arriba.

**A tener en cuenta**

- 11 teselas no existen porque son mar abierto (dan 404).
- Hay elevaciones negativas reales: la depresión de Bayóvar, en Sechura, está bajo el nivel del mar.

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
