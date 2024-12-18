import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from PIL import Image
import requests
from io import BytesIO

def configurar_driver():
    """Configura el navegador Chrome para la automatización"""
    opciones = webdriver.ChromeOptions()
    # Añadimos opciones para mejor rendimiento
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=opciones)

def generar_imagen(driver, descripcion, formato="9:16", cantidad=1):
    """
    Genera una imagen en piclumen.com con los parámetros especificados
    Retorna la URL de la imagen generada
    """
    try:
        # Navegamos a la página
        driver.get("https://piclumen.com/app/image-generator/create")
        
        # Esperamos a que cargue el campo de descripción
        campo_descripcion = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "prompt-input"))
        )
        
        # Ingresamos la descripción
        campo_descripcion.send_keys(descripcion)
        
        # Seleccionamos el formato
        formato_boton = driver.find_element(By.CSS_SELECTOR, f'[data-value="{formato}"]')
        formato_boton.click()
        
        # Seleccionamos la cantidad
        cantidad_selector = driver.find_element(By.ID, "quantity-select")
        cantidad_selector.click()
        driver.find_element(By.CSS_SELECTOR, f'[data-value="{cantidad}"]').click()
        
        # Generamos la imagen
        generar_boton = driver.find_element(By.ID, "generate-button")
        generar_boton.click()
        
        # Esperamos 10 segundos
        time.sleep(10)
        
        # Obtenemos la URL de la imagen generada
        imagen = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "generated-image"))
        )
        return imagen.get_attribute('src')
    
    except Exception as e:
        st.error(f"Error generando imagen: {str(e)}")
        return None

def main():
    st.title("Generador Automático de Imágenes con Piclumen")
    
    # Sección para subir el archivo Excel
    st.header("1. Sube tu archivo Excel")
    archivo = st.file_uploader("Selecciona tu archivo Excel", type=['xlsx', 'xls'])
    
    if archivo is not None:
        # Leemos el Excel
        df = pd.read_excel(archivo)
        st.success("✅ Archivo cargado correctamente")
        
        # Mostramos una vista previa de los datos
        st.header("2. Vista previa de las descripciones")
        st.dataframe(df)
        
        # Configuración de parámetros
        st.header("3. Configura los parámetros")
        col1, col2 = st.columns(2)
        with col1:
            formato = st.selectbox("Formato", ["9:16", "1:1", "16:9"])
        with col2:
            cantidad = st.selectbox("Cantidad de imágenes", [1, 2])
            
        # Botón para iniciar el proceso
        if st.button("🚀 Iniciar Generación de Imágenes"):
            # Creamos una carpeta para guardar las imágenes si no existe
            if not os.path.exists("imagenes_generadas"):
                os.makedirs("imagenes_generadas")
            
            # Iniciamos el navegador
            with st.spinner("Iniciando navegador..."):
                driver = configurar_driver()
                
            # Barra de progreso
            progreso = st.progress(0)
            estado = st.empty()
            
            try:
                for i, row in df.iterrows():
                    # Actualizamos el estado
                    estado.text(f"Procesando descripción {i+1} de {len(df)}")
                    
                    # Generamos la imagen
                    url_imagen = generar_imagen(driver, row['descripcion'], formato, cantidad)
                    
                    if url_imagen:
                        # Descargamos la imagen
                        response = requests.get(url_imagen)
                        imagen = Image.open(BytesIO(response.content))
                        
                        # Guardamos la imagen
                        nombre_archivo = f"imagen_{i+1}.png"
                        ruta_completa = os.path.join("imagenes_generadas", nombre_archivo)
                        imagen.save(ruta_completa)
                        
                        # Mostramos la imagen generada
                        st.image(imagen, caption=f"Imagen {i+1}: {row['descripcion'][:50]}...")
                    
                    # Actualizamos la barra de progreso
                    progreso.progress((i + 1) / len(df))
                
                st.success("¡Proceso completado! Las imágenes se han guardado en la carpeta 'imagenes_generadas'")
            
            except Exception as e:
                st.error(f"Ocurrió un error durante el proceso: {str(e)}")
            
            finally:
                # Cerramos el navegador
                driver.quit()

if __name__ == "__main__":
    main()
