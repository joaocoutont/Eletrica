import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import math
import Arch
import Part
from .socket_bim import ProfessionalBIMSocket
from .bim_placement_core import BIMPlacementEngine

LEVEL_KEYWORDS = ["level", "nivel", "nível", "pavimento", "storey", "story", "floor", "andar", "térreo", "terreo"]
DEFAULT_BIM_LEVELS = [
    ("Nivel Terreo", 0.0),
    ("Nivel 01", 3000.0),
    ("Nivel 02", 6000.0),
]

def _plain_value(value):
    return value.Value if hasattr(value, "Value") else value

def _set_property(obj, prop_type, name, group, value):
    try:
        if not hasattr(obj, name):
            obj.addProperty(prop_type, name, group)
        setattr(obj, name, value)
    except Exception:
        pass

def _object_text(obj):
    parts = [getattr(obj, "Name", ""), getattr(obj, "Label", ""), getattr(obj, "TypeId", "")]
    for prop in ["IfcType", "PredefinedType", "Role"]:
        if hasattr(obj, prop):
            try:
                parts.append(str(getattr(obj, prop)))
            except Exception:
                pass
    return " ".join(parts).lower()

def _is_level_object(obj):
    text = _object_text(obj)
    if any(word in text for word in LEVEL_KEYWORDS):
        return True
    if "buildingpart" in text or "ifcbuildingstorey" in text:
        return True
    return False

def _level_elevation(obj):
    for prop in ["Elevation", "Level", "IfcElevation"]:
        if hasattr(obj, prop):
            try:
                return float(_plain_value(getattr(obj, prop)))
            except Exception:
                pass
    try:
        return float(obj.Placement.Base.z)
    except Exception:
        return 0.0

def discover_project_levels(doc):
    levels = []
    if not doc:
        return levels

    seen = set()
    for obj in doc.Objects:
        if not _is_level_object(obj) or obj.Name in seen:
            continue
        seen.add(obj.Name)
        label = getattr(obj, "Label", obj.Name)
        elevation = _level_elevation(obj)
        levels.append({
            "name": label,
            "object": obj.Name,
            "elevation": elevation,
            "label": f"{label} - {elevation / 1000.0:.2f} m"
        })

    levels.sort(key=lambda item: (item["elevation"], item["name"]))
    return levels

def create_default_bim_levels(doc):
    """Cria níveis BIM padrão quando o projeto ainda não tem pavimentos."""
    created = []
    if not doc:
        return created

    for label, elevation in DEFAULT_BIM_LEVELS:
        try:
            obj = Arch.makeBuildingPart()
        except Exception:
            App.Console.PrintWarning("Nao foi possivel criar BuildingPart BIM para niveis padrao.\n")
            return created

        obj.Label = label
        try:
            obj.Placement.Base.z = elevation
        except Exception:
            pass

        try:
            if hasattr(obj, "IfcType"):
                obj.IfcType = "Building Storey"
        except Exception:
            pass

        try:
            if not hasattr(obj, "Elevation"):
                obj.addProperty("App::PropertyLength", "Elevation", "BIM_Nivel")
            obj.Elevation = elevation
        except Exception:
            pass

        created.append(obj)

    doc.recompute()
    return created

def discover_panel_boards(doc):
    if not doc:
        return []
    panels = []
    for obj in doc.Objects:
        if getattr(obj, "BIMRole", "") == "PanelBoard":
            panels.append({"name": obj.Label, "object": obj.Name})
    panels.sort(key=lambda item: item["name"])
    return panels

def discover_circuits(doc, panel_name=""):
    if not doc:
        return []
    circuits = []
    for obj in doc.Objects:
        if getattr(obj, "BIMRole", "") != "Circuit":
            continue
        if panel_name and getattr(obj, "PanelBoard", "") not in ["", panel_name]:
            continue
        circuits.append({
            "name": obj.Label,
            "object": obj.Name,
            "number": getattr(obj, "CircuitNumber", obj.Label),
            "voltage": getattr(obj, "Voltage", ""),
        })
    circuits.sort(key=lambda item: item["name"])
    return circuits

def discover_spaces_or_sectors(doc):
    if not doc:
        return []
    result = []
    keywords = ["Espaco", "Ambiente", "Setor", "Zona", "Area", "Patio", "Rede", "Alimentador"]
    for obj in doc.Objects:
        label = getattr(obj, "Label", "")
        role = getattr(obj, "BIMRole", "")
        if role == "IfcSpace" or any(k.lower() in label.lower() for k in keywords):
            result.append({"name": label, "object": obj.Name})
    result.sort(key=lambda item: item["name"])
    return result

class SocketTaskPanel:
    """Interface de Famílias de Tomadas (Estilo Revit)"""
    def __init__(self, command_obj):
        self.command = command_obj
        self.form = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(self.form)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # --- SCROLL AREA (Para telas menores e escalonamento de tela no Windows) ---
        self.scroll = QtGui.QScrollArea(self.form)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtGui.QFrame.NoFrame)
        self.layout.addWidget(self.scroll)
        
        self.scroll_content = QtGui.QWidget()
        self.scroll_layout = QtGui.QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        
        self.family_meta_by_source = {}
        
        # --- CATÁLOGO DE FAMÍLIAS (LISTA) ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Famílias e Tipos de Tomadas:</b>"))
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
        self.height_combo.addItems(["Baixa (300mm)", "Média (1100mm)", "Alta (2200mm)", "Especial"])
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
        self.circuit_combo.addItems(["TUG (Geral)", "TUE (Específico)", "UPS (Emergência)"])
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
        self.scroll_layout.addWidget(QtGui.QLabel("Dica: clique para inserir | ESPAÇO gira | H altura | N nível | A amperagem | M módulo | I modo | ESC sai"))
        
        # Sincronização Inicial
        self.sync_ui()

    def add_quick_type_controls(self):
        quick_group = QtGui.QGroupBox("Tipo rápido")
        quick_layout = QtGui.QGridLayout()

        self.quick_1m_btn = QtGui.QPushButton("1M")
        self.quick_2m_btn = QtGui.QPushButton("2M")
        self.quick_10a_btn = QtGui.QPushButton("10A")
        self.quick_20a_btn = QtGui.QPushButton("20A")

        for btn in [self.quick_1m_btn, self.quick_2m_btn, self.quick_10a_btn, self.quick_20a_btn]:
            btn.setCheckable(True)
            btn.setMinimumHeight(28)

        self.quick_1m_btn.clicked.connect(lambda: self.set_quick_type(modules="1 Módulo"))
        self.quick_2m_btn.clicked.connect(lambda: self.set_quick_type(modules="2 Módulos"))
        self.quick_10a_btn.clicked.connect(lambda: self.set_quick_type(amperage="10A"))
        self.quick_20a_btn.clicked.connect(lambda: self.set_quick_type(amperage="20A"))

        quick_layout.addWidget(self.quick_1m_btn, 0, 0)
        quick_layout.addWidget(self.quick_2m_btn, 0, 1)
        quick_layout.addWidget(self.quick_10a_btn, 1, 0)
        quick_layout.addWidget(self.quick_20a_btn, 1, 1)
        quick_group.setLayout(quick_layout)
        self.scroll_layout.addWidget(quick_group)

    def populate_levels(self):
        """Preenche o combo com níveis FreeCAD/IFC encontrados no documento."""
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
        last_panel = self.command.params.GetString("LastPanelBoard", "")
        if last_panel:
            idx = self.panel_combo.findText(last_panel)
            if idx >= 0:
                self.panel_combo.setCurrentIndex(idx)
                self.command.panel_board = last_panel

    def populate_circuits(self):
        self.circuit_options = discover_circuits(App.ActiveDocument, self.command.panel_board)
        self.circuit_ref_combo.clear()
        self.circuit_ref_combo.addItem("Sem circuito")
        for circuit in self.circuit_options:
            self.circuit_ref_combo.addItem(circuit["name"])
        self.command.circuit_object = self.circuit_options[0]["object"] if self.circuit_options else ""
        self.command.circuit_number = self.circuit_options[0]["number"] if self.circuit_options else "C-01"
        last_circuit = self.command.params.GetString("LastCircuit", "")
        if last_circuit:
            idx = self.circuit_ref_combo.findText(last_circuit)
            if idx >= 0:
                self.circuit_ref_combo.setCurrentIndex(idx)
                self.on_circuit_selected(idx)

    def on_panel_selected(self, index):
        self.command.panel_board = self.panel_options[index - 1]["name"] if index > 0 and index - 1 < len(self.panel_options) else ""
        self.command.params.SetString("LastPanelBoard", self.command.panel_board)
        self.populate_circuits()
        self.sync_values()

    def on_circuit_selected(self, index):
        if index > 0 and index - 1 < len(self.circuit_options):
            circuit = self.circuit_options[index - 1]
            self.command.circuit_object = circuit["object"]
            self.command.circuit_number = circuit["number"]
            self.command.params.SetString("LastCircuit", circuit["name"])
        else:
            self.command.circuit_object = ""
            self.command.circuit_number = "C-01"
            self.command.params.SetString("LastCircuit", "")
        self.sync_values()

    def populate_spaces(self):
        self.space_options = discover_spaces_or_sectors(App.ActiveDocument)
        self.space_combo.clear()
        self.space_combo.addItem("Sem ambiente/setor")
        for item in self.space_options:
            self.space_combo.addItem(item["name"])
        last_space = self.command.params.GetString("LastSpaceOrSector", "")
        if last_space:
            idx = self.space_combo.findText(last_space)
            if idx >= 0:
                self.space_combo.setCurrentIndex(idx)
                self.command.space_or_sector = last_space

    def on_space_selected(self, index):
        self.command.space_or_sector = self.space_options[index - 1]["name"] if index > 0 and index - 1 < len(self.space_options) else ""
        self.command.params.SetString("LastSpaceOrSector", self.command.space_or_sector)
        self.sync_values()

    def populate_families(self):
        """Lê os arquivos da biblioteca e preenche a lista de forma robusta."""
        base_path = os.path.dirname(os.path.dirname(__file__))
        lib_path = os.path.join(base_path, "Library", "3D", "Tomadas")
        self.family_meta_by_source = {}

        try:
            from EletricaLogic.FamilyCatalog import list_families
            families = list_families("Tomada")
        except Exception as exc:
            families = []
            App.Console.PrintWarning(f"Nao foi possivel ler catalogo de familias: {exc}\n")
        if families:
            self.family_list.clear()
            for family in families:
                source = family.get("source_3d") or ""
                if not source:
                    continue
                self.family_meta_by_source[source] = family
                item = QtGui.QListWidgetItem(family.get("name") or os.path.basename(source).replace(".FCStd", "").replace("_", " "))
                item.setData(QtCore.Qt.UserRole, source)
                self.family_list.addItem(item)
            if self.family_list.count() > 0:
                selected = self.select_family_file(self.command.family_file, apply=True)
                if not selected:
                    self.family_list.blockSignals(True)
                    self.family_list.setCurrentRow(0)
                    self.family_list.blockSignals(False)
                    self.on_family_selected(self.family_list.item(0))
                return
        
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
                    self.family_list.blockSignals(True)
                    self.family_list.setCurrentRow(0)
                    self.family_list.blockSignals(False)
                    self.on_family_selected(self.family_list.item(0))
        else:
            print(f"Erro: Pasta da biblioteca não encontrada em {lib_path}")

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

    def set_quick_type(self, modules=None, amperage=None):
        if modules:
            self.command.modules = modules
        if amperage:
            self.command.amperage = amperage
        if hasattr(self.command, "update_family_file_from_type"):
            self.command.update_family_file_from_type()
        self.sync_ui()
        self.refresh_ghost()

    def sync_quick_buttons(self):
        if not hasattr(self, "quick_1m_btn"):
            return
        button_states = [
            (self.quick_1m_btn, self.command.modules.startswith("1")),
            (self.quick_2m_btn, self.command.modules.startswith("2")),
            (self.quick_10a_btn, self.command.amperage == "10A"),
            (self.quick_20a_btn, self.command.amperage == "20A"),
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
        meta = self.family_meta_by_source.get(str(fname).replace("\\", "/"), {})
        if meta and hasattr(self.command, "apply_family_metadata"):
            self.command.apply_family_metadata(meta)
            if hasattr(self, "z_in"):
                self.sync_ui()
            else:
                self.sync_quick_buttons()
            self.refresh_ghost()
            print(f"Família Selecionada: {name}")
            return

        # Mapeia o nome da lista de volta para as propriedades
        if "Dupla" in name: self.command.modules = "2 Módulos"
        elif "Tripla" in name: self.command.modules = "3 Módulos"
        else: self.command.modules = "1 Módulo"
        
        if "20A" in name: self.command.amperage = "20A"
        else: self.command.amperage = "10A"
        self.sync_quick_buttons()
        self.refresh_ghost()

        print(f"Família Selecionada: {name}")

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
        if "Baixa" in txt: self.z_in.setValue(self.command.socket_low_height)
        elif "Média" in txt: self.z_in.setValue(self.command.socket_medium_height)
        elif "Alta" in txt: self.z_in.setValue(self.command.socket_high_height)
        self.sync_values()

    def on_insert_mode_changed(self, index):
        self.command.continuous_insert = index == 0
        self.command.params.SetBool("SocketContinuousInsert", self.command.continuous_insert)
        self.sync_values()

    def sync_values(self):
        self.command.z_level = self.z_in.value()
        self.command.rotation = self.rot_in.value()
        self.command.circuit_type = self.circuit_combo.currentText()
        self.command.height_type = self.height_combo.currentText()
        self.command.panel_board = self.panel_combo.currentText() if self.panel_combo.currentIndex() > 0 else self.command.panel_board
        self.command.circuit_number = self.circuit_ref_combo.currentText().split(" ", 1)[0] if self.circuit_ref_combo.currentIndex() > 0 else self.command.circuit_number
        self.command.space_or_sector = self.space_combo.currentText() if self.space_combo.currentIndex() > 0 else self.command.space_or_sector
        self.final_z_label.setText(f"Z final: {self.command.get_final_z():.0f} mm")
        # Se mudar altura/tipo/uso, o fantasma reflete a simbologia real imediatamente.
        self.refresh_ghost()
        
    def sync_ui(self):
        """Atualiza os controles do painel quando atalhos de teclado são usados."""
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

        self.select_family_file(self.command.family_file)
        self.sync_quick_buttons()
        self.final_z_label.setText(f"Z final: {self.command.get_final_z():.0f} mm")
        
        # Atualiza o texto de ajuda (Dica HUD)
        print(f"HUD: Nível={self.command.reference_level_name} | Altura={self.command.z_level}mm | Circuito={self.command.circuit_type}")

    def accept(self):
        Gui.Control.closeDialog()
        return True

class SocketCommand:
    """Comando de Inserção de Tomadas BIM (Estilo Revit)"""
    def __init__(self):
        self.modules = "1 Módulo"
        self.command_name = "Eletrica_InsertSocket"
        self.amperage = "10A"
        self.z_level = 1100.0
        self.rotation = 0
        self.circuit_type = "TUG (Geral)"
        self.circuit_number = "C-01"
        self.panel_board = ""
        self.circuit_object = ""
        self.space_or_sector = ""
        self.params = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Eletrica")
        self.continuous_insert = self.params.GetBool("SocketContinuousInsert", True)
        self.plate_size = "4x2"
        self.height_type = "Média (1100mm)"
        self.family_file = "Tomada_Simples_10A.FCStd"
        self.family_name = "Tomada Simples 10A"
        self.family_category = "Tomada"
        self.ifc_class = "IfcFlowTerminal"
        self.voltage = "127V"
        self.power = 100.0
        self.manufacturer = ""
        self.model = ""
        self.catalog_code = ""
        self.family_description = ""
        self.level_options = []
        self.reference_level_index = 0
        self.reference_level_name = "Projeto"
        self.reference_level_object = ""
        self.level_elevation = 0.0
        self.socket_low_height = 300.0
        self.socket_medium_height = 1100.0
        self.socket_high_height = 2200.0
        self.detect_surfaces = True
        self.quiet_placement = True
        self.snap_to_junction_boxes = False
        self.surface_offset = 5.0
        self.host_object = ""
        self.host_sub = ""
        self.load_project_defaults()
        self.engine = None # Inicializa o motor

    def IsActive(self):
        return App.ActiveDocument is not None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_path, "Icons", "Tomada_BR.svg")
        return {
            'Pixmap': icon_path, 
            'MenuText': 'Inserir Tomada BIM', 
            'ToolTip': 'Catálogo de Famílias de Tomadas NBR',
            'Checkable': True
        }

    def Activated(self, *args, **kwargs):
        from GeometryScripts.bim_placement_core import BIMPlacementEngine
        if BIMPlacementEngine.active_engine is not None:
            active_engine = BIMPlacementEngine.active_engine
            active_cmd = active_engine.cmd
            if isinstance(active_cmd, SocketCommand):
                same_button = getattr(active_cmd, "command_name", "") == getattr(self, "command_name", "")
                same_type_without_button = (
                    not getattr(active_cmd, "command_name", "")
                    and getattr(active_cmd, "circuit_type", "") == getattr(self, "circuit_type", "")
                )
                if same_button or same_type_without_button:
                    active_engine.stop()
                    return

        if not App.ActiveDocument:
            App.newDocument("Projeto_Eletrico")
        self.load_project_defaults()
        self.engine = BIMPlacementEngine(self, SocketTaskPanel, self.place_socket)
        self.engine.start()

    def IsChecked(self):
        try:
            from GeometryScripts.bim_placement_core import BIMPlacementEngine
            if BIMPlacementEngine.active_engine is not None:
                active_cmd = BIMPlacementEngine.active_engine.cmd
                if isinstance(active_cmd, self.__class__):
                    if getattr(active_cmd, "command_name", "") == getattr(self, "command_name", ""):
                        return True
                    if not getattr(active_cmd, "command_name", "") and getattr(active_cmd, "circuit_type", "") == getattr(self, "circuit_type", ""):
                        return True
        except Exception:
            pass
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
            ("surface_offset", "SurfaceOffset", 5.0),
        ]:
            try:
                value = getattr(project, prop)
                setattr(self, attr, float(value.Value if hasattr(value, "Value") else value))
            except Exception:
                setattr(self, attr, default)
        try:
            self.detect_surfaces = bool(project.DetectSurfaces)
        except Exception:
            self.detect_surfaces = True
        self.quiet_placement = self.params.GetBool("QuietSocketPlacement", True)
        if self.quiet_placement:
            self.detect_surfaces = False
        self.z_level = self.socket_medium_height

    def make_preview_shape(self):
        # Usa a mesma simbologia 2D da tomada real, mantendo o fantasma leve.
        try:
            from .socket_bim import make_socket_plan_symbol
            shape = make_socket_plan_symbol(self.normalized_height_type(), self.modules, self.amperage)
            if shape:
                return shape
        except Exception:
            pass

        # Fallback seguro para 4x2 retangular deitadinho
        w = 80.0
        h = 120.0
        plate = Part.makeBox(w, h, 2)
        plate.translate(App.Vector(-w/2, -h/2, 0))
        return plate

    def preview_color(self):
        if "UPS" in self.circuit_type:
            return (1.0, 0.0, 0.0)
        if "Específico" in self.circuit_type:
            return (1.0, 0.75, 0.0)
        return (0.0, 0.35, 1.0)

    def family_library_path(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_path, "Library", "3D", "Tomadas")

    def family_filename_for_type(self):
        try:
            from EletricaLogic.FamilyCatalog import find_family
            family = find_family("Tomada", modules=self.modules, amperage=self.amperage)
            if family and family.get("source_3d"):
                self.apply_family_metadata(family)
                return family.get("source_3d")
        except Exception:
            pass
        is_2 = self.modules.startswith("2")
        is_20 = self.amperage == "20A"
        if is_2:
            return "Tomada_Dupla_20A.FCStd" if is_20 else "Tomada_Dupla_10A_10A.FCStd"
        return "Tomada_Simples_20A.FCStd" if is_20 else "Tomada_Simples_10A.FCStd"

    def update_family_file_from_type(self):
        fname = self.family_filename_for_type()
        if os.path.exists(self.resolve_family_path(fname)):
            self.family_file = fname
        return self.family_file

    def resolve_family_path(self, source):
        source = str(source or "").replace("\\", "/").strip("/")
        if os.path.isabs(source):
            return source
        if "/" in source:
            base_path = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(base_path, "Library", "3D", source.replace("/", os.sep))
        return os.path.join(self.family_library_path(), source)

    def normalize_modules(self, value):
        text = str(value or "")
        if text.startswith("2"):
            return "2 Módulos"
        if text.startswith("3"):
            return "3 Módulos"
        return "1 Módulo"

    def normalize_height_label(self, value):
        text = str(value or "")
        if "Baixa" in text or text.startswith("300"):
            return "Baixa (300mm)"
        if "Alta" in text or text.startswith("2200"):
            return "Alta (2200mm)"
        return "Média (1100mm)"

    def apply_family_metadata(self, family):
        self.family_file = family.get("source_3d", self.family_file) or self.family_file
        self.family_name = family.get("name", self.family_name) or self.family_name
        self.family_category = family.get("category", self.family_category) or self.family_category
        self.ifc_class = family.get("ifc_class", self.ifc_class) or self.ifc_class
        self.modules = self.normalize_modules(family.get("modules", self.modules))
        self.amperage = family.get("amperage", self.amperage) or self.amperage
        self.voltage = family.get("voltage", self.voltage) or self.voltage
        self.power = float(family.get("power", self.power) or self.power)
        self.height_type = self.normalize_height_label(family.get("height_type", self.height_type))
        if family.get("mounting_height") not in [None, ""]:
            self.z_level = float(family.get("mounting_height"))
        self.manufacturer = family.get("manufacturer", self.manufacturer) or ""
        self.model = family.get("model", self.model) or ""
        self.catalog_code = family.get("catalog_code", self.catalog_code) or ""
        self.family_description = family.get("description", self.family_description) or ""

    def cycle_height(self):
        heights = [self.socket_low_height, self.socket_medium_height, self.socket_high_height]
        current = float(self.z_level)
        nearest = min(range(len(heights)), key=lambda idx: abs(float(heights[idx]) - current))
        self.z_level = float(heights[(nearest + 1) % len(heights)])
        self.height_type = self.normalized_height_type()

    def cycle_amperage(self):
        self.amperage = "20A" if self.amperage == "10A" else "10A"
        self.update_family_file_from_type()

    def cycle_modules(self):
        self.modules = "2 Módulos" if self.modules.startswith("1") else "1 Módulo"
        self.update_family_file_from_type()

    def cycle_insert_mode(self):
        self.continuous_insert = not self.continuous_insert
        self.params.SetBool("SocketContinuousInsert", self.continuous_insert)

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

    def cycle_level(self):
        if not self.level_options:
            return
        self.set_reference_level((self.reference_level_index + 1) % len(self.level_options))

    def get_final_z(self):
        return float(self.level_elevation) + float(self.z_level)

    def normalized_height_type(self):
        if self.z_level <= 700:
            return "Baixa (300mm)"
        if self.z_level <= 1600:
            return "Média (1100mm)"
        return "Alta (2200mm)"

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
        modules = self.matrix_token(self.modules)
        amperage = self.matrix_token(self.amperage)
        height = self.matrix_token(self.normalized_height_type())
        return f"Matriz_Tomada_{source}_{modules}_{amperage}_{height}"

    def mark_as_library_matrix(self, obj):
        if not obj:
            return
        _set_property(obj, "App::PropertyString", "BIMRole", "BIM_Classificacao", "SocketMatrix")
        _set_property(obj, "App::PropertyBool", "IsLibraryMatrix", "BIM_Classificacao", True)
        _set_property(obj, "App::PropertyString", "MatrixSourceFile", "BIM_Familia", self.family_file)
        _set_property(obj, "App::PropertyString", "MatrixFamilyName", "BIM_Familia", self.family_name)
        _set_property(obj, "App::PropertyString", "MatrixHeightType", "BIM_Familia", self.normalized_height_type())

        # Matriz e apenas geometria/familia. A carga real fica na instancia visivel.
        for attr, value in [
            ("CircuitNumber", ""),
            ("CircuitObject", ""),
            ("PanelBoard", ""),
            ("SpaceOrSector", ""),
            ("Power", 0.0),
        ]:
            if hasattr(obj, attr):
                try:
                    setattr(obj, attr, value)
                except Exception:
                    pass

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

    def make_socket_instance_object(self, doc, matriz):
        obj = doc.addObject("Part::Feature", f"Tomada_{self.modules.replace(' ', '_')}")
        source_shape = None
        try:
            if getattr(matriz, "Shape", None) and not matriz.Shape.isNull():
                source_shape = matriz.Shape.copy()
        except Exception:
            source_shape = None

        if source_shape is None:
            source_shape = self.make_preview_shape()

        obj.Shape = source_shape
        _set_property(obj, "App::PropertyString", "BIMRole", "BIM_Classificacao", "Socket")
        _set_property(obj, "App::PropertyBool", "IsLibraryMatrix", "BIM_Classificacao", False)
        _set_property(obj, "App::PropertyString", "LibraryMatrixObject", "BIM_Familia", getattr(matriz, "Name", ""))
        _set_property(obj, "App::PropertyString", "GeometrySourceMode", "BIM_Familia", "CachedShapeFromMatrix")
        return obj

    def enable_link_independent_placement(self, obj, placement=None):
        if not obj:
            return
        if placement is None:
            placement = getattr(obj, "Placement", None)
        try:
            if hasattr(obj, "LinkTransform"):
                # LinkTransform=False e o modo padrao do App::Link para cada instancia
                # sobrescrever a posicao da matriz com seu proprio Placement.
                obj.LinkTransform = False
        except Exception:
            pass
        try:
            if hasattr(obj, "LinkPlacement"):
                obj.LinkPlacement = App.Placement()
        except Exception:
            pass
        if placement is not None:
            try:
                obj.Placement = placement
            except Exception:
                pass
        try:
            if getattr(obj, "ViewObject", None):
                obj.ViewObject.Visibility = True
                obj.ViewObject.Selectable = True
        except Exception:
            pass

    def repair_socket_links(self, doc):
        if not doc:
            return
        for candidate in doc.Objects:
            try:
                if getattr(candidate, "BIMRole", "") != "Socket":
                    continue
                if getattr(candidate, "TypeId", "") != "App::Link":
                    continue
                source = getattr(candidate, "LinkedObject", None)
                if source is None and hasattr(candidate, "getLinkedObject"):
                    try:
                        source = candidate.getLinkedObject()
                    except Exception:
                        source = None
                if source and getattr(source, "BIMRole", "") == "SocketMatrix":
                    self.hide_library_matrix(source)
                self.enable_link_independent_placement(candidate, getattr(candidate, "Placement", None))
            except Exception:
                pass

    def make_arch_component(self, obj, label):
        component = Arch.makeComponent(obj)
        target = component or obj
        target.Label = label
        obj.Label = label
        return target

    def place_socket(self, point, is_ghost=False):
        # SEMPRE usa o documento que estava ativo no início do comando
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        
        if is_ghost:
            # CRIAR FANTASMA ULTRA-LEVE COM A MESMA SIMBOLOGIA DA TOMADA REAL
            obj = doc.addObject("Part::Feature", "GHOST_Socket")
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
                # ESCONDE DA ÁRVORE (Para ficar profissional e limpo)
                if hasattr(obj.ViewObject, "ShowInTree"):
                    obj.ViewObject.ShowInTree = False
            
        else:
            # --- LOGICA DE MATRIZ EM CACHE ---
            # Nome único e estável para a tomada matriz baseado na sua configuração
            matriz_label = self.matrix_label()
            
            # Procuramos se a tomada matriz já existe no documento
            matriz = None
            for o in doc.Objects:
                if o.Label == matriz_label:
                    matriz = o
                    break
                    
            # Se não existe, cria a tomada matriz uma única vez
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                matriz.Label = matriz_label
                from .socket_bim import ProfessionalBIMSocket
                ProfessionalBIMSocket(matriz)
                
                # Aplica as propriedades padrão da matriz
                matriz.Modules = self.modules
                matriz.Amperage = self.amperage
                matriz.SourceFile = self.family_file
                matriz.HeightType = self.normalized_height_type()
                matriz.IFC_Class = self.ifc_class
                source_matriz = matriz
                self.mark_as_library_matrix(source_matriz)
                
                # Mantem a matriz como FeaturePython: o ponto BIM real e a instancia visivel.
                matriz = source_matriz
                self.mark_as_library_matrix(source_matriz)
                self.mark_as_library_matrix(matriz)
                try:
                    doc.recompute()
                except Exception:
                    pass
                
                # Oculta a matriz do desenho e da árvore para ficar invisível e limpa
            self.mark_as_library_matrix(matriz)
            try:
                if not getattr(matriz, "Shape", None) or matriz.Shape.isNull():
                    doc.recompute()
            except Exception:
                pass

            # Cria a instancia visivel a partir da forma ja carregada na matriz.
            # App::Link ficou rapido, mas nao renderizou em alguns ambientes do FreeCAD.
            obj = self.make_socket_instance_object(doc, matriz)
            self.hide_library_matrix(matriz)
            
            # --- ADICIONA AS PROPRIEDADES BIM INDIVIDUAIS DIRETAMENTE NO LINK ---
            # Engenharia
            obj.addProperty("App::PropertyString", "CircuitNumber", "BIM_Engenharia").CircuitNumber = self.circuit_number
            obj.addProperty("App::PropertyEnumeration", "Voltage", "BIM_Engenharia").Voltage = ["127V", "220V", "380V"]
            try:
                obj.Voltage = self.voltage
            except Exception:
                pass
            obj.addProperty("App::PropertyFloat", "Power", "BIM_Engenharia").Power = self.power
            obj.addProperty("App::PropertyString", "PanelBoard", "BIM_Engenharia").PanelBoard = self.panel_board
            obj.addProperty("App::PropertyString", "CircuitObject", "BIM_Engenharia").CircuitObject = self.circuit_object
            obj.addProperty("App::PropertyString", "SpaceOrSector", "BIM_Engenharia").SpaceOrSector = self.space_or_sector
            
            # Posicionamento/Referência
            obj.addProperty("App::PropertyString", "ReferenceLevel", "BIM_Posicionamento").ReferenceLevel = self.reference_level_name
            obj.addProperty("App::PropertyString", "ReferenceLevelObject", "BIM_Posicionamento").ReferenceLevelObject = self.reference_level_object
            obj.addProperty("App::PropertyLength", "LevelElevation", "BIM_Posicionamento").LevelElevation = self.level_elevation
            obj.addProperty("App::PropertyLength", "MountingHeight", "BIM_Posicionamento").MountingHeight = self.z_level
            obj.addProperty("App::PropertyLength", "FinalElevation", "BIM_Posicionamento").FinalElevation = self.get_final_z()
            
            # Família
            obj.addProperty("App::PropertyString", "IFC_Class", "BIM_Classificacao").IFC_Class = self.ifc_class
            obj.addProperty("App::PropertyString", "FamilyName", "BIM_Familia").FamilyName = self.family_name
            obj.addProperty("App::PropertyString", "FamilyCategory", "BIM_Familia").FamilyCategory = self.family_category
            obj.addProperty("App::PropertyString", "Manufacturer", "BIM_Familia").Manufacturer = self.manufacturer
            obj.addProperty("App::PropertyString", "Model", "BIM_Familia").Model = self.model
            obj.addProperty("App::PropertyString", "CatalogCode", "BIM_Familia").CatalogCode = self.catalog_code
            obj.addProperty("App::PropertyString", "FamilyDescription", "BIM_Familia").FamilyDescription = self.family_description
            
            if self.detect_surfaces:
                obj.addProperty("App::PropertyString", "HostObject", "BIM_Posicionamento").HostObject = self.host_object
                obj.addProperty("App::PropertyString", "HostFace", "BIM_Posicionamento").HostFace = self.host_sub
                obj.addProperty("App::PropertyLength", "SurfaceOffset", "BIM_Posicionamento").SurfaceOffset = self.surface_offset
            
            # Tag IFC/BIM
            obj.addProperty("App::PropertyString", "Tag", "BIM_Classificacao")
            prefix = "TUG" if "Geral" in self.circuit_type else "TUE"
            if "UPS" in self.circuit_type: prefix = "UPS"
            obj.Tag = f"{prefix}-{self.amperage}"
            
            color = (0.9, 0.9, 0.9)
            if "UPS" in self.circuit_type: color = (1.0, 0.0, 0.0)
            elif "Específico" in self.circuit_type: color = (1.0, 1.0, 0.0)
            try:
                obj.ViewObject.ShapeColor = color
            except Exception:
                pass
            
            # Geração de Nome Inteligente (Ex: Tomada Simples 01)
            tipo_nome = "Simples" if "1" in self.modules else "Dupla"
            prefixo = f"Tomada {tipo_nome} {self.amperage}"
            
            # Conta quantos itens com esse prefixo já existem para numerar
            count = len([o for o in doc.Objects if prefixo in o.Label]) + 1
            label = f"{prefixo} {count:02d}"
            obj.Label = label

        # Posicionamento Real
        final_z = self.get_final_z()
        px = point.x if hasattr(point, 'x') else point[0]
        py = point.y if hasattr(point, 'y') else point[1]
        target_pos = App.Vector(px, py, final_z)
        if self.detect_surfaces and self.host_object:
            target_pos.z = final_z + self.surface_offset
        target_rot = App.Rotation(App.Vector(0,0,1), self.rotation)
        target_placement = App.Placement(target_pos, target_rot)
        if not is_ghost and getattr(obj, "TypeId", "") == "App::Link":
            self.enable_link_independent_placement(obj, target_placement)
            self.repair_socket_links(doc)
        else:
            obj.Placement = target_placement
        
        if not is_ghost:
            # Adiciona o objeto fisicamente ao nível/pavimento correto na árvore de projetos
            if hasattr(self, "reference_level_object") and self.reference_level_object:
                level_obj = doc.getObject(self.reference_level_object)
                if level_obj and hasattr(level_obj, "addObject"):
                    level_obj.addObject(obj)
            
            App.Console.PrintLog(f"Tomada inserida em: {px:.1f}, {py:.1f}, Z: {final_z:.1f} ({self.reference_level_name} + {self.z_level:.1f}mm)\n")
            try:
                from EletricaGuiCommands.ProjectSetup import recalculate_circuit_loads
                recalculate_circuit_loads(doc)
            except Exception:
                pass
            doc.recompute()
        return obj

try:
    existing_commands = Gui.listCommands()
except Exception:
    existing_commands = []

if 'Eletrica_InsertSocket' not in existing_commands:
    Gui.addCommand('Eletrica_InsertSocket', SocketCommand())
