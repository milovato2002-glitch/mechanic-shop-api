import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db, ma
from app.models import Mechanic, Customer, ServiceTicket  # noqa: F401
from app.blueprints.mechanic import mechanic_bp
from app.blueprints.customer import customer_bp
from app.blueprints.service_ticket import service_ticket_bp

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'SQLALCHEMY_DATABASE_URI',
        'mysql+mysqlconnector://root:password@localhost/mechanic_shop_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    ma.init_app(app)

    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')

    with app.app_context():
        db.create_all()

    return app
