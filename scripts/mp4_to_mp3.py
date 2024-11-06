# scripts/mp4_to_mp3.py

import moviepy.editor as mp
import os
import logging

def convert_mp4_to_mp3(mp4_dir, mp3_dir):
    """
    Convierte todos los archivos MP4 en un directorio a archivos MP3 en otro directorio.

    :param mp4_dir: Directorio que contiene archivos MP4.
    :param mp3_dir: Directorio donde se guardarán los archivos MP3 convertidos.
    :return: Lista de rutas de archivos MP3 creados.
    """
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Verificar existencia de directorios
    os.makedirs(mp3_dir, exist_ok=True)
    logging.info(f"Verificando existencia de directorio de MP3: {mp3_dir}")
    
    converted_audios = []
    
    for filename in os.listdir(mp4_dir):
        if filename.lower().endswith('.mp4'):
            mp4_file_path = os.path.join(mp4_dir, filename)
            mp3_file_name = os.path.splitext(filename)[0] + '.mp3'
            mp3_file_path = os.path.join(mp3_dir, mp3_file_name)
    
            if os.path.exists(mp3_file_path):
                logging.info(f"MP3 para '{filename}' ya existe. Saltando conversión.")
                converted_audios.append(mp3_file_path)
                continue
    
            logging.info(f"Convirtiendo '{mp4_file_path}' a MP3...")
            try:
                with mp.VideoFileClip(mp4_file_path) as video_clip:
                    if video_clip.audio is None:
                        logging.warning(f"No se encontró audio en '{mp4_file_path}'. Saltando.")
                        continue
                    video_clip.audio.write_audiofile(mp3_file_path, logger=None)
                logging.info(f"MP3 guardado en: {mp3_file_path}")
                converted_audios.append(mp3_file_path)
            except Exception as e:
                logging.error(f"Fallo al convertir '{mp4_file_path}' a MP3: {e}")
                continue
    
    logging.info("Proceso de conversión de MP4 a MP3 completado.")
    return converted_audios

