from app.extensions import db

service_mechanic = db.Table(
    'service_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'), primary_key=True),
)


class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_desc = db.Column(db.String(300), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)

    customer = db.relationship('Customer', back_populates='service_tickets')
    mechanics = db.relationship(
        'Mechanic',
        secondary=service_mechanic,
        back_populates='tickets',
    )
