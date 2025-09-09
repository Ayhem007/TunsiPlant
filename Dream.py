from flask import Flask, request, jsonify
from kindwise import PlantApi
import tempfile

app = Flask(__name__)
api = PlantApi(api_key="Da7fQIPJWhFs0hCDxJ55sI7frSjBmi75jOmL4gy5SYF9fsv6mw")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Plant Disease Detection API",
        "status": "running",
        "endpoint": "/detect-disease (POST)"
    })

@app.route("/detect-disease", methods=["POST"])
def detect_disease():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            file.save(tmp.name)
            image_path = tmp.name

            identification = api.identify(
                image_path,
                latitude_longitude=(49.20340, 16.57318)
            )

            result = api.get_identification(identification.access_token)
            api.delete_identification(identification)

        suggestions = result.result.classification.suggestions
        if not suggestions:
            return jsonify({"disease_name": "Unknown", "confidence": 0, "severity": "N/A", "description": "No match found", "treatments": []})

        top = suggestions[0]
        response = {
            "disease_name": top.name,
            "confidence": round(top.probability * 100, 2),
            "severity": "N/A",
            "description": top.details.description if top.details else "No description available",
            "treatments": ["This plant may need care steps depending on the disease"]
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
