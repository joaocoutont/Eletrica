import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .hmi_bim import ProfessionalBIMHMI
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, discover_panel_boards
)

HMI_FAMILIES = {
    "IHM 7\" Confort (800x480)":   {"file": "HMI_Confort_7.FCStd",  "size": "7\"",  "res": "800x480"},
    "IHM 10\" Basic (1024x600)":   {"file": "HMI_Basic_10.FCStd",    "size": "10\"", "res": "1024x600"},
    "IHM 12\" Profissional":        {"file": "HMI_Pro_12.FCStd",     "size": "12\"", "res": "1280x800"},
    "IHM 15\" Industrial Panel PC": {"file": "HMI_IPC_15.FCStd",     "size": "15\"", "res": "1920x1080"},
    "IHM Econômica 4.3\"":          {"file": "HMI_Eco_4.FCStd",      "size": "4.3\"", "res": "480x272"}
}

class HMITaskPanel:
    """Interface para Inserção de Telas IHM / Touchscreens"""
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
        
        # --- SELEÇÃO DE MODELO ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Modelo de Interface (IHM):</b>"))
        self.hmi_combo = QtGui.QComboBox()
        self.hmi_combo.addItems(sorted(HMI_FAMILIES.keys()))
        self.hmi_combo.currentTextChanged.connect(self.on_hmi_changed)
        self.scroll_layout.addWidget(self.hmi_combo)
        
        # TÉCNICO
        tech_group = QtGui.QGroupBox("Especificação da Tela")
        tech_form = QtGui.QFormLayout()
        
        self.size_label = QtGui.QLabel("7\"")
        tech_form.addRow("Tamanho:", self.size_label)
        
        self.res_label = QtGui.QLabel("800x480")
        tech_form.addRow("Resolução:", self.res_label)
        
        self.touch_combo = QtGui.QComboBox()
        self.touch_combo.addItems(["Capacitivo", "Resistivo", "Multitouch"])
        tech_form.addRow("Tecnologia:", self.touch_combo)
        
        tech_group.setLayout(tech_form)
        self.scroll_layout.addWidget(tech_group)

        # INSTALAÇÃO
        pos_group = QtGui.QGroupBox("Montagem no Painel")
        pos_form = QtGui.QFormLayout()
        
        self.mount_combo = QtGui.QComboBox()
        self.mount_combo.addItems(["Embutir (Painel)", "VESA 75", "VESA 100", "Suporte"])
        pos_form.addRow("Tipo de Fixação:", self.mount_combo)

        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 5000); self.z_in.setValue(1500)
        pos_form.addRow("Altura do Centro (mm):", self.z_in)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        # BIM
        bim_group = QtGui.QGroupBox("BIM")
        bim_form = QtGui.QFormLayout()
        self.tag_in = QtGui.QLineEdit("HMI-01")
        bim_form.addRow("TAG:", self.tag_in)
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        bim_form.addRow("Quadro/Console:", self.panel_combo)
        bim_group.setLayout(bim_form)
        self.scroll_layout.addWidget(bim_group)

        self.scroll_layout.addStretch()
        self.on_hmi_changed(self.hmi_combo.currentText())

    def on_hmi_changed(self, text):
        data = HMI_FAMILIES.get(text)
        if not data: return
        self.command.family_file = data["file"]
        self.command.screen_size = data["size"]
        self.command.resolution = data["res"]
        
        self.size_label.setText(data["size"])
        self.res_label.setText(data["res"])
        self.refresh_ghost()

    def populate_panels(self):
        panels = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.addItem("Console Local")
        for p in panels: self.panel_combo.addItem(p["name"])

    def sync_values(self):
        self.command.z_level = self.z_in.value()
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

class HMICommand:
    """Comando de Inserção de IHMs BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertHMI"
        self.screen_size = "7\""
        self.resolution = "800x480"
        self.z_level = 1500.0
        self.tag = "HMI-01"
        self.family_file = "HMI_7_Inch.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "HMI.svg"),
            'MenuText': 'Inserir IHM/Touch',
            'ToolTip': 'Insere telas de interface industrial com especificações BIM',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, HMITaskPanel, self.place_hmi)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .hmi_bim import make_hmi_plan_symbol
            return make_hmi_plan_symbol(self.screen_size)
        except Exception:
            return Part.makeBox(200, 140, 5)

    def place_hmi(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Automacao")
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_HMI")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.0, 0.8, 1.0)
                obj.ViewObject.Transparency = 30
        else:
            matriz_label = f"Matriz_HMI_{self.screen_size.replace('\"','')}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMHMI(matriz)
                matriz.SourceFile = self.family_file
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"HMI_{self.tag.replace('-','_')}")
            obj.LinkedObject = matriz
            
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("ScreenSize", self.screen_size)
            _set_prop("Resolution", self.resolution)
            _set_prop("Tag", self.tag, group="BIM_Classificacao")
            _set_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")

            obj.Label = f"[{self.tag}] IHM {self.screen_size}"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(0,0,0,1))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .hmi_bim import make_hmi_plan_symbol
            shape = make_hmi_plan_symbol(self.screen_size)
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.0, 0.6, 0.8)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertHMI', HMICommand())
