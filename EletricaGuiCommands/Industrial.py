import os
import FreeCAD
import FreeCADGui
from PySide import QtWidgets
from EletricaLogic.i18n import tr

ICON_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Icons")

class InsertMTCubicle:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Substation.svg'), 'MenuText': tr('Cubículo de MT'), 'ToolTip': tr('Insere cubículo blindado de proteção/medição em MT') }
    def Activated(self):
        pass

class InsertGenerator:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Generator.svg'), 'MenuText': tr('Grupo Moto-Gerador'), 'ToolTip': tr('Insere GMG para energia de emergência') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Generator_150kVA.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertUPS:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'UPS.svg'), 'MenuText': tr('Nobreak (UPS)'), 'ToolTip': tr('Insere sistema de energia ininterrupta') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("UPS_Rack.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class InsertQTA:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'QTA.svg'), 'MenuText': tr('Quadro de Transferência (QTA)'), 'ToolTip': tr('Insere chave de transferência automática Rede/Gerador') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("QTA_Panel.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class CreatePanel:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Panel.svg'), 'MenuText': tr('Criar Quadro (QDC)'), 'ToolTip': tr('Cria quadro de distribuição inteligente') }
    def Activated(self):
        from EletricaLogic.Panels import PanelManager
        PanelManager.create_panel("QDC Novo")

class InsertCCM:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'IndustrialPanel.svg'), 'MenuText': tr('Centro de Controle (CCM)'), 'ToolTip': tr('Insere CCM para comando de motores') }
    def Activated(self):
        from EletricaLogic.Panels import PanelManager
        PanelManager.create_panel("CCM-01", "CCM")

class InsertMotor:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Motor.svg'), 'MenuText': tr('Inserir Motor'), 'ToolTip': tr('Insere motor elétrico WEG/Industrial') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        obj = lib.insert_component("Motor_WEG_W22.FCStd")
        if obj: FreeCADGui.runCommand("Draft_Move")

class SetupMotorWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Automation.svg'), 'MenuText': tr('Dimensionar Partida'), 'ToolTip': tr('Wizard para dimensionamento de partida Estrela-Triângulo/Soft-Starter') }
    def Activated(self):
        pass

class InsertDataDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Telecom.svg'), 'MenuText': tr('Ponto de Dados/Telecom'), 'ToolTip': tr('Insere tomada RJ45, Rack ou Switch') }
    def Activated(self):
        pass

class InsertAutomationDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Automation.svg'), 'MenuText': tr('Sensor/Atuador Industrial'), 'ToolTip': tr('Insere PLC, HMI ou sensores industriais') }
    def Activated(self):
        pass

class InsertFireDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Fire.svg'), 'MenuText': tr('Detector de Incêndio'), 'ToolTip': tr('Insere detector de fumaça/térmico ou acionador') }
    def Activated(self):
        pass

class InsertSecurityDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Security.svg'), 'MenuText': tr('Câmera/Segurança'), 'ToolTip': tr('Insere CFTV, sensores de intrusão ou controle de acesso') }
    def Activated(self):
        pass

class InsertSoundDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Sound.svg'), 'MenuText': tr('Sonorização'), 'ToolTip': tr('Insere caixas de som e amplificadores') }
    def Activated(self):
        pass

class InsertSolarPanel:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Solar.svg'), 'MenuText': tr('Módulo Fotovoltaico'), 'ToolTip': tr('Insere painel solar com rastreamento') }
    def Activated(self):
        pass

class InsertSolarInverter:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Solar.svg'), 'MenuText': tr('Inversor Solar'), 'ToolTip': tr('Insere inversor de string ou micro-inversor') }
    def Activated(self):
        pass

class SolarAnalysis:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Solar.svg'), 'MenuText': tr('Simulação Solar'), 'ToolTip': tr('Calcula geração anual baseada em dados NASA/METEONORM') }
    def Activated(self):
        pass
