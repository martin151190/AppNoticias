import requests
from bs4 import BeautifulSoup
import pandas as pd

def extraer_noticias_infobae(debug=False):
    url_rss = "https://www.infobae.com/feeds/rss/"
    
    try:
        resp = requests.get(url_rss, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml-xml")
        items = soup.find_all("item")
        if debug:
            print(f"[Infobae] Items RSS encontrados: {len(items)}")
        
        noticias = []
        for item in items[:5]:
            titulo = item.title.text.strip() if item.title else None
            enlace = item.link.text.strip() if item.link else None
            imagen_tag = item.find("enclosure")
            imagen = imagen_tag["url"] if imagen_tag and imagen_tag.has_attr("url") else None
            if titulo and enlace:
                noticias.append({
                    "portal": "Infobae",
                    "titulo": titulo,
                    "enlace": enlace,
                    "imagen": imagen
                })
        
        if noticias:
            return pd.DataFrame(noticias)
        else:
            if debug:
                print("[Infobae] RSS vacío, intentando scraping directo...")
            return extraer_noticias_infobae_scraping(debug)
    
    except Exception as e:
        if debug:
            print("Error en extraer_noticias_infobae:", e)
        return extraer_noticias_infobae_scraping(debug)

def extraer_noticias_infobae_scraping(debug=False):
    url = "https://www.infobae.com/ultimas-noticias/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        # Buscar bloques de noticias
        articulos = soup.find_all("a", class_="feed-list-card")
        titulos, enlaces, imagenes = [], [], []

        for art in articulos:
            titulo = art.get("title") or art.text.strip()
            enlace = art.get("href")
            img_tag = art.find("img")
            imagen = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

            if titulo and enlace:
                titulos.append(titulo)
                enlaces.append(enlace)
                imagenes.append(imagen)

        # Asegurar que todas las listas tengan el mismo largo
        n = min(len(titulos), len(enlaces), len(imagenes))
        titulos, enlaces, imagenes = titulos[:n], enlaces[:n], imagenes[:n]

        df = pd.DataFrame({
            "portal": ["Infobae"] * n,
            "titulo": titulos,
            "enlace": enlaces,
            "imagen": imagenes
        })

        if debug:
            print(f"{n} noticias encontradas en Infobae")
            print(df.head())

        return df

    except Exception as e:
        print("Error en extraer_noticias_infobae_scraping:", e)
        return pd.DataFrame(columns=["portal", "titulo", "enlace", "imagen"])