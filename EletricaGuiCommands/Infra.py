import os
import FreeCAD
import FreeCADGui
try:
    from PySide import QtWidgets
except ImportError:
    try:
        from PySide2 import QtWidgets
    except ImportError:
        from PySide6 import QtWidgets
from EletricaLogic.i18n import tr

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Icons")

def insert_component_smart(filename, label="Componente"):
    """Helper inteligente para inserção de componentes de Infraestrutura."""
    doc = FreeCAD.ActiveDocument
    if not doc: return
    
    doc.openTransaction(tr("Inserir ") + label)
    try:
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component(filename)
        if obj:
            obj.Label = label
            doc.commitTransaction()
            FreeCADGui.runCommand("Draft_Move")
            return obj
    except Exception as e:
        FreeCAD.Console.PrintError(f"Erro ao inserir {filename}: {str(e)}\n")
        doc.abortTransaction()
    return None

class InsertConduit:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Conduit.svg'), 'MenuText': tr('Desenhar Eletroduto'), 'ToolTip': tr('Lança eletroduto flexível ou rígido') }
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        ConduitManager.start_conduit_tool()

class InsertCableTray:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Tray.svg'), 'MenuText': tr('Lançar Eletrocalha'), 'ToolTip': tr('Lança eletrocalha, aramado ou leito de cabos') }
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        ConduitManager.start_cable_tray_tool()

class AutoRouteWires:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Wiring3D.svg'), 'MenuText': tr('Fiação Automática'), 'ToolTip': tr('Gera fiação lógica baseada em circuitos') }
    def Activated(self):
        from EletricaLogic.Wiring import WiringManager
        WiringManager.generate_all_3d_wiring()

class CheckConduitFill:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'TrayAssistant.svg'), 'MenuText': tr('Taxa de Ocupação'), 'ToolTip': tr('Verifica se a ocupação do eletroduto respeita os 40% (NBR 5410)') }
    def Activated(self):
        from EletricaLogic.Conduit import CableTrayCalculator
        CableTrayCalculator.run_fill_audit_ui()

class InsertPullBox:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingBox.svg'), 'MenuText': tr('Caixa de Passagem'), 'ToolTip': tr('Insere caixa 4x2, 4x4 ou caixas de inspeção') }
    def Activated(self):
        insert_component_smart("Box_4x4_PVC.FCStd", tr("Caixa de Passagem"))

class InsertFitting:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Structure.svg'), 'MenuText': tr('Curva/Conector'), 'ToolTip': tr('Adiciona conexões e conexões de infraestrutura') }
    def Activated(self):
        from EletricaLogic.Fittings import FittingManager
        FittingManager.auto_insert_fittings()

class IntelligentAutoRoute:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AutoPlacement.svg'), 'MenuText': tr('Auto-Roteamento IA'), 'ToolTip': tr('Encontra o caminho mais curto e otimizado para a infraestrutura') }
    def Activated(self):
        from EletricaLogic.AutoRouter import GenerativeRouter
        GenerativeRouter.optimize_infrastructure()

class InsertUndergroundDuct:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BareCable.svg'), 'MenuText': tr('Duto Subterrâneo'), 'ToolTip': tr('Insere duto para rede enterrada') }
    def Activated(self):
        insert_component_smart("Underground_Duct_100mm.FCStd", tr("Duto Subterraneo"))

class InsertTrench:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Generic_Tool.svg'), 'MenuText': tr('Lançar Valeta'), 'ToolTip': tr('Desenha valeta técnica para cabos') }
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        ConduitManager.start_trench_tool()

class InsertManhole:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Instrumentation.svg'), 'MenuText': tr('Poço de Visita'), 'ToolTip': tr('Insere PV para redes subterrâneas') }
    def Activated(self):
        insert_component_smart("Manhole_Concrete_60x60.FCStd", tr("Poco de Visita"))

class InsertBuswayDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Busway.svg'), 'MenuText': tr('Barramento Blindado'), 'ToolTip': tr('Insere trecho de Busway') }
    def Activated(self):
        insert_component_smart("Busway_Section_1000A.FCStd", tr("Trecho Busway"))
