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
        
        try:
            import DraftGui
            import BIMGui
        except ImportError:
            pass
        
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
        
        # Registrando as Toolbars Separadas (Isso cria as divisórias visuais)
        self.appendToolbar("Elite 1: Início", toolbar_start)
        self.appendToolbar("Elite 2: Modelagem", toolbar_model)
        self.appendToolbar("Elite 3: Infraestrutura", toolbar_infra)
        self.appendToolbar("Elite 4: Engenharia", toolbar_eng)
        self.appendToolbar("Elite 5: Documentação", toolbar_doc)
        
        # Menu consolidado
        self.appendMenu("Eletrica Elite", toolbar_start + toolbar_model + toolbar_infra + toolbar_eng + toolbar_doc)

    def Activated(self):
        return

    def Deactivated(self):
        return

    def ContextMenu(self, recipient):
        return

    def GetClassName(self): 
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(EletricaWorkbench())
