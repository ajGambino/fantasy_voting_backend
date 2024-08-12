from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()  

app = Flask(__name__)
app.config.from_object('app.config.Config')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

from app import routes  
