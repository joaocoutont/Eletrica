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

    @staticmethod
    def generate_graphic_legend():
        """
        Gera uma folha no TechDraw com a legenda gráfica dos símbolos usados.
        """
        import os
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        # 1. Identificar símbolos únicos
        used_symbols = {}
        for obj in doc.Objects:
            if hasattr(obj, "TipoBIM") and obj.Label.startswith("Simbolo_"):
                sym_id = obj.Label
                if sym_id not in used_symbols:
                    desc = obj.Label.replace("Simbolo_", "").replace("_", " ")
                    used_symbols[sym_id] = {"obj": obj, "desc": desc}
        
        if not used_symbols:
            FreeCAD.Console.PrintWarning("Nenhum símbolo detectado no projeto.\n")
            return

        # 2. Criar página TechDraw
        page = doc.getObject("Folha_Legendas") or doc.addObject("TechDraw::DrawPage", "Folha_Legendas")
        if not page.Template:
            template = doc.addObject("TechDraw::DrawSVGTemplate", "Template_Legenda")
            template.Template = os.path.join(FreeCAD.getResourceDir(), "Mod", "TechDraw", "Templates", "A3_Landscape_ISO7200_NC.svg")
            page.Template = template

        # 3. Posicionar Símbolos e Textos
        y_start = 250
        x_start = 50
        y_step = 25
        
        for i, (sym_id, data) in enumerate(used_symbols.items()):
            y_pos = y_start - (i * y_step)
            
            # Vista do símbolo
            view = doc.addObject("TechDraw::DrawViewDraft", f"Legenda_View_{sym_id}")
            view.Source = data["obj"]
            page.addView(view)
            view.X = x_start
            view.Y = y_pos
            view.Scale = 1.0
            
            # Texto da descrição
            text = doc.addObject("TechDraw::DrawViewAnnotation", f"Legenda_Text_{sym_id}")
            text.Text = [data["desc"]]
            page.addView(text)
            text.X = x_start + 60
            text.Y = y_pos
        
        doc.recompute()
        FreeCAD.Console.PrintMessage("Legenda Gráfica gerada no TechDraw!\n")
        return page
