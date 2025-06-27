# Arquivo: backend/core/tests.py

from django.test import TestCase


# Exemplo de teste básico para evitar o erro F401
class MySimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


# Adicione seus testes de modelos e views aqui conforme o desenvolvimento
