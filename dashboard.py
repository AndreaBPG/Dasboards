#!/usr/bin/env python
# coding: utf-8

# In[39]:


import streamlit as st # para la creación del dashboard
import numpy as np # para cálculos numéricos
import pandas as pd # para manipulación de datos
import plotly.express as px # para gráficos interactivos
import matplotlib.pyplot as plt # para gráficos estáticos
import plotly.graph_objects as go # para gráficos avanzados


# ##Cargando bases de datos

# In[40]:


path = "datos_sw.xlsx"#Cargando datos
#leyendo hojas
df= pd.read_excel(path)


# ##Arreglos de la base de datos

# In[41]:


#===============================================================
# Convertir a minúscula y estandarizar valores, procesamiento de datos
#================================================================

#convertir texto a minuscula y limpiar espacios
cols_texto = ['id_estatus_servicio_cliente', 'id_municipio_cliente','id_plan_internet_cliente']
for col in cols_texto:
    df[col] = df[col].astype(str).str.lower().str.strip()

#normalizar nombres de columnas

df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
df.head()


# In[42]:


df.set_index('codigo_cliente', inplace=True) #para colocar los indeces id_cliente como los indes de la tabla en panda
df.head()


# ##extraer fechas para usarlos

# In[43]:


# Extraer componentes de la fecha columnas separadas con datos de las fechas instalacion
df['dia'] = df['f_instalacion_cliente'].dt.day #dia
df['mes'] = df['f_instalacion_cliente'].dt.month #mes
df['anio'] = df['f_instalacion_cliente'].dt.year #año


# In[44]:


df.head()


# #Validacoin de datos

# In[45]:


# Revisar valores nulos
df.isnull().sum()
# Revisar valores únicos en columnas clave
df['id_municipio_cliente'].unique()
df['id_estatus_servicio_cliente'].unique()
df['anio'].unique()
df['mes'].unique()
df['dia'].unique()


# ##Cargando css exterior personalizado

# In[46]:


#===========================
# Cargar CSS externon personalizado
#==========================

def cargar_css(ruta="style.css"):
    with open(ruta, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Llamada a la función
cargar_css("style.css")


# In[47]:


#===========================================
#Configurar la página principal del dashboard
#==========================================

st.set_page_config(page_title="Soluciones Wireless", layout="wide", page_icon="img/logoSolucionW.png")


# ##Menu

# In[48]:


#===============================
# Menú lateral principal con navegación entre páginas
#================================
with st.sidebar:
    st.image("img/logoSolucionW.png", width=180)

#opciones para ir a ver los dashboard
pagina = st.sidebar.radio("Ir a:", ["Dashboard de Clientes", "Dashboard Facturacion"])


# ##Paginas

# In[ ]:


# ================================
# Página: Dashboard de Clientes
# ================================

# 🔧 Reducir el espacio superior del dashboard
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5em !important;  /* Puedes ajustar a 0rem, 0.5rem, 1rem según lo que necesites */
    }
    </style>
    """, unsafe_allow_html=True)

if pagina == "Dashboard de Clientes":

#===============================
# 🧩 Título del dashboard
#===============================

    st.markdown("""
    <style>
       .dashboard-title {
        text-align: center;   # Centrar el texto
        font-family: 'Montserrat', sans-serif;    # Fuente moderna
        font-size: 10px;    # Tamaño pequeño
        font-weight: 600;   # Negrita
        color: #333333;     # Gris oscuro
        margin-bottom: 10px;  # Espacio inferior
    }
    </style>
    <h1 class="dashboard-title">Dashboard de Clientes</h1> 
    """, unsafe_allow_html=True) #nombre del dashboard

#================================
#Filtros del Menu
#================================

    # Extraer años únicos desde la base y ordenarlos
    anios_disponibles = sorted(df['anio'].unique())

    # Seleccionar el año más reciente como predeterminado
    anio_tope = max(anios_disponibles)

    # 🎛️ Filtros especificos
    st.sidebar.subheader("Filtros de Cliente")

    # Filtro por estado del cliente
    cliente = st.sidebar.selectbox("Clientes:", ["Todo", "activo", "suspendido", "retirado"])

    # Filtro por municipio
    ubicacion = st.sidebar.selectbox("Ubicación/Municipo:", ["Todo", "bolivar", "urbaneja", "sotillo"])

    # Filtro por año (con año más reciente preseleccionado)
    fecha = st.sidebar.selectbox("Año:", options=anios_disponibles,
    index=anios_disponibles.index(anio_tope))

    # Filtro por mes (en español)
    mes = st.sidebar.selectbox("Mes:", [
        "Todo", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
        "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ])


#================================
# 🧮 Aplicar filtros
#================================

    # Copiar el DataFrame original para aplicar filtros
    df_filtrado = df.copy()

    # Filtrar por año seleccionado
    df_filtrado = df_filtrado[df_filtrado['anio'] == fecha]

     # Filtrar por estado si no es "Todo"
    if cliente != "Todo":
        df_filtrado = df_filtrado[df_filtrado["id_estatus_servicio_cliente"] == cliente]

    # Filtrar por municipio si no es "Todo"
    if ubicacion != "Todo":
        df_filtrado = df_filtrado[df_filtrado["id_municipio_cliente"] == ubicacion]    

    # Filtrar por mes si se seleccionó uno específico
    if mes != "Todo":
      # Traducir nombre del mes al formato inglés que usa pandas
     MESES = {"Enero": "January", "Febrero": "February", "Marzo": "March", "Abril": "April",
     "Mayo": "May", "Junio": "June", "Julio": "July", "Agosto": "August",
     "Septiembre": "September", "Octubre": "October", "Noviembre": "November", "Diciembre": "December"
     }
     df_filtrado = df_filtrado[df_filtrado["f_instalacion_cliente"].dt.month_name() == MESES[mes]]

    # Ordenar por fecha de transacción para tomar el último estado por cliente
    df_filtrado = df_filtrado.sort_values(by='f_transaccion', kind='mergesort')

    #Eliminar duplicados manteniendo solo el último registro por cliente
    df_estado_unico = df_filtrado[~df_filtrado.index.duplicated(keep='last')]

    # Filtrar solo clientes con fecha de instalación válida
    df_con_fecha = df_estado_unico[df_estado_unico['f_instalacion_cliente'].notna()].copy()

    # Ordenar por fecha de instalación
    df_con_fecha = df_con_fecha.sort_values(by='f_instalacion_cliente')

    # Eliminar duplicados por cliente (quedarse con la primera instalación)
    df_nuevos = df_con_fecha[~df_con_fecha.index.duplicated(keep='first')].copy()

    # Extraer número de mes desde la fecha
    df_nuevos['mes'] = df_nuevos['f_instalacion_cliente'].dt.month


# ================================
# Subtítulo dinámico con filtros
# ================================
    subtitulo = "📍 Filtros aplicados:"
    if cliente != "Todo":
            subtitulo = f"📍 Estado: {cliente}"
    if ubicacion != "Todo":
            subtitulo += f" | Ubicación: {ubicacion}"
    if fecha != "Todo":
            subtitulo += f" | Año: {fecha}"
    if mes != "Todo":
            subtitulo += f" | Mes: {mes}"

# ===========================
# KPIs y gráficos según lógica
# ===========================

    # Si no hay datos después de los filtros, mostrar advertencia
    if df_filtrado.empty:
         # Si no hay coincidencias, se muestra este mensaje
        st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados.")
    else:
# =========================================
# 📈 KPIs por cliente único (último estado)
# =========================================

        # Calcular KPIs
        total_clientes = df_estado_unico.index.nunique() #clientes totales
        activos = (df_estado_unico["id_estatus_servicio_cliente"] == "activo").sum() #clientes activos
        suspendidos = (df_estado_unico["id_estatus_servicio_cliente"] == "suspendido").sum() #clientes suspendidos
        retirados = (df_estado_unico["id_estatus_servicio_cliente"] == "retirado").sum() #clientes retirados
        nuevos = df_nuevos.index.nunique() # Contar clientes nuevos

# ======================================
# 📊 Gráficos de líneas por estado y nuevo
# =======================================

    # Diccionario para ordenar meses en español
        MESES_ORDEN = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
               "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

        # Extraer el nombre del mes desde la fecha de instalación (en español)
        df_estado_unico['mes'] = df_estado_unico['f_instalacion_cliente'].dt.month_name(locale="es_ES")

        # Convertir el número de mes en df_nuevos a nombre de mes usando el diccionario
        df_nuevos['mes'] = df_nuevos['mes'].apply(lambda x: MESES_ORDEN[x - 1])

        # Convertir la columna 'mes' en una categoría ordenada para asegurar el orden correcto en los gráficos
        df_nuevos['mes'] = pd.Categorical(df_nuevos['mes'], categories=MESES_ORDEN, ordered=True)

# ==========================
# Activos
# ==========================

        # Agrupar clientes activos por mes y contar cuántos hay en cada uno
        resumen_activos = (
        df_estado_unico[df_estado_unico['id_estatus_servicio_cliente'] == "activo"]
        .groupby('mes').size()
        .reindex(MESES_ORDEN, fill_value=0)
        .reset_index(name="cantidad")
        )

        # Crear gráfico de línea para mostrar la evolución mensual de clientes activos
        fig_activos = px.line( #crear figura lineal 
            resumen_activos, #llamar el agrupamiento de cliente por mes
            x="mes",  #eje x mostrando datos de mes
            y="cantidad", #eje y mostrando datos para cantidad
            markers=True, #fondo de la tendencia
            title="✅ Activos", #titulo de la figura
            line_shape="spline" #suavizar la linea
            )

        # Actualizar diseño del gráfico
        fig_activos.update_layout(height=200, margin=dict(l=20,r=20,t=50,b=20), #tamaño del cuadro de figura
                      xaxis=dict(tickangle=-45), #estilo de letra 
                      plot_bgcolor="rgba(247, 247, 247, 0.5)", #color de la figura al rededor
                      paper_bgcolor="rgba(247, 247, 247, 0.5)" #color de la figura por dentro 
                      )

        # Personalizar el color y el grosor de la linea
        fig_activos.update_traces(line=dict(color="#2ECC71", width=2))  # verde

# ========================
# Suspendidos
# ========================

        # Agrupar clientes suspendidos por mes
        resumen_suspendidos = (
        df_estado_unico[df_estado_unico['id_estatus_servicio_cliente'] == "suspendido"] #filtrar suspendidos
        .groupby('mes').size() # contar por mes
        .reindex(MESES_ORDEN, fill_value=0) # asegurar todos los meses
        .reset_index(name="cantidad") # resetear índice
         )

        # Gráfico de línea para suspendidos
        fig_suspendidos = px.line(
            resumen_suspendidos, 
            x="mes", 
            y="cantidad", 
            markers=True, 
            title="⚠️ Suspendidos",
            line_shape="spline")

        # Actualizar diseño del gráfico para ajustes visuales
        fig_suspendidos.update_layout(height=200, margin=dict(l=20,r=20,t=50,b=20),
                      xaxis=dict(tickangle=-45),
                      plot_bgcolor="rgba(247, 247, 247, 0.5)",
                      paper_bgcolor="rgba(247, 247, 247, 0.5)")

        # Personalizar línea
        fig_suspendidos.update_traces(line=dict(color="#F1C40F", width=2))  # amarillo

# =====================
# Retirados
# =====================

        # Agrupar clientes retirados por mes
        resumen_retirados = (
        df_estado_unico[df_estado_unico['id_estatus_servicio_cliente'] == "retirado"]
        .groupby('mes').size()
        .reindex(MESES_ORDEN, fill_value=0)
        .reset_index(name="cantidad")
        )

        # Gráfico de línea para retirados
        fig_retirados = px.line(
            resumen_retirados, 
            x="mes", 
            y="cantidad", 
            markers=True, 
            title="❌ Retirados",
            line_shape="spline")

        # Actualizar diseño del gráfico
        fig_retirados.update_layout(height=200, margin=dict(l=20,r=20,t=50,b=20),
                      xaxis=dict(tickangle=-45),
                      plot_bgcolor="rgba(247, 247, 247, 0.5)",
                      paper_bgcolor="rgba(247, 247, 247, 0.5)")

        # Personalizar línea
        fig_retirados.update_traces(line=dict(color="#E74C3C", width=2))  # rojo

# ======================
# Nuevos
# ======================

        # Agrupar por mes y contar clientes únicos
        resumen_nuevos = (
           df_nuevos.groupby('mes')
          .size()
          .reindex(MESES_ORDEN, fill_value=0)
          .reset_index(name="cantidad")
       )

        # Gráfico de línea para nuevos
        fig_nuevos = px.line(
            resumen_nuevos, 
            x="mes", 
            y="cantidad", 
            markers=True, 
            title="🆕 Nuevos",
            line_shape="spline")

        # Actualizar diseño del gráfico
        fig_nuevos.update_layout(height=200, margin=dict(l=20,r=20,t=50,b=20),
                      xaxis=dict(tickangle=-45),
                      plot_bgcolor="rgba(247, 247, 247, 0.5)",
                      paper_bgcolor="rgba(247, 247, 247, 0.5)")

        # Personalizar línea
        fig_nuevos.update_traces(line=dict(color="#3498DB", width=2))  # azul

#=================================
# Graficos de planes de internet
#=================================

        # Crear una nueva columna con nombres legibles para los estados
        df_estado_unico['estado_cliente'] = df_estado_unico['id_estatus_servicio_cliente'].replace({
        'activo': 'Activo',
        'suspendido': 'Suspendido',  
        'deshabilitado': 'Retirado'
        })

        # Agrupar por plan y estado para contar clientes por combinación
        resumen_planes_estado = (
        df_estado_unico.groupby(['id_plan_internet_cliente', 'estado_cliente'])
        .size()
        .reset_index(name="cantidad")
        )

        # Ordenar los planes por total de clientes (de mayor a menor)
        orden_planes = (
        resumen_planes_estado.groupby("id_plan_internet_cliente")["cantidad"].sum()
        .sort_values(ascending=False)
        .index.tolist()
        )

        # Crear gráfico de barras apiladas por plan y estado
        fig_planes_estado = px.bar(
         resumen_planes_estado,
         x="cantidad",
         y="id_plan_internet_cliente",
         color="estado_cliente",
         text="cantidad",
         category_orders={"id_plan_internet_cliente": orden_planes}  # orden aplicado
         )

        # Ajustar diseño del gráfico
        fig_planes_estado.update_layout(
         height=450, #tamaño de figura
         xaxis_title="Planes de Internet", #titulo para eje x
         yaxis_title="Cantidad de Clientes", #titulo para eje y
         barmode="stack"  # barras apiladas
       )

        fig_planes_estado.update_traces(textposition="inside") # mostrar cantidad dentro de barras
        fig_planes_estado.update_layout(height=500,width=900, #tamaño 
                      xaxis=dict(tickangle=-45),
                      plot_bgcolor="rgba(247, 247, 247, 0.5)",
                      paper_bgcolor="rgba(247, 247, 247, 0.5)",
                      showlegend=False)

# ============================
# Por Municipio
# ============================

        # Agrupar por municipio y estado, y contar clientes
        resumen_municipio = (
        df_estado_unico
       .groupby(["id_municipio_cliente", "id_estatus_servicio_cliente"])
       .size()
       .unstack(fill_value=0)
       .reset_index()
       )

       # Renombrar columnas para mostrar íconos y etiquetas claras
        resumen_municipio = resumen_municipio.rename(columns={
        "activo": "✅ Activos",
        "suspendido": "⚠️ Suspendidos",
        "retirado": "❌ Retirados"
        })

        # Verificar qué columnas existen antes de calcular totales
        columnas_estado = [col for col in ["✅ Activos", "⚠️ Suspendidos", "❌ Retirados"] if col in resumen_municipio.columns]

        # Calcular totales solo con las columnas disponibles por estado y ordenarlos
        totales = resumen_municipio[columnas_estado].sum().sort_values(ascending=False)
        orden_estados = totales.index.tolist()

        # Transformar a formato largo para usar en Plotly
        resumen_long = resumen_municipio.melt(
        id_vars="id_municipio_cliente",
        value_vars=orden_estados,
        var_name="Estado",
        value_name="Cantidad"
        )

        # Crear gráfico de barras agrupadas por municipio y estado
        fig_municipio = px.bar(
           resumen_long,
          x="id_municipio_cliente",
          y="Cantidad",
          color="Estado",
          barmode="group", #barras agrupadas al lado
          category_orders={"Estado": orden_estados},
          title="Distribución de clientes por municipio y estado",
          color_discrete_map={
          "✅ Activos": "#2ECC71",
          "⚠️ Suspendidos": "#F1C40F",
          "❌ Retirados": "#E74C3C"
           })

        # Actualizar diseño del gráfico
        fig_municipio.update_traces(textposition="outside")

        # Ajustes visuales del gráfico
        fig_municipio.update_layout(
          xaxis_title="Municipio",
          yaxis_title="Cantidad de clientes",
          height=500,
          width=200,
          showlegend=True,
          plot_bgcolor="rgba(247, 247, 247, 0.5)",
          paper_bgcolor="rgba(247, 247, 247, 0.5)"
        )

#=====================================
#Graficos de porcentajes de estados
#=====================================

        # Calcular total de clientes
        total_clientes = len(df_estado_unico)

        # Obtener el mes actual
        ultimo_mes = pd.to_datetime("today").month

        # Filtrar clientes nuevos del mes actual
        df_nuevos = df_estado_unico[df_estado_unico['f_instalacion_cliente'].dt.month == ultimo_mes] # sacar colintes nuevos por fecha
        nuevos = len(df_nuevos) #contar clientes nuevos

        # Porcentajes por estado
        porcentaje_activos = (df_estado_unico['id_estatus_servicio_cliente'] == "activo").sum() / total_clientes * 100 # porcentaje activos
        porcentaje_retirados = (df_estado_unico['id_estatus_servicio_cliente'] == "retirado").sum() / total_clientes * 100
        porcentaje_suspendidos = (df_estado_unico['id_estatus_servicio_cliente'] == "suspendido").sum() / total_clientes * 100
        porcentaje_nuevos = nuevos / total_clientes * 100 # Porcentaje de nuevos

        #=================================
        # Gráfico de gauge para activos
        fig_gauge_activos = go.Figure(go.Indicator( # figura de indicador
            mode="gauge+number", # indicador de gauge y número
            value=porcentaje_activos, # valor del porcentaje
            number={'suffix': "%"},  #  símbolo %
            title={'text': "✅ Activos (%)"}, # título del gráfico
            gauge={'axis': {'range': [0, 100]}, # rango del eje
                     'bar': {'color': "#2ECC71"}})) # color de la barra
        # Actualizar diseño del gráfico
        fig_gauge_activos.update_layout(height=100, width=200, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10))

        #===================================
        # Gráfico de gauge para retirados
        fig_gauge_retirados = go.Figure(go.Indicator(
            mode="gauge+number",
            value=porcentaje_retirados,
            number={'suffix': "%"},  #  símbolo %
            title={'text': "❌ Retirados (%)"},
            gauge={'axis': {'range': [0, 100]},
                     'bar': {'color': "#E74C3C"}}))
        fig_gauge_retirados.update_layout(height=100, width=200, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10))  

        #====================================
        # Gráfico de gauge para suspendidos
        fig_gauge_suspendidos = go.Figure(go.Indicator(
            mode="gauge+number",
            value=porcentaje_suspendidos,
            number={'suffix': "%"},  #  símbolo %
            title={'text': "⚠️ Suspendidos (%)"},
            gauge={'axis': {'range': [0, 100]},
                     'bar': {'color': "#F1C40F"}}))
        fig_gauge_suspendidos.update_layout(height=100, width=200, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10))    

        #======================================
        # Gráfico de gauge para Nuevos
        fig_gauge_nuevos = go.Figure(go.Indicator(
           mode="gauge+number",
           value=porcentaje_nuevos,
           number={'suffix': "%"},  #  símbolo %
           title={'text': "🆕 Nuevos (%)"},
           gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#3498DB"}}  # azul
         ))
        fig_gauge_nuevos.update_layout(height=100, width=200, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))

# ==========================================
# Layout: KPIs izquierda, gráficos derecha
# ==========================================

        # Crear dos columnas: una angosta para KPIs y otra ancha para gráficos (proporción 1:6)
        col_kpi, col_graficos = st.columns([1, 6])  # proporción 1:6

        # KPIs apilados en columna izquierda
        with col_kpi:
          st.markdown("### 👥 KPIs")  # Título de la sección
          st.metric("📌 Total Clientes", total_clientes)  # Total general
          st.metric("✅ Activos", activos) # Clientes activos
          st.metric("⚠️ Suspendidos", suspendidos) # Clientes suspendidos
          st.metric("❌ Retirados", retirados)  # Clientes retirados
          st.metric("🆕 Nuevos", nuevos)  # Clientes nuevos

        # Mostrar los gráficos en la columna derecha
        with col_graficos:

          # Crear dos subcolumnas para mostrar el subtítulo dinámico
          sub1,sub2= st.columns([2,4])  # dos subcolumnas
          with sub1:
              st.markdown(f"#### {subtitulo}")  # subtítulo dinámico de filtros aplicados

#===============================
# Primera fila de gráficos %
# ==============================

          # Crear 4 columnas iguales para los indicadores tipo gauge
          g1, g2, g3, g4= st.columns([1,1,1,1])  
          with g1:
           st.plotly_chart(fig_gauge_activos, use_container_width=True)
          with g2:
           st.plotly_chart(fig_gauge_suspendidos, use_container_width=True)
          with g3:
           st.plotly_chart(fig_gauge_retirados, use_container_width=True)
          with g4:
           st.plotly_chart(fig_gauge_nuevos, use_container_width=True)

#========================================================
# Mostrar los 4 gráficos en una sola fila por estado
# =======================================================

          # Crear 4 columnas para los gráficos de líneas mensuales
          col1, col2, col3, col4 = st.columns(4)
          with col1:
             st.plotly_chart(fig_activos, use_container_width=True)
          with col2:
             st.plotly_chart(fig_suspendidos, use_container_width=True)
          with col3:
             st.plotly_chart(fig_retirados, use_container_width=True)
          with col4:
             st.plotly_chart(fig_nuevos, use_container_width=True)

#=============================
# tercera fila de gráficos
# ============================

          # Crear dos columnas para gráficos más anchos
          col5, col6 = st.columns(2)  # gráfico más ancho
          with col5:
                st.plotly_chart(fig_planes_estado, use_container_width=True)
          with col6:
                st.plotly_chart(fig_municipio, use_container_width=True)

# ====================================
# 💰 Página: Dashboard de Facturación
# ===================================

# Verifica si la página seleccionada es "Dashboard Facturacion"
elif pagina == "Dashboard Facturacion":

# ======================
#  Título del dashboard
# ======================

    # Mostrar título centrado con estilo personalizado
    st.markdown("""
    <style>
    .titulo-central {
        text-align: center;   # Centrar el texto
        font-family: 'Montserrat', sans-serif;   # Fuente moderna
        font-size: 20px;   # Tamaño del título
        font-weight: 700;  # Negrita
        color: #2C3E50;    # Azul oscuro
        margin-bottom: 20px;   # Espacio inferior
    }
    </style>
    <h1 class="titulo-central">📊 Dashboard de Facturación</h1>
    """, unsafe_allow_html=True)

#===========================
#MENU
#===========================

    # Copiar el DataFrame original para trabajar con él
    df_facturacion = df.copy()

    # Seleccionar el año más reciente como predeterminado
    anios_disponibles = sorted(df_facturacion['anio'].dropna().unique())

    # Seleccionar el año más reciente como predeterminado
    anio_tope = max(anios_disponibles)

    # Mostrar subtítulo en la barra lateral
    st.sidebar.subheader("Filtros de Facturacion")

    # Filtro para seleccionar tipo de dato (por ahora solo "ingresos")
    tipo_dato = st.sidebar.selectbox("Tipo de facturacion:", ["ingresos"])

    # Filtro para seleccionar el año de facturación
    anio_factura = st.sidebar.selectbox("Año:", options=anios_disponibles,
                                   index=anios_disponibles.index(anio_tope))

    # Filtro para seleccionar el mes de facturación
    mes_factura = st.sidebar.selectbox("Mes:", [
        "Todo", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
        "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ])

# ================================
# Subtítulo dinámico con filtros
# ================================

    # Crear subtítulo que muestre los filtros seleccionados
    subtitulo2 = "📍 Filtros aplicados:" 

    # Si el tipo de dato no es "ingresos", agregarlo al subtítulo (por si se agregan más tipos en el futuro)
    if tipo_dato != "ingresos": 
        subtitulo2 = f"📍 Tipo de dato: {tipo_dato}"   
    # Agregar año al subtítulo
    if anio_factura != "Todo":
        subtitulo2 += f" | Año: {anio_factura}"
    # Agregar mes al subtítulo si se seleccionó uno específico
    if mes_factura != "Todo":

# ===============================
# 📂 Preparación del DataFrame
# ===============================

     # Filtrar el dataframe de facturación según el año seleccionado
     df_facturacion_filtrado = df_facturacion[df_facturacion['anio'] == anio_factura]

    # Si se seleccionó un mes específico, filtrar también por mes
    if mes_factura != "Todo":
        MESES = {"Enero":"January","Febrero":"February","Marzo":"March","Abril":"April",
                 "Mayo":"May","Junio":"June","Julio":"July","Agosto":"August",
                 "Septiembre":"September","Octubre":"October","Noviembre":"November","Diciembre":"December"}

        # Aplicar filtro por nombre del mes en inglés
        df_facturacion = df_facturacion[df_facturacion["f_emision_factura"].dt.month_name() == MESES[mes_factura]]

# ================================
# Subtítulo dinámico con filtros
# ================================

    # Crear subtítulo que muestre los filtros seleccionados
    subtitulo2 = "📍 Filtros aplicados:" 

    # Si el tipo de dato no es "ingresos", agregarlo al subtítulo (por si se agregan más tipos en el futuro)
    if tipo_dato != "ingresos": 
        subtitulo2 = f"📍 Tipo de dato: {tipo_dato}"   
    # Agregar año al subtítulo
    if anio_factura != "Todo":
        subtitulo2 += f" | Año: {anio_factura}"
    # Agregar mes al subtítulo si se seleccionó uno específico
    if mes_factura != "Todo":
        subtitulo2 += f" | Mes: {mes_factura}"

#=================================
# 🧮 Preparar datos para gráficos 
#=================================

    # Reemplazar celdas vacías o con solo espacios por valores nulos (NaN)
    df_facturacion = df_facturacion.replace(r'^\s*$', np.nan, regex=True)

    # Eliminar filas que tengan valores nulos en columnas clave
    df_facturacion = df_facturacion.dropna(subset=['id_plan_internet_cliente','total_factura','neto_transaccion'])

    # Eliminar filas donde el campo de plan esté vacío (aunque no sea NaN)
    df_facturacion = df_facturacion[df_facturacion['id_plan_internet_cliente'].str.strip() != ""]

    # Eliminar espacios en blanco al inicio y final de todas las columnas tipo string
    df_facturacion = df_facturacion.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

#==============================
#graficos 
#==============================

    # Diccionario para mapear número de mes a nombre en español
    MES_MAP = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
     }

    # Extraer número de mes desde la fecha de emisión
    df_facturacion['mes_num'] = df_facturacion['f_emision_factura'].dt.month

    #este codigo mapea el numero del mes al nombre del mes es decir 1->Enero, 2->Febrero etc
    df_facturacion['mes_nombre'] = df_facturacion['mes_num'].map(MES_MAP) # mapa de número

    # Convertir a categoría ordenada para que los gráficos respeten el orden cronológico
    df_facturacion['mes_nombre'] = pd.Categorical( # convertir a categoría
    df_facturacion['mes_nombre'], # columna de mes
    categories=list(MES_MAP.values()), # categorías en orden
    ordered=True # ordenado
    )

    # Agrupar por mes y calcular totales facturados y cobrados
    df_line = df_facturacion.groupby('mes_nombre').agg({ # agrupar por mes
    'total_factura':'sum', # suma total facturas facturadas
    'neto_transaccion':'sum' # suma neto transacciones cobradas
    }).reset_index() # resetear índice para gráfico

    # Calcular monto pendiente por cobrar
    df_line['monto_a_cobrar'] = df_line['total_factura'] - df_line['neto_transaccion']

#=======================
# Monto Facturado
#======================

    # Crear gráfico de línea para el monto facturado mensual
    fig_facturado = px.line(
        df_line,
        x="mes_nombre",
        y="total_factura",
        labels={"total_factura":"Monto Facturado","mes":"Mes"}, 
        title="💰 Monto Facturado", #titulo
        markers=True, # activa los puntos en la curva
        line_shape="spline" #suavizar linea
    )
    # Personalizar tooltip con formato de moneda
    fig_facturado.update_traces(hovertemplate="Mes: %{x}<br>Facturado: $%{y:,.2f}") # formato moneda para hover
    # Ajustes visuales del gráfico
    fig_facturado.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20),
                      xaxis=dict(tickangle=-45),
                      plot_bgcolor="rgba(247, 247, 247, 0.5)",
                      paper_bgcolor="rgba(247, 247, 247, 0.5)")

#==============
# Monto Cobrado
#==============

    # Crear gráfico de línea para el monto cobrado mensual
    fig_cobrado = px.line(
        df_line,
        x="mes_nombre",
        y="neto_transaccion",
        labels={"neto_transaccion":"Monto Cobrado","mes":"Mes"},
        title="💵 Monto Cobrado",
        markers=True,  # activa los puntos en la curva
        line_shape="spline"
    )
    fig_cobrado.update_traces(hovertemplate="Mes: %{x}<br>Facturado: $%{y:,.2f}")

    fig_cobrado.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20),
                      xaxis=dict(tickangle=-45),
                      plot_bgcolor="rgba(247, 247, 247, 0.5)",
                      paper_bgcolor="rgba(247, 247, 247, 0.5)")

# ==============================================
# 🥧 Gráfico circular: Pagos en Divisas vs Bs
# ============================================== 

    # Diccionario para agrupar métodos de pago en categorías más generales
    MAPEO_PAGOS = {
    "transferencia_divisas": "Divisas",
    "efectivo_divisas": "Divisas",
    "transferenacia_bolivares": "Bolívares",
    "efectivo_bolivares": "Bolívares",
    "pago_movil": "Bolívares",
    "nota_credito": "Otros"
    } 

    # Crear nueva columna con el grupo de pago (Divisas, Bolívares, Otros)
    df_facturacion['grupo_pago'] = df_facturacion['id_pasarela_pago'].replace(MAPEO_PAGOS)

    # Filtrar solo pagos en Divisas y Bolívares y contar cuántos hay de cada uno
    df_pagos_tipo = (
        #este codigo agrupa los pagos en divisas y bolivares el .isin es para filtrar solo esos dos grupos
    df_facturacion[df_facturacion['grupo_pago'].isin(["Divisas","Bolívares"])]
    .groupby('grupo_pago') # agrupar por tipo de pago
    .size() # contar cantidad
    .reset_index(name='cantidad') # resetear índice
    )

    # Crear gráfico circular para mostrar distribución de pagos
    fig_pagos = px.pie(
     df_pagos_tipo,
     names="grupo_pago",
     values="cantidad",
     title="Distribución de Pagos: Divisas vs Bs",
     color="grupo_pago",
     color_discrete_map={
        "Divisas":"#F39C12",   # Naranja
        "Bolívares":"#3498DB"  # Azul
     }
    )
    # Mostrar porcentaje y etiqueta en cada porción
    fig_pagos.update_traces(textinfo="percent+label")

    # Ajustes visuales del gráfico
    fig_pagos.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20),
                      plot_bgcolor="rgba(247, 247, 247, 0.5)",
                      paper_bgcolor="rgba(247, 247, 247, 0.5)")

#==============================================
# Graficos Facturación y Cobranzas por Plan
#==============================================

    # Seleccionar columnas relevantes para el gráfico de violín
    df_violin = df_facturacion[['id_plan_internet_cliente', 'total_factura', 'neto_transaccion']].copy()

    # Transformar columnas de monto a formato largo (melt)
    df_violin_melt = df_violin.melt(
     id_vars='id_plan_internet_cliente',  # columna fija
     value_vars=['total_factura', 'neto_transaccion'],  # columnas a derretir
     var_name='tipo',     # nueva columna que indica el tipo de monto
     value_name='monto_usd'   # nueva columna con los valores
    )

    # Renombrar los tipos para que se vean más claros en el gráfico
    df_violin_melt['tipo'] = df_violin_melt['tipo'].replace({
     'total_factura': 'Facturación Activa ($)',
     'neto_transaccion': 'Cobranzas Activas ($)'
     })

    # Crear gráfico de violín para mostrar la distribución de montos por plan
    fig_violin = px.violin(
     df_violin_melt,
     x="id_plan_internet_cliente",   # eje X: planes
     y="monto_usd",   # eje Y: montos
     color="tipo",  # color por tipo de monto
     box=True,  # Mostrar caja dentro del violín
     points="all",  # Mostrar todos los puntos individuales
     title="🎻 Distribución de Facturación y Cobranzas por Plan",
     labels={
        "id_plan_internet_cliente": "Plan de Internet",
        "monto_usd": "Monto ($)",
        "tipo": "Tipo"
    })

    # Ajustes visuales del gráfico
    fig_violin.update_layout(
     height=500,
     width=900,
     showlegend=True,
     plot_bgcolor="rgba(247, 247, 247, 0.5)",
     paper_bgcolor="rgba(247, 247, 247, 0.5)"
    )

#===================================================
# 🥧 Gráfico circular: Ingresos por Método de Pago
#===================================================

    # Agrupar por método de pago y sumar el neto transaccionado ($)
    df_metodos_pago = (
     df_facturacion.groupby('id_pasarela_pago')['neto_transaccion']
      .sum()
     .reset_index()
    )

    # Crear gráfico circular para mostrar distribución de ingresos por método
    fig_metodos_pago = px.pie(
     df_metodos_pago,
     names="id_pasarela_pago",          # Método de pago
     values="neto_transaccion",         # Dinero total por método
     title="💳 Distribución de Ingresos por Método de Pago",
     color="id_pasarela_pago"
     )

    # Mostrar porcentaje y etiqueta en cada porción del gráfico
    fig_metodos_pago.update_traces(
     textinfo="percent+label",
     hovertemplate="<b>Método:</b> %{label}<br>Ingresos: $%{value:,.2f}<br>%{percent}"
    )

    # Ajustes visuales del gráfico
    fig_metodos_pago.update_layout(height=500, width=900,
                      plot_bgcolor="rgba(247, 247, 247, 0.5)",
                      paper_bgcolor="rgba(247, 247, 247, 0.5)")


# ==============================================
# Comparación de Facturación vs Cobranzas
# ==============================================

    # Calcular totales generales de facturación y cobranzas
    total_facturado = df_facturacion['total_factura'].sum()
    total_cobrado = df_facturacion['neto_transaccion'].sum()

    # Crear DataFrame con los totales para graficar
    comparacion_df = pd.DataFrame({
    'Tipo': ['Facturado', 'Cobrado'],
    'Monto': [total_facturado, total_cobrado]
    })

    # Crear gráfico de barras horizontales para comparar montos
    fig_comparacion = px.bar(
    comparacion_df,
    y='Tipo',  # eje Y: tipo de ingreso
    x='Monto', # eje X: monto total
    text='Monto', # mostrar monto en la barra
    color='Tipo',  # color por tipo
    color_discrete_map={
        'Facturado': '#2980B9',  # azul
        'Cobrado': '#27AE60'     # verde
    },
    title="💰 Comparación de Monto Facturado vs Cobrado",
    labels={'Monto': 'Monto ($)', 'Tipo': 'Tipo de Ingreso'}
    )

    # Mostrar monto con formato de moneda fuera de la barra
    fig_comparacion.update_traces(
     texttemplate="$%{text:,.2f}",
     textposition="outside"
    )

    # Ajustes visuales del gráfico
    fig_comparacion.update_layout(
     height=200, margin=dict(l=20,r=20,t=40,b=20),
     showlegend=False,
     plot_bgcolor="rgba(247, 247, 247, 0.5)",
     paper_bgcolor="rgba(247, 247, 247, 0.5)"
    )

# =========================
#  KPIs generales
# =========================

    # Verificar si el DataFrame está vacío después de aplicar los filtros
    if df_facturacion.empty:
        st.warning("⚠️ No hay datos de facturación para los filtros seleccionados.")
    else:
     # Obtener la fecha actual para comparar vencimientos
     hoy = pd.to_datetime("today")

     # Contar todas las facturas emitidas
     facturas_emitidas = len(df_facturacion) # facturas emitidas

     # Contar facturas cobradas (aquellas con fecha de transacción registrada)
     facturas_cobradas = len(df_facturacion[df_facturacion['f_transaccion'].notna()])  # facturas cobradas con fecha de transacción registrada

    # Contar facturas vencidas: con fecha de emisión y vencimiento válidas, y vencidas al día de hoy
    #este codigo cuenta las facturas vencidas y hace un filtro para evitar errores con nulos
     facturas_vencidas = len(df_facturacion[
        (df_facturacion['f_emision_factura'].notna()) & # emisión registrada para evitar errores y nulos
        (df_facturacion['f_vencimiento_factura'].notna()) & # vencimiento registrado para evitar errores y nulos
        (df_facturacion['f_vencimiento_factura'] < hoy) # vencidas de hoy y anteriores para saber las vencidas
     ])

     # Contar facturas anuladas: aquellas con monto total igual a cero
     facturas_anuladas = len(df_facturacion[df_facturacion['total_factura'] == 0])

     # Calcular el total facturado en dólares
     facturado_total  = df_facturacion['total_factura'].sum()  # total facturado


    # Crear dos columnas: una angosta para KPIs y otra ancha para los gráficos
     col_kpi, col_graf = st.columns([1,6])

     with col_kpi:
        st.markdown("### 📊 KPIs")
        st.metric("📄 Facturas Emitidas", facturas_emitidas)
        st.metric("⏰ Facturas Vencidas", facturas_vencidas)
        st.metric("✅ Facturas Cobradas", facturas_cobradas)
        st.metric("❌ Facturas Anuladas", facturas_anuladas)
        st.metric("💰 Facturado", f"${facturado_total:,.2f}") #formato de moneda

     with col_graf:

        # Mostrar subtítulo con los filtros aplicados
        titu1, titu2 = st.columns([2,4])  # dos subcolumnas
        with titu1:
            st.markdown(f"#### {subtitulo2}")  # subtítulo dinámico de filtros aplicados

        # Crear 4 columnas para mostrar los gráficos principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
         st.plotly_chart(fig_facturado, use_container_width=True) 
        with col2:
         st.plotly_chart(fig_cobrado, use_container_width=True)
        with col3:
            st.plotly_chart(fig_comparacion)
        with col4:
         st.plotly_chart(fig_pagos, use_container_width=True)

        # Crear dos columnas para gráficos más anchos
        col5, col6 = st.columns([4,3])  # gráfico más ancho
        with col5:
         st.plotly_chart(fig_violin, use_container_width=True)
        with col6:
            st.plotly_chart(fig_metodos_pago, use_container_width=True)



