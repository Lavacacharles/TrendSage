# streamlit_app.py
# run the app with "streamlit run streamlit_app.py"
# Corregir errores de nombres de los archivos, que se guarden con el nombre de la query
# streamlit_app.py

import streamlit as st
import os
from scripts.tik_scraper import scrape_tiktok_search
from scripts.tik_vid_dowl import download_videos
from scripts.mp4_to_mp3 import convert_mp4_to_mp3
from scripts.transcription import transcribe_audios
import pandas as pd

def main():
    st.title("Pipeline de Scraping, Descarga, Conversión y Transcripción de Videos de TikTok")
    st.write("""
        Esta aplicación permite buscar videos en TikTok basados en una consulta, descargar los videos, extraer el audio, 
        transcribir el contenido de audio y visualizar los resultados.
    """)
    
    st.header("1. Configuración de la Consulta de Búsqueda")
    query = st.text_input("Ingrese la consulta de búsqueda:", "postres trend peru")
    num_videos = st.number_input("Número de videos a procesar:", min_value=1, max_value=100, value=9, step=1)
    base_output_dir = "data"  # Directorio base para almacenar todos los datos
    
    if st.button("Iniciar Pipeline"):
        if not query.strip():
            st.error("Por favor, ingrese una consulta de búsqueda válida.")
        else:
            st.success("Iniciando el pipeline...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Paso 1: Scraping
            status_text.text("1. Scraping de Videos...")
            df = scrape_tiktok_search(query, num_videos, base_output_dir)
            if df is None or df.empty:
                st.error("No se pudo scrapeadar ningún video. Verifique la consulta de búsqueda o intente nuevamente.")
                return
            progress_bar.progress(25)
            
            # Paso 2: Descarga de Videos
            status_text.text("2. Descargando Videos...")
            query_dir = os.path.join(base_output_dir, query.replace(' ', '_'))
            videos_dir = os.path.join(query_dir, "videos")
            csv_file = os.path.join(query_dir, 'scraped_data.csv')
            downloaded_videos = download_videos(csv_file, videos_dir)
            progress_bar.progress(50)
            
            # Paso 3: Conversión de MP4 a MP3
            status_text.text("3. Convirtiendo Videos a MP3...")
            audios_dir = os.path.join(query_dir, "audios")
            converted_audios = convert_mp4_to_mp3(videos_dir, audios_dir)
            progress_bar.progress(75)
            
            # Paso 4: Transcripción de Audio
            status_text.text("4. Transcribiendo Audios...")
            transcriptions_dir = os.path.join(query_dir, "transcriptions")
            transcriptions = transcribe_audios(audios_dir, transcriptions_dir)
            progress_bar.progress(100)
            
            status_text.text("Pipeline completado exitosamente.")
            st.balloons()
            
            # Mostrar Resultados
            st.header("2. Resultados")
            st.subheader("Datos Scrapeados")
            st.dataframe(df)
            
            st.subheader("Videos Descargados")
            for video_path in downloaded_videos:
                if os.path.exists(video_path):
                    st.video(video_path)
                else:
                    st.warning(f"El video no se encontró: {video_path}")
            
            st.subheader("Transcripciones")
            for transcription_path in transcriptions:
                if os.path.exists(transcription_path):
                    with open(transcription_path, 'r', encoding='utf-8') as file:
                        transcription_text = file.read()
                    st.text_area(os.path.basename(transcription_path), transcription_text, height=200)
                else:
                    st.warning(f"La transcripción no se encontró: {transcription_path}")

if __name__ == "__main__":
    main()

