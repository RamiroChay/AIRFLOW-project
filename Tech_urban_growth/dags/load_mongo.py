# load_mongo.py
import logging
from pymongo import MongoClient
import os
from datetime import datetime

def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    return MongoClient(mongo_uri)

def load_all_to_mongo(ti):
    try:
        logging.info("📦 Conectando a MongoDB...")
        client = get_mongo_client()
        db = client["TechAndUrbanGrowthDB"]

        urb_data = ti.xcom_pull(key="urbanization_clean_data", task_ids="transform_urbanization_data")
        air_data = ti.xcom_pull(key="air_quality_transformed", task_ids="transform_air_quality_data")
        pop_data = ti.xcom_pull(key="clean_population_data", task_ids="transform_population_data")

        logging.info(f"Datos urbanización recibidos: tipo={type(urb_data)}, cantidad={len(urb_data) if urb_data else 0}")
        logging.info(f"Datos calidad aire recibidos: tipo={type(air_data)}, cantidad={len(air_data) if air_data else 0}")
        logging.info(f"Datos población recibidos: tipo={type(pop_data)}, cantidad={len(pop_data) if pop_data else 0}")

        total_upserted = 0

        urb_count = 0
        if isinstance(urb_data, list) and urb_data:
            for record in urb_data:
                try:
                    db.urbanization.update_one(
                        {"country": record["country"], "year": record["year"]},
                        {"$set": record},
                        upsert=True
                    )
                    urb_count += 1
                except Exception as e:
                    logging.error(f"Error cargando registro urbanización {record}: {e}")
        else:
            logging.warning("⚠️ No hay datos de urbanización para cargar")
        ti.xcom_push(key="urbanization_loaded", value=urb_count)
        total_upserted += urb_count

        air_count = 0
        if isinstance(air_data, dict):
            db.air_quality.update_one(
                {"location": air_data.get("location", "default")},
                {"$set": air_data},
                upsert=True
            )
            air_count = 1
        elif isinstance(air_data, list) and air_data:
            for record in air_data:
                try:
                    db.air_quality.update_one(
                        {"location": record.get("location", "default"), "timestamp": record.get("timestamp")},
                        {"$set": record},
                        upsert=True
                    )
                    air_count += 1
                except Exception as e:
                    logging.error(f"Error cargando registro calidad aire {record}: {e}")
        else:
            logging.warning("⚠️ No hay datos de calidad del aire para cargar")
        ti.xcom_push(key="air_quality_loaded", value=air_count)
        total_upserted += air_count
        logging.info(f"💨 Calidad del aire: {air_count} registros upsertados")

        pop_count = 0
        if isinstance(pop_data, list) and pop_data:
            for record in pop_data:
                try:
                    # Normalizar el campo para que el filtro funcione igual que en urbanization
                    record["year"] = record.pop("date")
                    db.population.update_one(
                        {"country": record["country"], "year": record["year"]},  # Usa "year" ahora
                        {"$set": record},
                        upsert=True
                    )
                    pop_count += 1
                except KeyError as e:
                    logging.error(f"Error cargando registro población {record}: {e}")


        else:
            logging.warning("⚠️ No hay datos de población para cargar")
        ti.xcom_push(key="population_loaded", value=pop_count)
        total_upserted += pop_count

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "sources": ["population", "urbanization", "air_quality"],
            "summary": {
                "population": pop_count,
                "urbanization": urb_count,
                "air_quality": air_count,
                "total_upserted": total_upserted
            }
        }
        db.consolidated_summary.insert_one(summary)
        logging.info(f"📝 Resumen consolidado insertado: {summary}")

        ti.xcom_push(key="total_loaded", value=total_upserted)
        ti.xcom_push(key="load_status", value="completed")
        client.close()
        logging.info(f"✅ Carga finalizada con éxito: {total_upserted} registros upsertados")

        if total_upserted == 0:
            raise ValueError("❌ No se insertaron datos en MongoDB")

    except Exception as e:
        logging.error(f"❌ Error al cargar datos a MongoDB: {e}")
        ti.xcom_push(key="load_status", value=f"failed: {str(e)}")
        raise

def save_last_success_time():
    """
    Guarda la última vez que se ejecutó exitosamente el DAG en un archivo o en MongoDB.
    """
    client = get_mongo_client()
    db = client["TechAndUrbanGrowthDB"]
    db.execution_log.insert_one({
        "event": "last_success",
        "timestamp": datetime.utcnow().isoformat()
    })
    logging.info("🕒 Última ejecución exitosa registrada")