import logging
from datetime import datetime
from utils.transformation_helpers import country_codes

def transform_population_data(ti):
    raw_data = ti.xcom_pull(key="population_raw_data", task_ids="ingestion_population_data")

    if not raw_data or (isinstance(raw_data, dict) and "error" in raw_data):
        logging.error("❌ No se pudo transformar datos de población: no hay datos o contienen error.")
        ti.xcom_push(key="clean_population_data", value=[])
        return

    logging.info(f"DEBUG: raw_data tipo={type(raw_data)} cantidad={len(raw_data)}")

    allowed_countries = set(country_codes)  # Ya es lista con códigos ISO3

    cleaned_data = []
    for entry in raw_data:
        # Usa el código ISO3 correcto para filtrar
        iso3 = entry.get("countryiso3code") or entry.get("country_code")

        # Nombre del país
        country_name = entry.get("country", {}).get("value")

        year = entry.get("date")
        population_value = entry.get("value")

        if iso3 not in allowed_countries:
            logging.info(f"  -> país {iso3} no permitido")
            continue
        if population_value is None:
            logging.info(f"  -> valor población None")
            continue

        cleaned_entry = {
            "country": country_name,
            "country_code": iso3,
            "date": int(year) if year and year.isdigit() else None,
            "population": population_value,
            "transformed_at": datetime.utcnow().isoformat()
        }
        cleaned_data.append(cleaned_entry)

    logging.info(f"✔ {len(cleaned_data)} registros de población transformados correctamente")
    ti.xcom_push(key="clean_population_data", value=cleaned_data)
