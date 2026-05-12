# Logica de Eletrodutos e Tubulacoes
import FreeCAD
import Arch
import Draft

class ConduitManager:
    @staticmethod
    def create_conduit(points, diameter=20.0, label="Eletroduto"):
        """
        Cria um eletroduto (Pipe) baseado em uma lista de pontos.
        """
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument("ProjetoEletrico")
            
        # 1. Criar o caminho (Wire)
        wire = Draft.make_wire(points, closed=False, face=False)
        wire.Label = f"Caminho_{label}"
        
        # 2. Criar o Eletroduto (Arch Pipe) baseado no Wire
        pipe = Arch.makePipe(wire, diameter=diameter)
        pipe.Label = label
        
        # 3. Adicionar Propriedades Eletricas BIM
        if not hasattr(pipe, "TaxaOcupacao"):
            pipe.addProperty("App::PropertyPercent", "TaxaOcupacao", "Eletrica", "Taxa de ocupacao interna")
            pipe.TaxaOcupacao = 0.0
            
        if not hasattr(pipe, "Material"):
            pipe.addProperty("App::PropertyEnumeration", "Material", "Eletrica", "Material do eletroduto")
            pipe.Material = ["PVC Flexivel", "PVC Rigido Cinza", "Aco Galvanizado Leve", "Aco Galvanizado Pesado"]
            pipe.Material = "PVC Flexivel"
            
        if not hasattr(pipe, "CircuitosPassantes"):
            pipe.addProperty("App::PropertyStringList", "CircuitosPassantes", "Eletrica", "Lista de circuitos que passam por este eletroduto")
            pipe.addProperty("App::PropertyEnumeration", "MetodoInstalacao", "Eletrica", "Metodo de instalacao segundo NBR 5410")
            pipe.MetodoInstalacao = ["B1", "D", "A1"]
            pipe.MetodoInstalacao = "B1"

        doc.recompute()
        return pipe

    @staticmethod
    def create_cable_tray(points, width=200, height=100, label="Eletrocalha"):
        """Cria uma eletrocalha retangular industrial"""
        doc = FreeCAD.ActiveDocument
        
        # 1. Caminho
        wire = Draft.make_wire(points, closed=False)
        # 2. Perfil Retangular
        rect = Draft.make_rectangle(width, height)
        tray = Arch.makeStructure(rect, [wire])
        tray.Label = label
        
        # 3. Propriedades BIM
        if not hasattr(tray, "CircuitosPassantes"):
            tray.addProperty("App::PropertyStringList", "CircuitosPassantes", "Eletrica", "Circuitos")
            
        doc.recompute()
        return tray

    @staticmethod
    def suggest_conduit_size(conduit_obj):
        """Sugere o proximo diametro comercial se estiver superlotado"""
        if not hasattr(conduit_obj, "TaxaOcupacao") or not hasattr(conduit_obj, "DiametroNominal"):
            return None
            
        if conduit_obj.TaxaOcupacao <= 40.0:
            return None # Ja esta OK
            
        standard_sizes = ["16mm", "20mm", "25mm", "32mm", "40mm", "50mm"]
        current_size = conduit_obj.DiametroNominal
        
        try:
            idx = standard_sizes.index(current_size)
            for i in range(idx + 1, len(standard_sizes)):
                return standard_sizes[i]
        except:
            pass
        return None

    @staticmethod
    def check_all_conduits_fill():
        """
        Verifica a taxa de ocupacao de todos os eletrodutos do projeto.
        """
        doc = FreeCAD.ActiveDocument
        from EletricaLogic.Calculator import ElectricalCalculator
        
        results = []
        for obj in doc.Objects:
            if hasattr(obj, "CircuitosPassantes") and hasattr(obj, "Diameter"):
                num_circuits = len(obj.CircuitosPassantes)
                if num_circuits == 0: continue
                
                wire_area = ElectricalCalculator.get_wire_external_area(2.5) * 3 * num_circuits
                conduit_area = ElectricalCalculator.get_conduit_internal_area(float(obj.Diameter))
                occupancy = (wire_area / conduit_area) * 100
                
                obj.TaxaOcupacao = occupancy
                
                if occupancy > 40.0:
                    results.append(f"ALERTA: {obj.Label} esta com {occupancy:.1f}% de ocupacao")
                    if hasattr(obj, "ViewObject"):
                        obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
                else:
                    if hasattr(obj, "ViewObject"):
                        obj.ViewObject.ShapeColor = (0.7, 0.7, 0.7)
                        
        return results
