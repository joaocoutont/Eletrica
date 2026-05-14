import os
import FreeCAD
import FreeCADGui
from PySide import QtWidgets
from EletricaLogic.i18n import tr

ICON_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Icons")

class CheckSelectivity:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Selectivity.svg'), 'MenuText': tr('Estudo de Seletividade'), 'ToolTip': tr('Gera curvas tempo-corrente de proteção') }
    def Activated(self):
        pass

class PowerFactorCorrection:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PowerFactor.svg'), 'MenuText': tr('Correção Fator de Potência'), 'ToolTip': tr('Dimensiona banco de capacitores automático') }
    def Activated(self):
        pass

class SetupEmergencyPower:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'QTA.svg'), 'MenuText': tr('Dimensionar Gerador'), 'ToolTip': tr('Dimensiona GMG baseado em cargas essenciais') }
    def Activated(self):
        pass

class ArcFlashAnalysis:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ArcFlash.svg'), 'MenuText': tr('Estudo de Arc Flash'), 'ToolTip': tr('Calcula energia incidente e define EPIs (NFPA 70E)') }
    def Activated(self):
        pass

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
        pass

class BusbarSizing:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Busway.svg'), 'MenuText': tr('Dimensionar Barramento'), 'ToolTip': tr('Dimensiona barras de cobre/alumínio para quadros') }
    def Activated(self):
        pass

class MTInstrumentationWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Instrumentation.svg'), 'MenuText': tr('Dimensionar TC/TP'), 'ToolTip': tr('Dimensiona transformadores de instrumento para MT') }
    def Activated(self):
        pass

class RunLoadFlowSimulation:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Auditor.svg'), 'MenuText': tr('Fluxo de Carga'), 'ToolTip': tr('Executa simulação de fluxo de carga e estabilidade da rede') }
    def Activated(self):
        pass

class RunSelectivityAudit:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Selectivity.svg'), 'MenuText': tr('Auditoria de Seletividade'), 'ToolTip': tr('Verifica coordenação entre disjuntores e fusíveis') }
    def Activated(self):
        pass

class RunSurgeSimulation:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Shielding.svg'), 'MenuText': tr('Simulação de Surto'), 'ToolTip': tr('Verifica propagação de transientes e eficácia dos DPS') }
    def Activated(self):
        pass

class RunGenerativeRouting:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AutoPlacement.svg'), 'MenuText': tr('Roteamento Generativo'), 'ToolTip': tr('IA para encontrar o melhor caminho de cabos/conduites') }
    def Activated(self):
        pass

class LightingAnalysis:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Lighting.svg'), 'MenuText': tr('Análise Luminotécnica'), 'ToolTip': tr('Calcula iluminância média e uniformidade (Método dos Lúmens)') }
    def Activated(self):
        pass
