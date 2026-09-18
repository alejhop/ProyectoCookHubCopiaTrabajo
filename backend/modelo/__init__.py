from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .db import db, EnumANombre
from .receta import Dificultad, Receta
from .ingrediente import TipoIngrediente, UnidadMedida, Ingrediente


class RecetaSchema(SQLAlchemyAutoSchema):
    dificultad = EnumANombre(attribute='dificultad')

    class Meta:
        model = Receta
        include_relationships = True
        include_fk = True
        load_instance = True

class IngredienteSchema(SQLAlchemyAutoSchema):
    tipo = EnumANombre(attribute='tipo')
    unidad_medida = EnumANombre(attribute='unidad_medida')

    class Meta:
        model = Ingrediente
        include_relationships = True
        load_instance = True