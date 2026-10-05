import os
import re
import shutil

import FreeCAD

from EletricaLogic.i18n import tr

try:
    from PySide import QtCore, QtWidgets
except ImportError:
    try:
        from PySide import QtCore, QtGui as QtWidgets
    except ImportError:
        try:
            from PySide2 import QtCore, QtWidgets
        except ImportError:
            QtCore = None
            QtWidgets = None


ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Icons")
WORKBENCH_DIR = os.path.dirname(os.path.dirname(__file__))
LIBRARY_3D_DIR = os.path.join(WORKBENCH_DIR, "Library", "3D")
TOMADAS_DIR = os.path.join(LIBRARY_3D_DIR, "Tomadas")


def _slug(text):
    value = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or "familia"))
    return "_".join(part for part in value.split("_") if part) or "familia"


def _infer_family_from_source(source):
    source = str(source or "").replace("\\", "/").strip("/")
    base = os.path.splitext(os.path.basename(source))[0]
    text = base.lower()
    source_text = source.lower()
    is_modular = "conjuntos_modulares" in source_text or "conjunto" in source_text
    is_switch = "interruptor" in source_text or "/interruptores/" in f"/{source_text}" or "_s" in text
    is_socket = "tomada" in source_text or "/tomadas/" in f"/{source_text}" or "_t" in text
    socket_count = 0
    switch_count = 0
    composition = ""
    match = re.search(r"t(\d+)\s*[-_]\s*s(\d+)", text)
    if match:
        socket_count = int(match.group(1))
        switch_count = int(match.group(2))
        composition = f"T{socket_count}-S{switch_count}"
        is_modular = True
    elif is_socket:
        socket_count = 1
    elif is_switch:
        switch_count = 1

    if is_modular:
        module_count = max(1, socket_count + switch_count)
        modules = f"{module_count} Modulos" if module_count > 1 else "1 Modulo"
    elif "tripla" in text or "_t3" in text or "_s3" in text:
        modules = "3 Modulos"
    elif "dupla" in text or "_t2" in text or "_s2" in text:
        modules = "2 Modulos"
    else:
        modules = "1 Modulo"
    amperage = "" if is_switch else "20A" if "20a" in text else "10A"
    count = 3 if modules.startswith("3") else 2 if modules.startswith("2") else 1
    power = 0.0 if is_switch and not is_modular else (600.0 if amperage == "20A" else 100.0) * max(1, socket_count or count)
    return {
        "id": _slug(base),
        "name": base.replace("_", " "),
        "category": "Conjunto Modular" if is_modular else "Interruptor" if is_switch else "Tomada" if is_socket else "Equipamento",
        "discipline": "Eletrica",
        "ifc_class": "IfcDistributionElement" if is_modular else "IfcSwitchingDevice" if is_switch else "IfcFlowTerminal",
        "source_3d": source,
        "source_2d": "",
        "modules": modules,
        "amperage": amperage,
        "voltage": "127V",
        "power": power,
        "apparent_power_va": power,
        "active_power_w": power,
        "power_factor": 1.0,
        "demand_factor": 1.0,
        "phase": "R",
        "load_classification": "Misto" if is_modular else "Iluminacao" if is_switch else "TUG",
        "socket_application": "",
        "composition": composition,
        "socket_count": socket_count,
        "switch_count": switch_count,
        "ip_rating": "IP20",
        "electrical_standard": "NBR 5410",
        "height_type": "Media (1100mm)",
        "mounting_height": 1100.0,
        "manufacturer": "",
        "model": "",
        "catalog_code": "",
        "description": "",
    }


def _scan_family_files():
    families = []
    if not os.path.isdir(LIBRARY_3D_DIR):
        return families
    for root, dirs, files in os.walk(LIBRARY_3D_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".") and "backup" not in d.lower()]
        for fname in sorted(files):
            if not fname.lower().endswith(".fcstd"):
                continue
            rel = os.path.relpath(os.path.join(root, fname), LIBRARY_3D_DIR)
            families.append(_infer_family_from_source(rel))
    return families


def _import_family_file(path, category="Tomada"):
    if not path or not os.path.exists(path):
        return None
    target_dir = TOMADAS_DIR if category == "Tomada" else os.path.join(LIBRARY_3D_DIR, category)
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, os.path.basename(path))
    name, ext = os.path.splitext(target)
    count = 2
    while os.path.exists(target):
        target = f"{name}_{count}{ext}"
        count += 1
    shutil.copy2(path, target)
    rel = os.path.relpath(target, LIBRARY_3D_DIR)
    return _infer_family_from_source(rel)


def _import_family_file_to_folder(path, folder):
    if not path or not os.path.exists(path):
        return None
    folder = str(folder or "").strip().replace("\\", os.sep).replace("/", os.sep)
    target_dir = os.path.join(LIBRARY_3D_DIR, folder) if folder else TOMADAS_DIR
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, os.path.basename(path))
    name, ext = os.path.splitext(target)
    count = 2
    while os.path.exists(target):
        target = f"{name}_{count}{ext}"
        count += 1
    shutil.copy2(path, target)
    rel = os.path.relpath(target, LIBRARY_3D_DIR)
    return _infer_family_from_source(rel)


def _family_full_path(source):
    source = str(source or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source):
        return source
    return os.path.join(LIBRARY_3D_DIR, source)


def _set_fcstd_property(obj, prop_type, name, group, value):
    try:
        if not hasattr(obj, name):
            obj.addProperty(prop_type, name, group)
        setattr(obj, name, value)
    except Exception:
        pass


def _write_family_properties_to_fcstd(family):
    path = _family_full_path(family.get("source_3d", ""))
    if not os.path.exists(path):
        return False
    previous_doc_name = FreeCAD.ActiveDocument.Name if FreeCAD.ActiveDocument else None
    doc = FreeCAD.openDocument(path, True, True)
    try:
        target = None
        for obj in doc.Objects:
            try:
                if hasattr(obj, "Shape") and obj.Shape and not obj.Shape.isNull():
                    target = obj
                    break
            except Exception:
                pass
        if target is None and doc.Objects:
            target = doc.Objects[0]
        if target is None:
            return False

        _set_fcstd_property(target, "App::PropertyString", "FamilyName", "BIM_Familia", family.get("name", ""))
        _set_fcstd_property(target, "App::PropertyString", "FamilyCategory", "BIM_Familia", family.get("category", ""))
        _set_fcstd_property(target, "App::PropertyString", "IFC_Class", "BIM_Familia", family.get("ifc_class", "IfcFlowTerminal"))
        _set_fcstd_property(target, "App::PropertyString", "Modules", "BIM_Familia", family.get("modules", "1 Modulo"))
        _set_fcstd_property(target, "App::PropertyString", "Amperage", "BIM_Familia", family.get("amperage", "10A"))
        _set_fcstd_property(target, "App::PropertyString", "Composition", "BIM_Composicao", family.get("composition", ""))
        _set_fcstd_property(target, "App::PropertyInteger", "SocketCount", "BIM_Composicao", int(family.get("socket_count", 0) or 0))
        _set_fcstd_property(target, "App::PropertyInteger", "SwitchCount", "BIM_Composicao", int(family.get("switch_count", 0) or 0))
        _set_fcstd_property(target, "App::PropertyString", "TipoBIM", "BIM_Classificacao", "ModularAssembly" if family.get("category") == "Conjunto Modular" else family.get("category", ""))
        _set_fcstd_property(target, "App::PropertyString", "Voltage", "BIM_Engenharia", family.get("voltage", "127V"))
        _set_fcstd_property(target, "App::PropertyFloat", "Power", "BIM_Engenharia", float(family.get("power", 0.0) or 0.0))
        _set_fcstd_property(target, "App::PropertyFloat", "ApparentPowerVA", "BIM_Engenharia", float(family.get("apparent_power_va", family.get("power", 0.0)) or 0.0))
        _set_fcstd_property(target, "App::PropertyFloat", "ActivePowerW", "BIM_Engenharia", float(family.get("active_power_w", 0.0) or 0.0))
        _set_fcstd_property(target, "App::PropertyFloat", "PowerFactor", "BIM_Engenharia", float(family.get("power_factor", 1.0) or 1.0))
        _set_fcstd_property(target, "App::PropertyFloat", "DemandFactor", "BIM_Engenharia", float(family.get("demand_factor", 1.0) or 1.0))
        _set_fcstd_property(target, "App::PropertyString", "Phase", "BIM_Engenharia", family.get("phase", "R"))
        _set_fcstd_property(target, "App::PropertyString", "LoadClassification", "BIM_Engenharia", family.get("load_classification", "TUG"))
        _set_fcstd_property(target, "App::PropertyString", "SocketApplication", "BIM_Familia", family.get("socket_application", ""))
        _set_fcstd_property(target, "App::PropertyString", "IP_Rating", "BIM_Familia", family.get("ip_rating", ""))
        _set_fcstd_property(target, "App::PropertyString", "ElectricalStandard", "BIM_Familia", family.get("electrical_standard", "NBR 5410"))
        _set_fcstd_property(target, "App::PropertyString", "HeightType", "BIM_Posicionamento", family.get("height_type", "Media (1100mm)"))
        _set_fcstd_property(target, "App::PropertyLength", "MountingHeight", "BIM_Posicionamento", float(family.get("mounting_height", 1100.0) or 1100.0))
        _set_fcstd_property(target, "App::PropertyString", "Manufacturer", "BIM_Asset", family.get("manufacturer", ""))
        _set_fcstd_property(target, "App::PropertyString", "Model", "BIM_Asset", family.get("model", ""))
        _set_fcstd_property(target, "App::PropertyString", "CatalogCode", "BIM_Asset", family.get("catalog_code", ""))
        _set_fcstd_property(target, "App::PropertyString", "FamilyDescription", "BIM_Asset", family.get("description", ""))
        doc.saveAs(path)
        return True
    finally:
        try:
            FreeCAD.closeDocument(doc.Name)
        finally:
            if previous_doc_name:
                try:
                    FreeCAD.setActiveDocument(previous_doc_name)
                except Exception:
                    pass


def _module_label(value):
    text = str(value or "")
    if text.startswith("2"):
        return "2 Modulos"
    if text.startswith("3"):
        return "3 Modulos"
    return "1 Modulo"


class FamilyManagerDialog(QtWidgets.QDialog if QtWidgets else object):
    def __init__(self):
        super(FamilyManagerDialog, self).__init__()
        self.setWindowTitle(tr("Gerenciar Familias BIM"))
        self.resize(900, 560)
        self.data = {"family": _scan_family_files()}
        self.current_index = -1
        self.filtered_indexes = []

        root = QtWidgets.QHBoxLayout(self)

        left = QtWidgets.QVBoxLayout()
        self.folder_combo = QtWidgets.QComboBox()
        self.folder_combo.addItem(tr("Todas as pastas"), "")
        left.addWidget(self.folder_combo)
        self.family_list = QtWidgets.QListWidget()
        self.family_list.currentRowChanged.connect(self.load_family)
        left.addWidget(self.family_list)

        left_buttons = QtWidgets.QHBoxLayout()
        self.new_btn = QtWidgets.QPushButton(tr("Nova"))
        self.import_btn = QtWidgets.QPushButton(tr("Importar FCStd"))
        self.scan_btn = QtWidgets.QPushButton(tr("Reler Pastas"))
        self.export_mesh_btn = QtWidgets.QPushButton(tr("Exportar Malhas 3D"))
        left_buttons.addWidget(self.new_btn)
        left_buttons.addWidget(self.import_btn)
        left_buttons.addWidget(self.scan_btn)
        left_buttons.addWidget(self.export_mesh_btn)
        left.addLayout(left_buttons)

        form_box = QtWidgets.QGroupBox(tr("Metadados BIM da familia"))
        form = QtWidgets.QFormLayout(form_box)

        self.name_edit = QtWidgets.QLineEdit()
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(["Tomada", "Conjunto Modular", "Iluminacao", "Interruptor", "Automacao", "Industrial", "MT", "Importadas"])
        self.discipline_combo = QtWidgets.QComboBox()
        self.discipline_combo.setEditable(True)
        self.discipline_combo.addItems(["Eletrica", "Automacao", "Telecom", "SPDA", "MT"])
        self.ifc_edit = QtWidgets.QLineEdit("IfcFlowTerminal")
        self.source_edit = QtWidgets.QLineEdit()
        self.source_edit.setReadOnly(True)
        self.source_2d_edit = QtWidgets.QLineEdit()

        self.modules_combo = QtWidgets.QComboBox()
        self.modules_combo.addItems(["1 Modulo", "2 Modulos", "3 Modulos"])
        self.composition_edit = QtWidgets.QLineEdit()
        self.socket_count_spin = QtWidgets.QSpinBox()
        self.socket_count_spin.setRange(0, 20)
        self.switch_count_spin = QtWidgets.QSpinBox()
        self.switch_count_spin.setRange(0, 20)
        self.amperage_combo = QtWidgets.QComboBox()
        self.amperage_combo.setEditable(True)
        self.amperage_combo.addItems(["10A", "20A", "32A", "63A"])
        self.voltage_combo = QtWidgets.QComboBox()
        self.voltage_combo.setEditable(True)
        self.voltage_combo.addItems(["127V", "220V", "380V", "440V", "13.8kV", "34.5kV"])
        self.power_spin = QtWidgets.QDoubleSpinBox()
        self.power_spin.setRange(0.0, 100000000.0)
        self.power_spin.setDecimals(2)
        self.power_spin.setSuffix(" VA")
        self.active_power_spin = QtWidgets.QDoubleSpinBox()
        self.active_power_spin.setRange(0.0, 100000000.0)
        self.active_power_spin.setDecimals(2)
        self.active_power_spin.setSuffix(" W")
        self.power_factor_spin = QtWidgets.QDoubleSpinBox()
        self.power_factor_spin.setRange(0.0, 1.0)
        self.power_factor_spin.setDecimals(3)
        self.power_factor_spin.setSingleStep(0.05)
        self.power_factor_spin.setValue(1.0)
        self.demand_factor_spin = QtWidgets.QDoubleSpinBox()
        self.demand_factor_spin.setRange(0.0, 1.0)
        self.demand_factor_spin.setDecimals(3)
        self.demand_factor_spin.setSingleStep(0.05)
        self.demand_factor_spin.setValue(1.0)
        self.phase_combo = QtWidgets.QComboBox()
        self.phase_combo.setEditable(True)
        self.phase_combo.addItems(["R", "S", "T", "RS", "RT", "ST", "RST", "F+N+PE", "2F+PE", "3F+PE"])
        self.load_class_combo = QtWidgets.QComboBox()
        self.load_class_combo.setEditable(True)
        self.load_class_combo.addItems(["TUG", "TUE", "UPS", "Misto", "Iluminacao", "Industrial", "Hospitalar", "Automacao", "Geral"])
        self.application_combo = QtWidgets.QComboBox()
        self.application_combo.setEditable(True)
        self.application_combo.addItems(["Predial", "Residencial", "Comercial", "Hospitalar", "Industrial", "Saneamento", "Urbano", "Rural"])
        self.ip_edit = QtWidgets.QLineEdit("IP20")
        self.standard_edit = QtWidgets.QLineEdit("NBR 5410")
        self.height_combo = QtWidgets.QComboBox()
        self.height_combo.setEditable(True)
        self.height_combo.addItems(["Baixa (300mm)", "Media (1100mm)", "Alta (2200mm)", "Especial"])
        self.mounting_spin = QtWidgets.QDoubleSpinBox()
        self.mounting_spin.setRange(-5000.0, 50000.0)
        self.mounting_spin.setDecimals(1)
        self.mounting_spin.setSuffix(" mm")

        self.manufacturer_edit = QtWidgets.QLineEdit()
        self.model_edit = QtWidgets.QLineEdit()
        self.code_edit = QtWidgets.QLineEdit()
        self.description_edit = QtWidgets.QPlainTextEdit()
        self.description_edit.setMaximumHeight(80)

        form.addRow(tr("Nome:"), self.name_edit)
        form.addRow(tr("Categoria:"), self.category_combo)
        form.addRow(tr("Disciplina:"), self.discipline_combo)
        form.addRow(tr("Classe IFC:"), self.ifc_edit)
        form.addRow(tr("Arquivo 3D:"), self.source_edit)
        form.addRow(tr("Arquivo 2D:"), self.source_2d_edit)
        form.addRow(tr("Modulos:"), self.modules_combo)
        form.addRow(tr("Composicao:"), self.composition_edit)
        form.addRow(tr("Qtd. tomadas:"), self.socket_count_spin)
        form.addRow(tr("Qtd. interruptores:"), self.switch_count_spin)
        form.addRow(tr("Amperagem:"), self.amperage_combo)
        form.addRow(tr("Tensao:"), self.voltage_combo)
        form.addRow(tr("Potencia padrao:"), self.power_spin)
        form.addRow(tr("Potencia ativa:"), self.active_power_spin)
        form.addRow(tr("Fator de potencia:"), self.power_factor_spin)
        form.addRow(tr("Fator de demanda:"), self.demand_factor_spin)
        form.addRow(tr("Fase:"), self.phase_combo)
        form.addRow(tr("Classificacao da carga:"), self.load_class_combo)
        form.addRow(tr("Aplicacao:"), self.application_combo)
        form.addRow(tr("Grau IP:"), self.ip_edit)
        form.addRow(tr("Norma:"), self.standard_edit)
        form.addRow(tr("Altura padrao:"), self.height_combo)
        form.addRow(tr("Altura de montagem:"), self.mounting_spin)
        form.addRow(tr("Fabricante:"), self.manufacturer_edit)
        form.addRow(tr("Modelo:"), self.model_edit)
        form.addRow(tr("Codigo:"), self.code_edit)
        form.addRow(tr("Descricao:"), self.description_edit)

        right = QtWidgets.QVBoxLayout()
        right.addWidget(form_box)
        buttons = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton(tr("Salvar Familia"))
        self.close_btn = QtWidgets.QPushButton(tr("Fechar"))
        buttons.addStretch()
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.close_btn)
        right.addLayout(buttons)

        root.addLayout(left, 1)
        root.addLayout(right, 2)

        self.new_btn.clicked.connect(self.new_family)
        self.import_btn.clicked.connect(self.import_family)
        self.scan_btn.clicked.connect(self.scan_library)
        self.export_mesh_btn.clicked.connect(self.export_meshes)
        self.folder_combo.currentIndexChanged.connect(lambda _index: self.populate(0))
        self.save_btn.clicked.connect(self.save_current)
        self.close_btn.clicked.connect(self.accept)

        self.populate()

    def families(self):
        return self.data.setdefault("family", [])

    def family_folder(self, family):
        source = str(family.get("source_3d", "")).replace("\\", "/")
        folder = os.path.dirname(source).replace("\\", "/")
        return folder or tr("Raiz")

    def populate_folders(self):
        current = self.folder_combo.currentData() if hasattr(self, "folder_combo") else ""
        self.folder_combo.blockSignals(True)
        self.folder_combo.clear()
        self.folder_combo.addItem(tr("Todas as pastas"), "")
        folders = sorted({self.family_folder(family) for family in self.families()})
        for folder in folders:
            self.folder_combo.addItem(folder, folder)
        idx = self.folder_combo.findData(current)
        self.folder_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.folder_combo.blockSignals(False)

    def populate(self, select_index=0):
        self.populate_folders()
        selected_folder = self.folder_combo.currentData() or ""
        self.family_list.blockSignals(True)
        self.family_list.clear()
        self.filtered_indexes = []
        for index, family in enumerate(self.families()):
            folder = self.family_folder(family)
            if selected_folder and folder != selected_folder:
                continue
            label = f"{folder} - {family.get('name', family.get('id', ''))}"
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.UserRole, index)
            self.family_list.addItem(item)
            self.filtered_indexes.append(index)
        self.family_list.blockSignals(False)
        if self.family_list.count():
            self.family_list.setCurrentRow(max(0, min(select_index, self.family_list.count() - 1)))
        else:
            self.clear_fields()

    def select_source(self, source):
        source = str(source or "").replace("\\", "/")
        folder = os.path.dirname(source).replace("\\", "/")
        idx = self.folder_combo.findData(folder)
        if idx >= 0:
            self.folder_combo.setCurrentIndex(idx)
            self.populate(0)
        for row in range(self.family_list.count()):
            family_index = self.family_list.item(row).data(QtCore.Qt.UserRole)
            family = self.families()[family_index]
            if str(family.get("source_3d", "")).replace("\\", "/") == source:
                self.family_list.setCurrentRow(row)
                return True
        return False

    def clear_fields(self):
        self.current_index = -1
        for edit in [self.name_edit, self.ifc_edit, self.source_edit, self.source_2d_edit, self.composition_edit, self.manufacturer_edit, self.model_edit, self.code_edit]:
            edit.clear()
        self.description_edit.clear()
        self.power_spin.setValue(0.0)
        self.active_power_spin.setValue(0.0)
        self.socket_count_spin.setValue(0)
        self.switch_count_spin.setValue(0)
        self.power_factor_spin.setValue(1.0)
        self.demand_factor_spin.setValue(1.0)
        self.ip_edit.setText("IP20")
        self.standard_edit.setText("NBR 5410")
        self.mounting_spin.setValue(1100.0)

    def set_combo_text(self, combo, value):
        text = str(value or "")
        idx = combo.findText(text)
        if idx < 0:
            combo.addItem(text)
            idx = combo.findText(text)
        combo.setCurrentIndex(idx)

    def load_family(self, index):
        if index < 0 or index >= len(self.filtered_indexes):
            self.clear_fields()
            return
        self.current_index = self.filtered_indexes[index]
        family = self.families()[self.current_index]
        self.name_edit.setText(str(family.get("name", "")))
        self.set_combo_text(self.category_combo, family.get("category", "Tomada"))
        self.set_combo_text(self.discipline_combo, family.get("discipline", "Eletrica"))
        self.ifc_edit.setText(str(family.get("ifc_class", "IfcFlowTerminal")))
        self.source_edit.setText(str(family.get("source_3d", "")))
        self.source_2d_edit.setText(str(family.get("source_2d", "")))
        self.set_combo_text(self.modules_combo, _module_label(family.get("modules", "1 Modulo")))
        self.composition_edit.setText(str(family.get("composition", "")))
        self.socket_count_spin.setValue(int(family.get("socket_count", 0) or 0))
        self.switch_count_spin.setValue(int(family.get("switch_count", 0) or 0))
        self.set_combo_text(self.amperage_combo, family.get("amperage", "10A"))
        self.set_combo_text(self.voltage_combo, family.get("voltage", "127V"))
        self.power_spin.setValue(float(family.get("power", 0.0) or 0.0))
        self.active_power_spin.setValue(float(family.get("active_power_w", family.get("power", 0.0)) or 0.0))
        self.power_factor_spin.setValue(float(family.get("power_factor", 1.0) or 1.0))
        self.demand_factor_spin.setValue(float(family.get("demand_factor", 1.0) or 1.0))
        self.set_combo_text(self.phase_combo, family.get("phase", "R"))
        self.set_combo_text(self.load_class_combo, family.get("load_classification", "TUG"))
        self.set_combo_text(self.application_combo, family.get("socket_application", "Predial"))
        self.ip_edit.setText(str(family.get("ip_rating", "IP20")))
        self.standard_edit.setText(str(family.get("electrical_standard", "NBR 5410")))
        self.set_combo_text(self.height_combo, family.get("height_type", "Media (1100mm)"))
        self.mounting_spin.setValue(float(family.get("mounting_height", 1100.0) or 1100.0))
        self.manufacturer_edit.setText(str(family.get("manufacturer", "")))
        self.model_edit.setText(str(family.get("model", "")))
        self.code_edit.setText(str(family.get("catalog_code", "")))
        self.description_edit.setPlainText(str(family.get("description", "")))

    def collect_fields(self):
        old = self.families()[self.current_index] if 0 <= self.current_index < len(self.families()) else {}
        name = self.name_edit.text().strip() or old.get("name", "Nova Familia")
        family_id = old.get("id") or name.lower().replace(" ", "_")
        return {
            "id": family_id,
            "name": name,
            "category": self.category_combo.currentText().strip() or "Tomada",
            "discipline": self.discipline_combo.currentText().strip() or "Eletrica",
            "ifc_class": self.ifc_edit.text().strip() or "IfcDistributionElement",
            "source_3d": self.source_edit.text().strip(),
            "source_2d": self.source_2d_edit.text().strip(),
            "modules": self.modules_combo.currentText().strip(),
            "composition": self.composition_edit.text().strip(),
            "socket_count": int(self.socket_count_spin.value()),
            "switch_count": int(self.switch_count_spin.value()),
            "amperage": self.amperage_combo.currentText().strip(),
            "voltage": self.voltage_combo.currentText().strip(),
            "power": float(self.power_spin.value()),
            "apparent_power_va": float(self.power_spin.value()),
            "active_power_w": float(self.active_power_spin.value()),
            "power_factor": float(self.power_factor_spin.value()),
            "demand_factor": float(self.demand_factor_spin.value()),
            "phase": self.phase_combo.currentText().strip(),
            "load_classification": self.load_class_combo.currentText().strip(),
            "socket_application": self.application_combo.currentText().strip(),
            "ip_rating": self.ip_edit.text().strip(),
            "electrical_standard": self.standard_edit.text().strip(),
            "height_type": self.height_combo.currentText().strip(),
            "mounting_height": float(self.mounting_spin.value()),
            "manufacturer": self.manufacturer_edit.text().strip(),
            "model": self.model_edit.text().strip(),
            "catalog_code": self.code_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
        }

    def new_family(self):
        count = len(self.families()) + 1
        self.families().append({
            "id": f"nova_familia_{count}",
            "name": f"Nova Familia {count}",
            "category": "Tomada",
            "discipline": "Eletrica",
            "ifc_class": "IfcFlowTerminal",
            "source_3d": "",
            "source_2d": "",
            "modules": "1 Modulo",
            "composition": "",
            "socket_count": 0,
            "switch_count": 0,
            "amperage": "10A",
            "voltage": "127V",
            "power": 100.0,
            "apparent_power_va": 100.0,
            "active_power_w": 100.0,
            "power_factor": 1.0,
            "demand_factor": 1.0,
            "phase": "R",
            "load_classification": "TUG",
            "socket_application": "Predial",
            "ip_rating": "IP20",
            "electrical_standard": "NBR 5410",
            "height_type": "Media (1100mm)",
            "mounting_height": 1100.0,
            "manufacturer": "",
            "model": "",
            "catalog_code": "",
            "description": "",
        })
        self.populate(len(self.families()) - 1)

    def import_family(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            tr("Importar familia 3D"),
            "",
            "FreeCAD (*.FCStd *.fcstd);;Todos (*.*)",
        )
        if not path:
            return
        selected_folder = self.folder_combo.currentData() or ""
        category = self.category_combo.currentText().strip() or "Tomada"
        family = _import_family_file_to_folder(path, selected_folder or category)
        if not family:
            FreeCAD.Console.PrintError(f"Nao foi possivel importar familia: {path}\n")
            return
        self.data = {"family": _scan_family_files()}
        self.select_source(family.get("source_3d", ""))
        FreeCAD.Console.PrintLog(f"Familia importada para a biblioteca 3D: {path}\n")

    def scan_library(self):
        self.data = {"family": _scan_family_files()}
        self.populate(0)
        FreeCAD.Console.PrintLog("Biblioteca de familias relida a partir dos arquivos .FCStd.\n")

    def export_meshes(self):
        QtWidgets.QMessageBox.information(
            self,
            tr("Biblioteca 3D"),
            tr("A biblioteca agora usa os proprios arquivos .FCStd. Nenhum SQLite de familias sera gerado."),
        )

    def save_current(self):
        if self.current_index < 0:
            return
        family = self.collect_fields()
        self.families()[self.current_index] = family
        saved = _write_family_properties_to_fcstd(family)
        self.data = {"family": _scan_family_files()}
        self.select_source(family.get("source_3d", ""))
        if saved:
            FreeCAD.Console.PrintLog("Propriedades BIM gravadas no arquivo .FCStd da familia.\n")
        else:
            FreeCAD.Console.PrintWarning("Nao foi possivel gravar propriedades BIM no arquivo .FCStd da familia.\n")


class ManageFamilies:
    AllowNoDocument = False

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Library.svg"),
            "MenuText": tr("Gerenciar Familias"),
            "ToolTip": tr("Gerencia familias BIM a partir dos arquivos .FCStd da biblioteca"),
        }

    def Activated(self):
        if not QtWidgets:
            FreeCAD.Console.PrintError("PySide nao disponivel para abrir o gerenciador de familias.\n")
            return
        dialog = FamilyManagerDialog()
        dialog.exec_()
