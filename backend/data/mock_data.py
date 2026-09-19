# Datos mock para CookHub - Sistema de Gestión Culinaria

ingredientes = [
    {"id": 1, "nombre": "Pollo", "tipo": "Proteína", "unidad_medida": "gramos", "disponible": True},
    {"id": 2, "nombre": "Arroz", "tipo": "Carbohidrato", "unidad_medida": "gramos", "disponible": True},
    {"id": 3, "nombre": "Tomate", "tipo": "Vegetal", "unidad_medida": "unidades", "disponible": True},
    {"id": 4, "nombre": "Queso", "tipo": "Lácteo", "unidad_medida": "gramos", "disponible": True},
    {"id": 5, "nombre": "Pasta", "tipo": "Carbohidrato", "unidad_medida": "gramos", "disponible": True}
]

recetas = [
    {"id": 1, "nombre": "Pollo a la Plancha", "descripcion": "Pollo jugoso cocinado a la plancha con especias", "tiempo_preparacion": 25, "dificultad": "Fácil", "porciones": 4, "ingrediente_id": 1},
    {"id": 2, "nombre": "Arroz con Pollo", "descripcion": "Tradicional arroz amarillo con pollo y vegetales", "tiempo_preparacion": 45, "dificultad": "Medio", "porciones": 6, "ingrediente_id": 2},
    {"id": 3, "nombre": "Ensalada Caprese", "descripcion": "Ensalada fresca con tomate, mozzarella y albahaca", "tiempo_preparacion": 15, "dificultad": "Fácil", "porciones": 2, "ingrediente_id": 3},
    {"id": 4, "nombre": "Lasaña de Queso", "descripcion": "Lasaña cremosa con múltiples capas de queso", "tiempo_preparacion": 90, "dificultad": "Difícil", "porciones": 8, "ingrediente_id": 4},
    {"id": 5, "nombre": "Pasta Carbonara", "descripcion": "Pasta cremosa con huevo, queso y panceta", "tiempo_preparacion": 20, "dificultad": "Medio", "porciones": 4, "ingrediente_id": 5},
    {"id": 6, "nombre": "Pollo al Curry", "descripcion": "Pollo en salsa de curry con especias aromáticas", "tiempo_preparacion": 35, "dificultad": "Medio", "porciones": 4, "ingrediente_id": 1},
    {"id": 7, "nombre": "Risotto de Queso", "descripcion": "Arroz cremoso con queso parmesano", "tiempo_preparacion": 40, "dificultad": "Difícil", "porciones": 4, "ingrediente_id": 2}
]

# Datos mock para reporte de ingredientes por popularidad
reporte_ingredientes = {
    "resumen": {
        "totalRecetasSistema": 7,
        "totalIngredientes": 5,
        "ingredienteMasPopular": "Pollo"
    },
    "reporteIngredientes": [
        {
            "ingrediente": {"id": 1, "nombre": "Pollo", "tipo": "Proteína"},
            "totalRecetas": 2,
            "promedio": 30.0
        },
        {
            "ingrediente": {"id": 2, "nombre": "Arroz", "tipo": "Carbohidrato"},
            "totalRecetas": 2,
            "promedio": 42.5
        },
        {
            "ingrediente": {"id": 4, "nombre": "Queso", "tipo": "Lácteo"},
            "totalRecetas": 1,
            "promedio": 90.0
        },
        {
            "ingrediente": {"id": 5, "nombre": "Pasta", "tipo": "Carbohidrato"},
            "totalRecetas": 1,
            "promedio": 20.0
        },
        {
            "ingrediente": {"id": 3, "nombre": "Tomate", "tipo": "Vegetal"},
            "totalRecetas": 1,
            "promedio": 15.0
        }
    ]
}