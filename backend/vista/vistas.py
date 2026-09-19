from flask import request
from flask_restful import Resource

from modelo import db, Receta, RecetaSchema, Ingrediente, IngredienteSchema

recetas_schema = RecetaSchema()
ingrediente_schema = IngredienteSchema()


class VistaRecetas(Resource):
    def get(self):
        recetas_con_ingrediente = []
        for receta in Receta.query.all():
            receta_completa = recetas_schema.dump(receta)
            receta_completa["ingrediente"] = (
                ingrediente_schema.dump(receta.ingrediente_principal)
                if receta.ingrediente_principal else None
            )
            recetas_con_ingrediente.append(receta_completa)
        return recetas_con_ingrediente

    def post(self):
        try:
            nombre = request.json["nombre"]
            descripcion = request.json["descripcion"]
            tiempo_preparacion = int(request.json["tiempo_preparacion"])
            dificultad = request.json["dificultad"]
            porciones = int(request.json["porciones"])
            ingrediente_id = int(request.json["ingrediente_id"])
        except (KeyError, ValueError):
            return {"mensaje": "Datos inválidos para crear la receta"}, 400

        if Ingrediente.query.get(ingrediente_id) is None:
            return {"mensaje": "El ingrediente seleccionado no existe"}, 400

        nueva_receta = Receta(
            nombre=nombre,
            descripcion=descripcion,
            tiempo_preparacion=tiempo_preparacion,
            dificultad=dificultad,
            porciones=porciones,
            ingrediente_id=ingrediente_id,
        )
        db.session.add(nueva_receta)
        db.session.commit()

        return {"mensaje": "Receta creada exitosamente", "receta": recetas_schema.dump(nueva_receta)}, 201


class VistaReceta(Resource):
    def get(self, id_receta):
        receta = Receta.query.get(id_receta)
        if not receta:
            return {"mensaje": "Receta no encontrada"}, 404
        receta_completa = recetas_schema.dump(receta)
        receta_completa["ingrediente"] = (
            ingrediente_schema.dump(receta.ingrediente_principal)
            if receta.ingrediente_principal else None
        )
        return receta_completa

    def put(self, id_receta):
        receta = Receta.query.get(id_receta)
        if not receta:
            return {"mensaje": "Receta no encontrada"}, 404
        try:
            nombre = request.json["nombre"]
            descripcion = request.json["descripcion"]
            tiempo_preparacion = int(request.json["tiempo_preparacion"])
            dificultad = request.json["dificultad"]
            porciones = int(request.json["porciones"])
            ingrediente_id = int(request.json["ingrediente_id"])
        except (KeyError, ValueError):
            return {"mensaje": "Datos inválidos para actualizar la receta"}, 400

        if Ingrediente.query.get(ingrediente_id) is None:
            return {"mensaje": "El ingrediente seleccionado no existe"}, 400

        receta.nombre = nombre
        receta.descripcion = descripcion
        receta.tiempo_preparacion = tiempo_preparacion
        receta.dificultad = dificultad
        receta.porciones = porciones
        receta.ingrediente_id = ingrediente_id
        db.session.commit()

        return {"mensaje": "Receta actualizada exitosamente", "receta": recetas_schema.dump(receta)}

    def delete(self, id_receta):
        receta = Receta.query.get(id_receta)
        if not receta:
            return {"mensaje": "Receta no encontrada"}, 404
        db.session.delete(receta)
        db.session.commit()
        return {"mensaje": "Receta eliminada exitosamente"}


class VistaIngredientes(Resource):
    def get(self):
        ingredientes_con_conteo = []
        for ingrediente in Ingrediente.query.all():
            ingrediente_completo = ingrediente_schema.dump(ingrediente)
            ingrediente_completo["cantidad_recetas"] = len(ingrediente.recetas)
            ingredientes_con_conteo.append(ingrediente_completo)
        return ingredientes_con_conteo

    def post(self):
        try:
            nombre = request.json["nombre"]
            tipo = request.json["tipo"]
            unidad_medida = request.json["unidad_medida"].capitalize()
            disponible = bool(request.json.get("disponible", True))
        except (KeyError, ValueError):
            return {"mensaje": "Datos inválidos para crear el ingrediente"}, 400

        if Ingrediente.query.filter_by(nombre=nombre).first() is not None:
            return {"mensaje": "Ya existe un ingrediente con ese nombre"}, 400

        nuevo_ingrediente = Ingrediente(
            nombre=nombre, tipo=tipo, unidad_medida=unidad_medida, disponible=disponible
        )
        db.session.add(nuevo_ingrediente)
        db.session.commit()

        return {
            "mensaje": "Ingrediente creado exitosamente",
            "ingrediente": ingrediente_schema.dump(nuevo_ingrediente),
        }, 201


class VistaIngrediente(Resource):
    def get(self, id_ingrediente):
        ingrediente = Ingrediente.query.get(id_ingrediente)
        if not ingrediente:
            return {"mensaje": "Ingrediente no encontrado"}, 404
        ingrediente_completo = ingrediente_schema.dump(ingrediente)
        ingrediente_completo["cantidad_recetas"] = len(ingrediente.recetas)
        return ingrediente_completo

    def put(self, id_ingrediente):
        ingrediente = Ingrediente.query.get(id_ingrediente)
        if not ingrediente:
            return {"mensaje": "Ingrediente no encontrado"}, 404
        try:
            nombre = request.json["nombre"]
            tipo = request.json["tipo"]
            unidad_medida = request.json["unidad_medida"].capitalize()
            disponible = bool(request.json.get("disponible", True))
        except (KeyError, ValueError):
            return {"mensaje": "Datos inválidos para actualizar el ingrediente"}, 400

        ingrediente.nombre = nombre
        ingrediente.tipo = tipo
        ingrediente.unidad_medida = unidad_medida
        ingrediente.disponible = disponible
        db.session.commit()

        return {
            "mensaje": "Ingrediente actualizado exitosamente",
            "ingrediente": ingrediente_schema.dump(ingrediente),
        }

    def delete(self, id_ingrediente):
        ingrediente = Ingrediente.query.get(id_ingrediente)
        if ingrediente is None:
            return {"mensaje": "Ingrediente no encontrado"}, 404
        if len(ingrediente.recetas) > 0:
            return {"mensaje": "No se puede eliminar el ingrediente porque tiene recetas asociadas"}, 400
        db.session.delete(ingrediente)
        db.session.commit()
        return {"mensaje": "Ingrediente eliminado exitosamente"}


class VistaReporte(Resource):
    def get(self):
        ingredientes = Ingrediente.query.all()
        reporte_ingredientes = []
        ingrediente_mas_popular = None
        max_recetas = -1

        for ingrediente in ingredientes:
            recetas_del_ingrediente = Receta.query.filter_by(ingrediente_id=ingrediente.id).all()
            total_recetas = len(recetas_del_ingrediente)
            promedio = (
                sum(r.tiempo_preparacion for r in recetas_del_ingrediente) / total_recetas
                if total_recetas else 0
            )
            reporte_ingredientes.append({
                "ingrediente": {
                    "id": ingrediente.id,
                    "nombre": ingrediente.nombre,
                    "tipo": ingrediente.tipo.name if ingrediente.tipo else None,
                },
                "totalRecetas": total_recetas,
                "promedio": round(promedio, 1),
            })
            if total_recetas > max_recetas:
                max_recetas = total_recetas
                ingrediente_mas_popular = ingrediente.nombre

        return {
            "resumen": {
                "totalRecetasSistema": Receta.query.count(),
                "totalIngredientes": len(ingredientes),
                "ingredienteMasPopular": ingrediente_mas_popular,
            },
            "reporteIngredientes": reporte_ingredientes,
        }
