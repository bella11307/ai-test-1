import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string
import sys

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDWTIEvXo0sM5CBPlBUQmuVeMfvU9eiQMo")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chat-box {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: 20%;
        }
        .bot-message {
            background-color: #f5f5f5;
            margin-right: 20%;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <h1>AI Chatbot</h1>
        <div class="chat-box" id="chatBox"></div>
        <div class="input-container">
            <input type="text" id="userInput" placeholder="Type your message...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    <script>
        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (message) {
                addMessage(message, 'user');
                input.value = '';
                
                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({message: message}),
                })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.response, 'bot');
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessage('Sorry, there was an error processing your request.', 'bot');
                });
            }
        }

        function addMessage(message, sender) {
            const chatBox = document.getElementById('chatBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = message;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

def get_ai_response(message):
    try:
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    response = get_ai_response(message)
    return jsonify({'response': response})

def cli_mode():
    print("AI Chatbot CLI Mode (Type 'exit' to quit)")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        response = get_ai_response(user_input)
        print(f"\nAI: {response}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        cli_mode()
    else:
        app.run(debug=True) 