# backend/tests/test_coleccion.py


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

    def _generar_tipo_aleatorio(self):
        return random.choice([
            "Proteína", "Carbohidrato", "Vegetal",
            "Lácteo", "Fruta", "Condimento"
        ])

    def _generar_unidad_aleatoria(self):
        return random.choice([
            "Gramos", "Kilogramos", "Unidades",
            "Litros", "Mililitros", "Cucharadas"
        ])

    def test_eliminar_ingrediente_sin_recetas(self):
        nombre_aleatorio = self.fake.unique.name()
        ingrediente = self.coleccion.agregarIngrediente(
            nombre=nombre_aleatorio,
            tipo=self._generar_tipo_aleatorio(),
            unidad_medida=self._generar_unidad_aleatoria(),
            disponible=self.fake.boolean()
        )
        ingrediente_id = ingrediente.id
        self.assertEqual(Ingrediente.query.count(), 1)

        resultado = self.coleccion.eliminarIngrediente(ingrediente_id)

        self.assertTrue(resultado, "El resultado debe ser True")
        self.assertEqual(Ingrediente.query.count(), 0, "No debe quedar ningún ingrediente")
        self.assertIsNone(Ingrediente.query.get(ingrediente_id), "El ingrediente no debe existir")
        listado = self.coleccion.darIngrediente()
        nombres = [i["nombre"] for i in listado]
        self.assertNotIn(nombre_aleatorio, nombres, "El ingrediente eliminado no debe aparecer")

    def test_eliminar_ingrediente_con_recetas_asociadas(self):
        nombre_ingrediente = self.fake.unique.name()
        ingrediente = self.coleccion.agregarIngrediente(
            nombre=nombre_ingrediente,
            tipo=self._generar_tipo_aleatorio(),
            unidad_medida=self._generar_unidad_aleatoria(),
            disponible=True
        )
        
        nombre_receta = f"Receta {self.fake.unique.name()}"
        self.coleccion.agregarReceta(
            nombre=nombre_receta,
            descripcion=self.fake.text(max_nb_chars=100),
            tiempo_preparacion=self.fake.random_int(min=5, max=120),
            dificultad=random.choice(["Fácil", "Medio", "Difícil"]),
            porciones=self.fake.random_int(min=1, max=10),
            ingrediente_id=ingrediente.id
        )
        self.assertEqual(Ingrediente.query.count(), 1)
        self.assertEqual(Receta.query.count(), 1)

        resultado = self.coleccion.eliminarIngrediente(ingrediente.id)

        self.assertFalse(resultado, "El resultado debe ser False (no se puede eliminar)")
        self.assertEqual(Ingrediente.query.count(), 1, "El ingrediente debe seguir existiendo")
        self.assertIsNotNone(Ingrediente.query.get(ingrediente.id), "El ingrediente debe existir")

    def test_eliminar_ingrediente_inexistente(self):

        self.assertEqual(Ingrediente.query.count(), 0)
        id_inexistente = self.fake.random_int(min=10000, max=99999)

        resultado = self.coleccion.eliminarIngrediente(id_inexistente)

        self.assertFalse(resultado, "El resultado debe ser False")

    def test_eliminar_ingrediente_retorna_booleano(self):

        ingrediente = self.coleccion.agregarIngrediente(
            nombre=self.fake.unique.name(),
            tipo=self._generar_tipo_aleatorio(),
            unidad_medida=self._generar_unidad_aleatoria(),
            disponible=self.fake.boolean()
        )

        resultado = self.coleccion.eliminarIngrediente(ingrediente.id)

        self.assertIsInstance(resultado, bool, "Debe retornar un booleano")

    def test_eliminar_ingrediente_libera_memoria(self):

        nombres_creados = []
        ids_creados = []
        for _ in range(3):
            nombre = self.fake.unique.name()
            ing = self.coleccion.agregarIngrediente(
                nombre=nombre,
                tipo=self._generar_tipo_aleatorio(),
                unidad_medida=self._generar_unidad_aleatoria(),
                disponible=self.fake.boolean()
            )
            nombres_creados.append(nombre)
            ids_creados.append(ing.id)

        self.assertEqual(Ingrediente.query.count(), 3)

        self.coleccion.eliminarIngrediente(ids_creados[0])

        self.assertEqual(Ingrediente.query.count(), 2)
        listado = self.coleccion.darIngrediente()
        nombres_actuales = [i["nombre"] for i in listado]
        self.assertNotIn(nombres_creados[0], nombres_actuales, "El eliminado no debe aparecer")
        self.assertIn(nombres_creados[1], nombres_actuales, "El segundo debe seguir")
        self.assertIn(nombres_creados[2], nombres_actuales, "El tercero debe seguir")

    def test_eliminar_multiples_ingredientes_aleatorios(self):

        ids_creados = []
        for _ in range(5):
            ing = self.coleccion.agregarIngrediente(
                nombre=self.fake.unique.name(),
                tipo=self._generar_tipo_aleatorio(),
                unidad_medida=self._generar_unidad_aleatoria(),
                disponible=self.fake.boolean()
            )
            ids_creados.append(ing.id)

        self.assertEqual(Ingrediente.query.count(), 5)

        ids_a_eliminar = random.sample(ids_creados, 3)
        for id_ing in ids_a_eliminar:
            resultado = self.coleccion.eliminarIngrediente(id_ing)
            self.assertTrue(resultado, f"Debe eliminarse el ingrediente {id_ing}")

        self.assertEqual(Ingrediente.query.count(), 2)

        for id_eliminado in ids_a_eliminar:
            self.assertIsNone(Ingrediente.query.get(id_eliminado),
                              f"El ingrediente {id_eliminado} no debe existir")
