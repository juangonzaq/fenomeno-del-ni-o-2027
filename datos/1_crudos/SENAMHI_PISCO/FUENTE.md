# PISCO v2.1: lluvia de SENAMHI (estaciones + satélite)

**Qué es.** Grilla de lluvia del Perú a ~10 km que combina las estaciones de SENAMHI con CHIRPS. La versión estable (1981-2016) es la más confiable; la reciente (inestable) llega a hoy.

**De dónde.** https://iridl.ldeo.columbia.edu/SOURCES/.SENAMHI/.HSR/.PISCO/.Prec/.v2p1/ (vía IRI Data Library)

**Cómo se bajó.** `scripts/04_descargar_historicos.py lluvia pisco_diario`.

**Fecha de descarga.** 10-11-2026

**Archivos**

- `pisco_v2p1_estable_mensual_1981_2016.nc`: mensual estable.
- `pisco_v2p1_inestable_mensual_reciente.nc`: mensual inestable, 1981 a hoy.
- `pisco_diario/pisco_diario_AAAA.nc`: diaria estable, un archivo por año de 1981 a 2016.

**Cómo citarla.** Aybar, C. et al. (2020). Construction of a high-resolution gridded rainfall dataset for Peru from 1981 to the present day. Hydrological Sciences Journal, 65(5).

**Condiciones de uso.** Datos públicos de SENAMHI; cita la fuente.

**A tener en cuenta**

- En la versión inestable hay celdas de mar que solo traen dato en el último mes; la limpieza no las cuenta como tierra.

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
