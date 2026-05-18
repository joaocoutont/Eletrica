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

        def IsActive(self):
            import FreeCAD
            return FreeCAD.ActiveDocument is not None

        def GetResources(self):
            try:
                from EletricaLogic.i18n import tr
            except:
                tr = lambda x: x
                
            # Usar o nome do comando como ícone.
            icon = self.cmd_name
            # Nome oficial do ícone no FreeCAD 1.1 para o Explorador IFC
            if icon == "BIM_IfcExplorer":
                icon = "IFC"

            return {'MenuText': tr(self.cmd_name.replace("Arch_", "").replace("BIM_", "").replace("Draft_", "")), 
                    'Pixmap': icon,
                    'ToolTip': tr("Ferramenta Externa: ") + self.cmd_name}

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
        import GeometryScripts.junction_box_gui # Carrega o comando de Caixas
        import GeometryScripts.socket_gui       # Carrega o comando de Tomadas
        try:
            from EletricaLogic.i18n import tr
        except:
            tr = lambda x: x


        
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
            FreeCADGui.addCommand("Eletrica_Tool_" + cmd, self.ExternalToolProxy(cmd))

        # Registrar o comando do Dashboard importado dinamicamente para evitar conflitos de escopo global no FreeCAD
        try:
            from EletricaPanel import ToggleDashboardCommand
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Não foi possível importar ToggleDashboardCommand do EletricaPanel: {str(e)}. Usando stub de fallback.\n")
            class ToggleDashboardCommand:
                def Activated(self):
                    FreeCAD.Console.PrintError("Painel do Dashboard não disponível.\n")
                def GetResources(self):
                    return {
                        'MenuText': 'Exibir Dashboard Elétrica',
                        'ToolTip': 'Painel indisponível temporariamente',
                        'Pixmap': 'Dashboard'
                    }

        FreeCADGui.addCommand("Eletrica_ToggleDashboard", ToggleDashboardCommand())

        # --- REORGANIZAÇÃO POR FLUXO DE PROJETO ---

        # 1. SETUP: Configuração e Dados da Obra
        toolbar_setup = [
            "Eletrica_PrepareFromCAD",
            "Eletrica_PrepareFromIFC",
            "Eletrica_PrepareFromFreeCAD",
            "Eletrica_ManageFamilies",
            "Eletrica_EditProjectTemplates",
            "Eletrica_ProjectMetadata",
            "Eletrica_ServiceEntranceWizard",
            "Eletrica_InsertServiceEntrance",
            "Eletrica_CreatePanel",
            "Eletrica_GlobalSettings",
            "Eletrica_ToggleDashboard"
        ]
        
        # 2. BIM MODELING: Inserção de Cargas e Equipamentos
        toolbar_mod_lighting = ["Eletrica_InsertLight", "Eletrica_InsertSwitch", "Eletrica_MergeSwitches", "Eletrica_InsertSmartDevice"]
        toolbar_mod_loads    = ["Eletrica_InsertSocket", "Eletrica_InsertSpecialSocket", "Eletrica_InsertModularSet", "Eletrica_InsertAirConditioner"]
        toolbar_mod_motors   = ["Eletrica_SetupMotorWizard", "Eletrica_MotorWiringWizard", "Eletrica_InsertPumpSet", "Eletrica_LinkPumpSet", "Eletrica_InsertBoreholePump", "Eletrica_BIMifyEquipment"]
        
        # 3. TELECOM & DATA: Cabeamento Estruturado e VDI
        toolbar_telecom = [
            "Eletrica_InsertDataDevice",
            "Eletrica_InsertAutomationDevice"
        ]
        
        # 4. INFRASTRUCTURE: Infra, Roteamento e Redes
        toolbar_infra = [
            "Eletrica_InsertConduit",
            "Eletrica_InsertCableTray",
            "Eletrica_IntelligentAutoRoute",
            "Eletrica_CreatePreliminaryRoutes",
            "Eletrica_CheckConduitFill",
            "Eletrica_InsertPullBox",
            "Eletrica_JunctionBox"
        ]
        
        # 4. ENGINEERING: Engenharia de Sistemas e Cálculos MT/BT
        toolbar_eng_cables = ["Eletrica_MTInstrumentationWizard", "Eletrica_BusbarSizing"]
        toolbar_eng_analysis = ["Eletrica_CheckSelectivity", "Eletrica_PowerFactorCorrection", "Eletrica_SetupEmergencyPower", "Eletrica_LightingAnalysis", "Eletrica_ArcFlashAnalysis"]
        
        # 5. MANAGEMENT: Gestão de Painéis e Circuitos
        toolbar_mgmt = [
            "Eletrica_ManagePanelsCircuits",
            "Eletrica_RecalculateCircuitLoads",
            "Eletrica_BatchEditPoints",
            "Eletrica_CreateSpaceOrSector",
            "Eletrica_ConsolidateProject",
            "Eletrica_UpdatePricing",
            "Eletrica_CloneFloor",
            "Eletrica_SyncTitleBlock"
        ]
        
        # 6. QUALITY & BIM: Auditoria e Exportação
        toolbar_audit = [
            "Eletrica_RunProjectAudit",
            "Eletrica_ValidateElectricalProject",
            "Eletrica_VisualValidation",
            "Eletrica_ToggleSystemVisibility",
            "Eletrica_ToggleVoltageLevelHeatmap",
            "Eletrica_ToggleVoltageDropHeatmap",
            "Eletrica_GenerateTags",
            "Eletrica_GenerateMaintenanceQR",
            "Eletrica_ExportDisciplineBIM"
        ]

        # 7. OUTPUTS: Documentação e Custos
        toolbar_doc_reports = ["Eletrica_GenerateLoadSchedule", "Eletrica_GenerateCableSchedule", "Eletrica_ExportPointSchedule", "Eletrica_GenerateElectricalReport", "Eletrica_GenerateSymbolLegend"]
        toolbar_doc_export  = ["Eletrica_ExportBOM", "Eletrica_GenerateBudget", "Eletrica_GenerateUnifilar"]
        toolbar_doc_drawing = ["Eletrica_CreateRDUDrawing", "Eletrica_GenerateRDUMemorial"]

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
        
        # 8. RDU: Redes de Distribuição Urbana e Rural
        toolbar_rdu_poles = ["Eletrica_InsertPole", "Eletrica_AutoPolePlacement", "Eletrica_GISConverter", "Eletrica_InsertStructure"]
        toolbar_rdu_equip = ["Eletrica_InsertPoleTransformer", "Eletrica_InsertDistributionEquipment", "Eletrica_InsertGuyWire", "Eletrica_InsertPublicLighting"]
        toolbar_rdu_lines = ["Eletrica_InsertAerialCable", "Eletrica_AerialLineWizard", "Eletrica_ExportKML"]
        toolbar_rdu_ground = ["Eletrica_InsertPoleGrounding", "Eletrica_InsertFenceGrounding", "Eletrica_InsertGuyGrounding", "Eletrica_InsertNetworkSignaling"]

        # 9. Energia Solar Fotovoltaica (PV)
        toolbar_solar = [
            "Eletrica_InsertSolarPanel",
            "Eletrica_SolarWizard"
        ]

        # 10. Subestações e Média Tensão (MT)
        toolbar_substation = [
            "Eletrica_InsertMTCubicle",
            "Eletrica_SubstationWizard"
        ]

        # 11. Segurança, Incêndio e Sistemas Especiais
        toolbar_special_systems = [
            "Eletrica_InsertFireDevice",
            "Eletrica_InsertSecurityDevice",
            "Eletrica_InsertSoundDevice"
        ]
        
        # 12. Energia Crítica e de Emergência
        toolbar_critical = [
            "Eletrica_InsertGenerator",
            "Eletrica_InsertUPS"
        ]

        # 13. Distribuição Industrial Avançada
        toolbar_industrial_adv = [
            "Eletrica_InsertBuswayDevice",
            "Eletrica_RunSelectivityAudit"
        ]

        # 14. Ciclo de Vida BIM (4D até 9D)
        toolbar_lifecycle = [
            "Eletrica_GenerateBIM4D",            # 4D: Tempo
            "Eletrica_GenerateSustainabilityReport", # 6D: Sustentabilidade
            "Eletrica_GenerateMaintenancePlan",   # 7D: Facilidades
            "Eletrica_GenerateBIM8D",             # 8D: Segurança
            "Eletrica_GenerateCommissioningChecklist" # 9D: Comissionamento
        ]

        # 15. Engenharia de Simulação e Desenho
        toolbar_simulation = [
            "Eletrica_RunLoadFlowSimulation",
            "Eletrica_GenerateSingleLineDiagram"
        ]
        
        # 16. Business Intelligence e Finanças
        toolbar_bi = [
            "Eletrica_RunFinancialAnalysis",
            "Eletrica_GenerateBIM5D"
        ]

        # 17. IA, Inovação e Manufatura
        toolbar_innovation = [
            "Eletrica_RunGenerativeRouting",
            "Eletrica_ExportVRModel",
            "Eletrica_RunSurgeSimulation",
            "Eletrica_ExportBusbarCNC"
        ]
        
        # Auxiliares
        toolbar_draft = ["Eletrica_Tool_" + c for c in draft_cmds]
        toolbar_snaps = ["Eletrica_Tool_" + c for c in snap_cmds]
        toolbar_bim   = ["Eletrica_Tool_" + c for c in bim_cmds]
        
        # --- FUNÇÃO DE DEDUPLICAÇÃO ---
        def deduplicate(l):
            seen = set()
            return [x for x in l if not (x in seen or seen.add(x))]
        
        # FASE I: CONCEPÇÃO & BIM (Cargas e Iluminação)
        toolbar_phase_1 = deduplicate(
            toolbar_setup + 
            toolbar_mod_lighting + 
            toolbar_mod_loads + 
            toolbar_telecom + 
            toolbar_automation + 
            toolbar_special_systems
        )

        # FASE II: INFRAESTRUTURA & REDES (Físico)
        toolbar_phase_2 = deduplicate(
            toolbar_infra + 
            toolbar_earthing +        # Aterramento movido para Infra
            toolbar_rdu_poles + 
            toolbar_rdu_equip + 
            toolbar_rdu_lines +
            toolbar_rdu_ground
        )

        # FASE III: ENGENHARIA & MT (Cálculos e Sistemas)
        toolbar_phase_3 = deduplicate(
            toolbar_eng_cables + 
            toolbar_eng_analysis + 
            toolbar_mod_motors + 
            toolbar_industrial_adv + 
            toolbar_simulation + 
            toolbar_solar + 
            toolbar_substation + 
            toolbar_critical
        )

        # FASE IV: AUDITORIA & BIM 9D (Qualidade e Gestão)
        toolbar_phase_4 = deduplicate(
            toolbar_audit + 
            toolbar_mgmt + 
            toolbar_lifecycle + 
            toolbar_bi + 
            toolbar_innovation +
            toolbar_safety
        )

        # FASE V: DOCUMENTAÇÃO & ENTREGA (Finalização)
        toolbar_phase_5 = deduplicate(
            toolbar_doc_reports + 
            toolbar_doc_export + 
            toolbar_doc_drawing
        )

        # Montagem das 5 Barras de Fluxo no FreeCAD
        self.appendToolbar(tr("Fase I: Concepção & BIM"), toolbar_phase_1)
        self.appendToolbar(tr("Fase II: Infra & Redes"), toolbar_phase_2)
        self.appendToolbar(tr("Fase III: Engenharia & MT"), toolbar_phase_3)
        self.appendToolbar(tr("Fase IV: Auditoria & Lifecycle"), toolbar_phase_4)
        self.appendToolbar(tr("Fase V: Documentação & Entrega"), toolbar_phase_5)
        
        # Auxiliares (Draft/Snaps)
        self.appendToolbar(tr("Auxiliares (Draft/Snaps)"), deduplicate(toolbar_draft + toolbar_snaps))
        
        # Menu Suspenso Organizado por Submenus (Hierárquico)
        self.appendMenu([tr("Eletrica"), tr("Fase I: Concepção & BIM")], toolbar_phase_1)
        self.appendMenu([tr("Eletrica"), tr("Fase II: Infra & Redes")], toolbar_phase_2)
        self.appendMenu([tr("Eletrica"), tr("Fase III: Engenharia & MT")], toolbar_phase_3)
        self.appendMenu([tr("Eletrica"), tr("Fase IV: Auditoria & Lifecycle")], toolbar_phase_4)
        self.appendMenu([tr("Eletrica"), tr("Fase V: Documentação & Entrega")], toolbar_phase_5)

        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            BIMPlacementEngine.clear_checkable_actions()
        except Exception:
            pass


    def Activated(self):
        import FreeCADGui
        try:
            from EletricaLogic.i18n import tr
        except:
            tr = lambda x: x
            
        FreeCADGui.getMainWindow().statusBar().showMessage(tr("Bancada Eletrica Ativada - Pronto para projetar conforme NBR 5410"))
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is None:
                BIMPlacementEngine.clear_checkable_actions()
        except Exception:
            pass
        
        # O painel lateral (Dashboard) agora inicia desabilitado/ocultado por padrão conforme solicitação do usuário.
        # Ele pode ser ativado a qualquer momento clicando no botão "Exibir Dashboard Eletrica" na barra de ferramentas SETUP ou no menu.
        pass

    def Deactivated(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                BIMPlacementEngine.active_engine.stop()
        except Exception as e:
            import FreeCAD
            FreeCAD.Console.PrintError(f"Erro ao desativar bancada Eletrica: {str(e)}\n")

FreeCADGui.addWorkbench(EletricaWorkbench())
