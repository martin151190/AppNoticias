import streamlit as st
import pandas as pd
import requests
from Funcion_Infobae import extraer_noticias_infobae_scraping
from Funcion_Clarin import extraer_noticias_clarin
from Funcion_LN import extraer_noticias_lanacion

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(page_title="🗞️ Noticias Argentinas", layout="wide")

# ---------------- ESTILOS PERSONALIZADOS ----------------
# Se mantiene el estilo que enviaste.
st.markdown("""
<style>
body {
    background-color: #f9fafb;
}
h1 {
    color: #1a237e;
    text-align: center;
    font-weight: 700;
    margin-bottom: 0.2em;
}
h2 {
    color: #283593;
    font-weight: 600;
    margin-top: 0; /* Ajustado para pestañas */
}
.cotizaciones {
    background-color: #1a237e;
    color: white;
    padding: 10px 0;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    text-align: center;
    font-size: 1.05rem;
    margin-bottom: 25px;
}
.cotizaciones strong {
    color: #bbdefb;
}
.news-card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    min-height: 250px; /* Asegura altura mínima para consistencia */
}
.news-card img {
    border-radius: 10px;
    margin-bottom: 8px;
}
/* Estilo para las pestañas de Streamlit */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px; /* Espacio entre pestañas */
    padding-bottom: 10px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #f0f2f6; /* Fondo de la pestaña */
    border-radius: 8px;
    padding: 10px 15px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCIÓN COTIZACIONES ----------------
@st.cache_data(ttl=300)
def obtener_cotizaciones():
    try:
        resp = requests.get("https://dolarapi.com/v1/dolares", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        d_oficial = next((x for x in data if x["nombre"] == "Oficial"), None)
        d_blue    = next((x for x in data if x["nombre"] == "Blue"), None)
        d_mep     = next((x for x in data if x["nombre"] == "Bolsa"), None)
        
        riesgo_pais = "N/D"
        
        return {
            "Oficial": d_oficial["venta"] if d_oficial else None,
            "Blue":    d_blue["venta"]    if d_blue    else None,
            "MEP":     d_mep["venta"]     if d_mep     else None,
            "Riesgo País": riesgo_pais
        }
    except Exception:
        return {"Oficial": None, "Blue": None, "MEP": None, "Riesgo País": "N/D"}

cot = obtener_cotizaciones()

# ---------------- CABECERA (Cotizaciones y Título) ----------------
st.markdown(f"""
<div class="cotizaciones">
  💵 <strong>Dólar Oficial:</strong> ${cot['Oficial']} &nbsp;|&nbsp;
  💸 <strong>Dólar Blue:</strong> ${cot['Blue']} &nbsp;|&nbsp;
  📊 <strong>Dólar MEP:</strong> ${cot['MEP']} &nbsp;|&nbsp;
  📉 <strong>Riesgo País:</strong> {cot['Riesgo País']}
</div>
""", unsafe_allow_html=True)

st.title("🗞️ Top 5 de la prensa argentina")

# ---------------- BOTÓN PARA RECARGAR ----------------
if st.button("🔄 Recargar noticias"):
    st.cache_data.clear()
    st.experimental_rerun() # Fuerza la recarga de la página

# ---------------- OBTENER NOTICIAS ----------------
@st.cache_data(ttl=3600)
def obtener_todas():
    # Asegúrate de que estas funciones devuelvan un DataFrame válido, incluso vacío.
    df_infobae = extraer_noticias_infobae_scraping()
    df_clarin = extraer_noticias_clarin()
    df_ln = extraer_noticias_lanacion()
    return pd.concat([df_infobae, df_clarin, df_ln], ignore_index=True)

df = obtener_todas()

# ---------------- MOSTRAR NOTICIAS EN PESTAÑAS (CARRUSEL SIMULADO) ----------------

if df.empty:
    st.warning("⚠️ No se pudieron obtener noticias en este momento.")
else:
    # Agrupamos los datos por portal
    grouped_df = df.groupby("portal")
    
    # Creamos la lista de pestañas (el "carrusel")
    portal_nombres = list(grouped_df.groups.keys())
    tabs = st.tabs(portal_nombres)
    
    for i, portal in enumerate(portal_nombres):
        # Cada pestaña es un "slide" del carrusel
        with tabs[i]:
            subdf = grouped_df.get_group(portal)
            
            # Título dentro de la pestaña (opcional, si quieres un encabezado dentro del contenido)
            st.markdown(f"<h2>{portal}</h2>", unsafe_allow_html=True)

            # Usamos la lógica de columnas dentro de la pestaña
            cols = st.columns(2)
            
            # Mostramos las primeras 5 noticias en dos columnas alternadas
            for j, (_, row) in enumerate(subdf.head(5).iterrows()):
                with cols[j % 2]:
                    st.markdown('<div class="news-card">', unsafe_allow_html=True)
                    
                    # Mostrar imagen si está disponible
                    # Nota: Debes asegurarte que 'imagen' contiene URLs válidas y accesibles.
                    if row.get("imagen"): 
                        try:
                            st.image(str(row["imagen"]), use_container_width=True)
                        except Exception:
                            # st.info(f"No se pudo cargar la imagen para {portal}.")
                            pass

                    # Título y enlace
                    st.markdown(f"**[{row['titulo']}]({row['enlace']})**", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)