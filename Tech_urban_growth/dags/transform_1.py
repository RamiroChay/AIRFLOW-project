import logging
from datetime import datetime

def transform_air_quality_data(ti):
    raw_list = ti.xcom_pull(key="air_quality_raw_data", task_ids="ingestion_air_quality_data")
    
    if not raw_list or not isinstance(raw_list, list):
        ti.xcom_push(key="air_quality_transformed", value=[])
        logging.error("❌ No hay datos de calidad del aire para transformar o formato incorrecto")
        return

    def classify_aqi(aqi):
        if aqi == 1:
            return "good"
        elif aqi == 2:
            return "moderate"
        elif aqi == 3:
            return "unhealthy"
        elif aqi == 4:
            return "very_unhealthy"
        elif aqi == 5:
            return "hazardous"
        else:
            return "unknown"

    transformed_list = []

    for idx, raw in enumerate(raw_list):
        if "error" in raw:
            logging.warning(f"⚠️ Dato con error en posición {idx}, se omite")
            continue
        try:
            entry = raw.get("list", [])[0]
            components = entry.get("components", {})
            main_data = entry.get("main", {})

            aqi = main_data.get("aqi", 0)
            quality_status = classify_aqi(aqi)

            transformed = {
                "timestamp": datetime.utcnow().isoformat(),
                "extracted_at": raw.get("extracted_at"),
                "location": raw.get("location", {}),
                "aqi": aqi,
                "quality_status": quality_status,
                "co": components.get("co", 0),
                "no": components.get("no", 0),
                "no2": components.get("no2", 0),
                "o3": components.get("o3", 0),
                "so2": components.get("so2", 0),
                "pm2_5": components.get("pm2_5", 0),
                "pm10": components.get("pm10", 0),
                "nh3": components.get("nh3", 0),
                "is_unhealthy": aqi > 3
            }

            transformed_list.append(transformed)
            logging.info(f"✔ Transformado dato calidad aire {idx} para {transformed['location'].get('city', 'desconocido')}")

        except (IndexError, KeyError, TypeError) as e:
            logging.error(f"❌ Error transformando dato en posición {idx}: {str(e)}")
            continue

    ti.xcom_push(key="air_quality_transformed", value=transformed_list)
