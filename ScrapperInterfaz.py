from .ScrapperTools import *
from .ScrapperRequest import *
from .ScrapperCargarDrive import *
import os 
import json

def load_keys(dir_keys = './'):
    path_keys = "scrapper_keys.json"
    path_keys = os.path.join(dir_keys, path_keys)
    with open(path_keys, 'r') as f:
        keys_scrapper = json.load(f)
    path_keys = "drive_keys.json"
    path_keys = os.path.join(dir_keys, path_keys)
    with open(path_keys, 'r') as f:
        keys_drive = json.load(f)
    return keys_drive | keys_scrapper

def Interfaz(input_user):
    message_user = input_user['message_user']
    resultados_por_pagina = input_user['resultados_por_pagina']
    perfiles_maximos_por_busqueda = input_user['perfiles_maximos_por_busqueda']
    dir_data = input_user['dir_data']
    name_user = input_user['name_user']
    #----------------------------- Mensaje de prueba-------------------------#
    # message_user = """
    # Soy un empresario que vende zapatillas y necesito aumentar la visibilidad de mi marca, vendo en
    # Gamarra, Perú desde hace 1 año, ofrezco gran variedad de marcas a precios comodos pero no tengo clientes,
    # y por eso es quiero empezar en las redes sociales a publicitar mi marca """
    #----------------------------- Se cargan las llaves -------------------------#
    keys = load_keys(dir_data)
    TOKEN_APIFY = keys['token_apify']
    OPENAI_KEY = keys['openai_key']
    ACTOR_APIFY = keys['actor_apify']
    FOLDER_ID_DRIVE = keys['folder_id']
    #----------------------------- No modificar, es el prompt base -------------------------#
    message_promt = """
    Este es el mensaje de un usuario que describe su emprendimiento y la razón su necesidad de publicidad: {}
    \n Quiero solo una lista de mensajes de búsqueda como un cliente que busca productos del rubro del usuario,
    sin texto adicional""".format(message_user)

    #----------------------------- Obtener queries de gpt4o-mini -------------------------#
    message_4o = query4o_Mini(message_promt, OPENAI_KEY)
    message_4o = message_4o.content

    #----------------------------- Scrappear con Apify -------------------------#
    data = ScrapperTiktok(message_4o=message_4o, token_apify=TOKEN_APIFY, actor=ACTOR_APIFY, resultados_por_pagina=resultados_por_pagina, perfiles_maximos_por_busqueda=perfiles_maximos_por_busqueda)
    with open(os.path.join(dir_data, 'data_universidad.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    #----------------------------- Parsear y crear CVSs -------------------------#
    path_dict = ParseData_Mejorado(data=data,dir_data=dir_data, name_user=name_user)
    
    #----------------------------- Se suben los CSVs -------------------------#
    link_folder = SubirCSVs(dir_folder_credentials=dir_data, master_drive_key=FOLDER_ID_DRIVE, owner_data=name_user, path_dict=path_dict)
    # print(message_4o)
    return link_folder

def test_subir_datos():
    with open("data_zapatillas.json", 'r') as f:
        data = json.load(f)
    dir_data ='.'
    keys = load_keys(dir_data)
    TOKEN_APIFY = keys['token_apify']
    OPENAI_KEY = keys['openai_key']
    ACTOR_APIFY = keys['actor_apify']
    FOLDER_ID_DRIVE = keys['folder_id']
    name_user = "GermainSports"
    path_dict = ParseData_Mejorado(data=data, dir_data=dir_data, name_user=name_user)
    link_folder = SubirCSVs(dir_folder_credentials=dir_data, master_drive_key=FOLDER_ID_DRIVE, owner_data=name_user, path_dict=path_dict)
    print(link_folder)
# if __name__ == "__main__":
#     test_subir_datos()