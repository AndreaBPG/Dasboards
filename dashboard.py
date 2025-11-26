#!/usr/bin/env python
# coding: utf-8

# In[14]:


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


# In[9]:


#===========================================
#Configurar la página principal del dashboard
#==========================================

st.set_page_config(page_title="Soluciones Wireless", layout="wide")


# ##Menu

# In[10]:


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
    📊 Dashboard de Clientes
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
        st.subheader(subtitulo)

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
          st.markdown("### 📈 Visualizaciones")

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

    # Selectbox de municipio
    municipio = st.sidebar.selectbox(
    "Selecciona el municipio",
    ["Todo", "bolivar","urbaneja", "sotillo"]
    )

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

     # Subtítulo dinámico según filtros
    st.markdown(f"Visualizando **{tipo_dato}** para el período seleccionado.")


    # ---------------------------
    # 📂 Preparación del DataFrame
    # ---------------------------

    #  Copiamos el DataFrame original (df) para trabajar solo con facturación
    df_facturacion = df.copy()

    #  Aseguramos que f_emision_factura sea datetime (si no lo está ya)
    #    Esto es importante para poder usar .dt.year, .dt.month y agrupar por periodos.
    if not pd.api.types.is_datetime64_any_dtype(df_facturacion["f_emision_factura"]):
        df_facturacion["f_emision_factura"] = pd.to_datetime(df_facturacion["f_emision_factura"], errors="coerce")

    #  Filtro por municipio
    if municipio != "Todo":
       df_facturacion = df_facturacion[df_facturacion["id_municipio_cliente"] == municipio]

    #  Filtro por año si se selecciona uno específico
    if año_factura != "Todo":
        df_facturacion = df_facturacion[df_facturacion['f_emision_factura'].dt.year == int(año_factura)]

    # Filtro por mes si se selecciona uno específico
    if mes_factura != "Todo":
        MESES = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
            "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
            "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }
        df_facturacion = df_facturacion[df_facturacion['f_emision_factura'].dt.month == MESES[mes_factura]]


    # ---------------------------
    # 📊 KPIs de Facturación
    # ---------------------------
    # Total de transacciones registradas
    total_transacciones = df_facturacion.shape[0]

    # Total de facturas emitidas (facturas con fecha válida)
    total_facturas = df_facturacion['f_emision_factura'].notna().sum()

    # Total facturado (suma de todas las facturas)
    total_facturado = df_facturacion['total_factura'].sum()

    # Ingresos (monto positivo en transacciones)
    ingresos = df_facturacion[df_facturacion['monto_transaccion'] > 0]['monto_transaccion'].sum()

    # Comisiones (suma de comisiones de transacciones)
    comisiones = df_facturacion['comision_transaccion'].sum()

    # Mostrar KPIs en columnas
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Transacciones", total_transacciones)
    col2.metric("🧾 Facturas Emitidas", total_facturas)
    col3.metric("📊 Total Facturado", f"${total_facturado:,.2f}")
    col4.metric("📈 Ingresos", f"${ingresos:,.2f}")
    col5.metric("💸 Comisiones", f"${comisiones:,.2f}")

    # ---------------------------
    # 📈 Gráficos generales de Facturación
    # ---------------------------

    # Primero creamos una columna "periodo" que convierte la fecha de emisión en un formato de mes/año.
    # Esto nos permite agrupar las transacciones por cada mes y ver la evolución temporal.
    df_facturacion['periodo'] = df_facturacion['f_emision_factura'].dt.to_period("M").dt.to_timestamp()

    # ============================================================
    # 📈 Gráfico 1: Ingresos por Mes
    # ============================================================


    # Filtramos solo las transacciones positivas (monto_transaccion > 0),
    #  porque representan dinero que entra a la empresa.
    df_ingresos = df_facturacion[df_facturacion['monto_transaccion'] > 0]

    # Agrupamos por "periodo" y sumamos los ingresos de cada mes.
    resumen_ingresos = df_ingresos.groupby('periodo')['monto_transaccion'].sum().reset_index()

    # Creamos un gráfico de línea para mostrar cómo evolucionan los ingresos mes a mes.
    fig_ingresos = px.line(
     resumen_ingresos,
     x='periodo',                # eje X = meses
     y='monto_transaccion',      # eje Y = suma de ingresos
     markers=True,               # mostramos puntos en la línea
     title="📈 Ingresos por Mes" # título del gráfico
    )

    # Personalizamos el estilo de la línea (color verde, grosor 2).
    fig_ingresos.update_traces(line=dict(color='#2ECC71', width=2))

    # Etiquetas de los ejes
    fig_ingresos.update_layout(yaxis_title="Ingresos ($)", xaxis_title="Periodo")


    # ============================================================
    # ⚖️ Gráfico 2: Balance Ingresos vs Egresos
    # ============================================================

    # Aquí no filtramos: usamos todos los montos de transacciones.
    #    Al sumar ingresos (positivos) y egresos (negativos) obtenemos el balance neto de cada mes.
    resumen_balance = df_facturacion.groupby('periodo')['monto_transaccion'].sum().reset_index()

    # Creamos un gráfico de barras para mostrar el balance mensual.
    fig_balance = px.bar(
     resumen_balance,
     x='periodo',                # eje X = meses
     y='monto_transaccion',      # eje Y = balance neto
     title="⚖️ Balance Ingresos vs Egresos por Mes",
     color='monto_transaccion',  # coloreamos según el valor (positivo/negativo)
     color_continuous_scale=['#E74C3C','#2ECC71']  # rojo = pérdida, verde = ganancia
    )

    # Etiquetas de los ejes
    fig_balance.update_layout(yaxis_title="Balance ($)", xaxis_title="Periodo")

   # ============================================================
   # 📊 Gráfico 3: Ingresos por Tipo de Factura
   # ============================================================
    resumen_tipo = df_facturacion.groupby('id_tipo_factura')['total_factura'].sum().reset_index()

    fig_tipo = px.bar(
     resumen_tipo,
     x='id_tipo_factura',
     y='total_factura',
     title="📊 Ingresos por Tipo de Factura",
     color='id_tipo_factura',
     color_discrete_map={
        'Servicio': '#3498DB',
        'Libre': '#9B59B6',
        'Especial': '#F1C40F'
      }
    )
    fig_tipo.update_layout(yaxis_title="Total Facturado ($)", xaxis_title="Tipo de Factura")

  # ============================================================
  # 🏙️ Gráfico 4: Ingresos por Municipio
  # ============================================================

   # Agrupamos por id_municipio_cliente y sumamos ingresos
    resumen_municipio = df_facturacion.groupby('id_municipio_cliente')['monto_transaccion'].sum().reset_index()  

    fig_municipio = px.line(
    resumen_municipio,
    x='id_municipio_cliente',      # eje X = municipios
    y='monto_transaccion',         # eje Y = suma de ingresos
    markers=True,                  # puntos en la línea
    title="🏙️ Ingresos por Municipio"
   )

    fig_municipio.update_traces(line=dict(color='#9B59B6', width=2))
    fig_municipio.update_layout(yaxis_title="Ingresos ($)", xaxis_title="Municipio")

# ============================================================
# 📌 Layout condicional
# ============================================================
    if año_factura == "Todo" and mes_factura == "Todo":

    # Mostrar en columnas (2x2)
     col1, col2 = st.columns(2)
     with col1:
        st.plotly_chart(fig_ingresos, use_container_width=True)
     with col2:
        st.plotly_chart(fig_balance, use_container_width=True)

     col3, col4 = st.columns(2)
     with col3:
        st.plotly_chart(fig_tipo, use_container_width=True)
     with col4:
         st.plotly_chart(fig_municipio, use_container_width=True)

    else:
    # Mostrar
        col1, col2 = st.columns(2)
        with col1:
         st.plotly_chart(fig_ingresos, use_container_width=True)
        with col2:
         st.plotly_chart(fig_balance, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
         st.plotly_chart(fig_tipo, use_container_width=True)
        with col4:
         st.plotly_chart(fig_municipio, use_container_width=True)

