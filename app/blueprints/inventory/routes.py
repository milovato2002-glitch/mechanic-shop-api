from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.inventory import Inventory
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema


@inventory_bp.route('/', methods=['POST'])
def create_inventory():
    try:
        item_data = inventory_schema.load(request.json, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(item_data)
    db.session.commit()
    return jsonify(inventory_schema.dump(item_data)), 201


@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    items = Inventory.query.all()
    return jsonify(inventories_schema.dump(items)), 200


@inventory_bp.route('/<int:id>', methods=['PUT'])
def update_inventory(id):
    item = Inventory.query.get_or_404(id)
    try:
        updated = inventory_schema.load(request.json, instance=item, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return jsonify(inventory_schema.dump(updated)), 200


@inventory_bp.route('/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    item = Inventory.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': f'Inventory item {id} deleted'}), 200
