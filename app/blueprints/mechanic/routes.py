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
    """
    Create a new mechanic
    ---
    tags:
      - Mechanics
    summary: Create a new mechanic
    description: Creates a new mechanic record with name, email, phone, and salary.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicPayload'
    responses:
      201:
        description: Mechanic created successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
        examples:
          application/json:
            id: 1
            name: "Jane Smith"
            email: "jane@shop.com"
            phone: "555-5678"
            salary: 55000.0
      400:
        description: Validation error
    definitions:
      MechanicPayload:
        type: object
        required:
          - name
          - email
          - phone
          - salary
        properties:
          name:
            type: string
            example: "Jane Smith"
          email:
            type: string
            example: "jane@shop.com"
          phone:
            type: string
            example: "555-5678"
          salary:
            type: number
            example: 55000.0
      MechanicResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          name:
            type: string
            example: "Jane Smith"
          email:
            type: string
            example: "jane@shop.com"
          phone:
            type: string
            example: "555-5678"
          salary:
            type: number
            example: 55000.0
    """
    try:
        mechanic_data = mechanic_schema.load(request.json, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(mechanic_data)
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic_data)), 201


@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    """
    List all mechanics
    ---
    tags:
      - Mechanics
    summary: List all mechanics
    description: Returns a list of all mechanic records.
    responses:
      200:
        description: A list of mechanics
        schema:
          type: array
          items:
            $ref: '#/definitions/MechanicResponse'
        examples:
          application/json:
            - id: 1
              name: "Jane Smith"
              email: "jane@shop.com"
              phone: "555-5678"
              salary: 55000.0
    """
    mechanics = Mechanic.query.all()
    return jsonify(mechanics_schema.dump(mechanics)), 200


@mechanic_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    """
    Update a mechanic
    ---
    tags:
      - Mechanics
    summary: Update an existing mechanic
    description: Updates a mechanic's information by ID.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Mechanic ID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicPayload'
    responses:
      200:
        description: Mechanic updated successfully
        schema:
          $ref: '#/definitions/MechanicResponse'
      400:
        description: Validation error
      404:
        description: Mechanic not found
    """
    mechanic = Mechanic.query.get_or_404(id)
    try:
        updated = mechanic_schema.load(request.json, instance=mechanic, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return jsonify(mechanic_schema.dump(updated)), 200


@mechanic_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    """
    Delete a mechanic
    ---
    tags:
      - Mechanics
    summary: Delete a mechanic
    description: Deletes a mechanic record by ID.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Mechanic ID
    responses:
      200:
        description: Mechanic deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
        examples:
          application/json:
            message: "Mechanic 1 deleted"
      404:
        description: Mechanic not found
    """
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'Mechanic {id} deleted'}), 200


@mechanic_bp.route('/most-tickets', methods=['GET'])
def mechanics_by_tickets():
    """
    Mechanics ranked by ticket count
    ---
    tags:
      - Mechanics
    summary: Get mechanics ranked by number of tickets
    description: Returns all mechanics ordered by the number of service tickets they have worked on (descending).
    responses:
      200:
        description: List of mechanics with ticket counts
        schema:
          type: array
          items:
            allOf:
              - $ref: '#/definitions/MechanicResponse'
              - type: object
                properties:
                  ticket_count:
                    type: integer
                    example: 5
        examples:
          application/json:
            - id: 1
              name: "Jane Smith"
              email: "jane@shop.com"
              phone: "555-5678"
              salary: 55000.0
              ticket_count: 5
    """
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
