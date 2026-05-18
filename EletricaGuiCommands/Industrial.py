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

class CreatePanel:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Panel.svg'), 'MenuText': tr('Criar Quadro (QDC)'), 'ToolTip': tr('Cria quadro de distribution inteligente') }
    def Activated(self):
        from EletricaLogic.Panels import PanelManager
        doc = FreeCAD.ActiveDocument
        doc.openTransaction(tr("Criar Quadro"))
        PanelManager.create_panel(tr("QDC Novo"))
        doc.commitTransaction()

class InsertCCM:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'IndustrialPanel.svg'), 'MenuText': tr('Centro de Controle (CCM)'), 'ToolTip': tr('Insere CCM para comando de motores') }
    def Activated(self):
        from EletricaLogic.Panels import PanelManager
        doc = FreeCAD.ActiveDocument
        doc.openTransaction(tr("Criar CCM"))
        PanelManager.create_panel(tr("CCM-01"), "CCM")
        doc.commitTransaction()

class InsertMotor:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'MotorStarter.svg'), 'MenuText': tr('Inserir Motor'), 'ToolTip': tr('Insere motor elétrico WEG/Industrial') }
    def Activated(self):
        insert_component_smart("Motor_WEG_W22.FCStd", tr("Motor Eletrico"))

class SetupMotorWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Instrumentation.svg'), 'MenuText': tr('Dimensionar Partida'), 'ToolTip': tr('Wizard para dimensionamento de partida Estrela-Triângulo/Soft-Starter') }
    def Activated(self):
        from EletricaLogic.Starters import StarterManager
        StarterManager.open_wizard()

class InsertDataDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Telecom.svg'), 'MenuText': tr('Ponto de Dados/Telecom'), 'ToolTip': tr('Insere tomada RJ45, Rack ou Switch') }
    def Activated(self):
        insert_component_smart("Data_Outlet_RJ45.FCStd", tr("Ponto de Dados"))

class InsertPLC:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PLC.svg'), 'MenuText': tr('Inserir CLP'), 'ToolTip': tr('Insere Controlador Lógico Programável') }
    def Activated(self):
        insert_component_smart("PLC_S7_1200.FCStd", tr("Controlador CLP"))

class InsertHMI:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'HMI.svg'), 'MenuText': tr('Inserir IHM'), 'ToolTip': tr('Insere Interface Homem-Máquina') }
    def Activated(self):
        insert_component_smart("HMI_Comfort_7.FCStd", tr("Interface IHM"))

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
        return { 'Pixmap': os.path.join(ICON_DIR, 'Automation.svg'), 'MenuText': tr('Sensor/Atuador Industrial'), 'ToolTip': tr('Insere PLC, HMI ou sensores industriais') }
    def Activated(self):
        insert_component_smart("Industrial_Sensor_Inductive.FCStd", tr("Sensor Indutivo"))

class InsertFireDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Fire.svg'), 'MenuText': tr('Detector de Incêndio'), 'ToolTip': tr('Insere detector de fumaça/térmico ou acionador') }
    def Activated(self):
        insert_component_smart("Fire_Smoke_Detector.FCStd", tr("Detector Fumaca"))

class InsertSecurityDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Camera.svg'), 'MenuText': tr('Câmera/Segurança'), 'ToolTip': tr('Insere CFTV, sensores de intrusão ou controle de acesso') }
    def Activated(self):
        insert_component_smart("CCTV_Camera_Dome.FCStd", tr("Camera CFTV"))

class InsertSoundDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SoundDevice.svg'), 'MenuText': tr('Sonorização'), 'ToolTip': tr('Insere caixas de som e amplificadores') }
    def Activated(self):
        insert_component_smart("Sound_Speaker_Ceiling.FCStd", tr("Arandela de Som"))
