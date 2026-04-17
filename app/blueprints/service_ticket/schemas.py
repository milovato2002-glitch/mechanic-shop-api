from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.service_ticket import ServiceTicket
from app.blueprints.mechanic.schemas import MechanicSchema
from app.blueprints.inventory.schemas import InventorySchema


class ServiceTicketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_relationships = True
        dump_only = ('mechanics', 'parts')

    mechanics = fields.Nested(MechanicSchema, many=True)
    parts = fields.Nested(InventorySchema, many=True)


class EditTicketSchema(Schema):
    add_ids = fields.List(fields.Integer(), load_default=[])
    remove_ids = fields.List(fields.Integer(), load_default=[])


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_ticket_schema = EditTicketSchema()
