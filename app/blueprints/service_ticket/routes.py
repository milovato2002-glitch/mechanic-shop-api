from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.service_ticket import ServiceTicket
from app.models.mechanic import Mechanic
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.service_ticket.schemas import service_ticket_schema, service_tickets_schema


@service_ticket_bp.route('/', methods=['POST'])
def create_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(ticket_data)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket_data)), 201


@service_ticket_bp.route('/', methods=['GET'])
def get_tickets():
    tickets = ServiceTicket.query.all()
    return jsonify(service_tickets_schema.dump(tickets)), 200


@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic in ticket.mechanics:
        return jsonify({'message': 'Mechanic already assigned to this ticket'}), 400

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200


@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic not in ticket.mechanics:
        return jsonify({'message': 'Mechanic is not assigned to this ticket'}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200
