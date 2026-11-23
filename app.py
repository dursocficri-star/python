import math
import logging

from flask import Flask, jsonify, render_template_string, request


app = Flask(__name__)
app.logger.setLevel(logging.INFO)

PAGE = """
<!doctype html>
<html lang="it">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Condividi la posizione</title>
  </head>
  <body>
    <main>
      <h1>Condividi la tua posizione</h1>
      <p>
        Se acconsenti, la tua posizione sarà inviata al server e registrata
        nei log del servizio, accessibili al gestore del sito.
      </p>
      <label>
        <input id="consent" type="checkbox">
        Acconsento a inviare la mia posizione
      </label>
      <p><button id="share" type="button" disabled>Condividi posizione</button></p>
      <p id="status" role="status" aria-live="polite"></p>
    </main>
    <script>
      const consent = document.getElementById("consent");
      const share = document.getElementById("share");
      const status = document.getElementById("status");

      consent.addEventListener("change", () => {
        share.disabled = !consent.checked;
      });

      share.addEventListener("click", () => {
        if (!consent.checked) return;
        if (!navigator.geolocation) {
          status.textContent = "La geolocalizzazione non è supportata.";
          return;
        }

        status.textContent = "Richiesta della posizione in corso...";
        navigator.geolocation.getCurrentPosition(async (position) => {
          try {
            const response = await fetch("/share-location", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
              })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || "Invio non riuscito.");
            status.textContent = "Posizione inviata al server.";
          } catch (error) {
            status.textContent = error.message || "Errore durante l'invio.";
          }
        }, (error) => {
          status.textContent = error.message || "Impossibile ottenere la posizione.";
        });
      });
    </script>
  </body>
</html>
"""


@app.get("/")
def home():
    return render_template_string(PAGE)


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