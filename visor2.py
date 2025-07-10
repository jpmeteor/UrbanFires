import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster

# Configuración de la app
st.set_page_config(layout="wide", page_title="Visor de Incendios Urbanos")
st.title("🔥 Visor de Incendios Urbanos - Lima Metropolitana")
st.markdown("Actualizado automáticamente desde `df_hoy.xlsx`")

# Ruta del archivo Excel (local, cambiar si es necesario)
excel_path = "df_hoy.xlsx"

# Cargar datos
@st.cache_data(show_spinner=False)
def cargar_datos(path):
    df = pd.read_excel(path)
    column_rename_map = {
        'Latitude': 'Latitud',
        'Longitude': 'Longitud',
        '#Máquinas': 'Num_Maquinas',
        'Elevation (m)': 'Elevacion',
        'Fecha y hora': 'Fecha',
        'Ver Mapa URL': 'URL'
    }
    df = df.rename(columns=column_rename_map)
    df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
    df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
    df = df.dropna(subset=['Latitud', 'Longitud'])
    return df

# Leer datos
try:
    df = cargar_datos(excel_path)
except FileNotFoundError:
    st.error("No se encontró el archivo df_hoy.xlsx. Verifica la ruta.")
    st.stop()

# Convertir a GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df['Longitud'], df['Latitud']),
    crs="EPSG:4326"
)

# Crear mapa centrado en Lima
m = folium.Map(location=[-12.0464, -77.0428], zoom_start=11, control_scale=True)
marker_cluster = MarkerCluster().add_to(m)

# Agregar puntos
for _, row in gdf.iterrows():
    popup_text = f"""
    <strong>Nro Parte:</strong> {row['Nro Parte']}<br>
    <strong>Fecha:</strong> {row['Fecha']}<br>
    <strong>Dirección:</strong> {row['Dirección / Distrito']}<br>
    <strong>Tipo:</strong> {row['Tipo']}<br>
    <strong>Estado:</strong> {row['Estado']}<br>
    <strong>Máquinas:</strong> {row['Máquinas']}<br>
    <strong>Elevación:</strong> {row['Elevacion']} m<br>
    <strong>#Máquinas:</strong> {row['Num_Maquinas']}<br>
    <a href='{row['URL']}' target='_blank'>Ver Mapa</a>
    """
    folium.CircleMarker(
        location=[row['Latitud'], row['Longitud']],
        radius=6,
        color='crimson',
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(marker_cluster)

# Mostrar mapa
tab1, tab2 = st.tabs(["🗺️ Mapa", "📋 Tabla"])

with tab1:
    folium_static(m, width=1000, height=600)

with tab2:
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True)
