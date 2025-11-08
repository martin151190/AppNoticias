import requests
from bs4 import BeautifulSoup
import pandas as pd

def extraer_noticias_googlenews(debug=False):
    """
    Extrae los titulares principales de Google News (Argentina) utilizando su feed RSS.
    Google News es una fuente muy estable y raramente presenta bloqueos 403.
    Devuelve un DataFrame con las columnas: portal, titulo, enlace, imagen.
    """
    # URL de RSS de Google News para Titulares Principales en Argentina (Español)
    url_rss = "https://news.google.com/rss?hl=es-419&gl=AR&ceid=AR:es-419&oc=1"
    portal_nombre = "Google News (Titulares)"
    
    # Headers básicos, aunque Google News es muy permisivo con el acceso a su RSS
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        resp = requests.get(url_rss, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml-xml")
        items = soup.find_all("item")
        
        if debug:
            print(f"[{portal_nombre}] Items RSS encontrados: {len(items)}")
            
        noticias = []
        # Limitamos a los primeros 5 titulares
        for item in items[:5]:
            titulo = item.title.text.strip() if item.title else None
            # Google usa un enlace largo en el link, pero el enlace real está en el tag 'guid' o 'source'
            enlace_google = item.link.text.strip() if item.link else None
            
            # Google News RSS no incluye una imagen de forma estándar.
            # Dejamos 'imagen' como None para no romper la app
            imagen = None 
            
            # El enlace en el tag <link> de Google News es una URL de redirección.
            # Para mayor estabilidad y si el feed no tiene un enlace 'guid' limpio,
            # usaremos el enlace de redirección que funciona perfectamente.
            if titulo and enlace_google:
                noticias.append({
                    "portal": portal_nombre,
                    "titulo": titulo,
                    "enlace": enlace_google,
                    "imagen": imagen
                })
                
        return pd.DataFrame(noticias)
        
    except Exception as e:
        if debug:
            print(f"Error en extraer_noticias_googlenews: {e}")
        return pd.DataFrame(columns=["portal", "titulo", "enlace", "imagen"])
    
