import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def clean_text(text):
    # Elimina espacios extra y saltos de línea
    text = re.sub(r'\s+', ' ', text).strip()
    # Elimina caracteres especiales
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text

def extract_and_save_news(url, output_file=None):
    try:
        result = extract_news_content(url)
        
        if not output_file:
            # Generar nombre de archivo basado en título
            safe_title = re.sub(r'[^a-zA-Z0-9]', '_', result['title'][:50])
            output_file = f"{safe_title}_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Escribir título
            f.write(f"TÍTULO:\n{result['title']}\n\n")
            
            # Escribir epígrafe
            f.write(f"EPÍGRAFE:\n{result['epigraph']}\n\n")
            
            # Escribir contenido
            f.write("CONTENIDO:\n")
            for element in result['content']:
                if element['type'] == 'subtitle':
                    f.write(f"\n## {element['text']}\n\n")
                else:
                    f.write(f"{element['text']}\n\n")
            
            # Escribir metadatos
            f.write(f"\n---\nFuente: {url}\n")
            f.write(f"Fecha de extracción: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        print(f"Noticia guardada en: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error al guardar la noticia: {str(e)}")
        return None

def extract_news_content(url):
    try:
        # Obtener el contenido HTML
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.60 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer título usando la clase específica
        main_title = soup.find('h1', class_='title full padding-lr fsize-xl')
        main_title = main_title.text.strip() if main_title else ''

        # Extraer epígrafe usando la clase específica
        epigraph = soup.find('div', class_='epigraph full padding-lr')
        epigraph = epigraph.text.strip() if epigraph else ''
        
        # Contenido principal
        article_content = soup.find('div', class_='article-content full padding-lr')
        content_elements = []
        
        if article_content:
            # Ignorar elementos de publicidad
            ads = article_content.find_all(class_=re.compile('ad-slot'))
            for ad in ads:
                ad.decompose()
                
            # Extraer contenido párrafo por párrafo
            for element in article_content.find_all(['h2', 'p']):
                # Ignorar párrafos vacíos
                if element.name == 'p' and not element.text.strip():
                    continue
                    
                content_elements.append({
                    'type': 'subtitle' if element.name == 'h2' else 'paragraph',
                    'text': clean_text(element.text)
                })
        
        return {
            'title': clean_text(main_title),
            'epigraph': clean_text(epigraph),
            'content': content_elements
        }
        
    except Exception as e:
        return {'error': str(e)}

# Ejemplo de uso
if __name__ == "__main__":
    url = "https://www.iprofesional.com/impuestos/415994-arca-que-va-a-pasar-con-monotributistas-tras-disolucion-afip"
    filename = extract_and_save_news(url)
    if filename:
        print(f"Archivo creado: {filename}")