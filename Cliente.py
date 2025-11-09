# Importar librerías necesarias
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as pl
import matplotlib.pyplot as plt

path = "Consolidado Cobranzas.xlsx"#cargando documento
df_cliente = pd.read_excel(path, sheet_name="Dim_Clientes")#hoja excel 
df_Factura = pd.read_excel(path, sheet_name="Dim_Facturas")#hoja excel

df_cliente.set_index('id_cliente', inplace=True) #para colocar los indeces id_cliente como los indes de la tabla en panda

# Cargar CSS externo
def cargar_css(ruta):
    with open(ruta) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# 🧵 Llamar la función con tu archivo
cargar_css("style.css")


#Configurar la página principal del dashboard
st.set_page_config(page_title="Soluciones Wireless", layout="wide")

# Menú lateral principal con navegación entre páginas
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

# ================================
# Página: Dashboard de Clientes
# ================================

if pagina == "Dashboard de Clientes":
    #  Filtros específicos para el dashboard de clientes
    st.sidebar.subheader("Filtros de Cliente")

    # Filtro por tipo de cliente
    cliente = st.sidebar.selectbox('Clientes:', ['Todo', 'Nuevos', 'Activos', 'Morosos', 'Retirados'])

    # Filtro por ubicación geográfica
    ubicacion = st.sidebar.selectbox('Ubicación:', ['Todo', 'Barcelona', 'Lechería', 'Puerto la Cruz'])

    # Filtro por año de instalación
    fecha = st.sidebar.selectbox('Año:', ['Todo', '2019', '2020', '2021', '2022', '2023', '2024'])

    # Filtro por mes de instalación
    Mes = st.sidebar.selectbox('Mes:', [
        'Todo', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo',
        'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ])

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
    
    st.markdown("Selecciona los filtros en el menú lateral para visualizar los KPIs.")
    # Aquí se insertará el bloque de KPIs y visualizaciones más adelante

# ================================
# Página: Panel de Facturación
# ================================

elif pagina == "Dashboard Facturacion":
    # Filtros específicos para la sección de facturación
    st.sidebar.subheader("Filtros de Facturación")

    # Filtro por tipo de dato financiero
    tipo_dato = st.sidebar.selectbox("Tipo de dato:", ["Ingresos", "Egresos", "Gastos"])

    # Filtro por año de facturación
    año_factura = st.sidebar.selectbox("Año:", ["Todo", "2022", "2023", "2024"])

    # Filtro por mes de facturación
    mes_factura = st.sidebar.selectbox("Mes:", [
        "Todo", "Enero", "Febrero", "Marzo", "Abril", "Mayo",
        "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ])

#Color y estilo al titulo de la pagina
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
    # Aquí se insertará la lógica para mostrar KPIs, tablas o gráficos de facturación