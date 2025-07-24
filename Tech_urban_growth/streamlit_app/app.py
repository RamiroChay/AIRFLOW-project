from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import streamlit as st
import plotly.express as px

# ------------------ CONEXIÓN MONGO ------------------

def get_mongo_client(uri="mongodb://host.docker.internal:27017/"):
    """Conexión a MongoDB usando host.docker.internal para entorno Docker."""
    return MongoClient(uri)

def load_collection(db, collection_name):
    """Carga los datos de una colección específica como DataFrame."""
    data = list(db[collection_name].find())
    if not data:
        print(f"No hay datos en la colección '{collection_name}'.")
        return pd.DataFrame()
    df = pd.DataFrame(data)

    # Eliminar columnas no necesarias si existen
    for col in ["_id", "location", "timestamp", "extracted_at", "transformed_at"]:
        if col in df.columns:
            df = df.drop(columns=[col])
    return df

def normalize_date(df):
    if "date" in df.columns:
        # Convertir a numérico, convirtiendo errores a NaN
        df["date"] = pd.to_numeric(df["date"], errors="coerce")
        
        # Reemplazar valores NaN o infinitos con el año actual
        df["date"] = df["date"].replace([float("inf"), float("-inf")], pd.NA)
        df["date"] = df["date"].fillna(datetime.utcnow().year)

        # Asegurar que los valores sean enteros válidos
        df["date"] = df["date"].astype(int)
    return df


# ------------------ INICIO APP ------------------

st.set_page_config(layout="wide", page_title="Drought & Agronomic Dashboard")
st.title("🌎 Análisis Global: Clima, Agricultura y Contaminación")

# ------------------ CONEXIÓN ------------------

client = get_mongo_client()
db = client["global_data"]

# Carga de datos
weather_df = load_collection(db, "weather_data")
carbon_df = load_collection(db, "carbon_intensity_data")
agro_df = load_collection(db, "agronomic_data")
air_df = load_collection(db, "air_quality_data")

# Normalización de fechas si aplica
agro_df = normalize_date(agro_df)
carbon_df = normalize_date(carbon_df)
weather_df = normalize_date(weather_df)
air_df = normalize_date(air_df)

# ------------------ INTERFAZ ------------------

tab1, tab2, tab3, tab4 = st.tabs(["🌾 Agronomía", "☁️ Contaminación", "🌡️ Clima", "⚡ Carbono"])

# AGRONOMÍA
with tab1:
    st.subheader("Producción Agronómica por País")
    if not agro_df.empty:
        fig = px.bar(agro_df, x="country", y="production", color="production", title="Producción Agronómica")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos de producción agronómica disponibles.")

# CALIDAD DEL AIRE
with tab2:
    st.subheader("Calidad del Aire por País")
    if not air_df.empty:
        air_avg = air_df.groupby("country")[["aqi", "pm2_5", "pm10", "co", "no2"]].mean().reset_index()
        fig = px.bar(air_avg, x="country", y="aqi", color="aqi", title="Promedio de Índice de Calidad del Aire (AQI)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos de calidad del aire disponibles.")

# CLIMA
with tab3:
    st.subheader("Temperaturas y Precipitaciones por País")
    if not weather_df.empty:
        weather_avg = weather_df.groupby("country")[["temperature", "precipitation"]].mean().reset_index()
        col1, col2 = st.columns(2)
        with col1:
            fig_temp = px.bar(weather_avg, x="country", y="temperature", color="temperature", title="Temperatura Promedio")
            st.plotly_chart(fig_temp, use_container_width=True)
        with col2:
            fig_prec = px.bar(weather_avg, x="country", y="precipitation", color="precipitation", title="Precipitación Promedio")
            st.plotly_chart(fig_prec, use_container_width=True)
    else:
        st.warning("No hay datos climáticos disponibles.")

# INTENSIDAD DE CARBONO
with tab4:
    st.subheader("Intensidad de Carbono por País")
    if not carbon_df.empty:
        fig = px.bar(carbon_df, x="country", y="carbon_intensity", color="carbon_intensity", title="Intensidad de Carbono")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos de intensidad de carbono disponibles.")
