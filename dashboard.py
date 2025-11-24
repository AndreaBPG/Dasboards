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


#=====================================
#Grafico barra de estado total cliente
#=====================================

    def grafico_estado(df_input):

        # Agrupar por estado del cliente y contar cuántos hay de cada uno
        resumen = df_input.groupby('id_estatus_servicio_cliente').size().reset_index(name='cantidad')
        resumen = resumen.rename(columns={'id_estatus_servicio_cliente': 'estado'})

        # Si el resumen está vacío, mostrar gráfico vacío con mensaje
        if df_input.empty:
          return px.bar(title="⚠️ No hay datos para mostrar")

        # Ordenar los estados en el orden lógico del embudo
        orden_estado = ["suspendido","retirado","activo"]
        resumen['estado'] = pd.Categorical(resumen['estado'], categories=orden_estado, ordered=True)
        resumen = resumen.sort_values('estado')

        # Si hay más de un estado, usar gráfico de barras horizontal
        if resumen['estado'].nunique() > 1:

         fig = px.funnel(
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
        else:
        # Si solo hay un estado, usar gráfico de línea para evitar barra gigante
         fig = px.line(
            resumen,
            x='estado',
            y='cantidad',
            markers=True,
            title='📈 Total de Clientes por Estado'
        )
         # Etiquetas de los ejes
        fig.update_layout(xaxis_title= 'Cantidad de Clientes', yaxis_title='Estados')
        return fig

#======================================
#Grafico de Lineas por año y Mes
#======================================

    def grafico_instalaciones(df_input):

        # Filtrar registros con fecha válida de instalación
        df_temp = df_input[df_input['f_instalacion_cliente'].notna()].copy()

        # Crear columna 'periodo' con año y mes como timestamp
        df_temp['periodo'] = df_temp['f_instalacion_cliente'].dt.to_period('M').dt.to_timestamp()

        # Agrupar por periodo y contar instalaciones
        resumen = df_temp.groupby('periodo').size().reset_index(name='cantidad')

        # Si no hay datos, mostrar gráfico vacío
        if df_input.empty:
          return px.line(title="⚠️ No hay datos para mostrar")

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

        # Agrupar por municipio y estado, contar clientes
        resumen = (
        df_input.groupby(['id_municipio_cliente','id_estatus_servicio_cliente'])
                .size()
                .reset_index(name='cantidad')
        )

        # Si no hay datos, mostrar gráfico vacío
        if df_input.empty:
          return px.bar(title="⚠️ No hay datos para mostrar")

        # Si hay varios municipios, usar gráfico de barras agrupadas
        if resumen['id_municipio_cliente'].nunique() > 1:

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

        else:
        # Si solo hay un municipio, usar gráfico de línea
         fig = px.line(
            resumen,
            x='id_municipio_cliente',
            y='cantidad',
            markers=True,
            title='📈 Clientes en Municipio seleccionado'
        )

        # Etiquetas de los ejes
        fig.update_layout(xaxis_title= 'Municipios', yaxis_title='Cantidad de Clientes')
        return fig

#===============================================
# 📈 Evolución mensual del estado filtrado
#==============================================

    def grafico_clientes_nuevos(df_input):

        # Filtrar registros con fecha válida
        df_temp = df_input[df_input['f_instalacion_cliente'].notna()].copy()

        # Extraer año de instalación
        df_temp['año'] = df_temp['f_instalacion_cliente'].dt.year

         # Agrupar por año y contar clientes
        resumen = df_temp.groupby('año').size().reset_index(name='cantidad')

        # Si no hay datos, mostrar gráfico vacío
        if resumen.empty:
         return px.line(title="⚠️ No hay datos para mostrar")

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

        # Mostrar KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📌 Total Clientes", total_clientes)
        col2.metric("✅ Activos", activos)
        col3.metric("⚠️ Suspendidos", suspendidos)
        col4.metric("❌ Retirados", retirados)
        col5.metric("🆕 Nuevos", nuevos)

        # ================================
        # Subtítulo dinámico con filtros
        # ================================
        subtitulo = "📊 Vista General de Clientes"
        if cliente != "Todo":
            subtitulo = f"📍 Estado: {cliente}"
        if ubicacion != "Nada":
            subtitulo += f" | Ubicación: {ubicacion}"
        if fecha != "Nada":
            subtitulo += f" | Año: {fecha}"
        if mes != "Nada":
            subtitulo += f" | Mes: {mes}"
        st.subheader(subtitulo)

        # ================================
        # Mostrar gráficos generales filtrados
        # Siempre se muestran los mismos 4 gráficos,
        # pero alimentados con df_estado_unico ya filtrado
        # ================================
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(grafico_estado(df_estado_unico), use_container_width=True)
        with col2:
            st.plotly_chart(grafico_instalaciones(df_estado_unico), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(grafico_estado_por_ubicacion(df_estado_unico), use_container_width=True)
        with col4:
            st.plotly_chart(grafico_clientes_nuevos(df_estado_unico), use_container_width=True)

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

     # Subtítulo dinámico según filtros
    st.markdown(f"Visualizando **{tipo_dato}** para el período seleccionado.")


    # ---------------------------
    # 📂 Preparación del DataFrame
    # ---------------------------

    # 👉 Copiamos el DataFrame original (df) para trabajar solo con facturación
    df_facturacion = df.copy()

    # 👉 Aseguramos que f_emision_factura sea datetime (si no lo está ya)
    #    Esto es importante para poder usar .dt.year, .dt.month y agrupar por periodos.
    if not pd.api.types.is_datetime64_any_dtype(df_facturacion["f_emision_factura"]):
        df_facturacion["f_emision_factura"] = pd.to_datetime(df_facturacion["f_emision_factura"], errors="coerce")

    # 👉 Filtro por año si se selecciona uno específico
    if año_factura != "Todo":
        df_facturacion = df_facturacion[df_facturacion['f_emision_factura'].dt.year == int(año_factura)]

    # 👉 Filtro por mes si se selecciona uno específico
    if mes_factura != "Todo":
        MESES = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
            "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
            "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }
        df_facturacion = df_facturacion[df_facturacion['f_emision_factura'].dt.month == MESES[mes_factura]]

    # 👉 Filtro por tipo de dato
    if tipo_dato == "Ingresos":
     df_facturacion = df_facturacion[df_facturacion['monto_transaccion'] > 0]
    elif tipo_dato == "Egresos":
     df_facturacion = df_facturacion[df_facturacion['monto_transaccion'] < 0]
    elif tipo_dato == "Gastos":
     df_facturacion = df_facturacion[df_facturacion['tipo_transaccion'] == "Gasto"]

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
# 📌 Layout condicional
# ============================================================
    if año_factura == "ingresos" and mes_factura == "Todo":

    # Mostrar en columnas (2x2)
     col1, col2 = st.columns(2)
     with col1:
        st.plotly_chart(fig_ingresos, use_container_width=True)
     with col2:
        st.plotly_chart(fig_balance, use_container_width=True)

     col3, col4 = st.columns(2)
     with col3:
        st.plotly_chart(fig_tipo, use_container_width=True)

    else:
    # Mostrar apilados
        col1, col2 = st.columns(2)
        with col1:
         st.plotly_chart(fig_ingresos, use_container_width=True)
        with col2:
         st.plotly_chart(fig_balance, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
         st.plotly_chart(fig_tipo, use_container_width=True)


# In[12]:


df.head()

