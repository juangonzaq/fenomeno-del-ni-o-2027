# Reporte de calidad de `datos/2_limpios/`

Generado por `scripts/06_validar_datos.py` el 2026-11-10 20:30.

**Resultado:** todas las comprobaciones pasaron.


## Resumen por tabla

| Tabla | Filas | Col. | Periodo | Clave | % vacío máx. | Estado |
|---|---:|---:|---|:---:|---:|:---:|
| `emergencias/indeci_emergencias_2003_2025.csv` | 142,139 | 52 | 2003-01-01 a 2025-12-31 | — | 64.26 | ok |
| `emergencias/desinventar_fichas_costa_norte.csv` | 5,388 | 36 | 1970-01-05 a 2015-12-30 | ok | 99.22 | ok |
| `emergencias/desinventar_panel_departamento_mes.csv` | 2,760 | 12 | 1970-01 a 2015-12 | ok | 0 | ok |
| `emergencias/desinventar_distrito_anio.csv` | 1,414 | 13 | 1970 a 2015 | ok | 0 | ok |
| `emergencias/indeci_distrito_anio_lluvias.csv` | 2,912 | 8 | 2003 a 2025 | ok | 0 | ok |
| `emergencias/impactos_eventos_nino_compilados.csv` | 53 | 10 | — | — | 39.62 | ok |
| `enso/enso_mensual_1854_hoy.csv` | 2,074 | 19 | 1854-01 a 2026-10 | ok | 72.32 | ok |
| `enso/enso_eventos_nino_costero.csv` | 57 | 8 | 1857-11 a 2026-02 | ok | 0 | ok |
| `lluvia/lluvia_chirps_anomalia_departamento.csv` | 1,716 | 6 | 1991-01 a 2026-09 | ok | 0 | ok |
| `lluvia/lluvia_mensual_departamento.csv` | 8,150 | 6 | 1891-01 a 2026-10 | ok | 73.5 | ok |
| `lluvia/lluvia_mensual_distrito.csv` | 200,200 | 8 | 1981-01 a 2026-10 | ok | 21.45 | ok |
| `lluvia/lluvia_intensidad_pisco_distrito_mes.csv` | 157,248 | 11 | 1981-01 a 2016-12 | ok | 0 | ok |
| `lluvia/lluvia_intensidad_chirps_eventos_distrito_mes.csv` | 16,744 | 11 | 1982-11 a 2026-09 | ok | 0 | ok |
| `lluvia/lluvia_diaria_chirps_eventos_distrito.csv` | 507,780 | 8 | 1982-11-01 a 2026-09-30 | ok | 0 | ok |
| `lluvia/estaciones_ghcn_lluvia_diaria.csv` | 65,745 | 4 | 1973-01-01 a 2025-08-19 | ok | 0 | ok |
| `lluvia/estaciones_ghcn_resumen.csv` | 10 | 16 | 1973-01-01 a 2025-08-19 | ok | 30 | ok |
| `caudales/caudales_glofas_diario.csv` | 64,926 | 3 | 1997-01-01 a 2026-04-30 | ok | 0 | ok |
| `caudales/caudales_glofas_mensual.csv` | 2,160 | 4 | 1997-01 a 2026-04 | ok | 0 | ok |
| `caudales/caudales_glofas_puntos.csv` | 18 | 3 | — | ok | 0 | ok |
| `caudales/caudales_glofas_pronostico.csv` | 3,726 | 10 | 2026-11-10 a 2027-06-04 | ok | 0 | ok |
| `caudales/caudales_pico_rio_piura_observados.csv` | 8 | 7 | 1983 a 2023-03 | — | 12.5 | ok |
| `territorio/distritos_costa_norte_atributos.csv` | 364 | 34 | — | ok | 0 | ok |
| `modelo/panel_costa_norte_2003_2025.csv` | 1,104 | 21 | 2003-01 a 2025-12 | ok | 0 | ok |
| `modelo/panel_distrito_temporada_1970_2025.csv` | 20,384 | 50 | 1970 a 2025 | ok | 35.71 | ok |
| `escenarios/icen_2027_supuesto.csv` | 5 | 3 | 2026-12 a 2027-04 | ok | 0 | ok |

## Detalle

### `emergencias/indeci_emergencias_2003_2025.csv`

- 142,139 filas × 52 columnas; periodo 2003-01-01 a 2025-12-31; clave sin clave (una fila por registro).
- Marcas (filas en verdadero): codigo_sinpad_repetido: 14; es_peligro_lluvias: 63,615.
- Vacíos: aulas_destruidas_o_inhabitables_2019_2024 64.26 %, colegios_cantidad_desde_2019 52.72 %, aulas_afectadas_desde_2019 52.72 %, aulas_destruidas_desde_2019 52.72 %, aulas_inhabitables_desde_2019 52.72 %, colegios_destruidos_hasta_2018 47.28 %, colegios_afectados_hasta_2018 47.28 %.
- Por qué: Colegios: hasta 2018 se registraban centros educativos y desde 2019 aulas, así que cada grupo de columnas está vacío en el otro periodo. codigo_sinpad no es clave: 7 códigos se repiten (marcados). ubigeo_mapa suma 2 distritos nuevos a su distrito de origen.
- Negativos inesperados: ninguno.

### `emergencias/desinventar_fichas_costa_norte.csv`

- 5,388 filas × 36 columnas; periodo 1970-01-05 a 2015-12-30; clave `id_desinventar`: única.
- Marcas (filas en verdadero): hidrometeorologico: 2,723; causa_el_nino: 988.
- Vacíos: lat 99.22 %, lon 99.22 %, descripcion_causa 52.6 %, lugar 49.76 %, distrito 12.45 %, ubigeo 12.45 %, provincia 4.75 %, dia 2.71 %, fecha 2.71 %, mes_num 0.13 %, fuentes 0.02 %.
- Por qué: lat/lon vacías en el 99 % (DesInventar las trae en 0). Fichas sin distrito o sin provincia: nivel_geografico lo indica. Mes o día vacío = no se registró.
- Negativos inesperados: ninguno.

### `emergencias/desinventar_panel_departamento_mes.csv`

- 2,760 filas × 12 columnas; periodo 1970-01 a 2015-12; clave `departamento + fecha`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `emergencias/desinventar_distrito_anio.csv`

- 1,414 filas × 13 columnas; periodo 1970 a 2015; clave `ubigeo + anio`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `emergencias/indeci_distrito_anio_lluvias.csv`

- 2,912 filas × 8 columnas; periodo 2003 a 2025; clave `ubigeo + anio`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `emergencias/impactos_eventos_nino_compilados.csv`

- 53 filas × 10 columnas; periodo —; clave sin clave (una fila por registro).
- Vacíos: nota 39.62 %, fecha_corte 28.3 %.
- Por qué: Cifras copiadas a mano de informes; fecha_corte y nota son opcionales.
- Negativos inesperados: ninguno.

### `enso/enso_mensual_1854_hoy.csv`

- 2,074 filas × 19 columnas; periodo 1854-01 a 2026-10; clave `fecha`: única.
- Vacíos: mei_v2 72.32 %, soi 56.61 %, cpc_nino12_anom 55.74 %, cpc_nino3_anom 55.74 %, cpc_nino4_anom 55.74 %, cpc_nino34_anom 55.74 %, icen_oficial 55.59 %, oni 55.59 %, roni 55.59 %, icen 0.1 %, icen_fuente 0.1 %, icen_reconstruido 0.1 %.
- Por qué: Cada índice cubre solo el periodo de su fuente: ICEN oficial, ONI, RONI y CPC desde 1950, SOI desde 1951 y MEI desde 1979. Los archivos de CPC (Niño 1+2, 3, 4, 3.4) llegan a 2026-06 y el SOI a 2025-12. El ICEN es un promedio centrado de 3 meses, así que el primer y el último mes quedan vacíos.
- Negativos inesperados: ninguno.

### `enso/enso_eventos_nino_costero.csv`

- 57 filas × 8 columnas; periodo 1857-11 a 2026-02; clave `inicio`: única.
- Marcas (filas en verdadero): en_curso: 1.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `lluvia/lluvia_chirps_anomalia_departamento.csv`

- 1,716 filas × 6 columnas; periodo 1991-01 a 2026-09; clave `departamento + mes`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `lluvia/lluvia_mensual_departamento.csv`

- 8,150 filas × 6 columnas; periodo 1891-01 a 2026-10; clave `departamento + fecha`: única.
- Vacíos: lluvia_pisco_estable_mm 73.5 %, lluvia_chirps_mm 66.32 %, lluvia_pisco_reciente_mm 66.26 %, lluvia_gpcc_mm 7.24 %.
- Por qué: La tabla va de 1891 a hoy y cada fuente cubre solo su periodo: GPCC 1891-2016, CHIRPS y PISCO desde 1981, PISCO estable hasta 2016.
- Negativos inesperados: ninguno.

### `lluvia/lluvia_mensual_distrito.csv`

- 200,200 filas × 8 columnas; periodo 1981-01 a 2026-10; clave `ubigeo + fecha`: única.
- Vacíos: lluvia_pisco_estable_mm 21.45 %, lluvia_chirps_mm 0.18 %.
- Por qué: PISCO estable termina en 2016 y CHIRPS todavía no publica el último mes.
- Negativos inesperados: ninguno.

### `lluvia/lluvia_intensidad_pisco_distrito_mes.csv`

- 157,248 filas × 11 columnas; periodo 1981-01 a 2016-12; clave `ubigeo + fecha`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `lluvia/lluvia_intensidad_chirps_eventos_distrito_mes.csv`

- 16,744 filas × 11 columnas; periodo 1982-11 a 2026-09; clave `ubigeo + fecha`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `lluvia/lluvia_diaria_chirps_eventos_distrito.csv`

- 507,780 filas × 8 columnas; periodo 1982-11-01 a 2026-09-30; clave `ubigeo + fecha`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `lluvia/estaciones_ghcn_lluvia_diaria.csv`

- 65,745 filas × 4 columnas; periodo 1973-01-01 a 2025-08-19; clave `estacion + fecha`: única.
- Marcas (filas en verdadero): revisar_mayor_200mm: 17.
- Sin vacíos.
- Por qué: Días sin dato no aparecen como filas.
- Negativos inesperados: ninguno.

### `lluvia/estaciones_ghcn_resumen.csv`

- 10 filas × 16 columnas; periodo 1973-01-01 a 2025-08-19; clave `estacion`: única.
- Marcas (filas en verdadero): dentro_area_estudio: 7.
- Vacíos: ubigeo 30 %.
- Por qué: ubigeo vacío = estación fuera de los 5 departamentos.
- Negativos inesperados: ninguno.

### `caudales/caudales_glofas_diario.csv`

- 64,926 filas × 3 columnas; periodo 1997-01-01 a 2026-04-30; clave `rio_punto + fecha`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `caudales/caudales_glofas_mensual.csv`

- 2,160 filas × 4 columnas; periodo 1997-01 a 2026-04; clave `rio_punto + mes`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `caudales/caudales_glofas_puntos.csv`

- 18 filas × 3 columnas; periodo —; clave `rio_punto`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `caudales/caudales_glofas_pronostico.csv`

- 3,726 filas × 10 columnas; periodo 2026-11-10 a 2027-06-04; clave `rio_punto + emitido + fecha`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `caudales/caudales_pico_rio_piura_observados.csv`

- 8 filas × 7 columnas; periodo 1983 a 2023-03; clave sin clave (una fila por registro).
- Vacíos: fecha 12.5 %.
- Por qué: Cifras de prensa e informes; hay valores en conflicto para 1998 (ver nota).
- Negativos inesperados: ninguno.

### `territorio/distritos_costa_norte_atributos.csv`

- 364 filas × 34 columnas; periodo —; clave `ubigeo`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

### `modelo/panel_costa_norte_2003_2025.csv`

- 1,104 filas × 21 columnas; periodo 2003-01 a 2025-12; clave `departamento + mes`: única.
- Sin vacíos.
- Por qué: No debe tener vacíos.
- Negativos inesperados: ninguno.

### `modelo/panel_distrito_temporada_1970_2025.csv`

- 20,384 filas × 50 columnas; periodo 1970 a 2025; clave `ubigeo + anio`: única.
- Vacíos: lluvia_ene_may_pisco_estable_mm 35.71 %, lluvia_max_diaria_ene_may_pisco_mm 35.71 %, dias_mayor_20mm_ene_may_pisco 35.71 %, max_acum_3dias_ene_may_pisco_mm 35.71 %, lluvia_nov_dic_previo_pisco_reciente_mm 21.43 %, lluvia_ene_may_pisco_reciente_mm 19.64 %, lluvia_ene_may_chirps_mm 19.64 %, lluvia_mes_max_ene_may_pisco_reciente_mm 19.64 %, lluvia_ene_may_pisco_reciente_relativa 19.64 %, lluvia_ene_may_chirps_relativa 19.64 %, hist_tuvo_damnificados_temporada_anterior 1.79 %, hist_temporadas_con_damnificados 1.79 % y 1 columnas más.
- Por qué: Vacíos esperados: no hay lluvia por distrito antes de 1981 (ni la de nov-dic previa antes de 1982), PISCO estable y la intensidad diaria terminan en 2016, y 1970 no tiene temporadas previas para el historial.
- Negativos inesperados: ninguno.

### `escenarios/icen_2027_supuesto.csv`

- 5 filas × 3 columnas; periodo 2026-12 a 2027-04; clave `mes`: única.
- Sin vacíos.
- Negativos inesperados: ninguno.

## Inventario de `datos/1_crudos/`

| Fuente (carpeta) | Archivos | Tamaño | FUENTE.md |
|---|---:|---:|:---:|
| `Compilado_manual` | 3 | 13 KB | sí |
| `Copernicus_DEM_GLO90` | 38 | 154 MB | sí |
| `DWD_GPCC` | 2 | 4 MB | sí |
| `DesInventar` | 12 | 53 MB | sí |
| `ENFEN_IGP_ICEN` | 3 | 32 KB | sí |
| `GloFAS_OpenMeteo` | 559 | 2 MB | sí |
| `HydroSHEDS_HydroRIVERS` | 2 | 14 MB | sí |
| `INDECI_SINPAD` | 2 | 26 MB | sí |
| `INEI_limites_geojson` | 4 | 3 MB | sí |
| `Indicadores_distritales` | 2 | 401 KB | sí |
| `NOAA_CPC_indices` | 6 | 261 KB | sí |
| `NOAA_ERSSTv5` | 2 | 14 MB | sí |
| `NOAA_GHCN_estaciones` | 13 | 12 MB | sí |
| `NOAA_PSL_MEI` | 2 | 6 KB | sí |
| `SENAMHI_PISCO` | 39 | 193 MB | sí |
| `UCSB_CHIRPS` | 9 | 129 MB | sí |
| `_registros_descarga` | 4 | 65 KB | sí |
