from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.mechanic import Mechanic
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
    return mechanic_schema.jsonify(mechanic_data), 201


@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanic_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    try:
        updated = mechanic_schema.load(request.json, instance=mechanic, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return mechanic_schema.jsonify(updated), 200


@mechanic_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'Mechanic {id} deleted'}), 200
