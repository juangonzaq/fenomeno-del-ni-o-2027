# Catálogo de datos

Todo lo que usa el proyecto está en dos carpetas:

```
datos/
  1_crudos/    CARPETA 1: archivos tal como se descargaron, una subcarpeta por fuente.
               Cada subcarpeta tiene un FUENTE.md (origen, URL, fecha, cita y advertencias).
               No se editan a mano.
  2_limpios/   CARPETA 2: tablas limpias y listas para el modelo, una subcarpeta por tema.
               Se pueden borrar y volver a generar con los scripts.
  CATALOGO_DATOS.md   este archivo
```

Las rutas de todas las carpetas están en un solo lugar: `scripts/rutas.py`.

## Carpeta 1: `1_crudos/` (por fuente)

| Carpeta | Qué tiene | La baja | La limpia |
|---|---|---|---|
| `INDECI_SINPAD/` | Emergencias y daños 2003-2025 (variable objetivo) | a mano | `02` |
| `DesInventar/` | Desastres 1970-2015 por distrito | `04 desastres` | `05 desinventar` |
| `ENFEN_IGP_ICEN/` | ICEN oficial 1950-hoy y sus versiones anteriores | `01` | `02`, `05 enso` |
| `NOAA_CPC_indices/` | ONI, RONI, SOI y anomalías Niño 1+2, 3, 4, 3.4 | `04 enso` | `05 enso` |
| `NOAA_PSL_MEI/` | MEI v2 | `04 enso` | `05 enso` |
| `NOAA_ERSSTv5/` | Temperatura del mar 1854-hoy (para reconstruir el ICEN) | `04 enso` | `05 enso` |
| `UCSB_CHIRPS/` | Lluvia satelital mensual (1981-hoy) y diaria (ventanas de Niños) | `01`, `04 lluvia chirps_diario` | `02`, `05` |
| `SENAMHI_PISCO/` | Lluvia SENAMHI mensual (1981-hoy) y diaria (1981-2016) | `04 lluvia pisco_diario` | `05` |
| `DWD_GPCC/` | Lluvia de estaciones 1891-2016 | `04 lluvia` | `05 lluvia` |
| `NOAA_GHCN_estaciones/` | Lluvia diaria de 10 estaciones | `04 estaciones` | `05 estaciones` |
| `GloFAS_OpenMeteo/` | Caudales ene-abr 1997-2026 y pronóstico a 210 días | `04 caudales caudales_resto` | `05 caudales` |
| `INEI_limites_geojson/` | Límites de departamentos, provincias y distritos | `01`, `04 territorio` | `02`, `05` |
| `Indicadores_distritales/` | Población, pobreza, IDH por distrito | `04 territorio` | `05 territorio` |
| `Copernicus_DEM_GLO90/` | Relieve a 90 m (37 teselas) | `04 relieve` | `05 territorio` |
| `HydroSHEDS_HydroRIVERS/` | Red de ríos recortada | `04 rios` | `05 territorio` |
| `Compilado_manual/` | Impactos de Niños y caudales del río Piura, copiados de informes | a mano | `05 compilados` |
| `_registros_descarga/` | Logs de las descargas | — | — |

## Carpeta 2: `2_limpios/` (por tema)

| Carpeta | Tablas | Las arma |
|---|---|---|
| `emergencias/` | INDECI limpia, DesInventar (fichas, por departamento y mes, por distrito y año), INDECI por distrito y año, impactos compilados | `02`, `05` |
| `enso/` | Índices ENSO mensuales desde 1854 y lista de eventos El Niño Costero | `05` |
| `lluvia/` | Lluvia por departamento, distrito y estación; intensidad diaria | `02`, `05` |
| `caudales/` | Caudales GloFAS (diario, mensual, pronóstico) y picos medidos del río Piura | `05` |
| `territorio/` | Atributos de los 364 distritos y su mapa (GeoJSON) | `05` |
| `modelo/` | `panel_costa_norte_2003_2025.csv` (departamento × mes, la que usa `03_modelo.py`) y `panel_distrito_temporada_1970_2025.csv` (distrito × temporada, para el mapa de riesgo) | `02`, `07` |
| `escenarios/` | `icen_2027_supuesto.csv`: tu supuesto editable de ICEN para 2027 | a mano |
| `_calidad/` | `reporte_calidad.md`: filas, periodo, claves, vacíos y negativos de cada tabla | `06` |

## Cómo regenerarlo

```bash
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/01_descargar_clima.py        # ICEN, CHIRPS del modelo y departamentos
.venv/bin/python scripts/04_descargar_historicos.py   # el resto (~600 MB, 15-30 min)
.venv/bin/python scripts/02_preparar_panel.py         # INDECI limpia y tabla del modelo
.venv/bin/python scripts/05_preparar_historicos.py    # todas las demás tablas limpias (~40 s)
.venv/bin/python scripts/07_panel_distrito_temporada.py  # tabla distrito × temporada
.venv/bin/python scripts/06_validar_datos.py          # reporte de calidad
.venv/bin/python scripts/03_modelo.py                 # el modelo
```

- **Orden:** `05` usa la base limpia de INDECI que arma `02`, y `07` usa las tablas de `02` y `05`.
- **Volver a correr:** `04` salta lo que ya existe y completa lo que falló.
- **Caudales:** el grupo `caudales_resto` no se baja por defecto porque Open-Meteo limita el uso gratuito a 10 000 llamadas por día. Ya está bajado: si borras los datos, córrelo aparte (`04_descargar_historicos.py caudales_resto`), idealmente otro día.
- **Relieve:** las 11 teselas de relieve que dan 404 son de mar abierto y no existen.
- **Sin GDAL:** los scripts no usan GDAL porque la instalación de Homebrew de esta Mac está rota (le falta `libOpenEXR`). Leen los GeoTIFF con `tifffile` e `imagecodecs`, y los shapefiles con `pyshp`.

---

## Reglas de limpieza (qué se corrigió y por qué)

Nada se corrige en los archivos crudos: todo lo hacen `02_preparar_panel.py` y `05_preparar_historicos.py`, y se puede revisar ahí.

| Fuente | Problema encontrado | Qué se hizo |
|---|---|---|
| INDECI | Fechas en dos formatos (dd/mm/aaaa hasta 2024, mm/dd/aa en 2025) | Se leen por separado y se comprueba que coincidan con AÑO y MES en las 142 139 filas |
| INDECI | Coma decimal, nombres de columna con espacios y tildes | Números con punto; columnas en `snake_case` |
| INDECI | 1 costo de ayuda negativo (código 5420, 2004) | Queda vacío |
| INDECI | 7 códigos SINPAD aparecen dos veces con fecha, lugar o peligro distintos | No se borran (parecen emergencias distintas): `codigo_sinpad_repetido` = verdadero |
| INDECI | Colegios: centros educativos hasta 2018, aulas desde 2019 | Columnas separadas con el periodo en el nombre; vacío = no se registraba |
| INDECI | 2 distritos que no están en el mapa: Veintiséis de Octubre (200115, creado en 2013, registrado desde 2015) y Alto Trujillo (130112, 2021), 212 registros | `ubigeo_mapa` los suma al distrito del que se separaron (Piura 200101 y El Porvenir 130102), como se registraban antes. Las tablas por distrito usan `ubigeo_mapa` |
| DesInventar | `serial` se repite entre departamentos | La clave es `id_desinventar` (el `uu_id` del XML) |
| DesInventar | Latitud/longitud en 0 en el 99 % de las fichas | Vacío |
| DesInventar | 7 fichas con mes 0 y 146 con día 0 | Vacío; `fecha` solo cuando hay año, mes y día |
| DesInventar | 671 fichas sin distrito (415 solo con provincia, 256 solo con departamento) | `nivel_geografico`; cuentan en el panel por departamento, no en la tabla por distrito |
| DesInventar | La tabla por distrito y año repetía claves (filas sin distrito) | Se agrupa solo por `ubigeo` + `anio` y los nombres se toman del mapa |
| DesInventar | Campo `glide` vacío en todas las fichas | No se incluye |
| Lluvia (PISCO) | Corrales (Tumbes, 240102) solo tiene celdas de mar, y el PISCO reciente trae dato en el mar solo en el último mes | Una celda cuenta si tiene dato en al menos la mitad de los meses; si el distrito no tiene ninguna, se usa la más cercana |
| CHIRPS diario | El tiempo viene en días julianos, no en "días desde 1960" | Se lee la unidad de cada archivo. **Antes de esta limpieza las fechas de las tablas diarias de CHIRPS salían en el año 8654** |
| GloFAS | Los últimos 3 días del pronóstico (5 al 7 de junio de 2027) vienen vacíos | Se quitan (54 filas) |
| GHCN | 17 días con más de 200 mm, algunos dudosos (Talara, 11-05-1994: 436 mm) | No se borran: `revisar_mayor_200mm` = verdadero |
| GHCN | 3 estaciones fuera de los 5 departamentos | `dentro_area_estudio` y `ubigeo` de la estación |
| Distritos | Bellavista (200602) y Acopampa (020602) sin polígono en el GeoJSON | Se toman del mapa de DesInventar (`geometria_fuente`) |
| Distritos | La Unión (200110) trae la provincia escrita "PUIRA" en el GeoJSON del INEI | Se corrige a PIURA en `05_preparar_historicos.py` (`PROVINCIA_CORREGIDA`) |

---

## Tablas limpias

### `emergencias/`

| Archivo | Una fila es | Periodo | Contenido |
|---|---|---|---|
| `indeci_emergencias_2003_2025.csv` | una emergencia (todo el Perú) | 2003-01 a 2025-12 | `codigo_sinpad`, `fecha`, `anio`, `mes_num`, `ubigeo`, `ubigeo_mapa`, `departamento`, `provincia`, `distrito`, `peligro`, `es_peligro_lluvias`, `tipo_peligro`, `region_natural` y 38 columnas numéricas de daños y ayuda: personas (`fallecidos`, `damnificados`, `afectados`...), viviendas, colegios, centros de salud, cultivos (ha), puentes, carreteras y caminos (km), canales, ganado, y `ayuda_peso` y `ayuda_costo` (INDECI no indica las unidades; probablemente kg y soles). Al final, `codigo_sinpad_repetido` |
| `desinventar_fichas_costa_norte.csv` | una ficha | 1970-2015 | 5 388 fichas de los 5 departamentos, de todos los tipos. `id_desinventar`, `serial`, ubicación y `nivel_geografico`, `evento`, `lugar`, `anio`, `mes_num`, `dia`, `fecha`, `fallecidos`, `desaparecidos`, `heridos`, `afectados`, `damnificados`, `evacuados`, `reubicados`, `viviendas_destruidas`, `viviendas_afectadas`, `ha_cultivos_bosques`, `vias_km`, `centros_educativos`, `centros_salud`, `perdidas_moneda_local`, `perdidas_usd`, `causa`, `descripcion_causa`, `duracion_dias`, `fuentes`, `lat`, `lon`, y las marcas `hidrometeorologico` y `causa_el_nino` |
| `desinventar_panel_departamento_mes.csv` | departamento × mes | 1970-01 a 2015-12 | Solo eventos por lluvias: `fichas`, `fichas_con_damnificados`, `fallecidos`, `damnificados`, `afectados`, `viviendas_destruidas`, `viviendas_afectadas`, `ha_cultivos_bosques`. Los meses sin registro van con 0 |
| `desinventar_distrito_anio.csv` | distrito × año con registros | 1970-2015 | Lo mismo, por distrito. Solo fichas registradas a nivel distrito |
| `indeci_distrito_anio_lluvias.csv` | distrito × año con registros | 2003-2025 | Desde la base INDECI limpia (por `ubigeo_mapa`), con el mismo filtro de peligros que el modelo: `emergencias_lluvias`, `emerg_con_damnificados`, `damnificados` |
| `impactos_eventos_nino_compilados.csv` | una cifra publicada | 1982-83, 1997-98, 2017, 2023 | Impactos nacionales, por departamento y por ciudad, cada uno con su fuente y URL. Las cifras que se contradicen van en filas separadas, con una nota |

"Por lluvias" en DesInventar significa: Inundación, Lluvias, Aluvión (Huayco), Avenida torrencial, Deslizamiento, Derrumbe y Erosión. Es equivalente al filtro de INDECI (lluvia intensa, inundación, huayco, deslizamiento, derrumbe de cerro y erosión) y **no** incluye marejadas.

**Años con más damnificados por lluvias (5 departamentos, DesInventar):**

| Año | Damnificados | Fichas |
|---|---|---|
| 1983 | 204 104 | 576 |
| 1998 | 145 002 | 310 |
| 1992 | 62 613 | 22 |
| 2001 | 19 353 | 85 |
| 1994 | 16 899 | 111 |
| 1997 | 12 270 | 125 |
| 1972 | 7 070 | 249 |

### `enso/`

| Archivo | Una fila es | Periodo | Contenido |
|---|---|---|---|
| `enso_mensual_1854_hoy.csv` | un mes | 1854-01 a 2026-10 | `icen`: oficial donde existe y reconstruido antes. `icen_fuente`, `icen_oficial`, `icen_reconstruido`. Anomalías ERSSTv5 propias de Niño 1+2 y 3.4. Anomalías de NOAA CPC para Niño 1+2, 3, 4 y 3.4. `oni`, `roni`, `soi` (estandarizado) y `mei_v2` |
| `enso_eventos_nino_costero.csv` | un evento | 1854 a hoy | Evento = ICEN ≥ 0,4 durante 3 meses o más. Incluye inicio, fin, número de meses, `icen_max`, mes del pico, `magnitud` y si sigue `en_curso` |

**Cómo se reconstruyó el ICEN.** Es la media móvil centrada de 3 meses de la anomalía de TSM ERSSTv5 en la caja Niño 1+2 (0-10°S, 90-80°W), ponderada por coseno de la latitud, con climatología 1981-2010. Reproduce el ICEN oficial de 1950-2026 con r = 0,97 y RMSE = 0,33 °C.

**Eventos fuertes y extraordinarios que salen:**

| Evento | ICEN máximo | Magnitud |
|---|---|---|
| 1877-78 | 3,67 | extraordinario |
| 1972-73 | 2,45 | fuerte |
| 1982-83 | 4,32 | extraordinario |
| 1997-98 | 4,08 | extraordinario |
| 2015-16 | 2,23 | fuerte |
| 2023 | 2,92 | fuerte |
| **2026 (en curso)** | **4,50 en set-2026** | **extraordinario** |

2017 sale "moderado" (1,31), igual que en el ENFEN.

### `lluvia/`

| Archivo | Una fila es | Periodo | Contenido |
|---|---|---|---|
| `lluvia_chirps_anomalia_departamento.csv` | departamento × mes (4 dptos) | 1991-01 a 2026-09 | La lluvia CHIRPS que usa el modelo: `lluvia_mm`, `lluvia_normal_mm` (1991-2020), `lluvia_anomalia_mm`, `lluvia_pct_normal` |
| `lluvia_mensual_departamento.csv` | departamento × mes (5 dptos) | 1891-01 a 2026-10 | `lluvia_gpcc_mm` (1891-2016), `lluvia_pisco_estable_mm` (1981-2016), `lluvia_pisco_reciente_mm` (1981-2026), `lluvia_chirps_mm` (1981-2026) |
| `lluvia_mensual_distrito.csv` | distrito × mes (364 distritos) | 1981-01 a 2026-10 | Las mismas tres series PISCO/CHIRPS promediadas por distrito |
| `lluvia_intensidad_pisco_distrito_mes.csv` | distrito × mes | 1981-2016 | Lluvia total, máximo diario (media del distrito y celda más lluviosa), días ≥ 10 y ≥ 20 mm, y máximo acumulado en 3 días, todo desde PISCO diario |
| `lluvia_intensidad_chirps_eventos_distrito_mes.csv` | distrito × mes | nov-may de 1982-83, 1997-98, 2015-16, 2016-17 y 2022-23; nov-2025 a set-2026 | Lo mismo, desde CHIRPS diario |
| `lluvia_diaria_chirps_eventos_distrito.csv` | distrito × día | las mismas ventanas | Serie diaria por distrito, para ver el desarrollo de cada evento |
| `estaciones_ghcn_lluvia_diaria.csv` | estación × día | 1973 a 2025 (varía) | Lluvia diaria de 10 estaciones GHCN, sin datos marcados por control de calidad, y `revisar_mayor_200mm` |
| `estaciones_ghcn_resumen.csv` | estación | | Nombre, coordenadas, `ubigeo` y `dentro_area_estudio`, cobertura, días para revisar y días con dato en 1983, 1998, 2017 y 2023 |

### `caudales/`

| Archivo | Una fila es | Periodo | Contenido |
|---|---|---|---|
| `caudales_glofas_diario.csv` | punto de río × día | **ene-abr** de 1997 a 2026 | Caudal simulado en m³/s |
| `caudales_glofas_mensual.csv` | punto × mes | ídem | Caudal medio y máximo |
| `caudales_glofas_puntos.csv` | punto | | Celda GloFAS usada (lat, lon) |
| `caudales_glofas_pronostico.csv` | punto × día | 10-nov-2026 al 4-jun-2027 | Pronóstico por ensamble: media, mediana, mínimo, máximo, p25 y p75 |
| `caudales_pico_rio_piura_observados.csv` | una medición publicada | 1983-2023 | Picos medidos del río Piura y capacidad del cauce urbano (~1900 m³/s), con fuente |

**Puntos prioritarios:** Tumbes (El Tigre), Zarumilla, Chira (Ardilla y Sullana), Piura (Tambogrande y bajo Piura), La Leche (Íllimo), Chancay-Lambayeque (Racarrumi), Jequetepeque, Santa (Condorcerro) y Huarmey.

**Puntos adicionales** (grupo `caudales_resto`): Motupe, Zaña, Chicama, Moche, Virú, Nepeña y Casma.

### `territorio/`

`distritos_costa_norte_atributos.csv` tiene una fila por distrito (364 distritos), sin vacíos:

| Grupo | Columnas | Fuente |
|---|---|---|
| Identificación | `ubigeo`, `distrito`, `provincia`, `departamento`, `geometria_fuente`, `capital`, `lat_centroide`, `lon_centroide` | Límites INEI (juaneladio/peru-geojson) |
| Social | `superficie_km2`, `pob_densidad_2020`, `poblacion_2020_estimada` (densidad × superficie), `idh_2019`, `pct_pobreza_total`, `pct_pobreza_extrema`, `indice_vulnerabilidad_alimentaria` | jmcastagnetto/ubigeo-peru-aumentado (compila INEI, PNUD y MIDIS) |
| Relieve | `elev_media_m`, `elev_min_m`, `elev_p10_m`, `pct_area_bajo_50m`, `pct_area_bajo_200m`, `pendiente_media_grados`, `pct_area_pendiente_menor_2` | Copernicus DEM GLO-90, remuestreado a ~270 m |
| Ríos | `dist_centroide_a_rio_mayor_km` (río con cuenca ≥ 1000 km²), `cuenca_max_que_cruza_km2` | HydroRIVERS v1.0 |
| Historial | `desinventar_fichas_lluvias_1970_2015`, `desinventar_damnificados_1983`, `desinventar_damnificados_1998`, `indeci_emergencias_lluvias_2003_2025`, `indeci_emerg_con_damnificados_2003_2025`, `indeci_damnificados_2017`, `indeci_damnificados_2023` | DesInventar e INDECI |

`distritos_costa_norte.geojson` es el mapa de esos 364 distritos (`ubigeo`, `distrito`, `provincia`, `departamento`), para dibujar resultados del modelo o subirlo a Google Earth Engine (`scripts/gee_inundaciones_sentinel1.js`).

### `modelo/`

`panel_costa_norte_2003_2025.csv`: departamento × mes, 4 departamentos × 276 meses = 1104 filas, sin vacíos. Columnas:
- **Identificación:** `departamento`, `mes`, `anio`, `mes_num`.
- **Conteos y daños por lluvias (INDECI):** `emergencias`, `emerg_con_damnificados` (la variable objetivo), `fallecidos`, `damnificados`, `afectados`, `viviendas_destruidas`, `viviendas_afectadas`, `ha_cultivo_destruido`, `ha_cultivo_afectado`.
- **ICEN:** `icen`, `icen_lag1`, `icen_lag2`, `icen_condicion`.
- **Lluvia CHIRPS:** `lluvia_mm`, `lluvia_normal_mm`, `lluvia_anomalia_mm`, `lluvia_pct_normal`.

`panel_distrito_temporada_1970_2025.csv`: un distrito (364) en la temporada de lluvias de un año
(enero a mayo), de 1970 a 2025: 20 384 filas × 50 columnas. Es la tabla para modelar **dónde** habrá
emergencias (clasificación, mapa de riesgo). La arma `07_panel_distrito_temporada.py`.

El sufijo de cada columna dice **cuándo se conoce**, que es lo que importa para validar sin hacer trampa:

| Grupo | Cuándo se conoce | Columnas |
|---|---|---|
| Identificación | — | `ubigeo`, `distrito`, `provincia`, `departamento`, `anio` (la temporada es enero-mayo de ese año), `fuente_objetivo` (DesInventar hasta 2002, INDECI desde 2003) |
| Variable objetivo | después de la temporada | `tuvo_damnificados` (0/1, la principal), `emergencias_lluvias`, `emerg_con_damnificados`, `damnificados`, `fallecidos`, `viviendas_destruidas` |
| Historial `hist_*` | antes | `hist_tuvo_damnificados_temporada_anterior`, `hist_temporadas_con_damnificados`, `hist_pct_temporadas_con_damnificados`: solo temporadas anteriores, nunca la del año |
| Océano `*_previo` | antes (hasta noviembre del año anterior) | `icen_nov_previo`, `icen_max_jun_nov_previo`, `icen_cambio_ago_nov_previo`, `nino34_anom_nov_previo` |
| Lluvia previa | antes | `lluvia_nov_dic_previo_pisco_reciente_mm` (desde 1982) |
| Océano `*_ene_may` | durante: solo como escenario | `icen_max_ene_may`, `icen_medio_ene_may` |
| Lluvia `*_ene_may` | durante: solo como escenario | `lluvia_ene_may_pisco_reciente_mm`, `lluvia_ene_may_chirps_mm` (1981-2025), sus versiones `_relativa` = log((lluvia + 10) / (normal 1991-2020 + 10)), `lluvia_mes_max_ene_may_pisco_reciente_mm`, `lluvia_ene_may_pisco_estable_mm`, `lluvia_max_diaria_ene_may_pisco_mm`, `dias_mayor_20mm_ene_may_pisco`, `max_acum_3dias_ene_may_pisco_mm` (estas cuatro, 1981-2016) |
| Atributos fijos | siempre | relieve, ríos, población, pobreza, IDH y centroide, de `distritos_costa_norte_atributos.csv` (sin sus columnas de historial, que mirarían el futuro) |

Comprobado: de 2003 a 2025 los conteos por distrito suman exactamente lo mismo que el panel por
departamento. De 1970 a 2002, el 89 % de las fichas de enero-mayo tienen distrito; el resto
(registradas solo por provincia o departamento) no entra.

---

## Advertencias de calidad (léelas antes de modelar)

1. **La lluvia satelital no ve los aguaceros del Niño en la costa desértica.** En marzo de 2017 la estación del aeropuerto de Piura (GHCN PEM00084401) midió **567,5 mm**. En esa celda, CHIRPS da ~20 mm y PISCO reciente ~25 mm. En marzo de 1983, para el departamento de Piura, CHIRPS da 157 mm, PISCO estable 441 mm y GPCC 398 mm. Por eso:
   - para 1981-2016 conviene usar **PISCO estable** (combina estaciones);
   - para 2017 en adelante en la costa, las **estaciones**;
   - la variable "lluvia relativa" del modelo B actual, hecha con CHIRPS, probablemente subestima 2017 y 2023 en Piura.
2. **GloFAS acierta el orden de los años en el río Piura, pero no los valores.** Picos de enero-abril en el punto del bajo Piura, comparados con lo medido:

   | Año | GloFAS (m³/s) | Medido (m³/s) | Diferencia |
   |---|---|---|---|
   | 1998 | 4570 | 3900-4400 | dentro del rango |
   | 2017 | 2581 | 3468 | ~25 % menos |
   | 2023 | 1204 | ~1700 | ~30 % menos |

   Sirve como variable relativa (qué año fue peor), no como caudal absoluto. Además, Open-Meteo solo tiene datos desde 1997 (antes devuelve vacíos) y aquí solo se bajó enero-abril de cada año.

   **Pronóstico del 10-nov-2026 (hasta el 4-jun-2027), río Piura en Tambogrande y bajo Piura:**
   - la mediana del ensamble llega a ~570 m³/s;
   - el percentil 75 a ~850 m³/s;
   - el miembro más extremo a ~2600 m³/s, por encima de los ~1900 m³/s que soporta el cauce urbano.

   Por la subestimación de la tabla, los valores reales podrían ser mayores. Es un pronóstico estacional, así que conviene volver a bajarlo cada mes (`04_descargar_historicos.py caudales` vuelve a pedir el pronóstico si cambió la fecha).
3. **La red de ríos de GloFAS está algo corrida.** El punto "bajo Piura" quedó en (-5.275, -80.725), unos 11 km al suroeste del puente Sánchez Cerro. Cada punto se ajustó tomando la celda de mayor caudal en un radio de ~10 km.
4. **El ICEN reconstruido antes de 1950 es poco confiable**, porque había pocas mediciones de barcos. No detecta el Niño costero de 1925, que fue fuerte y está bien documentado en Piura. Úsalo solo como referencia.
5. **Los umbrales de magnitud del ICEN son los clásicos del ENFEN 2012:** débil 0,4, moderado 1,0, fuerte 1,7 y extraordinario 3,0. La Nota Técnica ENFEN 2024 podría haberlos cambiado y no se pudo verificar. Están en `UMBRALES_ICEN`, al inicio de `05_preparar_historicos.py`.
6. **DesInventar no mide lo mismo que INDECI, y se queda corto.** Se basa sobre todo en prensa y reportes.
   - **2003-2015, los años que comparten:** DesInventar tiene entre 5 y 20 veces menos registros que INDECI en los 5 departamentos, y los damnificados anuales de ambos no se correlacionan (r = −0,02).
   - **1997-98, contra las cifras oficiales de INDECI:** Piura 22 411 frente a ~120 000 (≈19 %), Lambayeque 28 309 frente a 71 756 (≈39 %) y La Libertad 43 812 frente a 72 306 (≈61 %).
   - **Cómo usarlo:** sirve para saber **dónde y cuándo** hubo daño, por ejemplo una variable binaria "el distrito tuvo damnificados en la temporada". No sirve para comparar magnitudes con INDECI. Para un panel de 1970 a 2025, usa DesInventar hasta 2002 e INDECI desde 2003, agrega una variable indicadora de la fuente y no sumes los años que se traslapan.
7. **El número de emergencias no es lo mismo que el daño.** Por conteo de emergencias de INDECI dominan distritos andinos (Independencia, Ayabaca, Huaraz), que registran muchos eventos chicos. Por damnificados y por 1983/1998 dominan los de la llanura costera (Tumbes, Tambogrande, Chulucanas, Piura, Castilla).
8. **GHCN tiene pocas estaciones.** Son 10 en la caja, y 3 de ellas están fuera de los 5 departamentos (Chachapoyas, Cajamarca y Juanjuí): filtra con `dentro_area_estudio`. La de Chimbote termina en 2003.
9. **Los índices no llegan todos al mismo mes.** Al 10-nov-2026: ICEN oficial hasta set-2026, CPC mensual hasta jun-2026, SOI hasta dic-2025, CHIRPS hasta set-2026 y PISCO reciente hasta oct-2026.
10. **El ICEN ya superó tu supuesto para 2027.** El ICEN oficial de setiembre de 2026 es **4,50**, mientras que `2_limpios/escenarios/icen_2027_supuesto.csv` empieza en 3,5 en diciembre. Conviene revisarlo cuando pases a modelar.
11. **En la tabla distrito × temporada, la variable objetivo cambia de escala con la fuente.** Con DesInventar (1970-2002) solo el 2,2 % de las filas tiene damnificados (8,5 % en 1983 y 15,4 % en 1998). Con INDECI (2003-2025) es el 19,1 %, con 66 % en 2017, 75 % en 2023 y 58 % en 2025, un año con ICEN de apenas 0,72. Ese salto viene de cómo registra cada fuente y del aumento del registro de INDECI, no del clima. Por eso:
    - incluye `fuente_objetivo` (o el año) como variable, para que el modelo no le atribuya ese salto al ICEN;
    - valida sobre todo con años de INDECI (por ejemplo, entrena sin 2017 y predice 2017);
    - usa 1983 y 1998 para que el modelo vea cómo responde a un ICEN extremo, no para comparar magnitudes.

## Lo que no se pudo bajar automáticamente (y cómo conseguirlo)

| Dato | Dónde | Por qué falta |
|---|---|---|
| Estaciones SENAMHI (lluvia diaria y caudales observados de Piura, Chira, Tumbes...) | senamhi.gob.pe, "Descarga de datos hidrometeorológicos" | Hay que descargar a mano, estación por estación |
| Caudales observados ANA | snirh.ana.gob.pe | Portal interactivo |
| Mapas de inundación 2017 (Copernicus EMSR199) y 2023 (International Charter 811, UNOSAT) | rapidmapping.emergency.copernicus.eu, disasterscharter.org, unosat.org | La API pide credenciales. **Alternativa:** `scripts/gee_inundaciones_sentinel1.js` mapea la inundación con Sentinel-1 en Google Earth Engine y exporta hectáreas inundadas por distrito |
| Capas de CENEPRED (escenarios de riesgo, 209 distritos "muy alto") | sigrid.cenepred.gob.pe | Para descargar capas hay que registrarse como usuario |
| EM-DAT (desastres globales) | emdat.be | Requiere cuenta gratuita |
| ERA5 y GloFAS 1984-1996 completos | Copernicus CDS / EWDS | Requiere cuenta y clave de API |
| Censo 2025 por distrito | inei.gob.pe | Se publica por etapas desde julio de 2026 |

Si consigues alguno, guárdalo en una carpeta nueva de `1_crudos/` con su `FUENTE.md` y agrega su ruta en `scripts/rutas.py`.
