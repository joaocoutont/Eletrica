import csv
import os
import FreeCAD
import FreeCADGui
from EletricaLogic.i18n import tr
try:
    import tomllib
except Exception:
    tomllib = None
try:
    from PySide import QtWidgets
except ImportError:
    try:
        from PySide import QtGui as QtWidgets
    except ImportError:
        try:
            from PySide2 import QtWidgets
        except ImportError:
            QtWidgets = None

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Icons")
PROFILE_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Templates", "ProjectProfiles")


def _arch():
    try:
        import Arch
        return Arch
    except Exception:
        return None

DEFAULT_LEVELS = [
    ("Nivel Terreo", 0.0),
    ("Nivel 01", 3000.0),
    ("Nivel 02", 6000.0),
]

FILE_FILTERS = {
    "CAD": "Arquivos CAD (*.dxf *.dwg);;DXF (*.dxf);;DWG (*.dwg);;Todos (*.*)",
    "IFC": "Arquivos IFC (*.ifc *.ifczip);;Todos (*.*)",
    "FreeCAD": "Arquivos FreeCAD (*.FCStd *.fcstd);;Todos (*.*)",
}

PROJECT_GROUP = "Projeto Eletrico"
PROJECT_GROUPS = [
    "Referencias",
    "Contexto BIM",
    "Zonas e Setores",
    "Niveis",
    "Espacos",
    "Quadros",
    "Circuitos",
    "Pontos Eletricos",
    "Eletrodutos",
    "Condutores",
    "Documentacao",
]

PROJECT_PROFILES = {
    "Predial / Hospitalar": {
        "site": True,
        "building": True,
        "levels": True,
        "spaces": True,
        "groups": ["Ambientes", "Leitos / Areas Criticas", "Shafts", "Prumadas"],
    },
    "Industrial": {
        "site": True,
        "building": False,
        "levels": False,
        "spaces": False,
        "groups": ["Setor Producao", "Setor Utilidades", "Subestacoes", "CCMs", "Maquinas"],
    },
    "Automacao Residencial": {
        "site": True,
        "building": True,
        "levels": True,
        "spaces": True,
        "groups": [
            "Central Automacao", "Iluminacao Automatizada", "Cortinas e Persianas",
            "Climatizacao", "Audio e Video", "CFTV", "Controle de Acesso",
            "Rede Dados WiFi", "Sensores", "Atuadores"
        ],
    },
    "Automacao Industrial": {
        "site": True,
        "building": False,
        "levels": False,
        "spaces": False,
        "groups": [
            "PLCs", "IHMs", "Remotas IO", "Instrumentacao", "Sensores",
            "Atuadores", "Redes Industriais", "Painel Controle", "Seguranca Maquina"
        ],
    },
    "Saneamento": {
        "site": True,
        "building": False,
        "levels": False,
        "spaces": False,
        "groups": ["Captacao", "Elevatorias", "ETA / ETE", "Reservatorios", "Bombas e Motores"],
    },
    "Rede Urbana": {
        "site": True,
        "building": False,
        "levels": False,
        "spaces": False,
        "groups": ["Alimentadores MT", "Rede BT", "Postes", "Transformadores", "Iluminacao Publica", "Ramais"],
    },
    "Rede Rural": {
        "site": True,
        "building": False,
        "levels": False,
        "spaces": False,
        "groups": ["Alimentadores Rurais", "Trechos", "Postes", "Transformadores", "Chaves", "Ramais Rurais"],
    },
    "Subestacao / MT": {
        "site": True,
        "building": False,
        "levels": False,
        "spaces": False,
        "groups": ["Patio MT", "Cubiculos", "Transformadores", "Protecao", "Aterramento", "Barramentos"],
    },
    "Generico": {
        "site": True,
        "building": False,
        "levels": False,
        "spaces": False,
        "groups": ["Zonas", "Equipamentos", "Redes", "Cargas"],
    },
}

PROFILE_ELECTRICAL_DEFAULTS = {
    "Predial / Hospitalar": {
        "panels": ["QD-Terreo", "QD-Nivel-01"],
        "circuits": ["C-01 TUG", "C-02 TUE", "C-03 Iluminacao", "C-04 Emergencia"],
    },
    "Industrial": {
        "panels": ["QGBT", "CCM-01", "QD-Utilidades"],
        "circuits": ["AL-01 Alimentador", "M-01 Motores", "IL-01 Iluminacao", "TM-01 Tomadas Manutencao"],
    },
    "Automacao Residencial": {
        "panels": ["QDA-01 Automacao", "QDC-01 Dados"],
        "circuits": [
            "AUT-01 Central Automacao", "IL-01 Iluminacao Automatizada",
            "CT-01 Cortinas", "CL-01 Climatizacao", "AV-01 Audio Video",
            "CFTV-01 Cameras", "AC-01 Controle Acesso", "DADOS-01 Rede"
        ],
    },
    "Automacao Industrial": {
        "panels": ["QTA-01 Automacao", "PLC-01", "IHM-01", "RIO-01"],
        "circuits": [
            "INST-01 Instrumentacao", "COM-01 Comando", "ETH-01 Rede Industrial",
            "SEG-01 Seguranca", "IO-01 Remotas IO", "AT-01 Atuadores"
        ],
    },
    "Saneamento": {
        "panels": ["QGBT", "CCM-Bombas", "QD-Instrumentacao"],
        "circuits": ["B-01 Bomba", "B-02 Bomba Reserva", "I-01 Instrumentacao", "C-01 Comando"],
    },
    "Rede Urbana": {
        "panels": ["Alimentador-MT-01"],
        "circuits": ["MT-01 Alimentador", "BT-01 Rede BT", "IP-01 Iluminacao Publica"],
    },
    "Rede Rural": {
        "panels": ["Alimentador-Rural-01"],
        "circuits": ["MT-01 Tronco Rural", "RM-01 Ramal Rural", "TR-01 Transformador"],
    },
    "Subestacao / MT": {
        "panels": ["SE-01", "Cubiculo-MT-01", "QGBT"],
        "circuits": ["MT-01 Entrada", "TR-01 Transformador", "BT-01 Saida QGBT", "PR-01 Protecao"],
    },
    "Generico": {
        "panels": ["QD-01"],
        "circuits": ["C-01 Geral"],
    },
}

PROFILE_AUTOMATION_DEFAULTS = {
    "Automacao Residencial": {
        "AutomationScope": "Residencial inteligente",
        "ControlVoltage": "24Vcc / rede local",
        "Protocol": "KNX / Zigbee / Wi-Fi / Ethernet",
        "NetworkType": "Automacao residencial",
        "SafetyCategory": "Residencial",
    },
    "Automacao Industrial": {
        "AutomationScope": "Controle industrial e instrumentacao",
        "ControlVoltage": "24Vcc",
        "Protocol": "Profinet / Modbus TCP / EtherNet-IP",
        "NetworkType": "Ethernet industrial",
        "SafetyCategory": "NR-12 / seguranca de maquina",
    },
}


def _load_profiles_from_toml():
    if not tomllib or not os.path.isdir(PROFILE_TEMPLATE_DIR):
        return None

    profiles = {}
    electrical = {}
    automation = {}

    for fname in sorted(os.listdir(PROFILE_TEMPLATE_DIR)):
        if not fname.lower().endswith(".toml"):
            continue
        path = os.path.join(PROFILE_TEMPLATE_DIR, fname)
        try:
            with open(path, "rb") as fh:
                data = tomllib.load(fh)
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Perfil TOML ignorado ({fname}): {e}\n")
            continue

        name = data.get("name") or os.path.splitext(fname)[0].replace("_", " ").title()
        profiles[name] = {
            "site": bool(data.get("site", True)),
            "building": bool(data.get("building", False)),
            "levels": bool(data.get("levels", False)),
            "spaces": bool(data.get("spaces", False)),
            "groups": list(data.get("groups", [])),
        }

        electrical_data = data.get("electrical", {})
        electrical[name] = {
            "panels": list(electrical_data.get("panels", [])),
            "circuits": list(electrical_data.get("circuits", [])),
        }

        automation_data = data.get("automation", {})
        if automation_data:
            automation[name] = {str(k): str(v) for k, v in automation_data.items()}

    if not profiles:
        return None

    # Preserve built-in ordering, while still allowing additional TOML profiles.
    ordered_profiles = {}
    ordered_electrical = {}
    ordered_automation = {}
    for name in PROJECT_PROFILES.keys():
        if name in profiles:
            ordered_profiles[name] = profiles.pop(name)
            ordered_electrical[name] = electrical.pop(name, {"panels": [], "circuits": []})
            if name in automation:
                ordered_automation[name] = automation.pop(name)
        else:
            ordered_profiles[name] = PROJECT_PROFILES[name]
            ordered_electrical[name] = PROFILE_ELECTRICAL_DEFAULTS.get(name, {"panels": [], "circuits": []})
            if name in PROFILE_AUTOMATION_DEFAULTS:
                ordered_automation[name] = PROFILE_AUTOMATION_DEFAULTS[name]

    for name in sorted(profiles.keys()):
        ordered_profiles[name] = profiles[name]
        ordered_electrical[name] = electrical.get(name, {"panels": [], "circuits": []})
        if name in automation:
            ordered_automation[name] = automation[name]

    return ordered_profiles, ordered_electrical, ordered_automation


_loaded_templates = _load_profiles_from_toml()
if _loaded_templates:
    PROJECT_PROFILES, PROFILE_ELECTRICAL_DEFAULTS, PROFILE_AUTOMATION_DEFAULTS = _loaded_templates

LEVEL_KEYWORDS = [
    "level", "nivel", "nível", "pavimento", "storey", "story",
    "floor", "andar", "terreo", "térreo", "buildingpart", "ifcbuildingstorey",
]
SITE_KEYWORDS = ["site", "sitio", "sítio", "terreno", "empreendimento", "ifcsite"]
BUILDING_KEYWORDS = ["building", "edificacao", "edificação", "predio", "prédio", "ifcbuilding"]
SPACE_KEYWORDS = ["space", "espaco", "espaço", "ambiente", "room", "sala", "ifcspace"]


def _ensure_doc():
    return FreeCAD.ActiveDocument or FreeCAD.newDocument("Projeto_Eletrico")


def _plain_value(value):
    return value.Value if hasattr(value, "Value") else value


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
    return any(word in text for word in LEVEL_KEYWORDS)


def _is_site_object(obj):
    text = _object_text(obj)
    return any(word in text for word in SITE_KEYWORDS)


def _is_building_object(obj):
    text = _object_text(obj)
    return any(word in text for word in BUILDING_KEYWORDS)


def _is_space_object(obj):
    text = _object_text(obj)
    return any(word in text for word in SPACE_KEYWORDS)


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


def _find_group(doc, label):
    for obj in doc.Objects:
        if obj.Label == label and obj.TypeId == "App::DocumentObjectGroup":
            return obj
    return None


def _ensure_group(doc, label, parent=None):
    group = _find_group(doc, label)
    if not group:
        group = doc.addObject("App::DocumentObjectGroup", label.replace(" ", "_"))
        group.Label = label
    if parent:
        try:
            parent.addObject(group)
        except Exception:
            pass
    return group


def _ensure_property(obj, prop_type, name, group, value):
    try:
        if not hasattr(obj, name):
            obj.addProperty(prop_type, name, group)
        setattr(obj, name, value)
    except Exception:
        pass


class ElectricalPanelProxy:
    def __init__(self, obj):
        obj.Proxy = self
        _ensure_property(obj, "App::PropertyString", "BIMRole", "BIM_Eletrica", "PanelBoard")
        _ensure_property(obj, "App::PropertyString", "IFC_Class", "BIM_Eletrica", "IfcDistributionBoard")
        _ensure_property(obj, "App::PropertyString", "PanelType", "BIM_Eletrica", "Distribuicao")
        _ensure_property(obj, "App::PropertyString", "Voltage", "BIM_Eletrica", "127/220V")
        _ensure_property(obj, "App::PropertyString", "Phases", "BIM_Eletrica", "2F+N+PE")
        _ensure_property(obj, "App::PropertyString", "RatedCurrent", "BIM_Eletrica", "63A")
        _ensure_property(obj, "App::PropertyString", "ShortCircuitLevel", "BIM_Eletrica", "")
        _ensure_property(obj, "App::PropertyString", "FeedingFrom", "BIM_Eletrica", "")

    def execute(self, obj):
        pass


class ElectricalCircuitProxy:
    def __init__(self, obj):
        obj.Proxy = self
        _ensure_property(obj, "App::PropertyString", "BIMRole", "BIM_Eletrica", "Circuit")
        _ensure_property(obj, "App::PropertyString", "IFC_Class", "BIM_Eletrica", "IfcElectricalCircuit")
        _ensure_property(obj, "App::PropertyString", "CircuitNumber", "BIM_Eletrica", "")
        _ensure_property(obj, "App::PropertyString", "Usage", "BIM_Eletrica", "")
        _ensure_property(obj, "App::PropertyString", "Voltage", "BIM_Eletrica", "127V")
        _ensure_property(obj, "App::PropertyFloat", "Power", "BIM_Eletrica", 0.0)
        _ensure_property(obj, "App::PropertyFloat", "DemandFactor", "BIM_Calculo", 1.0)
        _ensure_property(obj, "App::PropertyFloat", "CurrentA", "BIM_Calculo", 0.0)
        _ensure_property(obj, "App::PropertyFloat", "DesignCurrent", "BIM_Calculo", 0.0)
        _ensure_property(obj, "App::PropertyString", "SuggestedBreaker", "BIM_Calculo", "")
        _ensure_property(obj, "App::PropertyString", "SuggestedCableSection", "BIM_Calculo", "")
        _ensure_property(obj, "App::PropertyFloat", "VoltageDropEstimate", "BIM_Calculo", 0.0)
        _ensure_property(obj, "App::PropertyString", "CableSection", "BIM_Eletrica", "2.5 mm2")
        _ensure_property(obj, "App::PropertyString", "Breaker", "BIM_Eletrica", "16A")
        _ensure_property(obj, "App::PropertyString", "PanelBoard", "BIM_Eletrica", "")
        _ensure_property(obj, "App::PropertyFloat", "ConnectedLoad", "BIM_Cargas", 0.0)
        _ensure_property(obj, "App::PropertyInteger", "PointCount", "BIM_Cargas", 0)

    def execute(self, obj):
        pass


def _safe_name(label):
    return "".join(ch if ch.isalnum() else "_" for ch in label)


def ensure_panel_object(doc, label, parent=None):
    for obj in doc.Objects:
        if obj.Label == label and getattr(obj, "BIMRole", "") == "PanelBoard":
            _add_child(parent, obj)
            return obj
    obj = doc.addObject("App::FeaturePython", _safe_name(label))
    obj.Label = label
    ElectricalPanelProxy(obj)
    _add_child(parent, obj)
    return obj


def ensure_circuit_object(doc, label, parent=None, panel=""):
    for obj in doc.Objects:
        if obj.Label == label and getattr(obj, "BIMRole", "") == "Circuit":
            _add_child(parent, obj)
            return obj
    obj = doc.addObject("App::FeaturePython", _safe_name(label))
    obj.Label = label
    ElectricalCircuitProxy(obj)
    parts = label.split(" ", 1)
    obj.CircuitNumber = parts[0]
    obj.Usage = parts[1] if len(parts) > 1 else label
    obj.PanelBoard = panel
    _add_child(parent, obj)
    return obj


def discover_levels(doc):
    levels = []
    seen = set()
    for obj in doc.Objects:
        if obj.Name in seen or not _is_level_object(obj):
            continue
        seen.add(obj.Name)
        levels.append(obj)
    levels.sort(key=lambda obj: (_level_elevation(obj), obj.Label))
    return levels


def _find_first(doc, predicate):
    for obj in doc.Objects:
        if predicate(obj):
            return obj
    return None


def discover_spaces(doc):
    return [obj for obj in doc.Objects if _is_space_object(obj)]


class SetupConfigDialog(QtWidgets.QDialog if QtWidgets else object):
    def __init__(self, source):
        super(SetupConfigDialog, self).__init__()
        self.source = source
        self.setWindowTitle(tr("Preparar Projeto Eletrico BIM"))
        self.resize(520, 360)

        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.file_in = QtWidgets.QLineEdit()
        self.file_btn = QtWidgets.QPushButton(tr("Escolher..."))
        file_row = QtWidgets.QHBoxLayout()
        file_row.addWidget(self.file_in)
        file_row.addWidget(self.file_btn)
        form.addRow(tr("Arquivo:"), file_row)

        self.profile_combo = QtWidgets.QComboBox()
        self.profile_combo.addItems(list(PROJECT_PROFILES.keys()))
        form.addRow(tr("Tipo de projeto:"), self.profile_combo)

        self.standard_in = QtWidgets.QLineEdit("NBR 5410")
        form.addRow(tr("Norma:"), self.standard_in)

        self.scope_in = QtWidgets.QLineEdit("BT/MT ate 35 kV")
        form.addRow(tr("Escopo:"), self.scope_in)

        self.reference_target_combo = QtWidgets.QComboBox()
        form.addRow(tr("Associar referencia a:"), self.reference_target_combo)

        self.create_missing_cb = QtWidgets.QCheckBox(tr("Criar Site/estrutura BIM quando faltar"))
        self.create_missing_cb.setChecked(True)
        form.addRow("", self.create_missing_cb)

        self.create_levels_cb = QtWidgets.QCheckBox(tr("Criar niveis padrao quando aplicavel e ausente"))
        self.create_levels_cb.setChecked(True)
        form.addRow("", self.create_levels_cb)

        self.create_spaces_cb = QtWidgets.QCheckBox(tr("Criar espacos gerais quando aplicavel e ausente"))
        self.create_spaces_cb.setChecked(True)
        form.addRow("", self.create_spaces_cb)

        self.lock_reference_cb = QtWidgets.QCheckBox(tr("Travar referencia importada/selecionada"))
        self.lock_reference_cb.setChecked(source in ["CAD", "IFC"])
        form.addRow("", self.lock_reference_cb)

        self.create_electrical_defaults_cb = QtWidgets.QCheckBox(tr("Criar quadros e circuitos padrao do perfil"))
        self.create_electrical_defaults_cb.setChecked(True)
        form.addRow("", self.create_electrical_defaults_cb)

        layout.addLayout(form)

        coords_group = QtWidgets.QGroupBox(tr("Referencia espacial / ponto base"))
        coords_form = QtWidgets.QFormLayout(coords_group)
        self.base_mode_combo = QtWidgets.QComboBox()
        self.base_mode_combo.addItems([
            "Usar origem do arquivo",
            "Mover ponto base para origem do projeto",
            "Aplicar deslocamento manual",
        ])
        self.base_x = QtWidgets.QDoubleSpinBox(); self.base_x.setRange(-1000000000, 1000000000); self.base_x.setDecimals(3)
        self.base_y = QtWidgets.QDoubleSpinBox(); self.base_y.setRange(-1000000000, 1000000000); self.base_y.setDecimals(3)
        self.base_z = QtWidgets.QDoubleSpinBox(); self.base_z.setRange(-1000000000, 1000000000); self.base_z.setDecimals(3)
        self.north_angle = QtWidgets.QDoubleSpinBox(); self.north_angle.setRange(-360, 360); self.north_angle.setDecimals(3)
        self.shared_coords_cb = QtWidgets.QCheckBox(tr("Preservar coordenadas compartilhadas do arquivo"))
        self.shared_coords_cb.setChecked(True)
        coords_form.addRow(tr("Origem:"), self.base_mode_combo)
        coords_form.addRow("Base X (mm):", self.base_x)
        coords_form.addRow("Base Y (mm):", self.base_y)
        coords_form.addRow("Base Z (mm):", self.base_z)
        coords_form.addRow("Norte / rotacao (graus):", self.north_angle)
        coords_form.addRow("", self.shared_coords_cb)
        layout.addWidget(coords_group)

        surface_group = QtWidgets.QGroupBox(tr("Superficies e hosts"))
        surface_form = QtWidgets.QFormLayout(surface_group)
        self.detect_surfaces_cb = QtWidgets.QCheckBox(tr("Detectar superficies como referencia de insercao"))
        self.detect_surfaces_cb.setChecked(True)
        self.use_terrain_cb = QtWidgets.QCheckBox(tr("Usar terreno/topografia como base Z quando existir"))
        self.use_terrain_cb.setChecked(source in ["IFC", "FreeCAD"])
        self.surface_offset = QtWidgets.QDoubleSpinBox(); self.surface_offset.setRange(-10000, 10000); self.surface_offset.setValue(5.0)
        surface_form.addRow("", self.detect_surfaces_cb)
        surface_form.addRow("", self.use_terrain_cb)
        surface_form.addRow("Offset da superficie (mm):", self.surface_offset)
        layout.addWidget(surface_group)

        scale_group = QtWidgets.QGroupBox(tr("Conferencia de escala CAD"))
        scale_form = QtWidgets.QFormLayout(scale_group)
        self.apply_scale_cb = QtWidgets.QCheckBox(tr("Aplicar fator de escala ao CAD importado"))
        self.apply_scale_cb.setChecked(False)
        self.known_len = QtWidgets.QDoubleSpinBox(); self.known_len.setRange(0.001, 1000000); self.known_len.setValue(1000)
        self.measured_len = QtWidgets.QDoubleSpinBox(); self.measured_len.setRange(0.001, 1000000); self.measured_len.setValue(1000)
        scale_form.addRow("", self.apply_scale_cb)
        scale_form.addRow("Distancia real (mm):", self.known_len)
        scale_form.addRow("Distancia no CAD:", self.measured_len)
        layout.addWidget(scale_group)
        scale_group.setVisible(source == "CAD")

        levels_group = QtWidgets.QGroupBox(tr("Niveis padrao"))
        levels_form = QtWidgets.QFormLayout(levels_group)
        self.level0 = QtWidgets.QDoubleSpinBox(); self.level0.setRange(-100000, 100000); self.level0.setValue(0)
        self.level1 = QtWidgets.QDoubleSpinBox(); self.level1.setRange(-100000, 100000); self.level1.setValue(3000)
        self.level2 = QtWidgets.QDoubleSpinBox(); self.level2.setRange(-100000, 100000); self.level2.setValue(6000)
        levels_form.addRow("Nivel Terreo (mm):", self.level0)
        levels_form.addRow("Nivel 01 (mm):", self.level1)
        levels_form.addRow("Nivel 02 (mm):", self.level2)
        layout.addWidget(levels_group)

        heights_group = QtWidgets.QGroupBox(tr("Alturas eletricas"))
        heights_form = QtWidgets.QFormLayout(heights_group)
        self.low_h = QtWidgets.QDoubleSpinBox(); self.low_h.setRange(-5000, 10000); self.low_h.setValue(300)
        self.mid_h = QtWidgets.QDoubleSpinBox(); self.mid_h.setRange(-5000, 10000); self.mid_h.setValue(1100)
        self.high_h = QtWidgets.QDoubleSpinBox(); self.high_h.setRange(-5000, 10000); self.high_h.setValue(2200)
        heights_form.addRow("Tomada baixa (mm):", self.low_h)
        heights_form.addRow("Tomada media (mm):", self.mid_h)
        heights_form.addRow("Tomada alta (mm):", self.high_h)
        layout.addWidget(heights_group)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        self.file_btn.clicked.connect(self.choose_file)
        self.profile_combo.currentTextChanged.connect(self.refresh_reference_targets)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.refresh_reference_targets()

    def choose_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            tr("Escolher arquivo de referencia"),
            "",
            FILE_FILTERS.get(self.source, "Todos (*.*)")
        )
        if path:
            self.file_in.setText(path)

    def config(self):
        scale_factor = 1.0
        if self.source == "CAD" and self.measured_len.value():
            scale_factor = self.known_len.value() / self.measured_len.value()
        return {
            "source": self.source,
            "file_path": self.file_in.text().strip(),
            "profile_name": self.profile_combo.currentText(),
            "create_missing": self.create_missing_cb.isChecked(),
            "create_levels": self.create_levels_cb.isChecked(),
            "create_spaces": self.create_spaces_cb.isChecked(),
            "lock_reference": self.lock_reference_cb.isChecked(),
            "reference_target": self.reference_target_combo.currentText(),
            "create_electrical_defaults": self.create_electrical_defaults_cb.isChecked(),
            "apply_cad_scale": self.apply_scale_cb.isChecked(),
            "cad_scale_factor": scale_factor,
            "base_mode": self.base_mode_combo.currentText(),
            "base_point": (self.base_x.value(), self.base_y.value(), self.base_z.value()),
            "north_angle": self.north_angle.value(),
            "use_shared_coordinates": self.shared_coords_cb.isChecked(),
            "detect_surfaces": self.detect_surfaces_cb.isChecked(),
            "use_terrain_surface": self.use_terrain_cb.isChecked(),
            "surface_offset": self.surface_offset.value(),
            "standard": self.standard_in.text().strip() or "NBR 5410",
            "voltage_scope": self.scope_in.text().strip() or "BT/MT ate 35 kV",
            "levels": [
                ("Nivel Terreo", self.level0.value()),
                ("Nivel 01", self.level1.value()),
                ("Nivel 02", self.level2.value()),
            ],
            "socket_heights": {
                "low": self.low_h.value(),
                "medium": self.mid_h.value(),
                "high": self.high_h.value(),
            },
        }

    def refresh_reference_targets(self):
        profile = PROJECT_PROFILES.get(self.profile_combo.currentText(), PROJECT_PROFILES["Generico"])
        items = ["Automatico / primeiro nivel ou setor"]
        items.extend([label for label, _ in DEFAULT_LEVELS])
        items.extend(profile.get("groups", []))
        current = self.reference_target_combo.currentText()
        self.reference_target_combo.clear()
        self.reference_target_combo.addItems(items)
        if current:
            self.reference_target_combo.setCurrentText(current)


def ask_setup_config(source):
    if not QtWidgets:
        return {
            "source": source,
            "file_path": "",
            "profile_name": list(PROJECT_PROFILES.keys())[0],
            "create_missing": True,
            "create_levels": True,
            "create_spaces": True,
            "lock_reference": source in ["CAD", "IFC"],
            "reference_target": "Automatico / primeiro nivel ou setor",
            "create_electrical_defaults": True,
            "apply_cad_scale": False,
            "cad_scale_factor": 1.0,
            "base_mode": "Usar origem do arquivo",
            "base_point": (0.0, 0.0, 0.0),
            "north_angle": 0.0,
            "use_shared_coordinates": True,
            "detect_surfaces": True,
            "use_terrain_surface": source in ["IFC", "FreeCAD"],
            "surface_offset": 5.0,
            "standard": "NBR 5410",
            "voltage_scope": "BT/MT ate 35 kV",
            "levels": DEFAULT_LEVELS,
            "socket_heights": {"low": 300.0, "medium": 1100.0, "high": 2200.0},
        }
    dialog = SetupConfigDialog(source)
    if dialog.exec_() != QtWidgets.QDialog.Accepted:
        return None
    return dialog.config()


def _add_child(parent, child):
    if not parent or not child:
        return
    try:
        parent.addObject(child)
    except Exception:
        pass


def ensure_site(doc, parent=None):
    site = _find_first(doc, _is_site_object)
    if not site:
        try:
            arch = _arch()
            if not arch:
                raise RuntimeError("Arch indisponivel")
            site = arch.makeSite()
        except Exception:
            site = doc.addObject("App::DocumentObjectGroup", "Sitio_Projeto")
        site.Label = "Sitio - Projeto"
        _ensure_property(site, "App::PropertyString", "BIMRole", "BIM_Contexto", "Site")
    _add_child(parent, site)
    return site


def ensure_building(doc, site=None):
    building = _find_first(doc, _is_building_object)
    if not building:
        try:
            arch = _arch()
            if not arch:
                raise RuntimeError("Arch indisponivel")
            building = arch.makeBuilding()
        except Exception:
            building = doc.addObject("App::DocumentObjectGroup", "Edificacao_Principal")
        building.Label = "Edificacao - Principal"
        _ensure_property(building, "App::PropertyString", "BIMRole", "BIM_Contexto", "Building")
    _add_child(site, building)
    return building


def create_default_levels(doc, parent=None, default_levels=None):
    created = []
    for label, elevation in (default_levels or DEFAULT_LEVELS):
        if any(obj.Label == label for obj in doc.Objects):
            continue
        try:
            arch = _arch()
            if not arch:
                raise RuntimeError("Arch indisponivel")
            obj = arch.makeBuildingPart()
        except Exception:
            obj = doc.addObject("App::DocumentObjectGroup", label.replace(" ", "_"))
        obj.Label = label
        try:
            obj.Placement.Base.z = elevation
        except Exception:
            pass
        _ensure_property(obj, "App::PropertyLength", "Elevation", "BIM_Nivel", elevation)
        try:
            if hasattr(obj, "IfcType"):
                obj.IfcType = "Building Storey"
        except Exception:
            pass
        if parent:
            try:
                parent.addObject(obj)
            except Exception:
                pass
        created.append(obj)
    return created


def create_default_spaces(doc, levels, parent=None):
    created = []
    for level in levels:
        label = f"Espaco Geral - {level.Label}"
        if any(obj.Label == label for obj in doc.Objects):
            continue
        obj = doc.addObject("App::DocumentObjectGroup", label.replace(" ", "_"))
        obj.Label = label
        _ensure_property(obj, "App::PropertyString", "BIMRole", "BIM_Espaco", "IfcSpace")
        _ensure_property(obj, "App::PropertyString", "ReferenceLevel", "BIM_Espaco", level.Label)
        _ensure_property(obj, "App::PropertyLength", "LevelElevation", "BIM_Espaco", _level_elevation(level))
        _add_child(parent, obj)
        _add_child(level, obj)
        created.append(obj)
    return created


def create_profile_groups(doc, profile_name, parent):
    profile = PROJECT_PROFILES.get(profile_name, PROJECT_PROFILES["Generico"])
    groups = {}
    for label in profile.get("groups", []):
        groups[label] = _ensure_group(doc, label, parent)
    return groups


def create_electrical_defaults(doc, profile_name, groups):
    defaults = PROFILE_ELECTRICAL_DEFAULTS.get(profile_name, PROFILE_ELECTRICAL_DEFAULTS["Generico"])
    first_panel = defaults.get("panels", [""])[0] if defaults.get("panels") else ""
    for panel_name in defaults.get("panels", []):
        panel = ensure_panel_object(doc, panel_name, groups.get("Quadros"))
        _ensure_property(panel, "App::PropertyString", "VoltageScope", "BIM_Eletrica", "BT/MT ate 35 kV")

    for circuit_name in defaults.get("circuits", []):
        circuit = ensure_circuit_object(doc, circuit_name, groups.get("Circuitos"), first_panel)
        _ensure_property(circuit, "App::PropertyString", "ProjectProfile", "BIM_Eletrica", profile_name)


def apply_automation_defaults(project, profile_name):
    defaults = PROFILE_AUTOMATION_DEFAULTS.get(profile_name)
    if not defaults:
        return
    for name, value in defaults.items():
        _ensure_property(project, "App::PropertyString", name, "BIM_Automacao", value)


def get_panel_objects(doc):
    return [obj for obj in doc.Objects if getattr(obj, "BIMRole", "") == "PanelBoard"]


def get_circuit_objects(doc):
    return [obj for obj in doc.Objects if getattr(obj, "BIMRole", "") == "Circuit"]


def is_library_matrix(obj):
    role = getattr(obj, "BIMRole", "")
    if role in ["SocketMatrix", "LibraryMatrix", "FamilyMatrix"]:
        return True
    try:
        if bool(getattr(obj, "IsLibraryMatrix", False)):
            return True
    except Exception:
        pass
    name = f"{getattr(obj, 'Name', '')} {getattr(obj, 'Label', '')}"
    return "Matriz_" in name or "Matrix_" in name


def get_load_objects(doc):
    loads = []
    for obj in doc.Objects:
        if is_library_matrix(obj):
            continue
        if hasattr(obj, "CircuitNumber") or hasattr(obj, "CircuitObject") or hasattr(obj, "PanelBoard"):
            if getattr(obj, "BIMRole", "") not in ["Circuit", "PanelBoard"]:
                loads.append(obj)
    return loads


def _parse_voltage(value):
    text = str(value or "127V").replace("V", "").replace("v", "").strip()
    if "/" in text:
        text = text.split("/", 1)[0]
    try:
        return max(float(text), 1.0)
    except Exception:
        return 127.0


def _suggest_breaker(current):
    for breaker in [10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 630]:
        if current <= breaker:
            return f"{breaker}A"
    return ">630A"


def _suggest_cable(current):
    table = [(15, "1.5 mm2"), (21, "2.5 mm2"), (28, "4 mm2"), (36, "6 mm2"), (50, "10 mm2"),
             (68, "16 mm2"), (89, "25 mm2"), (111, "35 mm2"), (134, "50 mm2"),
             (171, "70 mm2"), (207, "95 mm2"), (239, "120 mm2"), (299, "185 mm2")]
    for ampacity, cable in table:
        if current <= ampacity:
            return cable
    return "dimensionar"


def _parse_amp(value):
    try:
        return float(str(value or "").replace("A", "").replace("a", "").strip())
    except Exception:
        return 0.0


def recalculate_circuit_loads(doc=None):
    doc = doc or FreeCAD.ActiveDocument
    if not doc:
        return {}

    totals = {}
    counts = {}
    for circuit in get_circuit_objects(doc):
        totals[circuit.Name] = 0.0
        counts[circuit.Name] = 0

    for load in get_load_objects(doc):
        circuit_obj_name = getattr(load, "CircuitObject", "")
        circuit_number = getattr(load, "CircuitNumber", "")
        panel = getattr(load, "PanelBoard", "")

        target = None
        if circuit_obj_name:
            target = doc.getObject(circuit_obj_name)
        if not target and circuit_number:
            for circuit in get_circuit_objects(doc):
                if getattr(circuit, "CircuitNumber", "") == circuit_number and getattr(circuit, "PanelBoard", "") in ["", panel]:
                    target = circuit
                    break
        if not target:
            continue

        power = getattr(load, "Power", 0.0)
        try:
            power = float(power.Value if hasattr(power, "Value") else power)
        except Exception:
            power = 0.0

        totals[target.Name] = totals.get(target.Name, 0.0) + power
        counts[target.Name] = counts.get(target.Name, 0) + 1

    for circuit in get_circuit_objects(doc):
        _ensure_property(circuit, "App::PropertyFloat", "ConnectedLoad", "BIM_Cargas", totals.get(circuit.Name, 0.0))
        _ensure_property(circuit, "App::PropertyInteger", "PointCount", "BIM_Cargas", counts.get(circuit.Name, 0))
        connected = totals.get(circuit.Name, 0.0)
        demand = getattr(circuit, "DemandFactor", 1.0)
        try:
            demand = float(demand.Value if hasattr(demand, "Value") else demand)
        except Exception:
            demand = 1.0
        voltage = _parse_voltage(getattr(circuit, "Voltage", "127V"))
        current = connected / voltage if voltage else 0.0
        design_current = current * demand
        _ensure_property(circuit, "App::PropertyFloat", "CurrentA", "BIM_Calculo", current)
        _ensure_property(circuit, "App::PropertyFloat", "DesignCurrent", "BIM_Calculo", design_current)
        _ensure_property(circuit, "App::PropertyString", "SuggestedBreaker", "BIM_Calculo", _suggest_breaker(design_current))
        _ensure_property(circuit, "App::PropertyString", "SuggestedCableSection", "BIM_Calculo", _suggest_cable(design_current))
        _ensure_property(circuit, "App::PropertyFloat", "VoltageDropEstimate", "BIM_Calculo", 0.0)

    doc.recompute()
    return totals


def validate_electrical_project(doc=None):
    doc = doc or FreeCAD.ActiveDocument
    issues = []
    if not doc:
        return ["Nenhum documento ativo."]

    panels = get_panel_objects(doc)
    circuits = get_circuit_objects(doc)
    loads = get_load_objects(doc)

    if not panels:
        issues.append("Nenhum quadro BIM encontrado.")
    if not circuits:
        issues.append("Nenhum circuito BIM encontrado.")

    panel_names = set(panel.Label for panel in panels)
    for circuit in circuits:
        panel = getattr(circuit, "PanelBoard", "")
        if not panel:
            issues.append(f"Circuito sem quadro: {circuit.Label}")
        elif panel not in panel_names:
            issues.append(f"Circuito {circuit.Label} referencia quadro inexistente: {panel}")

    for load in loads:
        label = getattr(load, "Label", load.Name)
        if not getattr(load, "PanelBoard", ""):
            issues.append(f"Ponto sem quadro: {label}")
        if not getattr(load, "CircuitNumber", ""):
            issues.append(f"Ponto sem circuito: {label}")

    recalculate_circuit_loads(doc)
    for circuit in circuits:
        load = getattr(circuit, "ConnectedLoad", 0.0)
        try:
            load = float(load.Value if hasattr(load, "Value") else load)
        except Exception:
            load = 0.0
        if load <= 0:
            issues.append(f"Circuito sem cargas vinculadas: {circuit.Label}")
        breaker = _parse_amp(getattr(circuit, "Breaker", ""))
        design_current = getattr(circuit, "DesignCurrent", 0.0)
        try:
            design_current = float(design_current.Value if hasattr(design_current, "Value") else design_current)
        except Exception:
            design_current = 0.0
        if breaker and design_current > breaker:
            issues.append(f"Circuito {circuit.Label} acima do disjuntor: {design_current:.1f}A > {breaker:.1f}A")

    return issues


class CircuitManagerDialog(QtWidgets.QDialog if QtWidgets else object):
    def __init__(self, doc):
        super(CircuitManagerDialog, self).__init__()
        self.doc = doc
        self.setWindowTitle(tr("Quadros e Circuitos"))
        self.resize(620, 420)

        layout = QtWidgets.QVBoxLayout(self)
        lists = QtWidgets.QHBoxLayout()
        self.panel_list = QtWidgets.QListWidget()
        self.circuit_list = QtWidgets.QListWidget()
        lists.addWidget(self.panel_list)
        lists.addWidget(self.circuit_list)
        layout.addLayout(lists)

        buttons = QtWidgets.QHBoxLayout()
        self.add_panel_btn = QtWidgets.QPushButton(tr("Novo quadro"))
        self.add_circuit_btn = QtWidgets.QPushButton(tr("Novo circuito"))
        self.recalc_btn = QtWidgets.QPushButton(tr("Recalcular cargas"))
        self.validate_btn = QtWidgets.QPushButton(tr("Validar"))
        self.close_btn = QtWidgets.QPushButton(tr("Fechar"))
        for btn in [self.add_panel_btn, self.add_circuit_btn, self.recalc_btn, self.validate_btn, self.close_btn]:
            buttons.addWidget(btn)
        layout.addLayout(buttons)

        self.add_panel_btn.clicked.connect(self.add_panel)
        self.add_circuit_btn.clicked.connect(self.add_circuit)
        self.recalc_btn.clicked.connect(self.recalculate)
        self.validate_btn.clicked.connect(self.validate)
        self.close_btn.clicked.connect(self.accept)
        self.refresh()

    def refresh(self):
        self.panel_list.clear()
        self.circuit_list.clear()
        for panel in get_panel_objects(self.doc):
            self.panel_list.addItem(panel.Label)
        for circuit in get_circuit_objects(self.doc):
            load = getattr(circuit, "ConnectedLoad", 0.0)
            count = getattr(circuit, "PointCount", 0)
            try:
                load = float(load.Value if hasattr(load, "Value") else load)
            except Exception:
                load = 0.0
            self.circuit_list.addItem(f"{circuit.Label} | {getattr(circuit, 'PanelBoard', '')} | {load:.0f} VA | {count} pts")

    def add_panel(self):
        name, ok = QtWidgets.QInputDialog.getText(self, tr("Novo quadro"), tr("Nome do quadro:"))
        if ok and name:
            parent = _find_group(self.doc, "Quadros")
            ensure_panel_object(self.doc, str(name), parent)
            self.doc.recompute()
            self.refresh()

    def add_circuit(self):
        panel = ""
        selected = self.panel_list.currentItem()
        if selected:
            panel = selected.text()
        name, ok = QtWidgets.QInputDialog.getText(self, tr("Novo circuito"), tr("Nome do circuito:"))
        if ok and name:
            parent = _find_group(self.doc, "Circuitos")
            ensure_circuit_object(self.doc, str(name), parent, panel)
            self.doc.recompute()
            self.refresh()

    def recalculate(self):
        recalculate_circuit_loads(self.doc)
        self.refresh()

    def validate(self):
        issues = validate_electrical_project(self.doc)
        msg = "\n".join(issues) if issues else "Nenhum problema basico encontrado."
        QtWidgets.QMessageBox.information(self, tr("Validacao Eletrica"), msg)


def find_reference_target(doc, config, groups, levels):
    target_label = config.get("reference_target", "")
    if target_label and not target_label.startswith("Automatico"):
        for obj in doc.Objects:
            if obj.Label == target_label:
                return obj
        for group in groups.values():
            if group.Label == target_label:
                return group
    if levels:
        return levels[0]
    return groups.get("Zonas e Setores") or groups.get("Referencias")


def apply_cad_scale(objects, scale_factor):
    if not objects or abs(scale_factor - 1.0) < 0.000001:
        return False
    try:
        import Draft
        Draft.scale(objects, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(scale_factor, scale_factor, scale_factor), copy=False)
        return True
    except Exception as e:
        FreeCAD.Console.PrintWarning(f"Nao foi possivel aplicar escala CAD automaticamente: {e}\n")
        return False


def apply_spatial_reference(objects, config):
    if not objects:
        return
    mode = config.get("base_mode", "Usar origem do arquivo")
    base = config.get("base_point", (0.0, 0.0, 0.0))
    angle = float(config.get("north_angle", 0.0))

    if mode.startswith("Usar origem") and abs(angle) < 0.000001:
        return

    if mode.startswith("Mover ponto base"):
        offset = FreeCAD.Vector(-base[0], -base[1], -base[2])
    elif mode.startswith("Aplicar deslocamento"):
        offset = FreeCAD.Vector(base[0], base[1], base[2])
    else:
        offset = FreeCAD.Vector(0, 0, 0)

    rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle)
    for obj in objects:
        try:
            placement = obj.Placement
            placement.Base = placement.Base + offset
            if abs(angle) >= 0.000001:
                placement.Rotation = rotation.multiply(placement.Rotation)
            obj.Placement = placement
        except Exception:
            pass


def prepare_base(source, config=None):
    config = config or ask_setup_config(source)
    if config is None:
        return None, {}, []
    profile_name = config.get("profile_name") or list(PROJECT_PROFILES.keys())[0]
    profile = PROJECT_PROFILES.get(profile_name, PROJECT_PROFILES["Generico"])
    doc = _ensure_doc()
    project = _ensure_group(doc, PROJECT_GROUP)
    groups = {name: _ensure_group(doc, name, project) for name in PROJECT_GROUPS}
    context = groups["Contexto BIM"]
    sector_parent = groups["Zonas e Setores"]

    create_missing = config.get("create_missing", True)
    site = None
    building = None
    if profile.get("site"):
        site = ensure_site(doc, context) if create_missing else _find_first(doc, _is_site_object)
        _add_child(context, site)
    if profile.get("building"):
        building = ensure_building(doc, site or context) if create_missing else _find_first(doc, _is_building_object)
        _add_child(site or context, building)
    create_profile_groups(doc, profile_name, sector_parent)
    if config.get("create_electrical_defaults", True):
        create_electrical_defaults(doc, profile_name, groups)

    levels = discover_levels(doc)
    if profile.get("levels") and config.get("create_levels", True) and not levels:
        create_default_levels(doc, groups["Niveis"], config.get("levels"))
        levels = discover_levels(doc)

    for level in levels:
        _add_child(groups["Niveis"], level)
        _add_child(building or site, level)

    spaces = discover_spaces(doc)
    if profile.get("spaces") and config.get("create_spaces", True) and not spaces:
        create_default_spaces(doc, levels, groups["Espacos"])
        spaces = discover_spaces(doc)
    else:
        for space in spaces:
            _add_child(groups["Espacos"], space)

    _ensure_property(project, "App::PropertyString", "BIMSource", "BIM_Projeto", source)
    _ensure_property(project, "App::PropertyString", "ProjectProfile", "BIM_Projeto", profile_name)
    _ensure_property(project, "App::PropertyString", "ElectricalStandard", "BIM_Projeto", config.get("standard", "NBR 5410"))
    _ensure_property(project, "App::PropertyString", "VoltageScope", "BIM_Projeto", config.get("voltage_scope", "BT/MT ate 35 kV"))
    base = config.get("base_point", (0.0, 0.0, 0.0))
    _ensure_property(project, "App::PropertyString", "SpatialReferenceMode", "BIM_ReferenciaEspacial", config.get("base_mode", "Usar origem do arquivo"))
    _ensure_property(project, "App::PropertyLength", "BasePointX", "BIM_ReferenciaEspacial", base[0])
    _ensure_property(project, "App::PropertyLength", "BasePointY", "BIM_ReferenciaEspacial", base[1])
    _ensure_property(project, "App::PropertyLength", "BasePointZ", "BIM_ReferenciaEspacial", base[2])
    _ensure_property(project, "App::PropertyAngle", "ProjectNorthAngle", "BIM_ReferenciaEspacial", config.get("north_angle", 0.0))
    _ensure_property(project, "App::PropertyBool", "UseSharedCoordinates", "BIM_ReferenciaEspacial", config.get("use_shared_coordinates", True))
    _ensure_property(project, "App::PropertyBool", "DetectSurfaces", "BIM_Superficies", config.get("detect_surfaces", True))
    _ensure_property(project, "App::PropertyBool", "UseTerrainSurface", "BIM_Superficies", config.get("use_terrain_surface", False))
    _ensure_property(project, "App::PropertyLength", "SurfaceOffset", "BIM_Superficies", config.get("surface_offset", 5.0))
    apply_automation_defaults(project, profile_name)
    heights = config.get("socket_heights", {})
    _ensure_property(project, "App::PropertyLength", "SocketLowHeight", "BIM_Projeto", heights.get("low", 300.0))
    _ensure_property(project, "App::PropertyLength", "SocketMediumHeight", "BIM_Projeto", heights.get("medium", 1100.0))
    _ensure_property(project, "App::PropertyLength", "SocketHighHeight", "BIM_Projeto", heights.get("high", 2200.0))

    doc.recompute()
    return doc, groups, levels


def import_reference_file(source, file_path):
    if not file_path:
        return []
    if not os.path.exists(file_path):
        FreeCAD.Console.PrintError(f"Arquivo nao encontrado: {file_path}\n")
        return []

    if source == "FreeCAD":
        opened = FreeCAD.openDocument(file_path)
        FreeCAD.setActiveDocument(opened.Name)
        return list(opened.Objects)

    doc = _ensure_doc()
    before = set(obj.Name for obj in doc.Objects)
    try:
        import ImportGui
        ImportGui.insert(file_path, doc.Name)
    except Exception:
        try:
            import importDXF
            importDXF.insert(file_path, doc.Name)
        except Exception as e:
            FreeCAD.Console.PrintError(f"Falha ao importar referencia {file_path}: {e}\n")
            return []

    return [obj for obj in doc.Objects if obj.Name not in before]


def mark_references(objects, source, config, groups, levels):
    if not objects:
        return 0

    doc = FreeCAD.ActiveDocument
    target = find_reference_target(doc, config, groups, levels) if doc else None
    default_level = target if target and _is_level_object(target) else (levels[0] if levels else None)
    default_level_name = target.Label if target else "Projeto"
    default_elevation = _level_elevation(default_level) if default_level else 0.0

    count = 0
    for obj in objects:
        _ensure_property(obj, "App::PropertyString", "ReferenceSource", "BIM_Referencia", source)
        _ensure_property(obj, "App::PropertyString", "ReferenceLevel", "BIM_Referencia", default_level_name)
        _ensure_property(obj, "App::PropertyLength", "LevelElevation", "BIM_Referencia", default_elevation)
        _ensure_property(obj, "App::PropertyString", "ReferenceTarget", "BIM_Referencia", default_level_name)
        _ensure_property(obj, "App::PropertyString", "OriginalFile", "BIM_Referencia", config.get("file_path", ""))
        _ensure_property(obj, "App::PropertyFloat", "DrawingScaleFactor", "BIM_Referencia", config.get("cad_scale_factor", 1.0))
        locked = config.get("lock_reference", True)
        _ensure_property(obj, "App::PropertyBool", "LockedReference", "BIM_Referencia", locked)
        if locked:
            try:
                obj.ViewObject.Selectable = False
            except Exception:
                pass
        try:
            groups["Referencias"].addObject(obj)
        except Exception:
            pass
        _add_child(target, obj)
        count += 1

    return count


def run_preparation(source):
    config = ask_setup_config(source)
    if config is None:
        return None, 0, 0

    imported = import_reference_file(source, config.get("file_path", ""))
    selected = list(FreeCADGui.Selection.getSelection())

    doc, groups, levels = prepare_base(source, config)
    if not doc:
        return None, 0, 0

    reference_objects = imported or selected
    if source == "CAD" and config.get("apply_cad_scale", False):
        apply_cad_scale(reference_objects, config.get("cad_scale_factor", 1.0))
    apply_spatial_reference(reference_objects, config)
    count = mark_references(reference_objects, source, config, groups, levels)
    doc.recompute()
    return doc, len(levels), count


class PrepareFromCAD:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "DrawingSheet.svg"),
            "MenuText": tr("Preparar Projeto por CAD"),
            "ToolTip": tr("Cria estrutura BIM elétrica e vincula a planta CAD selecionada como referência 2D"),
        }

    def Activated(self):
        doc, level_count, ref_count = run_preparation("CAD")
        if doc:
            FreeCAD.Console.PrintLog(f"Projeto eletrico BIM preparado por CAD. Niveis: {level_count}. Referencias: {ref_count}\n")


class PrepareFromIFC:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "IFCExport.svg"),
            "MenuText": tr("Preparar Projeto por IFC"),
            "ToolTip": tr("Usa níveis IFC/Arquitetura existentes e cria a estrutura elétrica BIM"),
        }

    def Activated(self):
        doc, level_count, ref_count = run_preparation("IFC")
        if doc:
            FreeCAD.Console.PrintLog(f"Projeto eletrico BIM preparado por IFC. Niveis: {level_count}. Referencias: {ref_count}\n")


class PrepareFromFreeCAD:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "StartProject.svg"),
            "MenuText": tr("Preparar Projeto FreeCAD"),
            "ToolTip": tr("Cria estrutura elétrica BIM usando o desenho/arquitetura nativa do FreeCAD"),
        }

    def Activated(self):
        doc, level_count, ref_count = run_preparation("FreeCAD")
        if doc:
            FreeCAD.Console.PrintLog(f"Projeto eletrico BIM preparado por desenho FreeCAD. Niveis: {level_count}. Referencias: {ref_count}\n")


class ManagePanelsCircuits:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Panel.svg"),
            "MenuText": tr("Gerenciar Quadros/Circuitos"),
            "ToolTip": tr("Cria, lista, valida e recalcula cargas de quadros e circuitos BIM"),
        }

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            return
        if not QtWidgets:
            FreeCAD.Console.PrintError("Qt indisponivel para abrir o gerenciador.\n")
            return
        dialog = CircuitManagerDialog(doc)
        dialog.exec_()


class RecalculateCircuitLoads:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "LoadSchedule.svg"),
            "MenuText": tr("Recalcular Cargas"),
            "ToolTip": tr("Soma as cargas dos pontos vinculados a cada circuito"),
        }

    def Activated(self):
        totals = recalculate_circuit_loads(FreeCAD.ActiveDocument)
        FreeCAD.Console.PrintLog(f"Cargas recalculadas para {len(totals)} circuitos.\n")


class ValidateElectricalProject:
    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Audit.svg"),
            "MenuText": tr("Validar Eletrica BIM"),
            "ToolTip": tr("Verifica vinculos basicos de quadros, circuitos e pontos eletricos"),
        }

    def Activated(self):
        issues = validate_electrical_project(FreeCAD.ActiveDocument)
        msg = "\n".join(issues) if issues else "Nenhum problema basico encontrado."
        FreeCAD.Console.PrintLog(msg + "\n")
        if QtWidgets:
            QtWidgets.QMessageBox.information(None, tr("Validacao Eletrica"), msg)


def export_point_schedule(path, doc=None):
    doc = doc or FreeCAD.ActiveDocument
    if not doc or not path:
        return 0
    fields = ["Name", "Label", "Type", "Level", "SpaceOrSector", "PanelBoard", "CircuitNumber", "Power", "Voltage", "MountingHeight", "FinalElevation"]
    rows = []
    for obj in get_load_objects(doc):
        power = getattr(obj, "Power", "")
        try:
            power = power.Value if hasattr(power, "Value") else power
        except Exception:
            pass
        rows.append({
            "Name": obj.Name,
            "Label": getattr(obj, "Label", obj.Name),
            "Type": getattr(obj, "CircuitType", getattr(obj, "BIMRole", "")),
            "Level": getattr(obj, "ReferenceLevel", ""),
            "SpaceOrSector": getattr(obj, "SpaceOrSector", ""),
            "PanelBoard": getattr(obj, "PanelBoard", ""),
            "CircuitNumber": getattr(obj, "CircuitNumber", ""),
            "Power": power,
            "Voltage": getattr(obj, "Voltage", ""),
            "MountingHeight": getattr(obj, "MountingHeight", ""),
            "FinalElevation": getattr(obj, "FinalElevation", ""),
        })
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


class BatchEditPointsDialog(QtWidgets.QDialog if QtWidgets else object):
    def __init__(self, doc, objects):
        super(BatchEditPointsDialog, self).__init__()
        self.doc = doc
        self.objects = objects
        self.setWindowTitle(tr("Editar Pontos em Lote"))
        self.resize(420, 220)
        layout = QtWidgets.QFormLayout(self)

        panels = [p.Label for p in get_panel_objects(doc)]
        circuits = [c.Label for c in get_circuit_objects(doc)]
        spaces = [o.Label for o in doc.Objects if getattr(o, "BIMRole", "") == "IfcSpace" or "Setor" in o.Label or "Ambiente" in o.Label]

        self.panel_combo = QtWidgets.QComboBox(); self.panel_combo.addItem("Manter"); self.panel_combo.addItems(panels)
        self.circuit_combo = QtWidgets.QComboBox(); self.circuit_combo.addItem("Manter"); self.circuit_combo.addItems(circuits)
        self.space_combo = QtWidgets.QComboBox(); self.space_combo.addItem("Manter"); self.space_combo.addItems(spaces)
        self.power = QtWidgets.QDoubleSpinBox(); self.power.setRange(-1, 10000000); self.power.setValue(-1)
        self.height = QtWidgets.QDoubleSpinBox(); self.height.setRange(-1, 100000); self.height.setValue(-1)
        layout.addRow("Quadro:", self.panel_combo)
        layout.addRow("Circuito:", self.circuit_combo)
        layout.addRow("Ambiente/Setor:", self.space_combo)
        layout.addRow("Potencia (-1 manter):", self.power)
        layout.addRow("Altura (-1 manter):", self.height)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def apply(self):
        panel = self.panel_combo.currentText()
        circuit_label = self.circuit_combo.currentText()
        space = self.space_combo.currentText()
        circuit_obj = ""
        circuit_number = ""
        if circuit_label != "Manter":
            for circuit in get_circuit_objects(self.doc):
                if circuit.Label == circuit_label:
                    circuit_obj = circuit.Name
                    circuit_number = getattr(circuit, "CircuitNumber", circuit.Label)
                    break
        for obj in self.objects:
            if panel != "Manter" and hasattr(obj, "PanelBoard"):
                obj.PanelBoard = panel
            if circuit_label != "Manter":
                if hasattr(obj, "CircuitObject"):
                    obj.CircuitObject = circuit_obj
                if hasattr(obj, "CircuitNumber"):
                    obj.CircuitNumber = circuit_number
            if space != "Manter" and hasattr(obj, "SpaceOrSector"):
                obj.SpaceOrSector = space
            if self.power.value() >= 0 and hasattr(obj, "Power"):
                obj.Power = self.power.value()
            if self.height.value() >= 0 and hasattr(obj, "MountingHeight"):
                obj.MountingHeight = self.height.value()
        recalculate_circuit_loads(self.doc)


class ExportPointSchedule:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "ExportCSV.svg"), "MenuText": tr("Exportar Tabela de Pontos"), "ToolTip": tr("Exporta pontos eletricos para CSV")}

    def Activated(self):
        if not QtWidgets:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(None, tr("Exportar tabela de pontos"), "tabela_pontos.csv", "CSV (*.csv)")
        count = export_point_schedule(path, FreeCAD.ActiveDocument)
        FreeCAD.Console.PrintLog(f"Tabela de pontos exportada: {count} itens.\n")


class BatchEditPoints:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "SmartTags.svg"), "MenuText": tr("Editar Pontos em Lote"), "ToolTip": tr("Altera quadro, circuito, ambiente, potencia e altura dos pontos selecionados")}

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        selection = [obj for obj in FreeCADGui.Selection.getSelection() if obj in get_load_objects(doc)]
        if not doc or not selection or not QtWidgets:
            FreeCAD.Console.PrintWarning("Selecione pontos eletricos para editar em lote.\n")
            return
        dialog = BatchEditPointsDialog(doc, selection)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            dialog.apply()


class ToggleSystemVisibility:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "Heatmap.svg"), "MenuText": tr("Filtrar Sistemas"), "ToolTip": tr("Alterna visibilidade por tipo de circuito")}

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not doc or not QtWidgets:
            return
        types = sorted(set(getattr(obj, "CircuitType", "") for obj in get_load_objects(doc) if getattr(obj, "CircuitType", "")))
        if not types:
            return
        item, ok = QtWidgets.QInputDialog.getItem(None, tr("Filtrar Sistemas"), tr("Mostrar apenas:"), ["Todos"] + types, 0, False)
        if not ok:
            return
        item = str(item)
        for obj in get_load_objects(doc):
            try:
                obj.ViewObject.Visibility = item == "Todos" or getattr(obj, "CircuitType", "") == item
            except Exception:
                pass


def _point_base(obj):
    try:
        return obj.Placement.Base
    except Exception:
        return FreeCAD.Vector(0, 0, 0)


def create_preliminary_routes(doc=None):
    doc = doc or FreeCAD.ActiveDocument
    if not doc:
        return 0
    route_group = _ensure_group(doc, "Rotas Preliminares", _find_group(doc, PROJECT_GROUP))
    count = 0
    try:
        import Draft
    except Exception:
        Draft = None

    panels = {panel.Label: panel for panel in get_panel_objects(doc)}
    for circuit in get_circuit_objects(doc):
        panel = panels.get(getattr(circuit, "PanelBoard", ""))
        loads = []
        for obj in get_load_objects(doc):
            if getattr(obj, "CircuitObject", "") == circuit.Name or (
                getattr(obj, "CircuitNumber", "") == getattr(circuit, "CircuitNumber", "") and
                getattr(obj, "PanelBoard", "") == getattr(circuit, "PanelBoard", "")
            ):
                loads.append(obj)
        if not panel or not loads:
            continue
        pts = [_point_base(panel)] + [_point_base(load) for load in loads]
        try:
            if Draft:
                wire = Draft.make_wire(pts, closed=False)
            else:
                wire = doc.addObject("Part::Feature", _safe_name("Rota_" + circuit.Label))
            wire.Label = f"Rota Preliminar - {circuit.Label}"
            _ensure_property(wire, "App::PropertyString", "BIMRole", "BIM_Rota", "PreliminaryRoute")
            _ensure_property(wire, "App::PropertyString", "CircuitNumber", "BIM_Rota", getattr(circuit, "CircuitNumber", ""))
            _ensure_property(wire, "App::PropertyString", "PanelBoard", "BIM_Rota", getattr(circuit, "PanelBoard", ""))
            _add_child(route_group, wire)
            count += 1
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Falha ao criar rota de {circuit.Label}: {e}\n")
    doc.recompute()
    return count


def create_symbol_legend(doc=None):
    doc = doc or FreeCAD.ActiveDocument
    if not doc:
        return 0
    legend = _ensure_group(doc, "Legenda Eletrica", _find_group(doc, PROJECT_GROUP))
    used = sorted(set(getattr(obj, "CircuitType", getattr(obj, "BIMRole", "")) for obj in get_load_objects(doc)))
    count = 0
    for item in used:
        if not item:
            continue
        label = f"Legenda - {item}"
        obj = _ensure_group(doc, label, legend)
        _ensure_property(obj, "App::PropertyString", "SymbolType", "BIM_Legenda", item)
        count += 1
    doc.recompute()
    return count


def generate_html_report(path, doc=None):
    doc = doc or FreeCAD.ActiveDocument
    if not doc or not path:
        return False
    issues = validate_electrical_project(doc)
    recalculate_circuit_loads(doc)
    panels = get_panel_objects(doc)
    circuits = get_circuit_objects(doc)
    loads = get_load_objects(doc)

    def esc(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    rows = []
    for obj in loads:
        rows.append(
            f"<tr><td>{esc(obj.Label)}</td><td>{esc(getattr(obj, 'ReferenceLevel', ''))}</td>"
            f"<td>{esc(getattr(obj, 'SpaceOrSector', ''))}</td><td>{esc(getattr(obj, 'PanelBoard', ''))}</td>"
            f"<td>{esc(getattr(obj, 'CircuitNumber', ''))}</td><td>{esc(getattr(obj, 'Power', ''))}</td></tr>"
        )

    circuit_rows = []
    for circuit in circuits:
        circuit_rows.append(
            f"<tr><td>{esc(circuit.Label)}</td><td>{esc(getattr(circuit, 'PanelBoard', ''))}</td>"
            f"<td>{esc(getattr(circuit, 'ConnectedLoad', 0))}</td><td>{esc(getattr(circuit, 'DesignCurrent', 0))}</td>"
            f"<td>{esc(getattr(circuit, 'SuggestedBreaker', ''))}</td><td>{esc(getattr(circuit, 'SuggestedCableSection', ''))}</td></tr>"
        )

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Relatorio Eletrico BIM</title>
<style>body{{font-family:Arial,sans-serif;margin:32px}} table{{border-collapse:collapse;width:100%;margin:16px 0}} td,th{{border:1px solid #ccc;padding:6px}} th{{background:#eee}} .warn{{color:#9a4b00}}</style>
</head><body>
<h1>Relatorio Eletrico BIM</h1>
<p>Documento: {esc(doc.Name)}</p>
<h2>Resumo</h2>
<ul><li>Quadros: {len(panels)}</li><li>Circuitos: {len(circuits)}</li><li>Pontos: {len(loads)}</li></ul>
<h2>Alertas</h2>
<ul>{''.join('<li class="warn">'+esc(i)+'</li>' for i in issues) if issues else '<li>Nenhum problema basico encontrado.</li>'}</ul>
<h2>Circuitos</h2>
<table><tr><th>Circuito</th><th>Quadro</th><th>Carga</th><th>Corrente projeto</th><th>Disjuntor sugerido</th><th>Cabo sugerido</th></tr>{''.join(circuit_rows)}</table>
<h2>Pontos</h2>
<table><tr><th>Ponto</th><th>Nivel</th><th>Ambiente/Setor</th><th>Quadro</th><th>Circuito</th><th>Potencia</th></tr>{''.join(rows)}</table>
</body></html>"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return True


class TemplateEditorDialog(QtWidgets.QDialog if QtWidgets else object):
    def __init__(self):
        super(TemplateEditorDialog, self).__init__()
        self.setWindowTitle(tr("Editor de Templates TOML"))
        self.resize(760, 520)
        layout = QtWidgets.QVBoxLayout(self)
        self.file_combo = QtWidgets.QComboBox()
        self.text = QtWidgets.QPlainTextEdit()
        buttons = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton(tr("Salvar"))
        self.reload_btn = QtWidgets.QPushButton(tr("Recarregar"))
        self.close_btn = QtWidgets.QPushButton(tr("Fechar"))
        buttons.addWidget(self.save_btn); buttons.addWidget(self.reload_btn); buttons.addWidget(self.close_btn)
        layout.addWidget(self.file_combo)
        layout.addWidget(self.text)
        layout.addLayout(buttons)
        self.save_btn.clicked.connect(self.save)
        self.reload_btn.clicked.connect(self.load_selected)
        self.close_btn.clicked.connect(self.accept)
        self.file_combo.currentIndexChanged.connect(self.load_selected)
        self.populate()

    def populate(self):
        self.file_combo.clear()
        if os.path.isdir(PROFILE_TEMPLATE_DIR):
            for fname in sorted(os.listdir(PROFILE_TEMPLATE_DIR)):
                if fname.endswith(".toml"):
                    self.file_combo.addItem(fname)

    def current_path(self):
        return os.path.join(PROFILE_TEMPLATE_DIR, self.file_combo.currentText())

    def load_selected(self):
        path = self.current_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                self.text.setPlainText(fh.read())

    def save(self):
        path = self.current_path()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.text.toPlainText())
        FreeCAD.Console.PrintLog(f"Template salvo: {path}\n")


class CreatePreliminaryRoutes:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "Conduit.svg"), "MenuText": tr("Rotas Preliminares"), "ToolTip": tr("Cria rotas simples por circuito")}

    def Activated(self):
        count = create_preliminary_routes(FreeCAD.ActiveDocument)
        FreeCAD.Console.PrintLog(f"Rotas preliminares criadas: {count}\n")


class GenerateSymbolLegend:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "Legend.svg"), "MenuText": tr("Gerar Legenda"), "ToolTip": tr("Gera legenda dos sistemas usados")}

    def Activated(self):
        count = create_symbol_legend(FreeCAD.ActiveDocument)
        FreeCAD.Console.PrintLog(f"Itens de legenda criados: {count}\n")


class GenerateElectricalReport:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "Report.svg"), "MenuText": tr("Relatorio HTML"), "ToolTip": tr("Gera relatorio HTML do projeto eletrico")}

    def Activated(self):
        if not QtWidgets:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(None, tr("Salvar relatorio"), "relatorio_eletrico.html", "HTML (*.html)")
        if generate_html_report(path, FreeCAD.ActiveDocument):
            FreeCAD.Console.PrintLog(f"Relatorio gerado: {path}\n")


class EditProjectTemplates:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "GlobalSettings.svg"), "MenuText": tr("Editar Templates"), "ToolTip": tr("Edita templates TOML de perfis de projeto")}

    def Activated(self):
        if not QtWidgets:
            return
        dialog = TemplateEditorDialog()
        dialog.exec_()


class VisualValidation:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "Auditor.svg"), "MenuText": tr("Validacao Visual"), "ToolTip": tr("Pinta pontos com problemas de vinculo")}

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            return
        for obj in get_load_objects(doc):
            try:
                if not getattr(obj, "CircuitNumber", ""):
                    obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
                elif not getattr(obj, "PanelBoard", ""):
                    obj.ViewObject.ShapeColor = (1.0, 0.55, 0.0)
                else:
                    obj.ViewObject.ShapeColor = (0.9, 0.9, 0.9)
            except Exception:
                pass


class CreateSpaceOrSector:
    def GetResources(self):
        return {"Pixmap": os.path.join(ICON_DIR, "Structure.svg"), "MenuText": tr("Criar Ambiente/Setor"), "ToolTip": tr("Cria ambiente ou setor para associar aos pontos")}

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not doc or not QtWidgets:
            return
        name, ok = QtWidgets.QInputDialog.getText(None, tr("Novo Ambiente/Setor"), tr("Nome:"))
        if not ok or not name:
            return
        parent = _ensure_group(doc, "Espacos", _find_group(doc, PROJECT_GROUP))
        obj = _ensure_group(doc, str(name), parent)
        _ensure_property(obj, "App::PropertyString", "BIMRole", "BIM_Espaco", "IfcSpace")
        doc.recompute()
