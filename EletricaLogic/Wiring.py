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

    @staticmethod
    def generate_3d_cables(conduit_obj):
        """Cria os fios fisicos em 3D dentro do eletroduto"""
        if not hasattr(conduit_obj, "CircuitosPassantes") or not conduit_obj.CircuitosPassantes:
            return
            
        import Arch
        import Draft
        doc = FreeCAD.ActiveDocument
        
        # Cores padrao (NBR 5410)
        colors = {"Fase": (0.0, 0.0, 0.0), "Neutro": (0.0, 0.0, 1.0), "Terra": (0.0, 1.0, 0.0)}
        
        points = [v.Point for v in conduit_obj.Shape.Vertexes]
        
        for idx, circuit in enumerate(conduit_obj.CircuitosPassantes):
            for f_idx, (func, color) in enumerate(colors.items()):
                # Criar o cabo (fio fino)
                wire = Draft.make_wire(points, closed=False)
                # Offset leve para nao ficarem um dentro do outro
                wire.Placement.Base += FreeCAD.Vector(idx*1.5, f_idx*1.5, 0)
                
                cable = Arch.makePipe(wire, diameter=2.5) 
                cable.Label = f"Fio_{func}_{circuit}"
                cable.ViewObject.ShapeColor = color
                
        doc.recompute()
        return True
