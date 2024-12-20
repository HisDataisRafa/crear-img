from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

def setup_browser():
    """Configura el navegador Chrome"""
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = webdriver.ChromeService(
        executable_path=r"C:\Users\ASUS\Downloads\chromedriver_win32\chromedriver.exe"
    )
    
    print("Iniciando Chrome...")
    return webdriver.Chrome(service=service, options=options)

def generate_images(driver, prompt, index, save_folder):
    """Genera 2 imágenes usando PicLumen"""
    try:
        driver.get("https://piclumen.com/app/image-generator/create")
        print(f"\nGenerando imágenes para prompt {index}...")
        time.sleep(5)
        
        # Configura el ratio 9:16
        ratio_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='1:1 (1024 x 1024)']"))
        )
        ratio_button.click()
        time.sleep(2)
        
        ratio_916_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '9:16')]"))
        )
        ratio_916_option.click()
        
        # Configura 2 imágenes
        num_images_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='1']"))
        )
        num_images_button.click()
        time.sleep(2)
        
        two_images_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='2']"))
        )
        two_images_option.click()
        
        # Ingresa el prompt
        input_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='What do you want to draw?']"))
        )
        input_field.clear()
        input_field.send_keys(prompt)
        
        # Genera imágenes
        generate_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate')]"))
        )
        generate_button.click()
        print("Esperando generación de imágenes...")
        time.sleep(45)
        
        # Guarda las imágenes
        image_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.result-image"))
        )
        
        for i, img in enumerate(image_elements[:2], 1):
            url = img.get_attribute('src')
            filename = f"imagen_{index}_{i}.png"
            filepath = os.path.join(save_folder, filename)
            
            response = requests.get(url)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Imagen {i} guardada: {filepath}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    IMAGES_FOLDER = "D:/Carpeta descripcion visual/imagenes_generadas"
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    
    print("Ingresa tus prompts separados por //")
    print("Ejemplo: prompt1 // prompt2 // prompt3")
    prompts_input = input("Prompts: ")
    prompts = [p.strip() for p in prompts_input.split("//")]
    
    driver = None
    try:
        driver = setup_browser()
        
        for i, prompt in enumerate(prompts, 1):
            if prompt.strip():
                print(f"\nProcesando prompt {i} de {len(prompts)}")
                generate_images(driver, prompt, i, IMAGES_FOLDER)
                
                if i < len(prompts):
                    print("\nEsperando 15 segundos antes del siguiente prompt...")
                    time.sleep(15)
    
    finally:
        if driver:
            driver.quit()
            print("\nNavegador cerrado.")

if __name__ == "__main__":
    main()
