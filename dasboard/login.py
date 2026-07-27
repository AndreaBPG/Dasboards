import streamlit as st
import os
import base64
import sqlite3

#-----------------------------------------
#basede datos para nuevos usuarios SQlite
#-----------------------------------------
def crear_tabla_usuarios():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            clave TEXT
        )
    """)
    conn.commit()
    conn.close()

crear_tabla_usuarios()

#---------------------------------------------------------
#función para guardar nuevos usuarios en la base de datos
#---------------------------------------------------------

def guardar_usuario(nombre, clave):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO usuarios (nombre, clave) VALUES (?, ?)", (nombre, clave))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

#--------------------------------------
#funcion para eliminar usuarios de la base de datos
#--------------------------------------
def eliminar_usuario(nombre):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="SoluciónW", layout="wide")

# ---------------------------------------------------------
# FUNCIÓN PARA CARGAR CSS PERSONALIZADO
# ---------------------------------------------------------
def cargar_css(ruta="styles/login.css"):
    if os.path.exists(ruta):
        with open(ruta) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error("No se encontró el archivo CSS")

cargar_css()

# ---------------------------------------------------------
# FUNCIÓN PARA CONVERTIR IMÁGENES A BASE64
# ---------------------------------------------------------
def fondo_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

# ---------------------------------------------------------
# FONDO GENERAL
# ---------------------------------------------------------
fondo_data_url = fondo_base64("img/fondoS.png")
st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(rgba(255,255,255,0.40), rgba(255,255,255,0.40)),
                url("{fondo_data_url}");
    background-size: cover;
    background-position: center;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FONDO DEL CUADRO DE LOGIN
# ---------------------------------------------------------
fondo_box_url = fondo_base64("img/fondoS2.png")
st.markdown(f"""
<style>
.login-box {{
    background: linear-gradient(rgba(255, 255, 255, 0.60), rgba(255, 255, 255, 0.60)),
                url("{fondo_box_url}");
    background-size: cover;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# VARIABLES DE SESIÓN
# ---------------------------------------------------------
if "logueado" not in st.session_state:
    st.session_state.logueado = False

if "acceso_registro" not in st.session_state:
    st.session_state.acceso_registro = False

# ---------------------------------------------------------
# BLOQUE HTML DEL LOGIN (solo si no hay otras vistas)
# ---------------------------------------------------------
if (
    "registro" not in st.query_params and
    "pin" not in st.query_params and
    "ver_usuarios" not in st.query_params
):

 st.markdown("""
 <div class="login-container">
  <div class="login-info">
     <h1>Bienvenido a <span style="color:#0072C6;">Soluciones Wireless</span></h1>
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
    <form method="get">
        <input name="username" placeholder="Nombre de usuario" class="input-field" />
        <input name="password" type="password" placeholder="Contraseña" class="input-field" />
        <button class="login-button" type="submit">INGRESAR</button>
    </form>

    <p style="text-align:center; margin-top: 20px;">
        <a href="?registro=1" style="color:#0072C6; font-weight:bold;">
            Agregar nuevo usuario
        </a>
    </p>
  </div>
 </div>
 """, unsafe_allow_html=True)


# ---------------------------------------------------------
# BLOQUE HTML DEL PIN
# ---------------------------------------------------------
if "registro" in st.query_params:
    
    st.markdown("""
    <div class="overlay"></div>
    <div class="pin-container">
      <div class="pin-box">
        <h2>🔐 Acceso restringido</h2>
        <p>Ingrese el PIN de seguridad</p>
        <form method="get">
            <input name="pin" type="password" maxlength="4" placeholder="PIN" class="input-field" />
            <button class="login-button" type="submit">VALIDAR</button>
        </form>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# FORMULARIO DE CREACIÓN DE USUARIO
# ---------------------------------------------------------

if "pin" in st.query_params and st.query_params["pin"] == "2026":
    st.markdown("""
    <style>
    .user-container {
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        z-index: 999;
    }
    .user-box {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
        text-align: center;
        width: 320px;
    }
    .input-field {
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #ccc;
        border-radius: 6px;
    }
    .login-button {
        background-color: #0072C6;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
    }
    </style>

    <div class="user-container">
      <div class="user-box">
        <h2>👤 Crear nuevo usuario</h2>

      <form method="get">
            <input name="nuevo_nombre" placeholder="Nombre de usuario" class="input-field" />
            <input name="nuevo_clave" type="password" placeholder="Clave" class="input-field" />
            <button class="login-button" type="submit">REGISTRAR</button>
      </form>          
       
      <form method="get" style="margin-top:10px;">
        <input type="hidden" name="pin" value="2026">
        <input type="hidden" name="ver_usuarios" value="1">
        <button class="login-button" type="submit"> Ver usuarios registrados</button>
      </form>
        
      <form method="get" style="margin-top:10px;">
        <button type="submit"
        style="background-color:#ccc; color:#333; border:none; padding:6px 12px;
               border-radius:5px; cursor:pointer; font-size:12px;">
        ← Cerrar
        </button>
      </form>

      </div>
    </div>
    """, unsafe_allow_html=True)
 
# ---------------------------------------------------------
# PROCESAR REGISTRO DE NUEVO USUARIO
# ---------------------------------------------------------
if "nuevo_nombre" in st.query_params and "nuevo_clave" in st.query_params:

    nombre = st.query_params["nuevo_nombre"]
    clave = st.query_params["nuevo_clave"]

    if nombre.strip() == "" or clave.strip() == "":
        st.error("Debe ingresar un nombre y una clave válidos.")
    else:
        exito = guardar_usuario(nombre, clave)

        if exito:
            st.success(f"Usuario '{nombre}' registrado correctamente.")
        else:
            st.error("Ese nombre de usuario ya existe. Intente con otro.")
  
  
# ---------------------------------------------------------
# PROCESAR ELIMINACIÓN DE USUARIO
# ---------------------------------------------------------
if "eliminar" in st.query_params:
    usuario_a_eliminar = st.query_params["eliminar"]
    eliminar_usuario(usuario_a_eliminar)
    st.query_params.clear()  # Limpia la URL
    st.query_params["ver_usuarios"] = "1"  # Regresa a la lista
    st.rerun()

# ---------------------------------------------------------
# MOSTRAR USUARIOS REGISTRADOS (CON BOTÓN ELIMINAR)
# ---------------------------------------------------------
if "ver_usuarios" in st.query_params:

    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT nombre FROM usuarios")
    usuarios = c.fetchall()
    conn.close()

    lista_html = ""

    if usuarios:
        for u in usuarios:
            nombre = u[0]

            lista_html += (
                "<div style='display:flex; justify-content:space-between; align-items:center; margin:8px 0;'>"
                f"<span style='font-size:16px;'>• {nombre}</span>"
                "<form method='get' style='margin:0; padding:0;'>"
                f"<input type='hidden' name='eliminar' value='{nombre}'>"
                "<input type='hidden' name='ver_usuarios' value='1'>"
                "<button type='submit' "
                "style='background-color:#ff4d4d; color:white; border:none; padding:4px 10px; "
                "border-radius:5px; cursor:pointer; font-size:12px;'>"
                "Eliminar</button>"
                "</form>"
                "</div>"
            )
    else:
        lista_html = "<p>No hay usuarios registrados.</p>"

    html_final = (
        "<style>"
        ".lista-box {"
        "position: fixed;"
        "top: 50%; left: 50%;"
        "transform: translate(-50%, -50%);"
        "background: white;"
        "padding: 25px;"
        "border-radius: 12px;"
        "box-shadow: 0px 4px 20px rgba(0,0,0,0.3);"
        "width: 350px;"
        "text-align:center;"
        "z-index:999;"
        "}"
        "</style>"

        "<div class='lista-box'>"
        "<h2>📋 Usuarios registrados</h2>"
        f"{lista_html}"

        "<form method='get' style='margin-top:20px;'>"
        "<input type='hidden' name='pin' value='2026'>"
        "<button type='submit' style='background:none; border:none; color:#0072C6; font-weight:bold; cursor:pointer;'>"
        "Volver al registro"
        "</button>"
        "</form>"

        "</div>"
    )

    st.markdown(html_final, unsafe_allow_html=True)
