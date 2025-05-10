import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit.components.v1 import html
from pathlib import Path
import base64

# ABSOLUTAMENTE EL PRIMER COMANDO STREAMLIT
st.set_page_config(
    layout="wide",
    page_title="Dashboard Bangkok",
    page_icon="🏨"
)

# Cargar CSS (después de set_page_config)
def load_css():
    with open("estilos_pre.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# --- Prueba de configuración ---
st.button("Botón de prueba")
st.success("Mensaje de éxito")

# Función para convertir imágenes a base64
def img_to_base64(img_path):
    try:
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Imagen no encontrada: {img_path}")
        return ""

# Función para cargar CSS
def load_css(file_name):
    try:
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Archivo CSS no encontrado: {file_name}")

# Definimos la instancia con cache para la carga de datos
@st.cache_resource
def load_data():
    # Lectura del archivo csv
    df = pd.read_csv("Datos_Limpios_de_bangkook.csv", index_col='host_name')
    
    # Selecciono las columnas tipo numericas del dataframe
    numeric_df = df.select_dtypes(['float', 'int'])
    numeric_cols = numeric_df.columns

    # Selecciono las columnas tipo texto del dataframe
    text_df = df.select_dtypes(['object'])
    text_cols = text_df.columns

    # Selecciono algunas columnas categoricas
    categorical_column_sex = df['host_is_superhost']
    unique_categories_sex = categorical_column_sex.unique()

    return df, numeric_cols, text_cols, unique_categories_sex, numeric_df

# Cargo los datos obtenidos de la función "load_data"
df, numeric_cols, text_cols, unique_categories_sex, numeric_df = load_data()

# Configuración de la aplicación Streamlit
st.subheader("La ciudad de los Angeles")

# Menú de navegación principal
View = st.sidebar.selectbox(
    "Selecciona una de las siguientes opciones:",
    ["Pagina_Principal", "Analisis_de_Frecuencias", "Diagramas_de_Dispersion", "Regresion_lineal_simple", "Regresion_lineal_multiple","Analisis_Categorico"],
    index=0
)

# VISTA 0 - PÁGINA PRINCIPAL (HTML)
if View == "Pagina_Principal":
    # Cargar CSS primero
    load_css("estilos_pre.css")
    
    try:
        # Leer y procesar el HTML
        html_content = Path("Presentacion.html").read_text(encoding="utf-8")
        
        # Reemplazar la imagen con base64
        html_content = html_content.replace(
            'src="logo.png"',
            f'src="data:image/png;base64,{img_to_base64("logo.png")}"'
        )
        
        # Mostrar el HTML
        st.components.v1.html(html_content, height=800, scrolling=True)
        
    except Exception as e:
        st.error(f"Error al cargar la presentación: {str(e)}")
        st.info("Contenido alternativo:")
        st.write("""
        ## Acerca de Bangkok
        Explora esta maravillosa ciudad a través de nuestras herramientas.
        """)

# CONTENIDO DE LA VISTA 1
elif View == "Analisis_de_Frecuencias":
    st.title("BANGKOK - ANÁLISIS DE FRECUENCIAS")
    st.header("Tablas de Frecuencia por Intervalos")
    
    # Widgets en sidebar
    st.sidebar.header("Opciones de Configuración")
    
    # 1. Selección de variable numérica
    numeric_var = st.sidebar.selectbox(
        "Seleccione la variable numérica:",
        options=numeric_cols,
        index=0
    )
    
    # 2. Selección de número de intervalos (bins)
    bins = st.sidebar.slider(
        "Número de intervalos:",
        min_value=3,
        max_value=20,
        value=5,
        step=1
    )
    
    # 3. Selección de tipo de gráfico
    graph_type = st.sidebar.radio(
        "Tipo de gráfico:",
        ["Barras", "Pastel", "Histograma"],
        index=0
    )
    
    # 4. Checkbox para mostrar raw data
    show_raw = st.sidebar.checkbox("Mostrar datos originales")
    
    # Mostrar datos originales si se selecciona
    if show_raw:
        st.subheader("Datos Originales")
        st.dataframe(df[[numeric_var]].describe().T)
        st.dataframe(df[[numeric_var]].head(10))
    
    # Crear tabla de frecuencias
    st.subheader(f"Tabla de Frecuencias para: {numeric_var}")
    
    # Calcular los intervalos
    min_val = df[numeric_var].min()
    max_val = df[numeric_var].max()
    
    # Crear los intervalos y etiquetas
    intervals = pd.interval_range(
        start=min_val,
        end=max_val,
        periods=bins,
        closed='right'
    )
    labels = [f"{intv.left:.2f} - {intv.right:.2f}" for intv in intervals]
    
    # Asignar cada valor a su intervalo
    df['Intervalo'] = pd.cut(df[numeric_var], bins=bins, labels=labels)
    
    # Crear tabla de frecuencias
    freq_table = df['Intervalo'].value_counts().sort_index().reset_index()
    freq_table.columns = ['Intervalo', 'Frecuencia Absoluta']
    freq_table['Frecuencia Relativa'] = (freq_table['Frecuencia Absoluta'] / len(df)) * 100
    freq_table['Frecuencia Relativa'] = freq_table['Frecuencia Relativa'].round(2)
    
    # Mostrar tabla con estilo
    st.dataframe(
        freq_table.style
        .background_gradient(subset=['Frecuencia Absoluta'], cmap='Blues')
        .format({'Frecuencia Relativa': '{:.2f}%'})
        .set_properties(**{'text-align': 'center'})
    )
    
    # Gráfico según selección del usuario
    st.subheader(f"Visualización: {graph_type}")
    
    if graph_type == "Barras":
        fig = px.bar(
            freq_table,
            x='Intervalo',
            y='Frecuencia Absoluta',
            color='Intervalo',
            text='Frecuencia Absoluta',
            title=f"Distribución de {numeric_var} (Barras)"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Intervalos",
            yaxis_title="Frecuencia",
            showlegend=False
        )
        
    elif graph_type == "Pastel":
        fig = px.pie(
            freq_table,
            names='Intervalo',
            values='Frecuencia Absoluta',
            title=f"Distribución de {numeric_var} (Pastel)",
            hole=0.3
        )
        fig.update_traces(
            textinfo='percent+label',
            textposition='inside'
        )
        
    else:  # Histograma
        fig = px.histogram(
            df,
            x=numeric_var,
            nbins=bins,
            title=f"Distribución de {numeric_var} (Histograma)",
            color_discrete_sequence=['#636EFA']
        )
        fig.update_layout(
            bargap=0.1,
            xaxis_title=numeric_var,
            yaxis_title="Frecuencia"
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estadísticas descriptivas
    with st.expander("Ver estadísticas completas"):
        st.subheader("Estadísticas Descriptivas")
        stats = df[numeric_var].describe().to_frame().T
        st.dataframe(
            stats.style
            .format("{:.2f}")
            .background_gradient(cmap='YlOrRd')
        )



# CONTENIDO DE LA VISTA 2
elif View == "Diagramas_de_Dispersion":
    st.title("BANGKOK - Diagramas de Dispersion")
    st.header("¿Que son?")
    st.subheader("los diagramas de dispersión son herramientas muy utiles para explorar y comprender cómo dos variables se comportan permitiendonosobservar relaciones, patrones y posibles anomalías.")
    
    # Selectores de ejes
    x_selected = st.sidebar.selectbox(
        label="Variable X", 
        options=numeric_cols
    )
    y_selected = st.sidebar.selectbox(
        label="Variable Y", 
        options=numeric_cols
    )
    
    # GRAPH 2: SCATTERPLOT
    figure2 = px.scatter(
        data_frame=df, 
        x=x_selected, 
        y=y_selected, 
        title=f'Relación entre {x_selected} y {y_selected}',
        color='host_is_superhost'
    )
    st.plotly_chart(figure2, use_container_width=True)

# CONTENIDO DE LA VISTA 3
elif View == "Regresion_lineal_simple":
    st.title("BANGKOK ")
    st.header("algo de informacion")
    st.subheader("-------------------")
    
    # Selectores de variables
    Variable_cat = st.sidebar.selectbox(
        label="Variable Categórica", 
        options=text_cols
    )
    Variable_num = st.sidebar.selectbox(
        label="Variable Numérica", 
        options=numeric_cols
    )
    
    # GRAPH 3: PIEPLOT
    figure3 = px.pie(
        data_frame=df, 
        names=df[Variable_cat], 
        values=df[Variable_num], 
        title=f'Distribución de {Variable_num} por {Variable_cat}',
        width=1600, 
        height=600
    )
    st.plotly_chart(figure3, use_container_width=True)

# CONTENIDO DE LA VISTA 4
elif View == "Regresion_lineal_multiple":
    st.title("BANGKOK")
    st.header("un poco de informacion")
    st.subheader("-----------------------------")
    
    # Selectores de variables
    Variable_cat = st.sidebar.selectbox(
        label="Variable Categórica", 
        options=text_cols
    )
    Variable_num = st.sidebar.selectbox(
        label="Variable Numérica", 
        options=numeric_cols
    )
    
    # GRAPH 4: BARPLOT
    figure4 = px.bar(
        data_frame=df, 
        x=df[Variable_cat], 
        y=df[Variable_num], 
        title=f'Comparación de {Variable_num} por {Variable_cat}',
        color=df[Variable_cat]
    )
    figure4.update_xaxes(automargin=True)
    figure4.update_yaxes(automargin=True)
    st.plotly_chart(figure4, use_container_width=True)
