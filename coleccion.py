# backend/logica/coleccion.py

#---------------------------------------------------------ELIMINAR

def eliminarIngrediente(self, ingrediente_id):
    ingrediente = Ingrediente.query.get(ingrediente_id)
    if ingrediente is None:
        return False
    
    if len(ingrediente.recetas) > 0:
        return False
    
    db.session.delete(ingrediente)
    db.session.commit()
    
    return True

#---------------------------------------------------------ELIMINAR


#---------------------------------------------------------POPULARIDAD

def generarReportePopularidad(self):

    todos_los_ingredientes = Ingrediente.query.all()
    
    ingredientes_reporte = []
    for ingrediente in todos_los_ingredientes:
        total_recetas = Receta.query.filter_by(
            ingrediente_id=ingrediente.id
        ).count()
        
        ingredientes_reporte.append({
            "id": ingrediente.id,
            "nombre": ingrediente.nombre,
            "tipo": ingrediente.tipo.name if ingrediente.tipo else None,
            "unidad_medida": ingrediente.unidad_medida.name if ingrediente.unidad_medida else None,
            "disponible": ingrediente.disponible,
            "total_recetas": total_recetas
        })
    
    total_recetas_sistema = Receta.query.count()
    
    return {
        "total_ingredientes": len(todos_los_ingredientes),
        "total_recetas_sistema": total_recetas_sistema,
        "ingredientes": ingredientes_reporte
    }
#---------------------------------------------------------POPULARIDAD
