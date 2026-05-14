# Motor de Simulação de Transientes e Ondas de Choque (SPDA)
import math

class SurgeAnalysis:
    """Simula a propagação de ondas de choque em sistemas de proteção."""

    @staticmethod
    def calculate_surge_propagation(peak_current_ka, grounding_resistance_ohm, distance_m):
        """
        Simula a atenuação da onda de choque ao longo da malha.
        Baseado na impedância característica do solo e condutores.
        """
        # Impedância de surto simplificada (Z0)
        z0 = 100 # Ohm (Valor médio para malhas de aterramento)
        
        # Tensão de surto no ponto de impacto
        v_peak = peak_current_ka * 1000 * grounding_resistance_ohm
        
        # Atenuação por distância (modelo exponencial simplificado)
        v_dist = v_peak * math.exp(-0.05 * distance_m)
        
        return {
            "v_initial_kv": round(v_peak / 1000, 2),
            "v_at_distance_kv": round(v_dist / 1000, 2),
            "risk_level": "ALTO" if v_dist > 4000 else "MODERADO" # 4kV é limite para muita eletrônica
        }

    @staticmethod
    def recommend_dps_class(v_peak_kv):
        """Recomenda a classe do DPS baseada no pico de tensão."""
        if v_peak_kv > 20: return "CLASSE I (10/350µs)"
        if v_peak_kv > 5: return "CLASSE II (8/20µs)"
        return "CLASSE III"
