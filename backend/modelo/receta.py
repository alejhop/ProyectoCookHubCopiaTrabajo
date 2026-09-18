import enum

from .db import db


class Dificultad(enum.Enum):
    Fácil = 1
    Medio = 2
    Difícil = 3


class Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    descripcion = db.Column(db.String(256))
    tiempo_preparacion = db.Column(db.Integer)
    dificultad = db.Column(db.Enum(Dificultad))
    porciones = db.Column(db.Integer)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('ingrediente.id'), nullable=False)
    ingrediente_principal = db.relationship('Ingrediente', back_populates='recetas')
