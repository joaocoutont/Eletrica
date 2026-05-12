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
        static char * xpm_body[] = {
        "16 16 2 1",
        " 	c None",
        ".	c #FFCC00",
        "                ",
        "       ..       ",
        "      ....      ",
        "     ......     ",
        "    ........    ",
        "       ..       ",
        "       ..       ",
        "   ..........   ",
        "       ..       ",
        "       ..       ",
        "    ........    ",
        "     ......     ",
        "      ....      ",
        "       ..       ",
        "                ",
        "                "};
        """

    def Initialize(self):
        "This function is executed when FreeCAD starts"
        import EletricaGui
        import EletricaPanel
        
        # Comandos proprios da bancada
        eletrica_cmds = [
            "Eletrica_InsertSocket",
            "Eletrica_InsertLight",
            "Eletrica_InsertSwitch",
            "Eletrica_MergeSwitches",
            "Eletrica_InsertTUE",
            "Eletrica_ServiceEntranceWizard",
            "Eletrica_InsertSubstation",
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
            "Eletrica_GenerateBOM",
            "Eletrica_GenerateLegend",
            "Eletrica_GenerateTags",
            "Eletrica_GenerateWireSymbols",
            "Eletrica_ApplyHeatmap",
            "Eletrica_CheckConduitFill",
            "Eletrica_ManageBoxes",
            "Eletrica_CreateTechnicalSheet",
            "Eletrica_AnalyzeSpaceLighting",
            "Eletrica_BalancePhases",
            "Eletrica_CalculateWiring",
            "Eletrica_PrepareIFC",
            "Eletrica_ToggleDashboard",
            "Eletrica_GenerateBudget",
            "Eletrica_BIMifyEquipment",
            "Eletrica_DimensionMotorStarter",
            "Eletrica_CloneFloor",
            "Eletrica_Generate3DWiring",
            "Eletrica_CreateIndustrialConnection",
            "Eletrica_GenerateProjectQR",
            "Eletrica_InsertSmartDevice",
            "Eletrica_CheckSelectivity",
            "Eletrica_GenerateReport",
            "Eletrica_GenerateRiseFallSymbols",
            "Eletrica_AnnotateCircuits",
            "Eletrica_CreateCableTray",
            "Eletrica_RunProjectAudit",
            "Eletrica_GeneratePanelLabels",
            "Eletrica_SolarEstimate",
            "Eletrica_GenerateUnifilar",
            "Eletrica_SPDAGui",
            "Eletrica_SPDARiskWizard",
            "Eletrica_GroundingCalculator",
            "Eletrica_InsertSocket", 
            "Eletrica_InsertLight",
            "Eletrica_InsertTUE",
            "Eletrica_InsertServiceEntrance"
        ]
        
        # Comandos essenciais do BIM/Arch e Draft que vamos 'emprestar'
        bim_cmds = ["Arch_BuildingPart", "Arch_Project", "Arch_SectionPlane", "BIM_Library"]
        draft_cmds = ["Draft_Line", "Draft_Wire", "Draft_Move", "Draft_Rotate", "Draft_SelectPlane"]
        
        # Criando as Toolbars
        self.appendToolbar("Eletrica Predial", eletrica_cmds)
        self.appendToolbar("BIM Essentials", bim_cmds)
        self.appendToolbar("Draft Tools", draft_cmds)
        
        # Criando o Menu
        self.appendMenu("Eletrica", eletrica_cmds + ["---"] + bim_cmds + ["---"] + draft_cmds)

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
