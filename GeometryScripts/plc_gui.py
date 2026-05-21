import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .plc_bim import ProfessionalBIMPLC
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, discover_panel_boards
)

PLC_FAMILIES = {
    "S7-1200 CPU 1214C":   {"file": "PLC_S7_1214C.FCStd", "di": 14, "do": 10, "ai": 2, "ao": 0, "type": "CPU Principal"},
    "S7-1200 SM 1221 (8 DI)": {"file": "PLC_S7_SM1221.FCStd", "di": 8,  "do": 0,  "ai": 0, "ao": 0, "type": "Módulo DI/DO"},
    "S7-1200 SM 1222 (8 DO)": {"file": "PLC_S7_SM1222.FCStd", "di": 0,  "do": 8,  "ai": 0, "ao": 0, "type": "Módulo DI/DO"},
    "S7-1200 SM 1231 (4 AI)": {"file": "PLC_S7_SM1231.FCStd", "di": 0,  "do": 0,  "ai": 4, "ao": 0, "type": "Módulo AI/AO"},
    "PLC LOGO! 8":          {"file": "PLC_LOGO_8.FCStd",    "di": 8,  "do": 4,  "ai": 0, "ao": 0, "type": "CPU Principal"},
    "Módulo Misto Genérico": {"file": "PLC_Mixed_Gen.FCStd", "di": 8,  "do": 8,  "ai": 4, "ao": 2, "type": "Módulo Misto"}
}

class PLCTaskPanel:
    """Interface para Inserção de CLP e Módulos I/O"""
    def __init__(self, command_obj):
        self.command = command_obj
        self.form = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(self.form)
        
        self.scroll = QtGui.QScrollArea(self.form)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)
        
        self.scroll_content = QtGui.QWidget()
        self.scroll_layout = QtGui.QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        
        # --- SELEÇÃO DE HARDWARE ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Hardware CLP / Módulo:</b>"))
        self.hw_combo = QtGui.QComboBox()
        self.hw_combo.addItems(sorted(PLC_FAMILIES.keys()))
        self.hw_combo.currentTextChanged.connect(self.on_hw_changed)
        self.scroll_layout.addWidget(self.hw_combo)
        
        # I/O COUNT
        io_group = QtGui.QGroupBox("Contagem de Pontos I/O")
        io_form = QtGui.QFormLayout()
        
        self.di_in = QtGui.QSpinBox(); self.di_in.setRange(0, 128); self.di_in.valueChanged.connect(self.sync_values)
        io_form.addRow("Entradas Digitais (DI):", self.di_in)
        
        self.do_in = QtGui.QSpinBox(); self.do_in.setRange(0, 128); self.do_in.valueChanged.connect(self.sync_values)
        io_form.addRow("Saídas Digitais (DO):", self.do_in)
        
        self.ai_in = QtGui.QSpinBox(); self.ai_in.setRange(0, 64); self.ai_in.valueChanged.connect(self.sync_values)
        io_form.addRow("Entradas Analógicas (AI):", self.ai_in)
        
        self.ao_in = QtGui.QSpinBox(); self.ao_in.setRange(0, 64); self.ao_in.valueChanged.connect(self.sync_values)
        io_form.addRow("Saídas Analógicas (AO):", self.ao_in)
        
        io_group.setLayout(io_form)
        self.scroll_layout.addWidget(io_group)

        # BIM / INSTALAÇÃO
        bim_group = QtGui.QGroupBox("BIM e Instalação")
        bim_form = QtGui.QFormLayout()
        
        self.mount_combo = QtGui.QComboBox()
        self.mount_combo.addItems(["Trilho DIN", "Painel/Parafuso", "Rack"])
        bim_form.addRow("Montagem:", self.mount_combo)

        self.tag_in = QtGui.QLineEdit("PLC-01")
        bim_form.addRow("TAG:", self.tag_in)
        
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        bim_form.addRow("Instalado no Quadro:", self.panel_combo)
        
        bim_group.setLayout(bim_form)
        self.scroll_layout.addWidget(bim_group)

        self.scroll_layout.addStretch()
        self.on_hw_changed(self.hw_combo.currentText())

    def on_hw_changed(self, text):
        data = PLC_FAMILIES.get(text)
        if not data: return
        self.command.family_file = data["file"]
        self.command.device_type = data["type"]
        
        self.di_in.setValue(data["di"])
        self.do_in.setValue(data["do"])
        self.ai_in.setValue(data["ai"])
        self.ao_in.setValue(data["ao"])
        
        # Tenta sugerir um TAG baseado no tipo
        prefix = "PLC" if "CPU" in data["type"] else "MOD"
        self.tag_in.setText(f"{prefix}-01")
        
        self.refresh_ghost()

    def populate_panels(self):
        panels = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.addItem("Sem Quadro")
        for p in panels: self.panel_combo.addItem(p["name"])

    def sync_values(self):
        self.command.di = self.di_in.value()
        self.command.do = self.do_in.value()
        self.command.ai = self.ai_in.value()
        self.command.ao = self.ao_in.value()
        self.command.tag = self.tag_in.text()
        self.refresh_ghost()

    def refresh_ghost(self):
        if hasattr(self.command, 'engine') and self.command.engine.ghost:
            self.command.engine.ghost.Shape = self.command.make_preview_shape()
            Gui.updateGui()

    def accept(self):
        self.sync_values()
        Gui.Control.closeDialog()
        return True

class PLCCommand:
    """Comando de Inserção de CLP e I/O BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertPLC"
        self.device_type = "CPU Principal"
        self.di = 14
        self.do = 10
        self.ai = 2
        self.ao = 0
        self.tag = "PLC-01"
        self.family_file = "PLC_S7_1200.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "PLC.svg"),
            'MenuText': 'Inserir CLP/Módulo I/O',
            'ToolTip': 'Insere controladores e módulos de expansão I/O em trilho DIN',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, PLCTaskPanel, self.place_plc)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .plc_bim import make_plc_plan_symbol
            return make_plc_plan_symbol(self.device_type, self.di, self.do, self.ai, self.ao)
        except Exception:
            return Part.makeBox(100, 75, 5)

    def place_plc(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Automacao")
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_PLC")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.0, 0.5, 1.0)
                obj.ViewObject.Transparency = 30
        else:
            matriz_label = f"Matriz_PLC_{self.family_file.replace('.FCStd','')}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMPLC(matriz)
                matriz.SourceFile = self.family_file
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"PLC_{self.tag.replace('-','_')}")
            obj.LinkedObject = matriz
            
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("DeviceType", self.device_type)
            _set_prop("DI_Count", self.di, ptype="App::PropertyInteger")
            _set_prop("DO_Count", self.do, ptype="App::PropertyInteger")
            _set_prop("AI_Count", self.ai, ptype="App::PropertyInteger")
            _set_prop("AO_Count", self.ao, ptype="App::PropertyInteger")
            _set_prop("Tag", self.tag, group="BIM_Classificacao")

            obj.Label = f"[{self.tag}] {self.device_type}"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .plc_bim import make_plc_plan_symbol
            shape = make_plc_plan_symbol(self.device_type, self.di, self.do, self.ai, self.ao)
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.0, 0.4, 0.8)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertPLC', PLCCommand())
