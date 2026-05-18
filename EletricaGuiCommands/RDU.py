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
    """Helper inteligente para inserção de componentes RDU."""
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

class InsertPole:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Pole.svg'), 'MenuText': tr('Inserir Poste'), 'ToolTip': tr('Insere poste de concreto ou madeira (Padrão ABNT)') }
    def Activated(self):
        insert_component_smart("Pole_DT_11_600.FCStd", tr("Poste de Concreto"))

class AutoPolePlacement:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AutoPlacement.svg'), 'MenuText': tr('Locação Automática'), 'ToolTip': tr('Distribui postes ao longo de um traçado GIS/Draft') }
    def Activated(self):
        from EletricaLogic.AerialNetwork import AerialManager
        AerialNetwork_PlacementDialog().show()

class GISConverter:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GIS.svg'), 'MenuText': tr('Conversor GIS'), 'ToolTip': tr('Converte coordenadas geográficas para o sistema local') }
    def Activated(self):
        from EletricaLogic.ProjectManager import GISManager
        GISManager.open_converter_ui()

class InsertStructure:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Structure.svg'), 'MenuText': tr('Montar Estrutura'), 'ToolTip': tr('Adiciona cruzetas, isoladores e ferragens (N1, M1, etc)') }
    def Activated(self):
        insert_component_smart("Structure_N1_Generic.FCStd", tr("Estrutura MT"))

class InsertPoleTransformer:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PoleTransformer.svg'), 'MenuText': tr('Transformador de Poste'), 'ToolTip': tr('Insere transformador de distribuição aérea') }
    def Activated(self):
        insert_component_smart("Transformer_112_5_kVA.FCStd", tr("Trafo de Poste"))

class InsertDistributionEquipment:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'IndustrialPanel.svg'), 'MenuText': tr('Equipamento de Rede'), 'ToolTip': tr('Insere chaves fusíveis, religadores ou seccionalizadores') }
    def Activated(self):
        insert_component_smart("Fuse_Cutout_15kV.FCStd", tr("Chave Fusivel"))

class InsertGuyWire:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GuyWire.svg'), 'MenuText': tr('Inserir Estai'), 'ToolTip': tr('Adiciona cabo de estaiamento para contrapostagem') }
    def Activated(self):
        insert_component_smart("Guy_Wire_Simple.FCStd", tr("Cabo de Estai"))

class InsertPublicLighting:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PublicLighting.svg'), 'MenuText': tr('Iluminação Pública'), 'ToolTip': tr('Adiciona braços e luminárias IP ao poste') }
    def Activated(self):
        insert_component_smart("IP_LED_Arm_Generic.FCStd", tr("Luminaria IP"))

class InsertPoleGrounding:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Grounding.svg'), 'MenuText': tr('Aterramento de Poste'), 'ToolTip': tr('Adiciona descida de terra e hastes na base do poste') }
    def Activated(self):
        insert_component_smart("Grounding_Pole_ABNT.FCStd", tr("Aterramento Poste"))

class InsertFenceGrounding:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'FenceGrounding.svg'), 'MenuText': tr('Aterramento de Cerca'), 'ToolTip': tr('Aterra cercas que cruzam ou correm paralelas à rede MT') }
    def Activated(self):
        insert_component_smart("Fence_Grounding_Rural.FCStd", tr("Aterramento Cerca"))

class InsertGuyGrounding:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GuyGrounding.svg'), 'MenuText': tr('Aterramento de Estai'), 'ToolTip': tr('Aterra o cabo de aço do estai para segurança contra contatos acidentais') }
    def Activated(self):
        insert_component_smart("Guy_Grounding_System.FCStd", tr("Aterramento Estai"))

class InsertNetworkSignaling:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'NetworkSignaling.svg'), 'MenuText': tr('Sinalização de Rede'), 'ToolTip': tr('Insere placas de perigo, chapas anti-escalada e esferas') }
    def Activated(self):
        insert_component_smart("Signaling_Danger_Plate.FCStd", tr("Placa de Perigo"))

class InsertAerialCable:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AerialNetwork.svg'), 'MenuText': tr('Lançar Cabo Aéreo'), 'ToolTip': tr('Desenha cabos de MT/BT entre postes com catenária automática') }
    def Activated(self):
        from EletricaLogic.AerialNetwork import AerialManager
        AerialManager.start_catenary_tool()

class AerialLineWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Generic_Tool.svg'), 'MenuText': tr('Assistente de Redes'), 'ToolTip': tr('Wizard para cálculo mecânico e elétrico de redes aéreas') }
    def Activated(self):
        from EletricaLogic.AerialNetwork import AerialManager
        AerialManager.open_network_wizard()

class ExportKML:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ExportKML.svg'), 'MenuText': tr('Exportar para Google Earth'), 'ToolTip': tr('Gera arquivo KML com a rede georreferenciada') }
    def Activated(self):
        from EletricaLogic.Exporter import DisciplineExporter
        DisciplineExporter.export_to_kml()

class CreateRDUDrawing:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'DrawingSheet.svg'), 'MenuText': tr('Gerar Prancha RDU'), 'ToolTip': tr('Cria folha TechDraw com planta e detalhes da rede') }
    def Activated(self):
        from EletricaLogic.Documentation import DocumentationManager
        DocumentationManager.create_rdu_sheet()

class GenerateRDUMemorial:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'TechnicalReport.svg'), 'MenuText': tr('Memorial Descritivo RDU'), 'ToolTip': tr('Gera memorial técnico para aprovação em concessionária') }
    def Activated(self):
        from EletricaLogic.Reporting import ReportManager
        ReportManager.generate_rdu_memorial()
