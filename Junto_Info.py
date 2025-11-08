import pandas as pd
from Funcion_Clarin import extraer_noticias_clarin
from Funcion_Infobae import extraer_noticias_infobae, extraer_noticias_infobae_scraping
from Funcion_LN import   extraer_noticias_lanacion

def obtener_todas_las_noticias(debug=False):
    dfs = []

    for func in [extraer_noticias_clarin, extraer_noticias_infobae,extraer_noticias_lanacion]:
        try:
            df = func(debug)
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            if debug:
                print(f"Error ejecutando {func.__name__}: {e}")
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame(columns=["portal", "titulo", "enlace", "imagen"])

if __name__ == "__main__":
    noticias = obtener_todas_las_noticias()
    print(noticias.head(50))

