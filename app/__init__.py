from flask import Flask,render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
app = Flask(__name__)
app.config.from_object("app.config.Config")
db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
from app import models
from app import routes