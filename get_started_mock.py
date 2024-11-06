import streamlit as st
import time

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1

# Step 1: Questions
if st.session_state.step == 1:
    st.title("Consultor de Búsqueda de Redes Sociales")
    
    empresa = st.text_input("¿Cuál es el nombre de tu empresa o sector?", "")
    objetivo = st.text_input("¿Cuál es tu objetivo principal para esta búsqueda?", "")
    
    if st.button("Siguiente"):
        if empresa and objetivo:
            st.session_state.step = 2
        else:
            st.warning("Por favor completa ambos campos.")

# Step 2: Loading Page
if st.session_state.step == 2:
    st.title("Procesando...")
    with st.spinner("Generando sugerencias de búsqueda..."):
        time.sleep(2)  # Simulate processing time
    st.session_state.step = 3

# Step 3: Show Query Suggestions
if st.session_state.step == 3:
    st.title("Sugerencias de Búsqueda")

    st.write("Basado en tu información, aquí tienes algunas sugerencias de búsqueda en TikTok e Instagram:")
    st.write(f"- {empresa} en {objetivo}")
    st.write(f"- Tendencias de {empresa}")
    st.write(f"- Consejos sobre {objetivo} para {empresa}")
    st.write(f"- Ejemplos de {objetivo} exitosos en {empresa}")

    if st.button("Proceder con el scraping"):
        st.session_state.step = 4

# Step 4: Simulated Scraping with Loading Bar
if st.session_state.step == 4:
    st.title("Scraping en Proceso...")
    with st.spinner("Extrayendo datos de redes sociales..."):
        for i in range(101):
            time.sleep(0.05)
            st.progress(i)
    
    st.success("Scraping completado con éxito!")
