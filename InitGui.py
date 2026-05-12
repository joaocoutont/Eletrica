# ⚡ SUITE ELITE BIM - Engenharia Elétrica
# Autor: João Couto
# Contato: joaocoutont@hotmail.com
# Main Entry Point for Eletrica Workbench
import FreeCADGui

class EletricaWorkbench (FreeCADGui.Workbench):
    "Eletrica Workbench"

    MenuText = "Eletrica"
    ToolTip = "Ferramentas para Projetos Elétricos BIM"
    Icon = """
        /* XPM */
        static char * lightning_xpm[] = {
        "16 16 3 1",
        " 	c None",
        ".	c #FFCC00",
        "+	c #FFAA00",
        "                ",
        "      ...       ",
        "     ...        ",
        "    ...         ",
        "   ...          ",
        "  .......       ",
        " .......        ",
        "    ...         ",
        "   ...          ",
        "  ...           ",
        " ...            ",
        " ..             ",
        " .              ",
        "                ",
        "                ",
        "                "};
        """

    def Initialize(self):
        "This function is executed when FreeCAD starts"
        import EletricaGui
        import EletricaPanel
        
        # 1. GRUPO: INÍCIO E CONFIGURAÇÃO
        toolbar_start = ["Eletrica_StartNewProject", "Eletrica_ToggleDashboard"]
        
        # 2. GRUPO: MODELAGEM E CRIAÇÃO (BIM)
        toolbar_model = [
            "Eletrica_CreatePanel", "Eletrica_InsertSocket", "Eletrica_InsertLight", 
            "Eletrica_InsertSwitch", "Eletrica_MergeSwitches", "Eletrica_InsertSmartDevice"
        ]
        
        # 3. GRUPO: INFRAESTRUTURA
        toolbar_infra = [
            "Eletrica_CreateConduit", "Eletrica_CreateCableTray", 
            "Eletrica_CreateIndustrialConnection", "Eletrica_Generate3DWiring"
        ]
        
        # 4. GRUPO: ENGENHARIA E CÁLCULOS
        toolbar_eng = [
            "Eletrica_ServiceEntranceWizard", "Eletrica_InsertSubstation", 
            "Eletrica_InsertBoreholePump", "Eletrica_DimensionMotorStarter", 
            "Eletrica_SetupEmergencyPower", "Eletrica_CheckSelectivity"
        ]
        
        # 5. GRUPO: DOCUMENTAÇÃO E SAÍDA
        toolbar_doc = [
            "Eletrica_GenerateLoadSchedule", "Eletrica_GenerateCableSchedule", 
            "Eletrica_GenerateBudget", "Eletrica_GenerateUnifilar", "Eletrica_SyncTitleBlock", 
            "Eletrica_RunProjectAudit", "Eletrica_RunSafetyAudit", "Eletrica_GenerateProjectQR",
            "Eletrica_BIMifyEquipment", "Eletrica_ExportDisciplineBIM", "Eletrica_CloneFloor"
        ]
        
        # 6. GRUPO: FERRAMENTAS DE DESENHO (DRAFT)
        toolbar_draft = [
            "Draft_Line", "Draft_Wire", "Draft_Circle", "Draft_Arc", 
            "Draft_Move", "Draft_Rotate", "Draft_Mirror", "Draft_Offset", 
            "Draft_Trimex", "Draft_Stretch", "Draft_Upgrade", "Draft_Downgrade"
        ]
        
        # 7. GRUPO: SNAPS (ENCAIXE)
        toolbar_snap = [
            "Draft_Snap_Lock", "Draft_Snap_Endpoint", "Draft_Snap_Midpoint", 
            "Draft_Snap_Center", "Draft_Snap_Angle", "Draft_Snap_Intersection", 
            "Draft_Snap_Perpendicular", "Draft_Snap_Extension", "Draft_Snap_Parallel", 
            "Draft_Snap_Grid", "Draft_Snap_WorkingPlane"
        ]
        
        # 8. GRUPO: ESTRUTURA BIM
        toolbar_bim = ["Arch_Site", "Arch_Building", "Arch_BuildingPart"]
        
        # Registrando as Toolbars Separadas (Isso cria as divisórias visuais)
        self.appendToolbar("Elite 1: Início", toolbar_start)
        self.appendToolbar("Elite 2: Modelagem", toolbar_model)
        self.appendToolbar("Elite 3: Infraestrutura", toolbar_infra)
        self.appendToolbar("Elite 4: Engenharia", toolbar_eng)
        self.appendToolbar("Elite 5: Documentação", toolbar_doc)
        self.appendToolbar("Elite 6: Desenho (Draft)", toolbar_draft)
        self.appendToolbar("Elite 7: Snaps (Encaixe)", toolbar_snap)
        self.appendToolbar("Elite 8: Estrutura BIM", toolbar_bim)
        
        # Menu consolidado
        all_cmds = toolbar_start + toolbar_model + toolbar_infra + toolbar_eng + toolbar_doc + toolbar_draft + toolbar_bim
        self.appendMenu("Eletrica Elite", all_cmds)

    def Activated(self):
        # Opção Nuclear: Ativa rapidamente as bancadas dependentes para registrar os comandos
        import FreeCADGui
        try:
            # Salva o nome da bancada atual (Eletrica)
            current_wb = FreeCADGui.activeWorkbench().name()
            # "Acorda" o Draft e o BIM/Arch
            FreeCADGui.activateWorkbench("DraftWorkbench")
            try:
                FreeCADGui.activateWorkbench("BIMWorkbench")
            except:
                try:
                    FreeCADGui.activateWorkbench("ArchWorkbench")
                except:
                    pass
            # Volta para a Eletrica instantaneamente
            FreeCADGui.activateWorkbench(current_wb)
        except:
            pass

    def Deactivated(self):
        return

    def ContextMenu(self, recipient):
        return

    def GetClassName(self): 
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(EletricaWorkbench())
