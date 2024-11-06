# scripts/tik_vid_dowl.py

from tiktok_downloader import ttdownloader
import pandas as pd
import time
import os
import logging

def download_videos(csv_file, videos_dir, sleep_time=5):
    """
    Descarga videos de TikTok desde un archivo CSV que contiene URLs de videos.

    :param csv_file: Ruta al archivo CSV con URLs de videos.
    :param videos_dir: Directorio donde se guardarán los videos descargados.
    :param sleep_time: Tiempo de espera en segundos entre descargas para respetar las políticas de TikTok.
    :return: Lista de rutas de videos descargados.
    """
    logging.basicConfig(level=logging.INFO)
    
    # Verificar existencia del directorio de videos
    os.makedirs(videos_dir, exist_ok=True)
    logging.info(f"Verificando existencia de directorio de videos: {videos_dir}")
    
    # Leer el archivo CSV
    try:
        df = pd.read_csv(csv_file)
        urls = df['Video URL'].dropna().tolist()
        logging.info(f"Leídos {len(urls)} URLs de video desde {csv_file}.")
    except FileNotFoundError:
        logging.error(f"Archivo CSV no encontrado: {csv_file}")
        return []
    except pd.errors.EmptyDataError:
        logging.error(f"Archivo CSV vacío: {csv_file}")
        return []
    except Exception as e:
        logging.error(f"Ocurrió un error al leer el CSV: {e}")
        return []
    
    downloaded_videos = []
    
    for idx, url in enumerate(urls, start=1):
        video_filename = f"video_{idx}_tiktok_postres_trend_peru.mp4"
        video_path = os.path.join(videos_dir, video_filename)
    
        if os.path.exists(video_path):
            logging.info(f"Video {idx} ya existe. Saltando descarga.")
            downloaded_videos.append(video_path)
            continue
    
        logging.info(f"Descargando video {idx} desde {url}...")
        try:
            downloader = ttdownloader(url)
            downloader[0].download(video_path)
            logging.info(f"Video {idx} descargado y guardado en: {video_path}")
            downloaded_videos.append(video_path)
        except Exception as e:
            logging.error(f"Fallo al descargar el video {idx} desde {url}: {e}")
            continue
    
        logging.info(f"Esperando {sleep_time} segundos antes de la próxima descarga...")
        time.sleep(sleep_time)
    
    logging.info("Proceso de descarga de videos completado.")
    return downloaded_videos

