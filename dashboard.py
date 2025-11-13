#!/usr/bin/env python
# coding: utf-8

# In[92]:


import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


# ##Cargando bases de datos

# In[93]:


path = "Consolidado Cobranzas.xlsx"#cargando documento
#leyendo hojas
df_cliente = pd.read_excel(path, sheet_name="Dim_Clientes")#hoja excel 
df_Factura = pd.read_excel(path, sheet_name="Dim_Facturas")#hoja excel


# ##Arreglos de la base de datos

# In[94]:


#===============================================================
# Convertir a minúscula y estandarizar valores, procesamiento de datos
#================================================================

#convertir texto a minuscula y limpiar espacios
df_cliente = df_cliente.apply(lambda col: col.str.lower().str.strip() if col.dtype == "object" else col)

#normalizar nombres de columnas
df_cliente.columns = df_cliente.columns.str.strip().str.lower().str.replace(' ', '_')

df_cliente.head()


# In[95]:


df_cliente.drop('movil',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('correo',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('cedula',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('direccion_principal',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('column27',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('nombre',axis=1, inplace=True)# Elimninar columnas
df_cliente.head()


# In[96]:


df_cliente.set_index('id_cliente', inplace=True) #para colocar los indeces id_cliente como los indes de la tabla en panda
df_cliente.head()


# In[97]:


#Filtrar registros con fecha válida usarlas en el kpis
df_con_fecha = df_cliente[df_cliente['fecha_instalacion'].notna()]


# ##Cargando css exterior personalizado

# In[98]:


#===========================
# Cargar CSS externon personalizado
#==========================

def cargar_css(ruta):
    with open(ruta) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# 🧵 Llamar la función con tu archivo
cargar_css("style.css")


# ##Configuracion de la pagina

# In[99]:


#===========================================
#Configurar la página principal del dashboard
#==========================================

st.set_page_config(page_title="Soluciones Wireless", layout="wide")


# ##Menu

# In[100]:


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

if pagina == "Dashboard de Clientes":
    # 🎛️ Filtros especificos
    st.sidebar.subheader("Filtros de Cliente")

    cliente = st.sidebar.selectbox("Clientes:", ["Todo", "Nuevos", "Activos", "Suspendidos", "Retirados"])

    ubicacion = st.sidebar.selectbox("Ubicación:", ["Nada", "Barcelona", "Lechería", "Puerto la Cruz"])

    fecha = st.sidebar.selectbox("Año:", ["Nada", "2019", "2020", "2021", "2022", "2023", "2024"])

    mes = st.sidebar.selectbox("Mes:", [
        "Nada", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
        "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ])
    # 🧩 Título del dashboard
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

    # 🧮 Aplicar filtros
    df_filtrado = df_cliente.copy()

    if cliente.lower() != "Todo":
        df_filtrado = df_filtrado[df_filtrado["estado"] == cliente.lower()]

    if ubicacion.lower() != "Nada":
        df_filtrado = df_filtrado[df_filtrado["zona"] == ubicacion.lower()]

    if fecha != "Nada":
        df_filtrado = df_filtrado[df_filtrado["fecha_instalacion"].dt.year == int(fecha)]

    if mes != "Nada":
        df_filtrado = df_filtrado[df_filtrado["fecha_instalacion"].dt.month_name().str.lower() == mes.lower()]

    # ✅ Detectar si se seleccionó un estado específico sin filtros adicionales
    estado_especifico = cliente != "Todo"
    sin_filtros_adicionales = ubicacion == "Nada" and fecha == "Nada" and mes == "Nada"

    # ✅ Mostrar mensaje si hay estado pero sin filtros
    if estado_especifico and sin_filtros_adicionales:
      st.info("🔎 Selecciona los filtros que quieras aplicar para esta sección.")  

    #========================
    #Grafico barra de estado
    #========================

    def grafico_estado(df):
     resumen = df['estado'].value_counts().reset_index()
     resumen.columns = ['estado', 'cantidad']

     fig = px.bar(
        resumen,
        x='estado',
        y='cantidad',
        color='estado',
        title='📊 Total de Clientes por Estado',
        color_discrete_map={
        'activo': '#2ECC71',      # verde
        'suspendido': '#F1C40F',  # amarillo
        'retirado': '#E74C3C'     # rojo
        }
    )
     return fig

    #======================================
    #Grafico de Lineas por año y Mes
    #======================================

    def grafico_instalaciones(df):
     df = df[df['fecha_instalacion'].notna()].copy()
     df['periodo'] = df['fecha_instalacion'].dt.to_period('M').dt.to_timestamp()

     resumen = df.groupby('periodo').size().reset_index(name='cantidad')

     fig = px.line(
        resumen,
        x='periodo',          # eje X: mes y año
        y='cantidad',         # eje Y: instalaciones
        markers=True,
        title='📈 Instalaciones por Mes y Año',
    )
     fig.update_traces(line=dict(color='#FF5733'))  # naranja fuerte
     return fig

    #==============================================================
    # 📊 Clientes por ubicación (cuando se filtra por estado + ubicación)
    #==============================================================

    def grafico_estado_por_ubicacion(df):
        resumen = df['zona'].value_counts().reset_index()
        resumen.columns = ['ubicacion', 'cantidad']

        fig = px.bar(
            resumen,
            x='ubicacion',
            y='cantidad',
            color='ubicacion',
            title='📊 Clientes por Ubicación',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        return fig
    #===============================================
    # 📈 Evolución mensual del estado filtrado
    #==============================================

    def grafico_lineas_estado(df):
        df = df[df['fecha_instalacion'].notna()].copy()
        df['periodo'] = df['fecha_instalacion'].dt.to_period('M').dt.to_timestamp()
        resumen = df.groupby('periodo').size().reset_index(name='cantidad')

        fig = px.line(
            resumen,
            x='periodo',
            y='cantidad',
            markers=True,
            title='📈 Evolución Mensual del Estado Seleccionado'
        )
        fig.update_traces(line=dict(color='#3498DB'))  # azul
        return fig

    # ========================
    # KPIs y gráficos según lógica
    # ========================

    vista_general = cliente == "Todo" and ubicacion == "Nada" and fecha == "Nada" and mes == "Nada"

    # ✅ Elegir fuente de datos
    df_kpi = df_cliente.copy() if vista_general else df_filtrado.copy()

    # ✅ Verificar si hay datos
    if df_kpi.empty:
     st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados.")

    else:
     # 📈 KPIs
     #Clientes totales
      total_clientes = df_kpi.index.nunique()
     #clientes activos
      activos = (df_kpi["estado"] == "activo").sum()
     #clientes suspendidos
      suspendidos = (df_kpi["estado"] == "suspendido").sum()
     #clientes retirados
      retirados = (df_kpi["estado"] == "retirado").sum()

      col1, col2, col3, col4 = st.columns(4)
      col1.metric("📌 Total Clientes", total_clientes)
      col2.metric("✅ Activos", activos)
      col3.metric("⚠️ Suspendidos", suspendidos)
      col4.metric("❌ Retirados", retirados)


      # ✅ Mostrar gráficos por estado + ubicación si están seleccionados
    if cliente != "Todo" and ubicacion != "Nada":

        subtitulo = f"📍 Estado: {cliente} | Ubicación: {ubicacion}"

        if fecha != "Nada":
            subtitulo += f" | Año: {fecha}"

        if mes != "Nada":
            subtitulo += f" | Mes: {mes}"
        st.subheader(subtitulo)

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(grafico_estado_por_ubicacion(df_filtrado), use_container_width=False)
        with col2:
            st.plotly_chart(grafico_lineas_estado(df_filtrado), use_container_width=False)

# ✅ Mostrar gráficos generales si no hay filtros activos
    elif vista_general:

      col1, col2 = st.columns(2)

      with col1:
        st.plotly_chart(grafico_estado(df_cliente), use_container_width=False)
      with col2:
        st.plotly_chart(grafico_instalaciones(df_cliente), use_container_width=False)

# ================================
# 💰 Página: Dashboard de Facturación
# ================================

elif pagina == "Dashboard Facturacion":

    st.sidebar.subheader("Filtros de Facturacion")

    tipo_dato = st.sidebar.selectbox("Tipo de dato:", ["Ingresos", "Egresos", "Gastos"])

    año_factura = st.sidebar.selectbox("Año:", ["Todo", "2022", "2023", "2024"])

    mes_factura = st.sidebar.selectbox("Mes:", [
        "Todo", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
        "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ])

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

    st.markdown(f"Visualizando **{tipo_dato}** para el período seleccionado.")
    # Aquí puedes agregar KPIs y gráficos de facturación más adelante


