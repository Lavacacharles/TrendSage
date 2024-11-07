import streamlit as st
import time
import os
from dotenv import load_dotenv
import openai
from apify_client import ApifyClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from PIL import Image
import pandas as pd
from tiktok_downloader import ttdownloader
import logging
import moviepy.editor as mp
from faster_whisper import WhisperModel
import json
from datetime import datetime
import re
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer, WordNetLemmatizer
from wordcloud import WordCloud
from textblob import TextBlob
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from typing import Optional

# Cargar variables de entorno
load_dotenv(dotenv_path="keys_scrapper.env")

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Configuración de variables
APIFY_KEY = os.getenv("APIFY_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")
EMPRESA_NOMBRE = os.getenv("EMPRESA_NOMBRE")
APIFY_ACTOR = os.getenv("APIFY_ACTOR")
INSTAGRAM_USER = os.getenv("INSTAGRAM_USER")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Asegúrate de reemplazar '/ruta/a/tu/chromedriver' con la ruta real de tu ChromeDriver
CHROMEDRIVER_PATH = '/ruta/a/tu/chromedriver'  # <-- Actualiza esta ruta

# Funciones de Scraping y Procesamiento

def query4o_Mini(query):
    os.environ.pop("OPENAI_KEY", None)
    load_dotenv(dotenv_path="keys_scrapper.env")
    api_key = os.getenv("OPENAI_KEY")
    openai.api_key = api_key

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

def ParseHashTags(Modeltags):
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
            HashTagscadena += char

    HashTagsList = []
    nuevoTag = ""
    abreTag = False
    OpenClose = 0

    for char in HashTagscadena:
        if char == '"':
            OpenClose += 1
            abreTag = not abreTag
            continue
        if abreTag:
            nuevoTag += char
        if OpenClose == 2:
            OpenClose = 0
            HashTagsList.append(nuevoTag)
            nuevoTag = ""
    HashTagsList = HashTagsList[1:]
    HashTagsList = [tag[1:] for tag in HashTagsList]
    return HashTagsList

def HashTagScrapping(HashTagsList):
    os.environ.pop("APIFY_KEY", None)
    os.environ.pop("APIFY_ACTOR", None)
    load_dotenv(dotenv_path="keys_scrapper.env")
    apify_key = os.getenv("APIFY_KEY") 
    apify_actor = os.getenv("APIFY_ACTOR")

    client = ApifyClient(apify_key)
    run_input = {
        "hashtags": HashTagsList,
        "resultsPerPage": 5,
        "shouldDownloadVideos": True,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": True,
        "shouldDownloadSlideshowImages": False,
    }

    run = client.actor(apify_actor).call(run_input=run_input)

    ListData = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        ListData.append(item)
    return ListData

def ParseHashTagsScrapping(ListData):
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
            "IdVIdeo" : data['id'],
            "urls": data['mediaUrls']
        })
        VideoData.append(data['videoMeta'])
        Mentions.append({
            'IdVideo': data['id'],
            'mentions':data['mentions']
        })
        HashtagsData.append(data['hashtags'])
        EffectsStickers.append({
            'IdVideos': data['id'],
            'effectsStickers': data['effectStickers']
        })
        SearchHashtagMetrics.append(data['searchHashtag'])
    return JsonData, AuthorData, MusicData, MediaUrls, VideoData, Mentions, HashtagsData, EffectsStickers, SearchHashtagMetrics

def SaveData(ListData):
    JsonData, AuthorData, MusicData, MediaUrls, VideoData, Mentions, HashtagsData, EffectsStickers, SearchHashtagMetrics = ParseHashTagsScrapping(ListData=ListData)
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

    load_dotenv(dotenv_path="keys_scrapper.env")
    query_dir = os.getenv("EMPRESA_NOMBRE")

    videos_dir = os.path.join(query_dir, 'videos')
    audios_dir = os.path.join(query_dir, 'audios')
    transcriptions_dir = os.path.join(query_dir, 'transcriptions')
    
    for directory in [query_dir, videos_dir, audios_dir, transcriptions_dir]:
        os.makedirs(directory, exist_ok=True)

    DfAuthorData.to_csv(os.path.join(query_dir, "autores.csv"), index=False)
    DfMusicData.to_csv(os.path.join(query_dir, "música.csv"), index=False)
    DfVideoData.to_csv(os.path.join(query_dir, "videos.csv"), index=False)
    DfHashtagsData.to_csv(os.path.join(query_dir, "hashtags.csv"), index=False)
    DfJsonData.to_csv(os.path.join(query_dir,"publicaciones.csv"),index=False)

    return True

def download_videos(csv_file, videos_dir, sleep_time=5):
    load_dotenv(dotenv_path="keys_scrapper.env")
    custom_dir = os.getenv("EMPRESA_NOMBRE")
    logging.info(f"Verificando existencia de directorio de videos: {videos_dir}")
    
    os.makedirs(videos_dir, exist_ok=True)
    
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
        video_filename = f"video_tiktok_{custom_dir}_{idx}.mp4"
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

def convert_mp4_to_mp3(mp4_dir, mp3_dir):  
    logging.info(f"Verificando existencia de directorio de MP3: {mp3_dir}")
    os.makedirs(mp3_dir, exist_ok=True)
    
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

def transcribe_audios(mp3_dir, transcription_dir, model_size="medium", device="cpu", compute_type="int8"):
    logging.info(f"Verificando existencia de directorio de transcripciones: {transcription_dir}")
    os.makedirs(transcription_dir, exist_ok=True)
    
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

def InstagramScrappingOneHashTag(html, hashtag):
    soup = BeautifulSoup(html, 'html.parser')

    main_div = soup.find('div', class_='x9f619 x78zum5 xdt5ytf x1iyjqo2 x6ikm8r x1odjw0f xh8yej3 xocp1fn')
    if not main_div:
        logging.warning(f"No se encontró el div principal para el hashtag: {hashtag}")
        return

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

    with open(f'{hashtag}_usuarios.json', 'w', encoding='utf-8') as json_file:
        json.dump(resultado, json_file, indent=4, ensure_ascii=False)

def InstagramLogin(HashTagsList):
    service = Service(CHROMEDRIVER_PATH)  # <-- Actualiza esta ruta
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.instagram.com/")

    # Evitar problemas con SSL
    ssl._create_default_https_context = ssl._create_unverified_context

    # Login
    time.sleep(4)
    username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    username.clear()
    password.clear()
    username.send_keys(INSTAGRAM_USER)
    password.send_keys(INSTAGRAM_PASSWORD)
    login = driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    try:
        not_now = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Ahora no")]'))
        )
        not_now.click()
        not_now_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Ahora no")]'))
        )
        not_now_button.click()
    except Exception as e:
        logging.warning(f"No se pudo cerrar las ventanas emergentes: {e}")

    search_icon = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='Buscar']"))
    )

    search_icon.click()
    searchbox = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Buscar entrada']")
    searchbox.clear()
    for hashtag in HashTagsList:
        searchbox.send_keys(hashtag)
        time.sleep(5)
        html = driver.page_source
        InstagramScrappingOneHashTag(html, hashtag)
    driver.quit()

# Funciones de EDA y Análisis

# 1. Preparación de Datos
class PrepareDataEDA(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X['text'] = X['text'].astype(str)
        X['text'] = X['text'].apply(self.normalize_styled_text)
        X['hashtags'] = X['text'].apply(lambda x: ' '.join(re.findall(r'#\w+', x)))
        X['hashtag_count'] = X['hashtags'].apply(lambda x: len(x.split()) if x else 0)
        X['text'] = X['text'].str.replace(r'#\w+', '', regex=True).str.strip()
        X['text'] = X['text'].str.replace(r'[^\w\s]', '', regex=True).str.strip()
        return X
    
    def normalize_styled_text(self, text):
        normalized = unicodedata.normalize('NFKD', text)
        return normalized.lower()

# 2. Eliminación de Stop Words
class RemoveStopwordsEDA(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.stop_words = set(stopwords.words('english')).union(set(stopwords.words('spanish')))
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X['text'] = X['text'].apply(lambda text: ' '.join([word for word in text.split() if word not in self.stop_words]))
        return X

# 3. Normalización (Lemmatization)
class NormalizeTextLemmatizationEDA(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = SnowballStemmer('spanish')

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        def lemmatize_text(text):
            words = text.split()
            return ' '.join([self.stemmer.stem(word) if self.detect_language(word) == 'es' else self.lemmatizer.lemmatize(word) for word in words])
        
        X['text'] = X['text'].apply(lemmatize_text)
        return X
    
    def detect_language(self, word):
        if re.search(r'[ñáéíóú]', word):
            return 'es'
        else:
            return 'en'

# 4. Análisis de Ngrams
class AnalyzeNgramsEDA(BaseEstimator, TransformerMixin):
    def __init__(self, n=2):
        self.n = n
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        def get_ngrams(text, n):
            tokens = text.split()
            ngrams = zip(*[tokens[i:] for i in range(n)])
            return [' '.join(ngram) for ngram in ngrams]
        
        X[f'bigrams'] = X['text'].apply(lambda text: get_ngrams(text, 2))
        X[f'trigrams'] = X['text'].apply(lambda text: get_ngrams(text, 3))
        return X

# 5. Creación de Nubes de Palabras
def create_wordcloud(data, column):
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=20).generate(' '.join(data[column]))
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f"WordCloud for {column}")
    st.pyplot(plt)

# 6. Cálculo de Frecuencia de Términos
def term_frequency(data, column):
    term_freq = pd.Series(' '.join(data[column]).split()).value_counts()
    term_freq = term_freq[term_freq.index.str.match(r'^\w{2,}$')]
    st.write("Top 10 Term Frequency:")
    st.write(term_freq.head(10))
    return term_freq

# 7. Análisis de Sentimientos con TextBlob
class AnalyzeSentimentEDA(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        # Análisis de sentimiento en texto principal
        X['sentiment_analysis'] = X['text'].apply(lambda x: sentiment_category_textblob(x))
        # Puedes agregar más análisis si lo deseas
        return X

def sentiment_category_textblob(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        return 'Positive'
    elif polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'

# 8. Funciones de Análisis de Sentimientos con OpenAI

def analyze_sentiment(text: Optional[str]) -> str:
    if not text:
        return "No text provided"
    
    try:
        api_key = OPENAI_API_KEY
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes sentiment."},
                {"role": "user", "content": f"Analyze the sentiment of this text: '{text}', respond in Spanish, please"}
            ],
            max_tokens=100
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_sentiment_percentages(text: Optional[str]) -> str:
    if not text:
        return "No text provided"
    
    try:
        api_key = OPENAI_API_KEY
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes sentiment."},
                {"role": "user", "content": f"Analyze the following text and provide the percentage breakdown of the main emotions (happiness, sadness, anger, fear, surprise): '{text}', would you like to give it to me in list format (ex: ['happiness':0.25, 'sadness':0.25, 'anger':0.25, 'fear':0.25, 'surprise':0.25]), just return the list to me, nothing more "}
            ],
            max_tokens=100
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# Funciones de Recomendaciones e Insights

def recomendacion_descripcion(df: pd.DataFrame, cantidad: int, api:str ) -> str:
    df_filter = df[df["playCount"] > cantidad]
    text = " ".join(df_filter["text"].astype(str).values)
    
    try:
        openai.api_key = api
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "you are in charge of the marketing sector"},
                {"role": "user", "content": f"Below you have all the descriptions of videos that have a number of views greater than {cantidad}, which is the following {text}, I want you to analyze everything and return me the ideal description to create a high-impact video that produces great number of views. (Give me the description in Spanish please)(It is a description of tiktok, it should not be large in size)The characters should not exceed 50-100 [just give me the description, don't give me any more extra]"}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def ideas_principales(df: pd.DataFrame, cantidad: int ,num_ideas: int, api:str) -> str:
    df_filter = df[df["playCount"] > cantidad]
    text = " ".join(df_filter["text"].astype(str).values)
    
    try:
        openai.api_key = api
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "you are in charge of the marketing sector"},
                {"role": "user", "content": f"Below you have all the descriptions of videos that have a number of views greater than {cantidad}, which is the following {text},I want you to analyze these descriptions and tell me what are the {num_ideas} main ideas that the videos have(Give me the description in Spanish please)[I want you to put it in this format ['idea1','idea2', etc]]"}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def hashtags_ideales(df: pd.DataFrame, cantidad: int, num_hash: int, api: str) -> list:
    df_filter = df[df["playCount"] > cantidad]
    hashtags = "|".join(df_filter["hashtags"].astype(str).values)
    views = "|".join(df_filter["playCount"].astype(str).values)
    
    try:
        openai.api_key = api
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a hashtag analysis assistant."},
                {"role": "user", "content": f"Provide only a list of the top {num_hash} most impactful hashtags based on this data: views {views} and hashtags {hashtags} [hashtags per video are separated by '|']. Output only in this format: ['hashtag1', 'hashtag2', ...]"}
            ]
        )
        return eval(response.choices[0].message.content.strip())
    except Exception as e:
        return f"Error: {str(e)}"

def ideas_principales2(df: pd.DataFrame, num_ideas: int, api:str) -> str:
    text = "|".join(df["contenido_limpio"].astype(str).values)
    
    try:
        openai.api_key = api
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "you are in charge of the marketing sector"},
                {"role": "user", "content": f"Below you have all the transcripts of the videos that have a good number of views, these are the transcripts of the video {text} [they are separated by the transcripts from each other with '|'], I want you to analyze these transcripts and tell me which ones They are the {num_ideas} main ideas that the videos have (Give me the description in Spanish please) [I want you to put it in this format ['idea1','idea2', etc]]"}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def ideas_video(df: pd.DataFrame, num_ideas: int, api:str) -> str:
    text = "|".join(df["contenido_limpio"].astype(str).values)
    
    try:
        openai.api_key = api
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "you are in charge of the marketing sector"},
                {"role": "user", "content": f"Below you have all the transcripts of the videos that have a good number of views, these are the transcripts of the video {text} [they are separated by the transcripts from each other with '|'], I want you to analyze the descriptions and give me this many ideas {num_ideas} for future tik tok videos (Give me the description in Spanish please) [I want you to put it in this format ['idea1','idea2', etc]]"}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def idea_guion(df: pd.DataFrame, topic:str, api:str) -> str:
    text = "|".join(df["contenido_limpio"].astype(str).values)
    
    try:
        openai.api_key = api
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "you are in charge of the marketing sector"},
                {"role": "user", "content": f"Below you have all the transcripts of the videos that have a good number of views, these are the transcripts of the video {text} [they are separated by the transcripts from each other with '|'], I want you to analyze the descriptions and give me a script idea for a future TikTok video that I want to make that is a little related to this topic {topic}(Give me the description in Spanish please)"}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def resumen(df: pd.DataFrame, api:str) -> str:
    text = "|".join(df["contenido_limpio"].astype(str).values)
    
    try:
        openai.api_key = api
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "you are in charge of the marketing sector"},
                {"role": "user", "content": f"Below you have all the transcripts of the videos that have a good number of views, these are the transcripts of the video {text} [they are separated by the transcripts from each other with '|'], I want you to analyze the transcripts and give me a general summary of the videos(Give me the description in Spanish please)[in paragraph format]"}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def columnas_ideales(df: pd.DataFrame, peticion: str, api_key: str) -> list:
    columnas = list(df.columns)
    
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data analysis assistant."},
                {"role": "user", "content": f"Here are the columns: {columnas}. Please suggest the best columns for this request: '{peticion}'. Only return them as a Python list in this format: ['column1', 'column2', ...]. No additional explanation."}
            ]
        )
        recommended_columns = eval(response.choices[0].message.content.strip())
        return recommended_columns
    except Exception as e:
        logging.error(f"Error in columnas_ideales: {str(e)}")
        return []

def peticion_personalizada(df: pd.DataFrame, peticion: str, api_key: str) -> dict:
    columnas_recomendadas = columnas_ideales(df, peticion, api_key)
    existing_cols = [col for col in columnas_recomendadas if col in df.columns]

    if not existing_cols:
        return {"analysis": "Error: The provided DataFrame is empty or no matching columns found. Please provide a non-empty DataFrame with relevant columns to analyze.", "num_columns": 0, "num_rows": 0}

    df_recomendado = df[existing_cols]
    info_columnas = df_recomendado.to_string(index=False)

    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data analysis assistant."},
                {"role": "user", "content": f"Here is data for the relevant columns for this request: '{peticion}'.\n\n{info_columnas}\n\nPlease provide an analysis or insights based on this data.(Give me the description in Spanish please)"}
            ]
        )
        analysis = response.choices[0].message.content
        return {"analysis": analysis, "num_columns": len(existing_cols), "num_rows": len(df_recomendado)}
    except Exception as e:
        logging.error(f"Error in peticion_personalizada: {str(e)}")
        return {"analysis": "Error: Unable to perform analysis.", "num_columns": 0, "num_rows": 0}

# Interfaz de Usuario con Streamlit

def main():
    st.title("Consultor de Búsqueda y Análisis de Redes Sociales")

    if 'step' not in st.session_state:
        st.session_state.step = 1

    # Paso 1: Preguntas
    if st.session_state.step == 1:
        st.header("Paso 1: Información Básica")
        empresa = st.text_input("¿Cuál es el nombre de tu empresa o sector?", "")
        objetivo = st.text_input("¿Cuál es tu objetivo principal para esta búsqueda?", "")
        
        if st.button("Siguiente"):
            if empresa and objetivo:
                # Actualizar variables de entorno
                os.environ['EMPRESA_NOMBRE'] = empresa.replace(" ", "_")
                load_dotenv(dotenv_path="keys_scrapper.env", override=True)
                st.session_state.step = 2
            else:
                st.warning("Por favor completa ambos campos.")

    # Paso 2: Generar Sugerencias de Hashtags
    if st.session_state.step == 2:
        st.header("Paso 2: Generando Sugerencias de Hashtags")
        with st.spinner("Generando sugerencias de búsqueda..."):
            query = f"I need popular hashtags for {objetivo} in {empresa} in a list of Json"
            Modeltags = query4o_Mini(query=query)
            HashTagsList = ParseHashTags(Modeltags=Modeltags)
            st.session_state.hashtags = HashTagsList
            st.session_state.step = 3

    # Paso 3: Mostrar Sugerencias de Consulta
    if st.session_state.step == 3:
        st.header("Paso 3: Sugerencias de Búsqueda")
        st.write("Basado en tu información, aquí tienes algunas sugerencias de búsqueda en TikTok e Instagram:")
        for tag in st.session_state.hashtags:
            st.write(f"- {tag}")
        
        if st.button("Proceder con el Scraping"):
            st.session_state.step = 4

    # Paso 4: Scraping y Procesamiento
    if st.session_state.step == 4:
        st.header("Paso 4: Scraping y Procesamiento de Datos")
        with st.spinner("Extrayendo datos de redes sociales..."):
            # Scraping de Hashtags
            ListData = HashTagScrapping(st.session_state.hashtags)
            if SaveData(ListData):
                st.success("Datos guardados con éxito!")

            # Descarga de Videos
            load_dotenv(dotenv_path="keys_scrapper.env")
            query_dir = os.getenv("EMPRESA_NOMBRE")
            video_dir = os.path.join(query_dir, 'videos')
            mp3_dir = os.path.join(query_dir, 'audios')
            transcription_dir = os.path.join(query_dir, 'transcriptions')
            download_videos(os.path.join(query_dir, "publicaciones.csv"), video_dir)
            convert_mp4_to_mp3(video_dir, mp3_dir)
            transcribe_audios(mp3_dir, transcription_dir, model_size="medium", device="cpu", compute_type="int8")

            # Scraping de Instagram
            InstagramLogin(st.session_state.hashtags)

            st.session_state.step = 5

    # Paso 5: Análisis Exploratorio de Datos (EDA)
    if st.session_state.step == 5:
        st.header("Paso 5: Análisis Exploratorio de Datos (EDA)")
        with st.spinner("Procesando y analizando datos..."):
            # Cargar los datos procesados
            try:
                publicaciones_path = os.path.join(os.getenv("EMPRESA_NOMBRE"), "publicaciones.csv")
                processed_data = pd.read_csv(publicaciones_path)
            except FileNotFoundError:
                st.error("Archivo 'publicaciones.csv' no encontrado.")
                return

            # Aplicar Pipeline de EDA
            pipeline_steps = [
                ('prepare_data', PrepareDataEDA()), 
                ('remove_stopwords', RemoveStopwordsEDA()),
                ('normalize_text', NormalizeTextLemmatizationEDA()),
                ('analyze_ngrams', AnalyzeNgramsEDA()),
                ('analyze_sentiment', AnalyzeSentimentEDA())
            ]
            pipeline = Pipeline(steps=pipeline_steps)
            processed_data = pipeline.fit_transform(processed_data)

            # Guardar datos procesados
            processed_data.to_csv(os.path.join(os.getenv("EMPRESA_NOMBRE"), "processed_data.csv"), index=False)

            # Mostrar resultados de EDA
            st.subheader("WordCloud de Textos")
            create_wordcloud(processed_data, 'text')

            st.subheader("Frecuencia de Términos")
            term_freq = term_frequency(processed_data, 'text')

            st.subheader("Análisis de Sentimientos")
            sentiment_counts = processed_data['sentiment_analysis'].value_counts()
            st.bar_chart(sentiment_counts)

            st.session_state.processed_data = processed_data
            st.session_state.step = 6

    # Paso 6: Recomendaciones e Insights
    if st.session_state.step == 6:
        st.header("Paso 6: Recomendaciones e Insights")
        processed_data = st.session_state.processed_data

        st.subheader("Recomendación de Descripción Ideal")
        cantidad_vistas = st.number_input("Ingrese el umbral de vistas para filtrar los videos:", min_value=0, value=10000)
        if st.button("Generar Recomendación de Descripción"):
            recomendacion = recomendacion_descripcion(processed_data, cantidad_vistas, OPENAI_API_KEY)
            st.write(recomendacion)

        st.subheader("Ideas Principales de los Videos")
        num_ideas = st.number_input("Ingrese el número de ideas principales a obtener:", min_value=1, value=3)
        if st.button("Generar Ideas Principales"):
            ideas_prin = ideas_principales(processed_data, cantidad_vistas, num_ideas, OPENAI_API_KEY)
            st.write(ideas_prin)

        st.subheader("Hashtags Ideales")
        num_hash = st.number_input("Ingrese el número de hashtags ideales a obtener:", min_value=1, value=3)
        if st.button("Generar Hashtags Ideales"):
            hashtags = hashtags_ideales(processed_data, cantidad_vistas, num_hash, OPENAI_API_KEY)
            st.write(hashtags)

        st.subheader("Ideas Principales Basadas en Transcripción")
        if st.button("Generar Ideas Basadas en Transcripción"):
            ideas_prin2 = ideas_principales2(processed_data, num_ideas, OPENAI_API_KEY)
            st.write(ideas_prin2)

        st.subheader("Ideas para Videos")
        if st.button("Generar Ideas para Videos"):
            ideas = ideas_video(processed_data, num_ideas, OPENAI_API_KEY)
            st.write(ideas)

        st.subheader("Idea de Guion")
        tema = st.text_input("Ingrese el tema para el guion del video:", "cupcakes de navidad")
        if st.button("Generar Idea de Guion"):
            guion = idea_guion(processed_data, tema, OPENAI_API_KEY)
            st.write(guion)

        st.subheader("Resumen General de los Videos")
        if st.button("Generar Resumen"):
            resumen_text = resumen(processed_data, OPENAI_API_KEY)
            st.write(resumen_text)

        st.subheader("Insight Personalizado")
        peticion = st.text_input("Ingrese tu petición personalizada para el análisis de datos:", "quiero que me digas que topicos puedo hacer para mis futuros videos")
        if st.button("Generar Insight Personalizado"):
            insight = peticion_personalizada(processed_data, peticion, OPENAI_API_KEY)
            st.write(insight['analysis'])

        st.session_state.step = 7

    # Paso 7: Finalizado
    if st.session_state.step == 7:
        st.header("Proceso Completado")
        st.success("El scraping, procesamiento y análisis se han completado exitosamente.")
        st.balloons()

if __name__ == "__main__":
    main()
