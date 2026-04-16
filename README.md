# Mechanic Shop API

A RESTful Flask API for managing mechanics and service tickets at an auto repair shop.

## Tech Stack

- Python 3 + Flask
- Flask-SQLAlchemy (ORM)
- Flask-Marshmallow + Marshmallow-SQLAlchemy (serialization/validation)
- MySQL

## Project Structure

```
app/
├── __init__.py                  # App factory, blueprint registration
├── extensions.py                # SQLAlchemy & Marshmallow instances
├── models/
│   ├── mechanic.py              # Mechanic model
│   └── service_ticket.py        # ServiceTicket model + association table
└── blueprints/
    ├── mechanic/
    │   ├── __init__.py           # Blueprint init
    │   ├── routes.py             # CRUD endpoints
    │   └── schemas.py            # MechanicSchema
    └── service_ticket/
        ├── __init__.py           # Blueprint init
        ├── routes.py             # CRUD + assign/remove mechanic
        └── schemas.py            # ServiceTicketSchema
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

### Mechanics — `/mechanics`

| Method | Endpoint             | Description         |
|--------|----------------------|---------------------|
| POST   | `/mechanics/`        | Create a mechanic   |
| GET    | `/mechanics/`        | List all mechanics  |
| PUT    | `/mechanics/<id>`    | Update a mechanic   |
| DELETE | `/mechanics/<id>`    | Delete a mechanic   |

### Service Tickets — `/service-tickets`

| Method | Endpoint                                              | Description                     |
|--------|-------------------------------------------------------|---------------------------------|
| POST   | `/service-tickets/`                                   | Create a service ticket         |
| GET    | `/service-tickets/`                                   | List all service tickets        |
| PUT    | `/service-tickets/<ticket_id>/assign-mechanic/<mech_id>` | Assign a mechanic to a ticket   |
| PUT    | `/service-tickets/<ticket_id>/remove-mechanic/<mech_id>` | Remove a mechanic from a ticket |

## Postman Collection

Import `mechanic_shop_api.postman_collection.json` into Postman to test all endpoints.
