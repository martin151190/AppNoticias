import requests
from bs4 import BeautifulSoup
import pandas as pd

def extraer_noticias_clarin(debug=False):
    """
    Extrae las noticias principales de Clarín utilizando su feed RSS.
    Se agrega un User-Agent para simular un navegador y evitar bloqueos (error 403) en el servidor de despliegue.
    """
    url_rss = "https://www.clarin.com/rss/lo-ultimo/"
    
    # Encabezados para simular una solicitud de navegador (solución a 403 Forbidden)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    
    try:
        # Petición HTTP al feed RSS, incluyendo los headers
        resp = requests.get(url_rss, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml-xml")
        items = soup.find_all("item")
        if debug:
            print(f"[Clarín] Items RSS encontrados: {len(items)}")
        
        noticias = []
        for item in items[:5]:
            titulo = item.title.text.strip() if item.title else None
            enlace = item.link.text.strip() if item.link else None
            imagen_tag = item.find("enclosure")
            imagen = imagen_tag["url"] if imagen_tag and imagen_tag.has_attr("url") else None
            if titulo and enlace:
                noticias.append({
                    "portal": "Clarín",
                    "titulo": titulo,
                    "enlace": enlace,
                    "imagen": imagen
                })
        return pd.DataFrame(noticias)
    except Exception as e:
        if debug:
            print("Error en extraer_noticias_clarin:", e)
        return pd.DataFrame(columns=["portal", "titulo", "enlace", "imagen"])