import enum

from .db import db


class TipoIngrediente(enum.Enum):
    Proteína = 1
    Carbohidrato = 2
    Vegetal = 3
    Lácteo = 4
    Fruta = 5
    Condimento = 6


class UnidadMedida(enum.Enum):
    Gramos = 1
    Kilogramos = 2
    Unidades = 3
    Litros = 4
    Mililitros = 5
    Cucharadas = 6


class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    tipo = db.Column(db.Enum(TipoIngrediente))
    unidad_medida = db.Column(db.Enum(UnidadMedida))
    disponible = db.Column(db.Boolean, default=True)
    recetas = db.relationship('Receta', back_populates='ingrediente_principal')