import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Dashboard Distrito 208", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('cupcodigos_con_estado_2025.csv')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['estado'] = df['estado'].fillna('Pendiente').replace('', 'Pendiente')
    df['mes_num'] = df['created_at'].dt.month
    df['mes'] = df['created_at'].dt.month_name()
    return df

df = load_data()

# --- BARRA LATERAL (ASIDE) ---
st.sidebar.header("Filtros de Búsqueda")
df_base = df[df['distrito'].astype(str) == '208'].copy()

ruta_sel = st.sidebar.multiselect("Seleccionar Ruta", sorted(df_base['ruta'].astype(str).unique()))
cadena_sel = st.sidebar.multiselect("Seleccionar Cadena", sorted(df_base['cadena'].astype(str).unique()))
prod_sel = st.sidebar.multiselect("Seleccionar Producto", sorted(df_base['descripcion'].astype(str).unique()))
meses_ordenados = df_base.sort_values('mes_num')['mes'].unique()
mes_sel = st.sidebar.multiselect("Seleccionar Mes", meses_ordenados)
medico_sel = st.sidebar.multiselect("Seleccionar Médico", sorted(df_base['id_clientes'].astype(str).unique()))

# Aplicación de filtros
df_filtrado = df_base.copy()
if ruta_sel: df_filtrado = df_filtrado[df_filtrado['ruta'].astype(str).isin(ruta_sel)]
if cadena_sel: df_filtrado = df_filtrado[df_filtrado['cadena'].astype(str).isin(cadena_sel)]
if prod_sel: df_filtrado = df_filtrado[df_filtrado['descripcion'].astype(str).isin(prod_sel)]
if mes_sel: df_filtrado = df_filtrado[df_filtrado['mes'].isin(mes_sel)]
if medico_sel: df_filtrado = df_filtrado[df_filtrado['id_clientes'].astype(str).isin(medico_sel)]

# --- CUERPO PRINCIPAL ---
st.title("Gestión de Cheques - Distrito 208")

# --- SECCIÓN DE KPIs COMPACTA ---
total = len(df_filtrado)
redimidos = len(df_filtrado[df_filtrado['estado'] == 'redimido'])
pendientes = total - redimidos
efectividad = (redimidos / total) if total > 0 else 0

# Definimos las columnas (c4 será donde pondremos la métrica + la gráfica pequeña)
c1, c2, c3, c4 = st.columns([1, 1, 1, 2])

with c1:
    st.metric("Total Generados", f"{total:,}")
with c2:
    st.metric("Redimidos ✅", f"{redimidos:,}")
with c3:
    st.metric("Pendientes ⏳", f"{pendientes:,}")

with c4:
    # Mostramos el % y la barra
    st.write(f"**Efectividad: {efectividad*100:.1f}%**")
    st.progress(efectividad)
    
    # --- GRÁFICO LINEAL MINIATURA (Abajo de la efectividad) ---
    df_linea = df_filtrado.groupby(['mes_num', 'mes']).size().reset_index(name='cantidad')
    df_linea = df_linea.sort_values('mes_num')
    
    if not df_linea.empty:
        fig_mini_line = px.line(df_linea, x='mes', y='cantidad', markers=True,
                               template="plotly_white", height=140) # Altura reducida
        fig_mini_line.update_layout(margin=dict(l=0, r=0, t=0, b=0), # Quitar márgenes
                                    xaxis_title=None, yaxis_title=None)
        fig_mini_line.update_traces(line_color="#636EFA")
        st.plotly_chart(fig_mini_line, use_container_width=True, config={'displayModeBar': False})

st.divider()

# --- VISUALIZACIONES INFERIORES ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Estado de Redención")
    fig_pie = px.pie(df_filtrado, names='estado', hole=0.4, color='estado',
                     color_discrete_map={'redimido':'#00CC96', 'Pendiente':'#EF553B'})
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("Top 10 Médicos")
    top_medicos = df_filtrado['id_clientes'].value_counts().head(10).reset_index()
    fig_med = px.bar(top_medicos, x='count', y='id_clientes', orientation='h',
                     labels={'count':'Cupones', 'id_clientes':'Médico'})
    fig_med.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_med, use_container_width=True)

# --- TABLA ---
st.subheader("🔍 Detalle de Registros")
st.dataframe(df_filtrado[['created_at', 'id_clientes', 'descripcion', 'cadena', 'ruta', 'estado']], use_container_width=True)

# Botón de exportación
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(label="📥 Descargar CSV", data=csv, file_name='reporte_208.csv', mime='text/csv')
