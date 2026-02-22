import pandas as pd

def generar():
    # Hoja Alternativas
    df_alternativas = pd.DataFrame({
        'Alternativa': ['China', 'USA', 'Mexico'],
        'Costo_Min': [800, 1400, 1100],
        'Costo_Max': [1200, 1600, 1300],
        'Entrega_Min': [15, 3, 5],
        'Entrega_Max': [45, 7, 15],
        'Calidad_Min': [6, 8, 7],
        'Calidad_Max': [8, 10, 9]
    })

    # Hoja Criterios
    df_criterios = pd.DataFrame({
        'Criterio': ['Costo', 'Entrega', 'Calidad'],
        'Importancia (1-10)': [9, 7, 8],
        'Tipo': ['minimizar', 'minimizar', 'maximizar']
    })

    # Hoja Configuracion
    df_config = pd.DataFrame({
        'Parametro': ['Iteraciones', 'Nombre Decision'],
        'Valor': [10000, 'Selección de proveedor Q1 2025']
    })

    with pd.ExcelWriter('plantilla.xlsx', engine='openpyxl') as writer:
        df_alternativas.to_excel(writer, sheet_name='Alternativas', index=False)
        df_criterios.to_excel(writer, sheet_name='Criterios', index=False)
        df_config.to_excel(writer, sheet_name='Configuracion', index=False)

if __name__ == "__main__":
    try:
        generar()
        print("¡Archivo 'plantilla.xlsx' creado con éxito!")
    except Exception as e:
        print(f"Error: {e}")
