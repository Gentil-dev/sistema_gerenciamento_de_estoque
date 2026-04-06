from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from datetime import timedelta


db = SQLAlchemy()

def create_app():
    if os.getenv("RENDER") is None:
        load_dotenv()

    app = Flask(__name__)
    app.permanent_session_lifetime = timedelta(minutes=30)

    app.secret_key = 'cd_porta_chave_unica_segura'  # chave para sessão

    # Configurações do banco
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
     
    from app.models import (
    Produto, 
    Historico, 
    DespesasMensais, 
    MovimentacaoSaida,
    ItemMovimentacaoSaida,
)

    migrate = Migrate(app, db)
        

    # Importa e registra as rotas
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app

    
                  
    
    
    

    
     
    