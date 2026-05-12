# ⚡ SUITE ELITE BIM - Engenharia Elétrica
# Autor: João Couto
# Contato: joaocoutont@hotmail.com
# Main Entry Point for Eletrica Workbench
import FreeCADGui

class EletricaWorkbench (FreeCADGui.Workbench):
    "Eletrica Workbench"

    # Icon path - placeholder for now
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
        
        # Garante que os comandos do Draft e BIM estejam carregados
        try:
            import DraftGui
            import BIMGui
        except ImportError:
            pass
        
        # Comandos reais da Suite Elite 3.0
        eletrica_cmds = [
            "Eletrica_StartNewProject",
            "Eletrica_InsertSocket",
            "Eletrica_InsertLight",
            "Eletrica_InsertSwitch",
            "Eletrica_MergeSwitches",
            "Eletrica_CreatePanel",
            "Eletrica_CreateConduit",
            "Eletrica_CreateCableTray",
            "Eletrica_Generate3DWiring",
            "Eletrica_CreateIndustrialConnection",
            "Eletrica_GenerateLoadSchedule",
            "Eletrica_GenerateCableSchedule",
            "Eletrica_GenerateBudget",
            "Eletrica_RunProjectAudit",
            "Eletrica_GenerateUnifilar",
            "Eletrica_SyncTitleBlock",
            "Eletrica_BIMifyEquipment",
            "Eletrica_DimensionMotorStarter",
            "Eletrica_InsertBoreholePump",
            "Eletrica_InsertSubstation",
            "Eletrica_ServiceEntranceWizard",
            "Eletrica_SetupEmergencyPower",
            "Eletrica_RunSafetyAudit",
            "Eletrica_CheckSelectivity",
            "Eletrica_InsertSmartDevice",
            "Eletrica_GenerateProjectQR",
            "Eletrica_ToggleDashboard",
            "Eletrica_CloneFloor",
            "Eletrica_ExportDisciplineBIM"
        ]
        
        # Criando as Toolbars
        self.appendToolbar("Eletrica Elite (Principal)", eletrica_cmds)
        
        # Criando o Menu
        self.appendMenu("Eletrica", eletrica_cmds)

    def Activated(self):
        "This function is executed when the workbench is activated"
        return

    def Deactivated(self):
        "This function is executed when the workbench is deactivated"
        return

    def ContextMenu(self, recipient):
        "This function is executed whenever the user right-clicks on an object"
        return

    def GetClassName(self): 
        # This function is mandatory if you follow the "frozendict" example 
        # in the FreeCAD source code.
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(EletricaWorkbench())
