#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


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

# In[8]:


#===========================
# Cargar CSS externon personalizado
#==========================

def cargar_css(ruta):
    with open(ruta) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# 🧵 Llamar la función con tu archivo
cargar_css("style.css")


# ##Configuracion de la pagina

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

if pagina == "Dashboard de Clientes":

    # 🎛️ Filtros especificos
    st.sidebar.subheader("Filtros de Cliente")

    cliente = st.sidebar.selectbox("Clientes:", ["Todo", "Nuevos", "Activos", "Suspendidos", "Retirados"])

    ubicacion = st.sidebar.selectbox("Ubicación/Municipo:", ["Nada", "Bolivar", "Urbaneja", "Satillo"])

    fecha = st.sidebar.selectbox("Año:", ["Nada", "2019", "2020", "2021", "2022", "2023", "2024"])

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


    #========================
    #Grafico barra de estado
    #========================

    def grafico_estado(df_input):

        if df_input.empty:
          return px.bar(title="⚠️ No hay datos para mostrar")

        resumen = df_input.groupby('id_estatus_servicio_cliente').size().reset_index(name='cantidad')
        resumen = resumen.rename(columns={'id_estatus_servicio_cliente': 'estado'})

        fig = px.bar(
         resumen,
         x='cantidad',
         y='estado',
         orientation='h',
         color='estado',
         title='📊 Total de Clientes por Estado',
         color_discrete_map={
            'activo': '#2ECC71',
            'suspendido': '#F1C40F',
            'retirado': '#E74C3C'
        }
        )
        fig.update_layout(xaxis_title= 'Cantidad de Clientes', yaxis_title='Estados')
        return fig

    #======================================
    #Grafico de Lineas por año y Mes
    #======================================

    def grafico_instalaciones(df_input):

      if df_input.empty:
          return px.line(title="⚠️ No hay datos para mostrar")

      df_temp = df_input[df_input['f_instalacion_cliente'].notna()].copy()
      df_temp['periodo'] = df_temp['f_instalacion_cliente'].dt.to_period('M').dt.to_timestamp()

      resumen = df_temp.groupby('periodo').size().reset_index(name='cantidad')

      fig = px.line(
         resumen,
         x='periodo',
         y='cantidad',
         markers=True,
         title='📈 Instalaciones por Mes y Año',
      )
      fig.update_traces(line=dict(color='#FF5733'))
      return fig

    #==============================================================
    # 📊 Clientes por ubicación (cuando se filtra por estado + ubicación)
    #==============================================================

    def grafico_estado_por_ubicacion(df_input):

        if df_input.empty:
          return px.bar(title="⚠️ No hay datos para mostrar")

        resumen = (
        df_input.groupby(['id_municipio_cliente','id_estatus_servicio_cliente'])
                .size()
                .reset_index(name='cantidad')
        )

        fig = px.bar(
         resumen,
         x='id_municipio_cliente',
         y='cantidad',
         color='id_estatus_servicio_cliente',
         barmode='group',
         title='📊 Clientes por Estado en cada Municipio',
         color_discrete_map={
            'activo': '#2ECC71',
            'suspendido': '#F1C40F',
            'retirado': '#E74C3C'
          }
        )
        fig.update_layout(xaxis_title= 'Municipios', yaxis_title='Cantidad de Clientes')
        return fig

    #===============================================
    # 📈 Evolución mensual del estado filtrado
    #==============================================

    def grafico_clientes_nuevos(df_input):

        if df_input.empty:
          return px.line(title="⚠️ No hay datos para mostrar")

        # Filtro fechas validas
        df_temp = df_input[df_input['f_instalacion_cliente'].notna()].copy()

        #extraer por anio
        df_temp['año'] = df_temp ['f_instalacion_cliente'].dt.year

        resumen = df_temp.groupby('año').size().reset_index(name='cantidad')

        #grafico lineal 
        fig = px.line(
            resumen,
            x='año',
            y='cantidad',
            markers=True,
            title = 'Clientes nuevos por Año',
        )
        fig.update_traces(line = dict(color='#3498DB', width = 2))
        fig.update_layout(xaxis_title= 'Año', yaxis_title='Clientes Nuevos')
        return fig
    #================================
    # 🧮 Aplicar filtros
    #================================

    df_filtrado = df.copy()

    if cliente.lower() != "Todo":
        df_filtrado = df_filtrado[df_filtrado["id_estatus_servicio_cliente"].str.lower() == cliente.lower()]

    if ubicacion.lower() != "Nada":
        df_filtrado = df_filtrado[df_filtrado["id_municipio_cliente"].str.lower() == ubicacion.lower()]

    if fecha != "Nada":
        df_filtrado = df_filtrado[df_filtrado["f_instalacion_cliente"].dt.year == int(fecha)]

    if mes != "Nada":
        df_filtrado = df_filtrado[df_filtrado["f_instalacion_cliente"].dt.month_name().str.lower() == mes.lower()]

    # ✅ Detectar si se seleccionó un estado específico sin filtros adicionales
    estado_especifico = cliente != "Todo"
    sin_filtros_adicionales = ubicacion == "Nada" and fecha == "Nada" and mes == "Nada"

    # ✅ Mostrar mensaje si hay estado pero sin filtros
    if estado_especifico and sin_filtros_adicionales:
      st.info("🔎 Selecciona los filtros que quieras aplicar para esta sección.")  

    # ========================
    # KPIs y gráficos según lógica
    # ========================

    vista_general = cliente == "Todo" and ubicacion == "Nada" and fecha == "Nada" and mes == "Nada"

    # ✅ Elegir fuente de datos
    df_kpi = df.copy() if vista_general else df_filtrado.copy()

    # ✅ Verificar si hay datos
    if df_kpi.empty:
     st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados.")

    else:
     # ============================
     # 📈 KPIs por cliente único (último estado)
     # ============================

    # Ordena por fecha para tomar el último estado por cliente
    # Usa la columna que mejor represente la "actualidad" del estado
     df_kpi = df_kpi.sort_values(by='f_transaccion', kind='mergesort') #filtracion en la clumna f_transaccion

    # Elimina duplicados manteniendo solo el último registro por cliente (index = codigo_cliente)
     df_estado_unico = df_kpi[~df_kpi.index.duplicated(keep='last')] #elimina duplicados para esta ocasion

     #Clientes totales
     total_clientes = df_estado_unico.index.nunique()
     #clientes activos
     activos = (df_estado_unico["id_estatus_servicio_cliente"] == "activo").sum()
     #clientes suspendidos
     suspendidos = (df_estado_unico["id_estatus_servicio_cliente"] == "suspendido").sum()
     #clientes retirados
     retirados = (df_estado_unico["id_estatus_servicio_cliente"] == "retirado").sum()

     #mostrar los kpis
     col1, col2, col3, col4 = st.columns(4)
     col1.metric("📌 Total Clientes", total_clientes)
     col2.metric("✅ Activos", activos)
     col3.metric("⚠️ Suspendidos", suspendidos)
     col4.metric("❌ Retirados", retirados)


      # ✅ Mostrar gráficos por estado + ubicación si están seleccionados
     if cliente != "Todo" and ubicacion != "Nada":

        subtitulo = f"📍 Estado: {cliente} | Ubicación: {ubicacion}" #titulo

        if fecha != "Nada":
            subtitulo += f" | Año: {fecha}"

        if mes != "Nada":
            subtitulo += f" | Mes: {mes}"
        st.subheader(subtitulo)

       #columanas para visualizar las tablas
        col1, col2, col3 = st.columns(2)

        with col1:
            #mostrar graficos
            st.plotly_chart(grafico_estado_por_ubicacion(df_estado_unico), use_container_width=False)


# ✅ Mostrar gráficos generales si no hay filtros activos
     elif vista_general:

        col1, col2 = st.columns(2)
        with col1:
          #mostrar grafico
           st.plotly_chart(grafico_estado(df_estado_unico), use_container_width=False)
        with col2:
          #mostrar grafico
          st.plotly_chart(grafico_instalaciones(df_estado_unico), use_container_width=False)

        col3, col4 = st.columns(2)

        with col3:
            st.plotly_chart(grafico_estado_por_ubicacion(df_estado_unico), use_container_width=False)

        with col4:
            st.plotly_chart(grafico_clientes_nuevos(df_estado_unico), use_container_width=False) 
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

