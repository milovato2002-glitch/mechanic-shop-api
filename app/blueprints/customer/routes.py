from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.customer import Customer
from app.blueprints.customer import customer_bp
from app.blueprints.customer.schemas import customer_schema, customers_schema


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
def get_customers():
    customers = Customer.query.all()
    return jsonify(customers_schema.dump(customers)), 200


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
