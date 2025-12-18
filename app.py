import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Dashboard Distrito 208", layout="wide")

@st.cache_data
def load_data():
    # El archivo generado previamente en Colab
    df = pd.read_csv('cupcodigos_con_estado_2025.csv')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['estado'] = df['estado'].fillna('Pendiente').replace('', 'Pendiente')
    # Extraer el nombre del mes
    df['mes'] = df['created_at'].dt.month_name()
    return df

df = load_data()

# --- BARRA LATERAL (ASIDE) ---
st.sidebar.header("🔍 Filtros de Búsqueda")

# Filtro fijo inicial para Distrito 208
df_base = df[df['distrito'].astype(str) == '208'].copy()

# 1. Filtro de Ruta
rutas = sorted(df_base['ruta'].astype(str).unique())
ruta_sel = st.sidebar.multiselect("Seleccionar Ruta", rutas)

# 2. Filtro de Cadena
cadenas = sorted(df_base['cadena'].astype(str).unique())
cadena_sel = st.sidebar.multiselect("Seleccionar Cadena", cadenas)

# 3. Filtro de Descripción (Producto)
productos = sorted(df_base['descripcion'].astype(str).unique())
prod_sel = st.sidebar.multiselect("Seleccionar Producto", productos)

# 4. Filtro de Mes
meses = df_base['mes'].unique()
mes_sel = st.sidebar.multiselect("Seleccionar Mes", meses)

# 5. Filtro de Médico (usando columna id_clientes)
medicos = sorted(df_base['id_clientes'].astype(str).unique())
medico_sel = st.sidebar.multiselect("Seleccionar Médico", medicos)

# --- APLICACIÓN DE FILTROS DINÁMICOS ---
df_filtrado = df_base.copy()

if ruta_sel:
    df_filtrado = df_filtrado[df_filtrado['ruta'].astype(str).isin(ruta_sel)]
if cadena_sel:
    df_filtrado = df_filtrado[df_filtrado['cadena'].astype(str).isin(cadena_sel)]
if prod_sel:
    df_filtrado = df_filtrado[df_filtrado['descripcion'].astype(str).isin(prod_sel)]
if mes_sel:
    df_filtrado = df_filtrado[df_filtrado['mes'].isin(mes_sel)]
if medico_sel:
    df_filtrado = df_filtrado[df_filtrado['id_clientes'].astype(str).isin(medico_sel)]

# --- CUERPO PRINCIPAL ---
st.title("📋 Gestión de Cheques - Distrito 208")

# --- SECCIÓN DE KPIs CON BARRA DE EFECTIVIDAD ---
total = len(df_filtrado)
redimidos = len(df_filtrado[df_filtrado['estado'] == 'redimido'])
pendientes = total - redimidos
efectividad = (redimidos / total) if total > 0 else 0

c1, c2, c3, c4 = st.columns([1, 1, 1, 2]) # El cuarto es más ancho para la barra

with c1:
    st.metric("Total Generados", f"{total:,}")
with c2:
    st.metric("Redimidos ✅", f"{redimidos:,}")
with c3:
    st.metric("Pendientes ⏳", f"{pendientes:,}")
with c4:
    st.write(f"**% Efectividad: {efectividad*100:.1f}%**")
    st.progress(efectividad)

st.divider()

# --- VISUALIZACIONES ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Estado General de Redención")
    fig_pie = px.pie(df_filtrado, names='estado', hole=0.4, 
                     color='estado',
                     color_discrete_map={'redimido':'#00CC96', 'Pendiente':'#EF553B'})
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("Top 10 Médicos con más Generación")
    top_medicos = df_filtrado['id_clientes'].value_counts().head(10).reset_index()
    fig_med = px.bar(top_medicos, x='count', y='id_clientes', orientation='h',
                     labels={'count':'Cupones', 'id_clientes':'Médico'},
                     color_discrete_sequence=['#636EFA'])
    fig_med.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_med, use_container_width=True)

# --- TABLA DE DATOS ---
st.subheader("🔍 Detalle de Registros Filtrados")
st.dataframe(df_filtrado[['created_at', 'id_clientes', 'descripcion', 'cadena', 'ruta', 'estado']], 
             use_container_width=True)

# Botón de exportación
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Descargar CSV Filtrado",
    data=csv,
    file_name='reporte_distrito_208.csv',
    mime='text/csv',
)
