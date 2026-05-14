import os
import FreeCAD
import FreeCADGui
from PySide import QtWidgets
from EletricaLogic.i18n import tr

ICON_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Icons")

class RunProjectAudit:
    """Executa a auditoria completa de normas e segurança"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.svg'),
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
            'Pixmap': os.path.join(ICON_DIR, 'Auditor.svg'), 
            'MenuText': tr('Heatmap Queda de Tensão'), 
            'ToolTip': tr('Pinta o 3D baseado na queda de tensão calculada')
        }
    def Activated(self):
        from EletricaLogic.Visuals import HeatmapManager
        self.__class__._active = not self.__class__._active
        HeatmapManager.toggle_voltage_drop_heatmap(self.__class__._active)

class RunSafetyAudit:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.svg'), 'MenuText': tr('Auditoria de Segurança'), 'ToolTip': tr('Verifica conformidade com NR-10 e NR-12') }
    def Activated(self):
        pass

class ToggleOccupancyHeatmap:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Auditor.svg'), 'MenuText': tr('Heatmap de Ocupação'), 'ToolTip': tr('Visualiza taxa de ocupação dos eletrodutos') }
    def Activated(self):
        from EletricaLogic.Visuals import HeatmapManager
        pass

class CheckCollisions:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Auditor.svg'), 'MenuText': tr('Clash Detection'), 'ToolTip': tr('Verifica colisões entre elementos elétricos e civis') }
    def Activated(self):
        pass

class ProjectMetadata:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'TechnicalReport.svg'), 'MenuText': tr('Propriedades do Projeto'), 'ToolTip': tr('Define dados globais do projeto elétrico') }
    def Activated(self):
        from EletricaLogic.Settings import ProjectSettings
        obj = ProjectSettings.get_settings_obj()
        if obj: FreeCADGui.Selection.addSelection(obj)

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
        return { 'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.svg'), 'MenuText': tr('QR Code do Projeto'), 'ToolTip': tr('Gera QR Code para acesso à documentação na nuvem') }
    def Activated(self):
        pass

class GenerateMaintenanceQR:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.svg'), 'MenuText': tr('QR Code Manutenção'), 'ToolTip': tr('Gera etiquetas QR para cada equipamento para gestão de ativos') }
    def Activated(self):
        pass

class ExportDisciplineBIM:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GIS.svg'), 'MenuText': tr('Exportar Disciplina BIM'), 'ToolTip': tr('Exporta o modelo elétrico para IFC/Navisworks') }
    def Activated(self):
        pass

class CloneFloor:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AutoPlacement.svg'), 'MenuText': tr('Clonar Pavimento'), 'ToolTip': tr('Copia toda a rede elétrica para outros níveis') }
    def Activated(self):
        pass

class SyncTitleBlock:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'DrawingSheet.svg'), 'MenuText': tr('Sincronizar Selo'), 'ToolTip': tr('Atualiza dados dos selos com metadados do projeto') }
    def Activated(self):
        pass

class GenerateBIM4D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM4D.svg'), 'MenuText': tr('BIM 4D (Planejamento)'), 'ToolTip': tr('Gera cronograma de execução integrado ao 3D') }
    def Activated(self):
        pass

class GenerateBIM5D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM5D.svg'), 'MenuText': tr('BIM 5D (Custos)'), 'ToolTip': tr('Analisa custos ao longo do tempo de execução') }
    def Activated(self):
        pass

class GenerateBIM8D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM8D.svg'), 'MenuText': tr('BIM 8D (Segurança)'), 'ToolTip': tr('Plano de segurança do trabalho integrado ao modelo') }
    def Activated(self):
        pass

class GenerateCommissioningChecklist:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.svg'), 'MenuText': tr('Checklist de Comissionamento'), 'ToolTip': tr('Gera roteiro de testes para entrega da obra') }
    def Activated(self):
        pass

class RunFinancialAnalysis:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Budget.svg'), 'MenuText': tr('Análise Financeira (ROI)'), 'ToolTip': tr('Calcula retorno de investimento e payback') }
    def Activated(self):
        pass

class ExportVRModel:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GIS.svg'), 'MenuText': tr('Exportar para VR/AR'), 'ToolTip': tr('Gera modelo para realidade virtual (Oculus/Hololens)') }
    def Activated(self):
        pass

class ExportBusbarCNC:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Busbar.svg'), 'MenuText': tr('Exportar CNC de Barras'), 'ToolTip': tr('Gera arquivo DXF/STEP para dobra de barras de cobre') }
    def Activated(self):
        pass

class GenerateTags:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.svg'), 'MenuText': tr('Gerar Etiquetas 3D'), 'ToolTip': tr('Insere tags flutuantes no 3D com dados de circuitos') }
    def Activated(self):
        pass

class GenerateBIM6D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM6D.svg'), 'MenuText': tr('BIM 6D (Manutenção)'), 'ToolTip': tr('Gera plano de manutenção preventiva de ativos') }
    def Activated(self):
        pass

class GenerateBIM9D:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIM9D.svg'), 'MenuText': tr('BIM 9D (Construção Enxuta)'), 'ToolTip': tr('Otimiza processos de montagem em campo') }
    def Activated(self):
        pass
