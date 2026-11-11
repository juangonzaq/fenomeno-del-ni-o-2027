"""Rutas de las carpetas de datos, en un solo lugar para todos los scripts.

datos/1_crudos/   carpeta 1: archivos tal como se descargaron, una subcarpeta por fuente.
                  No se editan a mano; si algo está mal se corrige en los scripts 02 y 05.
datos/2_limpios/  carpeta 2: tablas limpias y listas para el modelo, una subcarpeta por tema.
                  Se pueden borrar y volver a generar con 02 y 05.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
CRUDOS = DATOS / "1_crudos"
LIMPIOS = DATOS / "2_limpios"

# ---------------------------------------------------------------- carpeta 1: por fuente
INDECI = CRUDOS / "INDECI_SINPAD"               # emergencias 2003-2025 (descarga manual)
DESINVENTAR = CRUDOS / "DesInventar"            # desastres 1970-2015 por distrito
ICEN = CRUDOS / "ENFEN_IGP_ICEN"                # Índice Costero El Niño oficial
CPC = CRUDOS / "NOAA_CPC_indices"               # ONI, RONI, SOI, Niño 1+2/3/3.4/4
MEI = CRUDOS / "NOAA_PSL_MEI"                   # MEI v2
ERSST = CRUDOS / "NOAA_ERSSTv5"                 # campo de temperatura del mar 1854+
CHIRPS = CRUDOS / "UCSB_CHIRPS"                 # lluvia satelital mensual y diaria
PISCO = CRUDOS / "SENAMHI_PISCO"                # lluvia SENAMHI (estaciones + satélite)
GPCC = CRUDOS / "DWD_GPCC"                      # lluvia de estaciones 1891-2016
GHCN = CRUDOS / "NOAA_GHCN_estaciones"          # lluvia diaria de estaciones
GLOFAS = CRUDOS / "GloFAS_OpenMeteo"            # caudales diarios y pronóstico
LIMITES = CRUDOS / "INEI_limites_geojson"       # límites de departamentos, provincias y distritos
INDICADORES = CRUDOS / "Indicadores_distritales"  # pobreza, IDH, población por distrito
DEM = CRUDOS / "Copernicus_DEM_GLO90"           # relieve a 90 m
RIOS = CRUDOS / "HydroSHEDS_HydroRIVERS"        # red de ríos
MANUAL = CRUDOS / "Compilado_manual"            # cifras copiadas a mano de informes
REGISTROS = CRUDOS / "_registros_descarga"      # logs de las descargas

# ---------------------------------------------------------------- carpeta 2: por tema
L_EMERGENCIAS = LIMPIOS / "emergencias"   # variable objetivo: INDECI y DesInventar
L_ENSO = LIMPIOS / "enso"                 # ICEN y demás índices oceánicos
L_LLUVIA = LIMPIOS / "lluvia"             # lluvia por departamento, distrito y estación
L_CAUDALES = LIMPIOS / "caudales"         # caudales GloFAS y observados
L_TERRITORIO = LIMPIOS / "territorio"     # atributos y mapa de distritos
L_MODELO = LIMPIOS / "modelo"             # tabla que usa 03_modelo.py
L_ESCENARIOS = LIMPIOS / "escenarios"     # supuestos editables para 2027
L_CALIDAD = LIMPIOS / "_calidad"          # reporte de calidad (06_validar_datos.py)
