import requests
import logging
from datetime import datetime
from utils.mongo_helpers import get_mongo_client
from utils.transformation_helpers import country_codes

def ingestion_population_data(ti):
    client = get_mongo_client()
    db = client["population_db"]
    raw_collection = db["raw_population"]

    all_observations = []
    errors = []

    for code in country_codes:
        url = f"https://api.worldbank.org/v2/country/{code}/indicator/SP.POP.TOTL?format=json&per_page=500"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            raw_collection.insert_one({
                "country_code": code,
                "data": data,
                "extracted_at": datetime.utcnow().isoformat()
            })

            if len(data) > 1:
                observations = data[1]
                for obs in observations:
                    obs["country_code"] = code
                    all_observations.append(obs)

            logging.info(f"✔ Datos población obtenidos para {code}, registros: {len(data[1]) if len(data)>1 else 0}")

        except Exception as e:
            logging.error(f"❌ Error al obtener datos población para {code}: {e}")
            errors.append({"country_code": code, "error": str(e)})

    ti.xcom_push(key="population_raw_data", value=all_observations)
    logging.info(f"✔ Total registros población obtenidos: {len(all_observations)}")
    if errors:
        logging.warning(f"⚠️ Errores en países: {errors}")