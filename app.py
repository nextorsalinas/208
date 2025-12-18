import streamlit as st
import pandas as pd
import plotly.express as px

# Función para cargar datos con manejo de errores
@st.cache_data
def load_data():
    try:
        # Asegúrate de que el CSV esté en la raíz de tu repositorio
        df = pd.read_csv('cupcodigos_con_estado_2025.csv')
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['estado'] = df['estado'].fillna('Pendiente').replace('', 'Pendiente')
        return df
    except FileNotFoundError:
        st.error("Archivo de datos no encontrado en el repositorio.")
        return None

df = load_data()

if df is not None:
    # --- Título y Filtros ---
    st.title("📊 Control de Cheques - Distrito 208")
    
    # Filtro automático para el distrito 208
    df_208 = df[df['distrito'].astype(str) == '208'].copy()
    
    if df_208.empty:
        st.warning("No se encontraron datos para el Distrito 208.")
    else:
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        total = len(df_208)
        redimidos = len(df_208[df_208['estado'] == 'redimido'])
        
        col1.metric("Total Cheques", f"{total}")
        col2.metric("Redimidos", f"{redimidos}")
        col3.metric("Eficiencia", f"{(redimidos/total*100):.1f}%")

        # Gráfico de barras por Cadena
        st.subheader("Redención por Cadena en Distrito 208")
        fig = px.bar(df_208, x='cadena', color='estado', barmode='group')
        st.plotly_chart(fig, use_container_width=True)

        # Tabla interactiva
        st.subheader("Listado Detallado")
        st.dataframe(df_208, use_container_width=True)
