import math
import logging
import sys

from flask import Flask, jsonify, render_template, request
from flask.logging import default_handler


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.logger.removeHandler(default_handler)
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.INFO)
app.logger.addHandler(log_handler)

@app.get("/")
def home():
    return render_template("index.html")


@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})


@app.post("/share-location")
def share_location():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "È richiesto un oggetto JSON valido."}), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    accuracy = data.get("accuracy")
    if (
        isinstance(latitude, bool)
        or not isinstance(latitude, (int, float))
        or not math.isfinite(latitude)
        or not -90 <= latitude <= 90
        or isinstance(longitude, bool)
        or not isinstance(longitude, (int, float))
        or not math.isfinite(longitude)
        or not -180 <= longitude <= 180
        or isinstance(accuracy, bool)
        or not isinstance(accuracy, (int, float))
        or not math.isfinite(accuracy)
        or accuracy < 0
    ):
        return jsonify({"error": "Coordinate o precisione non valide."}), 400

    app.logger.info(
        "Posizione condivisa: latitudine=%s, longitudine=%s, precisione=%s m",
        latitude,
        longitude,
        accuracy,
    )
    return jsonify({"message": "Posizione ricevuta."})


if __name__ == "__main__":
    app.run(debug=True)