import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .ac_socket_bim import ProfessionalBIMACSocket
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, create_default_bim_levels, discover_panel_boards,
    discover_circuits, discover_spaces_or_sectors
)
from .special_socket_bim import make_special_socket_plan_symbol

# BANCO DE DADOS TÉCNICO DE AR CONDICIONADO
AC_DATABASE = {
    "9.000 BTU/h":  {"power_w": 900,  "fp": 0.85, "phases": "Bifásico (2F+T)",   "v": "220V", "amp": "10A"},
    "12.000 BTU/h": {"power_w": 1200, "fp": 0.85, "phases": "Bifásico (2F+T)",   "v": "220V", "amp": "10A"},
    "18.000 BTU/h": {"power_w": 1800, "fp": 0.85, "phases": "Bifásico (2F+T)",   "v": "220V", "amp": "20A"},
    "24.000 BTU/h": {"power_w": 2400, "fp": 0.85, "phases": "Bifásico (2F+T)",   "v": "220V", "amp": "20A"},
    "30.000 BTU/h": {"power_w": 3000, "fp": 0.88, "phases": "Bifásico (2F+T)",   "v": "220V", "amp": "25A"},
    "36.000 BTU/h": {"power_w": 3600, "fp": 0.90, "phases": "Bifásico (2F+T)",   "v": "220V", "amp": "25A"},
    "48.000 BTU/h": {"power_w": 4800, "fp": 0.90, "phases": "Trifásico (3F+T)",  "v": "220V", "amp": "32A"},
    "60.000 BTU/h": {"power_w": 6000, "fp": 0.92, "phases": "Trifásico (3F+T)",  "v": "220V", "amp": "40A"},
}

class ACSocketTaskPanel:
    """Interface para Pontos de Ar Condicionado"""
    def __init__(self, command_obj):
        self.command = command_obj
        self.form = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(self.form)
        
        self.scroll = QtGui.QScrollArea(self.form)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtGui.QFrame.NoFrame)
        self.layout.addWidget(self.scroll)
        
        self.scroll_content = QtGui.QWidget()
        self.scroll_layout = QtGui.QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        
        # --- SELEÇÃO DE CAPACIDADE (BTU) ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Capacidade do Ar Condicionado:</b>"))
        self.btu_combo = QtGui.QComboBox()
        self.btu_combo.addItems(list(AC_DATABASE.keys()))
        self.btu_combo.currentTextChanged.connect(self.on_btu_changed)
        self.scroll_layout.addWidget(self.btu_combo)
        
        # INFORMAÇÕES TÉCNICAS SUGERIDAS
        self.info_group = QtGui.QGroupBox("Especificação Elétrica (Sugerida)")
        self.info_form = QtGui.QFormLayout()
        
        self.power_in = QtGui.QDoubleSpinBox(); self.power_in.setRange(0, 20000); self.power_in.setSuffix(" W")
        self.power_in.valueChanged.connect(self.sync_values)
        self.info_form.addRow("Potência Ativa:", self.power_in)

        self.voltage_combo = QtGui.QComboBox()
        self.voltage_combo.addItems(["220V", "127V", "380V"])
        self.voltage_combo.currentTextChanged.connect(self.sync_values)
        self.info_form.addRow("Tensão:", self.voltage_combo)

        self.phases_combo = QtGui.QComboBox()
        self.phases_combo.addItems(["Bifásico (2F+T)", "Monofásico (1F+N+T)", "Trifásico (3F+T)"])
        self.phases_combo.currentTextChanged.connect(self.sync_values)
        self.info_form.addRow("Configuração:", self.phases_combo)
        
        self.info_group.setLayout(self.info_form)
        self.scroll_layout.addWidget(self.info_group)

        # POSICIONAMENTO
        pos_group = QtGui.QGroupBox("Instalação")
        pos_form = QtGui.QFormLayout()
        
        self.level_combo = QtGui.QComboBox()
        self.populate_levels()
        pos_form.addRow("Nível:", self.level_combo)

        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 5000); self.z_in.setValue(2200)
        self.z_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Altura (mm):", self.z_in)

        self.rot_in = QtGui.QSpinBox(); self.rot_in.setRange(0, 360); self.rot_in.setSingleStep(90)
        self.rot_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Rotação (°):", self.rot_in)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        # BIM
        bim_group = QtGui.QGroupBox("BIM")
        bim_form = QtGui.QFormLayout()
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        bim_form.addRow("Quadro:", self.panel_combo)
        bim_group.setLayout(bim_form)
        self.scroll_layout.addWidget(bim_group)

        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(QtGui.QLabel("Dica: ACs acima de 30k BTU costumam ser trifásicos."))
        
        # Init
        self.on_btu_changed(self.btu_combo.currentText())

    def on_btu_changed(self, text):
        data = AC_DATABASE.get(text)
        if not data: return
        
        self.command.btu_rating = text
        self.power_in.blockSignals(True)
        self.power_in.setValue(data["power_w"])
        self.power_in.blockSignals(False)
        
        self.voltage_combo.setCurrentText(data["v"])
        self.phases_combo.setCurrentText(data["phases"])
        
        self.command.power_w = data["power_w"]
        self.command.voltage = data["v"]
        self.command.phases = data["phases"]
        self.command.power_factor = data["fp"]
        
        self.refresh_ghost()

    def populate_levels(self):
        levels = discover_project_levels(App.ActiveDocument)
        for level in levels: self.level_combo.addItem(level["label"])

    def populate_panels(self):
        panels = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.addItem("Sem quadro")
        for p in panels: self.panel_combo.addItem(p["name"])

    def sync_values(self):
        self.command.power_w = self.power_in.value()
        self.command.voltage = self.voltage_combo.currentText()
        self.command.phases = self.phases_combo.currentText()
        self.command.z_level = self.z_in.value()
        self.command.rotation = self.rot_in.value()
        self.refresh_ghost()

    def refresh_ghost(self):
        if hasattr(self.command, 'engine') and self.command.engine.ghost:
            self.command.engine.ghost.Shape = self.command.make_preview_shape()
            Gui.updateGui()

    def accept(self):
        Gui.Control.closeDialog()
        return True

class ACSocketCommand:
    """Comando de Inserção de Pontos de Ar Condicionado BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertAirConditioner"
        self.btu_rating = "9.000 BTU/h"
        self.power_w = 900.0
        self.power_factor = 0.85
        self.voltage = "220V"
        self.phases = "Bifásico (2F+T)"
        self.z_level = 2200.0
        self.rotation = 0
        self.family_file = "Tomada_Simples_20A.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "AirConditioning.svg"),
            'MenuText': 'Tomada Ar Condicionado',
            'ToolTip': 'Insere ponto de alimentação para AC com seleção por BTU',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, ACSocketTaskPanel, self.place_ac_socket)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .special_socket_bim import make_special_socket_plan_symbol
            # Ar condicionado usa o símbolo de TUE (preenchido) por padrão
            return make_special_socket_plan_symbol("Alta", "1 Módulo", "20A")
        except Exception:
            return Part.makeBox(80, 120, 2)

    def place_ac_socket(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_AC")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.0, 0.6, 1.0) # Azul gelo/ar
                obj.ViewObject.Transparency = 20
        else:
            matriz_label = f"Matriz_AC_{self.btu_rating.replace('.','').split(' ')[0]}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMACSocket(matriz)
                matriz.SourceFile = self.family_file
                matriz.BTU_Rating = self.btu_rating
                matriz.Label = f"Matriz AC {self.btu_rating}"
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"AC_{self.btu_rating.split(' ')[0]}")
            obj.LinkedObject = matriz
            
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("Power", self.power_w, ptype="App::PropertyFloat")
            _set_prop("Voltage", self.voltage)
            _set_prop("Phases", self.phases)
            _set_prop("Tag", f"AC-{self.btu_rating.split(' ')[0]}")
            _set_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")

            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.0, 0.6, 1.0)

            obj.Label = f"Tomada AC {self.btu_rating}"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(App.Vector(0,0,1), self.rotation + 180))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .special_socket_bim import make_special_socket_plan_symbol
            shape = make_special_socket_plan_symbol("Alta", "1 Módulo", "20A")
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py + 18.0, 0), App.Rotation(App.Vector(0,0,1), self.rotation))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.0, 0.5, 0.9)
                sym_obj.ViewObject.LineWidth = 2.5
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertAirConditioner', ACSocketCommand())
