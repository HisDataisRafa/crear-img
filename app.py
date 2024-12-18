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

def generar_imagen(driver, descripcion):
    """
    Genera una imagen basada en la descripción proporcionada
    """
    try:
        # Ingresar la descripción
        campo_descripcion = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='What do you want to draw?']"))
        )
        campo_descripcion.send_keys(descripcion)
        
        # Configurar formato 1:1
        formato_boton = driver.find_element(By.CSS_SELECTOR, '[data-v-0ce92661="1:1"]')
        formato_boton.click()
        
        # Hacer clic en Generate
        generar_boton = driver.find_element(By.CSS_SELECTOR, "button.generate-button")
        generar_boton.click()
        
        # Esperar 10 segundos
        time.sleep(10)
        
        # Capturar la imagen generada
        imagen = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.generated-image"))
        )
        return imagen.get_attribute('src')
        
    except Exception as e:
        st.error(f"Error en la generación de imagen: {str(e)}")
        return None

def main():
    st.title("Generador de Imágenes con PicLumen")
    
    # Subida de archivo Excel
    uploaded_file = st.file_uploader("Sube tu archivo Excel con las descripciones", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("Descripciones cargadas:", len(df))
        st.dataframe(df)
        
        if st.button("Generar Imágenes"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                driver = webdriver.Chrome(options=options)
                
                for index, row in df.iterrows():
                    status_text.text(f"Procesando imagen {index + 1} de {len(df)}")
                    
                    # Navegar a la página
                    driver.get("https://piclumen.com/app/image-generator/create")
                    
                    # Seleccionar el modelo
                    if seleccionar_modelo(driver):
                        # Generar la imagen
                        imagen_url = generar_imagen(driver, row['descripcion'])
                        
                        if imagen_url:
                            st.session_state.imagenes_generadas.append({
                                'descripcion': row['descripcion'],
                                'url': imagen_url
                            })
                            
                            # Mostrar la imagen generada
                            st.image(imagen_url, caption=f"Imagen {index + 1}: {row['descripcion']}")
                    
                    # Actualizar la barra de progreso
                    progress_bar.progress((index + 1) / len(df))
                
                st.success("¡Proceso completado!")
                
            except Exception as e:
                st.error(f"Error en el proceso: {str(e)}")
                
            finally:
                driver.quit()

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
