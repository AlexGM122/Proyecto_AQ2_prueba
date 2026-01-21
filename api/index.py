import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime, timezone

app = Flask(__name__)

# --- CONFIGURACIÓN DE MONGODB ---
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = 'temperatura_db'
COLLECTION_NAME = 'lecturas'

# Conexión Global
client = None
collection = None

try:
    if not MONGO_URI:
        print("ERROR: MONGO_URI no configurada en Vercel")
    else:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        client.admin.command('ping')
        print("Conexión a MongoDB exitosa")
except Exception as e:
    print(f"Error de conexión: {e}")

@app.route('/api/index', methods=['POST'])
def ingestar_temperatura():
    if collection is None:
        return jsonify({"error": "Base de datos no conectada"}), 500
    
    try:
        data = request.get_json()
        if not data or 'temperatura' not in data:
            return jsonify({"error": "Faltan datos"}), 400

        registro = {
            "temperatura": float(data.get('temperatura')),
            "timestamp": datetime.now(timezone.utc),
            "device_ip": request.headers.get('X-Forwarded-For', request.remote_addr)
        }

        collection.insert_one(registro)
        return jsonify({"mensaje": "OK", "status": "201"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Esta ruta es para que Vercel no de error al entrar con el navegador
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({"mensaje": "Servidor funcionando, usa POST en /api/index"}), 200
