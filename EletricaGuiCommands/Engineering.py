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

class CheckSelectivity:
    RequiredSelection = ["Disjuntor", "Fusivel"]
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Selectivity.svg'), 'MenuText': tr('Estudo de Seletividade'), 'ToolTip': tr('Gera curvas tempo-corrente de proteção') }
    def Activated(self):
        from EletricaLogic.Protection import SelectivityManager
        selection = FreeCADGui.Selection.getSelection()
        if selection:
            SelectivityManager.plot_curves(selection)
        else:
            QtWidgets.QMessageBox.information(None, tr("Estudo de Seletividade"), tr("Selecione os dispositivos de protecao (disjuntores/fusiveis) para plotar as curvas."))

class PowerFactorCorrection:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PowerFactor.svg'), 'MenuText': tr('Correção Fator de Potência'), 'ToolTip': tr('Dimensiona banco de capacitores automático') }
    def Activated(self):
        from EletricaLogic.PowerFactor import PFCManager
        PFCManager.open_calculator()

class SetupEmergencyPower:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Generator.svg'), 'MenuText': tr('Dimensionar Gerador'), 'ToolTip': tr('Dimensiona GMG baseado em cargas essenciais') }
    def Activated(self):
        from EletricaLogic.Generators import GeneratorSizer
        GeneratorSizer.run_wizard()

class ArcFlashAnalysis:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ArcFlash.svg'), 'MenuText': tr('Estudo de Arc Flash'), 'ToolTip': tr('Calcula energia incidente e define EPIs (NFPA 70E)') }
    def Activated(self):
        from EletricaLogic.SurgeAnalysis import ArcFlashCalculator
        ArcFlashAnalysis_Dialog().show()

class SubstationWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Substation.svg'), 'MenuText': tr('Assistente de Subestação'), 'ToolTip': tr('Dimensiona transformadores e cubículos de MT') }
    def Activated(self):
        from EletricaLogic.Substation import SubstationManager
        SubstationManager.create_substation_bim(500, 13.8)

class ServiceEntranceWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ServiceEntrance.svg'), 'MenuText': tr('Entrada de Serviço'), 'ToolTip': tr('Dimensiona padrão de entrada (Poste/Caixa/Proteção)') }
    def Activated(self):
        from EletricaGuiDialogs import show_service_entrance_dialog
        show_service_entrance_dialog()

class BusbarSizing:
    RequiredSelection = "Quadro"
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Busbar.svg'), 'MenuText': tr('Dimensionar Barramento'), 'ToolTip': tr('Dimensiona barras de cobre/alumínio para quadros') }
    def Activated(self):
        from EletricaLogic.Manufacturing import BusbarCalculator
        BusbarCalculator.open_ui()

class MTInstrumentationWizard:
    RequiredSelection = ["Subestacao", "Cubiculo"]
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Instrumentation.svg'), 'MenuText': tr('Dimensionar TC/TP'), 'ToolTip': tr('Dimensiona transformadores de instrumento para MT') }
    def Activated(self):
        from EletricaLogic.Substation import SubstationManager
        SubstationManager.open_instrumentation_wizard()

class RunLoadFlowSimulation:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PhaseBalance.svg'), 'MenuText': tr('Fluxo de Carga'), 'ToolTip': tr('Executa simulação de fluxo de carga e estabilidade da rede') }
    def Activated(self):
        from EletricaLogic.LoadFlow import LoadFlowEngine
        LoadFlowEngine.run_simulation()

class RunSelectivityAudit:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Selectivity.svg'), 'MenuText': tr('Auditoria de Seletividade'), 'ToolTip': tr('Verifica coordenação entre disjuntores e fusíveis') }
    def Activated(self):
        from EletricaLogic.Protection import SelectivityManager
        results = SelectivityManager.check_coordination_errors()
        if results:
            QtWidgets.QMessageBox.warning(None, tr("Auditoria de Seletividade"), "\n".join(results))
        else:
            QtWidgets.QMessageBox.information(None, tr("Auditoria de Seletividade"), tr("Nenhum erro de coordenacao encontrado."))

class RunSurgeSimulation:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SPDA.svg'), 'MenuText': tr('Simulação de Surto'), 'ToolTip': tr('Verifica propagação de transientes e eficácia dos DPS') }
    def Activated(self):
        from EletricaLogic.SurgeAnalysis import SurgeSimulator
        SurgeSimulator.run_analysis()

class RunGenerativeRouting:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AI.svg'), 'MenuText': tr('Roteamento Generativo'), 'ToolTip': tr('IA para encontrar o melhor caminho de cabos/conduites') }
    def Activated(self):
        from EletricaLogic.AutoRouter import GenerativeRouter
        GenerativeRouter.optimize_infrastructure()

class LightingAnalysis:
    RequiredSelection = "Espaco"
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'LightingAnalysis.svg'), 'MenuText': tr('Análise Luminotécnica'), 'ToolTip': tr('Calcula iluminância média e uniformidade (Método dos Lúmens)') }
    def Activated(self):
        from EletricaLogic.Lighting import LightingManager
        selection = FreeCADGui.Selection.getSelection()
        space = selection[0] if selection else None
        LightingManager.calculate_lux(space)

class MotorWiringWizard:
    RequiredSelection = "Motor"
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'MotorStarter.svg'), 'MenuText': tr('Assistente de Fiação de Motores'), 'ToolTip': tr('Dimensiona condutores e proteções para motores industriais') }
    def Activated(self):
        from EletricaLogic.Starters import StarterManager
        StarterManager.open_wiring_wizard()
