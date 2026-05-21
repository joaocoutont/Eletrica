import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .motor_bim import ProfessionalBIMMotor
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, discover_panel_boards
)

# TABELA TÉCNICA SIMPLIFICADA MOTORES WEG W22 (4 POLOS)
# cv: {frame, kW, efficiency, pf}
WEG_MOTOR_DATABASE = {
    "0.5 cv":  {"frame": "71",   "kw": 0.37, "eff": 78.0, "pf": 0.70},
    "0.75 cv": {"frame": "71",   "kw": 0.55, "eff": 80.0, "pf": 0.72},
    "1.0 cv":  {"frame": "80",   "kw": 0.75, "eff": 82.5, "pf": 0.75},
    "1.5 cv":  {"frame": "80",   "kw": 1.1,  "eff": 84.1, "pf": 0.77},
    "2.0 cv":  {"frame": "90S/L","kw": 1.5,  "eff": 85.3, "pf": 0.79},
    "3.0 cv":  {"frame": "90L",  "kw": 2.2,  "eff": 86.7, "pf": 0.81},
    "5.0 cv":  {"frame": "112M", "kw": 3.7,  "eff": 88.4, "pf": 0.83},
    "7.5 cv":  {"frame": "132S", "kw": 5.5,  "eff": 89.5, "pf": 0.84},
    "10 cv":   {"frame": "132M", "kw": 7.5,  "eff": 90.4, "pf": 0.85},
    "15 cv":   {"frame": "160M", "kw": 11.0, "eff": 91.4, "pf": 0.86},
    "20 cv":   {"frame": "160L", "kw": 15.0, "eff": 92.1, "pf": 0.87},
    "30 cv":   {"frame": "180M", "kw": 22.0, "eff": 93.0, "pf": 0.88}
}

class MotorTaskPanel:
    """Interface para Inserção de Motores Elétricos"""
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
        
        # --- SELEÇÃO DE POTÊNCIA ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Potência do Motor (WEG W22):</b>"))
        self.power_combo = QtGui.QComboBox()
        self.power_combo.addItems(list(WEG_MOTOR_DATABASE.keys()))
        self.power_combo.currentTextChanged.connect(self.on_power_changed)
        self.scroll_layout.addWidget(self.power_combo)
        
        # DADOS TÉCNICOS AUTOMÁTICOS
        self.data_group = QtGui.QGroupBox("Especificação Técnica (Auto)")
        self.data_form = QtGui.QFormLayout()
        self.info_label = QtGui.QLabel("---")
        self.data_form.addRow(self.info_label)
        self.data_group.setLayout(self.data_form)
        self.scroll_layout.addWidget(self.data_group)

        # ENGENHARIA ELÉTRICA
        eng_group = QtGui.QGroupBox("Engenharia Elétrica")
        eng_form = QtGui.QFormLayout()
        
        self.voltage_combo = QtGui.QComboBox()
        self.voltage_combo.addItems(["220/380/440V", "380/660V", "440/760V"])
        eng_form.addRow("Tensão Nom.:", self.voltage_combo)
        
        self.poles_combo = QtGui.QComboBox()
        self.poles_combo.addItems(["2 Polos (3600 rpm)", "4 Polos (1800 rpm)", "6 Polos (1200 rpm)", "8 Polos (900 rpm)"])
        self.poles_combo.setCurrentIndex(1)
        eng_form.addRow("Polos:", self.poles_combo)
        
        eng_group.setLayout(eng_form)
        self.scroll_layout.addWidget(eng_group)

        # BIM / IDENTIFICAÇÃO
        bim_group = QtGui.QGroupBox("BIM")
        bim_form = QtGui.QFormLayout()
        self.tag_in = QtGui.QLineEdit("M-01")
        bim_form.addRow("TAG Motor:", self.tag_in)
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        bim_form.addRow("Alimentado pelo Quadro:", self.panel_combo)
        bim_group.setLayout(bim_form)
        self.scroll_layout.addWidget(bim_group)

        self.scroll_layout.addStretch()
        self.on_power_changed(self.power_combo.currentText())

    def on_power_changed(self, text):
        data = WEG_MOTOR_DATABASE.get(text)
        if not data: return
        
        self.command.power_cv = text
        self.command.power_kw = data["kw"]
        self.command.frame = data["frame"]
        self.command.efficiency = data["eff"]
        self.command.pf = data["pf"]
        
        self.info_label.setText(
            f"<b>Carcaça:</b> {data['frame']} | <b>Potência:</b> {data['kw']} kW<br>"
            f"<b>Rendimento:</b> {data['eff']}% | <b>FP:</b> {data['pf']}"
        )
        self.refresh_ghost()

    def populate_panels(self):
        panels = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.addItem("Local / Direto")
        for p in panels: self.panel_combo.addItem(p["name"])

    def sync_values(self):
        self.command.voltage = self.voltage_combo.currentText()
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

class MotorCommand:
    """Comando de Inserção de Motores Elétricos BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertMotor"
        self.power_cv = "1.0 cv"
        self.power_kw = 0.75
        self.frame = "80"
        self.voltage = "220/380/440V"
        self.tag = "M-01"
        self.efficiency = 82.5
        self.pf = 0.75
        self.family_file = ""
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "MotorStarter.svg"),
            'MenuText': 'Inserir Motor Elétrico',
            'ToolTip': 'Insere motor WEG W22 com dados de placa e carcaça BIM',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, MotorTaskPanel, self.place_motor)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .motor_bim import make_motor_plan_symbol
            return make_motor_plan_symbol()
        except Exception:
            return Part.makeBox(150, 150, 5)

    def place_motor(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Industrial")
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_Motor")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
                obj.ViewObject.Transparency = 40
        else:
            matriz_label = f"Matriz_Motor_{self.frame.replace('/','_')}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMMotor(matriz)
                matriz.Frame = self.frame
                matriz.Power_cv = float(self.power_cv.split(' ')[0])
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"Motor_{self.tag.replace('-','_')}")
            obj.LinkedObject = matriz
            
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("Power_cv", float(self.power_cv.split(' ')[0]), ptype="App::PropertyFloat")
            _set_prop("Power_kw", self.power_kw, ptype="App::PropertyFloat")
            _set_prop("Frame", self.frame, group="BIM_3D_Parametros")
            _set_prop("Tag", self.tag, group="BIM_Classificacao")

            if obj.ViewObject: obj.ViewObject.ShapeColor = (0.2, 0.4, 0.6) # Azul WEG
            obj.Label = f"[{self.tag}] Motor {self.power_cv} ({self.frame})"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .motor_bim import make_motor_plan_symbol
            shape = make_motor_plan_symbol()
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.1, 0.3, 0.5)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertMotor', MotorCommand())
