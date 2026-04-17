import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from app.extensions import db, ma, limiter, cache
from app.models import Mechanic, Customer, ServiceTicket, Inventory  # noqa: F401
from app.blueprints.mechanic import mechanic_bp
from app.blueprints.customer import customer_bp
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.inventory import inventory_bp

load_dotenv()

SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'


def create_app(config_name='default'):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.config['CACHE_TYPE'] = 'SimpleCache'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'mysql+mysqlconnector://root:password@localhost/mechanic_shop_db'
        )
        app.config['CACHE_TYPE'] = 'SimpleCache'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

    # Swagger JSON endpoint
    @app.route('/api/swagger.json')
    def swagger_spec():
        swag = swagger(app)
        swag['info']['title'] = 'Mechanic Shop API'
        swag['info']['version'] = '1.0.0'
        swag['info']['description'] = 'A RESTful API for managing mechanics, customers, service tickets, and inventory at an auto repair shop.'
        swag['host'] = 'localhost:5000'
        swag['basePath'] = '/'
        swag['schemes'] = ['http']
        swag['securityDefinitions'] = {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT token. Format: Bearer <token>'
            }
        }
        return jsonify(swag)

    # Swagger UI blueprint
    swaggerui_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': 'Mechanic Shop API'}
    )
    app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)

    with app.app_context():
        db.create_all()

    return app
