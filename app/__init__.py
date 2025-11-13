from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = 'cd_porta_chave_unica_segura'  # chave para sessão

    # Configurações do banco
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Importa e registra as rotas
    from app import routes
    app.register_blueprint(routes.bp)

    return app
