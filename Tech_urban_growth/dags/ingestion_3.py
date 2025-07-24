# ingestion_population.py
import requests
from datetime import datetime

def ingestion_population_data(ti):
    url = "https://api.worldbank.org/v2/country/LCN/indicator/SP.POP.TOTL?format=json&per_page=500"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        data_with_timestamp = {
            'data': data,
            'extracted_at': datetime.now().isoformat()
        }
        ti.xcom_push(key="population_raw_data", value=data_with_timestamp)
        print("✔ Datos población obtenidos correctamente")
    except requests.exceptions.RequestException as e:
        error_data = {"error": str(e), "timestamp": datetime.now().isoformat()}
        ti.xcom_push(key="population_raw_data", value=error_data)
        print(f"❌ Error población: {str(e)}")
