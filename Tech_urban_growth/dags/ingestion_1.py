import requests
import logging
from datetime import datetime
from utils.mongo_helpers import get_mongo_client
from utils.api_helpers import capital_coords

def ingestion_air_quality_data(ti):
    client = get_mongo_client()
    db = client["air_quality_db"]
    raw_collection = db["raw_air_quality"]

    results = []

    for country_code, info in capital_coords.items():
        lat = info["lat"]
        lon = info["lon"]
        city = info["city"]

        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=1955d1ecdeb52a121a3892c12a4ab841"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            data["location"] = {
                "country": country_code,
                "city": city,
                "lat": lat,
                "lon": lon
            }
            data["extracted_at"] = datetime.utcnow().isoformat()

            # Guarda en MongoDB
            raw_collection.insert_one(data)

            # ⚠️ Copia segura para el XCom sin el _id de MongoDB
            data_copy = data.copy()
            data_copy.pop("_id", None)

            results.append(data_copy)

            logging.info(f"✔ Datos de calidad del aire obtenidos para {city}, {country_code}")

        except Exception as e:
            logging.error(f"❌ Error extrayendo calidad aire para {city}, {country_code}: {e}")

    # Solo datos JSON serializables en XCom
    ti.xcom_push(key="air_quality_raw_data", value=results)
