# Hub Central da Interface Grafica - Elite Industrial Suite
import FreeCAD
import FreeCADGui
from EletricaLogic.i18n import tr

# Importando Modulos Modularizados
from EletricaGuiCommands import BIM, RDU, Engineering, Infra, Audit, Documentation, Industrial

# Dicionario de Mapeamento de Comandos
# Chave: Nome interno no FreeCAD | Valor: Instancia da classe de comando
cmds = {
    # --- MODELAGEM BIM (BIM.py) ---
    'Eletrica_InsertSocket': BIM.InsertSocket(),
    'Eletrica_InsertSpecialSocket': BIM.InsertSpecialSocket(),
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
    'Eletrica_CreatePanel_Alias': Industrial.CreatePanel(), # Alias
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

    # --- DOCUMENTACAO (Documentation.py) ---
    'Eletrica_GenerateLoadSchedule': Documentation.GenerateLoadSchedule(),
    'Eletrica_GenerateCableSchedule': Documentation.GenerateCableSchedule(),
    'Eletrica_GenerateBudget': Documentation.GenerateBudget(),
    'Eletrica_GenerateUnifilar': Documentation.GenerateUnifilar(),
    'Eletrica_ExportBOM': Documentation.ExportBOM(),
    'Eletrica_GenerateGraphicLegend': Documentation.GenerateGraphicLegend(),
    'Eletrica_GenerateMaintenancePlan': Documentation.GenerateMaintenancePlan(),
    'Eletrica_UpdatePricing': Documentation.UpdatePricing(),
    'Eletrica_GenerateSustainabilityReport': Documentation.GenerateSustainabilityReport(),
}

# Registrar Comandos no FreeCAD
for name, obj in cmds.items():
    FreeCADGui.addCommand(name, obj)
