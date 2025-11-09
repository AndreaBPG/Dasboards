#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

path = "Consolidado Cobranzas.xlsx"#cargando documento
df_cliente = pd.read_excel(path, sheet_name="Dim_Clientes")#hoja excel 
df_Factura = pd.read_excel(path, sheet_name="Dim_Facturas")#hoja excel

#===========================
# Cargar CSS externon personalizado
#==========================

def cargar_css(ruta):
    with open(ruta) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# 🧵 Llamar la función con tu archivo
cargar_css("style.css")

#===========================================
#Configurar la página principal del dashboard
#==========================================

st.set_page_config(page_title="Soluciones Wireless", layout="wide")

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

#===============================================================
# Convertir a minúscula y estandarizar valores, procesamiento de datos
#================================================================
#convertir texto a minuscula y limpiar espacios
df_cliente = df_cliente.apply(lambda col: col.str.lower().str.strip() if col.dtype == "object" else col)

#normalizar nombres de columnas
df_cliente.columns = df_cliente.columns.str.strip().str.lower().str.replace(' ', '_')

#normalizar valores de columnas 'estado'
df_cliente["estado"] = df_cliente["estado"].replace({ 
    "activo": "activos",
    "suspendido": "suspendidos",
    "retirado": "retirados",
    "nuevo": "nuevos"
})
#convertir fechas y estableces indice
df_cliente["fecha_instalacion"] = pd.to_datetime(df_cliente["fecha_instalacion"], dayfirst=True, errors="coerce")
df_cliente.set_index("id_cliente", inplace=True)

# ================================
# Página: Dashboard de Clientes
# ================================

if pagina == "Dashboard de Clientes":
    # 🎛️ Filtros especificos
    st.sidebar.subheader("Filtros de Cliente")

    cliente = st.sidebar.selectbox("Clientes:", ["Todo", "Nuevos", "Activos", "Suspendidos", "Retirados"])

    ubicacion = st.sidebar.selectbox("Ubicación:", ["Todo", "Barcelona", "Lechería", "Puerto la Cruz"])

    fecha = st.sidebar.selectbox("Año:", ["Todo", "2019", "2020", "2021", "2022", "2023", "2024"])

    mes = st.sidebar.selectbox("Mes:", [
        "Todo", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
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

    if cliente.lower() != "todo":
        df_filtrado = df_filtrado[df_filtrado["estado"] == cliente.lower()]

    if ubicacion.lower() != "todo":
        df_filtrado = df_filtrado[df_filtrado["zona"] == ubicacion.lower()]

    if fecha != "Todo":
        df_filtrado = df_filtrado[df_filtrado["fecha_instalacion"].dt.year == int(fecha)]

    if mes != "Todo":
        df_filtrado = df_filtrado[df_filtrado["fecha_instalacion"].dt.month_name().str.lower() == mes.lower()]

    # 📈 KPIs
    #cuenta los clientes totales
    total_clientes = df_filtrado.index.nunique()

    #cuenta clientes activos
    activos = (df_filtrado["estado"] == "activos").sum()

    #cuenta clientes suspendidos
    suspendidos = (df_filtrado["estado"] == "suspendidos").sum()

    #cuenta clientes retirados
    retirados = (df_filtrado["estado"] == "retirados").sum()

    #Muestra los kpi
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📌 Total Clientes", total_clientes) #muestra los clientes totales
    col2.metric("✅ Activos", activos) #muestra clientes activos
    col3.metric("⚠️ Suspendidos", suspendidos) #muestra clientes suspendidos
    col4.metric("❌ Retirados", retirados) #muestra clientes retirados

# 📊 Gráfico por estado + total
    conteo_estado = df_filtrado["estado"].value_counts()
    conteo_estado["total"] = total_clientes

    df_grafico = conteo_estado.reset_index()
    df_grafico.columns = ["estado", "cantidad"]

    fig_estado = px.bar(
        df_grafico,
        x="estado",
        y="cantidad",
        color="estado",
        title="Grafico general de clientes"
    )
    st.plotly_chart(fig_estado, use_container_width=True)

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



# In[2]:


# Convertir todos los valores tipo texto a minúscula
df_cliente = df_cliente.apply(lambda col: col.str.lower() if col.dtype == "object" else col)


# In[10]:


df_cliente.columns = df_cliente.columns.str.strip().str.lower().str.replace(' ', '_')#Cambiar mayusculas en los nombres, espacios _


# In[ ]:


df_cliente.drop('movil',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('correo',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('cedula',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('direccion_principal',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('column27',axis=1, inplace=True)# Elimninar columnas
df_cliente.drop('nombre',axis=1, inplace=True)# Elimninar columnas
df_cliente.head()


# In[21]:


#df_cliente.set_index('id_cliente', inplace=True) #para colocar los indeces id_cliente como los indes de la tabla en panda
df_cliente.head()

