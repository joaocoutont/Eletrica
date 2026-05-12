# Logica de Fiacao e Comprimento de Cabos
import FreeCAD
from EletricaLogic.Calculator import ElectricalCalculator
from EletricaLogic.Settings import ProjectSettings

class WiringManager:
    @staticmethod
    def calculate_circuit_lengths():
        """
        Calcula o comprimento total de cabos por circuito baseado nos eletrodutos.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return {}
        
        circuit_lengths = {}
        
        for obj in doc.Objects:
            # Verifica se e um eletroduto com circuitos definidos
            if hasattr(obj, "CircuitosPassantes") and hasattr(obj, "Shape"):
                length = obj.Shape.Length
                for circuit in obj.CircuitosPassantes:
                    if circuit not in circuit_lengths:
                        circuit_lengths[circuit] = 0.0
                    circuit_lengths[circuit] += length
                    
        return circuit_lengths

    @staticmethod
    def check_voltage_drop(circuit_name, current, section, length):
        """
        Verifica se a queda de tensao esta dentro dos limites (ex: 3%)
        """
        voltage = ProjectSettings.get_voltage()
        drop_percent = ElectricalCalculator.calculate_voltage_drop(current, length/1000.0, section, voltage)
        
        is_ok = drop_percent <= 3.0 # Limite de 3% para circuitos terminais
        return drop_percent, is_ok
