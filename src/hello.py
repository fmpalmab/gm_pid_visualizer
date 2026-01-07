import cloudscraper
from bs4 import BeautifulSoup

url = "https://www.coordinador.cl/operacion/documentos/programacion-intradiaria/"

# Creamos un "scraper" que simula ser un navegador real (Chrome/Firefox)
# Esto maneja automáticamente las cookies y desafíos de seguridad.
scraper = cloudscraper.create_scraper()

print(f"Intentando conectar a {url} usando Cloudscraper...")

try:
    # Usamos scraper.get en lugar de requests.get
    response = scraper.get(url)

    if response.status_code == 200:
        print("¡Conexión exitosa! Hemos burlado la seguridad.")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscamos los títulos (basado en el HTML que me mostraste)
        items = soup.find_all('span', class_='informes-estudio-Titulo')
        
        if not items:
            print("Conectamos, pero no encontramos archivos. (Puede que el HTML haya cambiado o cargue por JS).")
        else:
            print(f"Se encontraron {len(items)} archivos:\n")
            
            for item in items:
                nombre_archivo = item.text.strip()
                
                # Buscamos el enlace en el contenedor padre
                contenedor = item.parent
                enlace_tag = contenedor.find('a', string=lambda t: t and "Descargar ZIP" in t)
                
                if enlace_tag:
                    url_descarga = enlace_tag['href']
                    print(f"Archivo: {nombre_archivo}")
                    print(f"URL: {url_descarga}")
                    print("-" * 30)

    elif response.status_code == 403:
        print("Error 403: Cloudscraper no fue suficiente. El sitio podría estar bloqueando por IP o huella TLS.")
    else:
        print(f"Error inesperado: {response.status_code}")

except Exception as e:
    print(f"Ocurrió un error: {e}")