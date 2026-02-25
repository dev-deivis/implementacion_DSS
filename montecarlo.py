# Simulación Monte Carlo

import numpy as np

# Calcular rangos globales por criterio
def calcular_rangos_globales(alternativas: list, criterios: list) -> dict:
    rangos = {}

    for criterio in criterios:
        nombre = criterio['Criterio']
        tipo   = criterio['Tipo']
        col_min = f"{nombre}_Min"
        col_max = f"{nombre}_Max"

        todos_los_valores = []
        for alt in alternativas:
            todos_los_valores.append(alt[col_min])
            todos_los_valores.append(alt[col_max])

        rangos[nombre] = {
            "min":  min(todos_los_valores),
            "max":  max(todos_los_valores),
            "tipo": tipo
        }

    return rangos


# Normalizar un valor a escala 0-1
def normalizar_valor(valor: float,
                     minimo_global: float,
                     maximo_global: float,
                     tipo: str) -> float:
    if maximo_global == minimo_global:
        return 0.5

    if tipo.lower() == "minimizar":
        return (maximo_global - valor) / (maximo_global - minimo_global)
    else:
        return (valor - minimo_global) / (maximo_global - minimo_global)


# Simular UNA alternativa N veces
def simular_alternativa(alternativa: dict,
                        criterios: list,
                        pesos_normalizados: dict,
                        rangos_globales: dict,
                        iteraciones: int = 10000) -> list:

    # Crear vector de scores en cero
    scores = np.zeros(iteraciones)

    for criterio in criterios:
        nombre  = criterio['Criterio']
        col_min = f"{nombre}_Min"
        col_max = f"{nombre}_Max"

        val_min = alternativa[col_min]
        val_max = alternativa[col_max]

        min_global = rangos_globales[nombre]["min"]
        max_global = rangos_globales[nombre]["max"]
        tipo       = rangos_globales[nombre]["tipo"]

        # Generar TODOS los valores de una vez
        valores = np.random.uniform(val_min, val_max, iteraciones)

        # Normalización vectorizada
        if max_global == min_global:
            valores_norm = np.full(iteraciones, 0.5)
        elif tipo.lower() == "minimizar":
            valores_norm = (max_global - valores) / (max_global - min_global)
        else:
            valores_norm = (valores - min_global) / (max_global - min_global)

        # Acumular ponderación
        peso = pesos_normalizados[nombre]
        scores += peso * valores_norm

    return scores.tolist()

# Calcular estadísticas de los scores
def calcular_estadisticas(scores: list) -> dict:
    arr = np.array(scores)

    return {
        "media":        round(float(np.mean(arr)),             4),
        "desviacion":   round(float(np.std(arr)),              4),
        "percentil_5":  round(float(np.percentile(arr,  5)),   4),
        "percentil_95": round(float(np.percentile(arr, 95)),   4),
        "minimo":       round(float(np.min(arr)),              4),
        "maximo":       round(float(np.max(arr)),              4),
        "scores":       scores   # guardamos todos para la gráfica
    }


# Clasificar nivel de riesgo
def clasificar_riesgo(desviacion: float) -> str:
    """
    Clasifica el riesgo según la desviación estándar.
    Mayor desviación = más impredecible = más riesgo.

    Retorna: "BAJO", "MEDIO" o "ALTO"
    """
    if desviacion < 0.08:
        return "BAJO"
    elif desviacion < 0.15:
        return "MEDIO"
    else:
        return "ALTO"


# Probabilidad de ganar por alternativa
def calcular_prob_ganadora(scores_todas: dict) -> dict:
    nombres     = list(scores_todas.keys())
    matriz      = np.array(list(scores_todas.values()))
    iteraciones = matriz.shape[1]

    # Índice del ganador en cada iteración
    ganadores = np.argmax(matriz, axis=0)

    probabilidades = {}
    for i, nombre in enumerate(nombres):
        veces = np.sum(ganadores == i)
        probabilidades[nombre] = round(float(veces / iteraciones), 4)

    return probabilidades


# FUNCIÓN PRINCIPAL — Simular TODAS las alternativas
def simular_todas(alternativas: list,
                  criterios: list,
                  pesos_normalizados: dict,
                  iteraciones: int = 10000) -> dict:
    # Calcular rangos globales para normalización
    rangos_globales = calcular_rangos_globales(alternativas, criterios)

    scores_todas = {}
    resultados   = {}

    print(f"\nEjecutando {iteraciones:,} simulaciones por alternativa...")

    for alt in alternativas:
        nombre = alt['Alternativa']
        print(f"   Simulando: {nombre}...")

        scores = simular_alternativa(
            alt, criterios, pesos_normalizados,
            rangos_globales, iteraciones
        )

        scores_todas[nombre]    = scores
        stats                   = calcular_estadisticas(scores)
        stats["riesgo"]         = clasificar_riesgo(stats["desviacion"])
        resultados[nombre]      = stats

    # Probabilidad de ganar de cada alternativa
    probs = calcular_prob_ganadora(scores_todas)
    for nombre in resultados:
        resultados[nombre]["prob_ganar"] = probs[nombre]

    # Ganador = mayor media
    ganador = max(resultados, key=lambda x: resultados[x]["media"])

    print(f"\nSimulación completada.")
    print(f"Ganador Monte Carlo: {ganador}")

    return {
        "ganador":    ganador,
        "resultados": resultados
    }

# PRUEBA
if __name__ == "__main__":
    try:
        from excel_reader import leer_alternativas, leer_criterios, leer_configuracion, validar_excel
        from ahp_wsm import normalizar_pesos

        archivo = "plantilla.xlsx"

        print("=" * 55)
        print("             PRUEBA RÁPIDA")
        print("=" * 55)

        # Validar Excel
        ok, msg = validar_excel(archivo)
        if not ok:
            print(f"[!] {msg}")
            exit(1)

        # Leer datos
        alternativas, err = leer_alternativas(archivo)
        if err:
            print(f"[!] {err}")
            exit(1)

        criterios, err = leer_criterios(archivo)
        if err:
            print(f"[!] {err}")
            exit(1)

        config, err = leer_configuracion(archivo)
        if err:
            print(f"[!] {err}")
            exit(1)

        iteraciones = int(config.get("Iteraciones", 10000))

        # Obtener pesos normalizados de AHP
        criterios_con_pesos = normalizar_pesos(criterios)
        pesos = {c['Criterio']: c['peso'] for c in criterios_con_pesos}

        # Correr simulación
        resultado = simular_todas(
            alternativas, criterios, pesos, iteraciones
        )

        for nombre, datos in resultado["resultados"].items():
            print(f"\n{nombre}")
            print(f"   Valor esperado:   {datos['media']:.4f}")
            print(f"   Desviación:       {datos['desviacion']:.4f}")
            print(f"   Peor caso  (5%):  {datos['percentil_5']:.4f}")
            print(f"   Mejor caso (95%): {datos['percentil_95']:.4f}")
            print(f"   Nivel de riesgo:  {datos['riesgo']}")
            print(f"   Prob. de ganar:   {datos['prob_ganar']*100:.1f}%")

        print(f"\nGANADOR: {resultado['ganador']}")
        print("=" * 55)

    except FileNotFoundError:
        print("[!] No se encontró plantilla.xlsx")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")