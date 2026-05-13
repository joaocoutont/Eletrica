import FreeCAD
import FreeCADGui
import os
import sys

# --- CONFIGURAÇÃO DE CAMINHO ---
ELETRICA_DIR = os.path.normpath(os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica"))

# Garantir sys.path
if ELETRICA_DIR not in sys.path:
    sys.path.append(ELETRICA_DIR)

# --- TENTAR FORÇAR CARGA DE RECURSOS EXTERNOS ---
try:
    import Arch
    import BIM
except:
    pass

# --- TENTAR REGISTRAR ÍCONES DO BIM/ARCH PARA GARANTIR ORIGINAIS ---
try:
    import FreeCADGui
    # Tentar localizar a bancada BIM para pegar os ícones originais
    for p in sys.path:
        bim_path = os.path.join(p, "BIM", "Resources", "icons")
        if os.path.exists(bim_path):
            FreeCADGui.addIconPath(bim_path)
            break
        # Outro caminho comum em versões mais novas
        bim_path_alt = os.path.join(p, "BIM", "icons")
        if os.path.exists(bim_path_alt):
            FreeCADGui.addIconPath(bim_path_alt)
            break
except:
    pass


class EletricaWorkbench (FreeCADGui.Workbench):
    """Bancada de Engenharia Elétrica para FreeCAD 1.1"""
    
    DIR = os.path.normpath(os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica"))
    
    MenuText = "Eletrica"
    ToolTip = "Ferramentas Profissionais de Engenharia Elétrica (NBR 5410)"
    
    Icon = os.path.join(DIR, "Icons", "Raio.svg")

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        "Este método organiza a interface conforme o fluxo de confecção do projeto"
        import EletricaGui
        import EletricaPanel

        class ExternalToolProxy:
            """Proxy para ferramentas de outras bancadas (BIM, Draft)"""
            def __init__(self, cmd_name):
                self.cmd_name = cmd_name
                self.dir = os.path.normpath(os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica"))

            def Activated(self):
                import FreeCADGui
                try:
                    FreeCADGui.runCommand(self.cmd_name)
                except:
                    try:
                        FreeCADGui.activateWorkbench("BIMWorkbench")
                        FreeCADGui.activateWorkbench("EletricaWorkbench")
                        FreeCADGui.runCommand(self.cmd_name)
                    except:
                        FreeCAD.Console.PrintError("Falha ao abrir ferramenta: " + self.cmd_name + "\n")

            def GetResources(self):
                # Usar o nome do comando como ícone.
                icon = self.cmd_name
                # Nome oficial do ícone no FreeCAD 1.1 para o Explorador IFC
                if icon == "BIM_IfcExplorer":
                    icon = "IFC"

                return {'MenuText': tr(self.cmd_name.replace("Arch_", "").replace("BIM_", "").replace("Draft_", "")), 
                        'Pixmap': icon,
                        'ToolTip': tr("Ferramenta Externa: ") + self.cmd_name}

        def tr(text):
            try:
                from EletricaLogic.i18n import tr as real_tr
                return real_tr(text)
            except:
                return text
        
        # Proxies de ferramentas externas
        draft_cmds = ["Draft_Line", "Draft_Wire", "Draft_Circle", "Draft_Arc", 
                      "Draft_Move", "Draft_Rotate", "Draft_Mirror", "Draft_Offset", 
                      "Draft_Trimex", "Draft_Stretch", "Draft_Upgrade", "Draft_Downgrade"]
        snap_cmds = ["Draft_Snap_Lock", "Draft_Snap_Endpoint", "Draft_Snap_Midpoint", 
                     "Draft_Snap_Center", "Draft_Snap_Angle", "Draft_Snap_Intersection", 
                     "Draft_Snap_Perpendicular", "Draft_Snap_Extension", "Draft_Snap_Parallel", 
                     "Draft_Snap_Grid", "Draft_Snap_WorkingPlane"]
        bim_cmds = ["Arch_Site", "Arch_Building", "Arch_BuildingPart", "Arch_Reference", "BIM_IfcExplorer"]

        for cmd in draft_cmds + snap_cmds + bim_cmds:
            FreeCADGui.addCommand("Eletrica_Tool_" + cmd, ExternalToolProxy(cmd))

        # --- REORGANIZAÇÃO POR FLUXO DE PROJETO ---

        # 1. SETUP: Configuração e Dados da Obra
        toolbar_setup = [
            "Eletrica_StartNewProject", 
            "Eletrica_ProjectProperties", 
            "Eletrica_ToggleDashboard", 
            "Eletrica_SyncTitleBlock"
        ]
        
        # 2. BIM MODELING: Inserção de Cargas e Equipamentos
        toolbar_modeling = [
            "Eletrica_InsertSocket", 
            "Eletrica_InsertSpecialSocket",
            "Eletrica_InsertLight", 
            "Eletrica_InsertSwitch", 
            "Eletrica_MergeSwitches", 
            "Eletrica_InsertSmartDevice",
            "Eletrica_DimensionMotorStarter",
            "Eletrica_MotorWiringWizard",
            "Eletrica_InsertAirConditioner",
            "Eletrica_InsertPumpSet",
            "Eletrica_LinkPumpSet",
            "Eletrica_InsertBoreholePump",
            "Eletrica_BIMifyEquipment"
        ]
        
        # 3. TELECOM & DATA: Cabeamento Estruturado e VDI
        toolbar_telecom = [
            "Eletrica_InsertTelecomPoint",
            "Eletrica_InsertVDIRack"
        ]
        
        # 4. INFRASTRUCTURE: Infra, Roteamento e Redes
        toolbar_infra = [
            "Eletrica_CreateConduit", 
            "Eletrica_CreateCableTray", 
            "Eletrica_CableTrayAssistant",
            "Eletrica_AerialLineWizard",
            "Eletrica_SPDAWizard"
        ]
        
        # 4. ENGINEERING: Engenharia de Sistemas e Cálculos MT/BT
        toolbar_eng = [
            "Eletrica_ServiceEntranceWizard", 
            "Eletrica_SubstationWizard",
            "Eletrica_BusbarSizing",
            "Eletrica_CheckSelectivity",
            "Eletrica_PowerFactorCorrection",
            "Eletrica_SetupEmergencyPower",
            "Eletrica_LightingAnalysis",
            "Eletrica_ArcFlashAnalysis",
            "Eletrica_ConsolidateProject"
        ]
        
        # 5. MANAGEMENT: Gestão de Painéis e Circuitos
        toolbar_mgmt = [
            "Eletrica_CreatePanel", 
            "Eletrica_ConsolidateMultiDocument", 
            "Eletrica_CCMCommandDiagram",
            "Eletrica_Generate3DWiring",
            "Eletrica_CloneFloor"
        ]
        
        # 6. QUALITY & BIM: Auditoria e Exportação
        toolbar_audit = [
            "Eletrica_RunProjectAudit",
            "Eletrica_ToggleVoltageDropHeatmap",
            "Eletrica_GenerateTags",
            "Eletrica_GenerateMaintenanceQR",
            "Eletrica_ExportDisciplineBIM"
        ]

        # 7. OUTPUTS: Documentação e Custos
        toolbar_doc = [
            "Eletrica_PriceEditor",
            "Eletrica_GenerateLoadSchedule", 
            "Eletrica_GenerateCableSchedule", 
            "Eletrica_ExportBOM",
            "Eletrica_GenerateBudget", 
            "Eletrica_GenerateUnifilar"
        ]

        toolbar_safety = [
            "Eletrica_InsertEmergencyLight",
            "Eletrica_InsertExitSign",
            "Eletrica_RunSafetyAudit"
        ]

        toolbar_earthing = [
            "Eletrica_InsertGroundingRod",
            "Eletrica_InsertGroundingMesh",
            "Eletrica_InsertBareCable",
            "Eletrica_InsertBEP",
            "Eletrica_InsertGroundingBox",
            "Eletrica_GenerateGroundingReport",
            "Eletrica_SPDAWizard"
        ]

        toolbar_automation = [
            "Eletrica_InsertPLC",
            "Eletrica_InsertHMI",
            "Eletrica_CCMCommandDiagram"
        ]
        
        # Auxiliares
        toolbar_draft = ["Eletrica_Tool_" + c for c in draft_cmds]
        toolbar_snaps = ["Eletrica_Tool_" + c for c in snap_cmds]
        toolbar_bim   = ["Eletrica_Tool_" + c for c in bim_cmds]
        
        # Montagem das Toolbars no FreeCAD
        self.appendToolbar(tr("Configuração da Obra"), toolbar_setup)
        self.appendToolbar(tr("Modelagem Elétrica"), toolbar_modeling)
        self.appendToolbar(tr("Telecom e Dados"), toolbar_telecom)
        self.appendToolbar(tr("Infraestrutura"), toolbar_infra)
        self.appendToolbar(tr("Engenharia e Cálculos"), toolbar_eng)
        self.appendToolbar(tr("Gestão de Quadros"), toolbar_mgmt)
        self.appendToolbar(tr("Auditoria e BIM"), toolbar_audit)
        self.appendToolbar(tr("Segurança e Incêndio"), toolbar_safety)
        self.appendToolbar(tr("Automação e Controle"), toolbar_automation)
        self.appendToolbar(tr("Aterramento e SPDA"), toolbar_earthing)
        self.appendToolbar(tr("Documentação e Custos"), toolbar_doc)
        self.appendToolbar(tr("Desenho (Draft)"), toolbar_draft)
        self.appendToolbar(tr("Precisão (Snaps)"), toolbar_snaps)
        self.appendToolbar(tr("Referência BIM"), toolbar_bim)
        
        # Menu Suspenso Consolidado
        self.appendMenu("Eletrica", toolbar_setup + toolbar_modeling + toolbar_telecom + toolbar_infra + toolbar_eng + toolbar_mgmt + toolbar_doc)

    def Activated(self):
        return

    def Deactivated(self):
        return

FreeCADGui.addWorkbench(EletricaWorkbench())
