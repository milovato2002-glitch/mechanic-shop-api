from app.extensions import db

service_inventory = db.Table(
    'service_inventory',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'), primary_key=True),
)


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    tickets = db.relationship(
        'ServiceTicket',
        secondary=service_inventory,
        back_populates='parts',
    )
