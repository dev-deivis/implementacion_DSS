import pandas as pd

def generar_recomendacion(ganador_ahp, ganador_mc, nombre_decision="la decisión actual"):
    """
    Genera un párrafo de recomendación en español claro.
    """
    if ganador_ahp == ganador_mc:
        mensaje = (
            f"**Recomendación Final:** Con alta confianza, la mejor opción para {nombre_decision} "
            f"es **{ganador_ahp}**.\n\n"
            "Esta alternativa es superior tanto en el cumplimiento de los criterios establecidos (AHP) "
            "como en la previsibilidad frente a riesgos (Monte Carlo). Es una decisión sólida."
        )
    else:
        mensaje = (
            f"**Recomendación Final:** Existe una discrepancia entre los modelos para {nombre_decision}.\n\n"
            f"- El modelo de criterios (AHP) sugiere **{ganador_ahp}** por tener mejores características técnicas.\n"
            f"- Sin embargo, la simulación de riesgos (Monte Carlo) sugiere **{ganador_mc}** "
            "porque ofrece resultados más seguros y predecibles frente a la incertidumbre.\n\n"
            "**Consejo:** Si su prioridad es maximizar el beneficio técnico asumiendo cierto riesgo, elija la opción de AHP. "
            "Si prefiere evitar sorpresas y busca estabilidad, elija la opción de Monte Carlo."
        )
    
    return mensaje

def generar_razones(alternativa_nombre, criterios_pesos):
    """
    Explica por qué ganó una alternativa basándose en los pesos de los criterios.
    """
    # Ordenamos los criterios de mayor a menor peso para destacar lo importante
    criterios_ordenados = sorted(criterios_pesos.items(), key=lambda x: x[1], reverse=True)
    top_criterios = criterios_ordenados[:2] # Tomamos los 2 más importantes
    
    razon = f"La opción **{alternativa_nombre}** destaca principalmente porque domina en los criterios clave para la empresa:\n"
    
    detalles = []
    for criterio, peso in top_criterios:
        detalles.append(f"- **{criterio}** (que representa el {peso*100:.1f}% de la decisión).")
    
    return razon + "\n".join(detalles)

def generar_advertencias(resultados_mc):
    """
    Genera advertencias si hay riesgos altos o baja probabilidad de éxito.
    """
    advertencias = []
    
    # Iteramos sobre los resultados de Monte Carlo
    for nombre, datos in resultados_mc.items():
        riesgo = datos.get('riesgo', 'BAJO') 
        # prob_ganar viene en decimal (ej. 0.55), lo evaluamos
        prob_ganar = datos.get('prob_ganar', 1.0) 
        
        if riesgo == 'ALTO':
            advertencias.append(f"⚠️ **Precaución con {nombre}:** Se ha detectado una ALTA variabilidad. "
                                "Esto significa que los resultados reales podrían ser muy diferentes a lo planeado.")
            
        if prob_ganar < 0.60:
            porcentaje = prob_ganar * 100
            advertencias.append(f"⚠️ **Ojo con {nombre}:** En las simulaciones, ganó solo el {porcentaje:.1f}% de las veces. "
                                "No es una apuesta segura frente a la competencia.")
            
    if not advertencias:
        return "✅ No se detectaron riesgos críticos ni variabilidad excesiva en las opciones principales."
    
    return "\n\n".join(advertencias)

def generar_tabla_resumen(resultados_ahp_lista, resultados_mc):
    """
    Crea una tabla final con toda la información condensada.
    """
    data_resumen = []
    
    # Extraemos los nombres de las alternativas desde la lista de AHP
    for item_ahp in resultados_ahp_lista:
        nombre = item_ahp['alternativa']
        score_ahp = item_ahp['score']
        
        # Buscamos los datos de esta alternativa en Monte Carlo
        stats_mc = resultados_mc.get(nombre, {})
        
        fila = {
            "Alternativa": nombre,
            "Score Técnico (AHP)": f"{score_ahp:.4f}",
            "Valor Esperado (MC)": f"{stats_mc.get('media', 0):.4f}",
            "Nivel de Riesgo": stats_mc.get('riesgo', 'N/A'),
            "Prob. de Ganar": f"{stats_mc.get('prob_ganar', 0) * 100:.1f}%"
        }
        data_resumen.append(fila)
        
    df = pd.DataFrame(data_resumen)
    return df

# --- BLOQUE DE INTEGRACIÓN REAL ---
if __name__ == "__main__":
    print("=" * 60)
    print(" 🛠️ PRUEBA DE INTEGRACIÓN: AHP + Monte Carlo + Recomendación")
    print("=" * 60)
    
    try:
        import sys
        # Importamos las funciones de tus compañeros
        from excel_reader import leer_alternativas, leer_criterios, leer_configuracion
        from ahp_wsm import rankear_alternativas, normalizar_pesos
        from montecarlo import simular_todas
        
        archivo = "plantilla.xlsx"
        
        # 1. Leer datos del Excel con MANEJO DE ERRORES
        alternativas, err_alt = leer_alternativas(archivo)
        if err_alt or alternativas is None:
            print(f"[!] Error en excel_reader (Alternativas): {err_alt}")
            sys.exit(1)
            
        criterios, err_crit = leer_criterios(archivo)
        if err_crit or criterios is None:
            print(f"[!] Error en excel_reader (Criterios): {err_crit}")
            sys.exit(1)
            
        config, err_conf = leer_configuracion(archivo)
        if err_conf or config is None:
            print(f"[!] Error en excel_reader (Configuración): {err_conf}")
            print("💡 Revisa que tu archivo plantilla.xlsx tenga una hoja llamada 'Configuracion' escrita exactamente así.")
            sys.exit(1)
            
        nombre_decision = config.get("Nombre decision", "la selección actual")
        
        # 2. Ejecutar AHP
        ranking_ahp = rankear_alternativas(alternativas, criterios)
        ganador_ahp = ranking_ahp[0]['alternativa']
        pesos_criterios = ranking_ahp[0]['pesos']
        
        # 3. Ejecutar Monte Carlo
        criterios_con_pesos = normalizar_pesos(criterios)
        pesos_mc = {c['Criterio']: c['peso'] for c in criterios_con_pesos}
        resultado_mc = simular_todas(alternativas, criterios, pesos_mc, iteraciones=1000)
        ganador_mc = resultado_mc['ganador']
        stats_mc = resultado_mc['resultados']
        
        # 4. PROBAR TU MÓDULO (Persona 6)
        print("\n[1] TEXTO DE RECOMENDACIÓN:")
        print("-" * 40)
        print(generar_recomendacion(ganador_ahp, ganador_mc, nombre_decision))
        
        print("\n[2] RAZONES PRINCIPALES:")
        print("-" * 40)
        print(generar_razones(ganador_ahp, pesos_criterios))
        
        print("\n[3] ALERTAS Y ADVERTENCIAS:")
        print("-" * 40)
        print(generar_advertencias(stats_mc))
        
        print("\n[4] TABLA RESUMEN PARA DIRECTIVOS:")
        print("-" * 40)
        # Mostrar el DataFrame de Pandas en la consola
        print(generar_tabla_resumen(ranking_ahp, stats_mc).to_string(index=False))
        
        print("\n" + "=" * 60)
        print("✅ Todo funciona correctamente y está integrado.")
        
    except FileNotFoundError:
        print("[!] No se encontró el archivo plantilla.xlsx. Asegúrate de que esté en la misma carpeta.")
    except ImportError as e:
        print(f"[!] Faltan archivos de tus compañeros. Error: {e}")