import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .light_bim import ProfessionalBIMLight
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, discover_panel_boards, discover_circuits
)

LIGHT_FAMILIES = {
    "Plafon LED Quadrado (18W)": {"file": "LED_Square_18W.FCStd", "power": 18, "flux": 1400, "mount": "Teto"},
    "Plafon LED Redondo (12W)":  {"file": "LED_Round_12W.FCStd",  "power": 12, "flux": 900,  "mount": "Teto"},
    "Spot LED Embutir (5W)":     {"file": "LED_Spot_5W.FCStd",   "power": 5,  "flux": 400,  "mount": "Embutir"},
    "Arandela Externa (10W)":    {"file": "Wall_Light_10W.FCStd", "power": 10, "flux": 800,  "mount": "Parede (Arandela)"},
    "Lustre Pendente":           {"file": "Pendant_Light.FCStd", "power": 30, "flux": 2400, "mount": "Teto"},
    "Ponto de Luz (Bocal E27)":  {"file": "Generic_Light.FCStd", "power": 60, "flux": 800,  "mount": "Teto"}
}

class LightTaskPanel:
    """Interface para Inserção de Luminárias"""
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
        
        # --- SELEÇÃO DE FAMÍLIA ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Família de Luminária:</b>"))
        self.family_combo = QtGui.QComboBox()
        self.family_combo.addItems(sorted(LIGHT_FAMILIES.keys()))
        self.family_combo.currentTextChanged.connect(self.on_family_changed)
        self.scroll_layout.addWidget(self.family_combo)
        
        # TÉCNICO
        tech_group = QtGui.QGroupBox("Dados Fotométricos")
        tech_form = QtGui.QFormLayout()
        
        self.power_in = QtGui.QDoubleSpinBox(); self.power_in.setSuffix(" W")
        self.power_in.valueChanged.connect(self.sync_values)
        tech_form.addRow("Potência:", self.power_in)

        self.flux_in = QtGui.QDoubleSpinBox(); self.flux_in.setRange(0, 100000); self.flux_in.setSuffix(" lm")
        self.flux_in.valueChanged.connect(self.sync_values)
        tech_form.addRow("Fluxo Lum.:", self.flux_in)

        self.temp_combo = QtGui.QComboBox()
        self.temp_combo.addItems(["2700K (Quente)", "3000K (Morna)", "4000K (Neutra)", "6500K (Fria)"])
        tech_form.addRow("Cor:", self.temp_combo)
        
        tech_group.setLayout(tech_form)
        self.scroll_layout.addWidget(tech_group)

        # POSIÇÃO
        pos_group = QtGui.QGroupBox("Instalação")
        pos_form = QtGui.QFormLayout()
        
        self.mount_combo = QtGui.QComboBox()
        self.mount_combo.addItems(["Teto", "Parede (Arandela)", "Embutir", "Piso"])
        self.mount_combo.currentTextChanged.connect(self.on_mount_changed)
        pos_form.addRow("Tipo:", self.mount_combo)

        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 10000); self.z_in.setValue(2800)
        self.z_in.valueChanged.connect(self.sync_values)
        pos_form.addRow("Altura Z (mm):", self.z_in)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        # BIM
        bim_group = QtGui.QGroupBox("BIM")
        bim_form = QtGui.QFormLayout()
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        bim_form.addRow("Quadro:", self.panel_combo)
        self.circuit_combo = QtGui.QComboBox()
        self.populate_circuits()
        bim_form.addRow("Circuito:", self.circuit_combo)
        bim_group.setLayout(bim_form)
        self.scroll_layout.addWidget(bim_group)

        self.scroll_layout.addStretch()
        self.on_family_changed(self.family_combo.currentText())

    def on_family_changed(self, text):
        data = LIGHT_FAMILIES.get(text)
        if not data: return
        self.command.power = data["power"]
        self.command.flux = data["flux"]
        self.command.family_file = data["file"]
        self.command.mount_type = data["mount"]
        
        self.power_in.setValue(data["power"])
        self.flux_in.setValue(data["flux"])
        self.mount_combo.setCurrentText(data["mount"])
        
        if data["mount"] == "Parede (Arandela)": self.z_in.setValue(2200)
        else: self.z_in.setValue(2800)
        self.refresh_ghost()

    def on_mount_changed(self, text):
        self.command.mount_type = text
        self.refresh_ghost()

    def populate_panels(self):
        panels = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.addItem("Sem quadro")
        for p in panels: self.panel_combo.addItem(p["name"])

    def populate_circuits(self):
        circuits = discover_circuits(App.ActiveDocument)
        for c in circuits: self.circuit_combo.addItem(c["name"])

    def sync_values(self):
        self.command.power = self.power_in.value()
        self.command.flux = self.flux_in.value()
        self.command.z_level = self.z_in.value()
        self.refresh_ghost()

    def refresh_ghost(self):
        if hasattr(self.command, 'engine') and self.command.engine.ghost:
            self.command.engine.ghost.Shape = self.command.make_preview_shape()
            Gui.updateGui()

    def accept(self):
        Gui.Control.closeDialog()
        return True

class LightCommand:
    """Comando de Inserção de Luminárias BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertLight"
        self.power = 10.0
        self.flux = 800.0
        self.mount_type = "Teto"
        self.z_level = 2800.0
        self.family_file = "Luminaria_LED.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "Light.svg"),
            'MenuText': 'Inserir Luminária',
            'ToolTip': 'Insere ponto de iluminação com dados fotométricos NBR',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, LightTaskPanel, self.place_light)
        self.engine.start()

    def make_preview_shape(self):
        try:
            from .light_bim import make_light_plan_symbol
            return make_light_plan_symbol(self.mount_type)
        except Exception:
            return Part.makeCylinder(50, 10)

    def place_light(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_Light")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (1.0, 1.0, 0.0) # Amarelo para luz
                obj.ViewObject.Transparency = 30
        else:
            matriz_label = f"Matriz_Luz_{self.family_file.replace('.FCStd','')}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMLight(matriz)
                matriz.SourceFile = self.family_file
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"Luz_{int(self.power)}W")
            obj.LinkedObject = matriz
            
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("Power", self.power, ptype="App::PropertyFloat")
            _set_prop("LuminousFlux", self.flux, ptype="App::PropertyFloat")
            _set_prop("MountingType", self.mount_type, group="BIM_Posicionamento")
            _set_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")
            _set_prop("Tag", f"L-{int(self.power)}W", group="BIM_Classificacao")

            if obj.ViewObject: obj.ViewObject.ShapeColor = (1.0, 1.0, 0.8)
            obj.Label = f"Luminaria {int(self.power)}W"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(0,0,0,1))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .light_bim import make_light_plan_symbol
            shape = make_light_plan_symbol(self.mount_type)
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.8, 0.8, 0.0)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertLight', LightCommand())
