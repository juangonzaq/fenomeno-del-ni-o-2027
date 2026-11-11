# INDECI: emergencias y daños 2003-2025 (SINPAD)

**Qué es.** Base nacional de emergencias registradas en el SINPAD: 142 139 registros con fecha, distrito (ubigeo), peligro y daños (personas, viviendas, colegios, cultivos, vías, ganado, ayuda entregada). Es la **variable objetivo** del modelo.

**De dónde.** https://www.datosabiertos.gob.pe/dataset/emergencias-y-da%C3%B1os-nivel-nacional-por-departamento (publicado el 26-08-2026)

**Cómo se bajó.** **A mano**: el portal bloquea las descargas automáticas.

**Fecha de descarga.** 29-10-2026

**Archivos**

- `BD_2003-2025_EMERGENCIAS.csv`: separado por `;`, codificación Latin-1, coma decimal.

**Cómo citarla.** INDECI, Emergencias y daños a nivel nacional, Plataforma Nacional de Datos Abiertos.

**Condiciones de uso.** Datos abiertos del Estado peruano. Revisa la licencia en la ficha del dataset antes de publicar.

**A tener en cuenta**

- Las fechas de 2003-2024 vienen como dd/mm/aaaa y las de 2025 como mm/dd/aa.
- Hasta 2018 se registraban centros educativos; desde 2019, aulas (otras columnas).
- La limpieza está en `scripts/02_preparar_panel.py` → `2_limpios/emergencias/indeci_emergencias_2003_2025.csv`.

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
