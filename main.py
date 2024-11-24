from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from .ScrapperInterfaz import Interfaz
app = FastAPI()

class UserQuery(BaseModel):
    message_user: str
    name_user: str
    dir_data: str = './'  # Valor predeterminado
    resultados_por_pagina: int = 100  # Valor predeterminado
    perfiles_maximos_por_busqueda: int = 10  # Valor predeterminado


@app.post("/")
def create_item():
    return {"output": "Bienvenido a TrendSage Scrapper:)"}

@app.post("/make_scrapping/")
def create_item(query_dict: UserQuery):
    try:
        input_scrapper = {
            "dir_data": query_dict.dir_data,
            "resultados_por_pagina": query_dict.resultados_por_pagina,
            "perfiles_maximos_por_busqueda": query_dict.perfiles_maximos_por_busqueda,
            "name_user": query_dict.name_user,
            "message_user": query_dict.message_user
        }
        if not query_dict.message_user.strip():
            raise HTTPException(status_code=400, detail="Alerta: no existe una query válida")
        if not query_dict.name_user.strip():
            raise HTTPException(status_code=400, detail="Alerta: no existe un usuario válido")
        
        link = Interfaz(input_scrapper)

        return {
            "output": "Scraping completado. Revisa en el directorio especificado.",
            "details": link
        }
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")