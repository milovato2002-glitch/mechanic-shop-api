from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.inventory import Inventory
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema


@inventory_bp.route('/', methods=['POST'])
def create_inventory():
    """
    Create a new inventory item
    ---
    tags:
      - Inventory
    summary: Create a new inventory item
    description: Creates a new inventory item with name and price.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/InventoryPayload'
    responses:
      201:
        description: Inventory item created successfully
        schema:
          $ref: '#/definitions/InventoryResponse'
        examples:
          application/json:
            id: 1
            name: "Oil Filter"
            price: 12.99
      400:
        description: Validation error
    definitions:
      InventoryPayload:
        type: object
        required:
          - name
          - price
        properties:
          name:
            type: string
            example: "Oil Filter"
          price:
            type: number
            example: 12.99
      InventoryResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          name:
            type: string
            example: "Oil Filter"
          price:
            type: number
            example: 12.99
    """
    try:
        item_data = inventory_schema.load(request.json, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(item_data)
    db.session.commit()
    return jsonify(inventory_schema.dump(item_data)), 201


@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    """
    List all inventory items
    ---
    tags:
      - Inventory
    summary: List all inventory items
    description: Returns a list of all inventory items in the shop.
    responses:
      200:
        description: A list of inventory items
        schema:
          type: array
          items:
            $ref: '#/definitions/InventoryResponse'
        examples:
          application/json:
            - id: 1
              name: "Oil Filter"
              price: 12.99
    """
    items = Inventory.query.all()
    return jsonify(inventories_schema.dump(items)), 200


@inventory_bp.route('/<int:id>', methods=['PUT'])
def update_inventory(id):
    """
    Update an inventory item
    ---
    tags:
      - Inventory
    summary: Update an existing inventory item
    description: Updates an inventory item's information by ID.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Inventory Item ID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/InventoryPayload'
    responses:
      200:
        description: Inventory item updated successfully
        schema:
          $ref: '#/definitions/InventoryResponse'
      400:
        description: Validation error
      404:
        description: Inventory item not found
    """
    item = Inventory.query.get_or_404(id)
    try:
        updated = inventory_schema.load(request.json, instance=item, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return jsonify(inventory_schema.dump(updated)), 200


@inventory_bp.route('/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    """
    Delete an inventory item
    ---
    tags:
      - Inventory
    summary: Delete an inventory item
    description: Deletes an inventory item by ID.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Inventory Item ID
    responses:
      200:
        description: Inventory item deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
        examples:
          application/json:
            message: "Inventory item 1 deleted"
      404:
        description: Inventory item not found
    """
    item = Inventory.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': f'Inventory item {id} deleted'}), 200
