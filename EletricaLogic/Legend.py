# Gerador de Legenda de Simbolos
import FreeCAD
import Spreadsheet

class LegendManager:
    @staticmethod
    def generate_legend():
        """
        Gera uma planilha de legenda baseada nos simbolos 2D presentes no projeto.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        # 1. Identificar simbolos unicos
        unique_symbols = {}
        
        for obj in doc.Objects:
            if obj.Label.startswith("Simbolo_"):
                sym_name = obj.Label.replace("Simbolo_", "")
                if sym_name not in unique_symbols:
                    # Tenta extrair uma descricao amigavel
                    desc = sym_name.replace("_", " ").replace(".FCStd", "")
                    unique_symbols[sym_name] = desc
        
        # 2. Criar ou buscar a planilha de legenda
        sheet_name = "Legenda_de_Simbolos"
        sheet = doc.getObject(sheet_name)
        if not sheet:
            sheet = doc.addObject("Spreadsheet::Sheet", sheet_name)
            
        # 3. Preencher cabecalho
        sheet.set("A1", "Simbolo")
        sheet.set("B1", "Descricao")
        sheet.setStyle("A1:B1", "bold", "add")
        
        # 4. Preencher dados
        row = 2
        for sym, desc in unique_symbols.items():
            sheet.set(f"A{row}", sym)
            sheet.set(f"B{row}", desc)
            row += 1
            
        doc.recompute()
        FreeCAD.Console.PrintMessage("Legenda de simbolos gerada com sucesso!\n")
        return sheet
