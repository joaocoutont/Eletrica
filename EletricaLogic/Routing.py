# Logica de Roteamento Automatico de Eletrodutos
import FreeCAD
import Draft
from EletricaLogic.Conduit import ConduitManager

class AutoRouter:
    @staticmethod
    def connect_in_sequence(objects):
        """Conecta uma lista de objetos em sequencia com eletrodutos"""
        if len(objects) < 2: return
        
        for i in range(len(objects) - 1):
            p1 = objects[i].Placement.Base
            p2 = objects[i+1].Placement.Base
            
            # Criar trajetoria (pode ser uma linha reta ou com desvio)
            points = [p1, p2]
            ConduitManager.create_conduit(points)
            
        FreeCAD.ActiveDocument.recompute()

    @staticmethod
    def connect_to_nearest_ceiling(device_objs):
        """Conecta cada dispositivo ao ponto de luz de teto mais proximo"""
        doc = FreeCAD.ActiveDocument
        lights = [obj for obj in doc.Objects if "Luz" in obj.Label or "Lampada" in obj.Label]
        
        if not lights:
            FreeCAD.Console.PrintWarning("Nenhum ponto de luz no teto encontrado para conexao.\n")
            return
            
        for dev in device_objs:
            p_dev = dev.Placement.Base
            
            # Encontrar luz mais proxima (distancia 2D)
            nearest_light = min(lights, key=lambda l: (l.Placement.Base - p_dev).Length)
            p_light = nearest_light.Placement.Base
            
            # Trajetoria com subida vertical
            # 1. Ponto na tomada
            # 2. Ponto na mesma vertical, na altura do teto
            # 3. Ponto na luz
            p_top = FreeCAD.Vector(p_dev.x, p_dev.y, p_light.z)
            points = [p_dev, p_top, p_light]
            
            ConduitManager.create_conduit(points)
            
        doc.recompute()
