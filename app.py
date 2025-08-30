# app.py
from flask import Flask
app = Flask(__name__)

@app.get("/")
def home():
    return "Hello, world! 🚀"

if __name__ == "__main__":
    app.run()
