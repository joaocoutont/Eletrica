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

def get_socket_cmd(height_type="Média (1100mm)", special=False):
    """Retorna e ativa o comando de tomada pré-configurado."""
    from GeometryScripts.socket_gui import SocketCommand
    cmd = SocketCommand()
    cmd.z_level = 300.0 if "Baixa" in height_type else 1100.0
    if "Alta" in height_type: cmd.z_level = 2200.0
    
    if special:
        cmd.circuit_type = "TUE (Específico)"
        cmd.amperage = "20A"
    
    cmd.Activated()

def insert_component_smart(filename, label="Componente"):
    """Helper inteligente para inserção de componentes BIM."""
    doc = FreeCAD.ActiveDocument
    if not doc: return
    try:
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component(filename)
        if obj:
            obj.Label = label
            FreeCADGui.runCommand("Draft_Move")
    except:
        pass

class InsertSocket:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'Tomada_BR.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Inserir Tomada BIM'), 
            'ToolTip': tr('Insere tomada modular paramétrica (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.socket_gui import SocketCommand
        cmd = SocketCommand()
        cmd.command_name = "Eletrica_InsertSocket"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.socket_gui import SocketCommand
                if isinstance(active_cmd, SocketCommand) and getattr(active_cmd, "command_name", "") == "Eletrica_InsertSocket":
                    return True
                if isinstance(active_cmd, SocketCommand) and not getattr(active_cmd, "command_name", "") and getattr(active_cmd, "circuit_type", "") != "TUE (Específico)":
                    return True
        except Exception:
            pass
        return False

class InsertSpecialSocket:
    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(ICON_DIR, 'Tomada_TUE_BR.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Tomada Especial (TUE)'), 
            'ToolTip': tr('Insere tomada de Uso Especial com potência pré-configurada (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.special_socket_gui import SpecialSocketCommand
        cmd = SpecialSocketCommand()
        cmd.command_name = "Eletrica_InsertSpecialSocket"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.special_socket_gui import SpecialSocketCommand
                if isinstance(active_cmd, SpecialSocketCommand):
                    return True
        except Exception:
            pass
        return False

class InsertModularSet:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'Switch.svg')
        return {
            'Pixmap': icon_path,
            'MenuText': tr('Conjunto Modular'),
            'ToolTip': tr('Insere placa 4x2 com modulos combinados, como interruptor + tomada (Mira BIM)'),
            'Checkable': True
        }

    def Activated(self, *args, **kwargs):
        from GeometryScripts.modular_set_gui import ModularSetCommand
        cmd = ModularSetCommand()
        cmd.command_name = "Eletrica_InsertModularSet"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.modular_set_gui import ModularSetCommand
                if isinstance(active_cmd, ModularSetCommand):
                    return True
        except Exception:
            pass
        return False

class InsertLight:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'Light.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Inserir Luminária'), 
            'ToolTip': tr('Insere ponto de iluminação com dados fotométricos e simbologia NBR (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.light_gui import LightCommand
        cmd = LightCommand()
        cmd.command_name = "Eletrica_InsertLight"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.light_gui import LightCommand
                if isinstance(active_cmd, LightCommand):
                    return True
        except Exception:
            pass
        return False

class InsertSwitch:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'Switch.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Inserir Interruptor'), 
            'ToolTip': tr('Insere interruptor simples ou paralelo (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.switch_gui import SwitchCommand
        cmd = SwitchCommand()
        cmd.command_name = "Eletrica_InsertSwitch"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.switch_gui import SwitchCommand
                if isinstance(active_cmd, SwitchCommand):
                    return True
        except Exception:
            pass
        return False

class MergeSwitches:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Merge.svg'), 'MenuText': tr('Agrupar Interruptores'), 'ToolTip': tr('Transforma interruptores individuais em um conjunto') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        LibraryManager.group_selected_switches()

class InsertSmartDevice:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'SmartHome.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Dispositivo IoT'), 
            'ToolTip': tr('Insere atuadores ou sensores inteligentes (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.iot_gui import IoTCommand
        cmd = IoTCommand()
        cmd.command_name = "Eletrica_InsertSmartDevice"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.iot_gui import IoTCommand
                if isinstance(active_cmd, IoTCommand):
                    return True
        except Exception:
            pass
        return False

class InsertAirConditioner:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'AirConditioning.svg')
        return {
            'Pixmap': icon_path,
            'MenuText': tr('Ar Condicionado'),
            'ToolTip': tr('Insere tomada para Ar Condicionado com seleção por BTU e Fases (Mira BIM)'),
            'Checkable': True
        }

    def Activated(self, *args, **kwargs):
        from GeometryScripts.ac_socket_gui import ACSocketCommand
        cmd = ACSocketCommand()
        cmd.command_name = "Eletrica_InsertAirConditioner"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.ac_socket_gui import ACSocketCommand
                if isinstance(active_cmd, ACSocketCommand):
                    return True
        except Exception:
            pass
        return False

class InsertPumpSet:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PumpSet.svg'), 'MenuText': tr('Conjunto Motobomba'), 'ToolTip': tr('Insere bomba de recalque ou incêndio') }
    def Activated(self): insert_component_smart("WaterPump.FCStd", tr("Motobomba"))

class LinkPumpSet:
    RequiredSelection = "Bomba"
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Generic_Tool.svg'), 'MenuText': tr('Vincular Bomba'), 'ToolTip': tr('Associa bomba ao seu quadro de comando') }
    def Activated(self):
        from EletricaLogic.BoreholePumps import PumpManager
        PumpManager.link_pump_to_panel()

class InsertBoreholePump:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Pump.svg'), 'MenuText': tr('Bomba de Poço Artasiano'), 'ToolTip': tr('Insere bomba submersa profunda') }
    def Activated(self): insert_component_smart("SubmersiblePump.FCStd", tr("Bomba Poco"))

class BIMifyEquipment:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIMify.svg'), 'MenuText': tr('BIMificar Objeto'), 'ToolTip': tr('Transforma um sólido genérico em componente elétrico inteligente') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        LibraryManager.bimify_selection()

class InsertEVCharger:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'EVCharger.svg'), 'MenuText': tr('Carregador de Veículo Elétrico'), 'ToolTip': tr('Insere estação de recarga (Wallbox)') }
    def Activated(self): insert_component_smart("EV_Wallbox.FCStd", tr("Wallbox EV"))

class InsertServiceEntrance:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ServiceEntrance.svg'), 'MenuText': tr('Entrada de Serviço'), 'ToolTip': tr('Cria um padrão de entrada paramétrico') }
    def Activated(self):
        from EletricaLogic.ServiceEntrance import create_service_entrance
        create_service_entrance(tr("Entrada_Servico"))
