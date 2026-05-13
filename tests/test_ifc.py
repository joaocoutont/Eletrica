import unittest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock FreeCAD objects for testing
class MockObject:
    def __init__(self, label, tipo_bim=None, potencia=None):
        self.Label = label
        self.Name = label.replace(" ", "_")
        if tipo_bim: self.TipoBIM = tipo_bim
        if potencia: self.Potencia = potencia
        self._props = {}

    def addProperty(self, prop_type, name, group, desc):
        self._props[name] = {"type": prop_type, "group": group, "desc": desc}
        setattr(self, name, None)
        return self

    def hasattr(self, name):
        return hasattr(self, name)

class MockDoc:
    def __init__(self):
        self.Objects = []
    def getObject(self, name):
        for o in self.Objects:
            if o.Name == name: return o
        return None

class TestIFCIntegration(unittest.TestCase):
    
    def test_property_mapping_logic(self):
        # Como o IFC.py importa FreeCAD, precisamos mockar o módulo se estivermos fora dele
        # Mas aqui vamos testar a lógica de mapeamento indiretamente ou garantir que o arquivo carrega
        try:
            from EletricaLogic.IFC import IFC_TYPE_MAP, PROP_MAP
            self.assertIn("Tomada", IFC_TYPE_MAP)
            self.assertEqual(IFC_TYPE_MAP["Tomada"][0], "IfcOutlet")
            
            self.assertIn("Potencia", PROP_MAP)
            self.assertEqual(PROP_MAP["Potencia"][0], "NominalPower")
        except ImportError:
            self.skipTest("FreeCAD module not available for full integration test")

if __name__ == "__main__":
    unittest.main()
