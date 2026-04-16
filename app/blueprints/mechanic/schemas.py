from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.mechanic import Mechanic


class MechanicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_relationships = True


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
