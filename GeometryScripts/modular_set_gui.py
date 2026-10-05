import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import math
import Part
from .modular_set_bim import ProfessionalBIMModularSet
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, create_default_bim_levels, discover_panel_boards,
    discover_circuits, discover_spaces_or_sectors
)
from .socket_bim import make_socket_plan_symbol
from .switch_bim import make_switch_plan_symbol

MODULAR_COMPOSITIONS = {
    "1 Tomada + 1 Interruptor Simples": {
        "modules": ["Tomada 10A", "Interruptor Simples"],
        "3d_file": "Placa_1T_1Int.FCStd",
        "label": "T+I"
    },
    "2 Tomadas + 1 Interruptor Simples": {
        "modules": ["Tomada 10A", "Tomada 10A", "Interruptor Simples"],
        "3d_file": "Placa_2T_1Int.FCStd",
        "label": "2T+I"
    },
    "1 Tomada + 2 Interruptores Simples": {
        "modules": ["Tomada 10A", "Interruptor 2 Teclas"],
        "3d_file": "Placa_1T_2Int.FCStd",
        "label": "T+2I"
    },
    "3 Tomadas 10A": {
        "modules": ["Tomada 10A", "Tomada 10A", "Tomada 10A"],
        "3d_file": "Placa_3T.FCStd",
        "label": "3T"
    },
    "2 Interruptores Paralelos": {
        "modules": ["Interruptor Paralelo", "Interruptor Paralelo"],
        "3d_file": "Placa_2Int_Paralelo.FCStd",
        "label": "2IP"
    }
}

def _infer_modular_composition_from_file(fname):
    base = os.path.splitext(os.path.basename(fname))[0]
    text = base.lower()
    import re
    match = re.search(r"t(\d+)\s*[-_]\s*s(\d+)", text)
    if not match:
        return None
    socket_count = int(match.group(1))
    switch_count = int(match.group(2))
    modules = (["Tomada 10A"] * socket_count) + (["Interruptor Simples"] * switch_count)
    composition = f"T{socket_count}-S{switch_count}"
    return {
        "modules": modules,
        "3d_file": f"Conjuntos_Modulares/{fname}",
        "label": composition,
        "composition": composition,
        "socket_count": socket_count,
        "switch_count": switch_count,
    }

def _available_modular_compositions():
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_path = os.path.join(base_path, "Library", "3D", "Conjuntos_Modulares")
    result = {}
    if os.path.isdir(lib_path):
        for fname in sorted(os.listdir(lib_path)):
            if not fname.lower().endswith(".fcstd"):
                continue
            data = _infer_modular_composition_from_file(fname)
            if data:
                result[f"Conjunto Modular {data['composition']}"] = data
    return result or MODULAR_COMPOSITIONS

class ModularSetTaskPanel:
    """Interface para Conjuntos Modulares (Placas Combinadas)"""
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
        
        # --- SELEÇÃO DE COMPOSIÇÃO ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Composição do Conjunto:</b>"))
        self.comp_list = QtGui.QListWidget()
        self.compositions = _available_modular_compositions()
        for name in sorted(self.compositions.keys()):
            item = QtGui.QListWidgetItem(name)
            self.comp_list.addItem(item)
        self.comp_list.currentItemChanged.connect(self.on_comp_selected)
        self.scroll_layout.addWidget(self.comp_list)
        
        # AJUSTES
        adj_group = QtGui.QGroupBox("Ajustes")
        adj_form = QtGui.QFormLayout()
        
        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 5000); self.z_in.setValue(1100)
        self.z_in.valueChanged.connect(self.sync_values)
        adj_form.addRow("Altura (mm):", self.z_in)

        self.rot_in = QtGui.QSpinBox(); self.rot_in.setRange(0, 360); self.rot_in.setSingleStep(90)
        self.rot_in.valueChanged.connect(self.sync_values)
        adj_form.addRow("Rotação (°):", self.rot_in)
        
        adj_group.setLayout(adj_form)
        self.scroll_layout.addWidget(adj_group)

        # BIM
        bim_group = QtGui.QGroupBox("BIM")
        bim_form = QtGui.QFormLayout()
        self.panel_combo = QtGui.QComboBox()
        self.populate_panels()
        bim_form.addRow("Quadro:", self.panel_combo)
        bim_group.setLayout(bim_form)
        self.scroll_layout.addWidget(bim_group)

        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(QtGui.QLabel("Dica: Use 4x4 para mais de 3 módulos."))

    def on_comp_selected(self, current):
        if not current: return
        name = current.text()
        data = self.compositions.get(name)
        if not data: return
        
        self.command.composition_name = name
        self.command.modules = data["modules"]
        self.command.family_file = data["3d_file"]
        self.command.tag_label = data["label"]
        self.command.socket_count = int(data.get("socket_count", 0) or 0)
        self.command.switch_count = int(data.get("switch_count", 0) or 0)
        self.command.composition_code = data.get("composition", data["label"])
        
        self.refresh_ghost()

    def populate_panels(self):
        panels = discover_panel_boards(App.ActiveDocument)
        self.panel_combo.addItem("Sem quadro")
        for p in panels: self.panel_combo.addItem(p["name"])

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

class ModularSetCommand:
    """Comando de Inserção de Conjuntos Modulares BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertModularSet"
        self.composition_name = ""
        self.modules = []
        self.z_level = 1100.0
        self.rotation = 0
        self.family_file = "Placa_Padrao.FCStd"
        self.tag_label = "CONJ"
        self.composition_code = ""
        self.socket_count = 0
        self.switch_count = 0
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "Switch.svg"),
            'MenuText': 'Conjunto Modular',
            'ToolTip': 'Insere placa com múltiplos módulos combinados',
            'Checkable': True
        }

    def Activated(self, *args, **kwargs):
        self.engine = BIMPlacementEngine(self, ModularSetTaskPanel, self.place_modular_set)
        self.engine.start()

    def make_preview_shape(self):
        """Cria uma simbologia 2D composta."""
        try:
            parts = []
            # Separa os módulos para desenhar símbolos lado a lado (simplificado)
            sockets = [m for m in self.modules if "Tomada" in m]
            switches = [m for m in self.modules if "Interruptor" in m]
            
            offset_x = 0
            for _ in sockets:
                sym = make_socket_plan_symbol("Média", "1 Módulo", "10A")
                if sym:
                    sym.translate(App.Vector(offset_x, 0, 0))
                    parts.append(sym)
                    offset_x += 160
            
            for _ in switches:
                sym = make_switch_plan_symbol("1 Tecla", "Simples")
                if sym:
                    sym.translate(App.Vector(offset_x, 0, 0))
                    parts.append(sym)
                    offset_x += 110
            
            if not parts:
                return Part.makeBox(120, 80, 2)
                
            return Part.makeCompound(parts)
        except Exception:
            return Part.makeBox(120, 80, 2)

    def place_modular_set(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_Modular")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.5, 0.5, 1.0)
                obj.ViewObject.Transparency = 20
        else:
            matriz_label = f"Matriz_Modular_{self.tag_label}"
            matriz = doc.getObject(matriz_label)
            if not matriz:
                matriz = doc.addObject("Part::FeaturePython", matriz_label)
                ProfessionalBIMModularSet(matriz)
                matriz.SourceFile = self.family_file
                matriz.Modules = self.modules
                if hasattr(matriz, "Composition"):
                    matriz.Composition = self.composition_code
                if hasattr(matriz, "SocketCount"):
                    matriz.SocketCount = self.socket_count
                if hasattr(matriz, "SwitchCount"):
                    matriz.SwitchCount = self.switch_count
                doc.recompute([matriz])

            obj = doc.addObject("App::Link", f"Conjunto_{self.tag_label}")
            obj.LinkedObject = matriz
            
            def _add_prop(name, value, group="BIM_Composicao", ptype="App::PropertyString"):
                if not hasattr(obj, name): obj.addProperty(ptype, name, group)
                setattr(obj, name, value)

            _add_prop("Composition", self.composition_code or self.composition_name)
            _add_prop("FamilyCategory", "Conjunto Modular", group="BIM_Familia")
            _add_prop("IFC_Class", "IfcDistributionElement", group="BIM_Classificacao")
            _add_prop("TipoBIM", "ModularAssembly", group="BIM_Classificacao")
            _add_prop("SocketCount", self.socket_count, ptype="App::PropertyInteger")
            _add_prop("SwitchCount", self.switch_count, ptype="App::PropertyInteger")
            _add_prop("LoadClassification", "Misto", group="BIM_Engenharia")
            _add_prop("Tag", f"CONJ-{self.tag_label}", group="BIM_Classificacao")
            _add_prop("MountingHeight", self.z_level, group="BIM_Posicionamento", ptype="App::PropertyLength")

            obj.Label = f"Conjunto {self.composition_name}"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        obj.Placement = App.Placement(App.Vector(px, py, self.z_level), App.Rotation(App.Vector(0,0,1), self.rotation + 180))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            shape = self.make_preview_shape()
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py + 18.0, 0), App.Rotation(App.Vector(0,0,1), self.rotation))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.3, 0.3, 1.0)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertModularSet', ModularSetCommand())
