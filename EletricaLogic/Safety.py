# Analise de Seguranca NR-10 e Arco Eletrico (Arc Flash)
import FreeCAD

class SafetyManager:
    @staticmethod
    def calculate_arc_flash(ka_short_circuit, voltage=380, distance_mm=455):
        """
        Calculo simplificado de Energia Incidente (cal/cm2) baseado na IEEE 1584.
        """
        # Constantes simplificadas para baixa tensao
        energy = (ka_short_circuit * (voltage/1000) * 1.5) / (distance_mm/100)
        
        # Categorias de EPI (NR-10 / NFPA 70E)
        if energy < 1.2:
            cat = "Categoria 0 (Farda Algodão)"
        elif energy < 4:
            cat = "Categoria 1 (FR - 4 cal/cm2)"
        elif energy < 8:
            cat = "Categoria 2 (FR - 8 cal/cm2)"
        elif energy < 25:
            cat = "Categoria 3 (FR - 25 cal/cm2)"
        else:
            cat = "Categoria 4 (Risco Extremo - 40 cal/cm2)"
            
        return {
            "Energia": round(energy, 2),
            "EPI_Sugerido": cat,
            "DistanciaSegura": "1.5 metros"
        }

    @staticmethod
    def apply_safety_to_panel(panel_obj):
        """Aplica analise de arco eletrico ao painel"""
        # Pega o curto circuito calculado anteriormente (ou default se nao houver)
        ka = getattr(panel_obj, "CurtoCircuitoKA", 10.0)
        result = SafetyManager.calculate_arc_flash(ka)
        
        if not hasattr(panel_obj, "RiscoArco"):
            panel_obj.addProperty("App::PropertyString", "RiscoArco", "Segurança").RiscoArco = result["EPI_Sugerido"]
            panel_obj.addProperty("App::PropertyFloat", "EnergiaIncidente", "Segurança").EnergiaIncidente = result["Energia"]
            
        return result
