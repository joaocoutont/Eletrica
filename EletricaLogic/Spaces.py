# Integracao com Arch Spaces para calculos de iluminacao
import FreeCAD
from EletricaLogic.Calculator import ElectricalCalculator
from EletricaLogic.Settings import ProjectSettings

class SpaceLightingManager:
    @staticmethod
    def analyze_space(space_obj):
        """
        Analisa um objeto Arch Space e sugere a iluminacao.
        """
        if not hasattr(space_obj, "Area"):
            return None
            
        area = float(space_obj.Area)
        min_power = ElectricalCalculator.calculate_min_lighting_power(area)
        
        # Sugestao Luminotecnica (NBR ISO/CIE 8995-1)
        # Nivel de iluminancia sugerido (lux) baseado no tipo de edificacao
        edificacao = ProjectSettings.get_settings_obj().TipoEdificacao
        
        lux_target = 300 # Padrao residencial (Sala/Quarto)
        if edificacao == "Comercial (Escritorio)":
            lux_target = 500
        elif edificacao == "Industrial":
            lux_target = 750
            
        # Calculo simplificado (Metodo dos Lumens reverso)
        # Fluxo = (Lux * Area) / (u * d) -> u*d aprox 0.5
        flux_needed = (lux_target * area) / 0.5
        
        # Se uma lampada LED comum tem ~1000 lumens
        points_suggested = max(1, round(flux_needed / 1000.0))
        
        return {
            "Area": area,
            "PowerVA": min_power,
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
