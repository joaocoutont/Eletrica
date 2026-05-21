import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Part
from .panel_bim import ProfessionalBIMPanel, make_panel_plan_symbol
from .bim_placement_core import BIMPlacementEngine

from .socket_gui import (
    discover_project_levels, _set_property
)

PANEL_TEMPLATES = {
    "Quadro 400x300x200 (Compacto)": {"w": 300, "h": 400, "d": 200, "type": "QDC (Distribuição)"},
    "Quadro 600x400x250 (Padrão)":  {"w": 400, "h": 600, "d": 250, "type": "QDC (Distribuição)"},
    "Quadro 800x600x300 (Grande)":   {"w": 600, "h": 800, "d": 300, "type": "QDC (Distribuição)"},
    "Coluna 2000x800x600 (QGBT)":    {"w": 800, "h": 2000, "d": 600, "type": "QGBT (Geral)"},
    "Console CCM (Motor Control)":   {"w": 600, "h": 1200, "d": 400, "type": "CCM (Motores)"}
}

class PanelTaskPanel:
    """Interface para Inserção de Quadros de Comando e Distribuição"""
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
        
        # --- SELEÇÃO DE TEMPLATE ---
        self.scroll_layout.addWidget(QtGui.QLabel("<b>Modelo de Quadro:</b>"))
        self.template_combo = QtGui.QComboBox()
        self.template_combo.addItems(sorted(PANEL_TEMPLATES.keys()))
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        self.scroll_layout.addWidget(self.template_combo)
        
        # DIMENSÕES CUSTOM
        dim_group = QtGui.QGroupBox("Dimensões Reais (mm)")
        dim_form = QtGui.QFormLayout()
        
        self.w_in = QtGui.QDoubleSpinBox(); self.w_in.setRange(50, 5000); self.w_in.setValue(400)
        self.w_in.valueChanged.connect(self.sync_values)
        dim_form.addRow("Largura (W):", self.w_in)

        self.h_in = QtGui.QDoubleSpinBox(); self.h_in.setRange(50, 5000); self.h_in.setValue(600)
        self.h_in.valueChanged.connect(self.sync_values)
        dim_form.addRow("Altura (H):", self.h_in)

        self.d_in = QtGui.QDoubleSpinBox(); self.d_in.setRange(50, 2000); self.d_in.setValue(200)
        self.d_in.valueChanged.connect(self.sync_values)
        dim_form.addRow("Profundidade (D):", self.d_in)
        
        dim_group.setLayout(dim_form)
        self.scroll_layout.addWidget(dim_group)

        # BIM / ENGENHARIA
        eng_group = QtGui.QGroupBox("Engenharia BIM")
        eng_form = QtGui.QFormLayout()
        
        self.type_combo = QtGui.QComboBox()
        self.type_combo.addItems(["QDC (Distribuição)", "QGBT (Geral)", "CCM (Motores)", "Quadro de Comando"])
        self.type_combo.currentTextChanged.connect(self.sync_values)
        eng_form.addRow("Função:", self.type_combo)

        self.mount_combo = QtGui.QComboBox()
        self.mount_combo.addItems(["Sobrepor", "Embutir", "Autosustentado (Coluna)"])
        self.mount_combo.currentTextChanged.connect(self.sync_values)
        eng_form.addRow("Montagem:", self.mount_combo)

        self.tag_in = QtGui.QLineEdit("QD-01")
        eng_form.addRow("TAG (Ident.):", self.tag_in)
        
        eng_group.setLayout(eng_form)
        self.scroll_layout.addWidget(eng_group)

        # POSIÇÃO
        pos_group = QtGui.QGroupBox("Instalação")
        pos_form = QtGui.QFormLayout()
        
        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(0, 10000); self.z_in.setValue(1200)
        pos_form.addRow("Altura do Topo (mm):", self.z_in)
        
        pos_group.setLayout(pos_form)
        self.scroll_layout.addWidget(pos_group)

        self.scroll_layout.addStretch()
        self.on_template_changed(self.template_combo.currentText())

    def on_template_changed(self, text):
        data = PANEL_TEMPLATES.get(text)
        if not data: return
        self.w_in.setValue(data["w"])
        self.h_in.setValue(data["h"])
        self.d_in.setValue(data["d"])
        self.type_combo.setCurrentText(data["type"])
        self.refresh_ghost()

    def sync_values(self):
        self.command.width = self.w_in.value()
        self.command.height = self.h_in.value()
        self.command.depth = self.d_in.value()
        self.command.panel_type = self.type_combo.currentText()
        self.command.mounting = self.mount_combo.currentText()
        self.command.tag = self.tag_in.text()
        self.command.z_level = self.z_in.value()
        self.refresh_ghost()

    def refresh_ghost(self):
        if hasattr(self.command, 'engine') and self.command.engine.ghost:
            self.command.engine.ghost.Shape = self.command.make_preview_shape()
            Gui.updateGui()

    def accept(self):
        self.sync_values()
        Gui.Control.closeDialog()
        return True

class PanelCommand:
    """Comando de Inserção de Quadros Elétricos BIM"""
    def __init__(self):
        self.command_name = "Eletrica_InsertPanel"
        self.width = 400.0
        self.height = 600.0
        self.depth = 200.0
        self.panel_type = "QDC (Distribuição)"
        self.mounting = "Sobrepor"
        self.tag = "QD-01"
        self.z_level = 1500.0
        self.engine = None

    def GetResources(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        return {
            'Pixmap': os.path.join(base_path, "Icons", "IndustrialPanel.svg"),
            'MenuText': 'Inserir Quadro de Comando',
            'ToolTip': 'Insere quadros de distribuição (QDC) ou comando (CCM) paramétricos',
            'Checkable': True
        }

    def Activated(self):
        self.engine = BIMPlacementEngine(self, PanelTaskPanel, self.place_panel)
        self.engine.start()

    def make_preview_shape(self):
        # O fantasma do quadro é o próprio sólido 3D em wireframe
        try:
            box = Part.makeBox(self.width, self.depth, self.height)
            box.translate(App.Vector(-self.width/2, 0, 0))
            return box
        except Exception:
            return Part.makeBox(400, 200, 600)

    def place_panel(self, point, is_ghost=False):
        doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_Panel")
            obj.Shape = self.make_preview_shape()
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.7, 0.7, 0.7)
                obj.ViewObject.Transparency = 50
        else:
            obj = doc.addObject("Part::FeaturePython", f"Quadro_{self.tag.replace('-','_')}")
            ProfessionalBIMPanel(obj)
            
            # Aplica parâmetros
            obj.Width = self.width
            obj.Height = self.height
            obj.Depth = self.depth
            obj.PanelType = self.panel_type
            obj.Mounting = self.mounting
            obj.Tag = self.tag
            
            # Recalcula para gerar a shape
            doc.recompute([obj])
            
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
            
            obj.Label = f"[{self.tag}] {self.panel_type.split(' ')[0]}"
            self._create_2d_symbol(doc, obj, point)

        px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
        # O Z do quadro geralmente é o topo ou base. Vamos usar o pé-direito - altura ou altura fixa.
        target_z = self.z_level - self.height if not is_ghost else self.z_level - self.height
        obj.Placement = App.Placement(App.Vector(px, py, max(0, target_z)), App.Rotation(0,0,0,1))
        doc.recompute()
        return obj

    def _create_2d_symbol(self, doc, instance_obj, point):
        try:
            shape = make_panel_plan_symbol(self.width, self.depth, self.panel_type)
            sym_obj = doc.addObject("Part::Feature", f"Sym2D_{instance_obj.Name}")
            sym_obj.Shape = shape
            sym_obj.Label = f"↗ {instance_obj.Label}"
            px, py = (point.x, point.y) if hasattr(point, 'x') else (point[0], point[1])
            sym_obj.Placement = App.Placement(App.Vector(px, py, 0), App.Rotation(0,0,0,1))
            if sym_obj.ViewObject:
                sym_obj.ViewObject.LineColor = (0.1, 0.1, 0.1)
                sym_obj.ViewObject.LineWidth = 2.0
        except Exception: pass

if hasattr(Gui, "addCommand"):
    Gui.addCommand('Eletrica_InsertPanel', PanelCommand())
