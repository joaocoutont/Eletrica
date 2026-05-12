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

    @staticmethod
    def calculate_min_lighting_power(area):
        """Calcula a potencia minima de iluminacao (VA) segundo a NBR 5410"""
        if area <= 6.0:
            return 100.0
        
        # 100VA para os primeiros 6m2 + 60VA para cada 4m2 inteiros restantes
        remaining_area = area - 6.0
        extra_units = math.floor(remaining_area / 4.0)
        return 100.0 + (extra_units * 60.0)

    @staticmethod
    def get_wire_external_area(section):
        """Retorna a area externa aproximada (mm2) do cabo com isolacao (PVC 750V)"""
        # Secao -> Diametro Externo Aprox (mm)
        diameters = {
            1.5: 3.0,
            2.5: 3.7,
            4.0: 4.3,
            6.0: 5.0,
            10.0: 6.2,
            16.0: 7.5
        }
        d = diameters.get(section, 3.7)
        return (math.pi * (d**2)) / 4.0

    @staticmethod
    def get_conduit_internal_area(nominal_diameter):
        """Retorna a area interna util (mm2) de um eletroduto comercial (PVC)"""
        # Nominal -> Interno Aprox (mm)
        internal_diameters = {
            20: 16.0,
            25: 20.5,
            32: 27.0,
            40: 34.0,
            50: 43.0
        }
        d = internal_diameters.get(nominal_diameter, 16.0)
        return (math.pi * (d**2)) / 4.0

    @staticmethod
    def get_grouping_factor(num_circuits):
        """Retorna o fator de agrupamento (fca) segundo a NBR 5410"""
        factors = {
            1: 1.0,
            2: 0.80,
            3: 0.70,
            4: 0.65,
            5: 0.60,
            6: 0.57,
            7: 0.54,
            8: 0.52,
            9: 0.50
        }
        if num_circuits >= 9: return 0.50
        return factors.get(num_circuits, 1.0)
