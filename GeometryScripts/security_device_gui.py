import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .security_device_bim import ProfessionalBIMSecurityDevice
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, discover_panel_boards
)

SECURITY_DEVICES = {
    "Câmera Dome IP (Interna)":   {"file": "Camera_Dome_IP.FCStd",   "type": "Câmera Dome", "mount": "Teto", "z": 2800, "fov": 90.0, "tag": "CAM"},
    "Câmera Bullet IP (Externa)": {"file": "Camera_Bullet_IP.FCStd", "type": "Câmera Bullet", "mount": "Parede", "z": 3000, "fov": 60.0, "tag": "CAM"},
    "Câmera PTZ Speed Dome":      {"file": "Camera_PTZ_IP.FCStd",    "type": "Câmera PTZ", "mount": "Poste", "z": 5000, "fov": 360.0, "tag": "PTZ"},
    "Câmera Fisheye 360°":        {"file": "Camera_Fisheye.FCStd",   "type": "Câmera Fisheye 360", "mount": "Teto", "z": 2800, "fov": 180.0, "tag": "CAM"},
    "Leitor Biométrico / Facial": {"file": "Access_Reader_Bio.FCStd","type": "Leitor de Acesso (RFID/Biometria)", "mount": "Parede", "z": 1200, "fov": 0.0, "tag": "ACA"},
    "Sensor de Intrusão (PIR)":   {"file": "Sensor_PIR_Motion.FCStd","type": "Sensor de Intrusão (PIR)", "mount": "Parede", "z": 2200, "fov": 110.0, "tag": "PIR"}
}

class SecurityDeviceTaskPanel:
    """Interface para Inserção de Dispositivos de CFTV e Segurança"""
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
        
        # --- SELEÇÃO DE EQUIPAMENTO ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Equipamento de Segurança:</b>"))
        self.dev_combo = QtGui.QComboBox()
        self.dev_combo.addItems(sorted(SECURITY_DEVICES.keys()))
        self.dev_combo.currentTextChanged.connect(self.on_device_changed)
        self.scroll_layout.addWidget(self.dev_combo)
        
        # ENGENHARIA CFTV
        cftv_group = QtGui.QGroupBox("Especificação Técnica")
        cftv_form = QtGui.QFormLayout()
        
        self.res_combo = QtGui.QComboBox()
        self.res_combo.addItems(["2 MP (1080p)", "4 MP (1440p)", "8 MP (4K UHD)", "N/A (Acesso/Sensor)"])
        cftv_form.addRow("Resolução:", self.res_combo)
        
        self.lens_combo = QtGui.QComboBox()
        self.lens_combo.addItems(["2.8mm (Grande Angular)", "3.6mm (Padrão)", "6.0mm (Teleobjetiva)", "Varifocal Motorizada"])
        cftv_form.addRow("Lente:", self.lens_combo)
        
        self.fov_in = QtGui.QDoubleSpinBox(); self.fov_in.setRange(0, 360); self.fov_in.setValue(90)
        self.fov_in.valueChanged.connect(self.sync_values)
        cftv_form.addRow("Ângulo Visão (FOV):", self.fov_in)
        
        self.power_combo = QtGui.QComboBox()
        self.power_combo.addItems(["PoE (802.3af/at)", "12V DC", "24V AC"])
        cftv_form.addRow("Alimentação:", self.power_combo)
        
        cftv_group.setLayout(cftv_form)
        self.scroll_layout.addWidget(cftv_group)

        # INSTALAÇÃO
        pos_group = QtGui.QGroupBox("Instalação")
        pos_form = QtGui.QFormLayout()
        
        self.tag_in = QtGui.QLineEdit("CAM-01")
        pos_form.addRow("TAG/Nome:", self.tag_in)
        
        self.mount_combo = QtGui.QComboBox()
        self.mount_combo.addItems(["Teto", "Parede", "Poste", "Muro"])
        pos_form.addRow("Montagem:", self.mount_combo)

        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 100000); self.z_in.setValue(2800)
        self.z_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Altura Z (mm):", self.z_in)
        
        self.rot_in = QtGui.QSpinBox(); self.rot_in.setRange(0, 360); self.rot_in.setSingleStep(45)
        self.rot_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Orientação Lente:", self.rot_in)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        self.scroll_layout.addStretch()
        self.on_device_changed(self.dev_combo.currentText())

    def on_device_changed(self, text):
        data = SECURITY_DEVICES.get(text)
        if not data: return
        self.command.device_type = data["type"]
        self.command.family_file = data["file"]
        self.mount_combo.setCurrentText(data["mount"])
        self.z_in.setValue(data["z"])
        self.fov_in.setValue(data["fov"])
        self.tag_in.setText(f"{data['tag']}-01")
        
        if "Câmera" not in data["type"]:
            self.res_combo.setCurrentText("N/A (Acesso/Sensor)")
            self.power_combo.setCurrentText("12V DC")
        else:
            self.res_combo.setCurrentIndex(0)
            self.power_combo.setCurrentText("PoE (802.3af/at)")

        self.refresh_ghost()

    def sync_values(self):
        self.command.z_level = self.z_in.value()
        self.command.rotation = self.rot_in.value()
        self.command.fov = self.fov_in.value()
        self.command.tag = self.tag_in.text()
        self.command.resolution = self.res_combo.currentText()
        self.command.lens = self.lens_combo.currentText()
        self.command.power = self.power_combo.currentText()
        self.refresh_ghost()

    def refresh_ghost(self):
        if hasattr(self.command, 'engine') and self.command.engine.ghost:
            self.command.engine.ghost.Shape = self.command.make_preview_shape()
            Gui.updateGui()

    def accept(self):
        self.sync_values()
        Gui.Control.closeDialog()
        return True

class SecurityDeviceCommand:
    """Comando de Inserção de CFTV e Segurança BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertSecurityDevice"
        self.device_type = "Câmera Dome"
        self.z_level = 2800.0
        self.rotation = 0
        self.fov = 90.0
        self.tag = "CAM-01"
        self.resolution = "2 MP (1080p)"
        self.lens = "2.8mm"
        self.power = "PoE"
        self.family_file = "Camera_Dome.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "Camera.svg"),
            'MenuText': 'Câmera/Segurança',
            'ToolTip': 'Insere câmeras CFTV, controles de acesso e sensores',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, SecurityDeviceTaskPanel, self.place_device)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .security_device_bim import make_security_plan_symbol
            # Rotacionar o símbolo para apontar na direção configurada
            shape = make_security_plan_symbol(self.device_type, self.fov)
            if shape: shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), self.rotation)
            return shape
        except Exception:
            return Part.makeSphere(40)

    def place_device(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Seguranca")
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_Security")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.9, 0.9, 0.9) # Branco câmera
                obj.ViewObject.Transparency = 30
        else:
            matriz_label = f"Matriz_Sec_{self.device_type.replace(' ','')}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMSecurityDevice(matriz)
                matriz.SourceFile = self.family_file
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"SEC_{self.tag.replace('-','_')}")
            obj.LinkedObject = matriz
            
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("DeviceType", self.device_type)
            _set_prop("Resolution", self.resolution)
            _set_prop("Lens", self.lens)
            _set_prop("FOV_Angle", self.fov, ptype="App::PropertyFloat")
            _set_prop("PowerSupply", self.power)
            
            _set_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")
            _set_prop("Tag", self.tag, group="BIM_Classificacao")

            if obj.ViewObject: obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
            obj.Label = f"[{self.tag}] {self.device_type}"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(0,0,0,1))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .security_device_bim import make_security_plan_symbol
            shape = make_security_plan_symbol(self.device_type, self.fov)
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(App.Vector(0,0,1), self.rotation))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.2, 0.2, 0.2)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertSecurityDevice', SecurityDeviceCommand())
