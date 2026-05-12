# Estimador de Energia Solar Fotovoltaica
import math

class SolarEstimator:
    @staticmethod
    def estimate_pv_system(total_load_va, hsp=5.0):
        """
        Estima o kit solar baseado na carga e nas Horas de Sol Pleno (HSP).
        HSP padrao Brasil ~ 5.0
        """
        # Estimativa de consumo mensal (considerando fator de uso de 30% da carga instalada)
        # Consumo = (P * 24h * 30 dias * Fator de Uso) / 1000
        monthly_kwh = (total_load_va * 24 * 30 * 0.3) / 1000.0
        
        # Potencia do Kit necessária (P_pico = Consumo_mensal / (HSP * 30))
        p_pico_kw = monthly_kwh / (hsp * 30)
        
        # Quantidade de paineis (Assumindo paineis de 550W)
        panel_power = 0.55
        num_panels = math.ceil(p_pico_kw / panel_power)
        
        # Area necessária (Assumindo 2.5m2 por painel)
        area_needed = num_panels * 2.5
        
        return {
            "MonthlyConsumption": round(monthly_kwh, 2),
            "SystemPowerKWp": round(p_pico_kw, 2),
            "NumPanels": num_panels,
            "AreaNeeded": round(area_needed, 2)
        }
