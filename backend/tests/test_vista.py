import os
import random
import unittest

from faker import Faker

os.environ.setdefault("COOKHUB_DATABASE_URL", "sqlite:///test_cookhub.db")

from controlador.controlador import app
from modelo import db, Receta, Ingrediente
from vista import (
    VistaRecetas,
    VistaReceta,
    VistaIngredientes,
    VistaIngrediente,
    VistaReporte,
)


def _resultado(valor):
    """Normaliza el retorno de un método de vista a (cuerpo, status)."""
    if isinstance(valor, tuple):
        return valor[0], valor[1]
    return valor, 200


def _tipo_aleatorio():
    return random.choice(
        ["Proteína", "Carbohidrato", "Vegetal", "Lácteo", "Fruta", "Condimento"]
    )


def _unidad_aleatoria():
    return random.choice(
        ["Gramos", "Kilogramos", "Unidades", "Litros", "Mililitros", "Cucharadas"]
    )


class VistaTestCase(unittest.TestCase):
    """Caso base: limpia la base de datos y ofrece helpers para invocar la vista."""

    def setUp(self):
        self.fake = Faker("es_ES")
        self.app_context = app.app_context()
        self.app_context.push()
        Receta.query.delete()
        Ingrediente.query.delete()
        db.session.commit()

    def tearDown(self):
        Receta.query.delete()
        Ingrediente.query.delete()
        db.session.commit()
        self.app_context.pop()

    def crear_ingrediente(self, nombre=None, tipo=None, unidad_medida=None, disponible=True):
        payload = {
            "nombre": nombre or self.fake.unique.name(),
            "tipo": tipo or _tipo_aleatorio(),
            "unidad_medida": unidad_medida or _unidad_aleatoria(),
            "disponible": disponible,
        }
        with app.test_request_context(json=payload, method="POST"):
            return _resultado(VistaIngredientes().post())

    def crear_receta(self, nombre=None, descripcion=None, tiempo_preparacion=None,
                      dificultad=None, porciones=None, ingrediente_id=None):
        payload = {
            "nombre": nombre or self.fake.sentence(nb_words=3),
            "descripcion": descripcion or self.fake.sentence(nb_words=10),
            "tiempo_preparacion": tiempo_preparacion or random.randint(5, 180),
            "dificultad": dificultad or random.choice(["Fácil", "Medio", "Difícil"]),
            "porciones": porciones or random.randint(1, 12),
            "ingrediente_id": ingrediente_id,
        }
        with app.test_request_context(json=payload, method="POST"):
            return _resultado(VistaRecetas().post())


class TestVistaIngredientesListar(VistaTestCase):

    def test_listar_ingredientes_vacio(self):
        with app.test_request_context():
            cuerpo, status = _resultado(VistaIngredientes().get())
        self.assertEqual(status, 200)
        self.assertEqual(cuerpo, [])

    def test_listar_ingredientes(self):
        self.crear_ingrediente(nombre="Pollo")
        self.crear_ingrediente(nombre="Arroz")

        with app.test_request_context():
            ingredientes, status = _resultado(VistaIngredientes().get())

        self.assertEqual(status, 200)
        self.assertIsInstance(ingredientes, list)
        self.assertEqual(len(ingredientes), 2)
        nombres = [i["nombre"] for i in ingredientes]
        self.assertIn("Pollo", nombres)
        self.assertIn("Arroz", nombres)
        for ingrediente in ingredientes:
            self.assertEqual(ingrediente["cantidad_recetas"], 0)


class TestVistaRecetas(VistaTestCase):

    def test_agregar_receta(self):
        ingrediente, _ = self.crear_ingrediente()

        cuerpo, status = self.crear_receta(
            nombre="Sopa de prueba", ingrediente_id=ingrediente["ingrediente"]["id"]
        )

        self.assertEqual(status, 201)
        self.assertEqual(cuerpo["receta"]["nombre"], "Sopa de prueba")
        self.assertEqual(Receta.query.count(), 1)

    def test_agregar_receta_con_datos_aleatorios(self):
        ingrediente, _ = self.crear_ingrediente()
        ingrediente_id = ingrediente["ingrediente"]["id"]

        nombre_aleatorio = self.fake.sentence(nb_words=3)
        descripcion_aleatoria = self.fake.sentence(nb_words=10)
        tiempo_preparacion_aleatorio = random.randint(5, 180)
        dificultad_aleatoria = random.choice(["Fácil", "Medio", "Difícil"])
        porciones_aleatorias = random.randint(1, 12)

        cuerpo, status = self.crear_receta(
            nombre=nombre_aleatorio,
            descripcion=descripcion_aleatoria,
            tiempo_preparacion=tiempo_preparacion_aleatorio,
            dificultad=dificultad_aleatoria,
            porciones=porciones_aleatorias,
            ingrediente_id=ingrediente_id,
        )

        self.assertEqual(status, 201)
        receta = cuerpo["receta"]
        self.assertEqual(receta["nombre"], nombre_aleatorio)
        self.assertEqual(receta["descripcion"], descripcion_aleatoria)
        self.assertEqual(receta["tiempo_preparacion"], tiempo_preparacion_aleatorio)
        self.assertEqual(receta["dificultad"], dificultad_aleatoria)
        self.assertEqual(receta["porciones"], porciones_aleatorias)
        self.assertEqual(receta["ingrediente_id"], ingrediente_id)

        receta_db = Receta.query.filter_by(nombre=nombre_aleatorio).first()
        self.assertIsNotNone(receta_db, "La receta debe estar en la base de datos")
        self.assertEqual(Receta.query.count(), 1)

    def test_agregar_receta_con_ingrediente_inexistente(self):
        cuerpo, status = self.crear_receta(ingrediente_id=999999)
        self.assertEqual(status, 400)
        self.assertEqual(Receta.query.count(), 0)

    def test_agregar_receta_con_datos_invalidos(self):
        with app.test_request_context(json={"nombre": "Incompleta"}, method="POST"):
            cuerpo, status = _resultado(VistaRecetas().post())
        self.assertEqual(status, 400)

    def test_listar_recetas(self):
        ingrediente_a, _ = self.crear_ingrediente()
        ingrediente_b, _ = self.crear_ingrediente()
        self.crear_receta(nombre="Receta A", ingrediente_id=ingrediente_a["ingrediente"]["id"])
        self.crear_receta(nombre="Receta B", ingrediente_id=ingrediente_b["ingrediente"]["id"])

        with app.test_request_context():
            recetas, status = _resultado(VistaRecetas().get())

        self.assertEqual(status, 200)
        self.assertIsInstance(recetas, list)
        nombres = [r["nombre"] for r in recetas]
        self.assertIn("Receta A", nombres)
        self.assertIn("Receta B", nombres)


class TestVistaAgregarIngrediente(VistaTestCase):

    def test_agregar_ingrediente_con_datos_aleatorios(self):
        nombre_aleatorio = self.fake.unique.name()
        tipo_aleatorio = _tipo_aleatorio()
        unidad_aleatoria = _unidad_aleatoria()
        disponible_aleatorio = self.fake.boolean()

        cuerpo, status = self.crear_ingrediente(
            nombre=nombre_aleatorio,
            tipo=tipo_aleatorio,
            unidad_medida=unidad_aleatoria,
            disponible=disponible_aleatorio,
        )

        self.assertEqual(status, 201)
        ingrediente = cuerpo["ingrediente"]
        self.assertEqual(ingrediente["nombre"], nombre_aleatorio)
        self.assertEqual(ingrediente["tipo"], tipo_aleatorio)
        self.assertEqual(ingrediente["unidad_medida"], unidad_aleatoria)
        self.assertEqual(ingrediente["disponible"], disponible_aleatorio)

        ingrediente_db = Ingrediente.query.filter_by(nombre=nombre_aleatorio).first()
        self.assertIsNotNone(ingrediente_db, "El ingrediente debe estar en la base de datos")
        self.assertEqual(Ingrediente.query.count(), 1)

    def test_agregar_multiples_ingredientes_aleatorios(self):
        creados = 0
        for _ in range(5):
            _, status = self.crear_ingrediente()
            if status == 201:
                creados += 1

        self.assertEqual(creados, 5, "Deben crearse 5 ingredientes")
        self.assertEqual(Ingrediente.query.count(), 5, "Deben haber 5 ingredientes en BD")

    def test_agregar_ingrediente_nombre_duplicado(self):
        nombre = self.fake.unique.name()
        self.crear_ingrediente(nombre=nombre, tipo="Proteína", unidad_medida="Gramos")

        _, status = self.crear_ingrediente(
            nombre=nombre, tipo="Vegetal", unidad_medida="Unidades", disponible=False
        )

        self.assertEqual(status, 400)
        self.assertEqual(Ingrediente.query.count(), 1, "Solo debe haber 1 ingrediente")


class TestVistaReporte(VistaTestCase):

    def _crear_ingrediente_y_recetas(self, num_recetas):
        ingrediente, _ = self.crear_ingrediente()
        ingrediente = ingrediente["ingrediente"]

        for i in range(num_recetas):
            self.crear_receta(
                nombre=f"Receta {i} - {self.fake.unique.name()}",
                ingrediente_id=ingrediente["id"],
            )

        return ingrediente

    def test_reporte_incluye_total_ingredientes(self):
        for _ in range(3):
            self.crear_ingrediente()

        with app.test_request_context():
            reporte, status = _resultado(VistaReporte().get())

        self.assertEqual(status, 200)
        self.assertIn("resumen", reporte)
        self.assertEqual(reporte["resumen"]["totalIngredientes"], 3)

    def test_reporte_incluye_total_recetas_por_ingrediente(self):
        ing_con_2_recetas = self._crear_ingrediente_y_recetas(num_recetas=2)
        ing_con_0_recetas = self._crear_ingrediente_y_recetas(num_recetas=0)
        ing_con_1_receta = self._crear_ingrediente_y_recetas(num_recetas=1)

        with app.test_request_context():
            reporte, _ = _resultado(VistaReporte().get())

        totales = {
            item["ingrediente"]["nombre"]: item["totalRecetas"]
            for item in reporte["reporteIngredientes"]
        }

        self.assertEqual(totales[ing_con_2_recetas["nombre"]], 2)
        self.assertEqual(totales[ing_con_0_recetas["nombre"]], 0)
        self.assertEqual(totales[ing_con_1_receta["nombre"]], 1)

    def test_reporte_incluye_listado_de_ingredientes(self):
        nombres_creados = []
        for _ in range(5):
            cuerpo, _ = self.crear_ingrediente()
            nombres_creados.append(cuerpo["ingrediente"]["nombre"])

        with app.test_request_context():
            reporte, _ = _resultado(VistaReporte().get())

        self.assertIn("reporteIngredientes", reporte)
        self.assertEqual(len(reporte["reporteIngredientes"]), 5)

        nombres_reporte = [item["ingrediente"]["nombre"] for item in reporte["reporteIngredientes"]]
        for nombre in nombres_creados:
            self.assertIn(nombre, nombres_reporte)


class TestVistaEliminarIngrediente(VistaTestCase):

    def test_eliminar_ingrediente_sin_recetas(self):
        cuerpo, _ = self.crear_ingrediente()
        ingrediente = cuerpo["ingrediente"]
        self.assertEqual(Ingrediente.query.count(), 1)

        with app.test_request_context(method="DELETE"):
            _, status = _resultado(VistaIngrediente().delete(ingrediente["id"]))

        self.assertEqual(status, 200)
        self.assertEqual(Ingrediente.query.count(), 0)
        self.assertIsNone(Ingrediente.query.get(ingrediente["id"]))

        with app.test_request_context():
            listado, _ = _resultado(VistaIngredientes().get())
        nombres = [i["nombre"] for i in listado]
        self.assertNotIn(ingrediente["nombre"], nombres)

    def test_eliminar_ingrediente_con_recetas_asociadas(self):
        cuerpo, _ = self.crear_ingrediente()
        ingrediente = cuerpo["ingrediente"]
        self.crear_receta(ingrediente_id=ingrediente["id"])
        self.assertEqual(Ingrediente.query.count(), 1)
        self.assertEqual(Receta.query.count(), 1)

        with app.test_request_context(method="DELETE"):
            _, status = _resultado(VistaIngrediente().delete(ingrediente["id"]))

        self.assertEqual(status, 400)
        self.assertEqual(Ingrediente.query.count(), 1, "El ingrediente debe seguir existiendo")
        self.assertIsNotNone(Ingrediente.query.get(ingrediente["id"]))

    def test_eliminar_ingrediente_inexistente(self):
        with app.test_request_context(method="DELETE"):
            _, status = _resultado(VistaIngrediente().delete(999999))
        self.assertEqual(status, 404)


class TestVistaRecetaDetalle(VistaTestCase):

    def test_obtener_receta_por_id(self):
        cuerpo_ingrediente, _ = self.crear_ingrediente()
        ingrediente_id = cuerpo_ingrediente["ingrediente"]["id"]
        cuerpo_receta, _ = self.crear_receta(nombre="Receta X", ingrediente_id=ingrediente_id)
        receta_id = cuerpo_receta["receta"]["id"]

        with app.test_request_context():
            receta, status = _resultado(VistaReceta().get(receta_id))

        self.assertEqual(status, 200)
        self.assertEqual(receta["nombre"], "Receta X")
        self.assertEqual(receta["ingrediente"]["id"], ingrediente_id)

    def test_obtener_receta_inexistente(self):
        with app.test_request_context():
            _, status = _resultado(VistaReceta().get(999999))
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
