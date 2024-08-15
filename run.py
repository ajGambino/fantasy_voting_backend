from flask import Flask
from flask_cors import CORS
from app import app

# deploy version
# CORS(app, resources={r"/*": {"origins": "https://theresurrection.vercel.app"}})

# local
CORS(app, resources={r"/*": {"origins": "*" }})

# below is for local development
if __name__ == '__main__':
    app.run(debug=True)
