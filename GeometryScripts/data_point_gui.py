import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .data_point_bim import ProfessionalBIMDataPoint
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, create_default_bim_levels, discover_panel_boards,
    discover_circuits, discover_spaces_or_sectors
)

TELECOM_CATEGORIES = {
    "Dados (RJ45)": {"file": "Tomada_Dados_RJ45.FCStd", "standards": ["Cat5e", "Cat6", "Cat6a", "Cat7"], "tag": "D"},
    "Voz (RJ11)":   {"file": "Tomada_Voz_RJ11.FCStd", "standards": ["Padrao Telebras", "RJ11"], "tag": "V"},
    "TV (Coaxial)": {"file": "Tomada_TV_Coaxial.FCStd", "standards": ["RG6", "RG59"], "tag": "TV"},
    "Fibra Óptica": {"file": "Tomada_Fibra_Optica.FCStd", "standards": ["SingleMode SC", "MultiMode LC"], "tag": "FO"},
    "Multimídia":   {"file": "Tomada_HDMI_USB.FCStd", "standards": ["HDMI", "USB 3.0", "VGA"], "tag": "M"}
}

class DataPointTaskPanel:
    """Interface para Pontos de Telecomunicações e Dados"""
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
        
        # --- SELEÇÃO DE CATEGORIA ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Categoria de Telecom:</b>"))
        self.cat_combo = QtGui.QComboBox()
        self.cat_combo.addItems(list(TELECOM_CATEGORIES.keys()))
        self.cat_combo.currentTextChanged.connect(self.on_cat_changed)
        self.scroll_layout.addWidget(self.cat_combo)
        
        # ESPECIFICAÇÃO
        spec_group = QtGui.QGroupBox("Especificação Técnica")
        spec_form = QtGui.QFormLayout()
        
        self.std_combo = QtGui.QComboBox()
        spec_form.addRow("Padrão/Cabo:", self.std_combo)
        
        self.port_in = QtGui.QSpinBox(); self.port_in.setRange(1, 4); self.port_in.setValue(1)
        self.port_in.valueChanged.connect(self.sync_values)
        spec_form.addRow("Nº de Portas:", self.port_in)
        
        spec_group.setLayout(spec_form)
        self.scroll_layout.addWidget(spec_group)

        # POSICIONAMENTO
        pos_group = QtGui.QGroupBox("Instalação")
        pos_form = QtGui.QFormLayout()
        
        self.level_combo = QtGui.QComboBox()
        self.populate_levels()
        pos_form.addRow("Nível:", self.level_combo)

        self.height_combo = QtGui.QComboBox()
        self.height_combo.addItems(["Rodapé (300mm)", "Média (1100mm)", "Alta (2200mm)"])
        self.height_combo.currentTextChanged.connect(self.sync_height)
        pos_form.addRow("Sugestão Z:", self.height_combo)

        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 5000); self.z_in.setValue(300)
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
        self.vdi_combo = QtGui.QComboBox()
        self.populate_racks()
        bim_form.addRow("Quadro/Rack (VDI):", self.vdi_combo)
        bim_group.setLayout(bim_form)
        self.scroll_layout.addWidget(bim_group)

        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(QtGui.QLabel("Dica: Use Cat6 para redes gigabit."))
        
        # Init
        self.on_cat_changed(self.cat_combo.currentText())

    def on_cat_changed(self, text):
        data = TELECOM_CATEGORIES.get(text)
        if not data: return
        
        self.command.category = text
        self.command.family_file = data["file"]
        
        self.std_combo.blockSignals(True)
        self.std_combo.clear()
        self.std_combo.addItems(data["standards"])
        self.std_combo.blockSignals(False)
        
        self.refresh_ghost()

    def populate_levels(self):
        levels = discover_project_levels(App.ActiveDocument)
        for level in levels: self.level_combo.addItem(level["label"])

    def populate_racks(self):
        # Procura quadros VDI ou Racks
        panels = discover_panel_boards(App.ActiveDocument)
        self.vdi_combo.addItem("Sem Rack Central")
        for p in panels: 
            if "VDI" in p["name"].upper() or "RACK" in p["name"].upper():
                self.vdi_combo.addItem(p["name"])

    def sync_height(self):
        txt = self.height_combo.currentText()
        if "Rodapé" in txt: self.z_in.setValue(300.0)
        elif "Média" in txt: self.z_in.setValue(1100.0)
        elif "Alta" in txt: self.z_in.setValue(2200.0)

    def sync_values(self):
        self.command.category = self.cat_combo.currentText()
        self.command.standard = self.std_combo.currentText()
        self.command.ports = self.port_in.value()
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

class DataPointCommand:
    """Comando de Inserção de Pontos de Dados/Telecom BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertDataDevice"
        self.category = "Dados (RJ45)"
        self.standard = "Cat6"
        self.ports = 1
        self.z_level = 300.0
        self.rotation = 0
        self.family_file = "Tomada_Dados_RJ45.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "Telecom.svg"),
            'MenuText': 'Ponto de Dados/Telecom',
            'ToolTip': 'Insere tomadas RJ45, RJ11, TV ou Fibra com simbologia NBR',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, DataPointTaskPanel, self.place_data_point)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .data_point_bim import make_data_plan_symbol
            return make_data_plan_symbol(self.category, self.ports)
        except Exception:
            return Part.makeBox(80, 120, 2)

    def place_data_point(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_Data")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.0, 1.0, 0.5) # Verde esmeralda para telecom
                obj.ViewObject.Transparency = 20
        else:
            # Matriz Cache
            matriz_label = f"Matriz_Telecom_{self.category.split(' ')[0]}_{self.ports}P"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMDataPoint(matriz)
                matriz.SourceFile = self.family_file
                matriz.Category = self.category
                matriz.PortCount = self.ports
                matriz.Label = f"Matriz Telecom {self.category}"
                doc.recompute([matriz])

            # Instância Link
            obj = doc.addObject("App::Link", f"Telecom_{self.category.split(' ')[0]}")
            obj.LinkedObject = matriz
            
            # Propriedades Telecom
            def _set_prop(name, value, group="BIM_Telecom", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("Category", self.category)
            _set_prop("Standard", self.standard)
            _set_prop("PortCount", self.ports, ptype="App::PropertyInteger")
            _set_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")
            _set_prop("TipoBIM", "Ponto Telecom", group="BIM_Classificacao")

            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.0, 0.8, 0.4)

            obj.Label = f"Telecom {self.category} {self.ports}P"
            
            # Símbolo 2D
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(App.Vector(0,0,1), self.rotation + 180))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .data_point_bim import make_data_plan_symbol
            shape = make_data_plan_symbol(self.category, self.ports)
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py + 18.0, 0), App.Rotation(App.Vector(0,0,1), self.rotation))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.0, 0.6, 0.3)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertDataDevice', DataPointCommand())
