# Gerador de Documentacao Tecnica (TechDraw)
import FreeCAD
import TechDraw

class DocumentationManager:
    @staticmethod
    def create_technical_sheet():
        """
        Cria uma pagina no TechDraw e insere as planilhas de Quadro de Cargas e Legenda.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        # 1. Criar a Pagina TechDraw (se nao existir)
        page_name = "Folha_Projeto_Eletrico"
        page = doc.getObject(page_name)
        if not page:
            page = doc.addObject('TechDraw::DrawPage', page_name)
            # Usar um template padrao (A3 Landscape)
            template = doc.addObject('TechDraw::DrawSVGTemplate', 'Template')
            template.Template = FreeCAD.getResourceDir() + 'Mod/TechDraw/Templates/A3_Landscape_ISO7200.svg'
            page.Template = template
            
        # 2. Inserir o Quadro de Cargas
        sheet_qc = doc.getObject("Quadro_de_Cargas")
        if sheet_qc:
            view_qc = doc.addObject('TechDraw::DrawViewSpreadsheet', 'Vista_Quadro_Cargas')
            view_qc.Source = sheet_qc
            page.addView(view_qc)
            view_qc.X = 50
            view_qc.Y = 250
            
        # 3. Inserir a Legenda
        sheet_leg = doc.getObject("Legenda_de_Simbolos")
        if sheet_leg:
            view_leg = doc.addObject('TechDraw::DrawViewSpreadsheet', 'Vista_Legenda')
            view_leg.Source = sheet_leg
            page.addView(view_leg)
            view_leg.X = 50
            view_leg.Y = 100
            
        doc.recompute()
        FreeCAD.Console.PrintMessage("Prancha tecnica gerada no Workbench TechDraw!\n")
        return page
