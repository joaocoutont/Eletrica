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

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Icons").replace('\\', '/')

class RunProjectAudit:
    """Executa a auditoria completa de normas e segurança"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Audit.svg'),
            'MenuText': tr('Auditoria de Projeto'),
            'ToolTip': tr('Verifica erros de norma, queda de tensão e colisões')
        }
    def Activated(self):
        from EletricaLogic.Auditor import ProjectAuditor
        ProjectAuditor.run_full_audit()

class ToggleVoltageLevelHeatmap:
    """Ativa/Desativa o mapa de cores por níveis de tensão no 3D"""
    _active = False
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'PhaseBalance.svg'), 
            'MenuText': tr('Mapa de Cores por Tensão'), 
            'ToolTip': tr('Pinta o 3D baseado nos níveis de tensão (MT/BT)')
        }
    def Activated(self):
        from EletricaLogic.Visuals import HeatmapManager
        self.__class__._active = not self.__class__._active
        HeatmapManager.apply_voltage_heatmap(self.__class__._active)

class ToggleVoltageDropHeatmap:
    """Ativa/Desativa o mapa de calor por queda de tensão no 3D"""
    _active = False
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Heatmap.svg'), 
            'MenuText': tr('Heatmap Queda de Tensão'), 
            'ToolTip': tr('Pinta o 3D baseado na queda de tensão calculada')
        }
    def Activated(self):
        from EletricaLogic.Visuals import HeatmapManager
        self.__class__._active = not self.__class__._active
        HeatmapManager.toggle_voltage_drop_heatmap(self.__class__._active)

class RunSafetyAudit:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Safety.svg'), 'MenuText': tr('Auditoria de Segurança'), 'ToolTip': tr('Verifica conformidade com NR-10 e NR-12') }
    def Activated(self):
        from EletricaLogic.Auditor import ProjectAuditor
        ProjectAuditor.run_safety_check()

class ToggleOccupancyHeatmap:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Dashboard.svg'), 'MenuText': tr('Heatmap de Ocupação'), 'ToolTip': tr('Visualiza taxa de ocupação dos eletrodutos') }
    def Activated(self):
        from EletricaLogic.Visuals import HeatmapManager
        HeatmapManager.toggle_conduit_fill_heatmap()

class CheckCollisions:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Auditor.svg'), 'MenuText': tr('Clash Detection'), 'ToolTip': tr('Verifica colisões entre elementos elétricos e civis') }
    def Activated(self):
        from EletricaLogic.Auditor import ProjectAuditor
        ProjectAuditor.check_clashes()

class ProjectMetadata:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'TechnicalReport.svg'), 'MenuText': tr('Propriedades do Projeto'), 'ToolTip': tr('Define dados globais do projeto elétrico') }
    def Activated(self):
        from EletricaGuiDialogs import show_metadata_dialog
        show_metadata_dialog()

class ConsolidateProject:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Consolidate.svg'), 'MenuText': tr('Consolidar Projeto'), 'ToolTip': tr('Sincroniza todas as potências e cálculos do modelo') }
    def Activated(self):
        from EletricaLogic.Panels import PanelManager
        doc = FreeCAD.ActiveDocument
        panels = [o for o in doc.Objects if hasattr(o, "TipoBIM") and o.TipoBIM == "Quadro"]
        for p in panels:
            PanelManager.sync_voltage_from_source(p)

        from EletricaLogic.ProjectManager import MultiDocumentManager
        total, summary = MultiDocumentManager.aggregate_load_data()
        
        txt = f"=== CONSOLIDAÇÃO MASTER ===\n"
        txt += f"Carga Total Master: {total:,.0f} VA\n\n"
        txt += tr("Detalhamento por Arquivo:") + "\n"
        for doc_name, va in summary.items():
            txt += f"- {doc_name}: {va:,.0f} VA\n"
            
        QtWidgets.QMessageBox.information(None, "Master Project Manager", txt)

class GenerateProjectQR:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'QR_AR.svg'), 'MenuText': tr('QR Code do Projeto'), 'ToolTip': tr('Gera QR Code para acesso ao modelo em Realidade Aumentada') }
    def Activated(self):
        from EletricaLogic.AR import ARManager
        ARManager.generate_project_link()

class GenerateMaintenanceQR:
    RequiredSelection = ["Quadro", "Motor", "Transformador", "GMG", "UPS"]
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'QRMaintenance.svg'), 'MenuText': tr('QR Code de Manutenção'), 'ToolTip': tr('Gera etiqueta para colagem no painel físico com dados de manutenção') }
    def Activated(self):
        from EletricaLogic.Maintenance import MaintenanceManager
        selection = FreeCADGui.Selection.getSelection()
        if selection:
            MaintenanceManager.generate_qr_for_obj(selection[0])
        else:
            QtWidgets.QMessageBox.information(None, tr("QR Maintenance"), tr("Selecione um equipamento para gerar o QR Code."))

class ExportDisciplineBIM:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'IFCExport.svg'), 'MenuText': tr('Exportar Disciplina BIM'), 'ToolTip': tr('Exporta o modelo elétrico para IFC/Navisworks') }
    def Activated(self):
        from EletricaLogic.IFC import IFCManager
        IFCManager.export_electrical_discipline()

class CloneFloor:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Replicate.svg'), 'MenuText': tr('Clonar Pavimento'), 'ToolTip': tr('Copia toda a rede elétrica para outros níveis') }
    def Activated(self):
        from EletricaLogic.ProjectManager import FloorManager
        FloorManager.replicate_to_next_level()

class SyncTitleBlock:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SyncTitleBlock.svg'), 'MenuText': tr('Sincronizar Selo'), 'ToolTip': tr('Atualiza dados dos selos com metadados do projeto') }
    def Activated(self):
        from EletricaLogic.Documentation import DocumentationManager
        DocumentationManager.sync_all_title_blocks()

class GenerateBIM4D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM4D.svg'), 'MenuText': tr('BIM 4D (Planejamento)'), 'ToolTip': tr('Gera cronograma de execução integrado ao 3D') }
    def Activated(self):
        from EletricaLogic.Reporting import ReportManager
        ReportManager.generate_4d_schedule()

class GenerateBIM5D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM5D.svg'), 'MenuText': tr('BIM 5D (Custos)'), 'ToolTip': tr('Analisa custos ao longo do tempo de execução') }
    def Activated(self):
        from EletricaLogic.Reporting import ReportManager
        ReportManager.generate_5d_cost_analysis()

class GenerateBIM8D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM8D.svg'), 'MenuText': tr('BIM 8D (Segurança)'), 'ToolTip': tr('Plano de segurança do trabalho integrado ao modelo') }
    def Activated(self):
        from EletricaLogic.Safety import SafetyManager
        SafetyManager.generate_8d_plan()

class GenerateCommissioningChecklist:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Report.svg'), 'MenuText': tr('Checklist de Comissionamento'), 'ToolTip': tr('Gera roteiro de testes para entrega da obra') }
    def Activated(self):
        from EletricaLogic.Reporting import ReportManager
        ReportManager.generate_commissioning_checklist()

class RunFinancialAnalysis:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ROI.svg'), 'MenuText': tr('Análise Financeira (ROI)'), 'ToolTip': tr('Calcula retorno de investimento e payback') }
    def Activated(self):
        from EletricaLogic.Budget import BudgetManager
        BudgetManager.show_roi_analysis()

class ExportVRModel:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AR.svg'), 'MenuText': tr('Exportar para VR/AR'), 'ToolTip': tr('Gera modelo para realidade virtual (Oculus/Hololens)') }
    def Activated(self):
        from EletricaLogic.AR import ARManager
        ARManager.export_glbtf()

class ExportBusbarCNC:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Busbar.svg'), 'MenuText': tr('Exportar CNC de Barras'), 'ToolTip': tr('Gera arquivo DXF/STEP para dobra de barras de cobre') }
    def Activated(self):
        from EletricaLogic.Manufacturing import CNCExporter
        CNCExporter.export_busbars()

class GenerateTags:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SmartTags.svg'), 'MenuText': tr('Gerar Etiquetas 3D'), 'ToolTip': tr('Insere tags flutuantes no 3D com dados de circuitos') }
    def Activated(self):
        from EletricaLogic.Tagging import TagManager
        TagManager.generate_smart_tags()

class GenerateBIM6D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM6D.svg'), 'MenuText': tr('BIM 6D (Manutenção)'), 'ToolTip': tr('Gera plano de manutenção preventiva de ativos') }
    def Activated(self):
        from EletricaLogic.Maintenance import MaintenanceManager
        MaintenanceManager.generate_maintenance_plan()

class GenerateBIM9D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM9D.svg'), 'MenuText': tr('BIM 9D (Construção Enxuta)'), 'ToolTip': tr('Otimiza processos de montagem em campo') }
    def Activated(self):
        from EletricaLogic.Reporting import ReportManager
        ReportManager.generate_lean_construction_report()
