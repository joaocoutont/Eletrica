# Logica de Calculo Eletrico - NBR 5410
import math

class ElectricalCalculator:
    @staticmethod
    def calculate_current(power_va, voltage, phases=None, cos_phi=1.0):
        """Calcula a corrente nominal (A) considerando o sistema do projeto"""
        if phases is None:
            from EletricaLogic.Settings import ProjectSettings
            settings = ProjectSettings.get_settings_obj()
            sistema = settings.Sistema
            if "Trifasico" in sistema:
                phases = 3
            else:
                phases = 1
                
        if phases == 1:
            return power_va / voltage
        elif phases == 3:
            return power_va / (math.sqrt(3) * voltage)
        return 0

    @staticmethod
    def get_standard_wire_gauge(current, method="B1"):
        """
        Retorna a secao do cabo (mm2) baseada na corrente e metodo de instalacao.
        Metodo B1: Embutido em alvenaria.
        Metodo D: Enterrado no solo.
        """
        # Tabelas simplificadas NBR 5410 (3 condutores carregados)
        table_b1 = {
            1.5: 15.5,
            2.5: 21,
            4: 28,
            6: 36,
            10: 50,
            16: 68,
            25: 89,
            35: 110,
            50: 134,
            70: 171,
            95: 207
        }
        
        table_d = {
            1.5: 18,
            2.5: 24,
            4: 32,
            6: 41,
            10: 57,
            16: 76,
            25: 101,
            35: 125,
            50: 151,
            70: 192,
            95: 232
        }
        
        active_table = table_d if method == "D" else table_b1
        
        for gauge, capacity in active_table.items():
            if current <= capacity:
                return gauge
        return 120 # Valor maximo se exceder

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
    def get_grouping_factor(num_circuits, is_leito=False):
        """Retorna o FCA. Se for Leito, o fator e mais favoravel (Tabela 40 NBR 5410)."""
        if is_leito:
            factors = {1: 1.0, 2: 0.88, 3: 0.82, 4: 0.77, 5: 0.75}
            return factors.get(num_circuits, 0.73)
            
        factors = {1: 1.0, 2: 0.80, 3: 0.70, 4: 0.65, 5: 0.60, 6: 0.57}
        return factors.get(num_circuits, 0.50)

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
        return factors.get(num_circuits, 1.0)

    @staticmethod
    def get_standard_breaker(current):
        """Retorna o disjuntor comercial (DIN) imediatamente superior a corrente"""
        standard_breakers = [10, 16, 20, 25, 32, 40, 50, 63, 70, 80, 100, 125]
        for b in standard_breakers:
            if current <= b:
                return b
        return 125 # Valor maximo para circuitos terminais comuns

    @staticmethod
    def calculate_short_circuit(voltage, distance_m, section):
        """
        Estimativa simplificada da corrente de curto-circuito (kA).
        """
        # Resistividade do cobre
        rho = 0.0172
        # Impedancia do cabo (aproximada)
        r_cable = (rho * distance_m) / section
        z_source = 0.02 # Impedancia da rede/trafo estimada
        isc = voltage / (z_source + r_cable)
        return isc / 1000.0 # Em kA

    @staticmethod
    def calculate_demand(total_power_va):
        """Calcula a demanda simplificada (kVA)"""
        # Ex: Fator de demanda residencial tipico ~ 0.6
        return (total_power_va * 0.6) / 1000.0

    @staticmethod
    def check_breaker_selectivity(upstream_breaker, downstream_breaker):
        """
        Verifica a seletividade amperimetrica entre dois disjuntores.
        Idealmente, Upstream >= 1.6 * Downstream
        """
        ratio = float(upstream_breaker) / float(downstream_breaker)
        is_selective = ratio >= 1.6
        
        msg = f"Relação de Corrente: {ratio:.2f}\n"
        if is_selective:
            msg += "✅ SELETIVO: O disjuntor de jusante deve desarmar primeiro."
        else:
            msg += "⚠️ NÃO SELETIVO: Risco de queda simultânea (Blackout)."
            
        return is_selective, msg
