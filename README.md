# Mechanic Shop API

A RESTful Flask API for managing mechanics, customers, service tickets, and inventory at an auto repair shop.

## Tech Stack

- Python 3 + Flask
- Flask-SQLAlchemy (ORM)
- Flask-Marshmallow + Marshmallow-SQLAlchemy (serialization/validation)
- Flask-Limiter (rate limiting)
- Flask-Caching (response caching)
- python-jose (JWT authentication)
- MySQL

## Project Structure

```
app/
├── __init__.py                  # App factory, blueprint registration
├── extensions.py                # SQLAlchemy, Marshmallow, Limiter, Cache
├── utils/
│   └── auth.py                  # encode_token, token_required decorator
├── models/
│   ├── mechanic.py              # Mechanic model
│   ├── customer.py              # Customer model
│   ├── service_ticket.py        # ServiceTicket model + association table
│   └── inventory.py             # Inventory model + association table
└── blueprints/
    ├── mechanic/
    │   ├── __init__.py           # Blueprint init
    │   ├── routes.py             # CRUD + most-tickets ranking
    │   └── schemas.py            # MechanicSchema
    ├── customer/
    │   ├── __init__.py           # Blueprint init
    │   ├── routes.py             # CRUD + login + my-tickets (paginated GET)
    │   └── schemas.py            # CustomerSchema, LoginSchema
    ├── service_ticket/
    │   ├── __init__.py           # Blueprint init
    │   ├── routes.py             # CRUD + assign/remove mechanic + edit + add-part
    │   └── schemas.py            # ServiceTicketSchema, EditTicketSchema
    └── inventory/
        ├── __init__.py           # Blueprint init
        ├── routes.py             # Full CRUD
        └── schemas.py            # InventorySchema
```

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/Scripts/activate   # Windows Git Bash
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create the MySQL database:
   ```sql
   CREATE DATABASE mechanic_shop_db;
   ```

4. Update `app/__init__.py` with your MySQL credentials.

5. Run the server:
   ```
   python run.py
   ```

## API Endpoints

### Customers — `/customers`

| Method | Endpoint                | Description                          |
|--------|-------------------------|--------------------------------------|
| POST   | `/customers/`           | Create a customer                    |
| GET    | `/customers/?page=1&per_page=10` | List customers (paginated, cached) |
| PUT    | `/customers/<id>`       | Update a customer                    |
| DELETE | `/customers/<id>`       | Delete a customer                    |
| POST   | `/customers/login`      | Login (returns JWT token, rate limited) |
| GET    | `/customers/my-tickets` | Get logged-in customer's tickets (token required) |

### Mechanics — `/mechanics`

| Method | Endpoint                  | Description                              |
|--------|---------------------------|------------------------------------------|
| POST   | `/mechanics/`             | Create a mechanic                        |
| GET    | `/mechanics/`             | List all mechanics                       |
| GET    | `/mechanics/most-tickets` | Mechanics ordered by most tickets worked |
| PUT    | `/mechanics/<id>`         | Update a mechanic                        |
| DELETE | `/mechanics/<id>`         | Delete a mechanic                        |

### Service Tickets — `/service-tickets`

| Method | Endpoint                                                 | Description                     |
|--------|----------------------------------------------------------|---------------------------------|
| POST   | `/service-tickets/`                                      | Create a service ticket         |
| GET    | `/service-tickets/`                                      | List all service tickets        |
| PUT    | `/service-tickets/<ticket_id>/assign-mechanic/<mech_id>` | Assign a mechanic to a ticket   |
| PUT    | `/service-tickets/<ticket_id>/remove-mechanic/<mech_id>` | Remove a mechanic from a ticket |
| PUT    | `/service-tickets/<ticket_id>/edit`                      | Bulk add/remove mechanics       |
| PUT    | `/service-tickets/<ticket_id>/add-part/<inventory_id>`   | Add an inventory part to ticket |

### Inventory — `/inventory`

| Method | Endpoint          | Description             |
|--------|-------------------|-------------------------|
| POST   | `/inventory/`     | Create an inventory item |
| GET    | `/inventory/`     | List all inventory items |
| PUT    | `/inventory/<id>` | Update an inventory item |
| DELETE | `/inventory/<id>` | Delete an inventory item |

## Authentication

The `/customers/login` endpoint accepts `email` and `password` and returns a JWT token. Include the token in subsequent requests using the `Authorization: Bearer <token>` header to access protected routes like `/customers/my-tickets`.

## Rate Limiting

The login endpoint is rate-limited to **5 requests per minute** per IP address. Global defaults are 200/day and 50/hour.

## Caching

The `GET /customers/` endpoint is cached for 60 seconds using Flask-Caching with a simple in-memory cache.

## Postman Collection

Import `mechanic_shop_api.postman_collection.json` into Postman to test all endpoints.
