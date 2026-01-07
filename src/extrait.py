import pandas as pd

# Especifica la ruta de tu archivo Excel
filename = 'PRG260105.xlsx'

# Leemos sin encabezado para obtener la matriz completa
df = pd.read_excel(filename, sheet_name='PROGRAMA', header=None, engine='openpyxl')

# 1. Limpieza estructural: Borrar fila 0 y columnas 0, 1
df = df.iloc[1:, 2:]
df = df.reset_index(drop=True)
df.columns = range(df.shape[1]) 

tables = {}
header_indices = []

# 2. Detección de encabezados (buscando secuencia 1, 2, 3 en columnas 2, 3, 4)
for i in df.index:
    try:
        # Convertimos a string para asegurar comparación (maneja '1', 1, 1.0)
        v1 = str(df.iloc[i, 2]).strip().replace('.0', '')
        v2 = str(df.iloc[i, 3]).strip().replace('.0', '')
        v3 = str(df.iloc[i, 4]).strip().replace('.0', '')
        
        if v1 == '1' and v2 == '2' and v3 == '3':
             header_indices.append(i)
    except:
        continue

# 3. Procesamiento de tablas con limpieza de "cola"
ranges = []
for i in range(len(header_indices)):
    start = header_indices[i]
    # El límite teórico es el siguiente encabezado o el final
    limit = header_indices[i+1] if i < len(header_indices) - 1 else len(df)
    
    # Nombre de la categoría (Columna 0 del encabezado)
    category = str(df.iloc[start, 0]).strip()
    
    # Corrección Nombre Primera Tabla (si es fecha)
    if i == 0 and any(c.isdigit() for c in category):
        category = "Resumen Programación"
        
    # Extraer bloque crudo
    raw_block = df.iloc[start+1:limit].copy()
    
    # --- CORRECCIÓN FINAL DE TABLA (LAST TABLE FIX) ---
    # En lugar de tomar todo el bloque, buscamos dónde termina realmente la data.
    # Criterio: Las filas válidas tienen datos en la columna 0 (Nombre)
    # Y generalmente terminan en una fila "Total" o antes de notas vacías.
    
    valid_rows = []
    found_total = False
    
    for idx, row in raw_block.iterrows():
        name = str(row[0]).strip()
        
        # Si el nombre está vacío o es 'nan', es probable que la tabla haya terminado
        if not name or name.lower() == 'nan':
            # Si ya encontramos datos y ahora hay vacío, paramos (fin de tabla)
            if len(valid_rows) > 0:
                break
            else:
                continue # Filas vacías al inicio (raro, pero posible)
        
        # Si detectamos texto largo de nota al pie (ej. empieza con "Nota:" o es muy largo en col 0)
        # O si detectamos que las columnas de datos (2 en adelante) son nulas
        # Asumimos fin de tabla.
        
        # Agregamos la fila
        valid_rows.append(row)
        
        # Si la fila es "Total", la tabla suele terminar aquí.
        if name.lower() == 'total':
            found_total = True
            # Opcional: break aquí si sabemos que Total es la última. 
            # A veces hay desglose post-total, pero en este archivo parece ser el cierre.
            # Dejaremos que el loop continúe solo si hay más datos inmediatos, 
            # pero el check de "name empty" en la siguiente vuelta lo detendrá.
    
    if valid_rows:
        data = pd.DataFrame(valid_rows)
        
        # Definir columnas
        col_names = ['Nombre', 'ID'] + [str(h) for h in range(1, 25)]
        cols_to_keep = [0, 1] + list(range(2, 26))
        
        # Si hay columna Total (col 26)
        if data.shape[1] > 26:
            cols_to_keep.append(26)
            col_names.append('Total')
            
        data = data.iloc[:, cols_to_keep]
        data.columns = col_names
        
        tables[category] = data.reset_index(drop=True)

# Resultado
print("Tablas extraídas y limpiadas:", list(tables.keys()))

print("\n", tables["Resumen Programación"])