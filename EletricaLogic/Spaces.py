# Integracao com Arch Spaces para calculos de iluminacao
import FreeCAD
from EletricaLogic.Calculator import ElectricalCalculator
from EletricaLogic.Settings import ProjectSettings

class SpaceSizingManager:
    """
    Especialista em dimensionamento de ambientes (Luz e Tomadas) segundo NBR 5410.
    """
    @staticmethod
    def calculate_required_lumens(area, target_lux=300, utilization_factor=0.5, maintenance_factor=0.8):
        """
        Calcula o fluxo luminoso total necessario usando o Metodo dos Lumens.
        Phi = (E * A) / (u * d)
        """
        total_lumens = (target_lux * area) / (utilization_factor * maintenance_factor)
        return total_lumens

    @staticmethod
    def calculate_min_tugs(perimeter, is_wet_area=False):
        """
        Calcula o número mínimo de tomadas de uso geral (TUGs) - NBR 5410.
        Geral: 1 a cada 5m de perímetro.
        Cozinhas/Áreas de Serviço: 1 a cada 3,5m.
        """
        import math
        spacing = 3.5 if is_wet_area else 5.0
        return math.ceil(perimeter / spacing)

    @staticmethod
    def analyze_space(space_obj):
        """
        Analisa um objeto Arch Space e sugere a iluminacao e tomadas.
        """
        if not hasattr(space_obj, "Area") or not hasattr(space_obj, "Shape"):
            return None
            
        area = float(space_obj.Area)
        # Calcula perímetro real da face da base
        perimeter = space_obj.Shape.Length / 2.0 # Aproximação se for um volume extrudado
        if hasattr(space_obj, "Perimeter"): perimeter = float(space_obj.Perimeter)
        
        min_lighting_va = ElectricalCalculator.calculate_min_lighting_power(area)
        
        # Detectar se é área úmida pelo label
        wet_keywords = ["Cozinha", "Banheiro", "Lavanderia", "Serviço", "Copa"]
        is_wet = any(kw.lower() in space_obj.Label.lower() for kw in wet_keywords)
        
        min_tugs = SpaceSizingManager.calculate_min_tugs(perimeter, is_wet)
        
        # Sugestao Luminotecnica (NBR ISO/CIE 8995-1)
        settings = ProjectSettings.get_settings_obj()
        edificacao = getattr(settings, "TipoEdificacao", "Residencial")
        
        lux_target = 300 # Padrao residencial
        if edificacao == "Comercial (Escritorio)":
            lux_target = 500
        elif edificacao == "Industrial":
            lux_target = 750
            
        flux_needed = SpaceSizingManager.calculate_required_lumens(area, lux_target)
        points_suggested = max(1, round(flux_needed / 1000.0))
        
        return {
            "Area": round(area, 2),
            "Perimeter": round(perimeter, 2),
            "MinLightingVA": min_lighting_va,
            "MinTUGs": min_tugs,
            "IsWetArea": is_wet,
            "LuxTarget": lux_target,
            "PointsSuggested": points_suggested
        }

    @staticmethod
    def distribute_lights(space_obj, num_points):
        """
        Distribui os pontos de luz em uma malha (grid) dentro do Arch Space.
        """
        import math
        from EletricaLogic.Library import LibraryManager
        
        # 1. Pegar as dimensoes do espaco
        bbox = space_obj.Shape.BoundBox
        width = bbox.XMax - bbox.XMin
        length = bbox.YMax - bbox.YMin
        
        # 2. Calcular grid (ex: 4 pontos -> 2x2)
        cols = math.ceil(math.sqrt(num_points))
        rows = math.ceil(num_points / cols)
        
        dx = width / (cols + 1)
        dy = length / (rows + 1)
        
        manager = LibraryManager()
        # Tentar achar um bocal/lampada padrao na biblioteca
        all_comps = manager.list_components()
        light_file = next((f for f in all_comps if "Luz" in f or "Lampada" in f or "Bocal" in f), None)
        
        if not light_file:
            FreeCAD.Console.PrintWarning("Nenhum componente de iluminacao encontrado na biblioteca 3D.\n")
            return
            
        inserted_points = []
        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                if len(inserted_points) >= num_points: break
                
                x = bbox.XMin + (c * dx)
                y = bbox.YMin + (r * dy)
                z = bbox.ZMax # Coloca no teto do espaco
                
                # Inserir o componente
                obj = manager.insert_component(light_file)
                if obj:
                    obj.Placement.Base = FreeCAD.Vector(x, y, z)
                    inserted_points.append(obj)
        
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.Console.PrintMessage(f"{len(inserted_points)} pontos de luz distribuidos em {space_obj.Label}.\n")
