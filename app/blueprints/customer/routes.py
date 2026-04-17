from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import db, cache, limiter
from app.models.customer import Customer
from app.blueprints.customer import customer_bp
from app.blueprints.customer.schemas import customer_schema, customers_schema, login_schema
from app.blueprints.service_ticket.schemas import service_tickets_schema
from app.utils.auth import encode_token, token_required


@customer_bp.route('/', methods=['POST'])
def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    summary: Create a new customer
    description: Creates a new customer record with name, email, and phone.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerPayload'
    responses:
      201:
        description: Customer created successfully
        schema:
          $ref: '#/definitions/CustomerResponse'
        examples:
          application/json:
            id: 1
            name: "John Doe"
            email: "john@example.com"
            phone: "555-1234"
      400:
        description: Validation error
        schema:
          type: object
          properties:
            name:
              type: array
              items:
                type: string
        examples:
          application/json:
            email: ["Not a valid email address."]
    definitions:
      CustomerPayload:
        type: object
        required:
          - name
          - email
          - phone
        properties:
          name:
            type: string
            example: "John Doe"
          email:
            type: string
            example: "john@example.com"
          phone:
            type: string
            example: "555-1234"
      CustomerResponse:
        type: object
        properties:
          id:
            type: integer
            example: 1
          name:
            type: string
            example: "John Doe"
          email:
            type: string
            example: "john@example.com"
          phone:
            type: string
            example: "555-1234"
    """
    try:
        customer_data = customer_schema.load(request.json, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(customer_data)
    db.session.commit()
    return jsonify(customer_schema.dump(customer_data)), 201


@customer_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_customers():
    """
    List all customers
    ---
    tags:
      - Customers
    summary: List all customers (paginated)
    description: Returns a paginated list of customers. Results are cached for 60 seconds.
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: Page number
      - in: query
        name: per_page
        type: integer
        default: 10
        description: Items per page
    responses:
      200:
        description: A list of customers
        schema:
          type: array
          items:
            $ref: '#/definitions/CustomerResponse'
        examples:
          application/json:
            - id: 1
              name: "John Doe"
              email: "john@example.com"
              phone: "555-1234"
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(customers_schema.dump(pagination.items)), 200


@customer_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    """
    Update a customer
    ---
    tags:
      - Customers
    summary: Update an existing customer
    description: Updates a customer's information by ID.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Customer ID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerPayload'
    responses:
      200:
        description: Customer updated successfully
        schema:
          $ref: '#/definitions/CustomerResponse'
      400:
        description: Validation error
      404:
        description: Customer not found
    """
    customer = Customer.query.get_or_404(id)
    try:
        updated = customer_schema.load(request.json, instance=customer, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return jsonify(customer_schema.dump(updated)), 200


@customer_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """
    Delete a customer
    ---
    tags:
      - Customers
    summary: Delete a customer
    description: Deletes a customer record by ID.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Customer ID
    responses:
      200:
        description: Customer deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
        examples:
          application/json:
            message: "Customer 1 deleted"
      404:
        description: Customer not found
    """
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f'Customer {id} deleted'}), 200


@customer_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    Customer login
    ---
    tags:
      - Customers
    summary: Login and receive a JWT token
    description: Authenticates a customer by email and returns a JWT token. Rate limited to 5 requests per minute.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/LoginPayload'
    responses:
      200:
        description: Login successful
        schema:
          $ref: '#/definitions/LoginResponse'
        examples:
          application/json:
            token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      400:
        description: Validation error
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            message:
              type: string
        examples:
          application/json:
            message: "Invalid credentials"
    definitions:
      LoginPayload:
        type: object
        required:
          - email
          - password
        properties:
          email:
            type: string
            example: "john@example.com"
          password:
            type: string
            example: "secret123"
      LoginResponse:
        type: object
        properties:
          token:
            type: string
            example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    try:
        data = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = Customer.query.filter_by(email=data['email']).first()
    if not customer:
        return jsonify({'message': 'Invalid credentials'}), 401

    token = encode_token(customer.id)
    return jsonify({'token': token}), 200


@customer_bp.route('/test-token', methods=['GET'])
def test_token():
    """
    Test token header
    ---
    tags:
      - Customers
    summary: Debug endpoint for authorization headers
    description: Returns the Authorization header and all request headers for debugging purposes.
    responses:
      200:
        description: Header information
        schema:
          type: object
          properties:
            authorization_header:
              type: string
            headers_present:
              type: object
    """
    auth_header = request.headers.get('Authorization', None)
    return jsonify({
        'authorization_header': auth_header,
        'headers_present': dict(request.headers),
    }), 200


@customer_bp.route('/my-tickets', methods=['GET'])
@token_required
def my_tickets(customer_id):
    """
    Get my service tickets
    ---
    tags:
      - Customers
    summary: Get the logged-in customer's service tickets
    description: Returns all service tickets for the authenticated customer. Requires a valid JWT token.
    security:
      - Bearer: []
    responses:
      200:
        description: A list of customer's service tickets
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicketResponse'
      401:
        description: Missing or invalid token
        schema:
          type: object
          properties:
            message:
              type: string
        examples:
          application/json:
            message: "Missing token"
      404:
        description: Customer not found
    """
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(service_tickets_schema.dump(customer.service_tickets)), 200
