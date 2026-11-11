"""Modelo binomial negativo del número de emergencias por lluvias con damnificados en la costa norte.

Variable objetivo: emerg_con_damnificados (por departamento y mes).
- Modelo A (pronóstico): solo calendario, tendencia e ICEN del mes anterior. Se puede usar sin saber cuánto lloverá.
- Modelo B (escenarios): A + lluvia del mes respecto a lo normal. Sirve para preguntar "¿y si llueve como en 2017?".

Validación fuera de muestra: se entrena con los años anteriores y se predice enero-mayo de 2017 y de 2023.
Después se reentrena con 2003-2025 y se proyecta enero-mayo de 2027 con el ICEN supuesto en
datos/2_limpios/escenarios/icen_2027_supuesto.csv.
Lee la tabla de datos/2_limpios/modelo/ (la arma 02_preparar_panel.py).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / "resultados"
FIGURAS = RESULTADOS / "figuras"
NORTE = ["TUMBES", "PIURA", "LAMBAYEQUE", "LA LIBERTAD"]
TEMPORADA = [1, 2, 3, 4, 5]  # enero-mayo, lo que se predice
LLUVIOSA = [1, 2, 3, 4]      # meses en que el mar caliente se traduce en lluvia en la costa norte
SIMULACIONES = 5000
rng = np.random.default_rng(2027)

FORMULA_A = "y ~ C(departamento) + C(mes_num) + tendencia + icen_pos + icen_pos:lluviosa"
FORMULA_B = FORMULA_A + " + lluvia_rel + lluvia_rel:lluviosa"


def preparar(df, icen_max=None):
    d = df.copy()
    if "emerg_con_damnificados" in d:  # no existe en los meses futuros
        d["y"] = d["emerg_con_damnificados"]
    d["tendencia"] = d["anio"] - 2003  # recoge que cada año se registran más emergencias
    d["lluviosa"] = d["mes_num"].isin(LLUVIOSA).astype(int)
    d["icen_pos"] = d["icen_lag1"].clip(lower=0)
    if icen_max is not None:
        d["icen_pos"] = d["icen_pos"].clip(upper=icen_max)
    # log de la lluvia relativa; los 10 mm evitan divisiones por meses secos con normal casi cero
    d["lluvia_rel"] = np.log((d["lluvia_mm"] + 10) / (d["lluvia_normal_mm"] + 10))
    return d


def ajustar(formula, datos):
    return smf.negativebinomial(formula, datos).fit(disp=0, maxiter=500)


def simular_total(mu, alpha):
    """Distribución del total sumando binomiales negativas independientes (no incluye la incertidumbre de los coeficientes)."""
    n = 1 / alpha
    p = n / (n + np.asarray(mu))
    return rng.negative_binomial(n, p, size=(SIMULACIONES, len(mu))).sum(axis=1)


def resumen(nombre, mu, alpha):
    s = simular_total(mu, alpha)
    return {"modelo": nombre, "predicho": mu.sum(), "p10": np.percentile(s, 10), "p90": np.percentile(s, 90)}


def validar(panel, anio):
    entreno = preparar(panel[panel["anio"] < anio])
    icen_max = entreno["icen_pos"].max()
    prueba = preparar(panel[(panel["anio"] == anio) & panel["mes_num"].isin(TEMPORADA)], icen_max)
    filas, detalle = [], prueba[["departamento", "mes_num", "y"]].copy()

    # Línea base: promedio histórico del mismo departamento y mes
    base = entreno.groupby(["departamento", "mes_num"])["y"].mean()
    detalle["linea_base"] = [base[(d, m)] for d, m in zip(prueba["departamento"], prueba["mes_num"])]
    filas.append({"modelo": "Línea base (promedio histórico)", "predicho": detalle["linea_base"].sum(),
                  "p10": np.nan, "p90": np.nan})

    for nombre, formula in [("A: ICEN", FORMULA_A), ("B: ICEN + lluvia", FORMULA_B)]:
        m = ajustar(formula, entreno)
        mu = m.predict(prueba)
        detalle[nombre] = mu.values
        filas.append(resumen(nombre, mu, m.params["alpha"]))

    tabla = pd.DataFrame(filas)
    tabla.insert(0, "anio", anio)
    tabla["observado"] = prueba["y"].sum()
    tabla["error_%"] = (tabla["predicho"] - tabla["observado"]) / tabla["observado"] * 100
    tabla["mae_depto_mes"] = [np.abs(detalle[c] - detalle["y"]).mean()
                              for c in ["linea_base", "A: ICEN", "B: ICEN + lluvia"]]
    detalle.insert(0, "anio", anio)
    return tabla, detalle


def proyectar_2027(panel):
    entreno = preparar(panel)
    icen_max = entreno["icen_pos"].max()
    sup = pd.read_csv(RAIZ / "datos" / "2_limpios" / "escenarios" / "icen_2027_supuesto.csv")
    icen_prev = dict(zip(pd.PeriodIndex(sup["mes"], freq="M") + 1, sup["icen"]))  # ICEN del mes anterior

    futuro = pd.DataFrame([(d, m) for d in NORTE for m in TEMPORADA], columns=["departamento", "mes_num"])
    futuro["anio"] = 2027
    futuro["icen_lag1"] = [icen_prev[pd.Period(year=2027, month=m, freq="M")] for m in futuro["mes_num"]]

    normal = panel.groupby(["departamento", "mes_num"])["lluvia_normal_mm"].first()
    futuro["lluvia_normal_mm"] = [normal[(d, m)] for d, m in zip(futuro["departamento"], futuro["mes_num"])]

    m_a = ajustar(FORMULA_A, entreno)
    m_b = ajustar(FORMULA_B, entreno)
    escenarios, detalle = [], []

    for recorte, etiqueta in [(icen_max, "ICEN recortado al máximo observado"), (None, "ICEN sin recortar")]:
        f = futuro.copy()
        f["lluvia_mm"] = f["lluvia_normal_mm"]
        f = preparar(f, recorte)
        mu = m_a.predict(f)
        escenarios.append({"escenario": f"A: solo ICEN ({etiqueta})", **resumen("A", mu, m_a.params["alpha"])})
        detalle.append(f.assign(escenario=f"A ({etiqueta})", predicho=mu.values))

    for lluvia, anio_ref in [("normal", None), ("como 2023", 2023), ("como 2017", 2017)]:
        f = futuro.copy()
        if anio_ref is None:
            f["lluvia_mm"] = f["lluvia_normal_mm"]
        else:
            ref = panel[panel["anio"] == anio_ref].set_index(["departamento", "mes_num"])["lluvia_mm"]
            f["lluvia_mm"] = [ref[(d, m)] for d, m in zip(f["departamento"], f["mes_num"])]
        f = preparar(f, icen_max)
        mu = m_b.predict(f)
        escenarios.append({"escenario": f"B: lluvia {lluvia}", **resumen("B", mu, m_b.params["alpha"])})
        detalle.append(f.assign(escenario=f"B (lluvia {lluvia})", predicho=mu.values))

    return m_a, m_b, icen_max, pd.DataFrame(escenarios), pd.concat(detalle, ignore_index=True)


def coeficientes(m):
    t = pd.DataFrame({"coef": m.params, "p_valor": m.pvalues})
    t["efecto_multiplicativo"] = np.exp(t["coef"])
    return t.round(4)


def graficar(panel, validacion, detalle_val, escenarios):
    plt.rcParams.update({"figure.dpi": 150, "font.size": 9})

    # 1. Historia: total enero-mayo por año
    t = panel[panel["mes_num"].isin(TEMPORADA)].groupby("anio").agg(
        y=("emerg_con_damnificados", "sum"), icen=("icen", "mean"))
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.bar(t.index, t["y"], color="#4C78A8")
    ax.set_ylabel("Emergencias con damnificados (ene-may)")
    ax2 = ax.twinx()
    ax2.plot(t.index, t["icen"], color="#E45756", marker="o", ms=3)
    ax2.set_ylabel("ICEN promedio ene-may", color="#E45756")
    ax.set_title("Costa norte: emergencias por lluvias con damnificados e ICEN")
    fig.tight_layout(); fig.savefig(FIGURAS / "01_historia_costa_norte.png"); plt.close(fig)

    # 2. Validación por departamento
    fig, ejes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=False)
    columnas = ["y", "linea_base", "A: ICEN", "B: ICEN + lluvia"]
    nombres = ["Observado", "Línea base", "A: ICEN", "B: ICEN + lluvia"]
    colores = ["#333333", "#BAB0AC", "#F58518", "#54A24B"]
    for ax, anio in zip(ejes, [2017, 2023]):
        g = detalle_val[detalle_val["anio"] == anio].groupby("departamento")[columnas].sum().reindex(NORTE)
        x = np.arange(len(NORTE))
        for i, (c, n, col) in enumerate(zip(columnas, nombres, colores)):
            ax.bar(x + (i - 1.5) * 0.2, g[c], 0.2, label=n, color=col)
        ax.set_xticks(x, [d.title() for d in NORTE]); ax.set_title(f"Enero-mayo {anio} (fuera de muestra)")
    ejes[0].set_ylabel("Emergencias con damnificados"); ejes[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIGURAS / "02_validacion_2017_2023.png"); plt.close(fig)

    # 3. Escenarios 2027
    fig, ax = plt.subplots(figsize=(8, 3.6))
    e = escenarios
    y = np.arange(len(e))
    ax.barh(y, e["predicho"], color=["#F58518"] * 2 + ["#54A24B"] * 3)
    ax.errorbar(e["predicho"], y, xerr=[e["predicho"] - e["p10"], e["p90"] - e["predicho"]], fmt="none", color="k", capsize=3)
    for anio, lado in [(2017, "right"), (2023, "left")]:
        obs = validacion.loc[validacion["anio"] == anio, "observado"].iloc[0]
        ax.axvline(obs, ls="--", color="#777777")
        ax.text(obs, len(e) - 0.45, f" real {anio} ", fontsize=7, ha=lado, color="#555555")
    ax.set_yticks(y, e["escenario"]); ax.invert_yaxis()
    ax.set_xlabel("Emergencias con damnificados, ene-may 2027 (línea negra: intervalo 80 %)")
    ax.set_title("Escenarios 2027, costa norte")
    fig.tight_layout(); fig.savefig(FIGURAS / "03_escenarios_2027.png", bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    FIGURAS.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(RAIZ / "datos" / "2_limpios" / "modelo" / "panel_costa_norte_2003_2025.csv")

    tablas, detalles = zip(*[validar(panel, a) for a in [2017, 2023]])
    validacion = pd.concat(tablas, ignore_index=True)
    detalle_val = pd.concat(detalles, ignore_index=True)
    validacion.round(1).to_csv(RESULTADOS / "validacion_resumen.csv", index=False)
    detalle_val.round(2).to_csv(RESULTADOS / "validacion_por_departamento_mes.csv", index=False)

    m_a, m_b, icen_max, escenarios, detalle_esc = proyectar_2027(panel)
    escenarios.round(1).to_csv(RESULTADOS / "escenarios_2027.csv", index=False)
    (detalle_esc[["escenario", "departamento", "mes_num", "icen_lag1", "icen_pos", "lluvia_mm", "predicho"]]
     .round(2).to_csv(RESULTADOS / "escenarios_2027_por_departamento_mes.csv", index=False))

    with open(RESULTADOS / "coeficientes_modelos.txt", "w") as f:
        f.write(f"Entrenados con 2003-2025 ({len(panel)} filas). ICEN máximo observado (icen_pos): {icen_max:.2f}\n\n")
        for nombre, m in [("MODELO A: ICEN", m_a), ("MODELO B: ICEN + lluvia", m_b)]:
            f.write(f"== {nombre}\nAIC {m.aic:.1f} | pseudo R2 {m.prsquared:.3f} | alpha {m.params['alpha']:.3f}\n")
            f.write(coeficientes(m).to_string() + "\n\n")

    graficar(panel, validacion, detalle_val, escenarios)

    pd.set_option("display.width", 160)
    print("VALIDACIÓN (enero-mayo, 4 departamentos)\n", validacion.round(1).to_string(index=False))
    print("\nESCENARIOS 2027\n", escenarios.round(1).to_string(index=False))
    print(f"\nICEN máximo observado: {icen_max:.2f}")
    print(f"A: AIC {m_a.aic:.0f}, pseudo R2 {m_a.prsquared:.3f} | B: AIC {m_b.aic:.0f}, pseudo R2 {m_b.prsquared:.3f}")
