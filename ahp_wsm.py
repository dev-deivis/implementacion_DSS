


def normalizar_pesos(criterios: list[dict]) -> list[dict]:
    
    if not criterios:
        raise ValueError("La lista de criterios está vacía.")

    total = sum(c['Importancia (1-10)'] for c in criterios)

    if total == 0:
        raise ValueError("La suma de importancias no puede ser cero.")

    resultado = []
    for c in criterios:
        copia = dict(c)
        copia['peso'] = copia['Importancia (1-10)'] / total
        resultado.append(copia)

    return resultado


def normalizar_valores(valor: float, minimo: float, maximo: float, tipo: str) -> float:
   
    if maximo == minimo:
        # Si todos los valores son iguales, no hay diferencia entre alternativas
        return 0.5

    if tipo.lower() == 'minimizar':
        # Invertimos: el valor más bajo obtiene el score más alto (1.0)
        return (maximo - valor) / (maximo - minimo)
    else:
        # 'maximizar': el valor más alto obtiene el score más alto (1.0)
        return (valor - minimo) / (maximo - minimo)


def calcular_score(valores_normalizados: dict, criterios_con_pesos: list[dict]) -> float:
   
    score = 0.0
    for criterio in criterios_con_pesos:
        nombre = criterio['Criterio']
        peso = criterio['peso']
        valor = valores_normalizados.get(nombre, 0.0)
        score += peso * valor

    return score


def rankear_alternativas(alternativas: list[dict], criterios: list[dict]) -> list[dict]:
    
    if not alternativas:
        raise ValueError("No hay alternativas para evaluar.")
    if not criterios:
        raise ValueError("No hay criterios definidos.")

    # PASO 1: Normalizar pesos de criterios
    criterios_con_pesos = normalizar_pesos(criterios)

    # PASO 2: Para cada criterio, calcular el rango global usando el promedio de cada alternativa
    # Usamos el promedio de (Min + Max) / 2 como valor representativo de cada alternativa
    rangos_globales = {}
    for criterio in criterios_con_pesos:
        nombre = criterio['Criterio']
        col_min = f"{nombre}_Min"
        col_max = f"{nombre}_Max"

        # Calculamos el valor promedio de cada alternativa para este criterio
        promedios = []
        for alt in alternativas:
            if col_min in alt and col_max in alt:
                promedio = (alt[col_min] + alt[col_max]) / 2
            elif nombre in alt:
                # Por si el criterio tiene un solo valor (sin rango)
                promedio = alt[nombre]
            else:
                promedio = 0.0
            promedios.append(promedio)

        rangos_globales[nombre] = {
            'min': min(promedios),
            'max': max(promedios),
            'tipo': criterio['Tipo']
        }

    # PASO 3 y 4: Normalizar valores y calcular score por alternativa
    resultados = []
    pesos_dict = {c['Criterio']: c['peso'] for c in criterios_con_pesos}

    for alt in alternativas:
        valores_normalizados = {}

        for criterio in criterios_con_pesos:
            nombre = criterio['Criterio']
            col_min = f"{nombre}_Min"
            col_max = f"{nombre}_Max"

            # Valor representativo de esta alternativa para este criterio
            if col_min in alt and col_max in alt:
                valor_repr = (alt[col_min] + alt[col_max]) / 2
            elif nombre in alt:
                valor_repr = alt[nombre]
            else:
                valor_repr = 0.0

            rango = rangos_globales[nombre]
            valores_normalizados[nombre] = normalizar_valores(
                valor=valor_repr,
                minimo=rango['min'],
                maximo=rango['max'],
                tipo=rango['tipo']
            )

        score = calcular_score(valores_normalizados, criterios_con_pesos)

        resultados.append({
            'alternativa': alt['Alternativa'],
            'score': round(score, 4),
            'desglose': {k: round(v, 4) for k, v in valores_normalizados.items()},
            'pesos': pesos_dict
        })

    # PASO 5: Ordenar de mayor a menor score
    resultados.sort(key=lambda x: x['score'], reverse=True)

    return resultados


if __name__ == "__main__":
    try:
        from excel_reader import leer_alternativas, leer_criterios, validar_excel

        archivo = "plantilla.xlsx"

        print("=" * 55)
        print("       PRUEBA RÁPIDA — ahp_wsm.py")
        print("=" * 55)

        ok, msg = validar_excel(archivo)
        if not ok:
            print(f"[!] Error en el Excel: {msg}")
            exit(1)

        alternativas, err = leer_alternativas(archivo)
        if err:
            print(f"[!] {err}")
            exit(1)

        criterios, err = leer_criterios(archivo)
        if err:
            print(f"[!] {err}")
            exit(1)

        # Correr el modelo
        ranking = rankear_alternativas(alternativas, criterios)

        print("\n PESOS NORMALIZADOS (AHP):")
        for nombre, peso in ranking[0]['pesos'].items():
            print(f"   {nombre:<15} → {peso * 100:.1f}%")

        print("\n RANKING DE ALTERNATIVAS (WSM):")
        for i, res in enumerate(ranking, start=1):
            print(f"\n  #{i}  {res['alternativa']}")
            print(f"       Score final: {res['score']:.4f}")
            print("       Desglose por criterio:")
            for criterio, val_norm in res['desglose'].items():
                print(f"         • {criterio:<15} valor normalizado: {val_norm:.4f}")

        print("\n" + "=" * 55)
        print(f"   MEJOR OPCIÓN: {ranking[0]['alternativa']}  (score: {ranking[0]['score']})")
        print("=" * 55)

    except ImportError:
        print("[!] No se encontró excel_reader.py.")
        print("    Asegúrate de correr este script desde la carpeta del proyecto.")
    except FileNotFoundError:
        print("[!] No se encontró plantilla.xlsx.")
        print("    Corre primero: python crear_plantilla.py")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")