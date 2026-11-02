from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def index():
    return jsonify(message="Hello from CI/CD", version="1.0.2")

@app.get("/health")
def health():
    return jsonify(status="ok")