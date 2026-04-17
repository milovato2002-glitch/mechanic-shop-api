from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from jose import jwt, JWTError

SECRET_KEY = 'super-secret-key'


def encode_token(customer_id):
    payload = {
        'sub': str(customer_id),
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Missing token'}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            customer_id = int(payload['sub'])
        except JWTError:
            return jsonify({'message': 'Invalid or expired token'}), 401

        return f(customer_id, *args, **kwargs)
    return decorated
