# GUI Commands for Eletrica Workbench
import FreeCAD
import FreeCADGui

class SyncTitleBlock:
    """Sincroniza o carimbo da folha TechDraw"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Sincronizar Carimbo (Selo)',
            'ToolTip': 'Preenche automaticamente os dados do cliente e RT na folha'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Diagrams import UnifilarGenerator
        selection = FreeCADGui.Selection.getSelection()
        page = next((obj for obj in selection if obj.isDerivedFrom("TechDraw::DrawPage")), None)
        
        if not page:
            from PySide2 import QtWidgets
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione uma Folha TechDraw na árvore.")
            return
            
        UnifilarGenerator.sync_title_block(page)

class GenerateBudget:
    """Gera o orçamento financeiro do projeto"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Orçamento (R$)',
            'ToolTip': 'Calcula o custo total de materiais do projeto'
        }

    def Activated(self):
        from EletricaLogic.BOM import BOMManager
        from EletricaLogic.Budget import BudgetManager
        from PySide2 import QtWidgets
        
        bom_data = BOMManager.get_bom_data() 
        budget_text = BudgetManager.generate_budget_report(bom_data)
        
        QtWidgets.QMessageBox.information(None, "Orçamento de Materiais", budget_text)

class InsertSocket:
    """Insere tomadas com presets de altura e deteccao de andar"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Tomada (TUG)',
            'ToolTip': 'Insere tomadas em alturas padronizadas (Baixa, Media, Alta)'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Library import LibraryManager
        import FreeCADGui
        
        # 1. Escolher Altura (Preset)
        heights = {"Baixa (0.30m)": 300, "Média (1.10m)": 1100, "Alta (2.10m)": 2100}
        pos, ok = QtWidgets.QInputDialog.getItem(None, "Altura da Tomada", "Selecione a Posicao:", list(heights.keys()), 0, False)
        if not ok: return
        z_offset = heights[pos]
        
        # 2. Detectar Andar (BuildingPart) ativo
        base_z = 0.0
        active_container = None
        
        selection = FreeCADGui.Selection.getSelection()
        for s in selection:
            if hasattr(s, "InList") and s.isDerivedFrom("App::Part"): 
                base_z = s.Placement.Base.z
                active_container = s
                break
        
        # 3. Inserir
        manager = LibraryManager()
        obj = manager.insert_component("Tomada_TUG.FCStd")
        if obj:
            obj.Placement.Base = FreeCAD.Vector(0, 0, base_z + z_offset)
            if active_container:
                active_container.addObject(obj)
            FreeCADGui.runCommand("Draft_Move")
