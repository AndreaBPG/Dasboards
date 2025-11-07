# Importar librerías necesarias
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as pl
import matplotlib.pyplot as plt

# Cargar CSS externo
def cargar_css(ruta):
    with open(ruta) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# 🧵 Llamar la función con tu archivo
cargar_css("style.css")


#Configurar la página principal del dashboard
st.set_page_config(page_title="Soluciones Wireless", layout="wide")

# Menú lateral principal con navegación entre páginas
st.sidebar.title("Soluciones Wireless")
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

    # Título y descripción de la sección
    st.title("📊 Dashboard de Clientes")
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

    # Título y descripción de la sección
    st.title("💰 Dashboard de Facturación")
    st.markdown(f"Visualizando **{tipo_dato}** para el período seleccionado.")
    # Aquí se insertará la lógica para mostrar KPIs, tablas o gráficos de facturación


