#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# ##Cargando bases de datos

# In[2]:


path = "datos_sw.xlsx"#Cargando datos
#leyendo hojas
df= pd.read_excel(path)


# ##Arreglos de la base de datos

# In[3]:


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


# In[4]:


df.set_index('codigo_cliente', inplace=True) #para colocar los indeces id_cliente como los indes de la tabla en panda
df.head()


# ##extraer fechas para usarlos

# In[5]:


# Extraer componentes de la fecha columnas separadas con datos de las fechas instalacion
df['dia'] = df['f_instalacion_cliente'].dt.day #dia
df['mes'] = df['f_instalacion_cliente'].dt.month #mes
df['año'] = df['f_instalacion_cliente'].dt.year #año


# In[6]:


df.head()


# #Validacoin de datos

# In[7]:


# Revisar valores nulos
df.isnull().sum()
# Revisar valores únicos en columnas clave
df['id_municipio_cliente'].unique()
df['id_estatus_servicio_cliente'].unique()
df['año'].unique()
df['mes'].unique()
df['dia'].unique()


# ##Cargando css exterior personalizado

# In[ ]:


#===========================
# Cargar CSS externon personalizado
#==========================

def cargar_css(ruta="style.css"):
    with open(ruta, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Llamada a la función
cargar_css("style.css")


# In[ ]:


#===========================================
#Configurar la página principal del dashboard
#==========================================

st.set_page_config(page_title="Soluciones Wireless", layout="wide")


# ##Menu

# In[ ]:


#===============================
# Menú lateral principal con navegación entre páginas
#================================
st.sidebar.markdown("""
<h1 style='
    font-family: "Montserrat", sans-serif;
    font-size: 24px;
    color: #ffffff;
    font-weight: 500;
    margin-bottom: 10px;
'>
Soluciones Wireless
</h1>
""", unsafe_allow_html=True)
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

    # 🎛️ Filtros especificos
    st.sidebar.subheader("Filtros de Cliente")

    cliente = st.sidebar.selectbox("Clientes:", ["Todo", "activo", "suspendido", "retirado"])

    ubicacion = st.sidebar.selectbox("Ubicación/Municipo:", ["Nada", "bolivar", "urbaneja", "sotillo"])

    fecha = st.sidebar.selectbox("Año:", ["Nada", "2019", "2020", "2021", "2022", "2023", "2024","2025"])

    mes = st.sidebar.selectbox("Mes:", [
        "Nada", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
        "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ])

#===============================
# 🧩 Título del dashboard
#===============================

    st.markdown("""
    <h1 style='
        font-family: "Roboto", sans-serif;
        font-size: 32px;
        color: #96d3ff;
        font-weight: 600;
        margin-bottom: 20px;
    '>
    📊 Dashboard Clientes
    </h1>
    """, unsafe_allow_html=True)

#================================
# 🧮 Aplicar filtros
#================================

    df_filtrado = df.copy()

    #filtro por estado
    if cliente != "Todo":
        df_filtrado = df_filtrado[df_filtrado["id_estatus_servicio_cliente"] == cliente]

    #filtro por municipio
    if ubicacion != "Nada":
        df_filtrado = df_filtrado[df_filtrado["id_municipio_cliente"] == ubicacion]

    #filtro por año
    if fecha != "Nada":
        df_filtrado = df_filtrado[df_filtrado["f_instalacion_cliente"].dt.year == int(fecha)]

    #filtro por mes
    if mes != "Nada":
    # Diccionario para traducir meses español → inglés
     MESES = {"Enero": "January", "Febrero": "February", "Marzo": "March", "Abril": "April",
     "Mayo": "May", "Junio": "June", "Julio": "July", "Agosto": "August",
    "Septiembre": "September", "Octubre": "October", "Noviembre": "November", "Diciembre": "December"
     }
     df_filtrado = df_filtrado[df_filtrado["f_instalacion_cliente"].dt.month_name() == MESES[mes]]

    # ===========================
    # KPIs y gráficos según lógica
    # ===========================
    if df_filtrado.empty:
         # Si no hay coincidencias, se muestra este mensaje
        st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados.")
    else:
        # =========================================
        # 📈 KPIs por cliente único (último estado)
        # =========================================

        # Ordenar por fecha de transacción para tomar el último estado por cliente
        df_filtrado = df_filtrado.sort_values(by='f_transaccion', kind='mergesort')

        #Eliminar duplicados manteniendo solo el último registro por cliente
        df_estado_unico = df_filtrado[~df_filtrado.index.duplicated(keep='last')]

        # Calcular KPIs
        total_clientes = df_estado_unico.index.nunique() #clientes totales
        activos = (df_estado_unico["id_estatus_servicio_cliente"] == "activo").sum() #clientes activos
        suspendidos = (df_estado_unico["id_estatus_servicio_cliente"] == "suspendido").sum() #clientes suspendidos
        retirados = (df_estado_unico["id_estatus_servicio_cliente"] == "retirado").sum() #clientes retirados

# =========================================
# 🆕 Calcular clientes nuevos por fecha
# =========================================

       # 👉 Filtrar por fecha válida
        df_nuevos = df_estado_unico[df_estado_unico['f_instalacion_cliente'].notna()].copy()

       # 👉 Aplicar filtros de año y mes si están activos
        if fecha != "Nada":
         df_nuevos = df_nuevos[df_nuevos['f_instalacion_cliente'].dt.year == int(fecha)]

        if mes != "Nada":
         df_nuevos = df_nuevos[df_nuevos['f_instalacion_cliente'].dt.month_name() == MESES[mes]]

        # 👉 Contar clientes nuevos
        nuevos = df_nuevos.index.nunique()    

        # ================================
        # Subtítulo dinámico con filtros
        # ================================
        subtitulo = "📍 Filtros aplicados:"
        if cliente != "Todo":
            subtitulo = f"📍 Estado: {cliente}"
        if ubicacion != "Nada":
            subtitulo += f" | Ubicación: {ubicacion}"
        if fecha != "Nada":
            subtitulo += f" | Año: {fecha}"
        if mes != "Nada":
            subtitulo += f" | Mes: {mes}"


# ======================================
# 📊 Gráficos de líneas por estado y nuevo
# =======================================

    # Diccionario para ordenar meses en español
        MESES_ORDEN = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
               "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

        df_estado_unico['mes'] = df_estado_unico['f_instalacion_cliente'].dt.month_name(locale="es_ES")

       # ============
       # Activos
       # ===========
       # Crear resumen de activos por mes
        resumen_activos = (
          df_estado_unico[df_estado_unico['id_estatus_servicio_cliente']=="activo"]
          .groupby('mes').size().reset_index(name="cantidad")
        )
        # Ordenar meses correctamente
        resumen_activos['mes'] = pd.Categorical(resumen_activos['mes'], categories=MESES_ORDEN, ordered=True)
        resumen_activos = resumen_activos.sort_values('mes')

        # Gráfico de línea para activos
        fig_activos = px.line(
            resumen_activos, 
            x="mes", 
            y="cantidad", 
            markers=True, 
            title="✅ Activos")

        # Actualizar diseño del gráfico
        fig_activos.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))
        # Personalizar línea
        fig_activos.update_traces(line=dict(color="#2ECC71", width=2))  # verde

       # ==================
       # Suspendidos
       # ==================
       # Crear resumen de suspendidos por mes
        resumen_suspendidos = (
          df_estado_unico[df_estado_unico['id_estatus_servicio_cliente']=="suspendido"]
         .groupby('mes').size().reset_index(name="cantidad")
        )

        # Ordenar meses correctamente
        resumen_suspendidos['mes'] = pd.Categorical(resumen_suspendidos['mes'], categories=MESES_ORDEN, ordered=True)
        resumen_suspendidos = resumen_suspendidos.sort_values('mes')

        # Gráfico de línea para suspendidos
        fig_suspendidos = px.line(
            resumen_suspendidos, 
            x="mes", 
            y="cantidad", 
            markers=True, 
            title="⚠️ Suspendidos")
        # Actualizar diseño del gráfico
        fig_suspendidos.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))
        # Personalizar línea
        fig_suspendidos.update_traces(line=dict(color="#F1C40F", width=2))  # amarillo

       # ==============
       # Retirados
       # ==============

       # Crear resumen de retirados por mes
        resumen_retirados = (
         df_estado_unico[df_estado_unico['id_estatus_servicio_cliente']=="retirado"]
        .groupby('mes').size().reset_index(name="cantidad") # contar por mes
        )

        # Ordenar meses correctamente
        resumen_retirados['mes'] = pd.Categorical(resumen_retirados['mes'], categories=MESES_ORDEN, ordered=True)
        resumen_retirados = resumen_retirados.sort_values('mes')

        # Gráfico de línea para retirados
        fig_retirados = px.line(
            resumen_retirados, 
            x="mes", 
            y="cantidad", 
            markers=True, 
            title="❌ Retirados")

        # Actualizar diseño del gráfico
        fig_retirados.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))
        # Personalizar línea
        fig_retirados.update_traces(line=dict(color="#E74C3C", width=2))  # rojo

        # ========
        # Nuevos
        # ========
        # Crear resumen de nuevos por mes
        resumen_nuevos = (
         df_estado_unico[df_estado_unico['f_instalacion_cliente'].notna()]
         .groupby('mes').size().reset_index(name="cantidad")
        )

        # Ordenar meses correctamente
        resumen_nuevos['mes'] = pd.Categorical(resumen_nuevos['mes'], categories=MESES_ORDEN, ordered=True)
        resumen_nuevos = resumen_nuevos.sort_values('mes')

        # Gráfico de línea para nuevos
        fig_nuevos = px.line(
            resumen_nuevos, 
            x="mes", 
            y="cantidad", 
            markers=True, 
            title="🆕 Nuevos")

        # Actualizar diseño del gráfico
        fig_nuevos.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))
        # Personalizar línea
        fig_nuevos.update_traces(line=dict(color="#3498DB", width=2))  # azul

        #===============================
        # Graficos de planes de internet
        #===============================

        # Mapear estados reales
        df_estado_unico['estado_cliente'] = df_estado_unico['id_estatus_servicio_cliente'].replace({
        'activo': 'Activo',
        'suspendido': 'Suspendido',   # aquí entran también los morosos
        'deshabilitado': 'Retirado'
        })

        # Agrupar por plan y estado
        resumen_planes_estado = (
        df_estado_unico.groupby(['id_plan_internet_cliente', 'estado_cliente'])
        .size()
        .reset_index(name="cantidad")
        )

        # Crear gráfico de barras agrupado
        fig_planes_estado = px.bar(
         resumen_planes_estado,
         x="cantidad",
         y="id_plan_internet_cliente",
         color="estado_cliente",
         text="cantidad",
         title="📊 Distribución de Clientes por Plan y Estado"
        )

        # Ajustes visuales
        fig_planes_estado.update_layout(
         height=450,
         xaxis_title="Planes de Internet",
         yaxis_title="Cantidad de Clientes",
         barmode="stack"  # barras apiladas
       )

        fig_planes_estado.update_traces(textposition="inside") # mostrar cantidad dentro de barras
        fig_planes_estado.update_layout(height=500,width=900, showlegend=False)

        # ============================
        # Activos por Municipio
        # ============================
        resumen_activos_mun = (
         df_estado_unico[df_estado_unico['id_estatus_servicio_cliente']=="activo"]
         .groupby('id_municipio_cliente').size().reset_index(name="cantidad")
       )
        # Gráfico de barras para activos por municipio
        fig_activos_mun = px.bar(
         resumen_activos_mun,
         x="id_municipio_cliente",
         y="cantidad",
         text="cantidad",
         title="✅ Activos"
        ) 
        # Actualizar diseño del gráfico
        fig_activos_mun.update_traces(textposition="outside", marker_color="#2ECC71")
        # Personalizar línea
        fig_activos_mun.update_layout(height=500, width=280, showlegend=False,  xaxis_title="Municipio", yaxis_title="Cantidad")

       # ============================
        # Retirados (deshabilitado) por Municipio
       # ============================
        resumen_retirados_mun = (
         df_estado_unico[df_estado_unico['id_estatus_servicio_cliente']=="retirado"]
         .groupby('id_municipio_cliente').size().reset_index(name="cantidad")
        )
        # Gráfico de barras para retirados por municipio
        fig_retirados_mun = px.bar(
         resumen_retirados_mun,
         x="id_municipio_cliente",
         y="cantidad",
         text="cantidad",
         title="❌ Retirados"
        )
        # Actualizar diseño del gráfico
        fig_retirados_mun.update_traces(textposition="outside", marker_color="#E74C3C")
        # Personalizar línea
        fig_retirados_mun.update_layout(height=500, width=280, showlegend=False, xaxis_title="Municipio",yaxis_title="Cantidad")

       # ============================
       # Suspendidos por Municipio
       # ============================
        resumen_suspendidos_mun = (
             df_estado_unico[df_estado_unico['id_estatus_servicio_cliente']=="suspendido"]
            .groupby('id_municipio_cliente').size().reset_index(name="cantidad")
        )

         # Gráfico de barras para suspendidos por municipio
        fig_suspendidos_mun = px.bar(
         resumen_suspendidos_mun,
         x="id_municipio_cliente",
         y="cantidad",
         text="cantidad",
         title="⚠️ Suspendidos"
        )

        # Actualizar diseño del gráfico
        fig_suspendidos_mun.update_traces(textposition="outside", marker_color="#F1C40F")
        fig_suspendidos_mun.update_layout(height=500, width=280, showlegend=False, xaxis_title="Municipio", yaxis_title="Cantidad")

        #===================================
        #Graficos de porcentajes de estados
        #===================================

        # Total de clientes
        total_clientes = len(df_estado_unico)
        ultimo_mes = pd.to_datetime("today").month # columna de dias
        df_nuevos = df_estado_unico[df_estado_unico['f_instalacion_cliente'].dt.month == ultimo_mes] # sacar colintes nuevos por fecha
        nuevos = len(df_nuevos) #contar clientes nuevos

        # Porcentajes por estado
        porcentaje_activos = (df_estado_unico['id_estatus_servicio_cliente'] == "activo").sum() / total_clientes * 100 # porcentaje activos
        porcentaje_retirados = (df_estado_unico['id_estatus_servicio_cliente'] == "retirado").sum() / total_clientes * 100
        porcentaje_suspendidos = (df_estado_unico['id_estatus_servicio_cliente'] == "suspendido").sum() / total_clientes * 100
        porcentaje_nuevos = nuevos / total_clientes * 100 # Porcentaje de nuevos

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

        # Gráfico de gauge para retirados
        fig_gauge_retirados = go.Figure(go.Indicator(
            mode="gauge+number",
            value=porcentaje_retirados,
            number={'suffix': "%"},  #  símbolo %
            title={'text': "❌ Retirados (%)"},
            gauge={'axis': {'range': [0, 100]},
                     'bar': {'color': "#E74C3C"}}))
        fig_gauge_retirados.update_layout(height=100, width=200, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10))  

        # Gráfico de gauge para suspendidos
        fig_gauge_suspendidos = go.Figure(go.Indicator(
            mode="gauge+number",
            value=porcentaje_suspendidos,
            number={'suffix': "%"},  #  símbolo %
            title={'text': "⚠️ Suspendidos (%)"},
            gauge={'axis': {'range': [0, 100]},
                     'bar': {'color': "#F1C40F"}}))
        fig_gauge_suspendidos.update_layout(height=100, width=200, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10))    

        # Gráfico de gauge para Nuevos
        fig_gauge_nuevos = go.Figure(go.Indicator(
           mode="gauge+number",
           value=porcentaje_nuevos,
           number={'suffix': "%"},  #  símbolo %
           title={'text': "🆕 Nuevos (%)"},
           gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#3498DB"}}  # azul
         ))
        fig_gauge_nuevos.update_layout(height=100, width=200, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))

        # ============================
        # Layout: KPIs izquierda, gráficos derecha
        # ============================

        col_kpi, col_graficos = st.columns([1, 6])  # proporción 1:6

        # KPIs apilados en columna izquierda
        with col_kpi:
          st.markdown("### 👥 KPIs")
          st.metric("📌 Total Clientes", total_clientes)
          st.metric("✅ Activos", activos)
          st.metric("⚠️ Suspendidos", suspendidos)
          st.metric("❌ Retirados", retirados)
          st.metric("🆕 Nuevos", nuevos)


         # Gráficos en columna derecha
        with col_graficos:

          sub1, sub2 = st.columns([2,4])  # dos subcolumnas
          with sub1:
              st.markdown("### 📈 Visualizaciones")
          with sub2:
              st.markdown(f"#### {subtitulo}")  # subtítulo dinámico de filtros aplicados

         #===========================
         # Primera fila de gráficos
         # ============================

          g1, g2, g3, g4= st.columns([1,1,1,1])  
          with g1:
           st.plotly_chart(fig_gauge_activos, use_container_width=True)
          with g2:
           st.plotly_chart(fig_gauge_suspendidos, use_container_width=True)
          with g3:
           st.plotly_chart(fig_gauge_retirados, use_container_width=True)
          with g4:
           st.plotly_chart(fig_gauge_nuevos, use_container_width=True)

         #==============================
         # Mostrar los 4 gráficos en una sola fila
         # ============================
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
          col5, col6, col7, col8 = st.columns([3,1,1,1])  # gráfico más ancho
          with col5:
                st.plotly_chart(fig_planes_estado, use_container_width=True)
          with col6:
                st.plotly_chart(fig_activos_mun, use_container_width=True)
          with col7:
                st.plotly_chart(fig_retirados_mun, use_container_width=True)
          with col8:
                st.plotly_chart(fig_suspendidos_mun, use_container_width=True)   

#====================================
# 💰 Página: Dashboard de Facturación
# ===================================

elif pagina == "Dashboard Facturacion":

    # Filtros especificos de selectbox
    st.sidebar.subheader("Filtros de Facturacion")

     # Selección del tipo de dato a visualizar (Ingresos, Egresos, Gastos)
    tipo_dato = st.sidebar.selectbox("Tipo de facturacion:", ["ingresos"])

    # Selección del año de facturación
    año_factura = st.sidebar.selectbox("Año:", ["Todo", "2019","2020","2021","2022", "2023", "2024","2025"])

     # Selección del mes de facturación
    mes_factura = st.sidebar.selectbox("Mes:", [
        "Todo", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
        "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ])

    # ---------------------------
    # 🏷️ Título del dashboard
    # ---------------------------

    st.markdown("""
    <h1 style='
        font-family: "Roboto", sans-serif;
        font-size: 32px;
        color: #96d3ff;
        font-weight: 600;
        margin-bottom: 20px;
    '>
    💰 Dashboard de Facturación
    </h1>
    """, unsafe_allow_html=True)

    # ---------------------------
    # 📂 Preparación del DataFrame
    # ---------------------------
    df_facturacion = df.copy()   # aquí usas tu df real

    # Filtros básicos
    if año_factura != "Todo":
        df_facturacion = df_facturacion[df_facturacion["f_emision_factura"].dt.year == int(año_factura)]

    # Filtro por mes
    if mes_factura != "Todo":
        MESES = {"Enero":"January","Febrero":"February","Marzo":"March","Abril":"April",
                 "Mayo":"May","Junio":"June","Julio":"July","Agosto":"August",
                 "Septiembre":"September","Octubre":"October","Noviembre":"November","Diciembre":"December"}
        df_facturacion = df_facturacion[df_facturacion["f_emision_factura"].dt.month_name() == MESES[mes_factura]]

    # ================================
    # Subtítulo dinámico con filtros
    # ================================
    subtitulo2 = "📍 Filtros aplicados:" 
    if tipo_dato != "ingresos": 
        subtitulo2 = f"📍 Tipo de dato: {tipo_dato}"   
    if año_factura != "Todo":
        subtitulo2 += f" | Año: {año_factura}"
    if mes_factura != "Todo":
        subtitulo2 += f" | Mes: {mes_factura}"

    #==============================
    # 🧮 Preparar datos para gráficos
    #=============================

    # Reemplazar strings vacíos o solo espacios por NaN
    df_facturacion = df_facturacion.replace(r'^\s*$', np.nan, regex=True)

    # Eliminar filas con NaN en columnas clave
    df_facturacion = df_facturacion.dropna(subset=['id_plan_internet_cliente','total_factura','neto_transaccion'])

    # Quitar filas donde el plan esté vacío
    df_facturacion = df_facturacion[df_facturacion['id_plan_internet_cliente'].str.strip() != ""]

    # Aplicar strip() a todas las columnas de tipo string
    df_facturacion = df_facturacion.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    #==============================
    #graficos 
    #==============================

    # Preparar datos mensuales
    MES_MAP = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
     }

    # Extraer mes numérico y nombre del mes
    df_facturacion['mes_num'] = df_facturacion['f_emision_factura'].dt.month

    #este codigo mapea el numero del mes al nombre del mes es decir 1->Enero, 2->Febrero etc
    df_facturacion['mes_nombre'] = df_facturacion['mes_num'].map(MES_MAP) # mapa de número

    # Convertir a categoría ordenada para que Plotly respete el orden
    df_facturacion['mes_nombre'] = pd.Categorical( # convertir a categoría
    df_facturacion['mes_nombre'], # columna de mes
    categories=list(MES_MAP.values()), # categorías en orden
    ordered=True # ordenado
    )

    # Resumir datos por mes
    df_line = df_facturacion.groupby('mes_nombre').agg({ # agrupar por mes
    'total_factura':'sum', # suma total facturas facturadas
    'neto_transaccion':'sum' # suma neto transacciones cobradas
    }).reset_index() # resetear índice para gráfico

    # Calcular monto a cobrar
    df_line['monto_a_cobrar'] = df_line['total_factura'] - df_line['neto_transaccion']

    #=======================
    # 💰 Facturado
    #======================

    fig_facturado = px.line(
        df_line,
        x="mes_nombre",
        y="total_factura",
        labels={"total_factura":"Monto Facturado","mes":"Mes"},
        title="💰 Monto Facturado",
        markers=True  # activa los puntos en la curva
    )
    # Personalizar hover
    fig_facturado.update_traces(hovertemplate="Mes: %{x}<br>Facturado: $%{y:,.2f}") # formato moneda para hover
    fig_facturado.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))

    #==============
    # 💵 Cobrado
    #==============

    fig_cobrado = px.line(
        df_line,
        x="mes_nombre",
        y="neto_transaccion",
        labels={"neto_transaccion":"Monto Cobrado","mes":"Mes"},
        title="💵 Monto Cobrado",
        markers=True  # activa los puntos en la curva
    )
    fig_cobrado.update_traces(hovertemplate="Mes: %{x}<br>Facturado: $%{y:,.2f}")
    fig_cobrado.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))

    #================
    # 📌 a Cobrar
    #================

    # 📌 Monto a Cobrar
    fig_a_cobrar = px.line(
        df_line, x="mes_nombre", 
        y="monto_a_cobrar",
        labels={"monto_a_cobrar":"Monto a Cobrar","mes_nombre":"Mes"},
        title="📌 Monto a Cobrar",
        markers=True
    )
    fig_a_cobrar.update_traces(hovertemplate="Mes: %{x}<br>Facturado: $%{y:,.2f}")
    fig_a_cobrar.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))

    # ---------------------------
    # 🥧 Gráfico circular: Pagos en Divisas vs Bs
    # ---------------------------   

    # Diccionario de mapeo directo
    MAPEO_PAGOS = {
    "transferencia_divisas": "Divisas",
    "efectivo_divisas": "Divisas",
    "transferenacia_bolivares": "Bolívares",
    "efectivo_bolivares": "Bolívares",
    "pago_movil": "Bolívares",
    "nota_credito": "Otros"
    } 

    # Crear columna agrupada con replace
    df_facturacion['grupo_pago'] = df_facturacion['id_pasarela_pago'].replace(MAPEO_PAGOS)

    # Agrupar solo Divisas y Bs
    df_pagos_tipo = (
        #este codigo agrupa los pagos en divisas y bolivares el .isin es para filtrar solo esos dos grupos
    df_facturacion[df_facturacion['grupo_pago'].isin(["Divisas","Bolívares"])]
    .groupby('grupo_pago') # agrupar por tipo de pago
    .size() # contar cantidad
    .reset_index(name='cantidad') # resetear índice
    )

    # Crear gráfico circular
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
    # Mostrar % en el gráfico
    fig_pagos.update_traces(textinfo="percent+label")
    fig_pagos.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))

    #==============================================
    # 📊 Graficos Facturación y Cobranzas por Plan
    #==============================================

    # Agrupar por plan y sumar facturación/cobranzas
    resumen_planes = (
     df_facturacion.groupby('id_plan_internet_cliente')
     .agg({
        'total_factura':'sum',       # Facturación Activa ($)
        'neto_transaccion':'sum'     # Cobranzas Activas ($)
     })
     .reset_index()
    )

    # Reestructurar para gráfico de barras
    resumen_planes_melt = resumen_planes.melt(
     id_vars='id_plan_internet_cliente', # columna de planes
     value_vars=['total_factura','neto_transaccion'], # columnas a derretir
     var_name='tipo', # nombre de la nueva columna para tipos
     value_name='monto_usd' # nombre de la nueva columna para montos
    )

    # Renombrar etiquetas
    resumen_planes_melt['tipo'] = resumen_planes_melt['tipo'].replace({
     'total_factura':'Facturación Activa ($)', # etiqueta legible
     'neto_transaccion':'Cobranzas Activas ($)' # etiqueta legible
    })

    # Crear gráfico de barras agrupadas (side-by-side)
    fig_planes_factura = px.bar(
     resumen_planes_melt,
     x="monto_usd", # eje x con montos
     y="id_plan_internet_cliente", # eje y con planes
     color="tipo", # color por tipo
     text="monto_usd", # mostrar monto en barra
     barmode="group",  # barras lado a lado
     title="📊 Facturación y Cobranzas Activas por Plan (USD)",
     labels={ # etiquetas legibles
        "id_plan_internet_cliente":"Plan de Internet",
        "monto_usd":"Monto ($)",
        "tipo":"Tipo"
     }
    )

    # Ajustes visuales
    fig_planes_factura.update_traces( # ajustes de trazas
     texttemplate="$%{text:.2f}",  # formato moneda
     textposition="outside", # mostrar fuera de la barra
     hovertemplate="<b>Plan:</b> %{y}<br><b>Tipo:</b> %{fullData.name}<br>Monto: $%{x:,.2f}"# formato hover
   )
    # Diseño del gráfico
    fig_planes_factura.update_layout(
     height=500,
     width=900,
     showlegend=True
    ) 

    #=============================  
    # 🥧 Gráfico circular: Ingresos por Método de Pago
    #=============================

    # Agrupar por método de pago y sumar el neto transaccionado ($)
    df_metodos_pago = (
     df_facturacion.groupby('id_pasarela_pago')['neto_transaccion']
      .sum()
     .reset_index()
    )

    # Crear gráfico circular
    fig_metodos_pago = px.pie(
     df_metodos_pago,
     names="id_pasarela_pago",          # Método de pago
     values="neto_transaccion",         # Dinero total por método
     title="💳 Distribución de Ingresos por Método de Pago",
     color="id_pasarela_pago"
     )

    # Mostrar % y monto al pasar el mouse
    fig_metodos_pago.update_traces(
     textinfo="percent+label",
     hovertemplate="<b>Método:</b> %{label}<br>Ingresos: $%{value:,.2f}<br>%{percent}"
    )

     # Ajustar tamaño compacto
    fig_metodos_pago.update_layout(height=500, width=900)

    # ---------------------------
    # 📊 KPIs generales
    # ---------------------------

    if df_facturacion.empty:
        st.warning("⚠️ No hay datos de facturación para los filtros seleccionados.")
    else:
     # Fecha actual para cálculos de vencimiento
     hoy = pd.to_datetime("today")

     facturas_emitidas = len(df_facturacion) # facturas emitidas
     facturas_cobradas = len(df_facturacion[df_facturacion['f_transaccion'].notna()])  # facturas cobradas con fecha de transacción registrada

    # Facturas vencidas: vencimiento < hoy y con emisión registrada
    #este codigo cuenta las facturas vencidas y hace un filtro para evitar errores con nulos
     facturas_vencidas = len(df_facturacion[
        (df_facturacion['f_emision_factura'].notna()) & # emisión registrada para evitar errores y nulos
        (df_facturacion['f_vencimiento_factura'].notna()) & # vencimiento registrado para evitar errores y nulos
        (df_facturacion['f_vencimiento_factura'] < hoy) # vencidas de hoy y anteriores para saber las vencidas
     ])

     # Facturas anuladas: total factura = 0
     facturas_anuladas = len(df_facturacion[df_facturacion['total_factura'] == 0])
     facturado_total  = df_facturacion['total_factura'].sum()  # total facturado

     col_kpi, col_graf = st.columns([1,6])

     with col_kpi:
        st.markdown("### 📊 KPIs")
        st.metric("📄 Facturas Emitidas", facturas_emitidas)
        st.metric("⏰ Facturas Vencidas", facturas_vencidas)
        st.metric("✅ Facturas Cobradas", facturas_cobradas)
        st.metric("❌ Facturas Anuladas", facturas_anuladas)
        st.metric("💰 Facturado", f"${facturado_total:,.2f}")

     with col_graf:

        titu1, titu2 = st.columns([2,4])  # dos subcolumnas
        with titu1:
          st.markdown("### 📈 Evolución Anual de Montos")
        with titu2:
          st.markdown(f"#### {subtitulo2}")  # subtítulo dinámico de filtros aplicados

        col1, col2, col3, col4 = st.columns(4)
        with col1:
         st.plotly_chart(fig_facturado, use_container_width=True) 
        with col2:
         st.plotly_chart(fig_cobrado, use_container_width=True)
        with col3:
         st.plotly_chart(fig_a_cobrar, use_container_width=True)
        with col4:
         st.plotly_chart(fig_pagos, use_container_width=True)

        col5, col6 = st.columns([3,3])  # gráfico más ancho
        with col5:
         st.plotly_chart(fig_planes_factura, use_container_width=True)
        with col6:
            st.plotly_chart(fig_metodos_pago, use_container_width=True)

