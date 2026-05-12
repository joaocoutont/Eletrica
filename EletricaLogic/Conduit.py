# Logica de Eletrodutos e Tubulacoes
import FreeCAD
import Arch

class ConduitManager:
    @staticmethod
    def create_conduit(points, diameter=20.0, label="Eletroduto"):
        """
        Cria um eletroduto (Pipe) baseado em uma lista de pontos.
        """
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument("ProjetoEletrico")
            
        import Draft
        # 1. Criar o caminho (Wire)
        wire = Draft.make_wire(points, closed=False, face=False)
        wire.Label = f"Caminho_{label}"
        
        # 2. Criar o Eletroduto (Arch Pipe) baseado no Wire
        # O Arch Pipe do FreeCAD e excelente para isso
        pipe = Arch.makePipe(wire, diameter=diameter)
        pipe.Label = label
        
        # 3. Adicionar Propriedades Eletricas BIM
        if not hasattr(pipe, "TaxaOcupacao"):
            pipe.addProperty("App::PropertyPercent", "TaxaOcupacao", "Eletrica", "Taxa de ocupacao interna")
            pipe.TaxaOcupacao = 0.0
            
        if not hasattr(pipe, "Material"):
            pipe.addProperty("App::PropertyString", "Material", "Eletrica", "Material do eletroduto")
            pipe.Material = "PVC Flexivel"
            
        if not hasattr(pipe, "CircuitosPassantes"):
            pipe.addProperty("App::PropertyStringList", "CircuitosPassantes", "Eletrica", "Lista de circuitos que passam por este eletroduto")
            pipe.addProperty("App::PropertyEnumeration", "MetodoInstalacao", "Eletrica", "Metodo de instalacao segundo NBR 5410")
            pipe.MetodoInstalacao = ["B1", "D", "A1"]
            pipe.MetodoInstalacao = "B1"

        doc.recompute()
        return pipe

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
                test_size = standard_sizes[i]
                # Simular ocupacao no novo tamanho
                # (Apenas um calculo rapido aqui para a sugestao)
                # ...
                return test_size
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
        from EletricaLogic.Circuits import CircuitManager
        
        # Obter secoes de cabos por circuito (usando a logica do quadro de cargas)
        # Simplificacao: Vamos assumir que cada circuito tem 3 cabos (F, N, T)
        results = []
        
        for obj in doc.Objects:
            if hasattr(obj, "CircuitosPassantes") and hasattr(obj, "Diameter"):
                num_circuits = len(obj.CircuitosPassantes)
                if num_circuits == 0: continue
                
                # Calcular area ocupada (simplificado: cada circuito = 3 fios de 2.5mm2 padrao)
                # Em um projeto real, buscaríamos a secao exata calculada para aquele circuito
                wire_area = ElectricalCalculator.get_wire_external_area(2.5) * 3 * num_circuits
                
                conduit_area = ElectricalCalculator.get_conduit_internal_area(float(obj.Diameter))
                occupancy = (wire_area / conduit_area) * 100
                
                # NBR 5410: Max 40% para 3 ou mais cabos
                limit = 40.0
                is_ok = occupancy <= limit
                
                obj.TaxaOcupacao = occupancy
                
                if not is_ok:
                    results.append(f"ALERTA: {obj.Label} esta com {occupancy:.1f}% de ocupacao (Limite 40%)")
                    # Mudar cor para vermelho se estiver cheio
                    if hasattr(obj, "ViewObject"):
                        obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
                else:
                    if hasattr(obj, "ViewObject"):
                        obj.ViewObject.ShapeColor = (0.7, 0.7, 0.7) # Cor padrao
                        
        return results

    @staticmethod
    def calculate_diameter(n_wires, wire_section):
        """
        Calculo simplificado de diametro baseado na NBR 5410 (40% de taxa de ocupacao)
        Retorna o diametro nominal comercial (20, 25, 32mm...)
        """
        # Implementacao futura baseada em tabelas
        return 20.0
