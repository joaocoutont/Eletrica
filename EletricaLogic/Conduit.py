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

        doc.recompute()
        return pipe

    @staticmethod
    def calculate_diameter(n_wires, wire_section):
        """
        Calculo simplificado de diametro baseado na NBR 5410 (40% de taxa de ocupacao)
        Retorna o diametro nominal comercial (20, 25, 32mm...)
        """
        # Implementacao futura baseada em tabelas
        return 20.0
