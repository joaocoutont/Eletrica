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

class GenerateLoadSchedule:
    RequiredSelection = "Quadro"
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'LoadSchedule.svg'), 'MenuText': tr('Quadro de Cargas'), 'ToolTip': tr('Gera planilha de cargas NBR 5410') }
    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule()

class GenerateCableSchedule:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'CableSchedule.svg'), 'MenuText': tr('Lista de Cabos'), 'ToolTip': tr('Gera lista de cabos com comprimentos e seções') }
    def Activated(self):
        from EletricaLogic.CableSchedule import CableScheduleManager
        CableScheduleManager.export_to_spreadsheet()

class GenerateBudget:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Budget.svg'), 'MenuText': tr('Orçamento Estimativo'), 'ToolTip': tr('Gera planilha de custos baseada em tabela SINAPI/Própria') }
    def Activated(self):
        from EletricaLogic.BOM import BOMManager
        from EletricaLogic.Budget import BudgetManager
        from EletricaLogic.Exporter import DisciplineExporter
        bom = BOMManager.get_raw_bom_data()
        report, _ = BudgetManager.generate_budget_report(bom)
        DisciplineExporter.export_bom_to_csv(bom, report)

class GenerateUnifilar:
    RequiredSelection = ["Quadro", "Subestacao"]
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Unifilar.svg'), 'MenuText': tr('Diagrama Unifilar'), 'ToolTip': tr('Gera desenho unifilar automático no TechDraw') }
    def Activated(self):
        from EletricaLogic.Diagrams import UnifilarGenerator
        selection = FreeCADGui.Selection.getSelection()
        target = selection[0] if selection else None
        if target and getattr(target, "TipoBIM", "") == "Subestacao":
            UnifilarGenerator.create_mt_unifilar(target)
        elif target:
            UnifilarGenerator.create_graphic_diagram(target)
        else:
            QtWidgets.QMessageBox.warning(None, tr("Diagrama Unifilar"), tr("Selecione um quadro ou subestacao."))

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
        return { 'Pixmap': os.path.join(ICON_DIR, 'MaintenancePlan.svg'), 'MenuText': tr('Plano de Manutenção'), 'ToolTip': tr('Gera cronograma preventivo (BIM 6D)') }
    def Activated(self):
        from EletricaLogic.Maintenance import MaintenanceManager
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            QtWidgets.QMessageBox.warning(None, tr("Plano de Manutencao"), tr("Selecione um equipamento."))
            return
        MaintenanceManager.generate_qr_for_obj(selection[0])

class UpdatePricing:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PriceEditor.svg'), 'MenuText': tr('Atualizar Preços'), 'ToolTip': tr('Sincroniza base de preços via API ou CSV') }
    def Activated(self):
        from EletricaLogic.Budget import BudgetManager
        prices = BudgetManager.load_prices()
        QtWidgets.QMessageBox.information(None, tr("Atualizar Precos"), tr("Base de precos carregada: ") + str(len(prices)) + tr(" itens."))

class GenerateSustainabilityReport:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ESG.svg'), 'MenuText': tr('Relatório de Sustentabilidade'), 'ToolTip': tr('Analisa eficiência energética e créditos de carbono') }
    def Activated(self):
        from EletricaLogic.Reporting import ReportManager
        ReportManager.generate_markdown_memorial()

class GlobalSettings:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GlobalSettings.svg'), 'MenuText': tr('Configurações Globais'), 'ToolTip': tr('Configura caminhos de biblioteca e preferências') }
    def Activated(self):
        from EletricaGuiDialogs import show_settings_dialog
        show_settings_dialog()
