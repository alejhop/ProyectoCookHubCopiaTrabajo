import unittest
from unittest.mock import patch
from app import app

VISTA_RECETAS_URL = "/api/recetas"


class TestVistaRecetas(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def tearDown(self):
        """
        Docstring for tearDown
        Aquí va código que se quiere ejecutar después de que termine
        el test y sirve por ej para limpiar la BD, borrar archivos,
        cerrar conexiones, etc
        :param self: Description
        """
        pass

    def test_retorna_200_no_hay_recetas(self):
        resp = self.client.get(VISTA_RECETAS_URL)
        self.assertEqual(resp.status_code, 200)

    def test_retorna_json_con_lista_vacia_cuando_no_hay_recetas(self):
        with patch("vistas.vistas.recetas", []):
            resp = self.client.get(VISTA_RECETAS_URL)
            marcas = resp.json
            self.assertIsInstance(marcas, list)
            self.assertEqual(len(marcas), 0)
