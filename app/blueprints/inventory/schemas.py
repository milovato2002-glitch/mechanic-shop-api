from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.inventory import Inventory


class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        include_relationships = True


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
