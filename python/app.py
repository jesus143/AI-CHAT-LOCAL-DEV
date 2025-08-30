from flask import Flask, request, jsonify
import subprocess
import sys

app = Flask(__name__)

# Global conversation history
conversation_history = []
MAX_HISTORY = 10  # keep only last 10 exchanges


@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    

    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Please provide a message"}), 400


    logger("User: " + user_message)
    # Add user message to history
    conversation_history.append({"role": "user", "content": user_message + ". [Please always make your response consise and short, if you don't know the answer. Just say, I am not sure what you mean. And pls don't repeat this text inside this bracket]"})


    # Trim history to avoid overload
    conversation_history = conversation_history[-MAX_HISTORY:]

    # Build prompt from history
    prompt = ""
    for entry in conversation_history:
        role = entry["role"]
        content = entry["content"]
        prompt += f"{role.capitalize()}: {content}\n"
    prompt += "AI:"  # Hint for model to continue as AI

    # Call Ollama using subprocess
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
    conversation_history.append({"role": "ai", "content": ai_response})

    logger("AI:" + ai_response)

    return jsonify({
        "reply": ai_response,
        "history": conversation_history  # optional, to debug
    })

def logger(message):
    print(f"INFO {message}", file=sys.stderr)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
