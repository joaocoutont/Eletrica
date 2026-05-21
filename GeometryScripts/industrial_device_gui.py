import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .industrial_device_bim import ProfessionalBIMIndustrialDevice
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, discover_panel_boards, discover_circuits
)

INDUSTRIAL_DEVICES = {
    "Transmissor de Pressão (PIT)": {"file": "Pressure_Transmitter.FCStd", "cat": "Instrumentação/Sensor", "sig": "4-20 mA", "tag": "PIT"},
    "Transmissor de Nível (LIT)":    {"file": "Level_Transmitter.FCStd",    "cat": "Instrumentação/Sensor", "sig": "4-20 mA", "tag": "LIT"},
    "Medidor de Vazão (FIT)":       {"file": "Flow_Meter.FCStd",          "cat": "Instrumentação/Sensor", "sig": "4-20 mA", "tag": "FIT"},
    "Sensor Indutivo (ZSC)":        {"file": "Proximity_Inductive.FCStd", "cat": "Instrumentação/Sensor", "sig": "Digital (PNP/NPN)", "tag": "ZSC"},
    "Válvula Solenoide (XV)":       {"file": "Solenoid_Valve.FCStd",       "cat": "Atuador/Execução",      "sig": "Digital (24V DC)", "tag": "XV"},
    "Motor Elétrico (M)":           {"file": "Industrial_Motor.FCStd",     "cat": "Atuador/Execução",      "sig": "Digital (Comando)", "tag": "M"},
    "Inversor de Frequência (VFD)": {"file": "Frequency_Inverter.FCStd",  "cat": "Atuador/Execução",      "sig": "Modbus RTU", "tag": "VFD"}
}

class IndustrialDeviceTaskPanel:
    """Interface para Automação e Instrumentação Industrial"""
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
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Dispositivo de Automação:</b>"))
        self.dev_combo = QtGui.QComboBox()
        self.dev_combo.addItems(sorted(INDUSTRIAL_DEVICES.keys()))
        self.dev_combo.currentTextChanged.connect(self.on_device_changed)
        self.scroll_layout.addWidget(self.dev_combo)
        
        # ENGENHARIA
        eng_group = QtGui.QGroupBox("Especificação Técnica")
        eng_form = QtGui.QFormLayout()
        
        self.sig_combo = QtGui.QComboBox()
        self.sig_combo.addItems(["4-20 mA", "0-10 V", "Digital (PNP/NPN)", "Modbus RTU", "Profinet", "Hart"])
        eng_form.addRow("Tipo de Sinal:", self.sig_combo)

        self.voltage_combo = QtGui.QComboBox()
        self.voltage_combo.addItems(["24V DC", "127V AC", "220V AC", "Loop Powered"])
        eng_form.addRow("Alimentação:", self.voltage_combo)

        self.tag_in = QtGui.QLineEdit("FIT-101")
        eng_form.addRow("TAG (Instrumento):", self.tag_in)
        
        eng_group.setLayout(eng_form)
        self.scroll_layout.addWidget(eng_group)

        # INSTALAÇÃO
        pos_group = QtGui.QGroupBox("Instalação / Processo")
        pos_form = QtGui.QFormLayout()
        
        self.mount_in = QtGui.QLineEdit("Tubulação / Flange")
        pos_form.addRow("Montagem:", self.mount_in)

        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(-1000, 50000); self.z_in.setValue(1500)
        pos_form.addRow("Elevação (mm):", self.z_in)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        self.scroll_layout.addStretch()
        self.on_device_changed(self.dev_combo.currentText())

    def on_device_changed(self, text):
        data = INDUSTRIAL_DEVICES.get(text)
        if not data: return
        self.command.device_type = text
        self.command.family_file = data["file"]
        self.command.device_category = data["cat"]
        self.command.tag_prefix = data["tag"]
        
        self.sig_combo.setCurrentText(data["sig"])
        self.tag_in.setText(f"{data['tag']}-101")
        self.refresh_ghost()

    def sync_values(self):
        self.command.tag = self.tag_in.text()
        self.command.signal_type = self.sig_combo.currentText()
        self.command.z_level = self.z_in.value()
        self.refresh_ghost()

    def refresh_ghost(self):
        if hasattr(self.command, 'engine') and self.command.engine.ghost:
            self.command.engine.ghost.Shape = self.command.make_preview_shape()
            Gui.updateGui()

    def accept(self):
        self.sync_values()
        Gui.Control.closeDialog()
        return True

class IndustrialDeviceCommand:
    """Comando de Inserção de Instrumentação Industrial BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertAutomationDevice"
        self.device_type = ""
        self.device_category = "Instrumentação/Sensor"
        self.signal_type = "4-20 mA"
        self.tag = "FIT-101"
        self.tag_prefix = "FIT"
        self.z_level = 1500.0
        self.family_file = "Sensor_Generico.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "Automation.svg"),
            'MenuText': 'Sensor/Atuador Industrial',
            'ToolTip': 'Insere sensores de nível, pressão, vazão e atuadores conforme ISA-5.1',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, IndustrialDeviceTaskPanel, self.place_device)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .industrial_device_bim import make_industrial_plan_symbol
            return make_industrial_plan_symbol(self.device_type, self.tag_prefix[0])
        except Exception:
            return Part.makeSphere(50)

    def place_device(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Automacao")
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_IndDevice")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.5, 0.0, 1.0) # Roxo para automação industrial
                obj.ViewObject.Transparency = 30
        else:
            matriz_label = f"Matriz_Ind_{self.tag_prefix}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMIndustrialDevice(matriz)
                matriz.SourceFile = self.family_file
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"IND_{self.tag.replace('-','_')}")
            obj.LinkedObject = matriz
            
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("DeviceCategory", self.device_category)
            _set_prop("SignalType", self.signal_type)
            _set_prop("Tag", self.tag, group="BIM_Classificacao")
            _set_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")

            if obj.ViewObject: obj.ViewObject.ShapeColor = (0.4, 0.0, 0.8)
            obj.Label = f"[{self.tag}] {self.device_type}"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(0,0,0,1))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .industrial_device_bim import make_industrial_plan_symbol
            shape = make_industrial_plan_symbol(self.device_type, self.tag_prefix[0])
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.4, 0.0, 0.7)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertAutomationDevice', IndustrialDeviceCommand())
