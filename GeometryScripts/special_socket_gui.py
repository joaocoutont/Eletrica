import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .special_socket_bim import ProfessionalBIMSpecialSocket
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, create_default_bim_levels, discover_panel_boards,
    discover_circuits, discover_spaces_or_sectors
)

# LISTA DE EQUIPAMENTOS TUE (NBR 5410 / PADRÃO DE MERCADO)
TUE_EQUIPMENT_DATABASE = {
    "Chuveiro Elétrico (Simples)": {"power_w": 5500, "fp": 1.0, "v": "220V", "h": 2200, "amp": "32A", "label": "CHU"},
    "Chuveiro Elétrico (Potente)": {"power_w": 7500, "fp": 1.0, "v": "220V", "h": 2200, "amp": "40A", "label": "CHU+"},
    "Ar Condicionado 9000 BTUs":   {"power_w": 900,  "fp": 0.85, "v": "220V", "h": 2200, "amp": "10A", "label": "AC9"},
    "Ar Condicionado 12000 BTUs":  {"power_w": 1200, "fp": 0.85, "v": "220V", "h": 2200, "amp": "10A", "label": "AC12"},
    "Ar Condicionado 18000 BTUs":  {"power_w": 1800, "fp": 0.85, "v": "220V", "h": 2200, "amp": "20A", "label": "AC18"},
    "Forno Elétrico":              {"power_w": 3000, "fp": 1.0, "v": "220V", "h": 1100, "amp": "20A", "label": "FOR"},
    "Micro-ondas":                 {"power_w": 1500, "fp": 0.95, "v": "127V", "h": 1100, "amp": "20A", "label": "MIC"},
    "Lava e Seca":                 {"power_w": 2500, "fp": 0.9,  "v": "127V", "h": 600,  "amp": "20A", "label": "LAV"},
    "Lava Louças":                 {"power_w": 2000, "fp": 0.9,  "v": "127V", "h": 600,  "amp": "20A", "label": "LOU"},
    "Torneira Elétrica":           {"power_w": 4500, "fp": 1.0, "v": "220V", "h": 1100, "amp": "30A", "label": "TOR"},
    "Secadora de Roupas":          {"power_w": 3500, "fp": 1.0, "v": "220V", "h": 1100, "amp": "20A", "label": "SEC"},
    "Cooktop Indução":             {"power_w": 7000, "fp": 1.0, "v": "220V", "h": 600,  "amp": "40A", "label": "CKT"},
    "Genérico TUE 1000W":          {"power_w": 1000, "fp": 1.0, "v": "127V", "h": 1100, "amp": "10A", "label": "TUE"},
    "Genérico TUE 2000W":          {"power_w": 2000, "fp": 1.0, "v": "127V", "h": 1100, "amp": "20A", "label": "TUE"}
}

class SpecialSocketTaskPanel:
    """Interface para Tomadas de Uso Especial (TUE)"""
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
        
        # --- SELEÇÃO DE EQUIPAMENTO ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Equipamento de Uso Especial (TUE):</b>"))
        self.equip_combo = QtGui.QComboBox()
        self.equip_combo.addItems(sorted(TUE_EQUIPMENT_DATABASE.keys()))
        self.equip_combo.currentTextChanged.connect(self.on_equip_changed)
        self.scroll_layout.addWidget(self.equip_combo)
        
        # EXIBIÇÃO DE DADOS TÉCNICOS AUTOMÁTICOS
        self.data_group = QtGui.QGroupBox("Dados Sugeridos (Auto)")
        self.data_form = QtGui.QFormLayout()
        self.info_label = QtGui.QLabel("Selecione um equipamento...")
        self.data_form.addRow(self.info_label)
        self.data_group.setLayout(self.data_form)
        self.scroll_layout.addWidget(self.data_group)

        # CONFIGURAÇÕES MANUAIS / AJUSTES
        adj_group = QtGui.QGroupBox("Ajustes de Instalação")
        adj_form = QtGui.QFormLayout()
        
        self.level_combo = QtGui.QComboBox()
        self.populate_levels()
        adj_form.addRow("Nível:", self.level_combo)

        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 5000); self.z_in.setValue(1100)
        self.z_in.valueChanged.connect(self.sync_values)
        adj_form.addRow("Altura (mm):", self.z_in)

        self.rot_in = QtGui.QSpinBox(); self.rot_in.setRange(0, 360); self.rot_in.setSingleStep(90)
        self.rot_in.valueChanged.connect(self.sync_values)
        adj_form.addRow("Rotação (°):", self.rot_in)
        
        adj_group.setLayout(adj_form)
        self.scroll_layout.addWidget(adj_group)

        # BIM
        bim_group = QtGui.QGroupBox("BIM & Circuitos")
        bim_form = QtGui.QFormLayout()
        
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        bim_form.addRow("Quadro:", self.panel_combo)

        self.circuit_combo = QtGui.QComboBox()
        self.populate_circuits()
        bim_form.addRow("Circuito TUE:", self.circuit_combo)
        
        bim_group.setLayout(bim_form)
        self.scroll_layout.addWidget(bim_group)

        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(QtGui.QLabel("Dica: TUEs geralmente exigem circuito exclusivo."))
        
        # Iniciar com o primeiro item
        self.on_equip_changed(self.equip_combo.currentText())

    def on_equip_changed(self, text):
        data = TUE_EQUIPMENT_DATABASE.get(text)
        if not data: return
        
        self.command.equipment_type = text
        self.command.power_w = data["power_w"]
        self.command.power_factor = data["fp"]
        self.command.voltage = data["v"]
        self.command.z_level = float(data["h"])
        self.command.amperage = data["amp"]
        self.command.tag_label = data["label"]
        
        # Atualiza UI
        self.info_label.setText(
            f"<b>Potência:</b> {data['power_w']}W | <b>Tensão:</b> {data['v']}<br>"
            f"<b>Fator de Potência:</b> {data['fp']} | <b>Amperagem:</b> {data['amp']}"
        )
        self.z_in.blockSignals(True)
        self.z_in.setValue(self.command.z_level)
        self.z_in.blockSignals(False)
        
        self.refresh_ghost()

    def populate_levels(self):
        levels = discover_project_levels(App.ActiveDocument)
        for level in levels: self.level_combo.addItem(level["label"])
        self.command.level_options = levels
        
    def populate_panels(self):
        panels = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.addItem("Sem quadro")
        for p in panels: self.panel_combo.addItem(p["name"])
        
    def populate_circuits(self):
        circuits = discover_circuits(App.ActiveDocument)
        self.circuit_combo.addItem("Novo Circuito TUE")
        for c in circuits: self.circuit_combo.addItem(c["name"])

    def sync_values(self):
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

class SpecialSocketCommand:
    """Comando de Inserção de Tomadas de Uso Especial (TUE)"""
    def __init__(self):
        self.command_name = "Eletrica_InsertSpecialSocket"
        self.equipment_type = ""
        self.power_w = 1000.0
        self.power_factor = 1.0
        self.voltage = "127V"
        self.z_level = 1100.0
        self.rotation = 0
        self.amperage = "20A"
        self.tag_label = "TUE"
        self.level_options = []
        self.family_file = "Tomada_Simples_20A.FCStd"
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "Tomada_TUE_BR.svg"),
            'MenuText': 'Tomada Especial (TUE)',
            'ToolTip': 'Insere tomadas com potência pré-definida por equipamento',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, SpecialSocketTaskPanel, self.place_special_socket)
        self.engine.start()

    def make_preview_shape(self):
        # Combina a simbologia 2D e o modelo 3D real no fantasma para TUE
        try:
            from .special_socket_bim import make_special_socket_plan_symbol
            from .socket_bim import load_socket_family_shape, normalize_socket_shape
            
            # 1. Tenta carregar a simbologia 2D
            sym_shape = None
            try:
                h_label = "Alta" if self.z_level > 1600 else "Média" if self.z_level > 700 else "Baixa"
                sym_shape = make_special_socket_plan_symbol(h_label, "1 Módulo", self.amperage)
            except Exception:
                pass
            
            # 2. Tenta carregar o modelo 3D real da tomada
            model_shape = None
            try:
                raw = load_socket_family_shape(self.family_file)
                model_shape = normalize_socket_shape(raw)
                if model_shape:
                    model_shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180.0)
            except Exception:
                pass
                
            shapes = []
            if model_shape:
                shapes.append(model_shape)
            if sym_shape:
                shapes.append(sym_shape)
                
            if shapes:
                return Part.makeCompound(shapes)
        except Exception:
            pass

        # Fallback seguro
        return Part.makeBox(80, 120, 2)

    def place_special_socket(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_TUE")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (1.0, 0.5, 0.0)
                obj.ViewObject.Transparency = 20
        else:
            # Matriz Cache
            matriz_label = f"Matriz_TUE_{self.tag_label}_{self.voltage}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMSpecialSocket(matriz)
                matriz.SourceFile = self.family_file
                matriz.Label = f"Matriz TUE {self.tag_label}"
                doc.recompute([matriz])

            # Instância Link
            obj = doc.addObject("App::Link", f"TUE_{self.tag_label}")
            obj.LinkedObject = matriz
            
            # Propriedades TUE
            def _set_prop(name, value, group="BIM_Engenharia", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _set_prop("EquipmentType", self.equipment_type)
            _set_prop("Power", self.power_w, ptype="App::PropertyFloat")
            _set_prop("Voltage", self.voltage)
            _set_prop("PowerFactor", self.power_factor, ptype="App::PropertyFloat")
            _set_prop("Tag", f"TUE-{self.tag_label}")
            _set_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")
            _set_prop("TipoBIM", "Tomada Especial", group="BIM_Classificacao")

            # Cor de Destaque (Laranja para TUE)
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (1.0, 0.5, 0.0)

            obj.Label = f"TUE {self.equipment_type}"
            
            # Símbolo 2D
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(App.Vector(0,0,1), self.rotation + 180))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            from .special_socket_bim import make_special_socket_plan_symbol
            h_label = "Alta" if self.z_level > 1600 else "Média" if self.z_level > 700 else "Baixa"
            shape = make_special_socket_plan_symbol(h_label, "1 Módulo", self.amperage)
            
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py + 18.0, 0), App.Rotation(App.Vector(0,0,1), self.rotation))
            
            # Cor laranja no 2D também
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (1.0, 0.5, 0.0)
                sym_obj.ViewObject.LineWidth = 2.5
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertSpecialSocket', SpecialSocketCommand())
