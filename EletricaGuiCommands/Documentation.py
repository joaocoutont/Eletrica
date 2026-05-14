import os
import FreeCAD
import FreeCADGui
from PySide import QtWidgets
from EletricaLogic.i18n import tr

ICON_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Icons")

class GenerateLoadSchedule:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'TechnicalReport.svg'), 'MenuText': tr('Quadro de Cargas'), 'ToolTip': tr('Gera planilha de cargas NBR 5410') }
    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule()

class GenerateCableSchedule:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'CableTray.svg'), 'MenuText': tr('Lista de Cabos'), 'ToolTip': tr('Gera lista de cabos com comprimentos e seções') }
    def Activated(self):
        pass

class GenerateBudget:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Budget.svg'), 'MenuText': tr('Orçamento Estimativo'), 'ToolTip': tr('Gera planilha de custos baseada em tabela SINAPI/Própria') }
    def Activated(self):
        pass

class GenerateUnifilar:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Unifilar.svg'), 'MenuText': tr('Diagrama Unifilar'), 'ToolTip': tr('Gera desenho unifilar automático no TechDraw') }
    def Activated(self):
        pass

class ExportBOM:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ExportBOM.svg'), 'MenuText': tr('Exportar Lista de Materiais'), 'ToolTip': tr('Gera lista quantitativa de todos os componentes') }
    def Activated(self):
        from EletricaLogic.BOM import BOMManager
        BOMManager.export_bom_to_csv()

class GenerateGraphicLegend:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Legend.svg'), 'MenuText': tr('Gerar Legenda Gráfica'), 'ToolTip': tr('Cria folha TechDraw com símbolos usados') }
    def Activated(self):
        from EletricaLogic.Legend import LegendManager
        LegendManager.generate_graphic_legend()

class GenerateMaintenancePlan:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.svg'), 'MenuText': tr('Plano de Manutenção'), 'ToolTip': tr('Gera cronograma preventivo (BIM 6D)') }
    def Activated(self):
        pass

class UpdatePricing:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Budget.svg'), 'MenuText': tr('Atualizar Preços'), 'ToolTip': tr('Sincroniza base de preços via API ou CSV') }
    def Activated(self):
        pass

class GenerateSustainabilityReport:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Solar.svg'), 'MenuText': tr('Relatório de Sustentabilidade'), 'ToolTip': tr('Analisa eficiência energética e créditos de carbono') }
    def Activated(self):
        pass
