import pandas as pd

def generar_recomendacion(ganador_ahp, ganador_mc, nombre_decision):
    """
    Genera un párrafo de recomendación en español claro.
    Recibe:
        - ganador_ahp: Nombre de la alternativa ganadora según AHP.
        - ganador_mc: Nombre de la alternativa ganadora según Monte Carlo (menor riesgo/mejor promedio).
        - nombre_decision: El contexto de la decisión (ej. "Selección de Proveedor").
    """
    # Lógica definida en PDF [cite: 257-260]
    if ganador_ahp == ganador_mc:
        mensaje = (
            f"**Recomendación Final:** Con alta confianza, la mejor opción para '{nombre_decision}' "
            f"es **{ganador_ahp}**.\n\n"
            "Esta alternativa es superior tanto en el cumplimiento de los criterios establecidos (AHP) "
            "como en la estabilidad frente a riesgos (Monte Carlo). Es una decisión sólida."
        )
    else:
        mensaje = (
            f"**Recomendación Final:** Existe una discrepancia entre los modelos para '{nombre_decision}'.\n\n"
            f"- El modelo de criterios (AHP) sugiere **{ganador_ahp}** por tener mejores características técnicas.\n"
            f"- Sin embargo, la simulación de riesgos (Monte Carlo) sugiere **{ganador_mc}** "
            "porque ofrece resultados más seguros y predecibles.\n\n"
            "**Consejo:** Si su prioridad es maximizar el beneficio técnico asumiendo cierto riesgo, elija la opción de AHP. "
            "Si prefiere evitar sorpresas y busca estabilidad, elija la opción de Monte Carlo."
        )
    
    return mensaje

def generar_razones(alternativa_nombre, criterios_pesos):
    """
    Explica por qué ganó una alternativa basándose en los pesos de los criterios.
    Recibe:
        - alternativa_nombre: Nombre de la opción a explicar.
        - criterios_pesos: Diccionario o lista con nombres de criterios y sus pesos (ej. {'Costo': 0.4}).
    """
    # Ordenamos los criterios de mayor a menor peso para destacar lo importante
    # Suponemos que criterios_pesos es un diccionario: {'Costo': 0.30, 'Calidad': 0.25...}
    criterios_ordenados = sorted(criterios_pesos.items(), key=lambda x: x[1], reverse=True)
    
    top_criterios = criterios_ordenados[:2] # Tomamos los 2 más importantes
    
    razon = f"La opción **{alternativa_nombre}** destaca principalmente porque domina en los criterios clave:\n"
    
    # Formato basado en PDF [cite: 261-263]
    detalles = []
    for criterio, peso in top_criterios:
        detalles.append(f"- **{criterio}** (que representa el {peso*100:.1f}% de la decisión).")
    
    return razon + "\n".join(detalles)

def generar_advertencias(resultados_mc):
    """
    Genera advertencias si hay riesgos altos o baja probabilidad de éxito.
    Recibe:
        - resultados_mc: Diccionario con datos de Monte Carlo por alternativa.
    """
    advertencias = []
    
    # Iteramos sobre cada alternativa analizada en Monte Carlo
    for nombre, datos in resultados_mc.items():
        riesgo = datos.get('riesgo', 'BAJO') # Puede ser BAJO, MEDIO, ALTO
        prob_exito = datos.get('prob_exito', 100) # Porcentaje de veces que fue la mejor
        
        # Lógica definida en PDF [cite: 264-266]
        if riesgo == 'ALTO':
            advertencias.append(f"⚠️ **Precaución con {nombre}:** Se ha detectado una ALTA variabilidad. "
                                "Esto significa que los resultados reales podrían ser muy diferentes a lo planeado.")
            
        if prob_exito < 60:
            advertencias.append(f"⚠️ **Ojo con {nombre}:** En las simulaciones, ganó menos del 60% de las veces. "
                                "No es una apuesta segura frente a la competencia.")
            
    if not advertencias:
        return "✅ No se detectaron riesgos críticos ni variabilidad excesiva en las opciones principales."
    
    return "\n\n".join(advertencias)

def generar_tabla_resumen(resultados_ahp, resultados_mc):
    """
    Crea una tabla final con toda la información condensada.
    Recibe:
        - resultados_ahp: Diccionario con scores AHP { 'China': 0.6, 'USA': 0.7 }
        - resultados_mc: Diccionario con stats MC { 'China': {'promedio': 7.5, 'riesgo': 'ALTO'} }
    """
    # Unificamos los datos en una lista para pandas [cite: 267-268]
    data_resumen = []
    
    todos_nombres = list(resultados_ahp.keys())
    
    for nombre in todos_nombres:
        score_ahp = resultados_ahp.get(nombre, 0)
        stats_mc = resultados_mc.get(nombre, {})
        
        fila = {
            "Alternativa": nombre,
            "Score Técnico (AHP)": f"{score_ahp:.2f}",
            "Score Esperado (MC)": f"{stats_mc.get('promedio', 0):.2f}",
            "Nivel de Riesgo": stats_mc.get('riesgo', 'N/A'),
            "Estabilidad": f"{stats_mc.get('estabilidad', 0)}%"
        }
        data_resumen.append(fila)
        
    # Creamos un DataFrame de Pandas para presentarlo bonito en Streamlit después
    df = pd.DataFrame(data_resumen)
    return df

# --- BLOQUE DE PRUEBA (Para que verifiques si funciona tu código solo) ---
if __name__ == "__main__":
    print("--- INICIANDO PRUEBA DEL MÓDULO RECOMENDACION ---")
    
    # 1. Datos simulados (Como si vinieran de los archivos de tus compañeros)
    mock_ahp_winner = "México"
    mock_mc_winner = "México"
    mock_decision = "Selección de Proveedor 2026"
    
    mock_ahp_scores = {"México": 0.85, "China": 0.65, "USA": 0.75}
    mock_criterios_pesos = {"Costo": 0.40, "Tiempo": 0.30, "Calidad": 0.30}
    
    mock_mc_stats = {
        "México": {"promedio": 8.2, "riesgo": "BAJO", "prob_exito": 95, "estabilidad": 94},
        "China": {"promedio": 6.1, "riesgo": "ALTO", "prob_exito": 20, "estabilidad": 61},
        "USA": {"promedio": 7.8, "riesgo": "MEDIO", "prob_exito": 40, "estabilidad": 85}
    }

    # 2. Probar tus funciones
    print("\n[1] RECOMENDACIÓN:")
    print(generar_recomendacion(mock_ahp_winner, mock_mc_winner, mock_decision))
    
    print("\n[2] RAZONES:")
    print(generar_razones(mock_ahp_winner, mock_criterios_pesos))
    
    print("\n[3] ADVERTENCIAS:")
    print(generar_advertencias(mock_mc_stats))
    
    print("\n[4] TABLA RESUMEN:")
    print(generar_tabla_resumen(mock_ahp_scores, mock_mc_stats))