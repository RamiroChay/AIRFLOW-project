from pymongo import MongoClient
import pandas as pd
from datetime import datetime  # ← corrección aquí

def get_mongo_client(uri="mongodb://host.docker.internal:27017/"):
    """Conexión a MongoDB usando localhost por defecto."""
    return MongoClient(uri)

def load_collection(db, collection_name):
    data = list(db[collection_name].find())
    if not data:
        print(f"No hay datos en la colección '{collection_name}'.")
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # Eliminar columnas no necesarias si existen
    for col in ["_id", "location", "timestamp", "extracted_at", "transformed_at"]:
        if col in df.columns:
            df = df.drop(columns=[col])
    return df

import numpy as np

def normalize_date(df):
    df["date"] = pd.to_numeric(df["date"], errors="coerce")       # errores a NaN
    df["date"].replace([np.inf, -np.inf], np.nan, inplace=True)   # infinitos a NaN
    df = df.dropna(subset=["date"]).copy()                        # eliminar filas con NaN en 'date'
    df["date"] = df["date"].astype(int)                           # convertir a entero
    return df







