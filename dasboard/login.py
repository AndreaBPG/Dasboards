import streamlit as st
import os
import base64

# Configuración de página
st.set_page_config(page_title="SoluciónW", layout="wide")

# Cargar CSS personalizado
def cargar_css(ruta="styles/login.css"):
    if os.path.exists(ruta):
        with open(ruta) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error("No se encontró el archivo CSS")

cargar_css()

# Convertir imagen local a base64
def fondo_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

# Fondo general de la app
fondo_data_url = fondo_base64("img/fondoS.png")
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255,255,255,0.40), rgba(255,255,255,0.40)),
                    url("{fondo_data_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
""", unsafe_allow_html=True)

# Fondo del cuadro de login
fondo_box_url = fondo_base64("img/fondoS2.png")
st.markdown(f"""
    <style>
    .login-box {{
        background: linear-gradient(rgba(255, 255, 255, 0.60), rgba(255, 255, 255, 0.60)),
                    url("{fondo_box_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
""", unsafe_allow_html=True)

# Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state.logueado = False

# Mostrar login si no está logueado
    if not st.session_state.logueado:
    # Formulario HTML que envía datos por GET (se agregan a la URL)
     st.markdown("""
    <div class="login-container">
     <div class="login-info">
        <h1>Bienvenida a <span style="color:#0072C6;">SoluciónW</span></h1>
        <p class="intro">Tu espacio para gestionar, visualizar y tomar decisiones con claridad.</p>
        <blockquote class="quote">
            “La mejor manera de predecir el futuro es crearlo.”<br>– Peter Drucker
        </blockquote>
        <h3>¿Qué puedes hacer aquí?</h3>
        <ul class="benefits">
            <li>📊 Visualizar tus métricas en tiempo real</li>
            <li>📁 Acceder a reportes personalizados</li>
            <li>🔒 Gestionar tu información de forma segura</li>
        </ul>
    </div>
    <div class="login-box">
        <img src=" " width="100">
        <form method="get">
            <input name="username" placeholder="Username" class="input-field" />
            <input name="password" type="password" placeholder="Password" class="input-field" />
            <button class="login-button" type="submit">INGRESAR</button>
        </form>
    </div>
 </div>
 """, unsafe_allow_html=True)

    # Leer los datos desde la URL
    params = st.query_params
    usuario = params.get("username", "")
    clave = params.get("password", "")

    # Solo validar si los parámetros existen en la URL
    if "username" in params and "password" in params:
     if usuario == "andrea" and clave == "clave123":
        st.session_state.logueado = True
        st.rerun()
     else:
        st.error("Credenciales incorrectas")

    st.stop()

# Si está logueado, ejecutar dashboard
with open("dashboard.py", "r", encoding="utf-8") as f:
    exec(f.read())
