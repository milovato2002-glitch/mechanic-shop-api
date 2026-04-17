from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.service_ticket import ServiceTicket
from app.models.mechanic import Mechanic
from app.models.inventory import Inventory
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.service_ticket.schemas import (
    service_ticket_schema, service_tickets_schema, edit_ticket_schema
)


@service_ticket_bp.route('/', methods=['POST'])
def create_ticket():
    """
    Create a new service ticket
    ---
    tags:
      - Service Tickets
    summary: Create a new service ticket
    description: Creates a new service ticket with VIN, service date, description, and customer info.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ServiceTicketPayload'
    responses:
      201:
        description: Service ticket created successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
        examples:
          application/json:
            id: 1
            vin: "1HGCM82633A004352"
            service_date: "2025-01-15"
            service_desc: "Oil change and tire rotation"
            customer_email: "john@example.com"
            customer_id: 1
            mechanics: []
            parts: []
      400:
        description: Validation error
    definitions:
      ServiceTicketPayload:
        type: object
        required:
          - vin
          - service_date
          - service_desc
          - customer_email
        properties:
          vin:
            type: string
            example: "1HGCM82633A004352"
          service_date:
            type: string
            format: date
            example: "2025-01-15"
          service_desc:
            type: string
            example: "Oil change and tire rotation"
          customer_email:
            type: string
            example: "john@example.com"
          customer_id:
            type: integer
            example: 1
      ServiceTicketResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          vin:
            type: string
            example: "1HGCM82633A004352"
          service_date:
            type: string
            example: "2025-01-15"
          service_desc:
            type: string
            example: "Oil change and tire rotation"
          customer_email:
            type: string
            example: "john@example.com"
          customer_id:
            type: integer
            example: 1
          mechanics:
            type: array
            items:
              $ref: '#/definitions/MechanicResponse'
          parts:
            type: array
            items:
              $ref: '#/definitions/InventoryResponse'
    """
    try:
        ticket_data = service_ticket_schema.load(request.json, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(ticket_data)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket_data)), 201


@service_ticket_bp.route('/', methods=['GET'])
def get_tickets():
    """
    List all service tickets
    ---
    tags:
      - Service Tickets
    summary: List all service tickets
    description: Returns a list of all service tickets with their assigned mechanics and parts.
    responses:
      200:
        description: A list of service tickets
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicketResponse'
    """
    tickets = ServiceTicket.query.all()
    return jsonify(service_tickets_schema.dump(tickets)), 200


@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    """
    Assign a mechanic to a ticket
    ---
    tags:
      - Service Tickets
    summary: Assign a mechanic to a service ticket
    description: Assigns a mechanic to a service ticket. Fails if the mechanic is already assigned.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: Service Ticket ID
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: Mechanic ID
    responses:
      200:
        description: Mechanic assigned successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Mechanic already assigned to this ticket
        schema:
          type: object
          properties:
            message:
              type: string
        examples:
          application/json:
            message: "Mechanic already assigned to this ticket"
      404:
        description: Ticket or mechanic not found
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic in ticket.mechanics:
        return jsonify({'message': 'Mechanic already assigned to this ticket'}), 400

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200


@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    """
    Remove a mechanic from a ticket
    ---
    tags:
      - Service Tickets
    summary: Remove a mechanic from a service ticket
    description: Removes a mechanic from a service ticket. Fails if the mechanic is not assigned.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: Service Ticket ID
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: Mechanic ID
    responses:
      200:
        description: Mechanic removed successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Mechanic is not assigned to this ticket
        schema:
          type: object
          properties:
            message:
              type: string
        examples:
          application/json:
            message: "Mechanic is not assigned to this ticket"
      404:
        description: Ticket or mechanic not found
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic not in ticket.mechanics:
        return jsonify({'message': 'Mechanic is not assigned to this ticket'}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200


@service_ticket_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_ticket(ticket_id):
    """
    Bulk edit ticket mechanics
    ---
    tags:
      - Service Tickets
    summary: Bulk add/remove mechanics from a service ticket
    description: Adds and/or removes multiple mechanics from a service ticket in a single request.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: Service Ticket ID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/EditTicketPayload'
    responses:
      200:
        description: Ticket updated successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Validation error
      404:
        description: Ticket or mechanic not found
    definitions:
      EditTicketPayload:
        type: object
        properties:
          add_ids:
            type: array
            items:
              type: integer
            example: [1, 2]
            description: List of mechanic IDs to add
          remove_ids:
            type: array
            items:
              type: integer
            example: [3]
            description: List of mechanic IDs to remove
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)

    try:
        data = edit_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for mechanic_id in data.get('add_ids', []):
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in data.get('remove_ids', []):
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200


@service_ticket_bp.route('/<int:ticket_id>/add-part/<int:inventory_id>', methods=['PUT'])
def add_part(ticket_id, inventory_id):
    """
    Add an inventory part to a ticket
    ---
    tags:
      - Service Tickets
    summary: Add an inventory part to a service ticket
    description: Adds an inventory item to a service ticket. Fails if the part is already added.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: Service Ticket ID
      - in: path
        name: inventory_id
        type: integer
        required: true
        description: Inventory Item ID
    responses:
      200:
        description: Part added successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
      400:
        description: Part already added to this ticket
        schema:
          type: object
          properties:
            message:
              type: string
        examples:
          application/json:
            message: "Part already added to this ticket"
      404:
        description: Ticket or inventory item not found
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    part = Inventory.query.get_or_404(inventory_id)

    if part in ticket.parts:
        return jsonify({'message': 'Part already added to this ticket'}), 400

    ticket.parts.append(part)
    db.session.commit()
    return jsonify(service_ticket_schema.dump(ticket)), 200
