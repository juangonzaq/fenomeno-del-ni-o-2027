"""Revisa la calidad de las tablas de datos/2_limpios/ y escribe
datos/2_limpios/_calidad/reporte_calidad.md.

Para cada tabla comprueba: filas, periodo, que la clave no se repita, el % de vacíos por
columna y que no haya negativos donde no tiene sentido (lluvia, caudal, damnificados...).
También hace un inventario de datos/1_crudos/ (archivos y tamaño por fuente).

Uso:  .venv/bin/python scripts/06_validar_datos.py
Termina con error (código 1) si alguna clave se repite, si hay negativos inesperados
o si la tabla del modelo tiene vacíos.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import CRUDOS, L_CALIDAD, LIMPIOS  # noqa: E402

# tabla -> (clave, explicación de los vacíos esperados)
TABLAS = {
    "emergencias/indeci_emergencias_2003_2025.csv": (
        None, "Colegios: hasta 2018 se registraban centros educativos y desde 2019 aulas, así que cada grupo de "
              "columnas está vacío en el otro periodo. codigo_sinpad no es clave: 7 códigos se repiten (marcados). "
              "ubigeo_mapa suma 2 distritos nuevos a su distrito de origen."),
    "emergencias/desinventar_fichas_costa_norte.csv": (
        ["id_desinventar"], "lat/lon vacías en el 99 % (DesInventar las trae en 0). Fichas sin distrito o sin "
                            "provincia: nivel_geografico lo indica. Mes o día vacío = no se registró."),
    "emergencias/desinventar_panel_departamento_mes.csv": (["departamento", "fecha"], ""),
    "emergencias/desinventar_distrito_anio.csv": (["ubigeo", "anio"], ""),
    "emergencias/indeci_distrito_anio_lluvias.csv": (["ubigeo", "anio"], ""),
    "emergencias/impactos_eventos_nino_compilados.csv": (None, "Cifras copiadas a mano de informes; fecha_corte y nota son opcionales."),
    "enso/enso_mensual_1854_hoy.csv": (
        ["fecha"], "Cada índice cubre solo el periodo de su fuente: ICEN oficial, ONI, RONI y CPC desde 1950, "
                   "SOI desde 1951 y MEI desde 1979. Los archivos de CPC (Niño 1+2, 3, 4, 3.4) llegan a 2026-06 y el "
                   "SOI a 2025-12. El ICEN es un promedio centrado de 3 meses, así que el primer y el último mes "
                   "quedan vacíos."),
    "enso/enso_eventos_nino_costero.csv": (["inicio"], ""),
    "lluvia/lluvia_chirps_anomalia_departamento.csv": (["departamento", "mes"], ""),
    "lluvia/lluvia_mensual_departamento.csv": (
        ["departamento", "fecha"], "La tabla va de 1891 a hoy y cada fuente cubre solo su periodo: GPCC 1891-2016, "
                                   "CHIRPS y PISCO desde 1981, PISCO estable hasta 2016."),
    "lluvia/lluvia_mensual_distrito.csv": (
        ["ubigeo", "fecha"], "PISCO estable termina en 2016 y CHIRPS todavía no publica el último mes."),
    "lluvia/lluvia_intensidad_pisco_distrito_mes.csv": (["ubigeo", "fecha"], ""),
    "lluvia/lluvia_intensidad_chirps_eventos_distrito_mes.csv": (["ubigeo", "fecha"], ""),
    "lluvia/lluvia_diaria_chirps_eventos_distrito.csv": (["ubigeo", "fecha"], ""),
    "lluvia/estaciones_ghcn_lluvia_diaria.csv": (["estacion", "fecha"], "Días sin dato no aparecen como filas."),
    "lluvia/estaciones_ghcn_resumen.csv": (["estacion"], "ubigeo vacío = estación fuera de los 5 departamentos."),
    "caudales/caudales_glofas_diario.csv": (["rio_punto", "fecha"], ""),
    "caudales/caudales_glofas_mensual.csv": (["rio_punto", "mes"], ""),
    "caudales/caudales_glofas_puntos.csv": (["rio_punto"], ""),
    "caudales/caudales_glofas_pronostico.csv": (["rio_punto", "emitido", "fecha"], ""),
    "caudales/caudales_pico_rio_piura_observados.csv": (None, "Cifras de prensa e informes; hay valores en conflicto para 1998 (ver nota)."),
    "territorio/distritos_costa_norte_atributos.csv": (
        ["ubigeo"], ""),
    "modelo/panel_costa_norte_2003_2025.csv": (["departamento", "mes"], "No debe tener vacíos."),
    "modelo/panel_distrito_temporada_1970_2025.csv": (
        ["ubigeo", "anio"], "Vacíos esperados: no hay lluvia por distrito antes de 1981 (ni la de nov-dic previa antes "
                            "de 1982), PISCO estable y la intensidad diaria terminan en 2016, y 1970 no tiene "
                            "temporadas previas para el historial."),
    "escenarios/icen_2027_supuesto.csv": (["mes"], ""),
}

# Columnas que pueden ser negativas (anomalías, índices, coordenadas y elevación: la depresión
# de Bayóvar, en Sechura, está bajo el nivel del mar)
NEGATIVOS_OK = ("anom", "icen", "oni", "soi", "mei", "nino", "lat", "lon", "elev")
BANDERAS = ("codigo_sinpad_repetido", "es_peligro_lluvias", "revisar_mayor_200mm", "dentro_area_estudio",
            "hidrometeorologico", "causa_el_nino", "en_curso")
PERIODO = ("fecha", "mes", "anio", "inicio", "primer_dia")


def tam(b: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.0f} {u}"
        b /= 1024
    return f"{b:.1f} TB"


def revisar(rel: str, clave, nota: str) -> tuple:
    p = LIMPIOS / rel
    if not p.exists():
        return {"tabla": rel, "estado": "FALTA"}, []
    df = pd.read_csv(p, low_memory=False, dtype={"ubigeo": str})
    errores, detalle = [], []
    # Periodo
    col_p = next((c for c in PERIODO if c in df.columns), None)
    periodo = f"{df[col_p].min()} a {df[col_p].max()}" if col_p else "—"
    if "ultimo_dia" in df.columns:
        periodo = f"{df['primer_dia'].min()} a {df['ultimo_dia'].max()}"
    # Clave
    if clave:
        rep = int(df.duplicated(subset=clave).sum())
        txt_clave = f"`{' + '.join(clave)}`: " + ("única" if rep == 0 else f"**{rep} repetidas**")
        if rep:
            errores.append(f"{rel}: {rep} claves repetidas")
    else:
        txt_clave = "sin clave (una fila por registro)"
    # Vacíos
    vac = (df.isna().mean() * 100).round(2)
    vac = vac[vac > 0].sort_values(ascending=False)
    # Negativos inesperados
    neg = []
    for c in df.select_dtypes("number").columns:
        if any(k in c.lower() for k in NEGATIVOS_OK) or df[c].dtype == bool:
            continue
        n = int((df[c] < 0).sum())
        if n:
            neg.append(f"{c} ({n})")
    if neg:
        errores.append(f"{rel}: negativos en {', '.join(neg)}")
    if rel == "modelo/panel_costa_norte_2003_2025.csv" and df.isna().any().any():
        errores.append(f"{rel}: la tabla del modelo tiene vacíos")
    # Banderas
    band = [f"{c}: {int(df[c].sum()):,}" for c in BANDERAS if c in df.columns and df[c].dtype == bool]

    detalle.append(f"### `{rel}`\n")
    detalle.append(f"- {len(df):,} filas × {df.shape[1]} columnas; periodo {periodo}; clave {txt_clave}.")
    if band:
        detalle.append(f"- Marcas (filas en verdadero): {'; '.join(band)}.")
    if len(vac):
        partes = [f"{c} {v:g} %" for c, v in vac.head(12).items()]
        mas = f" y {len(vac) - 12} columnas más" if len(vac) > 12 else ""
        detalle.append(f"- Vacíos: {', '.join(partes)}{mas}.")
    else:
        detalle.append("- Sin vacíos.")
    if nota:
        detalle.append(f"- Por qué: {nota}")
    detalle.append(f"- Negativos inesperados: {', '.join(neg) if neg else 'ninguno'}.\n")
    fila = {"tabla": rel, "filas": len(df), "columnas": df.shape[1], "periodo": periodo,
            "clave": "ok" if clave and not df.duplicated(subset=clave).any() else ("—" if not clave else "REPETIDA"),
            "pct_vacio_max": float(vac.max()) if len(vac) else 0.0, "estado": "ERROR" if errores else "ok"}
    return fila, detalle, errores


def inventario_crudos() -> list[str]:
    lineas = ["| Fuente (carpeta) | Archivos | Tamaño | FUENTE.md |", "|---|---:|---:|:---:|"]
    for d in sorted(p for p in CRUDOS.iterdir() if p.is_dir()):
        archivos = [f for f in d.rglob("*") if f.is_file() and f.name != ".DS_Store"]
        total = sum(f.stat().st_size for f in archivos)
        lineas.append(f"| `{d.name}` | {len(archivos):,} | {tam(total)} | {'sí' if (d / 'FUENTE.md').exists() else 'no'} |")
    return lineas


if __name__ == "__main__":
    filas, detalles, errores = [], [], []
    for rel, (clave, nota) in TABLAS.items():
        r = revisar(rel, clave, nota)
        if len(r) == 2:
            filas.append(r[0])
            errores.append(f"{rel}: no existe")
            continue
        fila, det, err = r
        filas.append(fila)
        detalles += det
        errores += err
    no_listadas = sorted(str(p.relative_to(LIMPIOS)) for p in LIMPIOS.glob("*/*.csv") if str(p.relative_to(LIMPIOS)) not in TABLAS)

    res = pd.DataFrame(filas)
    md = [f"# Reporte de calidad de `datos/2_limpios/`\n",
          f"Generado por `scripts/06_validar_datos.py` el {time.strftime('%Y-%m-%d %H:%M')}.\n",
          "**Resultado:** " + ("todas las comprobaciones pasaron." if not errores else f"{len(errores)} problemas:") + "\n"]
    md += [f"- {e}" for e in errores]
    md += ["\n## Resumen por tabla\n", "| Tabla | Filas | Col. | Periodo | Clave | % vacío máx. | Estado |", "|---|---:|---:|---|:---:|---:|:---:|"]
    for f in filas:
        if f.get("estado") == "FALTA":
            md.append(f"| `{f['tabla']}` | — | — | — | — | — | FALTA |")
        else:
            md.append(f"| `{f['tabla']}` | {f['filas']:,} | {f['columnas']} | {f['periodo']} | {f['clave']} | {f['pct_vacio_max']:g} | {f['estado']} |")
    if no_listadas:
        md.append(f"\nTablas en 2_limpios que este script no revisa todavía: {', '.join(no_listadas)}.")
    md += ["\n## Detalle\n"] + detalles
    md += ["## Inventario de `datos/1_crudos/`\n"] + inventario_crudos()
    L_CALIDAD.mkdir(parents=True, exist_ok=True)
    (L_CALIDAD / "reporte_calidad.md").write_text("\n".join(md) + "\n")
    print(res.to_string(index=False))
    print("\nReporte: datos/2_limpios/_calidad/reporte_calidad.md")
    if errores:
        print("\nPROBLEMAS:\n  " + "\n  ".join(errores))
        sys.exit(1)
    print("Todas las comprobaciones pasaron.")
