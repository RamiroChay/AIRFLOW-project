import os
from pymongo import MongoClient

def get_mongo_client():
    # Valor por defecto cambia a host.docker.internal para Docker Desktop Windows/Mac
    mongo_uri = os.getenv("MONGO_URI", "mongodb://host.docker.internal:27017/")
    return MongoClient(mongo_uri)
