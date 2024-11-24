from apify_client import ApifyClient
import unicodedata
from openai import OpenAI
import json
def LimpiarQuery(query: str):
    query = query.lower()
    query = unicodedata.normalize('NFKD', query).encode('ascii', 'ignore').decode('utf-8')
    return query

def reemplazar_caracteres(texto: str):
    caracteres_a_reemplazar = ['"', ',', ':', '$', '%', '!', '.']
    for char in caracteres_a_reemplazar:
        texto = texto.replace(char, '')
    return texto

def query4o_Mini(query, openai_key):
    client = OpenAI(api_key=openai_key)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": query
            }
        ]
    )
    return completion.choices[0].message

def ScrapperTiktok(message_4o: list, token_apify: str, actor: str, resultados_por_pagina = 100, perfiles_maximos_por_busqueda = 2):

    client = ApifyClient(token_apify)
    # url_base = "https://www.tiktok.com/search?q="

    search_messages = [reemplazar_caracteres(message).split(' ')[1:] for message in message_4o.split('\n')]

    # url_queries = [
    #     url_base + "%20".join(LimpiarQuery(word) for word in query)
    #     for query in search_messages
    # ]
    search_queries = [" ".join(query) for query in search_messages]
    with open('./queries.json', 'w') as f:
        json.dump(search_queries, f)
    # return search_queries, url_queries
    run_input =   {
        "excludePinnedPosts": False,
        "resultsPerPage": resultados_por_pagina,
        "searchQueries": search_queries,
        "shouldDownloadCovers": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadVideos": False,
        "profileScrapeSections": [
            "videos"
        ],
        "searchSection": "",
        "maxProfilesPerQuery": perfiles_maximos_por_busqueda,
        "proxy": {
            "useApifyProxy": True
        },
    }
    run = client.actor(actor).call(run_input=run_input)
    data = []
    # return run
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        data.append(item)
    return data