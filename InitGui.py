# FreeCAD Eletrica Workbench
# This file is part of the Eletrica Workbench for FreeCAD

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
        
        # Comandos proprios da bancada
        eletrica_cmds = [
            "Eletrica_InsertSocket",
            "Eletrica_InsertLight",
            "Eletrica_InsertSwitch",
            "Eletrica_MergeSwitches",
            "Eletrica_InsertTUE",
            "Eletrica_ServiceEntranceWizard",
            "Eletrica_InsertSubstation",
            "Eletrica_InsertBoreholePump",
            "Eletrica_SetupEmergencyPower",
            "Eletrica_GenerateControlWiring",
            "Eletrica_RunSafetyAudit",
            "Eletrica_CreatePanel",
            "Eletrica_CreateConduit",
            "Eletrica_CreateExposedConduit",
            "Eletrica_AssignCircuitToConduit",
            "Eletrica_ClearConduitCircuits",
            "Eletrica_AutoConnectSequence",
            "Eletrica_AutoConnectCeiling",
            "Eletrica_GenerateLoadSchedule",
            "Eletrica_GenerateCableSchedule",
            "Eletrica_ExportDisciplineBIM",
            "Eletrica_GenerateBOM",
            "Eletrica_GenerateLegend",
            "Eletrica_GenerateTags",
            "Eletrica_GenerateWireSymbols",
            "Eletrica_ApplyHeatmap",
            "Eletrica_CheckConduitFill",
            "Eletrica_ManageBoxes",
            "Eletrica_CreateTechnicalSheet",
            "Eletrica_AnalyzeSpaceLighting",
            "Eletrica_RunProjectAudit",
            "Eletrica_GenerateUnifilar",
            "Eletrica_ToggleDashboard",
            "Eletrica_CloneFloor",
            "Eletrica_Generate3DWiring",
            "Eletrica_CreateIndustrialConnection",
            "Eletrica_GenerateProjectQR",
            "Eletrica_InsertSmartDevice",
            "Eletrica_CheckSelectivity",
            "Eletrica_CreatePanel",
            "Eletrica_GenerateCableSchedule",
            "Eletrica_ServiceEntranceWizard",
            "Eletrica_InsertSubstation",
            "Eletrica_DimensionMotorStarter",
            "Eletrica_SetupEmergencyPower",
            "Eletrica_GenerateControlWiring",
            "Eletrica_RunSafetyAudit",
            "Eletrica_InsertBoreholePump",
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
