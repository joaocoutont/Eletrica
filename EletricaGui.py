# Hub Central da Interface Grafica - Elite Industrial Suite
import FreeCAD
import FreeCADGui
import traceback
from EletricaLogic.i18n import tr

# Importando Modulos Modularizados
from EletricaGuiCommands import BIM, RDU, Engineering, Infra, Audit, Documentation, Industrial
try:
    from EletricaGuiCommands import ProjectSetup
except Exception as e:
    ProjectSetup = None
    FreeCAD.Console.PrintError(f"Eletrica: falha ao carregar comandos de preparacao BIM: {e}\n")
try:
    from EletricaGuiCommands import FamilyManager
except Exception as e:
    FamilyManager = None
    FreeCAD.Console.PrintError(f"Eletrica: falha ao carregar gerenciador de familias: {e}\n")

# Dicionario de Mapeamento de Comandos
cmds = {
    # --- MODELAGEM BIM (BIM.py) ---
    'Eletrica_InsertSocket': BIM.InsertSocket(),
    'Eletrica_InsertSpecialSocket': BIM.InsertSpecialSocket(),
    'Eletrica_InsertModularSet': BIM.InsertModularSet(),
    'Eletrica_InsertLight': BIM.InsertLight(),
    'Eletrica_InsertSwitch': BIM.InsertSwitch(),
    'Eletrica_MergeSwitches': BIM.MergeSwitches(),
    'Eletrica_InsertSmartDevice': BIM.InsertSmartDevice(),
    'Eletrica_InsertAirConditioner': BIM.InsertAirConditioner(),
    'Eletrica_InsertPumpSet': BIM.InsertPumpSet(),
    'Eletrica_LinkPumpSet': BIM.LinkPumpSet(),
    'Eletrica_InsertBoreholePump': BIM.InsertBoreholePump(),
    'Eletrica_BIMifyEquipment': BIM.BIMifyEquipment(),
    'Eletrica_InsertEVCharger': BIM.InsertEVCharger(),
    'Eletrica_InsertServiceEntrance': BIM.InsertServiceEntrance(),

    # --- INFRAESTRUTURA (Infra.py) ---
    'Eletrica_InsertConduit': Infra.InsertConduit(),
    'Eletrica_InsertCableTray': Infra.InsertCableTray(),
    'Eletrica_AutoRouteWires': Infra.AutoRouteWires(),
    'Eletrica_CheckConduitFill': Infra.CheckConduitFill(),
    'Eletrica_InsertPullBox': Infra.InsertPullBox(),
    'Eletrica_InsertFitting': Infra.InsertFitting(),
    'Eletrica_IntelligentAutoRoute': Infra.IntelligentAutoRoute(),
    'Eletrica_InsertUndergroundDuct': Infra.InsertUndergroundDuct(),
    'Eletrica_InsertTrench': Infra.InsertTrench(),
    'Eletrica_InsertManhole': Infra.InsertManhole(),
    'Eletrica_InsertBuswayDevice': Infra.InsertBuswayDevice(),

    # --- REDES URBANAS / RDU (RDU.py) ---
    'Eletrica_InsertPole': RDU.InsertPole(),
    'Eletrica_AutoPolePlacement': RDU.AutoPolePlacement(),
    'Eletrica_GISConverter': RDU.GISConverter(),
    'Eletrica_InsertStructure': RDU.InsertStructure(),
    'Eletrica_InsertPoleTransformer': RDU.InsertPoleTransformer(),
    'Eletrica_InsertDistributionEquipment': RDU.InsertDistributionEquipment(),
    'Eletrica_InsertGuyWire': RDU.InsertGuyWire(),
    'Eletrica_InsertPublicLighting': RDU.InsertPublicLighting(),
    'Eletrica_InsertPoleGrounding': RDU.InsertPoleGrounding(),
    'Eletrica_InsertFenceGrounding': RDU.InsertFenceGrounding(),
    'Eletrica_InsertGuyGrounding': RDU.InsertGuyGrounding(),
    'Eletrica_InsertNetworkSignaling': RDU.InsertNetworkSignaling(),
    'Eletrica_InsertAerialCable': RDU.InsertAerialCable(),
    'Eletrica_AerialLineWizard': RDU.AerialLineWizard(),
    'Eletrica_ExportKML': RDU.ExportKML(),
    'Eletrica_CreateRDUDrawing': RDU.CreateRDUDrawing(),
    'Eletrica_GenerateRDUMemorial': RDU.GenerateRDUMemorial(),

    # --- ENGENHARIA E ANALISE (Engineering.py) ---
    'Eletrica_CheckSelectivity': Engineering.CheckSelectivity(),
    'Eletrica_PowerFactorCorrection': Engineering.PowerFactorCorrection(),
    'Eletrica_SetupEmergencyPower': Engineering.SetupEmergencyPower(),
    'Eletrica_ArcFlashAnalysis': Engineering.ArcFlashAnalysis(),
    'Eletrica_SubstationWizard': Engineering.SubstationWizard(),
    'Eletrica_ServiceEntranceWizard': Engineering.ServiceEntranceWizard(),
    'Eletrica_BusbarSizing': Engineering.BusbarSizing(),
    'Eletrica_MTInstrumentationWizard': Engineering.MTInstrumentationWizard(),
    'Eletrica_RunLoadFlowSimulation': Engineering.RunLoadFlowSimulation(),
    'Eletrica_RunSelectivityAudit': Engineering.RunSelectivityAudit(),
    'Eletrica_RunSurgeSimulation': Engineering.RunSurgeSimulation(),
    'Eletrica_RunGenerativeRouting': Engineering.RunGenerativeRouting(),
    'Eletrica_LightingAnalysis': Engineering.LightingAnalysis(),
    'Eletrica_MotorWiringWizard': Engineering.MotorWiringWizard(),

    # --- POTENCIA E INDUSTRIA (Industrial.py) ---
    'Eletrica_InsertMTCubicle': Industrial.InsertMTCubicle(),
    'Eletrica_InsertGenerator': Industrial.InsertGenerator(),
    'Eletrica_InsertUPS': Industrial.InsertUPS(),
    'Eletrica_InsertQTA': Industrial.InsertQTA(),
    'Eletrica_CreatePanel': Industrial.CreatePanel(),
    'Eletrica_InsertCCM': Industrial.InsertCCM(),
    'Eletrica_InsertMotor': Industrial.InsertMotor(),
    'Eletrica_SetupMotorWizard': Industrial.SetupMotorWizard(),
    'Eletrica_InsertDataDevice': Industrial.InsertDataDevice(),
    'Eletrica_InsertAutomationDevice': Industrial.InsertAutomationDevice(),
    'Eletrica_InsertFireDevice': Industrial.InsertFireDevice(),
    'Eletrica_InsertSecurityDevice': Industrial.InsertSecurityDevice(),
    'Eletrica_InsertSoundDevice': Industrial.InsertSoundDevice(),
    'Eletrica_InsertSolarPanel': Industrial.InsertSolarPanel(),
    'Eletrica_InsertSolarInverter': Industrial.InsertSolarInverter(),
    'Eletrica_SolarWizard': Industrial.SolarWizard(),
    'Eletrica_SolarAnalysis': Industrial.SolarAnalysis(),
    'Eletrica_InsertPLC': Industrial.InsertPLC(),
    'Eletrica_InsertHMI': Industrial.InsertHMI(),
    'Eletrica_CCMCommandDiagram': Industrial.CCMCommandDiagram(),
    'Eletrica_InsertEmergencyLight': Industrial.InsertEmergencyLight(),
    'Eletrica_InsertExitSign': Industrial.InsertExitSign(),
    'Eletrica_InsertGroundingRod': Industrial.InsertGroundingRod(),
    'Eletrica_InsertGroundingMesh': Industrial.InsertGroundingMesh(),
    'Eletrica_InsertBareCable': Industrial.InsertBareCable(),
    'Eletrica_InsertBEP': Industrial.InsertBEP(),
    'Eletrica_InsertGroundingBox': Industrial.InsertGroundingBox(),
    'Eletrica_GenerateGroundingReport': Industrial.GenerateGroundingReport(),
    'Eletrica_SPDAWizard': Industrial.SPDAWizard(),

    # --- AUDITORIA E BIM (Audit.py) ---
    'Eletrica_RunProjectAudit': Audit.RunProjectAudit(),
    'Eletrica_ToggleVoltageLevelHeatmap': Audit.ToggleVoltageLevelHeatmap(),
    'Eletrica_ToggleVoltageDropHeatmap': Audit.ToggleVoltageDropHeatmap(),
    'Eletrica_RunSafetyAudit': Audit.RunSafetyAudit(),
    'Eletrica_ToggleOccupancyHeatmap': Audit.ToggleOccupancyHeatmap(),
    'Eletrica_CheckCollisions': Audit.CheckCollisions(),
    'Eletrica_ProjectMetadata': Audit.ProjectMetadata(),
    'Eletrica_ConsolidateProject': Audit.ConsolidateProject(),
    'Eletrica_GenerateProjectQR': Audit.GenerateProjectQR(),
    'Eletrica_GenerateMaintenanceQR': Audit.GenerateMaintenanceQR(),
    'Eletrica_ExportDisciplineBIM': Audit.ExportDisciplineBIM(),
    'Eletrica_CloneFloor': Audit.CloneFloor(),
    'Eletrica_SyncTitleBlock': Audit.SyncTitleBlock(),
    'Eletrica_GenerateTags': Audit.GenerateTags(),
    'Eletrica_GenerateBIM4D': Audit.GenerateBIM4D(),
    'Eletrica_GenerateBIM5D': Audit.GenerateBIM5D(),
    'Eletrica_GenerateBIM6D': Audit.GenerateBIM6D(),
    'Eletrica_GenerateBIM8D': Audit.GenerateBIM8D(),
    'Eletrica_GenerateBIM9D': Audit.GenerateBIM9D(),
    'Eletrica_GenerateCommissioningChecklist': Audit.GenerateCommissioningChecklist(),
    'Eletrica_RunFinancialAnalysis': Audit.RunFinancialAnalysis(),
    'Eletrica_ExportVRModel': Audit.ExportVRModel(),
    'Eletrica_ExportBusbarCNC': Audit.ExportBusbarCNC(),

    # --- DOCUMENTACAO (Documentation.py) ---
    'Eletrica_GenerateLoadSchedule': Documentation.GenerateLoadSchedule(),
    'Eletrica_GenerateCableSchedule': Documentation.GenerateCableSchedule(),
    'Eletrica_GenerateBudget': Documentation.GenerateBudget(),
    'Eletrica_GenerateUnifilar': Documentation.GenerateUnifilar(),
    'Eletrica_GenerateSingleLineDiagram': Documentation.GenerateUnifilar(), # Alias
    'Eletrica_ExportBOM': Documentation.ExportBOM(),
    'Eletrica_GenerateGraphicLegend': Documentation.GenerateGraphicLegend(),
    'Eletrica_GenerateMaintenancePlan': Documentation.GenerateMaintenancePlan(),
    'Eletrica_UpdatePricing': Documentation.UpdatePricing(),
    'Eletrica_GenerateSustainabilityReport': Documentation.GenerateSustainabilityReport(),
    'Eletrica_GlobalSettings': Documentation.GlobalSettings(),
}

if ProjectSetup:
    cmds.update({
        'Eletrica_PrepareFromCAD': ProjectSetup.PrepareFromCAD(),
        'Eletrica_PrepareFromIFC': ProjectSetup.PrepareFromIFC(),
        'Eletrica_PrepareFromFreeCAD': ProjectSetup.PrepareFromFreeCAD(),
        'Eletrica_ManagePanelsCircuits': ProjectSetup.ManagePanelsCircuits(),
        'Eletrica_RecalculateCircuitLoads': ProjectSetup.RecalculateCircuitLoads(),
        'Eletrica_ValidateElectricalProject': ProjectSetup.ValidateElectricalProject(),
        'Eletrica_ExportPointSchedule': ProjectSetup.ExportPointSchedule(),
        'Eletrica_BatchEditPoints': ProjectSetup.BatchEditPoints(),
        'Eletrica_ToggleSystemVisibility': ProjectSetup.ToggleSystemVisibility(),
        'Eletrica_CreatePreliminaryRoutes': ProjectSetup.CreatePreliminaryRoutes(),
        'Eletrica_GenerateSymbolLegend': ProjectSetup.GenerateSymbolLegend(),
        'Eletrica_GenerateElectricalReport': ProjectSetup.GenerateElectricalReport(),
        'Eletrica_EditProjectTemplates': ProjectSetup.EditProjectTemplates(),
        'Eletrica_VisualValidation': ProjectSetup.VisualValidation(),
        'Eletrica_CreateSpaceOrSector': ProjectSetup.CreateSpaceOrSector(),
    })

if FamilyManager:
    cmds.update({
        'Eletrica_ManageFamilies': FamilyManager.ManageFamilies(),
    })

def command_wrapper(name, obj, original_activated):
    """Encapsula o comando para adicionar robustez, log e transacoes."""
    def activated_robust(*args, **kwargs):
        def sync_checkable_state():
            try:
                from GeometryScripts.bim_placement_core import BIMPlacementEngine
                if name in BIMPlacementEngine.CHECKABLE_PLACEMENT_COMMANDS and BIMPlacementEngine.active_engine is None:
                    BIMPlacementEngine.clear_checkable_actions()
            except Exception:
                pass

        doc = FreeCAD.ActiveDocument
        if not doc and not getattr(obj, "AllowNoDocument", False):
            FreeCAD.Console.PrintWarning(tr("Nenhum documento ativo.") + "\n")
            sync_checkable_state()
            return

        # Feedback na barra de status
        res = obj.GetResources()
        label = res.get('MenuText', name)
        FreeCADGui.getMainWindow().statusBar().showMessage(tr("Executando: ") + label + "...")
        
        # Iniciar Transação (Undo)
        if doc:
            doc.openTransaction(label)
        
        try:
            original_activated(*args, **kwargs)
            if doc:
                doc.commitTransaction()
            FreeCAD.Console.PrintLog(f"Eletrica: {name} executado com sucesso.\n")
        except Exception as e:
            if doc:
                doc.abortTransaction()
            sync_checkable_state()
            error_msg = f"Erro em {name}: {str(e)}"
            FreeCAD.Console.PrintError(error_msg + "\n")
            traceback.print_exc()
            from PySide import QtWidgets
            QtWidgets.QMessageBox.critical(None, "Eletrica Error", error_msg)
        finally:
            sync_checkable_state()
            FreeCADGui.getMainWindow().statusBar().showMessage(tr("Pronto."), 5000)
            
    return activated_robust

def is_active_standard(self):
    """Verifica documento ativo e requisitos de selecao."""
    doc = FreeCAD.ActiveDocument
    if doc is None and not getattr(self, "AllowNoDocument", False):
        return False
        
    # Verificacao opcional de selecao (Requirement: RequiredSelection)
    if hasattr(self, "RequiredSelection"):
        sel = FreeCADGui.Selection.getSelection()
        if not sel: return False
        
        req = self.RequiredSelection
        if isinstance(req, str): req = [req]
        
        # Verifica se pelo menos um objeto selecionado atende ao requisito
        match = False
        for o in sel:
            if hasattr(o, "TipoBIM") and o.TipoBIM in req:
                match = True
                break
        return match
        
    return True

# Registrar Comandos no FreeCAD com injeção de robustez
import types
for name, obj in cmds.items():
    # 1. Envolver o método Activated
    if hasattr(obj, "Activated"):
        original = obj.Activated
        obj.Activated = command_wrapper(name, obj, original)
        
    # 2. Injetar IsActive inteligente
    if not hasattr(obj, "IsActive"):
        obj.IsActive = types.MethodType(is_active_standard, obj)
        
    FreeCADGui.addCommand(name, obj)
