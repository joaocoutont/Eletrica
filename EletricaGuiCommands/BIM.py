import os
import FreeCAD
import FreeCADGui
from PySide import QtWidgets
from EletricaLogic.i18n import tr

ICON_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Icons")

class InsertSocket:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Socket.svg'), 'MenuText': tr('Inserir Tomada (TUG)'), 'ToolTip': tr('Insere tomada de uso geral') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Socket_TUG.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertSpecialSocket:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Socket.svg'), 'MenuText': tr('Inserir Tomada (TUE)'), 'ToolTip': tr('Insere tomada de uso específico (Ex: Chuveiro, Forno)') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Socket_TUE.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertLight:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Light.svg'), 'MenuText': tr('Inserir Luminária'), 'ToolTip': tr('Insere ponto de iluminação') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Light_Ceiling.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertSwitch:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Switch.svg'), 'MenuText': tr('Inserir Interruptor'), 'ToolTip': tr('Insere interruptor simples ou paralelo') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Switch_Simple.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class MergeSwitches:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Switch.svg'), 'MenuText': tr('Agrupar Interruptores'), 'ToolTip': tr('Transforma interruptores individuais em um conjunto') }
    def Activated(self):
        pass

class InsertSmartDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SmartHome.svg'), 'MenuText': tr('Dispositivo IoT'), 'ToolTip': tr('Insere atuadores ou sensores inteligentes') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("SmartRelay.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertAirConditioner:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AirConditioner.svg'), 'MenuText': tr('Ar Condicionado'), 'ToolTip': tr('Insere unidade evaporadora/condensadora') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("AC_Split.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertPumpSet:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Pump.svg'), 'MenuText': tr('Conjunto Motobomba'), 'ToolTip': tr('Insere bomba de recalque ou incêndio') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("WaterPump.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class LinkPumpSet:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Link.svg'), 'MenuText': tr('Vincular Bomba'), 'ToolTip': tr('Associa bomba ao seu quadro de comando') }
    def Activated(self):
        pass

class InsertBoreholePump:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BoreholePump.svg'), 'MenuText': tr('Bomba de Poço Artasiano'), 'ToolTip': tr('Insere bomba submersa profunda') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("SubmersiblePump.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class BIMifyEquipment:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIMify.svg'), 'MenuText': tr('BIMificar Objeto'), 'ToolTip': tr('Transforma um sólido genérico em componente elétrico inteligente') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        LibraryManager.bimify_selection()

class InsertEVCharger:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'EVCharger.svg'), 'MenuText': tr('Carregador de Veículo Elétrico'), 'ToolTip': tr('Insere estação de recarga (Wallbox)') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("EV_Wallbox.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")
