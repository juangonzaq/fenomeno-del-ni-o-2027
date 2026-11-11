# DesInventar Perú: desastres 1970-2015 por distrito

**Qué es.** Inventario de desastres armado sobre todo con prensa y reportes: 23 657 fichas en todo el Perú (5 388 en Tumbes, Piura, Lambayeque, La Libertad y Áncash). Es la única fuente con los Niños de 1972-73, 1982-83 y 1997-98 por distrito.

**De dónde.** https://www.desinventar.net/DesInventar/download/DI_export_per.zip

**Cómo se bajó.** `scripts/04_descargar_historicos.py desastres` (baja el zip y lo descomprime).

**Fecha de descarga.** 10-11-2026

**Archivos**

- `DI_export_per.zip`: el archivo original.
- `DI_export_per/DI_export_per.xml`: las fichas (tabla `<fichas>`).
- `DI_export_per/*_region.shp`: mapas de departamentos, provincias y distritos que usa DesInventar.

**Cómo citarla.** DesInventar Sendai, base de datos de Perú (desinventar.net).

**Condiciones de uso.** Base pública; cita la fuente.

**A tener en cuenta**

- `serial` se repite entre departamentos: la clave única es `uu_id`.
- Latitud y longitud vienen en 0 en el 99 % de las fichas.
- Registra muchos menos eventos que INDECI en los años que comparten (ver advertencia 6 del catálogo).

No edites estos archivos a mano: las correcciones van en los scripts de limpieza (`02` y `05`).
