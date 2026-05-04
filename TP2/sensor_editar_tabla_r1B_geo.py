# sensor_editar_tabla_r1B_geo.py

import os
import random
import sqlite3
import requests
import geocoder
import time

from datetime import datetime
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)

DB_NAME = "db.datos_sensores"

# Usar variable de entorno:
# export OPENWEATHER_API_KEY="TU_API_KEY"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()



# BASE DE DATOS


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lectura_sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            co2 REAL,
            temp REAL,
            hum REAL,
            fecha TEXT,
            lugar TEXT,
            altura REAL,
            presion REAL,
            presion_nm REAL,
            temp_ext REAL,
            humedad_ext REAL,
            descripcion_clima TEXT
        )
    """)

    conn.commit()
    conn.close()


def obtener_registros():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id,
            co2,
            temp,
            hum,
            fecha,
            lugar,
            altura,
            presion,
            presion_nm,
            temp_ext,
            humedad_ext,
            descripcion_clima
        FROM lectura_sensores
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    datos = []

    for r in rows:
        datos.append({
            "id": r[0],
            "co2": r[1],
            "temp": r[2],
            "hum": r[3],
            "fecha": r[4],
            "lugar": r[5],
            "altura": r[6],
            "presion": r[7],
            "presion_nm": r[8],
            "temp_ext": r[9],
            "humedad_ext": r[10],
            "descripcion_clima": r[11]
        })

    return datos



# GEOLOCALIZACION + CLIMA


def clima_simulado(ciudad="Buenos Aires"):
    return {
        "lat": -34.61,
        "lon": -58.38,
        "temp_ext": round(random.uniform(15, 29), 2),
        "presion": round(random.uniform(1002, 1022), 2),
        "humedad_ext": round(random.uniform(45, 85), 2),
        "descripcion_clima": f"simulado sin API key ({ciudad or 'ubicacion local'})",
        "fuente": "simulada"
    }


def validar_api_key():
    if not OPENWEATHER_API_KEY:
        raise RuntimeError(
            "Falta configurar OPENWEATHER_API_KEY. "
            "Mientras tanto se puede usar modo=simulado."
        )


def geo_latlon():
    validar_api_key()

    g = geocoder.ip("me")

    if not g.latlng:
        raise Exception("No se pudo obtener la ubicación por IP")

    lat, lon = g.latlng

    url = (
        "https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}"
        f"&appid={OPENWEATHER_API_KEY}"
        "&units=metric"
        "&lang=es"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    if str(data.get("cod")) not in ["200"]:
        raise Exception(f"Error OpenWeatherMap: {data}")

    main = data["main"]
    weather = data["weather"][0]

    temp_ext = main["temp"]
    presion = main["pressure"]
    humedad_ext = main["humidity"]
    descripcion_clima = weather["description"]

    return {
        "lat": lat,
        "lon": lon,
        "temp_ext": temp_ext,
        "presion": presion,
        "humedad_ext": humedad_ext,
        "descripcion_clima": descripcion_clima,
        "fuente": "openweathermap"
    }


def clima_por_ciudad(ciudad):
    validar_api_key()

    url = (
        "https://api.openweathermap.org/data/2.5/weather?"
        f"q={ciudad}"
        f"&appid={OPENWEATHER_API_KEY}"
        "&units=metric"
        "&lang=es"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    if str(data.get("cod")) not in ["200"]:
        raise Exception(f"Ciudad no encontrada o error OpenWeatherMap: {data}")

    main = data["main"]
    weather = data["weather"][0]

    return {
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
        "temp_ext": main["temp"],
        "presion": main["pressure"],
        "humedad_ext": main["humidity"],
        "descripcion_clima": weather["description"],
        "fuente": "openweathermap"
    }


def obtener_clima(ciudad="", modo="auto"):
    if modo == "simulado":
        return clima_simulado(ciudad)

    try:
        if ciudad:
            return clima_por_ciudad(ciudad)
        return geo_latlon()
    except Exception as exc:
        clima = clima_simulado(ciudad)
        clima["advertencia"] = str(exc)
        return clima



# SIMULACION DE SENSOR


def simular_lectura(lugar, altura, clima):
    temp_ext = float(clima["temp_ext"])
    presion = float(clima["presion"])

    co2_medido = random.uniform(250, 1100)
    temp_sensor = random.uniform(temp_ext, temp_ext + 10)
    humedad_relativa = random.uniform(40, 80)

    fecha = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")

    lectura = {
        "co2": round(co2_medido, 2),
        "temp": round(temp_sensor, 2),
        "hum": round(humedad_relativa, 2),
        "fecha": fecha,
        "lugar": lugar,
        "altura": altura,
        "presion": presion,
        "presion_nm": presion,
        "temp_ext": clima["temp_ext"],
        "humedad_ext": clima["humedad_ext"],
        "descripcion_clima": clima["descripcion_clima"]
    }

    return lectura


def insertar_lectura(lectura):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lectura_sensores (
            co2,
            temp,
            hum,
            fecha,
            lugar,
            altura,
            presion,
            presion_nm,
            temp_ext,
            humedad_ext,
            descripcion_clima
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lectura["co2"],
        lectura["temp"],
        lectura["hum"],
        lectura["fecha"],
        lectura["lugar"],
        lectura["altura"],
        lectura["presion"],
        lectura["presion_nm"],
        lectura["temp_ext"],
        lectura["humedad_ext"],
        lectura["descripcion_clima"]
    ))

    conn.commit()
    lectura["id"] = cursor.lastrowid
    conn.close()

    return lectura



# RUTAS WEB


@app.route("/")
def index():
    return render_template("tabla_sensores_geo.html")


@app.route("/api/datos")
def api_datos():
    return jsonify({
        "data": obtener_registros()
    })


@app.route("/api/clima")
def api_clima():
    ciudad = request.args.get("ciudad")
    modo = request.args.get("modo", "auto")

    clima = obtener_clima(ciudad or "", modo)

    return jsonify(clima)


@app.route("/api/capturar", methods=["POST"])
def api_capturar():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Debe enviar JSON"}), 400

    lugar = data.get("lugar", "Sin definir")
    altura = float(data.get("altura", 0))
    ciudad = data.get("ciudad", "").strip()
    modo = data.get("modo", "auto")
    cantidad = max(1, int(data.get("cantidad", 1)))
    intervalo = max(0.0, float(data.get("intervalo", 0)))

    try:
        lecturas = []

        for i in range(cantidad):
            clima = obtener_clima(ciudad, modo)
            lectura = simular_lectura(lugar, altura, clima)
            lectura = insertar_lectura(lectura)
            lecturas.append(lectura)

            if i < cantidad - 1 and intervalo > 0:
                time.sleep(intervalo)

        return jsonify({
            "mensaje": "Lecturas capturadas correctamente",
            "cantidad": len(lecturas),
            "lecturas": lecturas
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/api/data/<int:id>", methods=["DELETE"])
def borrar(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM lectura_sensores WHERE id = ?", (id,))
    conn.commit()

    borrados = cursor.rowcount
    conn.close()

    if borrados == 0:
        return jsonify({"error": "Registro no encontrado"}), 404

    return jsonify({
        "mensaje": "Registro eliminado",
        "id": id
    })



# MAIN


if __name__ == "__main__":
    create_table()
    app.run(host="0.0.0.0", port=5012, debug=True)
