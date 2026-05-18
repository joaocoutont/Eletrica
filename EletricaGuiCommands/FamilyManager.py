import os

import FreeCAD

from EletricaLogic.i18n import tr
from EletricaLogic.FamilyCatalog import (
    CATALOG_PATH,
    import_family_file,
    load_catalog,
    refresh_catalog_from_library,
    save_catalog,
)

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
        self.data = load_catalog()
        self.current_index = -1

        root = QtWidgets.QHBoxLayout(self)

        left = QtWidgets.QVBoxLayout()
        self.family_list = QtWidgets.QListWidget()
        self.family_list.currentRowChanged.connect(self.load_family)
        left.addWidget(self.family_list)

        left_buttons = QtWidgets.QHBoxLayout()
        self.new_btn = QtWidgets.QPushButton(tr("Nova"))
        self.import_btn = QtWidgets.QPushButton(tr("Importar FCStd"))
        self.scan_btn = QtWidgets.QPushButton(tr("Regerar Catalogo"))
        left_buttons.addWidget(self.new_btn)
        left_buttons.addWidget(self.import_btn)
        left_buttons.addWidget(self.scan_btn)
        left.addLayout(left_buttons)

        form_box = QtWidgets.QGroupBox(tr("Metadados BIM da familia"))
        form = QtWidgets.QFormLayout(form_box)

        self.name_edit = QtWidgets.QLineEdit()
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(["Tomada", "Iluminacao", "Interruptor", "Automacao", "Industrial", "MT", "Importadas"])
        self.discipline_combo = QtWidgets.QComboBox()
        self.discipline_combo.setEditable(True)
        self.discipline_combo.addItems(["Eletrica", "Automacao", "Telecom", "SPDA", "MT"])
        self.ifc_edit = QtWidgets.QLineEdit("IfcFlowTerminal")
        self.source_edit = QtWidgets.QLineEdit()
        self.source_edit.setReadOnly(True)
        self.source_2d_edit = QtWidgets.QLineEdit()

        self.modules_combo = QtWidgets.QComboBox()
        self.modules_combo.addItems(["1 Modulo", "2 Modulos", "3 Modulos"])
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
        form.addRow(tr("Amperagem:"), self.amperage_combo)
        form.addRow(tr("Tensao:"), self.voltage_combo)
        form.addRow(tr("Potencia padrao:"), self.power_spin)
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
        self.save_btn.clicked.connect(self.save_current)
        self.close_btn.clicked.connect(self.accept)

        self.populate()

    def families(self):
        return self.data.setdefault("family", [])

    def populate(self, select_index=0):
        self.family_list.blockSignals(True)
        self.family_list.clear()
        for family in self.families():
            label = f"{family.get('category', 'Familia')} - {family.get('name', family.get('id', ''))}"
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.UserRole, family.get("id", ""))
            self.family_list.addItem(item)
        self.family_list.blockSignals(False)
        if self.family_list.count():
            self.family_list.setCurrentRow(max(0, min(select_index, self.family_list.count() - 1)))
        else:
            self.clear_fields()

    def clear_fields(self):
        self.current_index = -1
        for edit in [self.name_edit, self.ifc_edit, self.source_edit, self.source_2d_edit, self.manufacturer_edit, self.model_edit, self.code_edit]:
            edit.clear()
        self.description_edit.clear()
        self.power_spin.setValue(0.0)
        self.mounting_spin.setValue(1100.0)

    def set_combo_text(self, combo, value):
        text = str(value or "")
        idx = combo.findText(text)
        if idx < 0:
            combo.addItem(text)
            idx = combo.findText(text)
        combo.setCurrentIndex(idx)

    def load_family(self, index):
        self.current_index = index
        if index < 0 or index >= len(self.families()):
            self.clear_fields()
            return
        family = self.families()[index]
        self.name_edit.setText(str(family.get("name", "")))
        self.set_combo_text(self.category_combo, family.get("category", "Tomada"))
        self.set_combo_text(self.discipline_combo, family.get("discipline", "Eletrica"))
        self.ifc_edit.setText(str(family.get("ifc_class", "IfcFlowTerminal")))
        self.source_edit.setText(str(family.get("source_3d", "")))
        self.source_2d_edit.setText(str(family.get("source_2d", "")))
        self.set_combo_text(self.modules_combo, _module_label(family.get("modules", "1 Modulo")))
        self.set_combo_text(self.amperage_combo, family.get("amperage", "10A"))
        self.set_combo_text(self.voltage_combo, family.get("voltage", "127V"))
        self.power_spin.setValue(float(family.get("power", 0.0) or 0.0))
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
            "amperage": self.amperage_combo.currentText().strip(),
            "voltage": self.voltage_combo.currentText().strip(),
            "power": float(self.power_spin.value()),
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
            "amperage": "10A",
            "voltage": "127V",
            "power": 100.0,
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
        category = self.category_combo.currentText().strip() or "Importadas"
        family = import_family_file(path, category)
        if not family:
            FreeCAD.Console.PrintError(f"Nao foi possivel importar familia: {path}\n")
            return
        self.data = load_catalog()
        index = 0
        for i, item in enumerate(self.families()):
            if item.get("id") == family.get("id"):
                index = i
                break
        self.populate(index)
        FreeCAD.Console.PrintLog(f"Familia importada para o catalogo: {path}\n")

    def scan_library(self):
        self.data = refresh_catalog_from_library()
        self.populate(self.current_index)
        FreeCAD.Console.PrintLog(f"Catalogo de familias atualizado: {CATALOG_PATH}\n")

    def save_current(self):
        if self.current_index < 0:
            return
        self.families()[self.current_index] = self.collect_fields()
        save_catalog(self.data)
        index = self.current_index
        self.populate(index)
        FreeCAD.Console.PrintLog(f"Familia salva no catalogo: {CATALOG_PATH}\n")


class ManageFamilies:
    AllowNoDocument = False

    def GetResources(self):
        return {
            "Pixmap": os.path.join(ICON_DIR, "Library.svg"),
            "MenuText": tr("Gerenciar Familias"),
            "ToolTip": tr("Edita o catalogo TOML de familias BIM sem carregar os arquivos 3D"),
        }

    def Activated(self):
        if not QtWidgets:
            FreeCAD.Console.PrintError("PySide nao disponivel para abrir o gerenciador de familias.\n")
            return
        dialog = FamilyManagerDialog()
        dialog.exec_()
