import streamlit as st
import pandas as pd
from pymongo import MongoClient
import altair as alt

# --- Page config ---
st.set_page_config(
    page_title="🌍 Dashboard Urbanización y Calidad Ambiental",
    page_icon="🌿",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
h1, h2, h3 {
    text-align: center;
}
.sidebar .sidebar-content {
    background-color: #1f2937;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- MongoDB connection (ajusta host si usas Docker o local) ---
@st.cache_resource
def get_mongo_client():
    return MongoClient("mongodb://mongodb:27017")  # Cambia "mongodb" si necesitas "localhost"

client = get_mongo_client()
db = client["TechAndUrbanGrowthDB"]

# --- Carga datos desde Mongo ---
def load_collection(collection_name):
    data = list(db[collection_name].find())
    if not data:
        st.warning(f"No hay datos en la colección '{collection_name}'.")
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # Limpiar columnas innecesarias
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    return df

urban_df = load_collection("urbanization")
pop_df = load_collection("population")
air_df = load_collection("air_quality")

# Normalizar fechas para filtro común
def normalize_date(df):
    if "date" not in df.columns and "year" in df.columns:
        df = df.rename(columns={"year": "date"})
    if "date" in df.columns:
        df["date"] = df["date"].astype(int)
    return df

urban_df = normalize_date(urban_df)
pop_df = normalize_date(pop_df)
air_df = normalize_date(air_df)

# --- Obtener años disponibles validando existencia de columna ---
years_set = set()
for df in [urban_df, pop_df, air_df]:
    if not df.empty and "date" in df.columns:
        years_set.update(df["date"].dropna().astype(int).unique().tolist())
years = sorted(years_set)

if not years:
    st.error("No hay datos disponibles para mostrar.")
    st.stop()

selected_year = st.sidebar.selectbox("Selecciona un año", years, index=len(years) - 1)

# --- Obtener países para el año filtrado ---
def get_countries_for_year(df, year):
    if df.empty or "country" not in df.columns or "date" not in df.columns:
        return []
    return df[df["date"] == year]["country"].dropna().unique().tolist()

countries = sorted(set(
    get_countries_for_year(urban_df, selected_year) +
    get_countries_for_year(pop_df, selected_year) +
    get_countries_for_year(air_df, selected_year)
))

selected_countries = st.sidebar.multiselect("Selecciona países", countries, default=countries)

# --- Tabs para datasets ---
tab1, tab2, tab3 = st.tabs(["Urbanización", "Población", "Calidad del Aire"])

def plot_metric_bar(df, x_col, y_col, title, y_label, color="#2b8cbe"):
    chart = alt.Chart(df).mark_bar(color=color).encode(
        x=alt.X(x_col, sort='-y', title="País"),
        y=alt.Y(y_col, title=y_label),
        tooltip=[x_col, y_col]
    ).properties(width=800, height=400, title=title)
    st.altair_chart(chart, use_container_width=True)

with tab1:
    st.header(f"📊 Urbanización en {selected_year}")
    df = urban_df[(urban_df["date"] == selected_year) & (urban_df["country"].isin(selected_countries))]
    if df.empty:
        st.info("No hay datos de urbanización para los filtros seleccionados.")
    else:
        st.metric("Número de países", len(df))
        y_col = "population" if "population" in df.columns else "value"
        plot_metric_bar(df, "country", y_col, "Porcentaje de población urbana (%)", "% Población Urbana")

        max_urban = df.loc[df[y_col].idxmax()]
        st.write(f"✅ País con mayor urbanización en {selected_year}: **{max_urban['country']}** con {max_urban[y_col]:.2f}% población urbana.")

with tab2:
    st.header(f"👥 Población total en {selected_year}")
    df = pop_df[(pop_df["date"] == selected_year) & (pop_df["country"].isin(selected_countries))]
    if df.empty:
        st.info("No hay datos de población para los filtros seleccionados.")
    else:
        st.metric("Número de países", len(df))
        y_col = "population" if "population" in df.columns else "value"
        plot_metric_bar(df, "country", y_col, "Población Total", "Población")

        max_pop = df.loc[df[y_col].idxmax()]
        st.write(f"✅ País más poblado en {selected_year}: **{max_pop['country']}** con {max_pop[y_col]:,.0f} habitantes.")

with tab3:
    st.header(f"🌬️ Calidad del aire en {selected_year}")
    df = air_df[(air_df["date"] == selected_year) & (air_df["country"].isin(selected_countries))]
    if df.empty:
        st.info("No hay datos de calidad del aire para los filtros seleccionados.")
    else:
        st.metric("Número de países", len(df))
        for col_candidate in ["aqi", "value", "pm2_5"]:
            if col_candidate in df.columns:
                y_col = col_candidate
                break
        else:
            y_col = None

        if y_col:
            plot_metric_bar(df, "country", y_col, f"Índice Calidad de Aire ({y_col.upper()})", y_col.upper(), color="#e07b39")

            worst_air = df.loc[df[y_col].idxmax()]
            st.write(f"⚠️ País con peor calidad del aire en {selected_year}: **{worst_air['country']}** con índice {worst_air[y_col]:.2f}.")
        else:
            st.info("No se encontró indicador de calidad del aire válido.")

# --- Insights comparativos básicos ---
st.markdown("---")
st.header("📈 Insights comparativos")

if not urban_df.empty and not pop_df.empty:
    merged = pd.merge(
        urban_df[(urban_df["date"] == selected_year) & (urban_df["country"].isin(selected_countries))][["country", "population"]],
        pop_df[(pop_df["date"] == selected_year) & (pop_df["country"].isin(selected_countries))][["country", "population"]],
        on="country",
        suffixes=("_urban", "_pop")
    )
    if not merged.empty:
        corr = merged["population_urban"].corr(merged["population_pop"])
        st.write(f"🔍 Correlación entre % urbanización y población total para {selected_year}: **{corr:.2f}** (valores cercanos a 1 indican alta correlación).")

if not air_df.empty and not pop_df.empty and y_col:
    merged_air_pop = pd.merge(
        air_df[(air_df["date"] == selected_year) & (air_df["country"].isin(selected_countries))][["country", y_col]],
        pop_df[(pop_df["date"] == selected_year) & (pop_df["country"].isin(selected_countries))][["country", "population"]],
        on="country"
    )
    if not merged_air_pop.empty:
        st.write("🔎 Relación calidad aire vs población (scatter plot):")
        scatter = alt.Chart(merged_air_pop).mark_circle(size=100).encode(
            x=alt.X("population", title="Población"),
            y=alt.Y(y_col, title=f"Calidad de aire ({y_col.upper()})"),
            tooltip=["country", "population", y_col],
            color=alt.value("#e07b39")
        ).properties(width=800, height=400)
        st.altair_chart(scatter, use_container_width=True)
else:
    st.info("No hay datos suficientes para insights comparativos.")

