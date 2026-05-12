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
