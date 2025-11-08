import requests
from bs4 import BeautifulSoup
import pandas as pd

def extraer_noticias_pagina12(debug=False):
    """
    Extrae las noticias principales de Página/12 utilizando su feed RSS.
    Devuelve un DataFrame con las columnas: portal, titulo, enlace, imagen.
    """
    # URL CORREGIDA: Cambiada de 'ultimasnoticias' a 'portada'
    url_rss = "https://www.pagina12.com.ar/rss/portada"
    
    try:
        # Petición HTTP al feed RSS
        resp = requests.get(url_rss, timeout=10)
        resp.raise_for_status()
        
        # Usamos lxml-xml para parsear el XML del feed
        soup = BeautifulSoup(resp.text, "lxml-xml")
        items = soup.find_all("item")
        
        if debug:
            print(f"[Página/12] Items RSS encontrados: {len(items)}")
            
        noticias = []
        # Limitamos a las primeras 5 noticias, al igual que los otros portales
        for item in items[:5]:
            titulo = item.title.text.strip() if item.title else None
            enlace = item.link.text.strip() if item.link else None
            
            # Página/12 usa el tag <media:content> para la imagen
            media_tag = item.find("media:content")
            imagen = media_tag["url"] if media_tag and media_tag.has_attr("url") else None
            
            if titulo and enlace:
                noticias.append({
                    "portal": "Página/12",
                    "titulo": titulo,
                    "enlace": enlace,
                    "imagen": imagen
                })
                
        return pd.DataFrame(noticias)
        
    except Exception as e:
        if debug:
            print("Error en extraer_noticias_pagina12:", e)
        # Devolver DataFrame vacío si hay un error para evitar que la app se rompa
        return pd.DataFrame(columns=["portal", "titulo", "enlace", "imagen"])
    
