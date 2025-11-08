import requests
from bs4 import BeautifulSoup
import pandas as pd

def extraer_noticias_lanacion(debug=False):
    url = "https://www.lanacion.com.ar/ultimas-noticias/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Buscar los artículos (nuevo selector)
        articulos = soup.select("div.com-title a, article.mod-article a")

        titulos, enlaces, imagenes = [], [], []

        for link_tag in articulos:
            titulo = link_tag.get("title") or link_tag.text.strip()
            enlace = link_tag.get("href")

            if not enlace or not titulo:
                continue

            if not enlace.startswith("http"):
                enlace = f"https://www.lanacion.com.ar{enlace}"

            # Buscar imagen asociada (opcional)
            art_parent = link_tag.find_parent("article")
            img_tag = art_parent.find("img") if art_parent else None
            imagen = None
            if img_tag:
                imagen = img_tag.get("data-src") or img_tag.get("src")

            titulos.append(titulo)
            enlaces.append(enlace)
            imagenes.append(imagen)

        # Recortar al mínimo número común
        n = min(len(titulos), len(enlaces))
        df = pd.DataFrame({
            "portal": ["La Nación"] * n,
            "titulo": titulos[:n],
            "enlace": enlaces[:n],
            "imagen": imagenes[:n] if len(imagenes) >= n else [None]*n
        })

        if debug:
            print(f"{n} noticias obtenidas de La Nación")
            print(df.head())

        return df

    except Exception as e:
        print("Error en extraer_noticias_lanacion:", e)
        return pd.DataFrame(columns=["portal", "titulo", "enlace", "imagen"])
