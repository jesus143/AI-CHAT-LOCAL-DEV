from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Store conversation in memory (global for demo)
conversation_history = []

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Please provide a message"}), 400

    # Append user message to history
    conversation_history.append({"role": "user", "content": user_message})

    # Prepare prompt with history
    prompt = ""
    for msg in conversation_history:
        role = msg["role"].capitalize()
        prompt += f"{role}: {msg['content']}\n"
    prompt += "AI:"

    # Call Ollama with the full conversation
    try:
        result = subprocess.run(
            ["ollama", "run", "phi4-mini:3.8b", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        ai_response = result.stdout.strip()
    except Exception as e:
        ai_response = f"Error generating response: {e}"

    # Save AI response to history
    conversation_history.append({"role": "ai", "content": ai_response + ". Pls always answer straight to the point and short."})

    return jsonify({
        "reply": ai_response,
        "history": conversation_history  # optional, for debugging
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
