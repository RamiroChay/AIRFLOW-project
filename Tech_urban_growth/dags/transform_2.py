import logging
from datetime import datetime
from utils.transformation_helpers import country_codes

import logging
from datetime import datetime

def transform_urbanization_data(ti):
    raw_data = ti.xcom_pull(key="urbanization_raw_data", task_ids="ingestion_urbanization_data")

    if not raw_data or isinstance(raw_data, dict) and "error" in raw_data:
        logging.error("❌ No se pudo transformar datos de urbanización: no hay datos o contienen error.")
        return

    cleaned_data = []

    for entry in raw_data:
        country = entry.get("country", {}).get("value")
        country_code = entry.get("country", {}).get("id")
        year = entry.get("date")
        urban_percent = entry.get("value")

        # Evaluación de calidad
        quality = "buena" if urban_percent is not None else "mala"

        cleaned_entry = {
            "country": country,
            "country_code": country_code,
            "year": int(year),
            "urban_population_percent": urban_percent,
            "quality": quality,
            "transformed_at": datetime.utcnow().isoformat()
        }

        cleaned_data.append(cleaned_entry)

    ti.xcom_push(key="urbanization_clean_data", value=cleaned_data)
    logging.info(f"✔ {len(cleaned_data)} registros de urbanización transformados correctamente")
