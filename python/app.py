from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# POST endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Please provide a message"}), 400

    # Call Ollama using subprocess
    try:
        result = subprocess.run(
            ["ollama", "run", "phi4-mini:3.8b", user_message],
            capture_output=True,
            text=True,
            check=True
        )
        ai_response = result.stdout.strip()
    except Exception as e:
        ai_response = f"Error generating response: {e}"

    return jsonify({
        "reply": ai_response
    })


if __name__ == "__main__":
    # Debug=True enables auto reload when file changes
    app.run(debug=True, host="0.0.0.0", port=5000)
