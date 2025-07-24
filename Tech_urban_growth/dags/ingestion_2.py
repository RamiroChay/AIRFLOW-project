import requests
import logging
from datetime import datetime
from utils.mongo_helpers import get_mongo_client

def ingestion_urbanization_data(ti):
    url = "https://api.worldbank.org/v2/country/LCN/indicator/SP.URB.TOTL.IN.ZS?format=json&per_page=500"

    client = get_mongo_client()
    db = client["urbanization_db"]
    raw_collection = db["raw_urbanization"]

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Guarda todo el resultado en Mongo
        result = {
            "data": data,
            "extracted_at": datetime.utcnow().isoformat()
        }
        raw_collection.insert_one(result)

        # Extrae solo la lista de observaciones (índice 1 del JSON)
        observations = data[1] if len(data) > 1 else []

        # Pushea solo esa lista (serializable)
        ti.xcom_push(key="urbanization_raw_data", value=observations)

        logging.info("✔ Datos de urbanización obtenidos y almacenados")

    except Exception as e:
        error_data = {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
        ti.xcom_push(key="urbanization_raw_data", value=error_data)
        logging.error(f"❌ Error en urbanización: {e}")
