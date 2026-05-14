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

class InsertPLC:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PLC.svg'), 'MenuText': tr('Inserir CLP'), 'ToolTip': tr('Insere Controlador Lógico Programável') }
    def Activated(self):
        pass

class InsertHMI:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'HMI.svg'), 'MenuText': tr('Inserir IHM'), 'ToolTip': tr('Insere Interface Homem-Máquina') }
    def Activated(self):
        pass

class CCMCommandDiagram:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'CCMDiagram.svg'), 'MenuText': tr('Diagrama de Comando'), 'ToolTip': tr('Gera diagrama funcional da partida do CCM') }
    def Activated(self):
        pass

class InsertEmergencyLight:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'EmergencyLight.svg'), 'MenuText': tr('Luz de Emergência'), 'ToolTip': tr('Insere bloco autônomo de iluminação de emergência') }
    def Activated(self):
        pass

class InsertExitSign:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ExitSign.svg'), 'MenuText': tr('Sinalização de Saída'), 'ToolTip': tr('Insere placa de saída iluminada (S1/S2)') }
    def Activated(self):
        pass

class InsertGroundingRod:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingRod.svg'), 'MenuText': tr('Haste de Terra'), 'ToolTip': tr('Insere haste de aterramento (Alta Camada)') }
    def Activated(self):
        pass

class InsertGroundingMesh:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingMesh.svg'), 'MenuText': tr('Malha de Terra'), 'ToolTip': tr('Desenha malha de aterramento equipotencial') }
    def Activated(self):
        pass

class InsertBareCable:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BareCable.svg'), 'MenuText': tr('Cabo Nu'), 'ToolTip': tr('Lança condutor de proteção/equipotencialização nu') }
    def Activated(self):
        pass

class InsertBEP:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BEP.svg'), 'MenuText': tr('Barramento de Equipotencialização (BEP)'), 'ToolTip': tr('Insere BEP ou BEL') }
    def Activated(self):
        pass

class InsertGroundingBox:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingBox.svg'), 'MenuText': tr('Caixa de Inspeção'), 'ToolTip': tr('Insere caixa de inspeção do terra') }
    def Activated(self):
        pass

class GenerateGroundingReport:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingReport.svg'), 'MenuText': tr('Relatório de Aterramento'), 'ToolTip': tr('Gera memória de cálculo da resistência de terra') }
    def Activated(self):
        pass

class SPDAWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SPDA.svg'), 'MenuText': tr('Assistente de SPDA'), 'ToolTip': tr('Dimensiona proteção contra descargas atmosféricas (Franklin/Gaiola)') }
    def Activated(self):
        pass

class SolarWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SolarWizard.svg'), 'MenuText': tr('Assistente Solar'), 'ToolTip': tr('Configura arranjos e strings fotovoltaicas') }
    def Activated(self):
        pass

class SolarAnalysis:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Solar.svg'), 'MenuText': tr('Simulação Solar'), 'ToolTip': tr('Calcula geração anual baseada em dados NASA/METEONORM') }
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
        return { 'Pixmap': os.path.join(ICON_DIR, 'Safety.svg'), 'MenuText': tr('Câmera/Segurança'), 'ToolTip': tr('Insere CFTV, sensores de intrusão ou controle de acesso') }
    def Activated(self):
        pass

class InsertSoundDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Telecom.svg'), 'MenuText': tr('Sonorização'), 'ToolTip': tr('Insere caixas de som e amplificadores') }
    def Activated(self):
        pass
