"""
=============================================================
  DSS - Sistema de Soporte a la Decisión Multicriterio
  Basado en: Turban, E. - "Decision Support Systems and
             Intelligent Systems" (Capítulo de Modelos)
  Modelos implementados:
    1. Decision Analysis / Weighted Sum Model (WSM)
       → Turban Cap. 4, Sección 4.7 (Decision Tables) y 4.10 (Multiple Goals)
       → Páginas 161-163 y 173-174
    2. AHP – Analytic Hierarchy Process
       → Turban Cap. 4, Sección 4.7 (multicriteria decision analysis, p. 163)
       → Referencia: Saaty (1999), Forman and Selly (2001)
=============================================================
"""

import os
import math


# ─────────────────────────────────────────────
#  UTILIDADES DE CONSOLA
# ─────────────────────────────────────────────

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def separador(char="─", largo=58):
    print(char * largo)


def titulo(texto):
    separador("═")
    print(f"  {texto}")
    separador("═")


def pedir_float(mensaje, minimo=None, maximo=None):
    while True:
        try:
            valor = float(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  ⚠  El valor debe ser ≥ {minimo}")
                continue
            if maximo is not None and valor > maximo:
                print(f"  ⚠  El valor debe ser ≤ {maximo}")
                continue
            return valor
        except ValueError:
            print("  ⚠  Ingresa un número válido.")


def pedir_int(mensaje, minimo=1, maximo=100):
    while True:
        try:
            valor = int(input(mensaje))
            if minimo <= valor <= maximo:
                return valor
            print(f"  ⚠  El valor debe estar entre {minimo} y {maximo}.")
        except ValueError:
            print("  ⚠  Ingresa un número entero válido.")


# ─────────────────────────────────────────────
#  MODELO 1: WEIGHTED SUM MODEL (WSM)
#  Referencia Turban: Cap. "Multi-Criteria
#  Decision Making" – Weighted Scoring Method
# ─────────────────────────────────────────────

def normalizar_pesos(pesos):
    """Normaliza una lista de pesos para que sumen 1.0"""
    total = sum(pesos)
    if total == 0:
        raise ValueError("La suma de pesos no puede ser 0.")
    return [p / total for p in pesos]


def wsm_calcular(alternativas, criterios, pesos, matriz_puntajes, beneficio_flags):
    """
    Calcula el WSM para cada alternativa.

    Parámetros:
    -----------
    alternativas     : list[str]  – nombres de las alternativas
    criterios        : list[str]  – nombres de los criterios
    pesos            : list[float]– pesos normalizados (suma = 1)
    matriz_puntajes  : list[list] – puntajes[alternativa][criterio]
    beneficio_flags  : list[bool] – True=maximizar, False=minimizar

    Retorna:
    --------
    dict con puntajes normalizados y ranking
    """
    n_alt = len(alternativas)
    n_crit = len(criterios)

    # Paso 1: Normalizar cada columna (criterio)
    normalizados = [[0.0] * n_crit for _ in range(n_alt)]
    for j in range(n_crit):
        columna = [matriz_puntajes[i][j] for i in range(n_alt)]
        col_max = max(columna)
        col_min = min(columna)
        rango = col_max - col_min if col_max != col_min else 1

        for i in range(n_alt):
            if beneficio_flags[j]:   # maximizar → mayor es mejor
                normalizados[i][j] = (columna[i] - col_min) / rango
            else:                     # minimizar → menor es mejor
                normalizados[i][j] = (col_max - columna[i]) / rango

    # Paso 2: Suma ponderada
    puntajes_finales = []
    for i in range(n_alt):
        score = sum(normalizados[i][j] * pesos[j] for j in range(n_crit))
        puntajes_finales.append(round(score, 4))

    # Paso 3: Ranking
    ranking = sorted(range(n_alt), key=lambda x: puntajes_finales[x], reverse=True)
    return {
        "normalizados": normalizados,
        "puntajes": puntajes_finales,
        "ranking": ranking
    }


def mostrar_resultados_wsm(alternativas, criterios, pesos, resultado):
    print("\n")
    titulo("RESULTADOS – Weighted Sum Model")

    # Tabla de puntajes normalizados
    print(f"\n{'Alternativa':<20}", end="")
    for c in criterios:
        print(f"{c[:12]:>14}", end="")
    print(f"{'Score WSM':>14}")
    separador()

    for i, alt in enumerate(alternativas):
        print(f"{alt:<20}", end="")
        for j in range(len(criterios)):
            print(f"{resultado['normalizados'][i][j]:>14.4f}", end="")
        print(f"{resultado['puntajes'][i]:>14.4f}")

    separador()
    print("\n📊  RANKING FINAL:")
    for pos, idx in enumerate(resultado["ranking"], 1):
        estrella = " ⭐ MEJOR OPCIÓN" if pos == 1 else ""
        print(f"  {pos}. {alternativas[idx]:<20}  Score: {resultado['puntajes'][idx]:.4f}{estrella}")

    mejor = alternativas[resultado["ranking"][0]]
    print(f"\n✅  RECOMENDACIÓN: El sistema recomienda '{mejor}' como la mejor alternativa")
    print(f"    según los criterios y pesos ingresados.\n")


def ejecutar_wsm():
    limpiar()
    titulo("MODELO 1: Weighted Sum Model (WSM)")
    print("  Basado en Turban – Multi-Criteria Decision Making\n")
    print("  Este modelo evalúa múltiples alternativas según criterios")
    print("  ponderados y recomienda la opción con mayor puntaje.\n")
    separador()

    # Ingresar alternativas
    n_alt = pedir_int("\n  ¿Cuántas alternativas deseas comparar? (2-10): ", 2, 10)
    alternativas = []
    for i in range(n_alt):
        nombre = input(f"  Nombre de la alternativa {i+1}: ").strip() or f"Alternativa_{i+1}"
        alternativas.append(nombre)

    # Ingresar criterios
    n_crit = pedir_int("\n  ¿Cuántos criterios de evaluación? (2-8): ", 2, 8)
    criterios = []
    beneficio_flags = []
    for j in range(n_crit):
        nombre = input(f"\n  Nombre del criterio {j+1}: ").strip() or f"Criterio_{j+1}"
        criterios.append(nombre)
        tipo = input(f"  ¿'{nombre}' es de beneficio (maximizar) o costo (minimizar)? [B/C]: ").strip().upper()
        beneficio_flags.append(tipo != "C")

    # Ingresar pesos
    print("\n  Ingresa los pesos relativos de cada criterio (cualquier número positivo):")
    pesos_raw = []
    for j, c in enumerate(criterios):
        p = pedir_float(f"  Peso de '{c}': ", 0.01)
        pesos_raw.append(p)
    pesos = normalizar_pesos(pesos_raw)
    print("\n  Pesos normalizados:")
    for j, c in enumerate(criterios):
        print(f"    {c}: {pesos[j]:.4f}  ({pesos[j]*100:.1f}%)")

    # Ingresar puntajes
    print("\n  Ingresa los puntajes de cada alternativa para cada criterio.")
    print("  (Usa la escala que prefieras, ej: 1-10, o valores reales como precio, tiempo, etc.)\n")
    matriz = []
    for i, alt in enumerate(alternativas):
        fila = []
        print(f"  → {alt}:")
        for j, crit in enumerate(criterios):
            val = pedir_float(f"       {crit}: ")
            fila.append(val)
        matriz.append(fila)

    # Calcular y mostrar
    resultado = wsm_calcular(alternativas, criterios, pesos, matriz, beneficio_flags)
    mostrar_resultados_wsm(alternativas, criterios, pesos, resultado)


# ─────────────────────────────────────────────
#  MODELO 2: AHP – Analytic Hierarchy Process
#  Referencia Turban: Cap. "AHP" – pairwise
#  comparison matrix & consistency ratio
# ─────────────────────────────────────────────

# Índice aleatorio de Saaty para n = 1..10
RI = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
      6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def ahp_normalizar_matriz(matriz):
    n = len(matriz)
    sumas_col = [sum(matriz[i][j] for i in range(n)) for j in range(n)]
    normalizada = [[matriz[i][j] / sumas_col[j] for j in range(n)] for i in range(n)]
    prioridades = [sum(normalizada[i]) / n for i in range(n)]
    return prioridades


def ahp_consistency(matriz, prioridades):
    n = len(matriz)
    # Vector ponderado
    weighted = [sum(matriz[i][j] * prioridades[j] for j in range(n)) for i in range(n)]
    # Lambda max
    lambda_max = sum(weighted[i] / prioridades[i] for i in range(n)) / n
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0
    ri = RI.get(n, 1.49)
    cr = ci / ri if ri > 0 else 0
    return lambda_max, ci, cr


def pedir_comparacion_pareada(elemento_a, elemento_b):
    """
    Escala de Saaty:
    1=igual, 3=moderadamente mejor, 5=fuertemente mejor,
    7=muy fuertemente mejor, 9=extremadamente mejor
    (o fracciones inversas)
    """
    escala = [1/9, 1/7, 1/5, 1/3, 1, 3, 5, 7, 9]
    print(f"\n  Comparando: '{elemento_a}'  vs  '{elemento_b}'")
    print("  Escala: 1/9(extremo menor) ... 1(igual) ... 9(extremo mayor)")
    while True:
        try:
            val = float(input(f"  ¿Cuánto más importante es '{elemento_a}' sobre '{elemento_b}'? "))
            if val <= 0:
                print("  ⚠  El valor debe ser positivo.")
                continue
            return val
        except ValueError:
            print("  ⚠  Ingresa un número válido (ej: 1, 3, 5, 1/3, 0.333).")


def ejecutar_ahp():
    limpiar()
    titulo("MODELO 2: Analytic Hierarchy Process (AHP)")
    print("  Basado en Turban – AHP de Thomas Saaty\n")
    print("  Descompone la decisión en criterios y alternativas,")
    print("  usando comparaciones pareadas para obtener pesos.\n")
    separador()

    n_crit = pedir_int("\n  ¿Cuántos criterios? (2-7): ", 2, 7)
    criterios = []
    for j in range(n_crit):
        nombre = input(f"  Criterio {j+1}: ").strip() or f"C{j+1}"
        criterios.append(nombre)

    # Matriz de comparación pareada de criterios
    print("\n  Ahora compara los criterios entre sí.")
    mat_crit = [[1.0] * n_crit for _ in range(n_crit)]
    for i in range(n_crit):
        for j in range(i+1, n_crit):
            val = pedir_comparacion_pareada(criterios[i], criterios[j])
            mat_crit[i][j] = val
            mat_crit[j][i] = 1.0 / val

    prioridades_crit = ahp_normalizar_matriz(mat_crit)
    lmax, ci, cr = ahp_consistency(mat_crit, prioridades_crit)

    print("\n  Prioridades de criterios (pesos AHP):")
    for j, c in enumerate(criterios):
        print(f"    {c}: {prioridades_crit[j]:.4f}  ({prioridades_crit[j]*100:.1f}%)")
    print(f"\n  Ratio de Consistencia (CR): {cr:.4f}", end="  ")
    if cr <= 0.10:
        print("✅ Consistente (CR ≤ 0.10)")
    else:
        print("⚠  Inconsistente (CR > 0.10) – considera revisar tus comparaciones")

    # Alternativas
    n_alt = pedir_int("\n  ¿Cuántas alternativas? (2-8): ", 2, 8)
    alternativas = []
    for i in range(n_alt):
        nombre = input(f"  Alternativa {i+1}: ").strip() or f"A{i+1}"
        alternativas.append(nombre)

    # Para cada criterio, comparar alternativas
    prioridades_alt = []
    for j, crit in enumerate(criterios):
        print(f"\n  ── Comparación de alternativas respecto a '{crit}' ──")
        mat_alt = [[1.0] * n_alt for _ in range(n_alt)]
        for a in range(n_alt):
            for b in range(a+1, n_alt):
                val = pedir_comparacion_pareada(alternativas[a], alternativas[b])
                mat_alt[a][b] = val
                mat_alt[b][a] = 1.0 / val
        prio = ahp_normalizar_matriz(mat_alt)
        prioridades_alt.append(prio)

    # Score global
    scores = []
    for i in range(n_alt):
        score = sum(prioridades_crit[j] * prioridades_alt[j][i] for j in range(n_crit))
        scores.append(round(score, 4))

    ranking = sorted(range(n_alt), key=lambda x: scores[x], reverse=True)

    # Mostrar resultados
    print("\n")
    titulo("RESULTADOS – AHP")
    separador()
    print(f"\n{'Alternativa':<20}  {'Score Global':>14}")
    separador()
    for i, alt in enumerate(alternativas):
        print(f"  {alt:<20}  {scores[i]:>14.4f}")
    separador()
    print("\n📊  RANKING FINAL:")
    for pos, idx in enumerate(ranking, 1):
        estrella = " ⭐ MEJOR OPCIÓN" if pos == 1 else ""
        print(f"  {pos}. {alternativas[idx]:<20}  Score: {scores[idx]:.4f}{estrella}")

    mejor = alternativas[ranking[0]]
    print(f"\n✅  RECOMENDACIÓN: Según el AHP, la mejor alternativa es '{mejor}'.\n")


# ─────────────────────────────────────────────
#  MENÚ PRINCIPAL
# ─────────────────────────────────────────────

def menu_principal():
    while True:
        limpiar()
        titulo("DSS – Sistema de Soporte a la Decisión")
        print("  Modelos basados en Efraim Turban\n")
        print("  1.  Weighted Sum Model (WSM)")
        print("      Evaluación multicriterio con pesos ponderados\n")
        print("  2.  Analytic Hierarchy Process (AHP)")
        print("      Comparaciones pareadas estilo Saaty\n")
        print("  0.  Salir")
        separador()
        opcion = input("  Selecciona una opción [0-2]: ").strip()

        if opcion == "1":
            ejecutar_wsm()
            input("\n  Presiona Enter para volver al menú...")
        elif opcion == "2":
            ejecutar_ahp()
            input("\n  Presiona Enter para volver al menú...")
        elif opcion == "0":
            print("\n  ¡Hasta luego!\n")
            break
        else:
            print("  Opción inválida.")
            input("  Presiona Enter para continuar...")


if __name__ == "__main__":
    menu_principal()