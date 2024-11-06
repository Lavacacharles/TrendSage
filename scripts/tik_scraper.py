# scripts/tik_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas as pd
import os
import logging

def scrape_tiktok_search(query, num_videos=9, output_dir='data'):
    """
    Scrapea TikTok para obtener URLs de videos y metadatos basados en una consulta de búsqueda.

    :param query: Consulta de búsqueda en TikTok.
    :param num_videos: Número de videos a scrapeadar.
    :param output_dir: Directorio base donde se guardarán los datos.
    :return: DataFrame con los datos scrapeados.
    """
    logging.basicConfig(level=logging.INFO)
    
    query_dir = os.path.join(output_dir, query.replace(' ', '_'))
    scraped_data_path = os.path.join(query_dir, 'scraped_data.csv')
    videos_dir = os.path.join(query_dir, 'videos')
    audios_dir = os.path.join(query_dir, 'audios')
    transcriptions_dir = os.path.join(query_dir, 'transcriptions')
    
    for directory in [query_dir, videos_dir, audios_dir, transcriptions_dir]:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Verificando existencia de directorio: {directory}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Superar problemas de recursos limitados
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    logging.info("Inicializado WebDriver de Selenium.")
    
    try:
        # Codificar la consulta para la URL
        query_encoded = "%20".join(query.strip().split())
        url = f"https://www.tiktok.com/search?q={query_encoded}"
        driver.get(url)
        logging.info(f"Navegando a la URL: {url}")
    
        time.sleep(5)
    
        # Desplazarse para cargar contenido dinámico
        scroll_attempts = 5
        for attempt in range(scroll_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            logging.info(f"Desplazamiento {attempt + 1}/{scroll_attempts}.")
    
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info("Analizando contenido de la página con BeautifulSoup.")
    
        # Encontrar el contenedor principal
        main_container = soup.find('div', class_="css-188jcdv-DivMainContainer ea3pfar0")
        if not main_container:
            logging.error("No se encontró el contenedor principal.")
            return None
    
        # Encontrar los divs de videos
        video_divs = main_container.find_all('div', class_="css-1soki6-DivItemContainerForSearch e19c29qe19", limit=num_videos)
        logging.info(f"Encontrados {len(video_divs)} divs de videos.")
    
        data = []
    
        for idx, video in enumerate(video_divs, start=1):
            # Extraer URL del video
            video_container = video.find('a', class_="css-1g95xhm-AVideoContainer e19c29qe13")
            video_url = video_container.get('href') if video_container else None
    
            # Extraer descripción y hashtags
            h1_container = video.find('h1', class_="css-6opxuj-H1Container ejg0rhn1")
            description = h1_container.get_text(strip=True) if h1_container else None
    
            # Extraer recuento de videos
            strong_tag = video.find('strong', class_="css-ws4x78-StrongVideoCount etrd4pu10")
            video_count = strong_tag.get_text(strip=True) if strong_tag else None
    
            # Extraer nombre de usuario
            username_p = video.find('p', class_="css-2zn17v-PUniqueId etrd4pu6")
            username = username_p.get_text(strip=True) if username_p else None
    
            data.append({
                'Video URL': video_url,
                'Description & Hashtags': description,
                'Video Count': video_count,
                'Username': username
            })
    
            logging.info(f"Scrapeado video {idx}: {username}")
    
        df = pd.DataFrame(data)
        df.to_csv(scraped_data_path, index=False)
        logging.info(f"Datos scrapeados guardados en: {scraped_data_path}")
        return df
    
    except Exception as e:
        logging.error(f"Ocurrió un error durante el scraping: {e}")
        return None
    
    finally:
        driver.quit()
        logging.info("Cerrado WebDriver de Selenium.")

