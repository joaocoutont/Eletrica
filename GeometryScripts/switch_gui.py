import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import math
try:
    import Arch
    _ARCH_AVAILABLE = True
except ImportError:
    _ARCH_AVAILABLE = False
import Part
from .switch_bim import ProfessionalBIMSwitch
from .bim_placement_core import BIMPlacementEngine

# Importa as rotinas auxiliares já existentes do socket_gui para não duplicar código base
from .socket_gui import (
    discover_project_levels, create_default_bim_levels, discover_panel_boards,
    discover_circuits, discover_spaces_or_sectors, LEVEL_KEYWORDS, DEFAULT_BIM_LEVELS,
    _is_level_object, _level_elevation, _plain_value, _set_property, _object_text
)

SYMBOL_PLANE_MODES = ["Plano de simbologia", "Junto do interruptor"]
SWITCH_3D_LINK_ROTATION_OFFSET_DEG = 180.0
SWITCH_2D_SYMBOL_Y_OFFSET = 18.0

class SwitchTaskPanel:
    """Interface de Famílias de Interruptores (Estilo Revit)"""
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
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Famílias e Tipos de Interruptores:</b>"))
        self.family_list = QtGui.QListWidget()
        self.family_list.setMinimumHeight(150)
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
        self.height_combo.addItems(["Baixa (300mm)", "Média (1100mm)", "Alta (2200mm)"])
        self.height_combo.currentTextChanged.connect(self.sync_height)
        pos_form.addRow("Altura Padrão:", self.height_combo)
        
        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(-5000, 10000); self.z_in.setValue(1100)
        self.z_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Altura Inst. (mm):", self.z_in)

        self.final_z_label = QtGui.QLabel("Z final: 1100 mm")
        pos_form.addRow("Resultado:", self.final_z_label)

        self.rot_in = QtGui.QSpinBox(); self.rot_in.setRange(0, 360); self.rot_in.setSingleStep(90)
        self.rot_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Rotação (°):", self.rot_in)

        self.insert_mode_combo = QtGui.QComboBox()
        self.insert_mode_combo.addItems(["Contínuo", "Uma vez"])
        self.insert_mode_combo.currentIndexChanged.connect(self.on_insert_mode_changed)
        pos_form.addRow("Modo:", self.insert_mode_combo)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        symbol_group = QtGui.QGroupBox("Simbologia 2D / plotagem")
        symbol_form = QtGui.QFormLayout()

        self.symbol_mode_combo = QtGui.QComboBox()
        self.symbol_mode_combo.addItems(SYMBOL_PLANE_MODES)
        self.symbol_mode_combo.currentTextChanged.connect(self.sync_values)
        symbol_form.addRow("Plano:", self.symbol_mode_combo)

        self.symbol_name_in = QtGui.QLineEdit(self.command.symbol_plane_name)
        self.symbol_name_in.textChanged.connect(self.sync_values)
        symbol_form.addRow("Nome:", self.symbol_name_in)

        self.symbol_height_in = QtGui.QDoubleSpinBox()
        self.symbol_height_in.setRange(0, 50000)
        self.symbol_height_in.setSingleStep(100)
        self.symbol_height_in.setSuffix(" mm")
        self.symbol_height_in.setValue(self.command.symbol_plane_height)
        self.symbol_height_in.valueChanged.connect(self.sync_values)
        symbol_form.addRow("Altura do plano:", self.symbol_height_in)

        self.symbol_final_z_label = QtGui.QLabel("Z simbologia: 0 mm")
        symbol_form.addRow("Resultado:", self.symbol_final_z_label)

        symbol_group.setLayout(symbol_form)
        self.scroll_layout.addWidget(symbol_group)

        # ESPECIFICAÇÃO TÉCNICA
        tech_group = QtGui.QGroupBox("Informações BIM")
        tech_form = QtGui.QFormLayout()
        
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

        self.circuit_combo = QtGui.QComboBox()
        self.circuit_combo.addItems(["Iluminação", "Automação"])
        self.circuit_combo.currentTextChanged.connect(self.sync_values)
        tech_form.addRow("Tipo de Uso:", self.circuit_combo)

        self.space_options = []
        self.space_combo = QtGui.QComboBox()
        self.populate_spaces()
        self.space_combo.currentIndexChanged.connect(self.on_space_selected)
        tech_form.addRow("Ambiente/Setor:", self.space_combo)
        
        tech_group.setLayout(tech_form)
        self.scroll_layout.addWidget(tech_group)

        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(QtGui.QLabel("Dica: clique para inserir | ESPAÇO gira | H altura | N nível | I modo | ESC sai"))
        
        self.sync_ui()

    def add_quick_type_controls(self):
        quick_group = QtGui.QGroupBox("Configuração Rápida")
        quick_layout = QtGui.QGridLayout()

        self.quick_1t_btn = QtGui.QPushButton("1 Tecla")
        self.quick_2t_btn = QtGui.QPushButton("2 Teclas")
        self.quick_3t_btn = QtGui.QPushButton("3 Teclas")
        self.quick_simples_btn = QtGui.QPushButton("Simples")
        self.quick_paralelo_btn = QtGui.QPushButton("Paralelo")
        self.quick_interm_btn = QtGui.QPushButton("Intermediário")

        for btn in [self.quick_1t_btn, self.quick_2t_btn, self.quick_3t_btn, self.quick_simples_btn, self.quick_paralelo_btn, self.quick_interm_btn]:
            btn.setCheckable(True)
            btn.setMinimumHeight(28)

        self.quick_1t_btn.clicked.connect(lambda: self.set_quick_type(keys="1 Tecla"))
        self.quick_2t_btn.clicked.connect(lambda: self.set_quick_type(keys="2 Teclas"))
        self.quick_3t_btn.clicked.connect(lambda: self.set_quick_type(keys="3 Teclas"))
        self.quick_simples_btn.clicked.connect(lambda: self.set_quick_type(switch_type="Simples"))
        self.quick_paralelo_btn.clicked.connect(lambda: self.set_quick_type(switch_type="Paralelo"))
        self.quick_interm_btn.clicked.connect(lambda: self.set_quick_type(switch_type="Intermediário"))

        quick_layout.addWidget(self.quick_1t_btn, 0, 0)
        quick_layout.addWidget(self.quick_2t_btn, 0, 1)
        quick_layout.addWidget(self.quick_3t_btn, 0, 2)
        quick_layout.addWidget(self.quick_simples_btn, 1, 0)
        quick_layout.addWidget(self.quick_paralelo_btn, 1, 1)
        quick_layout.addWidget(self.quick_interm_btn, 1, 2)
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
        lib_path = os.path.join(base_path, "Library", "3D", "Interruptores")
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

    def set_quick_type(self, keys=None, switch_type=None):
        if keys:
            self.command.keys = keys
        if switch_type:
            self.command.switch_type = switch_type
        if hasattr(self.command, "update_family_file_from_type"):
            self.command.update_family_file_from_type()
        self.sync_ui()
        self.refresh_ghost()

    def sync_quick_buttons(self):
        if not hasattr(self, "quick_1t_btn"):
            return
        button_states = [
            (self.quick_1t_btn, self.command.keys.startswith("1")),
            (self.quick_2t_btn, self.command.keys.startswith("2")),
            (self.quick_3t_btn, self.command.keys.startswith("3")),
            (self.quick_simples_btn, self.command.switch_type == "Simples"),
            (self.quick_paralelo_btn, self.command.switch_type == "Paralelo"),
            (self.quick_interm_btn, self.command.switch_type == "Intermediário"),
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
        
        # Mapeamento do nome para propriedades
        if "2 Teclas" in name or "Duplo" in name: self.command.keys = "2 Teclas"
        elif "3 Teclas" in name or "Triplo" in name: self.command.keys = "3 Teclas"
        else: self.command.keys = "1 Tecla"
        
        if "Paralelo" in name: self.command.switch_type = "Paralelo"
        elif "Intermediario" in name or "Intermediário" in name: self.command.switch_type = "Intermediário"
        else: self.command.switch_type = "Simples"
        
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
        if "Baixa" in txt: self.z_in.setValue(300.0)
        elif "Média" in txt: self.z_in.setValue(1100.0)
        elif "Alta" in txt: self.z_in.setValue(2200.0)
        self.sync_values()

    def on_insert_mode_changed(self, index):
        self.command.continuous_insert = index == 0
        self.sync_values()

    def sync_values(self):
        self.command.z_level = self.z_in.value()
        self.command.rotation = self.rot_in.value()
        self.command.circuit_type = self.circuit_combo.currentText()
        self.command.height_type = self.height_combo.currentText()
        self.command.panel_board = self.panel_combo.currentText() if self.panel_combo.currentIndex() > 0 else ""
        self.command.circuit_number = self.circuit_ref_combo.currentText().split(" ", 1)[0] if self.circuit_ref_combo.currentIndex() > 0 else self.command.circuit_number
        self.command.space_or_sector = self.space_combo.currentText() if self.space_combo.currentIndex() > 0 else self.command.space_or_sector
        
        if hasattr(self, "symbol_mode_combo"):
            self.command.symbol_plane_mode = self.symbol_mode_combo.currentText()
            self.command.symbol_plane_name = self.symbol_name_in.text() or "Plano de Simbologia"
            self.command.symbol_plane_height = self.symbol_height_in.value()
            symbol_enabled = not self.command.symbol_plane_mode.startswith("Junto")
            self.symbol_name_in.setEnabled(symbol_enabled)
            self.symbol_height_in.setEnabled(symbol_enabled)
            self.symbol_final_z_label.setText(f"Z simbologia: {self.command.get_symbol_final_z():.0f} mm")
        self.final_z_label.setText(f"Z final: {self.command.get_final_z():.0f} mm")
        self.refresh_ghost()
        
    def sync_ui(self):
        self.z_in.blockSignals(True)
        self.z_in.setValue(self.command.z_level)
        self.z_in.blockSignals(False)
        
        self.rot_in.blockSignals(True)
        self.rot_in.setValue(self.command.rotation)
        self.rot_in.blockSignals(False)
        
        self.circuit_combo.blockSignals(True)
        self.circuit_combo.setCurrentText(self.command.circuit_type)
        self.circuit_combo.blockSignals(False)

        self.height_combo.blockSignals(True)
        self.height_combo.setCurrentText(self.command.normalized_height_type())
        self.height_combo.blockSignals(False)

        self.level_combo.blockSignals(True)
        self.level_combo.setCurrentIndex(self.command.reference_level_index)
        self.level_combo.blockSignals(False)

        self.insert_mode_combo.blockSignals(True)
        self.insert_mode_combo.setCurrentIndex(0 if self.command.continuous_insert else 1)
        self.insert_mode_combo.blockSignals(False)

        if hasattr(self, "symbol_mode_combo"):
            self.symbol_mode_combo.blockSignals(True)
            self.symbol_mode_combo.setCurrentText(self.command.symbol_plane_mode)
            self.symbol_mode_combo.blockSignals(False)

            self.symbol_name_in.blockSignals(True)
            self.symbol_name_in.setText(self.command.symbol_plane_name)
            self.symbol_name_in.blockSignals(False)

            self.symbol_height_in.blockSignals(True)
            self.symbol_height_in.setValue(self.command.symbol_plane_height)
            self.symbol_height_in.blockSignals(False)
            
            self.symbol_final_z_label.setText(f"Z simbologia: {self.command.get_symbol_final_z():.0f} mm")

        self.select_family_file(self.command.family_file)
        self.sync_quick_buttons()
        self.final_z_label.setText(f"Z final: {self.command.get_final_z():.0f} mm")

    def accept(self):
        Gui.Control.closeDialog()
        return True

class SwitchCommand:
    """Comando de Inserção de Interruptores BIM (Estilo Revit)"""
    def __init__(self):
        self.command_name = "Eletrica_InsertSwitch"
        self.keys = "1 Tecla"
        self.switch_type = "Simples"
        self.z_level = 1100.0
        self.rotation = 0
        self.circuit_type = "Iluminação"
        self.circuit_number = "C-01"
        self.panel_board = ""
        self.circuit_object = ""
        self.space_or_sector = ""
        self.continuous_insert = True
        self.symbol_plane_mode = "Plano de simbologia"
        self.symbol_plane_name = "Plano de Simbologia"
        self.symbol_plane_height = 0.0
        self.height_type = "Média (1100mm)"
        self.family_file = "Interruptor_Simples_1_Tecla.FCStd"
        self.family_name = "Interruptor"
        self.family_category = "Interruptor"
        self.ifc_class = "IfcSwitchingDevice"
        self.electrical_standard = "NBR 5410"
        self.level_options = []
        self.reference_level_index = 0
        self.reference_level_name = "Projeto"
        self.reference_level_object = ""
        self.level_elevation = 0.0
        self.detect_surfaces = True
        self.surface_offset = 5.0
        self.host_object = ""
        self.host_sub = ""
        self.engine = None

    def IsActive(self):
        return App.ActiveDocument is not None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        # Usaremos Generic_Tool ou um Switch se existir
        icon_path = os.path.join(base_path, "Icons", "Interruptor_BR.svg")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_path, "Icons", "Generic_Tool.svg")
        return {
            'Pixmap': icon_path, 
            'MenuText': 'Inserir Interruptor BIM', 
            'ToolTip': 'Catálogo de Famílias de Interruptores NBR',
            'Checkable': True
        }

    def Activated(self, *args, **kwargs):
        from GeometryScripts.bim_placement_core import BIMPlacementEngine
        if BIMPlacementEngine.active_engine is not None:
            active_engine = BIMPlacementEngine.active_engine
            active_cmd = active_engine.cmd
            if isinstance(active_cmd, SwitchCommand):
                active_engine.stop()
                return

        if not App.ActiveDocument:
            App.newDocument("Projeto_Eletrico")
        self.engine = BIMPlacementEngine(self, SwitchTaskPanel, self.place_switch)
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
            from .switch_bim import make_switch_plan_symbol
            shape = make_switch_plan_symbol(self.keys, self.switch_type)
            if shape:
                shape.translate(App.Vector(0, 0, self.get_symbol_z_offset()))
                return shape
        except Exception:
            pass

        w = 80.0
        h = 120.0
        plate = Part.makeBox(w, h, 2)
        plate.translate(App.Vector(-w/2, -h/2, 0))
        return plate

    def preview_color(self):
        if "Automação" in self.circuit_type:
            return (0.0, 0.75, 1.0)
        return (1.0, 0.5, 0.0) # Laranja para interruptores

    def family_filename_for_type(self):
        prefix = "Interruptor"
        tipo = "Simples"
        if "Paralelo" in self.switch_type: tipo = "Paralelo"
        if "Intermediário" in self.switch_type: tipo = "Intermediario"
        
        teclas = "1_Tecla"
        if "2" in self.keys: teclas = "2_Teclas"
        if "3" in self.keys: teclas = "3_Teclas"
        
        return f"{prefix}_{tipo}_{teclas}.FCStd"

    def update_family_file_from_type(self):
        fname = self.family_filename_for_type()
        self.family_file = fname
        return self.family_file

    def normalized_height_type(self):
        if self.z_level <= 700:
            return "Baixa (300mm)"
        if self.z_level <= 1600:
            return "Média (1100mm)"
        return "Alta (2200mm)"

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
        if self.symbol_plane_mode.startswith("Junto"):
            return self.get_final_z() + 1.0
        return float(self.level_elevation) + float(self.symbol_plane_height)

    def get_symbol_z_offset(self):
        if self.symbol_plane_mode.startswith("Junto"):
            return 1.0
        return self.get_symbol_final_z() - self.get_final_z()

    def matrix_token(self, value):
        text = str(value or "").strip()
        if not text:
            return "Padrao"
        safe = []
        for ch in text:
            safe.append(ch if ch.isalnum() else "_")
        return "_".join(part for part in "".join(safe).split("_") if part) or "Padrao"

    def matrix_label(self):
        source = self.matrix_token(self.family_file)
        keys = self.matrix_token(self.keys)
        switch_type = self.matrix_token(self.switch_type)
        height = self.matrix_token(self.normalized_height_type())
        symbol = self.matrix_token(f"{self.symbol_plane_mode}_{self.get_symbol_z_offset():.0f}")
        return f"Matriz_Interruptor_{source}_{keys}_{switch_type}_{height}_{symbol}"

    def mark_as_library_matrix(self, obj):
        if not obj:
            return
        _set_property(obj, "App::PropertyString", "BIMRole", "BIM_Classificacao", "SwitchMatrix")
        _set_property(obj, "App::PropertyBool", "IsLibraryMatrix", "BIM_Classificacao", True)
        _set_property(obj, "App::PropertyString", "MatrixSourceFile", "BIM_Familia", self.family_file)

    def hide_library_matrix(self, obj):
        if not obj or not getattr(obj, "ViewObject", None):
            return
        try:
            obj.ViewObject.Visibility = False
            obj.ViewObject.Selectable = False
        except Exception:
            pass
        if hasattr(obj.ViewObject, "ShowInTree"):
            try:
                obj.ViewObject.ShowInTree = False
            except Exception:
                pass

    def make_switch_instance_object(self, doc, matriz):
        obj = None
        source_name = f"{getattr(matriz, 'Name', 'Matriz_Interruptor')}_LinkSource"
        source_obj = doc.getObject(source_name)
        if not source_obj:
            source_obj = doc.addObject("Part::Feature", source_name)
            source_obj.Label = f"{getattr(matriz, 'Label', source_name)} Link Source"
            
            # Carrega a shape
            try:
                from .switch_bim import load_switch_family_shape, normalize_switch_shape
                raw = load_switch_family_shape(self.family_file)
                source_shape = normalize_switch_shape(raw)
                if source_shape:
                    source_obj.Shape = source_shape
            except Exception:
                source_obj.Shape = self.make_preview_shape()
                
            self.mark_as_library_matrix(source_obj)
            self.hide_library_matrix(source_obj)

        obj = doc.addObject("App::Link", f"Interruptor_{self.keys.replace(' ', '_')}")
        obj.LinkedObject = source_obj
        try:
            obj.LinkTransform = True
            obj.LinkPlacement = App.Placement()
        except Exception:
            pass
        
        _set_property(obj, "App::PropertyString", "BIMRole", "BIM_Classificacao", "Switch")
        _set_property(obj, "App::PropertyBool", "IsLibraryMatrix", "BIM_Classificacao", False)
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .switch_bim import make_switch_plan_symbol
            sym_shape = make_switch_plan_symbol(self.keys, self.switch_type)
            if not sym_shape:
                return None

            import re
            safe_level = re.sub(r'[^A-Za-z0-9]', '_', self.reference_level_name or "Projeto").strip("_") or "Projeto"
            PARENT_NAME = "Simbologia_2D_Interruptores"
            LEVEL_NAME  = f"Sym2D_Nivel_{safe_level}"

            parent = doc.getObject(PARENT_NAME)
            if not parent:
                parent = doc.addObject("App::DocumentObjectGroup", PARENT_NAME)
                parent.Label = "Simbologia 2D — Interruptores"

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
                App.Vector(px, py + SWITCH_2D_SYMBOL_Y_OFFSET, self.get_symbol_final_z()),
                App.Rotation(App.Vector(0, 0, 1), self.rotation)
            )

            if getattr(sym_obj, "ViewObject", None):
                color = self.preview_color()
                try:
                    sym_obj.ViewObject.ShapeColor = color
                    sym_obj.ViewObject.LineColor   = color
                except Exception:
                    pass
                sym_obj.ViewObject.LineWidth   = 2.0

            try:
                if not hasattr(instance_obj, "Symbol2DObject"):
                    instance_obj.addProperty("App::PropertyString", "Symbol2DObject", "BIM_Simbologia").Symbol2DObject = sym_obj.Name
                else:
                    instance_obj.Symbol2DObject = sym_obj.Name
            except Exception:
                pass

            group.addObject(sym_obj)
            return sym_obj
        except Exception:
            return None

    def place_switch(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_Switch")
            obj.Shape = self.make_preview_shape()

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
            matriz_label = self.matrix_label()
            matriz = None
            for o in doc.Objects:
                if o.Label == matriz_label:
                    matriz = o
                    break

            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                matriz.Label = matriz_label
                from .switch_bim import ProfessionalBIMSwitch
                ProfessionalBIMSwitch(matriz)
                
                matriz.Keys = self.keys
                matriz.SwitchType = self.switch_type
                matriz.SourceFile = self.family_file
                self.mark_as_library_matrix(matriz)
                try:
                    doc.recompute([matriz])
                except Exception:
                    pass

            self.hide_library_matrix(matriz)
            obj = self.make_switch_instance_object(doc, matriz)

            def _add_prop(prop_type, name, group, value):
                try:
                    if not hasattr(obj, name):
                        obj.addProperty(prop_type, name, group)
                    setattr(obj, name, value)
                except Exception:
                    pass

            _add_prop("App::PropertyString", "CircuitNumber", "BIM_Engenharia", self.circuit_number)
            _add_prop("App::PropertyString", "CircuitObject", "BIM_Engenharia", self.circuit_object)
            _add_prop("App::PropertyString", "PanelBoard", "BIM_Engenharia", self.panel_board)
            _add_prop("App::PropertyString", "SpaceOrSector", "BIM_Engenharia", self.space_or_sector)
            
            _add_prop("App::PropertyString", "ReferenceLevel", "BIM_Posicionamento", self.reference_level_name)
            _add_prop("App::PropertyLength", "MountingHeight", "BIM_Posicionamento", self.z_level)
            _add_prop("App::PropertyLength", "FinalElevation", "BIM_Posicionamento", self.get_final_z())
            
            _add_prop("App::PropertyString", "SymbolPlaneMode", "BIM_Simbologia", self.symbol_plane_mode)
            _add_prop("App::PropertyLength", "SymbolFinalElevation", "BIM_Simbologia", self.get_symbol_final_z())
            
            _add_prop("App::PropertyString", "IFC_Class", "BIM_Classificacao", self.ifc_class)
            _add_prop("App::PropertyString", "TipoBIM", "BIM_Classificacao", "Interruptor")

            prefix_tag = "INT"
            if "Paralelo" in self.switch_type: prefix_tag = "3W"
            if "Intermediário" in self.switch_type: prefix_tag = "4W"
            _add_prop("App::PropertyString", "Tag", "BIM_Classificacao", f"{prefix_tag}-{self.keys[0]}")
            
            color = self.preview_color()
            try:
                obj.ViewObject.ShapeColor = color
            except Exception:
                pass
            
            count = len([o for o in doc.Objects if "Interruptor" in o.Label]) + 1
            obj.Label = f"Interruptor {self.switch_type} {self.keys} {count:02d}"

        final_z = self.get_final_z()
        px = point.x if hasattr(point, 'x') else point[0]
        py = point.y if hasattr(point, 'y') else point[1]
        target_pos = App.Vector(px, py, final_z)
        if self.detect_surfaces and self.host_object:
            target_pos.z = final_z + self.surface_offset
            
        rotation_offset = SWITCH_3D_LINK_ROTATION_OFFSET_DEG if not is_ghost else 0.0
        target_rot = App.Rotation(App.Vector(0,0,1), self.rotation + rotation_offset)
        
        if is_ghost:
            obj.Placement = App.Placement(target_pos, target_rot)
        else:
            # Lógica simplificada de posicionamento para o Link
            try:
                obj.Placement = App.Placement(target_pos, target_rot)
                doc.recompute([obj])
                
                # Opcional: Adicionar a um container de nível, se selecionado e disponível
                if hasattr(self, "reference_level_object") and self.reference_level_object:
                    candidate_level = doc.getObject(self.reference_level_object)
                    if candidate_level and hasattr(candidate_level, "addObject"):
                        try:
                            candidate_level.addObject(obj)
                            # Ajustar posicionamento global se estiver dentro de um container
                            if hasattr(candidate_level, "Placement"):
                                local_pos = candidate_level.Placement.inverse().multVec(target_pos)
                                obj.Placement = App.Placement(local_pos, target_rot)
                        except Exception:
                            pass
            except Exception as e:
                App.Console.PrintError(f"Erro ao posicionar interruptor: {e}\n")
                
            self._create_2d_symbol(doc, obj, point)
            doc.recompute()
            
        return obj

try:
    if hasattr(Gui, "listCommands") and 'Eletrica_InsertSwitch' in Gui.listCommands() and hasattr(Gui, "removeCommand"):
        Gui.removeCommand('Eletrica_InsertSwitch')
except Exception:
    pass
if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertSwitch', SwitchCommand())
