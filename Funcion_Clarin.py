import requests
from bs4 import BeautifulSoup
import pandas as pd

def extraer_noticias_clarin(debug=False):
    url_rss = "https://www.clarin.com/rss/lo-ultimo/"
    
    try:
        resp = requests.get(url_rss, timeout=10)
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
