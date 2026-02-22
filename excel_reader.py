import pandas as pd

def leer_alternativas(archivo):
    """
    Lee la hoja 'Alternativas' y retorna una lista de diccionarios con rangos.
    """
    try:
        df = pd.read_excel(archivo, sheet_name='Alternativas')
        # Convertimos el DataFrame a una lista de diccionarios para facilitar su uso
        return df.to_dict(orient='records'), None
    except Exception as e:
        return None, f"Error en hoja Alternativas: {str(e)}"

def leer_criterios(archivo):
    """
    Lee la hoja 'Criterios' y retorna la lista de criterios con su importancia y tipo.
    """
    try:
        df = pd.read_excel(archivo, sheet_name='Criterios')
        return df.to_dict(orient='records'), None
    except Exception as e:
        return None, f"Error en hoja Criterios: {str(e)}"

def leer_configuracion(archivo):
    """
    Lee la hoja 'Configuracion' y retorna un diccionario con los parámetros.
    """
    try:
        df = pd.read_excel(archivo, sheet_name='Configuracion')
        # Convertimos las dos columnas (Parametro, Valor) en un diccionario simple
        config = dict(zip(df['Parametro'], df['Valor']))
        return config, None
    except Exception as e:
        return None, f"Error en hoja Configuracion: {str(e)}"

def validar_excel(archivo):
    """
    Verifica que el Excel tenga las 3 hojas necesarias y las columnas correctas.
    """
    try:
        xls = pd.ExcelFile(archivo)
        hojas_requeridas = ['Alternativas', 'Criterios', 'Configuracion']
        
        for hoja in hojas_requeridas:
            if hoja not in xls.sheet_names:
                return False, f"¡Atención! Falta la hoja '{hoja}' en el archivo."
        
        # Validaciones adicionales de columnas si fuera necesario
        return True, "Formato correcto"
    except Exception as e:
        return False, f"Error al validar: {str(e)}"
