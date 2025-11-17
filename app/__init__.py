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
    
    from app.models import Produto, Historico

    # Criar tabelas somente no ambiente local
    if os.getenv("RENDER") is None:
        with app.app_context():
            db.create_all()

    # Importa e registra as rotas
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app

    
                  
    
    
    

    
     
    