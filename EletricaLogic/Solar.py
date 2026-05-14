# Motor de Cálculo Fotovoltaico (Solar PV)
import math

class SolarCalculator:
    """Cálculos de dimensionamento de sistemas fotovoltaicos."""

    @staticmethod
    def estimate_generation(installed_kwp, irradiation_kwh_m2_day=5.0, performance_ratio=0.75):
        """
        Estima a geração mensal de energia (kWh/mês).
        E = P_kwp * Irrad_diaria * 30 dias * PR
        """
        generation_monthly = installed_kwp * irradiation_kwh_m2_day * 30 * performance_ratio
        return round(generation_monthly, 2)

    @staticmethod
    def dimension_strings(panel_voc, panel_isc, inv_max_v, inv_min_v, inv_max_i, num_panels):
        """
        Calcula a configuração de strings (série/paralelo).
        Retorna: {panels_in_series, num_strings, status}
        """
        # Máximo em série por limite de tensão (considerando margem de 10% para frio)
        max_series = math.floor(inv_max_v / (panel_voc * 1.1))
        
        # Mínimo em série para partida do inversor
        min_series = math.ceil(inv_min_v / panel_voc)
        
        if num_panels <= max_series:
            series = num_panels
            strings = 1
        else:
            series = max_series
            strings = math.ceil(num_panels / max_series)
            
        # Check de corrente
        total_isc = strings * panel_isc
        status = "OK" if total_isc <= inv_max_i else "EXCEDE_CORRENTE"
        
        return {
            "series": series,
            "strings": strings,
            "total_voc": round(series * panel_voc * 1.1, 2),
            "total_isc": round(total_isc, 2),
            "status": status
        }

    @staticmethod
    def get_dc_cable_section(current_isc, length_m, voltage_v, loss_limit=1.0):
        """Dimensiona cabo solar CC para queda de tensão < 1%"""
        # Resistividade Cobre ~0.0172
        # ΔU = (2 * L * I * rho) / S
        # S = (2 * L * I * rho) / ΔU_lim
        delta_u_max = (loss_limit / 100.0) * voltage_v
        if delta_u_max == 0: return 4.0
        
        section_needed = (2 * length_m * current_isc * 0.0172) / delta_u_max
        
        for s in [4, 6, 10, 16]:
            if s >= section_needed:
                return s
        return 16 # Max default solar cable
