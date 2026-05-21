import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
try:
    import Arch
    _ARCH_AVAILABLE = True
except ImportError:
    _ARCH_AVAILABLE = False
import Part
from .iot_bim import ProfessionalBIMIoT
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, create_default_bim_levels, discover_panel_boards,
    discover_circuits, discover_spaces_or_sectors, LEVEL_KEYWORDS, DEFAULT_BIM_LEVELS,
    _is_level_object, _level_elevation, _plain_value, _set_property, _object_text
)

SYMBOL_PLANE_MODES = ["Plano de simbologia", "Junto do dispositivo"]
IOT_3D_LINK_ROTATION_OFFSET_DEG = 180.0
IOT_2D_SYMBOL_Y_OFFSET = 18.0

class IoTTaskPanel:
    """Interface de Famílias de IoT e Automação"""
    def __init__(self, command_obj):
        self.command = command_obj
        self.form = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(self.form)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QtGui.QScrollArea(self.form)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtGui.QFrame.NoFrame)
        self.layout.addWidget(self.scroll)
        
        self.scroll_content = QtGui.QWidget()
        self.scroll_layout = QtGui.QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        
        self.family_meta_by_source = {}
        
        # --- CATÁLOGO DE FAMÍLIAS (LISTA) ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Dispositivos Smart/IoT:</b>"))
        self.family_list = QtGui.QListWidget()
        self.family_list.setMinimumHeight(120)
        self.family_list.currentItemChanged.connect(lambda current, previous: self.on_family_selected(current))
        self.scroll_layout.addWidget(self.family_list)
        self.add_quick_type_controls()
        self.populate_families()
        
        # ALTURA E POSIÇÃO
        pos_group = QtGui.QGroupBox("Posicionamento (Z)")
        pos_form = QtGui.QFormLayout()

        self.level_options = []
        self.level_combo = QtGui.QComboBox()
        self.populate_levels()
        self.level_combo.currentIndexChanged.connect(self.on_level_selected)
        pos_form.addRow("Nível:", self.level_combo)
        
        self.height_combo = QtGui.QComboBox()
        self.height_combo.addItems(["Teto (2800mm)", "Parede Alta (2200mm)", "Parede Média (1100mm)", "Rodapé/Piso (300mm)"])
        self.height_combo.currentTextChanged.connect(self.sync_height)
        pos_form.addRow("Altura Padrão:", self.height_combo)
        
        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(-5000, 10000); self.z_in.setValue(2200)
        self.z_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Altura Inst. (mm):", self.z_in)

        self.rot_in = QtGui.QSpinBox(); self.rot_in.setRange(0, 360); self.rot_in.setSingleStep(90)
        self.rot_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Rotação (°):", self.rot_in)

        self.insert_mode_combo = QtGui.QComboBox()
        self.insert_mode_combo.addItems(["Contínuo", "Uma vez"])
        self.insert_mode_combo.currentIndexChanged.connect(self.on_insert_mode_changed)
        pos_form.addRow("Modo:", self.insert_mode_combo)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        # ESPECIFICAÇÃO TÉCNICA E IOT
        tech_group = QtGui.QGroupBox("Informações IoT e BIM")
        tech_form = QtGui.QFormLayout()
        
        self.type_combo = QtGui.QComboBox()
        self.type_combo.addItems([
            "Sensor de Presença", "Sensor Porta/Janela", "Módulo Relé", 
            "Smart Switch", "Smart Plug", "Hub/Gateway", "Câmera IP", "Outros"
        ])
        self.type_combo.currentTextChanged.connect(self.sync_values)
        tech_form.addRow("Tipo IoT:", self.type_combo)

        self.protocol_combo = QtGui.QComboBox()
        self.protocol_combo.addItems(["Wi-Fi", "Zigbee", "Matter", "Z-Wave", "Bluetooth", "Cabo (Ethernet)"])
        self.protocol_combo.currentTextChanged.connect(self.sync_values)
        tech_form.addRow("Protocolo:", self.protocol_combo)

        self.power_combo = QtGui.QComboBox()
        self.power_combo.addItems(["Rede Elétrica", "Bateria/Pilha", "PoE (Power over Ethernet)"])
        self.power_combo.currentTextChanged.connect(self.sync_values)
        tech_form.addRow("Alimentação:", self.power_combo)

        self.panel_options = []
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        self.panel_combo.currentIndexChanged.connect(self.on_panel_selected)
        tech_form.addRow("Quadro:", self.panel_combo)

        self.circuit_options = []
        self.circuit_ref_combo = QtGui.QComboBox()
        self.populate_circuits()
        self.circuit_ref_combo.currentIndexChanged.connect(self.on_circuit_selected)
        tech_form.addRow("Circuito:", self.circuit_ref_combo)

        self.space_options = []
        self.space_combo = QtGui.QComboBox()
        self.populate_spaces()
        self.space_combo.currentIndexChanged.connect(self.on_space_selected)
        tech_form.addRow("Ambiente/Setor:", self.space_combo)
        
        tech_group.setLayout(tech_form)
        self.scroll_layout.addWidget(tech_group)

        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(QtGui.QLabel("Dica: clique para inserir | ESPAÇO gira | H altura | N nível | ESC sai"))
        
        self.sync_ui()

    def add_quick_type_controls(self):
        quick_group = QtGui.QGroupBox("Atalhos IoT")
        quick_layout = QtGui.QGridLayout()

        self.btn_sensor = QtGui.QPushButton("Sensor")
        self.btn_rele = QtGui.QPushButton("Módulo Relé")
        self.btn_hub = QtGui.QPushButton("Hub")
        self.btn_wifi = QtGui.QPushButton("Wi-Fi")
        self.btn_zigbee = QtGui.QPushButton("Zigbee")

        for btn in [self.btn_sensor, self.btn_rele, self.btn_hub, self.btn_wifi, self.btn_zigbee]:
            btn.setCheckable(True)
            btn.setMinimumHeight(28)

        self.btn_sensor.clicked.connect(lambda: self.set_quick_type(device_type="Sensor de Presença"))
        self.btn_rele.clicked.connect(lambda: self.set_quick_type(device_type="Módulo Relé"))
        self.btn_hub.clicked.connect(lambda: self.set_quick_type(device_type="Hub/Gateway"))
        self.btn_wifi.clicked.connect(lambda: self.set_quick_type(protocol="Wi-Fi"))
        self.btn_zigbee.clicked.connect(lambda: self.set_quick_type(protocol="Zigbee"))

        quick_layout.addWidget(self.btn_sensor, 0, 0)
        quick_layout.addWidget(self.btn_rele, 0, 1)
        quick_layout.addWidget(self.btn_hub, 0, 2)
        quick_layout.addWidget(self.btn_wifi, 1, 0)
        quick_layout.addWidget(self.btn_zigbee, 1, 1)
        quick_group.setLayout(quick_layout)
        self.scroll_layout.addWidget(quick_group)

    def populate_levels(self):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        levels = discover_project_levels(doc)
        if not levels:
            create_default_bim_levels(doc)
            levels = discover_project_levels(doc)

        self.level_options = levels or [{
            "name": "Projeto",
            "object": "",
            "elevation": 0.0,
            "label": "Projeto / sem nível - 0.00 m"
        }]

        self.level_combo.clear()
        for level in self.level_options:
            self.level_combo.addItem(level["label"])

        self.command.level_options = list(self.level_options)
        self.command.set_reference_level(0)

    def on_level_selected(self, index):
        self.command.set_reference_level(index)
        self.sync_values()

    def populate_panels(self):
        self.panel_options = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.clear()
        self.panel_combo.addItem("Sem quadro")
        for panel in self.panel_options:
            self.panel_combo.addItem(panel["name"])
        self.command.panel_board = self.panel_options[0]["name"] if self.panel_options else ""

    def populate_circuits(self):
        self.circuit_options = discover_circuits(App.ActiveDocument, self.command.panel_board)
        self.circuit_ref_combo.clear()
        self.circuit_ref_combo.addItem("Sem circuito")
        for circuit in self.circuit_options:
            self.circuit_ref_combo.addItem(circuit["name"])
        self.command.circuit_object = self.circuit_options[0]["object"] if self.circuit_options else ""
        self.command.circuit_number = self.circuit_options[0]["number"] if self.circuit_options else "C-01"

    def on_panel_selected(self, index):
        self.command.panel_board = self.panel_options[index - 1]["name"] if index > 0 and index - 1 < len(self.panel_options) else ""
        self.populate_circuits()
        self.sync_values()

    def on_circuit_selected(self, index):
        if index > 0 and index - 1 < len(self.circuit_options):
            circuit = self.circuit_options[index - 1]
            self.command.circuit_object = circuit["object"]
            self.command.circuit_number = circuit["number"]
        else:
            self.command.circuit_object = ""
            self.command.circuit_number = "C-01"
        self.sync_values()

    def populate_spaces(self):
        self.space_options = discover_spaces_or_sectors(App.ActiveDocument)
        self.space_combo.clear()
        self.space_combo.addItem("Sem ambiente/setor")
        for item in self.space_options:
            self.space_combo.addItem(item["name"])

    def on_space_selected(self, index):
        self.command.space_or_sector = self.space_options[index - 1]["name"] if index > 0 and index - 1 < len(self.space_options) else ""
        self.sync_values()

    def populate_families(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        lib_path = os.path.join(base_path, "Library", "3D", "IoT")
        self.family_meta_by_source = {}

        if os.path.exists(lib_path):
            files = sorted([f for f in os.listdir(lib_path) if f.endswith(".FCStd")])
            self.family_list.clear()
            for fname in files:
                item = QtGui.QListWidgetItem(fname.replace(".FCStd", "").replace("_", " "))
                item.setData(QtCore.Qt.UserRole, fname)
                self.family_list.addItem(item)
            if self.family_list.count() > 0:
                selected = self.select_family_file(self.command.family_file, apply=True)
                if not selected:
                    self.family_list.setCurrentRow(0)
                    self.on_family_selected(self.family_list.item(0))
        else:
            print(f"Aviso: Pasta da biblioteca não encontrada em {lib_path}")

    def select_family_file(self, fname, apply=False):
        expected = str(fname or "").replace("\\", "/")
        expected_base = os.path.basename(expected)
        for row in range(self.family_list.count()):
            item = self.family_list.item(row)
            source = str(item.data(QtCore.Qt.UserRole) or "").replace("\\", "/")
            if item and (source == expected or os.path.basename(source) == expected_base):
                self.family_list.blockSignals(True)
                self.family_list.setCurrentRow(row)
                self.family_list.blockSignals(False)
                if apply:
                    self.on_family_selected(item)
                return True
        return False

    def set_quick_type(self, device_type=None, protocol=None):
        if device_type:
            self.command.device_type = device_type
        if protocol:
            self.command.protocol = protocol
        self.sync_ui()
        self.refresh_ghost()

    def sync_quick_buttons(self):
        if not hasattr(self, "btn_sensor"):
            return
        button_states = [
            (self.btn_sensor, "Sensor" in self.command.device_type),
            (self.btn_rele, "Relé" in self.command.device_type),
            (self.btn_hub, "Hub" in self.command.device_type),
            (self.btn_wifi, self.command.protocol == "Wi-Fi"),
            (self.btn_zigbee, self.command.protocol == "Zigbee"),
        ]
        for button, checked in button_states:
            button.blockSignals(True)
            button.setChecked(checked)
            button.blockSignals(False)

    def on_family_selected(self, item):
        if not item:
            return
        name = item.text()
        fname = item.data(QtCore.Qt.UserRole) or (name.replace(" ", "_") + ".FCStd")
        self.command.family_file = fname
        
        if "Sensor" in name: self.command.device_type = "Sensor de Presença"
        elif "Rele" in name or "Relé" in name or "Sonoff" in name: self.command.device_type = "Módulo Relé"
        elif "Hub" in name or "Gateway" in name: self.command.device_type = "Hub/Gateway"
        
        if "Zigbee" in name: self.command.protocol = "Zigbee"
        elif "Matter" in name: self.command.protocol = "Matter"
        
        self.sync_quick_buttons()
        self.refresh_ghost()

    def refresh_ghost(self):
        if not hasattr(self.command, 'engine') or not self.command.engine or not self.command.engine.ghost:
            return
        self.command.engine.ghost.Shape = self.command.make_preview_shape()
        try:
            self.command.engine.ghost.ViewObject.ShapeColor = self.command.preview_color()
            self.command.engine.ghost.ViewObject.LineColor = self.command.preview_color()
        except Exception:
            pass
        Gui.updateGui()

    def sync_height(self):
        txt = self.height_combo.currentText()
        if "Teto" in txt: self.z_in.setValue(2800.0)
        elif "Parede Alta" in txt: self.z_in.setValue(2200.0)
        elif "Parede Média" in txt: self.z_in.setValue(1100.0)
        elif "Piso" in txt or "Rodapé" in txt: self.z_in.setValue(300.0)
        self.sync_values()

    def on_insert_mode_changed(self, index):
        self.command.continuous_insert = index == 0
        self.sync_values()

    def sync_values(self):
        self.command.z_level = self.z_in.value()
        self.command.rotation = self.rot_in.value()
        
        self.command.device_type = self.type_combo.currentText()
        self.command.protocol = self.protocol_combo.currentText()
        self.command.power_source = self.power_combo.currentText()

        self.command.panel_board = self.panel_combo.currentText() if self.panel_combo.currentIndex() > 0 else ""
        self.command.circuit_number = self.circuit_ref_combo.currentText().split(" ", 1)[0] if self.circuit_ref_combo.currentIndex() > 0 else self.command.circuit_number
        self.command.space_or_sector = self.space_combo.currentText() if self.space_combo.currentIndex() > 0 else self.command.space_or_sector
        
        self.refresh_ghost()
        
    def sync_ui(self):
        self.z_in.blockSignals(True)
        self.z_in.setValue(self.command.z_level)
        self.z_in.blockSignals(False)
        
        self.rot_in.blockSignals(True)
        self.rot_in.setValue(self.command.rotation)
        self.rot_in.blockSignals(False)
        
        self.type_combo.blockSignals(True)
        self.type_combo.setCurrentText(self.command.device_type)
        self.type_combo.blockSignals(False)

        self.protocol_combo.blockSignals(True)
        self.protocol_combo.setCurrentText(self.command.protocol)
        self.protocol_combo.blockSignals(False)

        self.power_combo.blockSignals(True)
        self.power_combo.setCurrentText(self.command.power_source)
        self.power_combo.blockSignals(False)

        self.level_combo.blockSignals(True)
        self.level_combo.setCurrentIndex(self.command.reference_level_index)
        self.level_combo.blockSignals(False)

        self.insert_mode_combo.blockSignals(True)
        self.insert_mode_combo.setCurrentIndex(0 if self.command.continuous_insert else 1)
        self.insert_mode_combo.blockSignals(False)

        self.select_family_file(self.command.family_file)
        self.sync_quick_buttons()

    def accept(self):
        Gui.Control.closeDialog()
        return True

class IoTCommand:
    """Comando de Inserção de Dispositivos IoT BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertIoT"
        self.device_type = "Sensor de Presença"
        self.protocol = "Wi-Fi"
        self.power_source = "Bateria/Pilha"
        self.z_level = 2800.0
        self.rotation = 0
        self.circuit_number = "C-01"
        self.panel_board = ""
        self.circuit_object = ""
        self.space_or_sector = ""
        self.continuous_insert = True
        self.symbol_plane_mode = "Plano de simbologia"
        self.symbol_plane_height = 0.0
        self.family_file = "Sensor_Presenca_Teto.FCStd"
        self.level_options = []
        self.reference_level_index = 0
        self.reference_level_name = "Projeto"
        self.reference_level_object = ""
        self.level_elevation = 0.0
        self.detect_surfaces = True
        self.surface_offset = 2.0
        self.host_object = ""
        self.host_sub = ""
        self.engine = None

    def IsActive(self):
        return App.ActiveDocument is not None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_path, "Icons", "Automation.svg")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_path, "Icons", "Generic_Tool.svg")
        return {
            'Pixmap': icon_path, 
            'MenuText': 'Inserir Dispositivo IoT', 
            'ToolTip': 'Catálogo de Dispositivos Smart Home e IoT',
            'Checkable': True
        }

    def Activated(self, *args, **kwargs):
        from GeometryScripts.bim_placement_core import BIMPlacementEngine
        if BIMPlacementEngine.active_engine is not None:
            active_engine = BIMPlacementEngine.active_engine
            active_cmd = active_engine.cmd
            if isinstance(active_cmd, IoTCommand):
                active_engine.stop()
                return

        if not App.ActiveDocument:
            App.newDocument("Projeto_Eletrico")
        self.engine = BIMPlacementEngine(self, IoTTaskPanel, self.place_iot)
        self.engine.start()

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                if isinstance(BIMPlacementEngine.active_engine.cmd, self.__class__):
                    return True
        except Exception:
            pass
        return False

    def make_preview_shape(self):
        try:
            from .iot_bim import make_iot_plan_symbol
            shape = make_iot_plan_symbol(self.device_type, self.protocol)
            if shape:
                shape.translate(App.Vector(0, 0, self.get_symbol_z_offset()))
                return shape
        except Exception:
            pass

        w = 60.0
        h = 60.0
        plate = Part.makeBox(w, h, 20)
        plate.translate(App.Vector(-w/2, -h/2, 0))
        return plate

    def preview_color(self):
        # Cor ciano/azul piscina para automação e IoT
        return (0.0, 0.8, 0.8)

    def set_reference_level(self, index):
        if not self.level_options:
            self.level_options = [{
                "name": "Projeto",
                "object": "",
                "elevation": 0.0,
                "label": "Projeto / sem nível - 0.00 m"
            }]

        index = max(0, min(index, len(self.level_options) - 1))
        level = self.level_options[index]
        self.reference_level_index = index
        self.reference_level_name = level["name"]
        self.reference_level_object = level["object"]
        self.level_elevation = float(level["elevation"])

    def get_final_z(self):
        return float(self.level_elevation) + float(self.z_level)

    def get_symbol_final_z(self):
        return float(self.level_elevation) + float(self.symbol_plane_height)

    def get_symbol_z_offset(self):
        if self.symbol_plane_mode.startswith("Junto"):
            return 1.0
        return self.get_symbol_final_z() - self.get_final_z()

    def matrix_token(self, value):
        text = str(value or "").strip()
        if not text: return "Padrao"
        safe = [ch if ch.isalnum() else "_" for ch in text]
        return "_".join(part for part in "".join(safe).split("_") if part) or "Padrao"

    def matrix_label(self):
        source = self.matrix_token(self.family_file)
        dev_type = self.matrix_token(self.device_type)
        return f"Matriz_IoT_{source}_{dev_type}"

    def mark_as_library_matrix(self, obj):
        if not obj: return
        _set_property(obj, "App::PropertyString", "BIMRole", "BIM_Classificacao", "IoTMatrix")
        _set_property(obj, "App::PropertyBool", "IsLibraryMatrix", "BIM_Classificacao", True)
        _set_property(obj, "App::PropertyString", "MatrixSourceFile", "BIM_Familia", self.family_file)

    def hide_library_matrix(self, obj):
        if not obj or not getattr(obj, "ViewObject", None): return
        try:
            obj.ViewObject.Visibility = False
            obj.ViewObject.Selectable = False
        except Exception: pass
        if hasattr(obj.ViewObject, "ShowInTree"):
            try: obj.ViewObject.ShowInTree = False
            except Exception: pass

    def make_iot_instance_object(self, doc, matriz):
        obj = None
        source_name = f"{getattr(matriz, 'Name', 'Matriz_IoT')}_LinkSource"
        source_obj = doc.getObject(source_name)
        if not source_obj:
            source_obj = doc.addObject("Part::Feature", source_name)
            source_obj.Label = f"{getattr(matriz, 'Label', source_name)} Link Source"
            
            try:
                from .iot_bim import load_iot_family_shape, normalize_iot_shape
                raw = load_iot_family_shape(self.family_file)
                source_shape = normalize_iot_shape(raw)
                if source_shape:
                    source_obj.Shape = source_shape
            except Exception:
                source_obj.Shape = self.make_preview_shape()
                
            self.mark_as_library_matrix(source_obj)
            self.hide_library_matrix(source_obj)

        obj = doc.addObject("App::Link", f"IoT_{self.device_type.replace(' ', '_')[:10]}")
        obj.LinkedObject = source_obj
        try:
            obj.LinkTransform = True
            obj.LinkPlacement = App.Placement()
        except Exception:
            pass
        
        _set_property(obj, "App::PropertyString", "BIMRole", "BIM_Classificacao", "IoTDevice")
        _set_property(obj, "App::PropertyBool", "IsLibraryMatrix", "BIM_Classificacao", False)
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .iot_bim import make_iot_plan_symbol
            sym_shape = make_iot_plan_symbol(self.device_type, self.protocol)
            if not sym_shape: return None

            import re
            safe_level = re.sub(r'[^A-Za-z0-9]', '_', self.reference_level_name or "Projeto").strip("_") or "Projeto"
            PARENT_NAME = "Simbologia_2D_IoT"
            LEVEL_NAME  = f"Sym2D_Nivel_{safe_level}"

            parent = doc.getObject(PARENT_NAME)
            if not parent:
                parent = doc.addObject("App::DocumentObjectGroup", PARENT_NAME)
                parent.Label = "Simbologia 2D — IoT e Automação"

            group = doc.getObject(LEVEL_NAME)
            if not group:
                group = doc.addObject("App::DocumentObjectGroup", LEVEL_NAME)
                group.Label = self.reference_level_name or "Projeto"
                parent.addObject(group)

            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Label = f"↗ {instance_obj.Label}"
            sym_obj.Shape = sym_shape

            px = point.x if hasattr(point, 'x') else point[0]
            py = point.y if hasattr(point, 'y') else point[1]
            sym_obj.Placement = App.Placement(
                App.Vector(px, py + IOT_2D_SYMBOL_Y_OFFSET, self.get_symbol_final_z()),
                App.Rotation(App.Vector(0, 0, 1), self.rotation)
            )

            if getattr(sym_obj, "ViewObject", None):
                color = self.preview_color()
                try:
                    sym_obj.ViewObject.ShapeColor = color
                    sym_obj.ViewObject.LineColor   = color
                except Exception: pass
                sym_obj.ViewObject.LineWidth   = 2.0

            try:
                if not hasattr(instance_obj, "Symbol2DObject"):
                    instance_obj.addProperty("App::PropertyString", "Symbol2DObject", "BIM_Simbologia").Symbol2DObject = sym_obj.Name
                else:
                    instance_obj.Symbol2DObject = sym_obj.Name
            except Exception: pass

            group.addObject(sym_obj)
            return sym_obj
        except Exception:
            return None

    def place_iot(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_IoT")
            obj.Shape = self.make_preview_shape()

            doc.recompute()
            if obj.ViewObject is not None:
                obj.ViewObject.Transparency = 20
                obj.ViewObject.ShapeColor = self.preview_color()
                try: obj.ViewObject.LineColor = self.preview_color()
                except Exception: pass
                obj.ViewObject.LineWidth = 3.0
                obj.ViewObject.Selectable = False
                if hasattr(obj.ViewObject, "ShowInTree"):
                    obj.ViewObject.ShowInTree = False
        else:
            matriz_label = self.matrix_label()
            matriz = None
            for o in doc.Objects:
                if o.Label == matriz_label:
                    matriz = o
                    break

            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                matriz.Label = matriz_label
                from .iot_bim import ProfessionalBIMIoT
                ProfessionalBIMIoT(matriz)
                
                matriz.DeviceType = self.device_type
                matriz.Protocol = self.protocol
                matriz.SourceFile = self.family_file
                self.mark_as_library_matrix(matriz)
                try: doc.recompute([matriz])
                except Exception: pass

            self.hide_library_matrix(matriz)
            obj = self.make_iot_instance_object(doc, matriz)

            def _add_prop(prop_type, name, group, value):
                try:
                    if not hasattr(obj, name): obj.addProperty(prop_type, name, group)
                    setattr(obj, name, value)
                except Exception: pass

            _add_prop("App::PropertyString", "DeviceType", "BIM_IoT", self.device_type)
            _add_prop("App::PropertyString", "Protocol", "BIM_IoT", self.protocol)
            _add_prop("App::PropertyString", "PowerSource", "BIM_IoT", self.power_source)

            _add_prop("App::PropertyString", "CircuitNumber", "BIM_Engenharia", self.circuit_number)
            _add_prop("App::PropertyString", "PanelBoard", "BIM_Engenharia", self.panel_board)
            _add_prop("App::PropertyString", "SpaceOrSector", "BIM_Engenharia", self.space_or_sector)
            
            _add_prop("App::PropertyString", "ReferenceLevel", "BIM_Posicionamento", self.reference_level_name)
            _add_prop("App::PropertyLength", "MountingHeight", "BIM_Posicionamento", self.z_level)
            _add_prop("App::PropertyLength", "FinalElevation", "BIM_Posicionamento", self.get_final_z())
            
            _add_prop("App::PropertyString", "TipoBIM", "BIM_Classificacao", "IoT")

            prefix_tag = "IOT"
            if "Sensor" in self.device_type: prefix_tag = "SEN"
            if "Hub" in self.device_type: prefix_tag = "HUB"
            _add_prop("App::PropertyString", "Tag", "BIM_Classificacao", f"{prefix_tag}-{self.protocol[:2].upper()}")
            
            color = self.preview_color()
            try: obj.ViewObject.ShapeColor = color
            except Exception: pass
            
            count = len([o for o in doc.Objects if "IoT" in o.Label or "Sensor" in o.Label]) + 1
            short_type = self.device_type.split(" ")[0]
            obj.Label = f"IoT {short_type} {self.protocol} {count:02d}"

        final_z = self.get_final_z()
        px = point.x if hasattr(point, 'x') else point[0]
        py = point.y if hasattr(point, 'y') else point[1]
        target_pos = App.Vector(px, py, final_z)
        if self.detect_surfaces and self.host_object:
            target_pos.z = final_z + self.surface_offset
            
        rotation_offset = IOT_3D_LINK_ROTATION_OFFSET_DEG if not is_ghost else 0.0
        target_rot = App.Rotation(App.Vector(0,0,1), self.rotation + rotation_offset)
        
        if is_ghost:
            obj.Placement = App.Placement(target_pos, target_rot)
        else:
            try:
                obj.Placement = App.Placement(target_pos, target_rot)
                doc.recompute([obj])
                
                if hasattr(self, "reference_level_object") and self.reference_level_object:
                    candidate_level = doc.getObject(self.reference_level_object)
                    if candidate_level and hasattr(candidate_level, "addObject"):
                        try:
                            candidate_level.addObject(obj)
                            if hasattr(candidate_level, "Placement"):
                                local_pos = candidate_level.Placement.inverse().multVec(target_pos)
                                obj.Placement = App.Placement(local_pos, target_rot)
                        except Exception: pass
            except Exception as e:
                App.Console.PrintError(f"Erro ao posicionar IoT: {e}\n")
                
            self._create_2d_symbol(doc, obj, point)
            doc.recompute()
            
        return obj

try:
    if hasattr(Gui, "listCommands") and 'Eletrica_InsertIoT' in Gui.listCommands() and hasattr(Gui, "removeCommand"):
        Gui.removeCommand('Eletrica_InsertIoT')
except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertIoT', IoTCommand())
