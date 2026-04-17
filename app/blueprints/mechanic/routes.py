from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import func
from app.extensions import db
from app.models.mechanic import Mechanic
from app.models.service_ticket import service_mechanic
from app.blueprints.mechanic import mechanic_bp
from app.blueprints.mechanic.schemas import mechanic_schema, mechanics_schema


@mechanic_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(mechanic_data)
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic_data)), 201


@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return jsonify(mechanics_schema.dump(mechanics)), 200


@mechanic_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    try:
        updated = mechanic_schema.load(request.json, instance=mechanic, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return jsonify(mechanic_schema.dump(updated)), 200


@mechanic_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'Mechanic {id} deleted'}), 200


@mechanic_bp.route('/most-tickets', methods=['GET'])
def mechanics_by_tickets():
    results = (
        db.session.query(Mechanic, func.count(service_mechanic.c.service_ticket_id).label('ticket_count'))
        .outerjoin(service_mechanic, Mechanic.id == service_mechanic.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(func.count(service_mechanic.c.service_ticket_id).desc())
        .all()
    )
    output = []
    for mechanic, ticket_count in results:
        data = mechanic_schema.dump(mechanic)
        data['ticket_count'] = ticket_count
        output.append(data)
    return jsonify(output), 200
