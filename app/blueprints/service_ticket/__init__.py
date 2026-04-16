from flask import Blueprint

service_ticket_bp = Blueprint('service_ticket', __name__)

from app.blueprints.service_ticket import routes  # noqa: E402, F401
