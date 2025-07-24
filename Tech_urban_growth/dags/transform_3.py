import logging
from datetime import datetime
from utils.transformation_helpers import country_codes
def transform_population_data(ti):
    raw = ti.xcom_pull(key="population_raw_data", task_ids="ingestion_population_data")

    if not raw or not isinstance(raw, dict) or "data" not in raw:
        logging.warning("❌ No se recibió una estructura válida para población.")
        ti.xcom_push(key="clean_population_data", value=[])
        return

    observations = raw["data"]
    if len(observations) < 2:
        logging.warning("❌ No hay suficientes datos en la respuesta para población.")
        ti.xcom_push(key="clean_population_data", value=[])
        return

    cleaned = []
    for item in observations[1]:  # índice 1 contiene la lista de valores
        if not item or not isinstance(item, dict):
            continue

        country_info = item.get("country", {})
        country = country_info.get("value", "Unknown")

        entry = {
            "country": country,
            "date": item.get("date"),
            "value": item.get("value")
        }

        cleaned.append(entry)

    logging.info(f"✔ Población: {len(cleaned)} registros transformados.")
    ti.xcom_push(key="clean_population_data", value=cleaned)
