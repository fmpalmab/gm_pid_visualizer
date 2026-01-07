import cloudscraper
from bs4 import BeautifulSoup
import os
import zipfile
import urllib.parse # Para manejar bien los nombres de archivo en las URLs

# ================= CONFIGURACIÓN =================
URL_OBJETIVO = "https://www.coordinador.cl/operacion/documentos/programas-de-operacion-2021/"
DIRECTORIO_BASE = r"C:\Users\fpalma.practica\OneDrive - Generadora Metropolitana\Documentos\gm_pid_visualizer"
PATRON_ARCHIVO = "PROGRAMA" # El texto que debe tener el link para ser descargado

# ================= LÓGICA =================
def descargar_programa_operacion():
    # 1. Conectar (Anti-bloqueo)
    scraper = cloudscraper.create_scraper()
    print(f"Conectando a {URL_OBJETIVO}...")
    
    try:
        response = scraper.get(URL_OBJETIVO)
        if response.status_code != 200:
            print(f"Error al conectar: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. Buscar TODOS los enlaces de descarga ZIP
        candidatos = []
        
        # Buscamos directamente todas las etiquetas 'a' que tengan 'href'
        for enlace in soup.find_all('a', href=True):
            url = enlace['href']
            
            # FILTRO:
            # a) Que termine en .zip
            # b) Que contenga "PROGRAMA" (en mayúscula, como indicaste)
            if url.lower().endswith('.zip') and PATRON_ARCHIVO in url.upper():
                # Extraemos el nombre del archivo de la URL
                # Ejemplo: .../uploads/2026/01/PROGRAMA20260105-1.zip -> PROGRAMA20260105-1.zip
                nombre_archivo = os.path.basename(urllib.parse.urlparse(url).path)
                
                candidatos.append({
                    "nombre_archivo": nombre_archivo,
                    "url": url
                })

        if not candidatos:
            print(f"No se encontraron archivos ZIP que contengan '{PATRON_ARCHIVO}' en el nombre.")
            return

        # 3. Ordenar para encontrar el MÁS NUEVO
        # Al ordenar texto que empieza con fecha (PROGRAMA2026...), el orden alfabético 
        # inverso (descendente) nos da la fecha más reciente arriba.
        candidatos.sort(key=lambda x: x['nombre_archivo'], reverse=True)
        
        ultimo = candidatos[0]
        nombre_zip = ultimo['nombre_archivo']
        url_zip = ultimo['url']
        
        print(f"\n¡Archivo objetivo detectado!: {nombre_zip}")

        # 4. Verificar existencia
        ruta_zip_destino = os.path.join(DIRECTORIO_BASE, nombre_zip)
        
        if os.path.exists(ruta_zip_destino):
            print(f"El archivo {nombre_zip} ya existe localmente. Omitiendo descarga.")
        else:
            print(f"Descargando desde: {url_zip} ...")
            zip_response = scraper.get(url_zip)
            
            if zip_response.status_code == 200:
                with open(ruta_zip_destino, 'wb') as f:
                    f.write(zip_response.content)
                print(f"Descarga lista: {ruta_zip_destino}")
                
                # 5. Descomprimir
                # Usamos el nombre del archivo (sin .zip) para la carpeta
                nombre_carpeta = os.path.splitext(nombre_zip)[0] 
                ruta_extraccion = os.path.join(DIRECTORIO_BASE, nombre_carpeta)
                
                print(f"Descomprimiendo en: {ruta_extraccion} ...")
                try:
                    with zipfile.ZipFile(ruta_zip_destino, 'r') as zip_ref:
                        zip_ref.extractall(ruta_extraccion)
                    print("¡Proceso terminado con éxito!")
                except zipfile.BadZipFile:
                    print("Error: El ZIP parece estar dañado.")
            else:
                print("Error al descargar el binario del archivo.")

    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    if not os.path.exists(DIRECTORIO_BASE):
        os.makedirs(DIRECTORIO_BASE)
    descargar_programa_operacion()