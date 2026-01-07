import cloudscraper
from bs4 import BeautifulSoup
import os
import zipfile
import io

# ================= CONFIGURACIÓN =================
# URL de la página
URL_OBJETIVO = "https://www.coordinador.cl/operacion/documentos/programacion-intradiaria/"

# Tu directorio de trabajo
DIRECTORIO_BASE = r"C:\Users\fpalma.practica\OneDrive - Generadora Metropolitana\Documentos\gm_pid_visualizer"

# ================= LÓGICA =================

def descargar_y_descomprimir():
    # 1. Conectar a la página burlando la seguridad
    scraper = cloudscraper.create_scraper()
    print(f"Conectando a {URL_OBJETIVO}...")
    
    try:
        response = scraper.get(URL_OBJETIVO)
        if response.status_code != 200:
            print(f"Error al conectar: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. Buscar todos los archivos disponibles
        # Creamos una lista de diccionarios con nombre y url
        archivos_encontrados = []
        
        items = soup.find_all('span', class_='informes-estudio-Titulo')
        
        for item in items:
            nombre = item.text.strip() # Ej: PID 20260105_04
            
            # Buscamos el link asociado en el padre
            contenedor = item.parent
            enlace_tag = contenedor.find('a', string=lambda t: t and "Descargar ZIP" in t)
            
            if enlace_tag:
                url_descarga = enlace_tag['href']
                archivos_encontrados.append({
                    "nombre": nombre,
                    "url": url_descarga
                })

        if not archivos_encontrados:
            print("No se encontraron archivos ZIP en la página.")
            return

        # 3. Encontrar el ÚLTIMO (El más nuevo)
        # Ordenamos la lista alfabéticamente descendente.
        # Como el formato es PID AAAA-MM-DD, el orden alfabético coincide con el cronológico.
        archivos_encontrados.sort(key=lambda x: x['nombre'], reverse=True)
        
        ultimo_archivo = archivos_encontrados[0]
        nombre_zip = ultimo_archivo['nombre'] + ".zip"
        url_zip = ultimo_archivo['url']
        
        print(f"\n¡Último archivo detectado!: {ultimo_archivo['nombre']}")
        
        # 4. Verificar si ya existe el ZIP descargado para no repetirlo
        ruta_zip_destino = os.path.join(DIRECTORIO_BASE, nombre_zip)
        
        if os.path.exists(ruta_zip_destino):
            print(f"El archivo {nombre_zip} ya existe en la carpeta. No es necesario descargar.")
            # Opcional: Podrías forzar la descompresión aquí si quisieras
        else:
            print(f"Descargando desde: {url_zip} ...")
            
            # Descargamos el contenido binario
            zip_response = scraper.get(url_zip)
            
            if zip_response.status_code == 200:
                # Guardamos el ZIP
                with open(ruta_zip_destino, 'wb') as f:
                    f.write(zip_response.content)
                print(f"Descarga completada: {ruta_zip_destino}")
                
                # 5. Descomprimir
                print("Descomprimiendo...")
                ruta_extraccion = os.path.join(DIRECTORIO_BASE, ultimo_archivo['nombre']) # Crea carpeta con el nombre del PID
                
                try:
                    with zipfile.ZipFile(ruta_zip_destino, 'r') as zip_ref:
                        zip_ref.extractall(ruta_extraccion)
                    print(f"¡Éxito! Archivos descomprimidos en: {ruta_extraccion}")
                except zipfile.BadZipFile:
                    print("Error: El archivo descargado parece estar corrupto o no es un ZIP válido.")
            else:
                print("Error al intentar descargar el archivo ZIP.")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    # Asegurarnos de que el directorio base existe (por si acaso)
    if not os.path.exists(DIRECTORIO_BASE):
        os.makedirs(DIRECTORIO_BASE)
        
    descargar_y_descomprimir()