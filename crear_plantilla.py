import pandas as pd

def generar_excel_10_proveedores():
    # 1. Hoja Alternativas: 10 Proveedores y 5 Criterios (Min/Max)
    df_alternativas = pd.DataFrame({
        'Alternativa': [
            'China (Global)', 'USA (Premium)', 'México (Local)', 
            'Vietnam (Emergente)', 'Alemania (High-End)', 'Brasil (Mercosur)', 
            'India (Scale)', 'Japón (Calidad)', 'Canadá (Trade)', 'España (Euro-Med)'
        ],
        
        # Criterio 1: Costo por lote (Minimizar)
        'Costo_Min': [800, 1500, 1100, 750, 1800, 950, 700, 1900, 1400, 1200],
        'Costo_Max': [1200, 1700, 1300, 1000, 2200, 1300, 900, 2100, 1600, 1400],
        
        # Criterio 2: Tiempo de entrega en días (Minimizar)
        'Entrega_Min': [30, 3, 5, 35, 10, 20, 32, 12, 6, 14],
        'Entrega_Max': [60, 7, 12, 55, 15, 35, 50, 18, 10, 20],
        
        # Criterio 3: Calidad 1-10 (Maximizar)
        'Calidad_Min': [6, 9, 7, 5, 9, 6, 6, 10, 8, 8],
        'Calidad_Max': [8, 10, 9, 7, 10, 8, 8, 10, 9, 9],
        
        # Criterio 4: Confiabilidad 1-10 (Maximizar)
        'Confiabilidad_Min': [7, 9, 8, 5, 9, 6, 6, 10, 9, 8],
        'Confiabilidad_Max': [9, 10, 9, 7, 10, 8, 7, 10, 10, 9],
        
        # Criterio 5: Riesgo Geopolítico 1-10 (Minimizar - 1 es seguro)
        'Riesgo_Min': [7, 1, 3, 6, 1, 5, 5, 1, 1, 2],
        'Riesgo_Max': [9, 2, 5, 8, 2, 7, 8, 2, 2, 3]
    })

    # 2. Hoja Criterios: Los 5 criterios con sus importancias
    df_criterios = pd.DataFrame({
        'Criterio': ['Costo', 'Entrega', 'Calidad', 'Confiabilidad', 'Riesgo'],
        'Importancia (1-10)': [9, 8, 7, 8, 6],
        'Tipo': ['minimizar', 'minimizar', 'maximizar', 'maximizar', 'minimizar']
    })

    # 3. Hoja Configuracion
    df_config = pd.DataFrame({
        'Parametro': ['Iteraciones', 'Nombre Decision', 'Proyecto'],
        'Valor': [20000, 'Licitación Suministros Q3 2026', 'SmartDecide Pro']
    })

    # Guardar archivo
    nombre_archivo = 'plantilla_10_proveedores.xlsx'
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        df_alternativas.to_excel(writer, sheet_name='Alternativas', index=False)
        df_criterios.to_excel(writer, sheet_name='Criterios', index=False)
        df_config.to_excel(writer, sheet_name='Configuracion', index=False)
    
    return nombre_archivo

if __name__ == "__main__":
    try:
        archivo = generar_excel_10_proveedores()
        print(f"¡Excelente! Se ha creado '{archivo}'.")
        print("Este archivo contiene 10 proveedores y 5 criterios detallados.")
        print("Esto es exactamente lo que la profesora busca en un DSS robusto.")
    except Exception as e:
        print(f"Error: {e}")
