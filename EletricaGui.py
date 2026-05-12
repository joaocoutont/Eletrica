# GUI Commands for Eletrica Workbench
import FreeCAD
import FreeCADGui

# --- CLASSES DE NEGÓCIO E ORÇAMENTO ---
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

# --- CLASSES DE INSERÇÃO ---
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
        
        heights = {"Baixa (0.30m)": 300, "Média (1.10m)": 1100, "Alta (2.10m)": 2100}
        pos, ok = QtWidgets.QInputDialog.getItem(None, "Altura da Tomada", "Selecione a Posicao:", list(heights.keys()), 0, False)
        if not ok: return
        z_offset = heights[pos]
        
        base_z = 0.0
        active_container = None
        selection = FreeCADGui.Selection.getSelection()
        for s in selection:
            if hasattr(s, "InList") and s.isDerivedFrom("App::Part"): 
                base_z = s.Placement.Base.z
                active_container = s
                break
        
        manager = LibraryManager()
        obj = manager.insert_component("Tomada_TUG.FCStd")
        if obj:
            obj.Placement.Base = FreeCAD.Vector(0, 0, base_z + z_offset)
            if active_container:
                active_container.addObject(obj)
            FreeCADGui.runCommand("Draft_Move")

class InsertLight:
    def GetResources(self):
        return {'Pixmap': 'freecad', 'MenuText': 'Inserir Iluminação', 'ToolTip': 'Insere um ponto de luz'}
    def Activated(self):
        FreeCAD.Console.PrintMessage("Inserir Iluminação\n")

# --- CLASSES DE INFRAESTRUTURA ---
class CreateConduit:
    def GetResources(self):
        return {'Pixmap': 'freecad', 'MenuText': 'Criar Eletroduto', 'ToolTip': 'Converte linha em tubo'}
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        selection = FreeCADGui.Selection.getSelection()
        for obj in selection:
            if hasattr(obj, "Points"): ConduitManager.create_conduit(obj.Points)

class CreateCableTray:
    def GetResources(self):
        return {'Pixmap': 'freecad', 'MenuText': 'Lançar Eletrocalha', 'ToolTip': 'Cria infra retangular'}
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        from EletricaLogic.Fittings import FittingManager
        from PySide2 import QtWidgets
        
        materials = ["Aço Galvanizado", "Alumínio", "Aço Inox"]
        mat, ok1 = QtWidgets.QInputDialog.getItem(None, "Material", "Material:", materials, 0, False)
        types = ["Lisa", "Perfurada", "Aramada"]
        ctype, ok2 = QtWidgets.QInputDialog.getItem(None, "Tipo", "Tipo:", types, 1, False)
        supports = ["Teto (Trapézio)", "Teto (Tirante Central)", "Parede", "Nenhum"]
        sup, ok3 = QtWidgets.QInputDialog.getItem(None, "Suporte", "Suporte:", supports, 0, False)
        
        if ok1 and ok2 and ok3:
            FreeCADGui.runCommand("Draft_Wire")
            doc = FreeCAD.ActiveDocument
            last_wire = doc.Objects[-1]
            if hasattr(last_wire, "Points"):
                tray = ConduitManager.create_cable_tray(last_wire.Points, 200, 100)
                FittingManager.add_tray_fittings(tray)
                if sup != "Nenhum":
                    s_type = "Teto_Central" if "Central" in sup else ("Teto_Trapezio" if "Trapézio" in sup else "Parede")
                    FittingManager.add_tray_supports(tray, support_type=s_type)
                doc.removeObject(last_wire.Name)

# --- CLASSES DE CÁLCULO E DOCUMENTAÇÃO ---
class GenerateLoadSchedule:
    def GetResources(self): return {'Pixmap': 'freecad', 'MenuText': 'Quadro de Cargas'}
    def Activated(self): 
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule()

class RunProjectAudit:
    def GetResources(self): return {'Pixmap': 'freecad', 'MenuText': 'Auditoria'}
    def Activated(self):
        from EletricaLogic.Auditor import ProjectAuditor
        from PySide2 import QtWidgets
        report = ProjectAuditor.run_full_audit()
        QtWidgets.QMessageBox.information(None, "Auditoria", str(report))

class GenerateUnifilar:
    def GetResources(self): return {'Pixmap': 'freecad', 'MenuText': 'Diagrama Unifilar'}
    def Activated(self):
        from EletricaLogic.Diagrams import UnifilarGenerator
        selection = FreeCADGui.Selection.getSelection()
        panel = next((obj for obj in selection if hasattr(obj, "TipoBIM")), None)
        if panel: UnifilarGenerator.create_graphic_diagram(panel)

class ToggleDashboard:
    """Liga/Desliga o painel lateral de métricas"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Abrir/Fechar Dashboard',
            'ToolTip': 'Alterna a visualização das métricas em tempo real'
        }

    def Activated(self):
        from EletricaPanel import toggle_dashboard
        toggle_dashboard()

class CloneFloor:
    """Clona a rede eletrica de um andar para outro"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Replicar Redes (Andar Tipo)',
            'ToolTip': 'Copia toda a rede eletrica do andar selecionado para outro andar'
        }

    def Activated(self):
        from EletricaLogic.Automation import MultiStoreyManager
        from PySide2 import QtWidgets
        import FreeCADGui
        
        selection = FreeCADGui.Selection.getSelection()
        if len(selection) < 2:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione o ANDAR ORIGEM e depois o ANDAR DESTINO (BuildingParts).")
            return
            
        MultiStoreyManager.clone_electrical_to_floor(selection[0], selection[1])

class Generate3DWiring:
    """Gera os cabos fisicos 3D dentro da infraestrutura"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Fiação 3D (LOD 500)',
            'ToolTip': 'Desenha os cabos reais dentro dos eletrodutos'
        }

    def Activated(self):
        from EletricaLogic.Wiring import WiringManager
        import FreeCADGui
        selection = FreeCADGui.Selection.getSelection()
        for obj in selection:
            WiringManager.generate_3d_cables(obj)

# --- REGISTRO DE COMANDOS ---
cmds = {
    'Eletrica_InsertSocket': InsertSocket(),
    'Eletrica_InsertLight': InsertLight(),
    'Eletrica_CreateConduit': CreateConduit(),
    'Eletrica_CreateCableTray': CreateCableTray(),
    'Eletrica_GenerateLoadSchedule': GenerateLoadSchedule(),
    'Eletrica_RunProjectAudit': RunProjectAudit(),
    'Eletrica_GenerateUnifilar': GenerateUnifilar(),
    'Eletrica_SyncTitleBlock': SyncTitleBlock(),
    'Eletrica_GenerateBudget': GenerateBudget(),
    'Eletrica_ToggleDashboard': ToggleDashboard(),
    'Eletrica_CloneFloor': CloneFloor(),
    'Eletrica_Generate3DWiring': Generate3DWiring()
}

for name, obj in cmds.items():
    FreeCADGui.addCommand(name, obj)

# (Outros comandos simplificados para manter o arquivo funcional)
class Placeholder:
    def GetResources(self): return {'Pixmap': 'freecad', 'MenuText': 'Comando'}
    def Activated(self): pass

extra_cmds = [
    'Eletrica_OpenSettings', 'Eletrica_AnalyzeSpaceLighting', 'Eletrica_BalancePhases',
    'Eletrica_CalculateWiring', 'Eletrica_PrepareIFC', 'Eletrica_GenerateTags',
    'Eletrica_CheckConduitFill', 'Eletrica_GenerateBOM', 'Eletrica_GenerateWireSymbols',
    'Eletrica_GroundingCalculator', 'Eletrica_SPDAGui', 'Eletrica_SPDARiskWizard',
    'Eletrica_InsertTUE', 'Eletrica_InsertServiceEntrance', 'Eletrica_AutoConnectSequence',
    'Eletrica_AutoConnectCeiling', 'Eletrica_ApplyHeatmap', 'Eletrica_AssignCircuitToConduit',
    'Eletrica_ClearConduitCircuits', 'Eletrica_GenerateReport', 'Eletrica_SolarEstimate',
    'Eletrica_GeneratePanelLabels', 'Eletrica_CreateExposedConduit', 'Eletrica_GenerateRiseFallSymbols',
    'Eletrica_AnnotateCircuits', 'Eletrica_ManageBoxes'
]

for name in extra_cmds:
    if name not in cmds:
        FreeCADGui.addCommand(name, Placeholder())
