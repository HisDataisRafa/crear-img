import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from PIL import Image
import io
import base64

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="PicLumen Image Generator", layout="wide")

# Inicialización del estado de la sesión
if 'proceso_completado' not in st.session_state:
    st.session_state.proceso_completado = False
if 'imagenes_generadas' not in st.session_state:
    st.session_state.imagenes_generadas = []
if 'progreso_actual' not in st.session_state:
    st.session_state.progreso_actual = 0

def seleccionar_modelo(driver):
    """
    Selecciona PicLumen Realistic v2 del menú desplegable
    """
    try:
        # Esperar y hacer clic en el selector de modelo
        selector_modelo = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-v-0ce92661=""]'))
        )
        selector_modelo.click()
        
        # Seleccionar PicLumen Realistic v2
        modelo_realista = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'PicLumen Realistic v2')]"))
        )
        modelo_realista.click()
        
        return True
    except Exception as e:
        st.error(f"Error seleccionando el modelo: {str(e)}")
        return False

def generar_imagen(driver, descripcion, formato="1:1"):
    """
    Genera una imagen basada en la descripción proporcionada
    """
    try:
        # Ingresar la descripción
        campo_descripcion = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='What do you want to draw?']"))
        )
        campo_descripcion.clear()
        campo_descripcion.send_keys(descripcion)
        
        # Seleccionar el formato
        formato_boton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-value="{formato}"]'))
        )
        formato_boton.click()
        
        # Hacer clic en Generate
        generar_boton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.generate-button"))
        )
        generar_boton.click()
        
        # Esperar a que se genere la imagen
        time.sleep(10)
        
        # Capturar la imagen generada
        imagen = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.generated-image"))
        )
        return imagen.get_attribute('src')
        
    except Exception as e:
        st.error(f"Error en la generación de imagen: {str(e)}")
        return None

def procesar_excel(df):
    """
    Procesa cada fila del Excel y genera las imágenes
    """
    barra_progreso = st.progress(0)
    estado = st.empty()
    
    # Configuración del navegador
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    
    try:
        for i, row in df.iterrows():
            estado.text(f"Procesando descripción {i+1} de {len(df)}")
            
            # Navegar a la página y seleccionar el modelo
            driver.get("https://piclumen.com/app/image-generator/create")
            if not seleccionar_modelo(driver):
                continue
            
            # Generar la imagen
            imagen_url = generar_imagen(driver, row['descripcion'])
            
            if imagen_url:
                # Guardar la imagen en el estado de la sesión
                st.session_state.imagenes_generadas.append({
                    'descripcion': row['descripcion'],
                    'url': imagen_url
                })
                
                # Mostrar la imagen generada
                st.image(imagen_url, caption=f"Imagen {i+1}: {row['descripcion']}")
            
            # Actualizar progreso
            st.session_state.progreso_actual = (i + 1) / len(df)
            barra_progreso.progress(st.session_state.progreso_actual)
            
    finally:
        driver.quit()

def descargar_imagen(url, nombre):
    """
    Crea un botón para descargar la imagen
    """
    try:
        response = requests.get(url)
        imagen_bytes = io.BytesIO(response.content)
        btn = st.download_button(
            label=f"Descargar {nombre}",
            data=imagen_bytes,
            file_name=f"{nombre}.png",
            mime="image/png"
        )
        return btn
    except Exception as e:
        st.error(f"Error al preparar la descarga: {str(e)}")
        return None

def main():
    st.title("Generador de Imágenes con PicLumen Realistic v2")
    
    # Subida de archivo Excel
    uploaded_file = st.file_uploader(
        "Sube tu archivo Excel con las descripciones",
        type=['xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        # Leer el Excel
        try:
            df = pd.read_excel(uploaded_file)
            st.write("Descripciones cargadas:", len(df))
            st.dataframe(df)
            
            # Botón para iniciar el proceso
            if st.button("Generar Imágenes"):
                procesar_excel(df)
                st.session_state.proceso_completado = True
            
            # Mostrar imágenes generadas
            if st.session_state.proceso_completado:
                st.success("¡Proceso completado!")
                
                for i, imagen in enumerate(st.session_state.imagenes_generadas):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.image(imagen['url'], caption=f"Imagen {i+1}")
                    with col2:
                        descargar_imagen(
                            imagen['url'],
                            f"imagen_{i+1}"
                        )
        
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")

if __name__ == "__main__":
    main()
