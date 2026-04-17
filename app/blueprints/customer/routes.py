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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(customers_schema.dump(pagination.items)), 200


@customer_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        updated = customer_schema.load(request.json, instance=customer, session=db.session)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return jsonify(customer_schema.dump(updated)), 200


@customer_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f'Customer {id} deleted'}), 200


@customer_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = Customer.query.filter_by(email=data['email']).first()
    if not customer:
        return jsonify({'message': 'Invalid credentials'}), 401

    token = encode_token(customer.id)
    return jsonify({'token': token}), 200


@customer_bp.route('/my-tickets', methods=['GET'])
@token_required
def my_tickets(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(service_tickets_schema.dump(customer.service_tickets)), 200
