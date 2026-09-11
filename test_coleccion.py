# backend/test_coleccion.py

class TestColeccionEliminarIngrediente(unittest.TestCase):

    def setUp(self):
        self.coleccion = Coleccion()
        self.fake = Faker('es_ES')
        self.app_context = app.app_context()
        self.app_context.push()
        Ingrediente.query.delete()
        Receta.query.delete()
        db.session.commit()

    def tearDown(self):
        Ingrediente.query.delete()
        Receta.query.delete()
        db.session.commit()
        self.app_context.pop()

    def test_eliminar_ingrediente_sin_recetas(self):
        ingrediente = self.coleccion.agregarIngrediente(
            nombre=self.fake.unique.name(),
            tipo="Proteína",
            unidad_medida="Gramos",
            disponible=True
        )
        ingrediente_id = ingrediente.id
        self.assertEqual(Ingrediente.query.count(), 1)

        resultado = self.coleccion.eliminarIngrediente(ingrediente_id)

        self.assertTrue(resultado, "El resultado debe ser True")
        self.assertEqual(Ingrediente.query.count(), 0, "No debe quedar ningún ingrediente")
        self.assertIsNone(Ingrediente.query.get(ingrediente_id), "El ingrediente no debe existir")

    def test_eliminar_ingrediente_con_recetas_asociadas(self):
        ingrediente = self.coleccion.agregarIngrediente(
            nombre=self.fake.unique.name(),
            tipo="Proteína",
            unidad_medida="Gramos",
            disponible=True
        )
        
        self.coleccion.agregarReceta(
            nombre=f"Receta {self.fake.unique.name()}",
            descripcion="Receta de prueba",
            tiempo_preparacion=20,
            dificultad="Fácil",
            porciones=2,
            ingrediente_id=ingrediente.id
        )
        self.assertEqual(Ingrediente.query.count(), 1)
        self.assertEqual(Receta.query.count(), 1)

        resultado = self.coleccion.eliminarIngrediente(ingrediente.id)

        self.assertFalse(resultado, "El resultado debe ser False (no se puede eliminar)")
        self.assertEqual(Ingrediente.query.count(), 1, "El ingrediente debe seguir existiendo")

    def test_eliminar_ingrediente_inexistente(self):

        self.assertEqual(Ingrediente.query.count(), 0)

        resultado = self.coleccion.eliminarIngrediente(99999)

        self.assertFalse(resultado, "El resultado debe ser False")

    def test_eliminar_ingrediente_retorna_booleano(self):
        ingrediente = self.coleccion.agregarIngrediente(
            nombre=self.fake.unique.name(),
            tipo="Vegetal",
            unidad_medida="Unidades",
            disponible=True
        )

        resultado = self.coleccion.eliminarIngrediente(ingrediente.id)

        self.assertIsInstance(resultado, bool, "Debe retornar un booleano")

    def test_eliminar_ingrediente_libera_memoria(self):
        nombre1 = self.fake.unique.name()
        nombre2 = self.fake.unique.name()
        ing1 = self.coleccion.agregarIngrediente(nombre1, "Proteína", "Gramos", True)
        ing2 = self.coleccion.agregarIngrediente(nombre2, "Vegetal", "Unidades", True)

        self.coleccion.eliminarIngrediente(ing1.id)

        listado = self.coleccion.darIngrediente()
        nombres = [i["nombre"] for i in listado]
        self.assertNotIn(nombre1, nombres, "El ingrediente eliminado no debe aparecer")
        self.assertIn(nombre2, nombres, "El ingrediente no eliminado debe seguir")
        self.assertEqual(Ingrediente.query.count(), 1)
