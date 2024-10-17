# MOCK UP PROTOTIPO DE DASHBOARD, CONECTAR CON GENERACION DE INSIGHTS DE MAFER Y MODULO STORY TELLING

import streamlit as st
import pandas as pd
import plotly.express as px
import re
from collections import Counter

st.set_page_config(page_title="Dashboard de Marketing para Pastelería", layout="wide", page_icon="🍰")

color_palette = {
    'primary': '#6D9DC5',
    'secondary': '#D3E4CD',
    'accent': '#F4A261',
    'background': '#F0F0F0',
    'text': '#333333'
}

# Estilos CSS para personalizar la apariencia
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-color: {color_palette['background']};
    }}
    .sidebar .sidebar-content {{
        background-color: {color_palette['primary']} !important;
        color: white;
    }}
    .stMarkdown {{
        color: {color_palette['text']};
    }}
    .stButton>button {{
        background-color: {color_palette['accent']};
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Dashboard de Marketing para Pastelería Dulce Arte")

st.sidebar.header("Filtros de Datos")
fecha = st.sidebar.date_input("Selecciona el rango de fechas", [])
plataforma = st.sidebar.multiselect(
    "Selecciona la plataforma",
    options=["TikTok", "Instagram Reels"],
    default=["TikTok", "Instagram Reels"]
)
tipo_contenido = st.sidebar.multiselect(
    "Selecciona el tipo de contenido",
    options=["Tutoriales", "Reseñas", "Behind-the-Scenes", "Promociones"],
    default=["Tutoriales", "Reseñas", "Behind-the-Scenes", "Promociones"]
)

# Datos ficticios
data = {
    "Plataforma": ["TikTok"]*10 + ["Instagram Reels"]*10,
    "Tipo de Contenido": ["Tutoriales", "Reseñas", "Behind-the-Scenes", "Promociones", "Tutoriales",
                         "Reseñas", "Behind-the-Scenes", "Promociones", "Tutoriales", "Reseñas"]*2,
    "Vistas": [1500, 1200, 800, 2000, 1700, 1100, 900, 2100, 1600, 1300,
               1400, 1250, 850, 1900, 1650, 1150, 950, 2050, 1550, 1350],
    "Likes": [300, 250, 150, 400, 320, 260, 160, 420, 310, 270,
              290, 240, 140, 390, 310, 230, 170, 410, 300, 280],
    "Comentarios": [50, 40, 20, 60, 55, 45, 25, 65, 50, 42,
                    48, 38, 22, 58, 52, 44, 28, 62, 49, 43],
    "Hashtags": ["#chocolate #dulce #postres", "#vainilla #pastel #delicioso",
                "#frutas #sano #sabroso", "#promo #oferta #repostería",
                "#creativo #arte #repostero", "#receta #fácil #casero",
                "#detrás #cámaras #hechoamano", "#descuento #oferta #promoción",
                "#decoración #increíble #sabroso", "#innovador #tendencia #nuevo"]*2,
    "Sentimiento": ["Positivo", "Neutro", "Negativo", "Positivo", "Positivo",
                    "Neutro", "Negativo", "Positivo", "Positivo", "Neutro"]*2,
    "Comentarios_Texto": [
        "¡Deliciosos postres! Me encantó el chocolate.",
        "El pastel de vainilla estuvo bien, pero podría mejorar.",
        "Las frutas en el postre son muy frescas.",
        "¡Promoción increíble, aprovechar ahora!",
        "El arte en los postres es impresionante.",
        "Receta fácil y rápida, perfecta para casa.",
        "Detrás de cámaras muestra mucho esfuerzo.",
        "Descuento en promociones especiales.",
        "La decoración es simplemente sabrosa.",
        "Innovador y tendencia en nuevos sabores.",
        "Tutorial muy útil, gracias por compartir.",
        "Reseña honesta, me ayudó a decidir.",
        "Comentarios negativos sobre la textura.",
        "Gran promoción, muchas vistas.",
        "Las reseñas son muy positivas.",
        "Promociones que no se deben perder.",
        "Comentarios mixtos sobre el sabor.",
        "Excelente engagement en promociones.",
        "Comentarios neutrales sobre los nuevos sabores.",
        "Opiniones variadas sobre los productos."
    ]
}

df = pd.DataFrame(data)

if fecha:
    pass

df = df[df["Plataforma"].isin(plataforma)]
df = df[df["Tipo de Contenido"].isin(tipo_contenido)]

st.header("📈 Resumen Ejecutivo")

# Métricas clave
total_vistas = df["Vistas"].sum()
total_likes = df["Likes"].sum()
total_comentarios = df["Comentarios"].sum()
sentimiento_promedio = df["Sentimiento"].value_counts(normalize=True).mul(100).round(2)

col_a, col_b, col_c = st.columns(3)
col_a.metric("Total de Vistas", f"{total_vistas:,}")
col_b.metric("Total de Likes", f"{total_likes:,}")
col_c.metric("Total de Comentarios", f"{total_comentarios:,}")

# Gráfico de distribución de sentimientos
st.subheader("Distribución de Sentimientos")
sentiment_df = pd.DataFrame({
    "Sentimiento": sentimiento_promedio.index,
    "Porcentaje": sentimiento_promedio.values
})
fig_sentiment = px.pie(sentiment_df, values='Porcentaje', names='Sentimiento', 
                       title='Distribución de Sentimientos',
                       color='Sentimiento',
                       color_discrete_sequence=px.colors.sequential.Blues)
st.plotly_chart(fig_sentiment, use_container_width=True)

st.markdown("---")

st.header("👥 Influencers y Creadores de Contenido Clave")

# Datos ficticios de influencers
influencers = {
    "Nombre": ["@dulce_artist", "@pastel_master", "@sabor_exquisito", "@sweet_chef", "@postre_creativo"],
    "Seguidores": [50000, 75000, 30000, 60000, 45000],
    "Engagement": [0.05, 0.07, 0.04, 0.06, 0.05]
}
df_influencers = pd.DataFrame(influencers)

fig_influencers = px.bar(
    df_influencers, 
    x='Nombre', 
    y='Seguidores', 
    title='Top Influencers por Seguidores', 
    color='Engagement',
    labels={'Seguidores': 'Número de Seguidores', 'Engagement': 'Tasa de Engagement'},
    color_continuous_scale='Viridis'
)
st.plotly_chart(fig_influencers, use_container_width=True)

st.markdown("---")

st.header("🏷️ Análisis de Hashtags")

all_hashtags = ' '.join(df['Hashtags'])
hashtags_series = pd.Series(all_hashtags.split())
hashtag_counts = hashtags_series.value_counts().head(10).reset_index()
hashtag_counts.columns = ['Hashtag', 'Frecuencia']

fig_hashtags = px.bar(
    hashtag_counts, 
    x='Hashtag', 
    y='Frecuencia', 
    title='Top 10 Hashtags',
    color='Frecuencia', 
    color_continuous_scale='Plasma',
    labels={'Frecuencia': 'Frecuencia', 'Hashtag': 'Hashtags'}
)
st.plotly_chart(fig_hashtags, use_container_width=True)

st.markdown("---")

st.header("🔗 Correlación entre Hashtags y Vistas")

# Calcular la frecuencia de cada hashtag y su relación con las vistas
# Simulamos una correlación positiva multiplicando la frecuencia por un factor
hashtag_views = hashtag_counts.copy()
hashtag_views['Promedio Vistas'] = hashtag_views['Frecuencia'] * 100  # Mock correlation
hashtag_views['Engagement Total'] = [300, 420, 270, 500, 350, 400, 220, 450, 300, 380]  # Datos ficticios

fig_corr = px.scatter(
    hashtag_views, 
    x='Frecuencia', 
    y='Promedio Vistas', 
    size='Engagement Total', 
    color='Promedio Vistas',
    hover_name='Hashtag',
    title='Relación entre Frecuencia de Hashtags y Promedio de Vistas',
    labels={'Frecuencia': 'Frecuencia de Hashtag', 'Promedio Vistas': 'Promedio de Vistas'},
    size_max=60,
    color_continuous_scale='Teal'
)
fig_corr.update_layout(coloraxis_colorbar=dict(title="Promedio de Vistas"))
st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("---")

st.header("🗣️ Temas Emergentes en Comentarios")

# Simulamos temas emergentes basados en los comentarios ficticios
temas_emergentes = [
    {"Tema": "Mejoras en la Textura", "Comentarios Relacionados": 5},
    {"Tema": "Nuevas Combinaciones de Sabores", "Comentarios Relacionados": 4},
    {"Tema": "Promociones y Descuentos", "Comentarios Relacionados": 6},
    {"Tema": "Decoración y Presentación", "Comentarios Relacionados": 3},
    {"Tema": "Recetas y Tutoriales", "Comentarios Relacionados": 7}
]
df_temas = pd.DataFrame(temas_emergentes)

fig_temas = px.bar(
    df_temas, 
    x='Tema', 
    y='Comentarios Relacionados', 
    title='Temas Emergentes en Comentarios',
    color='Comentarios Relacionados', 
    color_continuous_scale='Sunset',
    labels={'Comentarios Relacionados': 'Número de Comentarios', 'Tema': 'Temas'},
    text='Comentarios Relacionados'
)
fig_temas.update_traces(textposition='outside')
fig_temas.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig_temas, use_container_width=True)

st.markdown("**Generado con AI**")

st.markdown("---")

st.header("✍️ Optimización de Títulos")
st.markdown("**Generado con AI**")

recomendaciones_titulos = [
    "Descubre el Nuevo Sabor de Chocolate Premium 🍫",
    "Tutorial: Cómo Decorar Postres como un Profesional",
    "Promoción Especial: 20% de Descuento en Todos los Pasteles 🎂",
    "Behind-the-Scenes: Creando el Pastel de Vainilla Perfecto",
    "Reseña: Nuestro Pastel de Frutas Favorito 🍓"
]

for i, recomendacion in enumerate(recomendaciones_titulos, 1):
    st.markdown(f"**{i}. {recomendacion}**")

st.markdown("---")

st.header("🛍️ Optimización de Nombres de Productos")
st.markdown("**Generado con AI**")

nombres_productos = {
    "Original": ["Pastel Clásico", "Tarta de Vainilla", "Cupcake de Fresas", "Brownie de Chocolate"],
    "Optimizado": ["Delicia Clásica de Chocolate", "Tarta Suprema de Vainilla", "Cupcake de Fresas Frescas", "Brownie Intenso de Chocolate"]
}

df_nombres = pd.DataFrame(nombres_productos)

st.table(df_nombres)

st.markdown("---")

# Sección de Resumen de Insights y Plan de Acción
st.header("📋 Resumen de Insights")
st.markdown("**Generado con AI**")
st.write("""
- **Tendencias de Sabores:** El chocolate y la vainilla son los sabores más populares entre la audiencia.
- **Engagement Alto en Tutoriales y Promociones:** Los contenidos de tutoriales y promociones generan mayor interacción.
- **Influencers Clave:** Colaborar con @pastel_master y @sweet_chef puede aumentar significativamente la visibilidad.
- **Correlación entre Hashtags y Vistas:** Hashtags más frecuentes están asociados con mayores vistas.
- **Temas Emergentes en Comentarios:** Los usuarios buscan mejoras en la textura y nuevas combinaciones de sabores.
""")

st.header("🚀 Plan de Acción a seguir")
st.markdown("**Generado con AI**")
st.write("""
1. **Introducir nuevos sabores de postres** basados en tendencias.
2. **Colaborar con los principales influencers** identificados.
3. **Optimizar el uso de hashtags** en las publicaciones.
4. **Crear más contenido de tutoriales y promociones**.
5. **Optimizar títulos y descripciones** para mejorar el engagement.
6. **Renombrar productos** para alinearlos con las preferencias emergentes.
""")

st.markdown("---")
st.markdown("© 2024 Pastelería Dulce Arte. Todos los derechos reservados.")
