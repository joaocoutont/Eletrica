import unittest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock FreeCAD if necessary, but i18n should handle its absence
from EletricaLogic.i18n import Translate, tr

class TestI18n(unittest.TestCase):
    
    def test_default_translation(self):
        # Como não temos FreeCAD ativo, deve cair no pt-BR (padrão)
        self.assertEqual(tr("Dashboard"), "Painel de Controle")
        self.assertEqual(tr("Projeto"), "Projeto Elétrico")

    def test_explicit_translation(self):
        # Forçar en-US
        self.assertEqual(Translate.tr("Dashboard", lang="en-US"), "Dashboard")
        self.assertEqual(Translate.tr("Projeto", lang="en-US"), "Electrical Project")
        
        # Forçar es-ES
        self.assertEqual(Translate.tr("Dashboard", lang="es-ES"), "Panel de Control")

    def test_fallback_missing_key(self):
        # Chave inexistente deve retornar ela mesma
        self.assertEqual(tr("ChaveInexistente"), "ChaveInexistente")

    def test_fallback_to_default_lang(self):
        # Simular uma tradução faltando no en-US mas presente no pt-BR
        # Para este teste, vamos adicionar temporariamente uma chave
        Translate.LANGUAGES["pt-BR"]["TesteFallback"] = "Sucesso"
        if "TesteFallback" in Translate.LANGUAGES["en-US"]:
            del Translate.LANGUAGES["en-US"]["TesteFallback"]
            
        self.assertEqual(Translate.tr("TesteFallback", lang="en-US"), "Sucesso")

if __name__ == "__main__":
    unittest.main()
