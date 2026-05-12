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

class BIMifyEquipment:
    """Converte um objeto 3D qualquer em equipamento eletrico inteligente"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'BIMificar Objeto (Tornar Motor/Máquina)',
            'ToolTip': 'Injeta propriedades eletricas e de calculo em qualquer objeto 3D selecionado'
        }

    def Activated(self):
        from EletricaLogic.Equipment import EquipmentManager
        from PySide2 import QtWidgets
        import FreeCADGui
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione o objeto 3D que deseja transformar.")
            return
            
        types = ["Motor Elétrico", "Máquina Industrial", "Ponte Rolante", "Transformador", "Painel Especial"]
        choice, ok = QtWidgets.QInputDialog.getItem(None, "BIMify", "Tipo de Equipamento:", types, 0, False)
        
        if ok:
            for obj in selection:
                EquipmentManager.bimify_equipment(obj, equipment_type=choice)
            
            QtWidgets.QMessageBox.information(None, "Sucesso", "Propriedades elétricas injetadas! Preencha os dados na aba 'Eletrica' do objeto.")

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

class CreateIndustrialConnection:
    """Insere Sealtub e Prensa-Cabo no final da linha"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Finalizar p/ Motor (Sealtub/Prensa-Cabo)',
            'ToolTip': 'Converte o final da linha em flexível estanque e insere prensa-cabo'
        }

    def Activated(self):
        from EletricaLogic.Fittings import FittingManager
        from PySide2 import QtWidgets
        import FreeCADGui
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione o eletroduto que chega ao motor.")
            return
            
        types = ["PG11", "PG13.5", "PG16", "PG21", "M20", "M25"]
        gland, ok = QtWidgets.QInputDialog.getItem(None, "Prensa-Cabo", "Selecione o Tamanho:", types, 2, False)
        
        if ok:
            for obj in selection:
                FittingManager.add_industrial_termination(obj, gland_type=gland)

class GenerateProjectQR:
    """Gera QR Code para Realidade Aumentada na prancha"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Link de Realidade Aumentada (QR)',
            'ToolTip': 'Cria um QR Code que leva ao modelo 3D no celular'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.AR import ARManager
        selection = FreeCADGui.Selection.getSelection()
        page = next((obj for obj in selection if obj.isDerivedFrom("TechDraw::DrawPage")), None)
        
        if not page:
            from PySide2 import QtWidgets
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione a Folha TechDraw para inserir o QR Code.")
            return
            
        link = ARManager.generate_project_qr_code(page)
        from PySide2 import QtWidgets
        QtWidgets.QMessageBox.information(None, "AR Ready", f"QR Code vinculado à folha!\nLink: {link}")

class InsertSmartDevice:
    """Insere dispositivos de casa inteligente"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Dispositivo Smart / IoT',
            'ToolTip': 'Insere sensores, cameras e hubs de automação'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.SmartHome import SmartHomeManager
        
        presets = SmartHomeManager.get_automation_presets()
        choice, ok = QtWidgets.QInputDialog.getItem(None, "Automação", "Selecione o dispositivo:", list(presets.keys()), 0, False)
        
        if ok:
            SmartHomeManager.insert_smart_device(choice)

class CheckSelectivity:
    """Verifica a coordenacao entre disjuntores"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Verificar Seletividade (Geral x Circuito)',
            'ToolTip': 'Avalia se o disjuntor geral nao vai cair junto com o do circuito'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Calculator import ElectricalCalculator
        
        up, ok1 = QtWidgets.QInputDialog.getInt(None, "Seletividade", "Corrente Disjuntor Geral (A):", 50, 10, 1000, 1)
        down, ok2 = QtWidgets.QInputDialog.getInt(None, "Seletividade", "Corrente Disjuntor Circuito (A):", 20, 10, 1000, 1)
        
        if ok1 and ok2:
            is_ok, msg = ElectricalCalculator.check_breaker_selectivity(up, down)
            QtWidgets.QMessageBox.information(None, "Análise de Seletividade", msg)

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
    'Eletrica_BIMifyEquipment': BIMifyEquipment(),
    'Eletrica_GenerateProjectQR': GenerateProjectQR(),
    'Eletrica_InsertSmartDevice': InsertSmartDevice(),
    'Eletrica_CheckSelectivity': CheckSelectivity(),
    'Eletrica_CreateIndustrialConnection': CreateIndustrialConnection(),
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
