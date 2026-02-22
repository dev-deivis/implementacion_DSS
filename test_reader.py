from excel_reader import leer_alternativas, leer_criterios, leer_configuracion, validar_excel

# Nombre del archivo que acabas de crear
archivo = "plantilla.xlsx"

print("\n--- PASO 1: VALIDANDO EL ARCHIVO EXCEL ---")
ok, msg = validar_excel(archivo)
print(f"Resultado: {msg}")

if ok:
    print("\n--- PASO 2: LEYENDO DATOS DE ALTERNATIVAS ---")
    alternativas, err = leer_alternativas(archivo)
    if alternativas:
        print(f"¡Éxito! Se cargaron {len(alternativas)} alternativas.")
        print(f"Ejemplo (primera fila): {alternativas[0]}")
    else:
        print(f"Error en alternativas: {err}")

    print("\n--- PASO 3: LEYENDO DATOS DE CRITERIOS ---")
    criterios, err = leer_criterios(archivo)
    if criterios:
        print(f"¡Éxito! Se cargaron {len(criterios)} criterios.")
        print(f"Ejemplo (primer criterio): {criterios[0]}")
    else:
        print(f"Error en criterios: {err}")

    print("\n--- PASO 4: LEYENDO CONFIGURACIÓN ---")
    config, err = leer_configuracion(archivo)
    if config:
        print("¡Éxito! Configuración cargada:")
        for clave, valor in config.items():
            print(f"  - {clave}: {valor}")
    else:
        print(f"Error en configuración: {err}")

    print("\n--- PRUEBA FINALIZADA CON ÉXITO ---")
else:
    print(f"\n[!] Error crítico: {msg}")
