import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .fire_device_bim import ProfessionalBIMFireDevice
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, discover_panel_boards
)

FIRE_DEVICES = {
    "Detector de Fumaça Óptico": {"file": "Detector_Smoke_Opt.FCStd", "mount": "Teto", "z": 2800},
    "Detector de Calor":         {"file": "Detector_Heat.FCStd",      "mount": "Teto", "z": 2800},
    "Acionador Manual (Quebre-Vidro)": {"file": "Manual_Call_Point.FCStd", "mount": "Parede", "z": 1400},
    "Sirene Audiovisual":        {"file": "Siren_AudioVisual.FCStd",  "mount": "Parede", "z": 2200},
    "Sirene Convencional":       {"file": "Siren_Simple.FCStd",       "mount": "Parede", "z": 2200}
}

class FireDeviceTaskPanel:
    """Interface para Inserção de Dispositivos de Incêndio"""
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
        
        # --- SELEÇÃO DE DISPOSITIVO ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Dispositivo de Incêndio:</b>"))
        self.dev_combo = QtGui.QComboBox()
        self.dev_combo.addItems(sorted(FIRE_DEVICES.keys()))
        self.dev_combo.currentTextChanged.connect(self.on_device_changed)
        self.scroll_layout.addWidget(self.dev_combo)
        
        # ENGENHARIA (LARE)
        eng_group = QtGui.QGroupBox("Endereçamento e Central")
        eng_form = QtGui.QFormLayout()
        
        self.proto_combo = QtGui.QComboBox()
        self.proto_combo.addItems(["Endereçável", "Convencional"])
        eng_form.addRow("Protocolo:", self.proto_combo)
        
        self.addr_in = QtGui.QSpinBox(); self.addr_in.setRange(1, 250); self.addr_in.setValue(1)
        eng_form.addRow("Endereço/Laço:", self.addr_in)
        
        self.central_in = QtGui.QLineEdit("Central 01")
        eng_form.addRow("Vincular à Central:", self.central_in)
        
        eng_group.setLayout(eng_form)
        self.scroll_layout.addWidget(eng_group)

        # POSIÇÃO
        pos_group = QtGui.QGroupBox("Instalação")
        pos_form = QtGui.QFormLayout()
        
        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 10000); self.z_in.setValue(2800)
        self.z_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Altura Z (mm):", self.z_in)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        self.scroll_layout.addStretch()
        self.on_device_changed(self.dev_combo.currentText())

    def on_device_changed(self, text):
        data = FIRE_DEVICES.get(text)
        if not data: return
        self.command.device_type = text
        self.command.family_file = data["file"]
        self.z_in.setValue(data["z"])
        self.refresh_ghost()

    def sync_values(self):
        self.command.z_level = self.z_in.value()
        self.command.address = self.addr_in.value()
        self.refresh_ghost()

    def refresh_ghost(self):
        if hasattr(self.command, 'engine') and self.command.engine.ghost:
            self.command.engine.ghost.Shape = self.command.make_preview_shape()
            Gui.updateGui()

    def accept(self):
        self.sync_values()
        Gui.Control.closeDialog()
        return True

class FireDeviceCommand:
    """Comando de Inserção de Dispositivos de Incêndio BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertFireDevice"
        self.device_type = ""
        self.z_level = 2800.0
        self.address = 1
        self.family_file = "Detector_Smoke.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "Fire.svg"),
            'MenuText': 'Detector de Incêndio',
            'ToolTip': 'Insere detectores de fumaça, calor, acionadores e sirenes conforme NBR 17240',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, FireDeviceTaskPanel, self.place_device)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .fire_device_bim import make_fire_plan_symbol
            return make_fire_plan_symbol(self.device_type)
        except Exception:
            return Part.makeCircle(50)

    def place_device(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Incendio")
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_Fire")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0) # Vermelho Incêndio
                obj.ViewObject.Transparency = 30
        else:
            matriz_label = f"Matriz_Fire_{self.device_type.split(' ')[0]}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMFireDevice(matriz)
                matriz.SourceFile = self.family_file
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"FIRE_{self.device_type.replace(' ','_')}")
            obj.LinkedObject = matriz
            
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("DeviceType", self.device_type)
            _set_prop("LoopAddress", self.address, ptype="App::PropertyInteger")
            _set_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")
            _set_prop("Tag", f"INC-{self.address:03d}", group="BIM_Classificacao")

            if obj.ViewObject: obj.ViewObject.ShapeColor = (0.8, 0.0, 0.0)
            obj.Label = f"[{self.address:03d}] {self.device_type}"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(0,0,0,1))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .fire_device_bim import make_fire_plan_symbol
            shape = make_fire_plan_symbol(self.device_type)
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (1.0, 0.0, 0.0)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertFireDevice', FireDeviceCommand())
