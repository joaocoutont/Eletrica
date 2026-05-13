# Logica de Calculo Eletrico - NBR 5410
import math
from typing import Optional, Union, Tuple


class ElectricalCalculator:
    @staticmethod
    def calculate_current(power_va: float, voltage: float, phases: int = 1, cos_phi: float = 1.0) -> float:
        """
        Calcula a corrente nominal (A) considerando o sistema do projeto.
        Esta é uma função pura, sem dependência de APIs externas.
        """
        if voltage <= 0:
            return 0.0
            
        if phases == 1 or phases == 2:
            # Em sistemas monofásicos ou bifásicos (F-F), a tensão passada deve ser a nominal do circuito
            return power_va / (voltage * cos_phi)
        elif phases == 3:
            # Em sistemas trifásicos, a tensão passada deve ser a de linha (ex: 220V ou 380V)
            return power_va / (math.sqrt(3) * voltage * cos_phi)
        return 0.0

    @staticmethod
    def get_temperature_factor(temp: float, insulation: str = "PVC") -> float:
        """Retorna o fator de correção de temperatura (FCT) segundo NBR 5410"""
        if insulation == "PVC":
            factors = {10: 1.22, 15: 1.17, 20: 1.12, 25: 1.06, 30: 1.00, 35: 0.94, 40: 0.87, 45: 0.79, 50: 0.71}
        else: # EPR/XLPE
            factors = {10: 1.15, 15: 1.12, 20: 1.08, 25: 1.04, 30: 1.00, 35: 0.96, 40: 0.91, 45: 0.87, 50: 0.82}
        
        # Busca o valor mais próximo (arredondado para cima para segurança)
        target_temp = min(max(10, (math.ceil(temp/5)*5)), 50)
        return factors.get(target_temp, 1.0)

    @staticmethod
    def get_standard_wire_gauge(current: float, method: str = "B1", insulation: str = "PVC", material: str = "Cu", ambient_temp: float = 30) -> float:
        """
        Retorna a secao do cabo (mm2) baseada na corrente e metodo de instalacao.
        Considera FCT (Temperatura) e material.
        """
        fct = ElectricalCalculator.get_temperature_factor(ambient_temp, insulation)
        corrected_current = current / fct if fct > 0 else current

        # Tabelas NBR 5410
        TABLES_PVC_CU = {
            "A1": {1.5: 13, 2.5: 17.5, 4: 23, 6: 29, 10: 39, 16: 52},
            "B1": {1.5: 15.5, 2.5: 21, 4: 28, 6: 36, 10: 50, 16: 68, 25: 89, 35: 110, 50: 134},
            "C":  {1.5: 17.5, 2.5: 24, 4: 32, 6: 41, 10: 57, 16: 76, 25: 101, 35: 125, 50: 151},
        }
        
        TABLES_XLPE_CU = {
            "A1": {1.5: 17, 2.5: 23, 4: 31, 6: 40, 10: 54, 16: 73},
            "B1": {1.5: 21, 2.5: 28, 4: 37, 6: 48, 10: 66, 16: 91, 25: 119, 35: 147, 50: 179},
            "C":  {1.5: 23, 2.5: 31, 4: 42, 6: 54, 10: 75, 16: 100, 25: 133, 35: 164, 50: 197},
        }

        active_table = TABLES_XLPE_CU if "90" in insulation or "EPR" in insulation else TABLES_PVC_CU
        table = active_table.get(method.upper(), active_table["B1"])
        
        factor = 1.0
        if "Al" in material: factor = 0.77

        sorted_gauges = sorted(table.keys())
        for gauge in sorted_gauges:
            if corrected_current <= (table[gauge] * factor):
                return gauge
                
        return 240.0

    @staticmethod
    def calculate_voltage_drop(current: float, length: float, section: float, voltage: float, phases: int = 1, material: str = "Cu") -> float:
        """
        Calcula a queda de tensao percentual (delta V %).
        Considera o fator 2 para Monofásico/Bifásico e sqrt(3) para Trifásico.
        """
        if section <= 0 or voltage <= 0:
            return 0.0
            
        # Resistividade: Cu = 1/58 (~0.0172), Al = 1/35 (~0.0282)
        rho = 0.0172
        if "Al" in material or material == "Alumínio":
            rho = 0.0282
        
        # Fator de fase (k)
        # Monofásico/Bifásico (F+N ou F+F): k=2
        # Trifásico (3F): k=sqrt(3)
        k = math.sqrt(3) if phases == 3 else 2.0
        
        drop_v = (k * rho * length * current) / section
        return (drop_v / voltage) * 100

    @staticmethod
    def calculate_min_lighting_power(area: float) -> float:
        """Calcula a potencia minima de iluminacao (VA) segundo a NBR 5410"""
        if area <= 6.0:
            return 100.0
        
        # 100VA para os primeiros 6m2 + 60VA para cada 4m2 inteiros restantes
        remaining_area = area - 6.0
        extra_units = math.floor(remaining_area / 4.0)
        return 100.0 + (extra_units * 60.0)

    @staticmethod
    def get_wire_external_area(section: float) -> float:
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
    def get_grouping_factor(num_circuits: int, is_leito: bool = False) -> float:
        """Retorna o FCA. Se for Leito, o fator e mais favoravel (Tabela 40 NBR 5410)."""
        if is_leito:
            factors = {1: 1.0, 2: 0.88, 3: 0.82, 4: 0.77, 5: 0.75}
            return factors.get(num_circuits, 0.73)
            
        factors = {1: 1.0, 2: 0.80, 3: 0.70, 4: 0.65, 5: 0.60, 6: 0.57}
        return factors.get(num_circuits, 0.50)

    @staticmethod
    def get_conduit_internal_area(nominal_diameter: int) -> float:
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
    def get_standard_breaker(current: float) -> int:
        """Retorna o disjuntor comercial (DIN) imediatamente superior a corrente"""
        standard_breakers = [10, 16, 20, 25, 32, 40, 50, 63, 70, 80, 100, 125]
        for b in standard_breakers:
            if current <= b:
                return b
        return 125 # Valor maximo para circuitos terminais comuns

    @staticmethod
    def calculate_short_circuit(voltage: float, distance_m: float, section: float, z_trafo_pct: float = 5.0, s_trafo_kva: float = 112.5) -> float:
        """
        Cálculo avançado da corrente de curto-circuito presumida (kA).
        Considera a impedância do transformador montante (Z%) e a resistência do cabo.
        """
        if section <= 0:
            return 0.0
            
        # 1. Impedância da fonte (Trafo) em Ohms
        # Zf = (Z% * V^2) / (100 * S)
        z_source = (z_trafo_pct * (voltage**2)) / (100 * s_trafo_kva * 1000)

        # 2. Impedância do cabo
        rho = 0.0172 # Cobre
        r_cable = (rho * distance_m) / section
        
        # 3. Corrente de Curto-Circuito (Icc)
        # Icc = V / Z_total
        z_total = z_source + r_cable
        if z_total <= 0:
            return 0.0
            
        isc = voltage / z_total
        return isc / 1000.0 # Retorna em kA

    @staticmethod
    def calculate_demand(total_power_va: float, project_type: str = "Residencial") -> float:
        """
        Calcula a demanda (kVA) com fator variável por tipo de instalação.
        """
        # Fatores de demanda típicos por tipo de instalação
        demand_factors = {
            "Residencial": 0.60,
            "Comercial":   0.75,
            "Industrial":  0.85,
            "Predial":     0.65,
            "Público":     0.70
        }
        
        factor = demand_factors.get(project_type, 0.60)
        return (total_power_va * factor) / 1000.0

    @staticmethod
    def check_breaker_selectivity(upstream_breaker: float, downstream_breaker: float) -> Tuple[bool, str]:
        """
        Verifica a seletividade amperimetrica entre dois disjuntores.
        Idealmente, Upstream >= 1.6 * Downstream
        """
        if downstream_breaker <= 0:
            return True, "N/A"
            
        ratio = float(upstream_breaker) / float(downstream_breaker)
        is_selective = ratio >= 1.6
        
        msg = f"Relação de Corrente: {ratio:.2f}\n"
        if is_selective:
            msg += "✅ SELETIVO: O disjuntor de jusante deve desarmar primeiro."
        else:
            msg += "⚠️ NÃO SELETIVO: Risco de queda simultânea (Blackout)."
            
        return is_selective, msg

