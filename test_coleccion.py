# backend/tests/test_coleccion.py

#---------------------------------------------------------------------------------------ELIMINAR
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
#---------------------------------------------------------------------------------------ELIMINAR

#---------------------------------------------------------------------------------------POPULARIDAD
# backend/tests/test_coleccion.py
# AGREGAR ESTA CLASE AL FINAL DEL ARCHIVO


class TestColeccionReportePopularidadParte1(unittest.TestCase):

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

    def _crear_ingrediente_y_recetas(self, num_recetas):
        nombre_ing = self.fake.unique.name()
        ingrediente = self.coleccion.agregarIngrediente(
            nombre=nombre_ing,
            tipo=self._generar_tipo_aleatorio(),
            unidad_medida=self._generar_unidad_aleatoria(),
            disponible=True
        )
        
        for i in range(num_recetas):
            self.coleccion.agregarReceta(
                nombre=f"Receta {i} - {self.fake.unique.name()}",
                descripcion=self.fake.text(max_nb_chars=100),
                tiempo_preparacion=self.fake.random_int(min=5, max=120),
                dificultad=random.choice(["Fácil", "Medio", "Difícil"]),
                porciones=self.fake.random_int(min=1, max=10),
                ingrediente_id=ingrediente.id
            )
        
        return ingrediente


    def test_reporte_incluye_total_ingredientes(self):
        for _ in range(3):
            self.coleccion.agregarIngrediente(
                nombre=self.fake.unique.name(),
                tipo=self._generar_tipo_aleatorio(),
                unidad_medida=self._generar_unidad_aleatoria(),
                disponible=self.fake.boolean()
            )

        reporte = self.coleccion.generarReportePopularidad()

        self.assertIn("total_ingredientes", reporte,
                      "El reporte debe tener 'total_ingredientes'")
        self.assertEqual(reporte["total_ingredientes"], 3,
                         "Debe haber 3 ingredientes en total")

    def test_reporte_incluye_total_recetas_por_ingrediente(self):

        ing_con_2_recetas = self._crear_ingrediente_y_recetas(num_recetas=2)
        ing_con_0_recetas = self._crear_ingrediente_y_recetas(num_recetas=0)
        ing_con_1_receta = self._crear_ingrediente_y_recetas(num_recetas=1)

        reporte = self.coleccion.generarReportePopularidad()

        ingredientes_reporte = {i["nombre"]: i["total_recetas"]
                                for i in reporte["ingredientes"]}
        
        self.assertEqual(ingredientes_reporte[ing_con_2_recetas.nombre], 2,
                         "El primer ingrediente debe tener 2 recetas")
        self.assertEqual(ingredientes_reporte[ing_con_0_recetas.nombre], 0,
                         "El segundo ingrediente debe tener 0 recetas")
        self.assertEqual(ingredientes_reporte[ing_con_1_receta.nombre], 1,
                         "El tercer ingrediente debe tener 1 receta")

    def test_reporte_incluye_listado_de_ingredientes(self):

        nombres_creados = []
        for _ in range(5):
            nombre = self.fake.unique.name()
            self.coleccion.agregarIngrediente(
                nombre=nombre,
                tipo=self._generar_tipo_aleatorio(),
                unidad_medida=self._generar_unidad_aleatoria(),
                disponible=self.fake.boolean()
            )
            nombres_creados.append(nombre)

        reporte = self.coleccion.generarReportePopularidad()

        self.assertIn("ingredientes", reporte,
                      "El reporte debe tener 'ingredientes'")
        self.assertEqual(len(reporte["ingredientes"]), 5,
                         "Debe haber 5 ingredientes en el listado")
        
        nombres_reporte = [i["nombre"] for i in reporte["ingredientes"]]
        for nombre in nombres_creados:
            self.assertIn(nombre, nombres_reporte,
                          f"El ingrediente '{nombre}' debe estar en el reporte")

    def test_reporte_cada_ingrediente_tiene_campos_requeridos(self):

        self.coleccion.agregarIngrediente(
            nombre=self.fake.unique.name(),
            tipo=self._generar_tipo_aleatorio(),
            unidad_medida=self._generar_unidad_aleatoria(),
            disponible=True
        )

        reporte = self.coleccion.generarReportePopularidad()

        self.assertTrue(len(reporte["ingredientes"]) > 0)
        ingrediente = reporte["ingredientes"][0]
        
        campos_requeridos = ["id", "nombre", "tipo", "unidad_medida", "total_recetas"]
        for campo in campos_requeridos:
            self.assertIn(campo, ingrediente,
                          f"Cada ingrediente debe tener el campo '{campo}'")

    def test_reporte_ingrediente_sin_recetas_muestra_cero(self):

        ingrediente = self.coleccion.agregarIngrediente(
            nombre=self.fake.unique.name(),
            tipo=self._generar_tipo_aleatorio(),
            unidad_medida=self._generar_unidad_aleatoria(),
            disponible=True
        )

        reporte = self.coleccion.generarReportePopularidad()

        ing_en_reporte = next(
            i for i in reporte["ingredientes"] if i["id"] == ingrediente.id
        )
        self.assertEqual(ing_en_reporte["total_recetas"], 0,
                         "El ingrediente sin recetas debe mostrar 0")

    def test_reporte_con_base_datos_vacia(self):

        self.assertEqual(Ingrediente.query.count(), 0)

        reporte = self.coleccion.generarReportePopularidad()

        self.assertEqual(reporte["total_ingredientes"], 0,
                         "Debe reportar 0 ingredientes")
        self.assertEqual(len(reporte["ingredientes"]), 0,
                         "La lista debe estar vacía")

    def test_reporte_no_incluye_ingrediente_mas_popular(self):

        self._crear_ingrediente_y_recetas(num_recetas=5)
        self._crear_ingrediente_y_recetas(num_recetas=2)

        reporte = self.coleccion.generarReportePopularidad()

        self.assertNotIn("ingrediente_mas_popular", reporte,
                         "La Parte 1 NO debe incluir el ingrediente más popular")

    def test_reporte_multiples_ingredientes_conteos_correctos(self):

        cantidades = [3, 0, 5, 1, 2]
        ingredientes_creados = []
        
        for cantidad in cantidades:
            ing = self._crear_ingrediente_y_recetas(num_recetas=cantidad)
            ingredientes_creados.append((ing.nombre, cantidad))

        reporte = self.coleccion.generarReportePopularidad()

        for nombre, cantidad_esperada in ingredientes_creados:
            ing_reporte = next(
                i for i in reporte["ingredientes"] if i["nombre"] == nombre
            )
            self.assertEqual(ing_reporte["total_recetas"], cantidad_esperada,
                             f"'{nombre}' debe tener {cantidad_esperada} recetas")
#---------------------------------------------------------------------------------------POPULARIDAD

#Prueba yaml Feature a develop, 6:57pm


