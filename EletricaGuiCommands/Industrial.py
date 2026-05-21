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
    """Helper inteligente para inserção de componentes com Undo/Redo e Move."""
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

class InsertMTCubicle:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'MTCubicle.svg'), 'MenuText': tr('Cubículo de MT'), 'ToolTip': tr('Insere cubículo blindado de proteção/medição em MT') }
    def Activated(self):
        insert_component_smart("MT_Cubicle_Generic.FCStd", tr("Cubiculo MT"))

class InsertGenerator:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Generator.svg'), 'MenuText': tr('Grupo Moto-Gerador'), 'ToolTip': tr('Insere GMG para energia de emergência') }
    def Activated(self):
        insert_component_smart("Generator_150kVA.FCStd", tr("Gerador 150kVA"))

class InsertUPS:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'UPS.svg'), 'MenuText': tr('Nobreak (UPS)'), 'ToolTip': tr('Insere sistema de energia ininterrupta') }
    def Activated(self):
        insert_component_smart("UPS_Rack.FCStd", tr("Nobreak UPS"))

class InsertQTA:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'QTA.svg'), 'MenuText': tr('Quadro de Transferência (QTA)'), 'ToolTip': tr('Insere chave de transferência automática Rede/Gerador') }
    def Activated(self):
        insert_component_smart("QTA_Panel.FCStd", tr("Quadro QTA"))

class InsertPanel:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'IndustrialPanel.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Inserir Quadro BIM'), 
            'ToolTip': tr('Insere quadros de distribuição, comando ou CCM paramétricos (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.panel_gui import PanelCommand
        cmd = PanelCommand()
        cmd.command_name = "Eletrica_InsertPanel"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.panel_gui import PanelCommand
                if isinstance(active_cmd, PanelCommand):
                    return True
        except Exception:
            pass
        return False

class InsertMotor:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'MotorStarter.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Inserir Motor'), 
            'ToolTip': tr('Insere motor elétrico WEG/Industrial com dados de carcaça (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.motor_gui import MotorCommand
        cmd = MotorCommand()
        cmd.command_name = "Eletrica_InsertMotor"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.motor_gui import MotorCommand
                if isinstance(active_cmd, MotorCommand):
                    return True
        except Exception:
            pass
        return False

class SetupMotorWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Instrumentation.svg'), 'MenuText': tr('Dimensionar Partida'), 'ToolTip': tr('Wizard para dimensionamento de partida Estrela-Triângulo/Soft-Starter') }
    def Activated(self):
        from EletricaLogic.Starters import StarterManager
        StarterManager.open_wizard()

class InsertDataDevice:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'Telecom.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Ponto de Dados/Telecom'), 
            'ToolTip': tr('Insere tomada RJ45, RJ11, TV ou Fibra com simbologia NBR (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.data_point_gui import DataPointCommand
        cmd = DataPointCommand()
        cmd.command_name = "Eletrica_InsertDataDevice"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.data_point_gui import DataPointCommand
                if isinstance(active_cmd, DataPointCommand):
                    return True
        except Exception:
            pass
        return False

class InsertPLC:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'PLC.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Inserir CLP'), 
            'ToolTip': tr('Insere Controlador Lógico Programável e módulos de expansão (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.plc_gui import PLCCommand
        cmd = PLCCommand()
        cmd.command_name = "Eletrica_InsertPLC"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.plc_gui import PLCCommand
                if isinstance(active_cmd, PLCCommand):
                    return True
        except Exception:
            pass
        return False

class InsertHMI:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'HMI.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Inserir IHM'), 
            'ToolTip': tr('Insere Interface Homem-Máquina e painéis touch (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.hmi_gui import HMICommand
        cmd = HMICommand()
        cmd.command_name = "Eletrica_InsertHMI"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.hmi_gui import HMICommand
                if isinstance(active_cmd, HMICommand):
                    return True
        except Exception:
            pass
        return False

class CCMCommandDiagram:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'CCMDiagram.svg'), 'MenuText': tr('Diagrama de Comando'), 'ToolTip': tr('Gera diagrama funcional da partida do CCM') }
    def Activated(self):
        from EletricaLogic.ControlDiagrams import DiagramManager
        DiagramManager.generate_motor_control()

class InsertEmergencyLight:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'EmergencyLight.svg'), 'MenuText': tr('Luz de Emergência'), 'ToolTip': tr('Insere bloco autônomo de iluminação de emergência') }
    def Activated(self):
        insert_component_smart("Emergency_Light_LED.FCStd", tr("Luz Emergencia"))

class InsertExitSign:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ExitSign.svg'), 'MenuText': tr('Sinalização de Saída'), 'ToolTip': tr('Insere placa de saída iluminada (S1/S2)') }
    def Activated(self):
        insert_component_smart("Exit_Sign_S1.FCStd", tr("Sinalizacao Saida"))

class InsertGroundingRod:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingRod.svg'), 'MenuText': tr('Haste de Terra'), 'ToolTip': tr('Insere haste de aterramento (Alta Camada)') }
    def Activated(self):
        insert_component_smart("Grounding_Rod_3_4.FCStd", tr("Haste de Terra"))

class InsertGroundingMesh:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingMesh.svg'), 'MenuText': tr('Malha de Terra'), 'ToolTip': tr('Desenha malha de aterramento equipotencial') }
    def Activated(self):
        from EletricaLogic.Grounding import GroundingManager
        GroundingManager.start_mesh_tool()

class InsertBareCable:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BareCable.svg'), 'MenuText': tr('Cabo Nu'), 'ToolTip': tr('Lança condutor de proteção/equipotencialização nu') }
    def Activated(self):
        insert_component_smart("Bare_Copper_50mm2.FCStd", tr("Cabo de Cobre Nu"))

class InsertBEP:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BEP.svg'), 'MenuText': tr('Barramento de Equipotencialização (BEP)'), 'ToolTip': tr('Insere BEP ou BEL') }
    def Activated(self):
        insert_component_smart("BEP_Bar_10_Ways.FCStd", tr("Barramento BEP"))

class InsertGroundingBox:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingBox.svg'), 'MenuText': tr('Caixa de Inspeção'), 'ToolTip': tr('Insere caixa de inspeção do terra') }
    def Activated(self):
        insert_component_smart("Grounding_Box_Circular.FCStd", tr("Caixa de Inspecao"))

class GenerateGroundingReport:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingReport.svg'), 'MenuText': tr('Relatório de Aterramento'), 'ToolTip': tr('Gera memória de cálculo da resistência de terra') }
    def Activated(self):
        from EletricaLogic.Grounding import GroundingManager
        GroundingManager.calculate_and_report()

class SPDAWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SPDA.svg'), 'MenuText': tr('Assistente de SPDA'), 'ToolTip': tr('Dimensiona proteção contra descargas atmosféricas (Franklin/Gaiola)') }
    def Activated(self):
        from EletricaLogic.SPDA import SPDAManager
        SPDAWizard_Dialog().show()

class SolarWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SolarWizard.svg'), 'MenuText': tr('Assistente Solar'), 'ToolTip': tr('Configura arranjos e strings fotovoltaicas') }
    def Activated(self):
        from EletricaLogic.Solar import SolarManager
        SolarManager.open_config_wizard()

class SolarAnalysis:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Heatmap.svg'), 'MenuText': tr('Simulação Solar'), 'ToolTip': tr('Calcula geração anual baseada em dados NASA/METEONORM') }
    def Activated(self):
        from EletricaLogic.Solar import SolarManager
        SolarManager.run_full_analysis()

class InsertSolarPanel:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SolarPanel.svg'), 'MenuText': tr('Módulo Fotovoltaico'), 'ToolTip': tr('Insere painel solar com rastreamento') }
    def Activated(self):
        insert_component_smart("Solar_Panel_550W.FCStd", tr("Painel Solar"))

class InsertSolarInverter:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Solar.svg'), 'MenuText': tr('Inversor Solar'), 'ToolTip': tr('Insere inversor de string ou micro-inversor') }
    def Activated(self):
        insert_component_smart("Solar_Inverter_10kW.FCStd", tr("Inversor Solar"))

class InsertAutomationDevice:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'Automation.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Sensor/Atuador Industrial'), 
            'ToolTip': tr('Insere sensores de nível, pressão, vazão e atuadores (Mira BIM/ISA-5.1)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.industrial_device_gui import IndustrialDeviceCommand
        cmd = IndustrialDeviceCommand()
        cmd.command_name = "Eletrica_InsertAutomationDevice"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.industrial_device_gui import IndustrialDeviceCommand
                if isinstance(active_cmd, IndustrialDeviceCommand):
                    return True
        except Exception:
            pass
        return False

class InsertFireDevice:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'Fire.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Detector de Incêndio'), 
            'ToolTip': tr('Insere detectores de fumaça, calor e acionadores (Mira BIM/NBR 17240)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.fire_device_gui import FireDeviceCommand
        cmd = FireDeviceCommand()
        cmd.command_name = "Eletrica_InsertFireDevice"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.fire_device_gui import FireDeviceCommand
                if isinstance(active_cmd, FireDeviceCommand):
                    return True
        except Exception:
            pass
        return False

class InsertSecurityDevice:
    def GetResources(self):
        icon_path = os.path.join(ICON_DIR, 'Camera.svg')
        return { 
            'Pixmap': icon_path, 
            'MenuText': tr('Câmera/Segurança'), 
            'ToolTip': tr('Insere CFTV, sensores de intrusão ou controle de acesso (Mira BIM)'),
            'Checkable': True
        }
    def Activated(self, *args, **kwargs):
        from GeometryScripts.security_device_gui import SecurityDeviceCommand
        cmd = SecurityDeviceCommand()
        cmd.command_name = "Eletrica_InsertSecurityDevice"
        cmd.Activated(*args, **kwargs)

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                from GeometryScripts.security_device_gui import SecurityDeviceCommand
                if isinstance(active_cmd, SecurityDeviceCommand):
                    return True
        except Exception:
            pass
        return False

class InsertSoundDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SoundDevice.svg'), 'MenuText': tr('Sonorização'), 'ToolTip': tr('Insere caixas de som e amplificadores') }
    def Activated(self):
        insert_component_smart("Sound_Speaker_Ceiling.FCStd", tr("Arandela de Som"))
