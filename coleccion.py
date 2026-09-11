# backend/logica/coleccion.py

def eliminarIngrediente(self, ingrediente_id):
    ingrediente = Ingrediente.query.get(ingrediente_id)
    if ingrediente is None:
        return False
    
    if len(ingrediente.recetas) > 0:
        return False
    
    db.session.delete(ingrediente)
    db.session.commit()
    
    return True
