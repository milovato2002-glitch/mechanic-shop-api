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


def _get_database_uri():
    """Resolve the database URI for the current environment.

    Priority:
      1. SQLALCHEMY_DATABASE_URI (explicit override)
      2. DATABASE_URL (Render / Heroku-style Postgres)
      3. Local MySQL fallback for development
    """
    uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if uri:
        return uri

    uri = os.environ.get('DATABASE_URL')
    if uri:
        if uri.startswith('postgres://'):
            uri = uri.replace('postgres://', 'postgresql://', 1)
        return uri

    return 'mysql+mysqlconnector://root:password@localhost/mechanic_shop_db'


def create_app(config_name='default'):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.config['CACHE_TYPE'] = 'SimpleCache'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = _get_database_uri()
        app.config['CACHE_TYPE'] = 'SimpleCache'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

    @app.route('/')
    def index():
        return jsonify({
            'name': 'Mechanic Shop API',
            'version': '1.0.0',
            'docs': '/api/docs',
            'status': 'ok'
        })

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'}), 200

    @app.route('/api/swagger.json')
    def swagger_spec():
        try:
            swag = swagger(app)
        except (AttributeError, TypeError):
            swag = {'swagger': '2.0', 'paths': {}}
        swag['info'] = {
            'title': 'Mechanic Shop API',
            'version': '1.0.0',
            'description': 'A RESTful API for managing mechanics, customers, service tickets, and inventory at an auto repair shop.'
        }
        swag['basePath'] = '/'
        swag['schemes'] = ['https', 'http']
        swag['securityDefinitions'] = {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT token. Format: Bearer <token>'
            }
        }
        return jsonify(swag)

    swaggerui_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': 'Mechanic Shop API'}
    )
    app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)

    with app.app_context():
        db.create_all()

    return app