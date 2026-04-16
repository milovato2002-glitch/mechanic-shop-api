from app.extensions import db


class Mechanic(db.Model):
    __tablename__ = 'mechanics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    salary = db.Column(db.Float, nullable=False)

    tickets = db.relationship(
        'ServiceTicket',
        secondary='service_mechanic',
        back_populates='mechanics',
    )
