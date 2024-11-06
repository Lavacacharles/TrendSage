# scripts/transcription.py

from faster_whisper import WhisperModel
import os
import logging

def transcribe_audios(mp3_dir, transcription_dir, model_size="medium", device="cpu", compute_type="int8"):
    """
    Transcribe todos los archivos MP3 en un directorio y guarda las transcripciones en otro directorio.

    :param mp3_dir: Directorio que contiene archivos MP3.
    :param transcription_dir: Directorio donde se guardarán las transcripciones.
    :param model_size: Tamaño del modelo Whisper (por defecto: "medium").
    :param device: Dispositivo para ejecutar el modelo ("cpu" o "cuda").
    :param compute_type: Tipo de cómputo para el modelo (por defecto: "int8").
    :return: Lista de rutas de archivos de transcripción creados.
    """
    logging.basicConfig(level=logging.INFO)
    
    # Verificar existencia de directorios
    os.makedirs(transcription_dir, exist_ok=True)
    logging.info(f"Verificando existencia de directorio de transcripciones: {transcription_dir}")
    
    # Inicializar el modelo Whisper
    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logging.info(f"Modelo Whisper '{model_size}' cargado en '{device}' con compute_type='{compute_type}'.")
    except Exception as e:
        logging.error(f"Fallo al cargar el modelo Whisper: {e}")
        return []
    
    transcriptions = []
    
    for filename in os.listdir(mp3_dir):
        if filename.lower().endswith('.mp3'):
            mp3_file_path = os.path.join(mp3_dir, filename)
            txt_file_name = os.path.splitext(filename)[0] + '.txt'
            txt_file_path = os.path.join(transcription_dir, txt_file_name)
    
            if os.path.exists(txt_file_path):
                logging.info(f"Transcripción para '{filename}' ya existe. Saltando transcripción.")
                transcriptions.append(txt_file_path)
                continue
    
            logging.info(f"Transcribiendo '{mp3_file_path}'...")
            try:
                segments, info = model.transcribe(mp3_file_path, beam_size=5)
                segments = list(segments)  # Ejecuta la transcripción
    
                with open(txt_file_path, "w", encoding="utf-8") as f:
                    f.write("Transcription:\n")
                    for segment in segments:
                        f.write(segment.text + "\n")
    
                logging.info(f"Transcripción guardada en: {txt_file_path}")
                transcriptions.append(txt_file_path)
            except Exception as e:
                logging.error(f"Fallo al transcribir '{mp3_file_path}': {e}")
                continue
    
    logging.info("Proceso de transcripción completado.")
    return transcriptions
