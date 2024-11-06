import openai
import fastapi
from apify_client import ApifyClient
from unicodedata import name
from selenium import webdriver
import urllib.request
import requests
import ssl
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from PIL import Image
import sys
from dotenv import load_dotenv
import os
from facebook_scraper import get_profile
from urllib.parse import urlparse, parse_qs
import moviepy.editor as mp
from faster_whisper import WhisperModel
from tiktok_downloader import ttdownloader
import numpy as np
import json
from datetime import datetime
import time
import logging
import pandas as pd

class Automator:
    def __init__(self):
        load_dotenv(dotenv_path="keys_scrapper.env")
        self.apify_key = os.getenv("APIFY_KEY")
        self.openai_key = os.getenv("OPENAI_KEY")
        self.empresa_nombre = os.getenv("EMPRESA_NOMBRE")
        self.apify_actor = os.getenv("APIFY_ACTOR")
        self.instagram_user = os.getenv("INSTAGRAM_USER")
        self.instagram_password = os.getenv("INSTAGRAM_PASSWORD")
        openai.api_key = self.openai_key

    def query4o_Mini(self, query):
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": query}
            ],
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response['choices'][0]['message']['content']

    def ParseHashTags(self, Modeltags):
        HashTagscadena = ""
        empieza = False
        termina = False
        for char in Modeltags:
            if termina:
                break
            if char == '{':
                empieza = True
            if char == '}':
                termina = True
            if empieza:
                HashTagscadena = HashTagscadena + char

        HashTagsList = []
        nuevoTag = ""
        abreTag = False
        OpenClose = 0

        for char in HashTagscadena:
            if char == '\"':
                OpenClose += 1
                abreTag = not abreTag
                continue
            if abreTag:
                nuevoTag = nuevoTag + char
            if OpenClose == 2:
                OpenClose = 0
                HashTagsList.append(nuevoTag)
                nuevoTag = ""
        HashTagsList = HashTagsList[1:]
        HashTagsList = [tag[1:] for tag in HashTagsList]
        return HashTagsList

    def HashTagScrapping(self, HashTagsList):
        client = ApifyClient(self.apify_key)
        run_input = {
            "hashtags": HashTagsList,
            "resultsPerPage": 5,
            "shouldDownloadVideos": True,
            "shouldDownloadCovers": False,
            "shouldDownloadSubtitles": True,
            "shouldDownloadSlideshowImages": False,
        }

        run = client.actor(self.apify_actor).call(run_input=run_input)

        ListData = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            ListData.append(item)
        return ListData

    def ParseHashTagsScrapping(self, ListData):
        JsonData = []
        AuthorData = []
        MusicData = []
        MediaUrls = []
        VideoData = []
        Mentions = []
        HashtagsData = []
        EffectsStickers = []
        SearchHashtagMetrics = []
        for data in ListData:
            if 'error' in data.keys():
                continue

            JsonData.append({
                'id': data['id'],
                'text': data['text'],
                'createTime': data['createTime'],
                'createTimeISO': data['createTimeISO'],
                'isAd': data['isAd'],
                'isMuted': data['isMuted'],
                'webVideoUrl': data['webVideoUrl'],
                'diggCount': data['diggCount'],
                'shareCount': data['shareCount'],
                'playCount': data['playCount'],
                'collectCount': data['collectCount'],
                'commentCount': data['commentCount'],
                'isSlideshow': data['isSlideshow'],
                'isPinned': data['isPinned'],
                'isSponsored': data['isSponsored'],
                'input': data['input']
            })
            AuthorData.append(data['authorMeta'])
            MusicData.append(data['musicMeta'])
            MediaUrls.append({
                "IdVIdeo": data['id'],
                "urls": data['mediaUrls']
            })
            VideoData.append(data['videoMeta'])
            Mentions.append({
                'IdVideo': data['id'],
                'mentions': data['mentions']
            })
            HashtagsData.append(data['hashtags'])
            EffectsStickers.append({
                'IdVideos': data['id'],
                'effectsStickers': data['effectStickers']
            })
            SearchHashtagMetrics.append(data['searchHashtag'])
        return JsonData, AuthorData, MusicData, MediaUrls, VideoData, Mentions, HashtagsData, EffectsStickers, SearchHashtagMetrics

    def SaveData(self, ListData):
        JsonData, AuthorData, MusicData, MediaUrls, VideoData, Mentions, HashtagsData, EffectsStickers, SearchHashtagMetrics = self.ParseHashTagsScrapping(ListData=ListData)
        DfJsonData = pd.DataFrame(JsonData)
        if 'createTime' in DfJsonData.columns:
            DfJsonData['year'] = DfJsonData['createTime'].apply(lambda timestamp: datetime.fromtimestamp(timestamp).strftime('%Y'))
            DfJsonData['month'] = DfJsonData['createTime'].apply(lambda timestamp: datetime.fromtimestamp(timestamp).strftime('%m'))
            DfJsonData['day'] = DfJsonData['createTime'].apply(lambda timestamp: datetime.fromtimestamp(timestamp).strftime('%d'))
            DfJsonData['hour'] = DfJsonData['createTime'].apply(lambda timestamp: datetime.fromtimestamp(timestamp).strftime('%H'))
            DfJsonData['minute'] = DfJsonData['createTime'].apply(lambda timestamp: datetime.fromtimestamp(timestamp).strftime('%M'))
            DfJsonData['second'] = DfJsonData['createTime'].apply(lambda timestamp: datetime.fromtimestamp(timestamp).strftime('%S'))
            DfJsonData = DfJsonData.drop(columns=["createTime", "createTimeISO"])
        DfAuthorData = pd.DataFrame(AuthorData)
        DfMusicData = pd.DataFrame(MusicData)
        DfVideoData = pd.DataFrame(VideoData)
        DfHashtagsData = pd.DataFrame(HashtagsData)

        query_dir = self.empresa_nombre
        videos_dir = os.path.join(query_dir, 'videos')
        audios_dir = os.path.join(query_dir, 'audios')
        transcriptions_dir = os.path.join(query_dir, 'transcriptions')

        for directory in [query_dir, videos_dir, audios_dir, transcriptions_dir]:
            os.makedirs(directory, exist_ok=True)

        DfAuthorData.to_csv(os.path.join(query_dir, "autores.csv"), index=False)
        DfMusicData.to_csv(os.path.join(query_dir, "música.csv"), index=False)
        DfVideoData.to_csv(os.path.join(query_dir, "videos.csv"), index=False)
        DfHashtagsData.to_csv(os.path.join(query_dir, "hashtags.csv"), index=False)
        DfJsonData.to_csv(os.path.join(query_dir, "publicaciones.csv"), index=False)

        return True

    def download_videos(self, csv_file, videos_dir, sleep_time=5):
        logging.basicConfig(level=logging.INFO)
        os.makedirs(videos_dir, exist_ok=True)
        logging.info(f"Verificando existencia de directorio de videos: {videos_dir}")

        try:
            df = pd.read_csv(csv_file)
            urls = df['webVideoUrl'].dropna().tolist()
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
            video_filename = f"video_tiktok_{self.empresa_nombre}_{idx}.mp4"
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

    def convert_mp4_to_mp3(self, mp4_dir, mp3_dir):
        logging.basicConfig(level=logging.INFO)
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

    def transcribe_audios(self, mp3_dir, transcription_dir, model_size="medium", device="cpu", compute_type="int8"):
        logging.basicConfig(level=logging.INFO)
        os.makedirs(transcription_dir, exist_ok=True)
        logging.info(f"Verificando existencia de directorio de transcripciones: {transcription_dir}")

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
                    segments = list(segments)

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

    def InstagramScrappingOneHashTag(self, html, hashtag):
        soup = BeautifulSoup(html, 'html.parser')
        main_div = soup.find('div', class_='x9f619 x78zum5 xdt5ytf x1iyjqo2 x6ikm8r x1odjw0f xh8yej3 xocp1fn')
        links = main_div.find_all('a', class_='x1i10hfl')
        resultado = []

        for link in links:
            nombre_span = link.find('span')
            nombre_usuario = nombre_span.get_text() if nombre_span else None
            if nombre_usuario:
                url_perfil = link['href']
                imagen_perfil = link.find('img')['src'] if link.find('img') else "Imagen no encontrada"

                resultado.append({
                    "nombre_usuario": nombre_usuario,
                    "url_perfil": f"https://instagram.com{url_perfil}",
                    "imagen_perfil": imagen_perfil
                })

        with open(f'{hashtag}_usuarios.json', 'w') as json_file:
            json.dump(resultado, json_file, indent=4)

    def InstagramLogin(self, HashTagsList):
        service = Service('D:/Mafer/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe')
        driver = webdriver.Chrome(service=service)
        driver.get("https://www.instagram.com/")

        ssl._create_default_https_context = ssl._create_unverified_context

        time.sleep(4)
        username = driver.find_element("css selector", "input[name='username']")
        password = driver.find_element("css selector", "input[name='password']")
        username.clear()
        password.clear()
        username.send_keys(self.instagram_user)
        password.send_keys(self.instagram_password)
        login = driver.find_element("css selector", "button[type='submit']").click()
        not_now = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Ahora no")]'))
        )
        not_now.click()
        not_now_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Ahora no")]'))
        )
        not_now_button.click()

        search_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='Buscar']"))
        )

        search_icon.click()
        searchbox = driver.find_element("css selector", "input[aria-label='Buscar entrada']")
        searchbox.clear()
        for hashtag in HashTagsList:
            searchbox.send_keys(hashtag)
            time.sleep(5)
            html = driver.page_source
            self.InstagramScrappingOneHashTag(html, hashtag)

def main():
    automator = Automator()
    query = "I need popular hashtags for cakes in peru during October in a list of Json"
    Modeltags = automator.query4o_Mini(query=query)
    HashTagsList = automator.ParseHashTags(Modeltags=Modeltags)
    ListData = automator.HashTagScrapping(HashTagsList)
    if automator.SaveData(ListData):
        print("Guardado")
    automator.download_videos(csv_file="CakesOctober/publicaciones.csv", videos_dir="CakesOctober/videos")
    automator.convert_mp4_to_mp3(mp4_dir="CakesOctober/videos", mp3_dir="CakesOctober/audios")
    automator.transcribe_audios(mp3_dir="CakesOctober/audios", transcription_dir="CakesOctober/transcriptions")
    automator.InstagramLogin(HashTagsList)

if __name__ == "__main__":
    main()