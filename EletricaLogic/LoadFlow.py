# Simulador de Fluxo de Carga e Queda de Tensão Dinâmica
import math

class LoadFlowSimulator:
    """Simula o comportamento elétrico da rede sob carga total."""

    @staticmethod
    def simulate_node(voltage_base, current_load, resistance_per_km, length_m):
        """Calcula a queda de tensão e tensão no nó final."""
        # V_drop = sqrt(3) * I * (R*cosphi + X*sinphi) * L
        # Simplificado para R (predominante em BT)
        length_km = length_m / 1000.0
        voltage_drop = math.sqrt(3) * current_load * resistance_per_km * length_km
        voltage_final = voltage_base - voltage_drop
        drop_percent = (voltage_drop / voltage_base) * 100.0
        
        status = "ESTÁVEL"
        if drop_percent > 5.0: status = "CRÍTICO"
        if drop_percent > 7.0: status = "FALHA"
        
        return {
            "v_drop": round(voltage_drop, 2),
            "v_final": round(voltage_final, 2),
            "percent": round(drop_percent, 2),
            "status": status
        }

    @staticmethod
    def analyze_transformers(trafo_kva, current_total, voltage):
        """Analisa a saturação do transformador."""
        capacity_amp = (trafo_kva * 1000) / (math.sqrt(3) * voltage)
        loading_percent = (current_total / capacity_amp) * 100.0
        
        return {
            "capacity": round(capacity_amp, 2),
            "loading": round(loading_percent, 2),
            "status": "OK" if loading_percent < 100 else "SOBRECARGA"
        }
