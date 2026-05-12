# Gerenciamento de Circuitos e Quadro de Cargas
import FreeCAD
import Spreadsheet
from EletricaLogic.Calculator import ElectricalCalculator

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
                power = float(obj.Potencia)
                
                if c_name not in circuits_data:
                    circuits_data[c_name] = {"power_va": 0.0, "objects": []}
                
                circuits_data[c_name]["power_va"] += power
                circuits_data[c_name]["objects"].append(obj)
        
        # 2. Criar ou buscar a planilha
        sheet_name = "Quadro_de_Cargas"
        sheet = doc.getObject(sheet_name)
        if not sheet:
            sheet = doc.addObject("Spreadsheet::Sheet", sheet_name)
        
        # 3. Preencher cabecalho
        headers = ["Circuito", "Carga (VA)", "Corrente (A)", "Secao (mm2)", "Disjuntor (A)"]
        for col, text in enumerate(headers):
            cell = chr(65 + col) + "1" # A1, B1...
            sheet.set(cell, text)
            sheet.setStyle(cell, "bold", "add")
        
        # 4. Preencher dados calculados
        row = 2
        voltage = 220.0 # Poderia ser uma configuracao do projeto
        
        for c_name, data in circuits_data.items():
            power_va = data["power_va"]
            current = ElectricalCalculator.calculate_current(power_va, voltage)
            wire = ElectricalCalculator.get_standard_wire_gauge(current)
            
            sheet.set(f"A{row}", c_name)
            sheet.set(f"B{row}", str(round(power_va, 2)))
            sheet.set(f"C{row}", str(round(current, 2)))
            sheet.set(f"D{row}", str(wire))
            sheet.set(f"E{row}", str(math.ceil(current/10)*10 if current > 0 else 0)) # Placeholder p/ disjuntor
            
            row += 1
            
        doc.recompute()
        FreeCAD.Console.PrintMessage("Quadro de Cargas atualizado com sucesso!\n")
        return sheet

import math
