
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (Criterio 2.1.1 - Layout Wide)
st.set_page_config(page_title="Dashboard de Streaming Musical", layout="wide")

# Título y contexto del Dashboard (Estructura Narrativa - Contexto)
st.title("🎧 Análisis de Tráfico de Servidores - Plataforma de Streaming Musical")
st.markdown("Este dashboard analiza el comportamiento de los usuarios y su impacto en la infraestructura de servidores para optimizar la asignación de recursos.")

# 2. Carga de Datos
@st.cache_data
def load_data():
    # Asegúrate de que el archivo CSV esté en la misma carpeta que este script
    df = pd.read_csv('streaming_trafico_limpio.csv')
    # Extraer solo la hora como número para facilitar filtros
    df['Hora_Num'] = df['Hora'].str.split(':').str[0].astype(int)
    return df

df = load_data()

# 3. Sidebar - Filtros Interactivos (Interactividad con propósito)
st.sidebar.header("Filtros de Análisis")

comuna_seleccionada = st.sidebar.multiselect(
    "Selecciona Comuna:",
    options=df['Comuna'].unique(),
    default=df['Comuna'].unique()
)

dispositivo_seleccionado = st.sidebar.multiselect(
    "Selecciona Dispositivo:",
    options=df['Dispositivo'].unique(),
    default=df['Dispositivo'].unique()
)

# NUEVO FILTRO: Género Musical
genero_seleccionado = st.sidebar.multiselect(
    "Selecciona Género Musical:",
    options=df['Genero_Musical'].unique(),
    default=df['Genero_Musical'].unique()
)

# Aplicar filtros cruzados
df_filtrado = df[
    (df['Comuna'].isin(comuna_seleccionada)) & 
    (df['Dispositivo'].isin(dispositivo_seleccionado)) &
    (df['Genero_Musical'].isin(genero_seleccionado))
]

# 4. KPIs Principales
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total de Sesiones Analizadas", value=len(df_filtrado))
with col2:
    carga_promedio = round(df_filtrado['Carga_Servidor_Pct'].mean(), 2)
    st.metric(label="Carga Promedio de Servidores", value=f"{carga_promedio}%")
with col3:
    if not df_filtrado.empty:
        genero_top = df_filtrado['Genero_Musical'].mode()[0]
    else:
        genero_top = "N/A"
    st.metric(label="Género Más Escuchado", value=genero_top)

st.divider()

# 5. Visualizaciones (Criterio 2.1.3 - Niveles de complejidad)

col_graf_1, col_graf_2 = st.columns(2)

with col_graf_1:
    # Conflicto: ¿A qué hora se saturan los servidores? (Evolución)
    st.subheader("Carga de Servidores por Hora del Día")
    if not df_filtrado.empty:
        carga_por_hora = df_filtrado.groupby('Hora_Num')['Carga_Servidor_Pct'].mean().reset_index()
        fig_line = px.line(carga_por_hora, x='Hora_Num', y='Carga_Servidor_Pct', 
                           markers=True, title="Evolución promedio de carga",
                           labels={'Hora_Num': 'Hora del Día', 'Carga_Servidor_Pct': 'Carga del Servidor (%)'})
        # Atributo preatentivo: Línea de advertencia
        fig_line.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="Pico Crítico (>75%)")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros actuales.")

with col_graf_2:
    # Composición: ¿Qué dispositivos generan más tráfico?
    st.subheader("Tráfico por Tipo de Dispositivo")
    if not df_filtrado.empty:
        trafico_disp = df_filtrado.groupby('Dispositivo')['Carga_Servidor_Pct'].mean().reset_index()
        fig_bar = px.bar(trafico_disp, x='Dispositivo', y='Carga_Servidor_Pct', 
                         color='Dispositivo', title="Carga promedio por Dispositivo")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros actuales.")

st.divider()

col_graf_3, col_graf_4 = st.columns(2)

with col_graf_3:
    # Relación: Duración de sesión vs Carga (Dispersión)
    st.subheader("Relación: Duración de la Sesión vs Carga")
    if not df_filtrado.empty:
        fig_scatter = px.scatter(df_filtrado, x='Duracion_Minutos', y='Carga_Servidor_Pct', 
                                 color='Genero_Musical', opacity=0.6,
                                 title="¿Más minutos significa más carga?")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros actuales.")

with col_graf_4:
    # Resolución: Qué géneros optimizar
    st.subheader("Top Géneros Musicales por Demanda")
    if not df_filtrado.empty:
        demanda_genero = df_filtrado['Genero_Musical'].value_counts().reset_index()
        demanda_genero.columns = ['Género', 'Sesiones']
        fig_pie = px.pie(demanda_genero, names='Género', values='Sesiones', hole=0.4,
                         title="Distribución de Sesiones por Género")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros actuales.")
