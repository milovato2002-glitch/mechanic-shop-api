from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.service_ticket import ServiceTicket
from app.blueprints.mechanic.schemas import MechanicSchema


class ServiceTicketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_relationships = True
        dump_only = ('mechanics',)

    mechanics = fields.Nested(MechanicSchema, many=True)


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
