import os
import random
import unittest
from unittest.mock import patch

from faker import Faker

os.environ.setdefault("COOKHUB_DATABASE_URL", "sqlite:///test_cookhub.db")

from app import app
from modelos import db, Receta, Ingrediente
from logica.coleccion import Coleccion
from data.mock_data import ingredientes



class TestColeccionIngredientes(unittest.TestCase):
    
    def tearDown(self):
        Receta.query.delete()
        Ingrediente.query.delete()
        db.session.commit()
        self.app_context.pop()

    def test_listar_ingredientes(self):
        """Prueba que darIngrediente() devuelva los ingredientes desde la base de datos"""
        ingredientes = self.coleccion.darIngrediente()

        self.assertIsInstance(ingredientes, list)
        self.assertEqual(len(ingredientes), 2)
        nombres = [i["nombre"] for i in ingredientes]
        self.assertIn("Pollo", nombres)
        self.assertIn("Arroz", nombres)
        for ingrediente in ingredientes:
            self.assertEqual(ingrediente["cantidad_recetas"], 0)

class TestColeccionRecetas(unittest.TestCase):


    def setUp(self):
        self.coleccion = Coleccion()
        self.fake = Faker('es_ES')
        self.app_context = app.app_context()
        self.app_context.push()
        Receta.query.delete()
        db.session.commit()

    def tearDown(self):
        """Borra las recetas creadas durante la prueba"""
        Receta.query.delete()
        db.session.commit()
        self.app_context.pop()

  
    def test_agregar_receta(self):
        receta = self.coleccion.agregarReceta(
            nombre="Sopa de prueba",
            descripcion="Sopa creada para la prueba",
            tiempo_preparacion=15,
            dificultad="Fácil",
            porciones=2,
            ingrediente_id=1
        )
        self.assertIsInstance(receta, Receta)
        self.assertEqual(receta.nombre, "Sopa de prueba")
        self.assertEqual(Receta.query.count(), 1)

    def test_agregar_receta_con_datos_aleatorios(self):
        nombre_aleatorio = self.fake.sentence(nb_words=3)
        descripcion_aleatoria = self.fake.sentence(nb_words=10)
        tiempo_preparacion_aleatorio = random.randint(5, 180)
        dificultad_aleatoria = random.choice(["Fácil", "Medio", "Difícil"])
        porciones_aleatorias = random.randint(1, 12)
        ingrediente_id_aleatorio = random.choice([i["id"] for i in ingredientes])

        receta = self.coleccion.agregarReceta(
            nombre=nombre_aleatorio,
            descripcion=descripcion_aleatoria,
            tiempo_preparacion=tiempo_preparacion_aleatorio,
            dificultad=dificultad_aleatoria,
            porciones=porciones_aleatorias,
            ingrediente_id=ingrediente_id_aleatorio
        )

        self.assertIsNotNone(receta, "La receta no debe ser None")
        self.assertIsInstance(receta, Receta)
        self.assertEqual(receta.nombre, nombre_aleatorio)
        self.assertEqual(receta.descripcion, descripcion_aleatoria)
        self.assertEqual(receta.tiempo_preparacion, tiempo_preparacion_aleatorio)
        self.assertEqual(receta.dificultad.name, dificultad_aleatoria)
        self.assertEqual(receta.porciones, porciones_aleatorias)
        self.assertEqual(receta.ingrediente_id, ingrediente_id_aleatorio)

        receta_db = Receta.query.filter_by(nombre=nombre_aleatorio).first()
        self.assertIsNotNone(receta_db, "La receta debe estar en la base de datos")
        self.assertEqual(Receta.query.count(), 1)

    def test_listar_recetas(self):
        """Prueba que darReceta() devuelva las recetas ya creadas"""
        self.coleccion.agregarReceta("Receta A", "desc", 10, "Fácil", 2, 1)
        self.coleccion.agregarReceta("Receta B", "desc", 20, "Medio", 4, 2)

        recetas = self.coleccion.darReceta()

        self.assertIsInstance(recetas, list)
        nombres = [r["nombre"] for r in recetas]
        self.assertIn("Receta A", nombres)
        self.assertIn("Receta B", nombres)






class TestColeccionAgregarIngrediente(unittest.TestCase):
    def setUp(self):
        self.coleccion = Coleccion()
        self.fake = Faker('es_ES')
        self.app_context = app.app_context()
        self.app_context.push()
        Ingrediente.query.delete()
        db.session.commit()
    
    def tearDown(self):
        Ingrediente.query.delete()
        db.session.commit()
        self.app_context.pop()
    
    def test_agregar_ingrediente_con_datos_aleatorios(self):
        nombre_aleatorio = self.fake.unique.name()
        tipo_aleatorio = random.choice([
            "Proteína", "Carbohidrato", "Vegetal", 
            "Lácteo", "Fruta", "Condimento"
        ])
        unidad_aleatoria = random.choice([
            "Gramos", "Kilogramos", "Unidades", 
            "Litros", "Mililitros", "Cucharadas"
        ])
        disponible_aleatorio = self.fake.boolean()
        
        ingrediente = self.coleccion.agregarIngrediente(
            nombre=nombre_aleatorio,
            tipo=tipo_aleatorio,
            unidad_medida=unidad_aleatoria,
            disponible=disponible_aleatorio
        )
        
        self.assertIsNotNone(ingrediente, "El ingrediente no debe ser None")
        self.assertEqual(ingrediente.nombre, nombre_aleatorio)
        self.assertEqual(ingrediente.tipo.name, tipo_aleatorio)
        self.assertEqual(ingrediente.unidad_medida.name, unidad_aleatoria)
        self.assertEqual(ingrediente.disponible, disponible_aleatorio)
        
        ingrediente_db = Ingrediente.query.filter_by(nombre=nombre_aleatorio).first()
        self.assertIsNotNone(ingrediente_db, "El ingrediente debe estar en la base de datos")
        self.assertEqual(Ingrediente.query.count(), 1)
    
    def test_agregar_multiples_ingredientes_aleatorios(self):
        ingredientes_creados = []
        for _ in range(5):
            nombre = self.fake.unique.name()
            tipo = random.choice(["Proteína", "Carbohidrato", "Vegetal"])
            unidad = random.choice(["Gramos", "Unidades", "Mililitros"])
            
            ingrediente = self.coleccion.agregarIngrediente(
                nombre=nombre,
                tipo=tipo,
                unidad_medida=unidad,
                disponible=self.fake.boolean()
            )
            
            if ingrediente:
                ingredientes_creados.append(ingrediente)
        

        self.assertEqual(len(ingredientes_creados), 5, "Deben crearse 5 ingredientes")
        self.assertEqual(Ingrediente.query.count(), 5, "Deben haber 5 ingredientes en BD")
    
    def test_agregar_ingrediente_nombre_duplicado(self):
      
        nombre = self.fake.unique.name()
        self.coleccion.agregarIngrediente(
            nombre=nombre,
            tipo="Proteína",
            unidad_medida="Gramos",
            disponible=True
        )
        
      
        resultado = self.coleccion.agregarIngrediente(
            nombre=nombre,  
            tipo="Vegetal",
            unidad_medida="Unidades",
            disponible=False
        )
 
        self.assertIsNone(resultado, "No debe crear ingrediente con nombre duplicado")
        self.assertEqual(Ingrediente.query.count(), 1, "Solo debe haber 1 ingrediente")


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