# Logica de Calculo Eletrico - NBR 5410
import math

class ElectricalCalculator:
    @staticmethod
    def calculate_current(power_va, voltage, phases=1, cos_phi=1.0):
        """Calcula a corrente nominal (A)"""
        if phases == 1:
            return power_va / voltage
        elif phases == 3:
            return power_va / (math.sqrt(3) * voltage)
        return 0

    @staticmethod
    def get_standard_wire_gauge(current, method="B1"):
        """Retorna a secao minima do condutor (mm2) baseado na capacidade de conducao simples"""
        # Tabela simplificada NBR 5410 (Metodo B1, PVC, 2 condutores carregados)
        standard_sections = [
            (14, 1.5),
            (17.5, 2.5),
            (24, 4),
            (32, 6),
            (41, 10),
            (57, 16),
            (76, 25),
            (101, 35)
        ]
        
        for cap, section in standard_sections:
            if current <= cap:
                return section
        return 35 # Placeholder para secoes maiores

    @staticmethod
    def calculate_voltage_drop(current, length, section, voltage, material="Cu"):
        """Calcula a queda de tensao percentual"""
        # Resistividade do cobre: 0.0172 Ohm*mm2/m
        rho = 0.0172 if material == "Cu" else 0.0282
        drop_v = (2 * rho * length * current) / section
        return (drop_v / voltage) * 100
