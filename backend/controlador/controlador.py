import os

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from modelo import db
from vista import (
    VistaRecetas,
    VistaReceta,
    VistaIngredientes,
    VistaIngrediente,
    VistaReporte,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "cookhub-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "COOKHUB_DATABASE_URL", "sqlite:///cookhub.db"
)
CORS(app)

db.init_app(app)

with app.app_context():
    db.create_all()

api = Api(app)

# Rutas para recetas
api.add_resource(VistaRecetas, "/api/recetas")
api.add_resource(VistaReceta, "/api/recetas/<int:id_receta>")

# Rutas para ingredientes
api.add_resource(VistaIngredientes, "/api/ingredientes")
api.add_resource(VistaIngrediente, "/api/ingredientes/<int:id_ingrediente>")

# Ruta para reportes
api.add_resource(VistaReporte, "/api/reportes/ingredientes")
