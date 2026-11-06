
import os
import socket
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

APP_NOMBRE = os.getenv("APP_NOMBRE", "g1-cpus-api")
DB_PATH = os.getenv("DB_PATH", "/datos/inventario.db")

CPUS_INICIALES = [
    {
        "id": 1,
        "marca": "Intel",
        "modelo": "Core i5-12400",
        "caracteristicas": {
            "nucleos": 6,
            "hilos": 12,
            "frecuencia_maxima": "4.2 GHz"
        }
    },
    {
        "id": 2,
        "marca": "Intel",
        "modelo": "Core i7-13700K",
        "caracteristicas": {
            "nucleos": 16,
            "hilos": 24,
            "frecuencia_maxima": "5.4 GHz"
        }
    },
    {
        "id": 3,
        "marca": "AMD",
        "modelo": "Ryzen 5 5600X",
        "caracteristicas": {
            "nucleos": 6,
            "hilos": 12,
            "frecuencia_maxima": "4.6 GHz"
        }
    },
    {
        "id": 4,
        "marca": "AMD",
        "modelo": "Ryzen 7 7700X",
        "caracteristicas": {
            "nucleos": 8,
            "hilos": 16,
            "frecuencia_maxima": "5.4 GHz"
        }
    },
    {
        "id": 5,
        "marca": "Apple",
        "modelo": "M2",
        "caracteristicas": {
            "nucleos": 8,
            "hilos": "No especificado",
            "frecuencia_maxima": "No publicada"
        }
    }
]


def conectar_db():
    conexion = sqlite3.connect(DB_PATH, timeout=10)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

    with conectar_db() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS cpus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                nucleos INTEGER NOT NULL,
                hilos TEXT NOT NULL,
                frecuencia_maxima TEXT NOT NULL
            )
        """)

        cantidad = conexion.execute(
            "SELECT COUNT(*) FROM cpus"
        ).fetchone()[0]

        if cantidad == 0:
            for cpu in CPUS_INICIALES:
                caracteristicas = cpu["caracteristicas"]

                conexion.execute("""
                    INSERT INTO cpus (
                        id, marca, modelo, nucleos,
                        hilos, frecuencia_maxima
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    cpu["id"],
                    cpu["marca"],
                    cpu["modelo"],
                    caracteristicas["nucleos"],
                    str(caracteristicas["hilos"]),
                    caracteristicas["frecuencia_maxima"]
                ))

        conexion.commit()


def convertir_cpu(fila):
    hilos = fila["hilos"]

    if hilos.isdigit():
        hilos = int(hilos)

    return {
        "id": fila["id"],
        "marca": fila["marca"],
        "modelo": fila["modelo"],
        "caracteristicas": {
            "nucleos": fila["nucleos"],
            "hilos": hilos,
            "frecuencia_maxima": fila["frecuencia_maxima"]
        }
    }


@app.route("/api/estado", methods=["GET"])
def estado():
    return jsonify({
        "aplicacion": APP_NOMBRE,
        "hostname": socket.gethostname(),
        "hora": datetime.now().isoformat(),
        "estado": "activo"
    })


@app.route("/api/cpus", methods=["GET"])
def listar_cpus():
    with conectar_db() as conexion:
        filas = conexion.execute(
            "SELECT * FROM cpus ORDER BY id"
        ).fetchall()

    return jsonify([convertir_cpu(fila) for fila in filas])


@app.route("/api/cpus/<int:id>", methods=["GET"])
def obtener_cpu(id):
    with conectar_db() as conexion:
        fila = conexion.execute(
            "SELECT * FROM cpus WHERE id = ?",
            (id,)
        ).fetchone()

    if fila is None:
        return jsonify({"error": "Procesador no encontrado"}), 404

    return jsonify(convertir_cpu(fila))


@app.route("/api/cpus", methods=["POST"])
def registrar_cpu():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Se requiere un objeto JSON valido"
        }), 400

    marca = datos.get("marca")
    modelo = datos.get("modelo")
    caracteristicas = datos.get("caracteristicas")

    if not isinstance(marca, str) or not marca.strip():
        return jsonify({"error": "Marca requerida"}), 400

    if not isinstance(modelo, str) or not modelo.strip():
        return jsonify({"error": "Modelo requerido"}), 400

    if not isinstance(caracteristicas, dict):
        return jsonify({
            "error": "Caracteristicas requeridas"
        }), 400

    nucleos = caracteristicas.get("nucleos")
    hilos = caracteristicas.get("hilos")
    frecuencia = caracteristicas.get("frecuencia_maxima")

    if type(nucleos) is not int or nucleos <= 0:
        return jsonify({
            "error": "Nucleos debe ser un entero positivo"
        }), 400

    if (
        not isinstance(hilos, (int, str))
        or isinstance(hilos, bool)
        or not str(hilos).strip()
    ):
        return jsonify({"error": "Hilos no valido"}), 400

    if isinstance(hilos, int) and hilos <= 0:
        return jsonify({
            "error": "Hilos debe ser positivo"
        }), 400

    if not isinstance(frecuencia, str) or not frecuencia.strip():
        return jsonify({
            "error": "Frecuencia maxima requerida"
        }), 400

    with conectar_db() as conexion:
        cursor = conexion.execute("""
            INSERT INTO cpus (
                marca, modelo, nucleos,
                hilos, frecuencia_maxima
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            marca.strip(),
            modelo.strip(),
            nucleos,
            str(hilos).strip(),
            frecuencia.strip()
        ))

        nuevo_id = cursor.lastrowid
        conexion.commit()

    return jsonify({
        "mensaje": "Procesador registrado correctamente",
        "procesador": {
            "id": nuevo_id,
            "marca": marca.strip(),
            "modelo": modelo.strip(),
            "caracteristicas": {
                "nucleos": nucleos,
                "hilos": hilos,
                "frecuencia_maxima": frecuencia.strip()
            }
        }
    }), 201


inicializar_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
