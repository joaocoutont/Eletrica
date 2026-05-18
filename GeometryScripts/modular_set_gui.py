import os
import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui
import Part

from .bim_placement_core import BIMPlacementEngine
from .socket_gui import (
    create_default_bim_levels,
    discover_circuits,
    discover_panel_boards,
    discover_project_levels,
    discover_spaces_or_sectors,
)


MODULE_TYPES = [
    "Vazio",
    "Tomada 10A",
    "Tomada 20A",
    "Interruptor simples",
    "Interruptor paralelo",
]


def module_power(module_type):
    if "20A" in module_type:
        return 600.0
    if "Tomada" in module_type:
        return 100.0
    return 0.0


def module_role(module_type):
    if "Tomada" in module_type:
        return "Tomada"
    if "Interruptor" in module_type:
        return "Interruptor"
    return "Vazio"


def _add_prop(obj, prop_type, name, group, default=None):
    if not hasattr(obj, name):
        obj.addProperty(prop_type, name, group)
    if default is not None:
        setattr(obj, name, default)


def _line(points):
    return Part.makePolygon(points + [points[0]])


def _slot_shape(cx, module_type):
    parts = []
    w = 70.0
    h = 82.0
    y = 82.0
    left = cx - w / 2
    right = cx + w / 2
    bottom = y - h / 2
    top = y + h / 2
    parts.append(_line([
        App.Vector(left, bottom, 0),
        App.Vector(right, bottom, 0),
        App.Vector(right, top, 0),
        App.Vector(left, top, 0),
    ]))

    if module_type == "Vazio":
        return parts

    if "Tomada" in module_type:
        s = 42.0
        h_tri = s * math.sqrt(3) / 2
        p1 = App.Vector(cx - s / 2, y - h_tri / 3, 0)
        p2 = App.Vector(cx + s / 2, y - h_tri / 3, 0)
        p3 = App.Vector(cx, y + h_tri * 2 / 3, 0)
        parts.append(Part.makePolygon([p1, p2, p3, p1]))
        if "20A" in module_type:
            parts.append(Part.makeCircle(9.0, App.Vector(cx, y + 6.0, 0), App.Vector(0, 0, 1)))
        return parts

    if "Interruptor" in module_type:
        parts.append(Part.makeCircle(8.0, App.Vector(cx - 18.0, y - 18.0, 0), App.Vector(0, 0, 1)))
        parts.append(Part.makeLine(App.Vector(cx - 12.0, y - 12.0, 0), App.Vector(cx + 22.0, y + 24.0, 0)))
        if "paralelo" in module_type:
            parts.append(Part.makeLine(App.Vector(cx - 22.0, y + 18.0, 0), App.Vector(cx + 22.0, y - 18.0, 0)))
        return parts

    return parts


def make_modular_set_symbol(module_types, plate_size="4x2"):
    parts = []
    count = max(1, len(module_types))
    spacing = 86.0
    width = max(180.0, 92.0 + spacing * (count - 1))
    height = 120.0
    y0 = 22.0
    left = -width / 2
    right = width / 2
    top = y0 + height

    parts.append(_line([
        App.Vector(left, y0, 0),
        App.Vector(right, y0, 0),
        App.Vector(right, top, 0),
        App.Vector(left, top, 0),
    ]))
    parts.append(Part.makeLine(App.Vector(left, 0, 0), App.Vector(right, 0, 0)))
    parts.append(Part.makeLine(App.Vector(0, 0, 0), App.Vector(0, y0, 0)))

    x0 = -spacing * (count - 1) / 2.0
    for idx, module_type in enumerate(module_types):
        parts.extend(_slot_shape(x0 + idx * spacing, module_type))

    return Part.makeCompound(parts)


class ModularSetTaskPanel:
    def __init__(self, command_obj):
        self.command = command_obj
        self.form = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(self.form)

        family_group = QtGui.QGroupBox("Conjunto modular")
        family_form = QtGui.QFormLayout()
        self.plate_combo = QtGui.QComboBox()
        self.plate_combo.addItems(["4x2 - 2 módulos"])
        self.plate_combo.currentTextChanged.connect(self.sync_values)
        family_form.addRow("Placa:", self.plate_combo)

        self.module1_combo = QtGui.QComboBox()
        self.module1_combo.addItems(MODULE_TYPES)
        self.module1_combo.setCurrentText(self.command.module1_type)
        self.module1_combo.currentTextChanged.connect(self.sync_values)
        family_form.addRow("Módulo 1:", self.module1_combo)

        self.module2_combo = QtGui.QComboBox()
        self.module2_combo.addItems(MODULE_TYPES)
        self.module2_combo.setCurrentText(self.command.module2_type)
        self.module2_combo.currentTextChanged.connect(self.sync_values)
        family_form.addRow("Módulo 2:", self.module2_combo)
        family_group.setLayout(family_form)
        self.layout.addWidget(family_group)

        pos_group = QtGui.QGroupBox("Posicionamento")
        pos_form = QtGui.QFormLayout()
        self.level_options = []
        self.level_combo = QtGui.QComboBox()
        self.populate_levels()
        self.level_combo.currentIndexChanged.connect(self.on_level_selected)
        pos_form.addRow("Nível:", self.level_combo)

        self.height_combo = QtGui.QComboBox()
        self.height_combo.addItems(["Baixa (300mm)", "Média (1100mm)", "Alta (2200mm)", "Especial"])
        self.height_combo.currentTextChanged.connect(self.sync_height)
        pos_form.addRow("Altura:", self.height_combo)

        self.z_in = QtGui.QDoubleSpinBox()
        self.z_in.setRange(-5000, 10000)
        self.z_in.setValue(self.command.z_level)
        self.z_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Altura inst. (mm):", self.z_in)

        self.final_z_label = QtGui.QLabel("Z final: 1100 mm")
        pos_form.addRow("Resultado:", self.final_z_label)

        self.rot_in = QtGui.QSpinBox()
        self.rot_in.setRange(0, 360)
        self.rot_in.setSingleStep(90)
        self.rot_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Rotação (°):", self.rot_in)

        self.insert_mode_combo = QtGui.QComboBox()
        self.insert_mode_combo.addItems(["Contínuo", "Uma vez"])
        self.insert_mode_combo.currentIndexChanged.connect(self.on_insert_mode_changed)
        pos_form.addRow("Modo:", self.insert_mode_combo)
        pos_group.setLayout(pos_form)
        self.layout.addWidget(pos_group)

        bim_group = QtGui.QGroupBox("Vínculos BIM")
        bim_form = QtGui.QFormLayout()
        self.panel_options = []
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        self.panel_combo.currentIndexChanged.connect(self.on_panel_selected)
        bim_form.addRow("Quadro:", self.panel_combo)

        self.circuit_options = []
        self.circuit1_combo = QtGui.QComboBox()
        self.circuit2_combo = QtGui.QComboBox()
        self.populate_circuits()
        self.circuit1_combo.currentIndexChanged.connect(self.on_circuit_selected)
        self.circuit2_combo.currentIndexChanged.connect(self.on_circuit_selected)
        bim_form.addRow("Circuito M1:", self.circuit1_combo)
        bim_form.addRow("Circuito M2:", self.circuit2_combo)

        self.space_options = []
        self.space_combo = QtGui.QComboBox()
        self.populate_spaces()
        self.space_combo.currentIndexChanged.connect(self.on_space_selected)
        bim_form.addRow("Ambiente/Setor:", self.space_combo)
        bim_group.setLayout(bim_form)
        self.layout.addWidget(bim_group)

        self.layout.addStretch()
        self.layout.addWidget(QtGui.QLabel("Dica: ESPAÇO gira | H altura | I modo | ESC sai"))
        self.sync_ui()

    def populate_levels(self):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        levels = discover_project_levels(doc)
        if not levels:
            create_default_bim_levels(doc)
            levels = discover_project_levels(doc)
        self.level_options = levels or [{"name": "Projeto", "object": "", "elevation": 0.0, "label": "Projeto / sem nível - 0.00 m"}]
        self.level_combo.clear()
        for level in self.level_options:
            self.level_combo.addItem(level["label"])
        self.command.level_options = list(self.level_options)
        self.command.set_reference_level(0)

    def populate_panels(self):
        self.panel_options = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.clear()
        self.panel_combo.addItem("Sem quadro")
        for panel in self.panel_options:
            self.panel_combo.addItem(panel["name"])

    def populate_circuits(self):
        self.circuit_options = discover_circuits(App.ActiveDocument, self.command.panel_board)
        for combo in [self.circuit1_combo, self.circuit2_combo]:
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Sem circuito")
            for circuit in self.circuit_options:
                combo.addItem(circuit["name"])
            combo.blockSignals(False)

    def populate_spaces(self):
        self.space_options = discover_spaces_or_sectors(App.ActiveDocument)
        self.space_combo.clear()
        self.space_combo.addItem("Sem ambiente/setor")
        for item in self.space_options:
            self.space_combo.addItem(item["name"])

    def on_level_selected(self, index):
        self.command.set_reference_level(index)
        self.sync_values()

    def on_panel_selected(self, index):
        self.command.panel_board = self.panel_options[index - 1]["name"] if index > 0 and index - 1 < len(self.panel_options) else ""
        self.populate_circuits()
        self.sync_values()

    def on_circuit_selected(self, index):
        self.sync_values()

    def on_space_selected(self, index):
        self.command.space_or_sector = self.space_options[index - 1]["name"] if index > 0 and index - 1 < len(self.space_options) else ""
        self.sync_values()

    def on_insert_mode_changed(self, index):
        self.command.continuous_insert = index == 0
        self.command.params.SetBool("ModularSetContinuousInsert", self.command.continuous_insert)
        self.sync_values()

    def sync_height(self):
        txt = self.height_combo.currentText()
        if "Baixa" in txt:
            self.z_in.setValue(self.command.socket_low_height)
        elif "Média" in txt:
            self.z_in.setValue(self.command.socket_medium_height)
        elif "Alta" in txt:
            self.z_in.setValue(self.command.socket_high_height)
        self.sync_values()

    def _circuit_data(self, combo):
        idx = combo.currentIndex()
        if idx > 0 and idx - 1 < len(self.circuit_options):
            circuit = self.circuit_options[idx - 1]
            return circuit["object"], circuit["number"]
        return "", ""

    def sync_values(self):
        self.command.plate_size = self.plate_combo.currentText()
        self.command.module1_type = self.module1_combo.currentText()
        self.command.module2_type = self.module2_combo.currentText()
        self.command.z_level = self.z_in.value()
        self.command.rotation = self.rot_in.value()
        self.command.module1_circuit_object, self.command.module1_circuit_number = self._circuit_data(self.circuit1_combo)
        self.command.module2_circuit_object, self.command.module2_circuit_number = self._circuit_data(self.circuit2_combo)
        self.final_z_label.setText(f"Z final: {self.command.get_final_z():.0f} mm")
        self.refresh_ghost()

    def sync_ui(self):
        self.z_in.blockSignals(True)
        self.z_in.setValue(self.command.z_level)
        self.z_in.blockSignals(False)
        self.rot_in.blockSignals(True)
        self.rot_in.setValue(self.command.rotation)
        self.rot_in.blockSignals(False)
        self.height_combo.blockSignals(True)
        self.height_combo.setCurrentText(self.command.normalized_height_type())
        self.height_combo.blockSignals(False)
        self.insert_mode_combo.blockSignals(True)
        self.insert_mode_combo.setCurrentIndex(0 if self.command.continuous_insert else 1)
        self.insert_mode_combo.blockSignals(False)
        self.final_z_label.setText(f"Z final: {self.command.get_final_z():.0f} mm")
        self.refresh_ghost()

    def refresh_ghost(self):
        if not hasattr(self.command, "engine") or not self.command.engine or not self.command.engine.ghost:
            return
        self.command.engine.ghost.Shape = self.command.make_preview_shape()
        try:
            self.command.engine.ghost.ViewObject.ShapeColor = self.command.preview_color()
            self.command.engine.ghost.ViewObject.LineColor = self.command.preview_color()
        except Exception:
            pass
        Gui.updateGui()

    def accept(self):
        Gui.Control.closeDialog()
        return True


class ModularSetCommand:
    def __init__(self):
        self.command_name = "Eletrica_InsertModularSet"
        self.tool_label = "conjunto modular"
        self.params = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Eletrica")
        self.plate_size = "4x2 - 2 módulos"
        self.module1_type = "Interruptor simples"
        self.module2_type = "Tomada 10A"
        self.z_level = 1100.0
        self.rotation = 0
        self.panel_board = ""
        self.space_or_sector = ""
        self.module1_circuit_object = ""
        self.module1_circuit_number = ""
        self.module2_circuit_object = ""
        self.module2_circuit_number = ""
        self.level_options = []
        self.reference_level_index = 0
        self.reference_level_name = "Projeto"
        self.reference_level_object = ""
        self.level_elevation = 0.0
        self.socket_low_height = 300.0
        self.socket_medium_height = 1100.0
        self.socket_high_height = 2200.0
        self.quiet_placement = True
        self.continuous_insert = self.params.GetBool("ModularSetContinuousInsert", True)
        self.engine = None
        self.load_project_defaults()

    def IsActive(self):
        return App.ActiveDocument is not None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            "Pixmap": os.path.join(base_path, "Icons", "Switch.svg"),
            "MenuText": "Conjunto Modular",
            "ToolTip": "Insere placa modular com tomada, interruptor ou módulos vazios",
            "Checkable": True,
        }

    def Activated(self, *args, **kwargs):
        if BIMPlacementEngine.active_engine is not None:
            active_engine = BIMPlacementEngine.active_engine
            active_cmd = active_engine.cmd
            if getattr(active_cmd, "command_name", "") == self.command_name:
                active_engine.stop()
                return
        if not App.ActiveDocument:
            App.newDocument("Projeto_Eletrico")
        self.load_project_defaults()
        self.engine = BIMPlacementEngine(self, ModularSetTaskPanel, self.place_set)
        self.engine.start()

    def IsChecked(self):
        try:
            return getattr(BIMPlacementEngine.active_engine.cmd, "command_name", "") == self.command_name
        except Exception:
            return False

    def load_project_defaults(self):
        doc = App.ActiveDocument
        if not doc:
            return
        project = None
        for obj in doc.Objects:
            if obj.Label == "Projeto Eletrico":
                project = obj
                break
        if not project:
            return
        for attr, prop, default in [
            ("socket_low_height", "SocketLowHeight", 300.0),
            ("socket_medium_height", "SocketMediumHeight", 1100.0),
            ("socket_high_height", "SocketHighHeight", 2200.0),
        ]:
            try:
                value = getattr(project, prop)
                setattr(self, attr, float(value.Value if hasattr(value, "Value") else value))
            except Exception:
                setattr(self, attr, default)
        self.z_level = self.socket_medium_height

    def set_reference_level(self, index):
        if not self.level_options:
            self.level_options = [{"name": "Projeto", "object": "", "elevation": 0.0, "label": "Projeto / sem nível - 0.00 m"}]
        index = max(0, min(index, len(self.level_options) - 1))
        level = self.level_options[index]
        self.reference_level_index = index
        self.reference_level_name = level["name"]
        self.reference_level_object = level["object"]
        self.level_elevation = float(level["elevation"])

    def cycle_level(self):
        if self.level_options:
            self.set_reference_level((self.reference_level_index + 1) % len(self.level_options))

    def cycle_height(self):
        heights = [self.socket_low_height, self.socket_medium_height, self.socket_high_height]
        nearest = min(range(len(heights)), key=lambda idx: abs(float(heights[idx]) - float(self.z_level)))
        self.z_level = float(heights[(nearest + 1) % len(heights)])

    def cycle_insert_mode(self):
        self.continuous_insert = not self.continuous_insert
        self.params.SetBool("ModularSetContinuousInsert", self.continuous_insert)

    def get_final_z(self):
        return float(self.level_elevation) + float(self.z_level)

    def normalized_height_type(self):
        if self.z_level <= 700:
            return "Baixa (300mm)"
        if self.z_level <= 1600:
            return "Média (1100mm)"
        return "Alta (2200mm)"

    def module_types(self):
        return [self.module1_type, self.module2_type]

    def make_preview_shape(self):
        return make_modular_set_symbol(self.module_types(), self.plate_size)

    def preview_color(self):
        if any("Interruptor" in item for item in self.module_types()) and any("Tomada" in item for item in self.module_types()):
            return (0.0, 0.45, 1.0)
        if any("Interruptor" in item for item in self.module_types()):
            return (0.05, 0.55, 0.25)
        return (0.0, 0.35, 1.0)

    def _summary_circuit_number(self):
        values = []
        for value in [self.module1_circuit_number, self.module2_circuit_number]:
            if value and value not in values:
                values.append(value)
        return " / ".join(values)

    def place_set(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        obj = doc.addObject("Part::Feature", "GHOST_ModularSet" if is_ghost else "Conjunto_Modular")
        obj.Shape = self.make_preview_shape()

        if is_ghost:
            doc.recompute()
            if obj.ViewObject is not None:
                obj.ViewObject.Transparency = 15
                obj.ViewObject.ShapeColor = self.preview_color()
                try:
                    obj.ViewObject.LineColor = self.preview_color()
                except Exception:
                    pass
                obj.ViewObject.LineWidth = 4.0
                obj.ViewObject.Selectable = False
                if hasattr(obj.ViewObject, "ShowInTree"):
                    obj.ViewObject.ShowInTree = False
        else:
            g = "BIM_Conjunto"
            _add_prop(obj, "App::PropertyString", "BIMRole", g, "ModularSet")
            _add_prop(obj, "App::PropertyString", "IFC_Class", g, "IfcFlowTerminal")
            _add_prop(obj, "App::PropertyString", "PlateSize", g, self.plate_size)
            _add_prop(obj, "App::PropertyString", "Module1Type", g, self.module1_type)
            _add_prop(obj, "App::PropertyString", "Module2Type", g, self.module2_type)
            _add_prop(obj, "App::PropertyString", "Module1Role", g, module_role(self.module1_type))
            _add_prop(obj, "App::PropertyString", "Module2Role", g, module_role(self.module2_type))
            _add_prop(obj, "App::PropertyString", "Module1CircuitNumber", g, self.module1_circuit_number)
            _add_prop(obj, "App::PropertyString", "Module2CircuitNumber", g, self.module2_circuit_number)
            _add_prop(obj, "App::PropertyString", "Module1CircuitObject", g, self.module1_circuit_object)
            _add_prop(obj, "App::PropertyString", "Module2CircuitObject", g, self.module2_circuit_object)
            _add_prop(obj, "App::PropertyFloat", "Module1Power", g, module_power(self.module1_type))
            _add_prop(obj, "App::PropertyFloat", "Module2Power", g, module_power(self.module2_type))
            _add_prop(obj, "App::PropertyString", "PanelBoard", g, self.panel_board)
            _add_prop(obj, "App::PropertyString", "CircuitNumber", g, self._summary_circuit_number())
            _add_prop(obj, "App::PropertyString", "CircuitObject", g, self.module1_circuit_object or self.module2_circuit_object)
            _add_prop(obj, "App::PropertyFloat", "Power", g, module_power(self.module1_type) + module_power(self.module2_type))
            _add_prop(obj, "App::PropertyString", "SpaceOrSector", g, self.space_or_sector)
            _add_prop(obj, "App::PropertyString", "ReferenceLevel", g, self.reference_level_name)
            _add_prop(obj, "App::PropertyString", "ReferenceLevelObject", g, self.reference_level_object)
            _add_prop(obj, "App::PropertyLength", "MountingHeight", g, self.z_level)
            _add_prop(obj, "App::PropertyLength", "FinalElevation", g, self.get_final_z())
            obj.ViewObject.ShapeColor = self.preview_color()

            count = len([o for o in doc.Objects if "Conjunto Modular" in getattr(o, "Label", "")]) + 1
            obj.Label = f"Conjunto Modular {count:02d}"

        px = point.x if hasattr(point, "x") else point[0]
        py = point.y if hasattr(point, "y") else point[1]
        obj.Placement = App.Placement(App.Vector(px, py, self.get_final_z()), App.Rotation(App.Vector(0, 0, 1), self.rotation))

        if not is_ghost:
            if self.reference_level_object:
                level_obj = doc.getObject(self.reference_level_object)
                if level_obj and hasattr(level_obj, "addObject"):
                    level_obj.addObject(obj)
            try:
                from EletricaGuiCommands.ProjectSetup import recalculate_circuit_loads
                recalculate_circuit_loads(doc)
            except Exception:
                pass
            doc.recompute()
        return obj
