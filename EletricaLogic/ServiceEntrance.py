# Logica de Entrada de Energia e Alimentadores
import FreeCAD
from EletricaLogic.Calculator import ElectricalCalculator
from EletricaLogic.Settings import ProjectSettings

class ServiceEntranceManager:
    @staticmethod
    def get_entrance_presets():
        return {
            "Caixa de Medicao Tipo N": {"desc": "Medicao Monofasica", "max_amp": 40},
            "Caixa de Medicao Tipo T": {"desc": "Medicao Trifasica", "max_amp": 100},
            "Caixa de Passagem 30x30": {"desc": "Caixa de Passagem de Solo", "type": "Box"},
            "Caixa de Passagem 40x40": {"desc": "Caixa de Passagem de Solo", "type": "Box"}
        }

    @staticmethod
    def calculate_feeder(total_power_va, length_m):
        """
        Calcula o cabo alimentador da entrada.
        Total_power_va: Soma de todas as cargas do projeto.
        """
        voltage = ProjectSettings.get_voltage()
        # Assume-se trifasico para entrada de energia em projetos BIM
        current = ElectricalCalculator.calculate_current(total_power_va, voltage, phases=3)
        
        # Secao baseada em corrente
        section_base = ElectricalCalculator.get_standard_wire_gauge(current)
        
        # Verificacao de queda de tensao (Limite rigido de 1% para alimentadores)
        drop, ok = 0.0, False
        section = section_base
        while not ok and section <= 120:
            drop = ElectricalCalculator.calculate_voltage_drop(current, length_m, section, voltage)
            if drop <= 1.0:
                ok = True
            else:
                # Aumentar para a proxima secao comercial
                standard_sections = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120]
                idx = standard_sections.index(section)
                if idx < len(standard_sections) - 1:
                    section = standard_sections[idx + 1]
                else:
                    break
                    
        return {
            "Current": round(current, 2),
            "Section": section,
            "VoltageDrop": round(drop, 2)
        }
