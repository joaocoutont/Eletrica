# Gerenciamento de Quadros e Hierarquia
import FreeCAD

class PanelManager:
    @staticmethod
    def create_panel(name, fed_by=None):
        """Cria um quadro de distribuicao com propriedades de hierarquia"""
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("App::FeaturePython", name)
        obj.Label = name
        
        # Propriedades de Hierarquia
        obj.addProperty("App::PropertyLink", "AlimentadoPor", "Hierarquia", "Quadro que alimenta este quadro")
        if fed_by:
            obj.AlimentadoPor = fed_by
            
        obj.addProperty("App::PropertyFloat", "PotenciaAcumulada", "Eletrica", "Soma das cargas deste quadro e sub-quadros")
        obj.PotenciaAcumulada = 0.0
        
        # Identificador para o sistema saber que e um Quadro
        if not hasattr(obj, "TipoBIM"):
            obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo de componente")
        obj.TipoBIM = "Quadro"
        
        return obj

    @staticmethod
    def recalculate_hierarchy():
        """Soma as cargas de todos os componentes vinculados aos quadros"""
        doc = FreeCAD.ActiveDocument
        
        # 1. Resetar potencias dos quadros
        panels = [o for o in doc.Objects if hasattr(o, "TipoBIM") and o.TipoBIM == "Quadro"]
        for p in panels:
            p.PotenciaAcumulada = 0.0
            
        # 2. Somar cargas terminais vinculadas a cada quadro
        for obj in doc.Objects:
            if hasattr(obj, "Circuito") and hasattr(obj, "Potencia") and hasattr(obj, "QuadroVinculado"):
                if obj.QuadroVinculado:
                    obj.QuadroVinculado.PotenciaAcumulada += float(obj.Potencia)
                    
        # 3. Propagar cargas na hierarquia (sub-quadros para quadros pais)
        # Fazemos varias passagens para garantir que a carga suba todos os níveis
        for _ in range(3):
            for p in panels:
                if p.AlimentadoPor:
                    p.AlimentadoPor.PotenciaAcumulada += p.PotenciaAcumulada
                    
        FreeCAD.Console.PrintMessage("Hierarquia de quadros recalculada!\n")
