import os
import FreeCAD
import FreeCADGui
from PySide import QtWidgets
from EletricaLogic.i18n import tr

ICON_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Icons")

class InsertPole:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Pole.svg'), 'MenuText': tr('Inserir Poste'), 'ToolTip': tr('Insere poste de concreto ou madeira (Padrão ABNT)') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Pole_DT_11_600.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class AutoPolePlacement:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AutoPlacement.svg'), 'MenuText': tr('Locação Automática'), 'ToolTip': tr('Distribui postes ao longo de um traçado GIS/Draft') }
    def Activated(self):
        pass

class GISConverter:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GIS.svg'), 'MenuText': tr('Conversor GIS'), 'ToolTip': tr('Converte coordenadas geográficas para o sistema local') }
    def Activated(self):
        pass

class InsertStructure:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Structure.svg'), 'MenuText': tr('Montar Estrutura'), 'ToolTip': tr('Adiciona cruzetas, isoladores e ferragens (N1, M1, etc)') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Structure_N1.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertPoleTransformer:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PoleTransformer.svg'), 'MenuText': tr('Transformador de Poste'), 'ToolTip': tr('Insere transformador de distribuição aérea') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Transformer_112_5.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertDistributionEquipment:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'IndustrialPanel.svg'), 'MenuText': tr('Equipamento de Rede'), 'ToolTip': tr('Insere chaves fusíveis, religadores ou seccionalizadores') }
    def Activated(self):
        pass

class InsertGuyWire:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GuyWire.svg'), 'MenuText': tr('Inserir Estai'), 'ToolTip': tr('Adiciona cabo de estaiamento para contrapostagem') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("GuyWire_Simple.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertPublicLighting:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Light.svg'), 'MenuText': tr('Iluminação Pública'), 'ToolTip': tr('Adiciona braços e luminárias IP ao poste') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("IP_LED_150W.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertPoleGrounding:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Grounding.svg'), 'MenuText': tr('Aterramento de Poste'), 'ToolTip': tr('Adiciona descida de terra e hastes na base do poste') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Grounding_Pole.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertFenceGrounding:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'FenceGrounding.svg'), 'MenuText': tr('Aterramento de Cerca'), 'ToolTip': tr('Aterra cercas que cruzam ou correm paralelas à rede MT') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Aterramento_Cerca_Rural.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertGuyGrounding:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GuyGrounding.svg'), 'MenuText': tr('Aterramento de Estai'), 'ToolTip': tr('Aterra o cabo de aço do estai para segurança contra contatos acidentais') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Aterramento_Estai.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertNetworkSignaling:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'NetworkSignaling.svg'), 'MenuText': tr('Sinalização de Rede'), 'ToolTip': tr('Insere placas de perigo, chapas anti-escalada e esferas') }
    def Activated(self):
        pass

class InsertAerialCable:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'CableTray.svg'), 'MenuText': tr('Lançar Cabo Aéreo'), 'ToolTip': tr('Desenha cabos de MT/BT entre postes com catenária automática') }
    def Activated(self):
        pass

class AerialLineWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AerialNetwork.svg'), 'MenuText': tr('Assistente de Redes'), 'ToolTip': tr('Wizard para cálculo mecânico e elétrico de redes aéreas') }
    def Activated(self):
        pass

class ExportKML:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GIS.svg'), 'MenuText': tr('Exportar para Google Earth'), 'ToolTip': tr('Gera arquivo KML com a rede georreferenciada') }
    def Activated(self):
        pass

class CreateRDUDrawing:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'DrawingSheet.svg'), 'MenuText': tr('Gerar Prancha RDU'), 'ToolTip': tr('Cria folha TechDraw com planta e detalhes da rede') }
    def Activated(self):
        pass

class GenerateRDUMemorial:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'TechnicalReport.svg'), 'MenuText': tr('Memorial Descritivo RDU'), 'ToolTip': tr('Gera memorial técnico para aprovação em concessionária') }
    def Activated(self):
        pass
