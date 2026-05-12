# ⚡ SUITE ELITE BIM - Engenharia Elétrica
# Autor: João Couto
# Contato: joaocoutont@hotmail.com
# GUI Commands for Eletrica Workbench
import FreeCAD
import FreeCADGui
import os

# Caminho para os novos ícones desenhados
ICON_DIR = os.path.join(os.path.dirname(__file__), "Icons")

# --- COMPATIBILIDADE PYSIDE2 / PYSIDE6 (FreeCAD 1.1+) ---
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

# --- 1. GRUPO: INÍCIO E CONFIGURAÇÃO ---

class StartNewProject:
    """Cria um novo documento e prepara o ambiente de desenho"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'StartProject.png'),
            'MenuText': 'Iniciar Novo Projeto Elétrico',
            'ToolTip': 'Cria um novo documento e prepara o ambiente BIM'
        }

    def Activated(self):
        import FreeCADGui
        import Draft
        doc = FreeCAD.newDocument("Novo_Projeto_Eletrica")
        
        view = FreeCADGui.activeDocument().activeView()
        if view:
            view.viewAxometric()
            
        # Ativação resiliente da grade (FreeCAD 1.1)
        try:
            FreeCADGui.runCommand("Draft_Grid")
        except Exception:
            try:
                FreeCADGui.runCommand("Draft_ToggleGrid")
            except Exception:
                try:
                    Draft.get_grid().show()
                except:
                    FreeCAD.Console.PrintWarning("Dica: Ative a grade manualmente no menu Draft se necessario.\n")
            
        QtWidgets.QMessageBox.information(None, "Suite Elite", "Novo projeto iniciado! A tela de desenho está pronta.")

class ToggleDashboard:
    """Liga/Desliga o painel lateral de métricas"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Dashboard.png'),
            'MenuText': 'Abrir/Fechar Dashboard',
            'ToolTip': 'Alterna a visualização das métricas em tempo real'
        }

    def Activated(self):
        from EletricaPanel import toggle_dashboard
        toggle_dashboard()

# --- 2. GRUPO: MODELAGEM E CRIAÇÃO (BIM) ---

class CreatePanel:
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Panel.png'),
            'MenuText': 'Criar Painel (QDC / CCM)',
            'ToolTip': 'Cria um painel inteligente'
        }
    def Activated(self):
        from EletricaLogic.Panels import PanelManager
        name, ok = QtWidgets.QInputDialog.getText(None, "Novo Painel", "Nome do Painel:")
        if ok and name:
            PanelManager.create_panel(name)

class InsertSocket:
    """Insere tomadas com Assistente NBR 5410"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Socket.png'),
            'MenuText': 'Inserir Tomada',
            'ToolTip': 'Insere uma tomada com sugestão NBR 5410'
        }

    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        import FreeCADGui
        
        power, ok1 = QtWidgets.QInputDialog.getInt(None, "NBR 5410", "Potência (VA/W):", 100, 100, 15000, 100)
        if not ok1: return
        
        suggestion = "TUG (Uso Geral - 10A)"
        if power == 600: suggestion = "TUG (Cozinha - 10A)"
        elif power >= 1200: suggestion = "TUE (Específico - 20A)"
            
        types = ["TUG (Uso Geral - 10A)", "TUG (Cozinha - 10A)", "TUE (Específico - 20A)"]
        sel_type, ok2 = QtWidgets.QInputDialog.getItem(None, "Tipo", "Classificação:", types, types.index(suggestion), False)
        if not ok2: return
        
        heights = {"Baixa (0.30m)": 300, "Média (1.10m)": 1100, "Alta (2.10m)": 2100}
        pos, ok3 = QtWidgets.QInputDialog.getItem(None, "Altura", "Selecione a Altura:", list(heights.keys()), 1, False)
        if not ok3: return
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
        file_name = "Tomada_TUE.FCStd" if "TUE" in sel_type else "Tomada_TUG.FCStd"
        obj = manager.insert_component(file_name)
        
        if obj:
            obj.Placement.Base = FreeCAD.Vector(0, 0, base_z + z_offset)
            if not hasattr(obj, "Potencia"): obj.addProperty("App::PropertyInteger", "Potencia", "Eletrica")
            obj.Potencia = power
            if not hasattr(obj, "Classificacao"): obj.addProperty("App::PropertyString", "Classificacao", "Eletrica")
            obj.Classificacao = sel_type
            if active_container: active_container.addObject(obj)
            FreeCADGui.runCommand("Draft_Move")

class InsertLight:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Light.png'), 'MenuText': 'Inserir Iluminação', 'ToolTip': 'Ponto de luz'}
    def Activated(self):
        FreeCAD.Console.PrintMessage("Inserindo luz...\n")

class InsertSwitch:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Switch.png'), 'MenuText': 'Inserir Interruptor', 'ToolTip': 'Simples/Paralelo'}
    def Activated(self):
        from EletricaLogic.Lighting import LightingManager
        cmd, ok = QtWidgets.QInputDialog.getText(None, "Comando", "Letra (a, b...):", text="a")
        if ok: LightingManager.insert_switch("Simples", cmd)

class MergeSwitches:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Merge.png'), 'MenuText': 'Mesclar Placas', 'ToolTip': '2 ou 3 teclas'}
    def Activated(self):
        from EletricaLogic.Lighting import LightingManager
        LightingManager.merge_switches(FreeCADGui.Selection.getSelection())

class InsertSmartDevice:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Light.png'), 'MenuText': 'Inserir Smart/IoT', 'ToolTip': 'Automação'}
    def Activated(self):
        from EletricaLogic.SmartHome import SmartHomeManager
        SmartHomeManager.insert_smart_device("Hub Zigbee")

# --- 3. GRUPO: INFRAESTRUTURA ---

class CreateConduit:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Conduit.png'), 'MenuText': 'Criar Eletroduto', 'ToolTip': 'Tubo 3D'}
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        for obj in FreeCADGui.Selection.getSelection():
            if hasattr(obj, "Points"): ConduitManager.create_conduit(obj.Points)

class CreateCableTray:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Tray.png'), 'MenuText': 'Lançar Eletrocalha', 'ToolTip': 'Infra industrial'}
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        FreeCADGui.runCommand("Draft_Wire")
        wire = FreeCAD.ActiveDocument.Objects[-1]
        if hasattr(wire, "Points"): ConduitManager.create_cable_tray(wire.Points, 200, 100)

class CreateIndustrialConnection:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Merge.png'), 'MenuText': 'Finalizar p/ Motor', 'ToolTip': 'Sealtub/Gland'}
    def Activated(self):
        from EletricaLogic.Fittings import FittingManager
        for obj in FreeCADGui.Selection.getSelection():
            FittingManager.add_industrial_termination(obj, "M20")

class Generate3DWiring:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Unifilar.png'), 'MenuText': 'Gerar Fiação 3D (Cabos)', 'ToolTip': 'Cabos LOD 500'}
    def Activated(self):
        from EletricaLogic.Wiring import WiringManager
        for obj in FreeCADGui.Selection.getSelection():
            WiringManager.generate_3d_cables(obj)

# --- 4. GRUPO: ENGENHARIA E CÁLCULOS ---

class ServiceEntranceWizard:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Switch.png'), 'MenuText': 'Padrão de Entrada', 'ToolTip': 'Concessionária'}
    def Activated(self):
        QtWidgets.QMessageBox.information(None, "Padrão", "Assistente de Padrão de Entrada iniciado.")

class InsertSubstation:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Panel.png'), 'MenuText': 'Dimensionar Subestação', 'ToolTip': 'MT/AT'}
    def Activated(self):
        QtWidgets.QMessageBox.information(None, "MT", "Cálculo de Subestação iniciado.")

class InsertBoreholePump:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Audit.png'), 'MenuText': 'Bomba de Poço', 'ToolTip': 'Ebara/Submersa'}
    def Activated(self):
        QtWidgets.QMessageBox.information(None, "Poço", "Cálculo de Bomba Submersa.")

class DimensionMotorStarter:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Switch.png'), 'MenuText': 'Partida Motor (WEG)', 'ToolTip': 'Dimensionamento'}
    def Activated(self):
        QtWidgets.QMessageBox.information(None, "WEG", "Dimensionamento de Partida iniciado.")

class SetupEmergencyPower:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Panel.png'), 'MenuText': 'Gerador e QTA', 'ToolTip': 'Emergência'}
    def Activated(self):
        QtWidgets.QMessageBox.information(None, "Energia", "Configuração de Gerador iniciada.")

class CheckSelectivity:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Audit.png'), 'MenuText': 'Verificar Seletividade', 'ToolTip': 'Coordenação'}
    def Activated(self):
        QtWidgets.QMessageBox.information(None, "Seletividade", "Análise de Curva iniciada.")

# --- 5. GRUPO: DOCUMENTAÇÃO E SAÍDA ---

class GenerateLoadSchedule:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Unifilar.png'), 'MenuText': 'Quadro de Cargas', 'ToolTip': 'Tabela de Circuitos'}
    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule()

class GenerateCableSchedule:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Report.png'), 'MenuText': 'Lista de Cabos', 'ToolTip': 'De/Para'}
    def Activated(self):
        from EletricaLogic.CableSchedule import CableScheduleManager
        CableScheduleManager.export_to_spreadsheet()

class GenerateBudget:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Budget.png'), 'MenuText': 'Gerar Orçamento (BOM)', 'ToolTip': 'Custos'}
    def Activated(self):
        from EletricaLogic.Budget import BudgetManager
        BudgetManager.generate_budget_report({})

class GenerateUnifilar:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Unifilar.png'), 'MenuText': 'Diagrama Unifilar', 'ToolTip': 'Esquema'}
    def Activated(self):
        from EletricaLogic.Diagrams import UnifilarGenerator
        UnifilarGenerator.create_graphic_diagram(None)

class SyncTitleBlock:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'StartProject.png'), 'MenuText': 'Sincronizar Selo', 'ToolTip': 'TechDraw'}
    def Activated(self):
        from EletricaLogic.Diagrams import UnifilarGenerator
        UnifilarGenerator.sync_title_block(None)

class RunProjectAudit:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Audit.png'), 'MenuText': 'Auditoria Geral', 'ToolTip': 'Erros'}
    def Activated(self):
        from EletricaLogic.Auditor import ProjectAuditor
        ProjectAuditor.run_full_audit()

class RunSafetyAudit:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Audit.png'), 'MenuText': 'Segurança (NR-10)', 'ToolTip': 'Arco Elétrico'}
    def Activated(self):
        from EletricaLogic.Safety import SafetyManager
        SafetyManager.apply_safety_to_panel(None)

class GenerateProjectQR:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'StartProject.png'), 'MenuText': 'Gerar QR Code AR', 'ToolTip': 'Realidade Aumentada'}
    def Activated(self):
        from EletricaLogic.AR import ARManager
        ARManager.generate_project_qr_code(None)

class BIMifyEquipment:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Panel.png'), 'MenuText': 'BIMificar Objeto', 'ToolTip': 'Propriedades'}
    def Activated(self):
        from EletricaLogic.Equipment import EquipmentManager
        EquipmentManager.bimify_equipment(None, "Motor")

class ExportDisciplineBIM:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Report.png'), 'MenuText': 'Exportar BIM', 'ToolTip': 'IFC/STEP'}
    def Activated(self):
        from EletricaLogic.Exporter import DisciplineExporter
        DisciplineExporter.run_multi_export("Export")

class CloneFloor:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Panel.png'), 'MenuText': 'Replicar Redes (Andar)', 'ToolTip': 'Automação'}
    def Activated(self):
        from EletricaLogic.Automation import MultiStoreyManager
        MultiStoreyManager.clone_electrical_to_floor(None, None)

# --- REGISTRO DE COMANDOS ---
cmds = {
    'Eletrica_StartNewProject': StartNewProject(),
    'Eletrica_ToggleDashboard': ToggleDashboard(),
    'Eletrica_CreatePanel': CreatePanel(),
    'Eletrica_InsertSocket': InsertSocket(),
    'Eletrica_InsertLight': InsertLight(),
    'Eletrica_InsertSwitch': InsertSwitch(),
    'Eletrica_MergeSwitches': MergeSwitches(),
    'Eletrica_InsertSmartDevice': InsertSmartDevice(),
    'Eletrica_CreateConduit': CreateConduit(),
    'Eletrica_CreateCableTray': CreateCableTray(),
    'Eletrica_CreateIndustrialConnection': CreateIndustrialConnection(),
    'Eletrica_Generate3DWiring': Generate3DWiring(),
    'Eletrica_ServiceEntranceWizard': ServiceEntranceWizard(),
    'Eletrica_InsertSubstation': InsertSubstation(),
    'Eletrica_InsertBoreholePump': InsertBoreholePump(),
    'Eletrica_DimensionMotorStarter': DimensionMotorStarter(),
    'Eletrica_SetupEmergencyPower': SetupEmergencyPower(),
    'Eletrica_CheckSelectivity': CheckSelectivity(),
    'Eletrica_GenerateLoadSchedule': GenerateLoadSchedule(),
    'Eletrica_GenerateCableSchedule': GenerateCableSchedule(),
    'Eletrica_GenerateBudget': GenerateBudget(),
    'Eletrica_GenerateUnifilar': GenerateUnifilar(),
    'Eletrica_SyncTitleBlock': SyncTitleBlock(),
    'Eletrica_RunProjectAudit': RunProjectAudit(),
    'Eletrica_RunSafetyAudit': RunSafetyAudit(),
    'Eletrica_GenerateProjectQR': GenerateProjectQR(),
    'Eletrica_BIMifyEquipment': BIMifyEquipment(),
    'Eletrica_ExportDisciplineBIM': ExportDisciplineBIM(),
    'Eletrica_CloneFloor': CloneFloor()
}

for name, obj in cmds.items():
    FreeCADGui.addCommand(name, obj)
