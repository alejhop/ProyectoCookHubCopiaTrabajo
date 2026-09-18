from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields

db = SQLAlchemy()


class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None

        return {
            'llave': value.name,
            'valor': value.value
        }


class EnumANombre(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None

        return value.name
