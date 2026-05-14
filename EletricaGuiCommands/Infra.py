import os
import FreeCAD
import FreeCADGui
from PySide import QtWidgets
from EletricaLogic.i18n import tr

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Icons")

class InsertConduit:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Conduit.svg'), 'MenuText': tr('Desenhar Eletroduto'), 'ToolTip': tr('Lança eletroduto flexível ou rígido') }
    def Activated(self):
        pass

class InsertCableTray:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Tray.svg'), 'MenuText': tr('Lançar Eletrocalha'), 'ToolTip': tr('Lança eletrocalha, aramado ou leito de cabos') }
    def Activated(self):
        pass

class AutoRouteWires:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AutoPlacement.svg'), 'MenuText': tr('Fiação Automática'), 'ToolTip': tr('Gera fiação lógica baseada em circuitos') }
    def Activated(self):
        pass

class CheckConduitFill:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Auditor.svg'), 'MenuText': tr('Taxa de Ocupação'), 'ToolTip': tr('Verifica se a ocupação do eletroduto respeita os 40% (NBR 5410)') }
    def Activated(self):
        pass

class InsertPullBox:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingBox.svg'), 'MenuText': tr('Caixa de Passagem'), 'ToolTip': tr('Insere caixa 4x2, 4x4 ou caixas de inspeção') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Box_4x2.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertFitting:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Structure.svg'), 'MenuText': tr('Curva/Conector'), 'ToolTip': tr('Adiciona conexões e conexões de infraestrutura') }
    def Activated(self):
        pass

class IntelligentAutoRoute:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AutoPlacement.svg'), 'MenuText': tr('Auto-Roteamento IA'), 'ToolTip': tr('Encontra o caminho mais curto e otimizado para a infraestrutura') }
    def Activated(self):
        pass

class InsertUndergroundDuct:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Conduit.svg'), 'MenuText': tr('Duto Subterrâneo'), 'ToolTip': tr('Insere duto para rede enterrada') }
    def Activated(self):
        pass

class InsertTrench:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Tray.svg'), 'MenuText': tr('Lançar Valeta'), 'ToolTip': tr('Desenha valeta técnica para cabos') }
    def Activated(self):
        pass

class InsertManhole:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingBox.svg'), 'MenuText': tr('Poço de Visita'), 'ToolTip': tr('Insere PV para redes subterrâneas') }
    def Activated(self):
        pass

class InsertBuswayDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Busway.svg'), 'MenuText': tr('Barramento Blindado'), 'ToolTip': tr('Insere trecho de Busway') }
    def Activated(self):
        pass
