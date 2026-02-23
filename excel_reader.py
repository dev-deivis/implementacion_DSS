import pandas as pd

def normalizar_df(df):
    """
    Limpia los nombres de las columnas (quita espacios extra) 
    y asegura que los datos de texto no tengan espacios al inicio/final.
    """
    df.columns = [str(col).strip() for col in df.columns]
    # Limpiar espacios en celdas de texto
    for col in df.select_dtypes(['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    return df

def validar_hojas(xls):
    """
    Busca las hojas requeridas manejando posibles variaciones (tildes/mayúsculas).
    """
    nombres_reales = xls.sheet_names
    mapeo = {}
    
    buscar = {
        'Alternativas': ['Alternativas', 'alternativas'],
        'Criterios': ['Criterios', 'criterios'],
        'Configuracion': ['Configuracion', 'Configuración', 'configuracion', 'configuración']
    }
    
    for clave, variaciones in buscar.items():
        encontrada = next((h for h in nombres_reales if h in variaciones), None)
        if encontrada:
            mapeo[clave] = encontrada
        else:
            return None, f"No se encontró la hoja '{clave}' (revisa el nombre o tildes)."
            
    return mapeo, None

def leer_alternativas(archivo):
    try:
        xls = pd.ExcelFile(archivo)
        mapeo, err = validar_hojas(xls)
        if err: return None, err
        
        df = pd.read_excel(xls, sheet_name=mapeo['Alternativas'])
        df = normalizar_df(df)
        
        if 'Alternativa' not in df.columns:
            return None, "Error: La columna 'Alternativa' es obligatoria en la hoja Alternativas."
            
        return df.to_dict(orient='records'), None
    except Exception as e:
        return None, f"Error en Alternativas: {str(e)}"

def leer_criterios(archivo):
    try:
        xls = pd.ExcelFile(archivo)
        mapeo, err = validar_hojas(xls)
        if err: return None, err
        
        df = pd.read_excel(xls, sheet_name=mapeo['Criterios'])
        df = normalizar_df(df)
        
        cols_req = ['Criterio', 'Importancia (1-10)', 'Tipo']
        for col in cols_req:
            if col not in df.columns:
                return None, f"Error: Falta la columna '{col}' en la hoja Criterios."
        
        return df.to_dict(orient='records'), None
    except Exception as e:
        return None, f"Error en Criterios: {str(e)}"

def leer_configuracion(archivo):
    try:
        xls = pd.ExcelFile(archivo)
        mapeo, err = validar_hojas(xls)
        if err: return None, err
        
        df = pd.read_excel(xls, sheet_name=mapeo['Configuracion'])
        df = normalizar_df(df)
        
        if 'Parametro' not in df.columns or 'Valor' not in df.columns:
            return None, "Error: La hoja Configuracion debe tener columnas 'Parametro' y 'Valor'."
            
        config = dict(zip(df['Parametro'], df['Valor']))
        return config, None
    except Exception as e:
        return None, f"Error en Configuracion: {str(e)}"

def validar_excel(archivo):
    """
    Verificación completa antes de procesar nada.
    """
    try:
        xls = pd.ExcelFile(archivo)
        mapeo, err = validar_hojas(xls)
        if err: return False, err
        return True, "Formato detectado correctamente."
    except Exception as e:
        return False, f"El archivo no es un Excel válido: {str(e)}"
