import os

from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_swagger import swagger

# Identifica el directorio base
basedir = os.path.abspath(os.path.dirname(__file__))

def registrar_handlers():
    import alpesonline.modulos.ordenes.aplicacion

def importar_modelos_alchemy():
    import alpesonline.modulos.ordenes.infraestructura.dto

def comenzar_consumidor(app):

    import threading
    import alpesonline.modulos.ordenes.infraestructura.consumidores as ordenes

    # Suscripción a eventos
    threading.Thread(target=ordenes.suscribirse_a_eventos, args=[app]).start()

    # Suscripción a comandos
    threading.Thread(target=ordenes.suscribirse_a_comandos, args=[app]).start()

def create_app(configuracion={}):
    # Init la aplicacion de Flask
    app = Flask(__name__, instance_relative_config=True)
    
    app.secret_key = '9d58f98f-3ae8-4149-a09f-3a8c2012e32c'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['TESTING'] = configuracion.get('TESTING')

     # Inicializa la DB
    from alpesonline.config.db import init_db, database_connection

    app.config['SQLALCHEMY_DATABASE_URI'] = database_connection(configuracion, basedir=basedir)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)

    from alpesonline.config.db import db

    importar_modelos_alchemy()
    registrar_handlers()

    with app.app_context():
        db.create_all()
        if not app.config.get('TESTING'):
            comenzar_consumidor(app)
        
     # Importa Blueprints
    from . import ordenes

    # Registro de Blueprints
    app.register_blueprint(ordenes.bp)

    @app.route("/spec")
    def spec():
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "My API"
        return jsonify(swag)

    @app.route("/health")
    def health():
        return {"status": "up"}

    return app
