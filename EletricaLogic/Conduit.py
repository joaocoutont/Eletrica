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
    def create_cable_tray(points, width=200, height=100, label="Eletrocalha", tray_type="Perfurada", material="Aço Galvanizado"):
        """
        Cria uma eletrocalha industrial com propriedades BIM completas.
        Tipos: Perfurada, Fechada (bandejão), Escada (ladder), Arame (wire mesh)
        """
        doc = FreeCAD.ActiveDocument

        # 1. Caminho da eletrocalha
        wire = Draft.make_wire(points, closed=False)
        wire.Label = f"Eixo_{label}"

        # 2. Perfil retangular (seção transversal)
        rect = Draft.make_rectangle(width, height)
        tray = Arch.makeStructure(rect, [wire])
        tray.Label = label

        # 3. Propriedades BIM completas
        grp = "Eletrocalha"
        props = {
            "TipoBIM":       ("App::PropertyString",      "Eletrica", "Tipo BIM"),
            "TipoEletrocalha":("App::PropertyEnumeration","Eletrocalha", "Tipo de Eletrocalha"),
            "MaterialCalha": ("App::PropertyString",      grp,        "Material"),
            "LarguraMM":     ("App::PropertyFloat",       grp,        "Largura (mm)"),
            "AlturaMM":      ("App::PropertyFloat",       grp,        "Altura / Profundidade (mm)"),
            "CapacidadeKg":  ("App::PropertyFloat",       grp,        "Capacidade de Carga (kg/m)"),
            "TaxaOcupacao":  ("App::PropertyFloat",       grp,        "Taxa de Ocupação (%)"),
            "CircuitosPassantes": ("App::PropertyStringList", grp,    "Circuitos passantes"),
            "Observacoes":   ("App::PropertyString",      grp,        "Observações"),
        }
        for prop, (ptype, grp_name, desc) in props.items():
            if not hasattr(tray, prop):
                tray.addProperty(ptype, prop, grp_name, desc)

        tray_type_map = {
            "Escada": "Escada (Ladder)",
            "Ladder": "Escada (Ladder)",
            "Arame": "Arame (Wire Mesh)",
            "Wire Mesh": "Arame (Wire Mesh)",
        }

        tray.TipoBIM         = "Eletrocalha"
        tray.TipoEletrocalha = ["Perfurada", "Fechada", "Escada (Ladder)", "Arame (Wire Mesh)"]
        tray.TipoEletrocalha = tray_type_map.get(tray_type, tray_type)
        tray.MaterialCalha   = material
        tray.LarguraMM       = float(width)
        tray.AlturaMM        = float(height)
        tray.TaxaOcupacao    = 0.0

        # Capacidade padrão por largura (kg/m) — valores típicos PEMSA/OBO
        cap_map = {100: 15, 150: 20, 200: 30, 300: 45, 400: 60, 500: 75, 600: 90}
        tray.CapacidadeKg = float(cap_map.get(int(width), 30))

        doc.recompute()
        return tray


class CableTrayCalculator:
    """Calcula o dimensionamento de eletrocalhas industriais."""

    # Diâmetros externos típicos de cabos (mm) por seção
    CABLE_DIAMETERS = {1.5: 7, 2.5: 8, 4: 9, 6: 10, 10: 12, 16: 14,
                       25: 17, 35: 19, 50: 22, 70: 25, 95: 29, 120: 32}

    # Larguras comerciais padrão (mm)
    STANDARD_WIDTHS = [100, 150, 200, 300, 400, 500, 600]

    @staticmethod
    def get_cable_diameter(section_mm2):
        """Retorna o diâmetro externo estimado (mm) do cabo."""
        return CableTrayCalculator.CABLE_DIAMETERS.get(section_mm2, 12)

    @staticmethod
    def dimension_tray(cables_list, fill_factor=0.40):
        """
        Dimensiona a eletrocalha para uma lista de cabos.
        cables_list: [(quantidade, seccao_mm2), ...]
        fill_factor: taxa de ocupação máxima (padrão 40% — boa prática IEC)
        """
        import math
        total_area = 0.0
        for qty, section in cables_list:
            d = CableTrayCalculator.get_cable_diameter(section)
            area = math.pi * (d / 2) ** 2
            total_area += qty * area

        required_area = total_area / fill_factor

        # Escolher largura mínima (altura padrão 50mm)
        height = 50
        for width in CableTrayCalculator.STANDARD_WIDTHS:
            tray_area = width * height
            if tray_area >= required_area:
                return {
                    "cables_area_mm2": round(total_area, 1),
                    "required_area_mm2": round(required_area, 1),
                    "width_mm": width,
                    "height_mm": height,
                    "fill_percent": round((total_area / (width * height)) * 100, 1),
                    "designation": f"Eletrocalha {width}x{height}mm",
                }
        # Se não couber em nenhum padrão, usar o maior com 2 andares
        return {
            "cables_area_mm2": round(total_area, 1),
            "required_area_mm2": round(required_area, 1),
            "width_mm": 600,
            "height_mm": 100,
            "fill_percent": round((total_area / (600 * 100)) * 100, 1),
            "designation": "Eletrocalha 600x100mm (verificar 2 andares)",
        }


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
        if not doc:
            return []

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
