# Gerenciamento de Circuitos e Quadro de Cargas
import FreeCAD
import Spreadsheet
from EletricaLogic.Calculator import ElectricalCalculator
from EletricaLogic.Settings import ProjectSettings
from EletricaLogic.Wiring import WiringManager

class CircuitManager:
    @staticmethod
    def generate_load_schedule():
        """
        Gera ou atualiza a planilha de Quadro de Cargas.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        # 1. Coletar dados dos objetos
        circuits_data = {}
        
        for obj in doc.Objects:
            if hasattr(obj, "Circuito") and hasattr(obj, "Potencia"):
                c_name = obj.Circuito
                if c_name not in circuits_data:
                    circuits_data[c_name] = {"power_va": 0.0, "tensao": "127V", "objects": []}
                circuits_data[c_name]["power_va"] += float(obj.Potencia)
                if hasattr(obj, "Tensao"):
                    circuits_data[c_name]["tensao"] = obj.Tensao
                circuits_data[c_name]["objects"].append(obj)
        
        # 2. Criar ou buscar a planilha
        sheet_name = "Quadro_de_Cargas"
        sheet = doc.getObject(sheet_name)
        if not sheet:
            sheet = doc.addObject("Spreadsheet::Sheet", sheet_name)
        
        # 3. Preencher cabecalho
        headers = ["Circuito", "Tensao", "Carga (VA)", "Corrente (A)", "Secao (mm2)", "Comprimento (m)", "Queda (%)", "Status"]
        for col, text in enumerate(headers):
            cell = chr(65 + col) + "1"
            sheet.set(cell, text)
            sheet.setStyle(cell, "bold", "add")
        
        # 4. Preencher dados calculados
        row = 2
        circuit_lengths = WiringManager.calculate_circuit_lengths()
        
        # Encontrar o pior agrupamento para cada circuito
        grouping_per_circuit = {}
        for obj in doc.Objects:
            if hasattr(obj, "CircuitosPassantes"):
                count = len(obj.CircuitosPassantes)
                for c in obj.CircuitosPassantes:
                    grouping_per_circuit[c] = max(grouping_per_circuit.get(c, 1), count)
        
        for c_name, data in circuits_data.items():
            power_va = data["power_va"]
            tensao_str = data["tensao"]
            v_val = float(tensao_str.replace("V", ""))
            
            current_nominal = ElectricalCalculator.calculate_current(power_va, v_val)
            
            # Aplicar fator de agrupamento
            num_in_conduit = grouping_per_circuit.get(c_name, 1)
            fca = ElectricalCalculator.get_grouping_factor(num_in_conduit)
            current_corrected = current_nominal / fca
            
            # Dimensionar com a corrente corrigida
            wire = ElectricalCalculator.get_standard_wire_gauge(current_corrected)
            
            # Comprimento real do 3D (em metros)
            length_m = circuit_lengths.get(c_name, 0.0) / 1000.0
            
            # Calculo de Queda de Tensao
            drop_percent = 0.0
            if length_m > 0:
                drop_percent = ElectricalCalculator.calculate_voltage_drop(current_nominal, length_m, wire, v_val)
            
            status = "OK" if drop_percent <= 3.0 else "REVISAR"
            
            sheet.set(f"A{row}", c_name)
            sheet.set(f"B{row}", tensao_str)
            sheet.set(f"C{row}", str(round(power_va, 2)))
            sheet.set(f"D{row}", str(round(current_nominal, 2)))
            sheet.set(f"E{row}", str(wire))
            sheet.set(f"F{row}", str(round(length_m, 2)))
            sheet.set(f"G{row}", str(round(drop_percent, 2)) + "%")
            sheet.set(f"H{row}", status)
            
            row += 1
            
        doc.recompute()
        FreeCAD.Console.PrintMessage("Quadro de Cargas atualizado com sucesso!\n")
        return sheet

    @staticmethod
    def balance_phases():
        """
        Distribui os circuitos entre as fases R, S e T para equilibrar a carga total.
        """
        doc = FreeCAD.ActiveDocument
        # Coletar circuitos e potencias
        circuits = {}
        for obj in doc.Objects:
            if hasattr(obj, "Circuito") and hasattr(obj, "Potencia"):
                circuits[obj.Circuito] = circuits.get(obj.Circuito, 0.0) + float(obj.Potencia)
        
        # Ordenar circuitos por potencia (decrescente) para o algoritmo de empacotamento
        sorted_circuits = sorted(circuits.items(), key=lambda x: x[1], reverse=True)
        
        phases = {"R": 0.0, "S": 0.0, "T": 0.0}
        distribution = {}
        
        for name, power in sorted_circuits:
            # Encontrar a fase com menor carga atual
            target_phase = min(phases, key=phases.get)
            distribution[name] = target_phase
            phases[target_phase] += power
            
        # Aplicar as fases aos objetos
        for obj in doc.Objects:
            if hasattr(obj, "Circuito") and obj.Circuito in distribution:
                if not hasattr(obj, "Fase"):
                    obj.addProperty("App::PropertyEnumeration", "Fase", "Eletrica", "Fase de alimentacao")
                    obj.Fase = ["R", "S", "T"]
                obj.Fase = distribution[obj.Circuito]
        
        msg = f"Equilibrio de Fases Concluido:\nR: {phases['R']} VA\nS: {phases['S']} VA\nT: {phases['T']} VA\n"
        FreeCAD.Console.PrintMessage(msg)
        return distribution

import math
