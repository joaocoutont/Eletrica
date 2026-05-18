import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import os
import Arch
from GeometryScripts.junction_box_bim import ProfessionalBIMJunctionBox
from GeometryScripts.bim_placement_core import BIMPlacementEngine

class JunctionBoxTaskPanel:
    """Interface do Configurador de Caixas de Passagem"""
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
        
        # TIPO
        self.scroll_layout.addWidget(QtGui.QLabel("Modelo Industrial / Tipo:"))
        self.type_combo = QtGui.QComboBox()
        self.type_combo.addItems([
            "4x2 PVC (Embutir)", "4x4 PVC (Embutir)", 
            "4x2 PVC (Sobrepor)", "4x4 PVC (Sobrepor)",
            "4x2 Alumínio (Sobrepor)", "4x4 Alumínio (Sobrepor)", 
            "4x2 Alumínio (Embutir)", "Octogonal (Laje/Embutir)",
            "Chapa Aço (20x20)", "Chapa Aço (30x30)", "Chapa Aço (40x40)",
            "Telecom VDI (20x20)", "Telecom VDI (30x30)", 
            "Passagem Solo (40x40)", "Passagem Solo (60x60)", 
            "Inspeção Aterramento", "Tomada de Piso (4x4)", 
            "Ar Condicionado (Dreno)", "Incêndio (Alarme)", "Customizada"
        ])
        self.type_combo.currentTextChanged.connect(self.sync_values)
        self.scroll_layout.addWidget(self.type_combo)

        # GRUPO: CATÁLOGO
        cat_group = QtGui.QGroupBox("Catálogo Industrial (Brasil)")
        cat_form = QtGui.QFormLayout()
        
        self.manu_combo = QtGui.QComboBox()
        self.manu_combo.addItems(["Genérico", "Tigre", "Amanco", "Tramontina", "Wetzel", "Daisa"])
        self.manu_combo.currentTextChanged.connect(self.sync_values)
        cat_form.addRow("Fabricante:", self.manu_combo)
        
        self.model_in = QtGui.QLineEdit("Padrão")
        self.model_in.setPlaceholderText("Ex: Tigreflex, Condulete...")
        self.model_in.textChanged.connect(self.sync_values)
        cat_form.addRow("Modelo/Ref:", self.model_in)
        
        self.info_label = QtGui.QLabel("Padrão: Dimensões Genéricas")
        self.info_label.setStyleSheet("color: #555; font-style: italic;")
        cat_form.addRow("Status:", self.info_label)
        
        cat_group.setLayout(cat_form)
        self.scroll_layout.addWidget(cat_group)
        
        # ALTURA Z
        self.scroll_layout.addWidget(QtGui.QLabel("Altura Z (mm):"))
        self.z_in = QtGui.QDoubleSpinBox(); self.z_in.setRange(-5000, 10000); self.z_in.setValue(1100)
        self.z_in.valueChanged.connect(self.sync_values)
        self.scroll_layout.addWidget(self.z_in)

        # ROTAÇÃO
        self.scroll_layout.addWidget(QtGui.QLabel("Rotação (Graus):"))
        self.rot_in = QtGui.QSpinBox(); self.rot_in.setRange(0, 360); self.rot_in.setSingleStep(90)
        self.rot_in.valueChanged.connect(self.sync_values)
        self.scroll_layout.addWidget(self.rot_in)

        self.scroll_layout.addStretch()
        self.scroll_layout.addWidget(QtGui.QLabel("Clique no 3D para inserir\nEspaço p/ girar | ESC p/ sair"))
        
    def sync_values(self):
        self.command.box_type = self.type_combo.currentText()
        self.command.manufacturer = self.manu_combo.currentText()
        self.command.model = self.model_in.text()
        self.command.z_level = self.z_in.value()
        self.command.rotation = self.rot_in.value()
        
        # Preview de Dimensões
        l, w, h = (100, 100, 50)
        if self.command.manufacturer in ["Tigre", "Amanco"]:
            l, w, h = (102, 61, 45) if "4x2" in self.command.box_type else (102, 102, 45)
            self.info_label.setText(f"NBR 15465 ({l}x{w}x{h}mm)")
        elif self.command.manufacturer in ["Tramontina", "Wetzel", "Daisa"]:
            l, w, h = (110, 60, 50) if "Alumínio" in self.command.box_type else (101, 51, 45)
            self.info_label.setText(f"Metálica ({l}x{w}x{h}mm)")
        else:
            self.info_label.setText("Dimensões Customizáveis")

    def sync_ui(self):
        """Atualiza a UI a partir do comando (ex: após apertar Espaço)"""
        self.rot_in.blockSignals(True)
        self.rot_in.setValue(self.command.rotation)
        self.rot_in.blockSignals(False)

    def accept(self):
        Gui.Control.closeDialog()
        return True

class JunctionBoxCommand:
    """Comando de Inserção de Caixas usando o Motor Universal"""
    def __init__(self):
        self.box_type = "4x2 PVC (Embutir)"
        self.manufacturer = "Genérico"
        self.model = "Padrão"
        self.z_level = 1100.0
        self.rotation = 0
        self.engine = None
        self.command_name = "Eletrica_JunctionBox"

    def IsActive(self):
        return App.ActiveDocument is not None

    def GetResources(self):
        icon_path = os.path.join(App.getUserAppDataDir(), "Mod", "Eletrica", "Icons", "JunctionBox.svg")
        return {
            'Pixmap': icon_path, 
            'MenuText': 'Caixa de Passagem BIM', 
            'ToolTip': 'Insere caixas usando a Mira BIM',
            'Checkable': True
        }

    def Activated(self, *args, **kwargs):
        if BIMPlacementEngine.active_engine is not None:
            if isinstance(BIMPlacementEngine.active_engine.cmd, JunctionBoxCommand):
                BIMPlacementEngine.active_engine.stop()
                return

        self.engine = BIMPlacementEngine(self, JunctionBoxTaskPanel, self.place_box)
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
        # Caixinha com dimensões baseadas no tipo selecionado (Ex: "4x2 PVC" ou "4x4") "em pé"
        is_4x4 = "4x4" in getattr(self, "box_type", "") or "Octogonal" in getattr(self, "box_type", "")
        w = 120.0 if is_4x4 else 80.0
        h = 120.0  # 120mm de altura padrão
        d = 45.0 # profundidade padrão
        
        shape = Part.makeBox(w, h, d)
        shape.translate(App.Vector(-w/2, -h/2, -d))
        return shape

    def place_box(self, point, is_ghost=False):
        doc = App.ActiveDocument
        px = point.x if hasattr(point, "x") else point[0]
        py = point.y if hasattr(point, "y") else point[1]
        final_z = self.z_level
        target_pos = App.Vector(px, py, final_z)
        target_rot = App.Rotation(App.Vector(0,0,1), self.rotation)

        if is_ghost:
            obj = doc.addObject("Part::Feature", "GHOST_JunctionBox")
            obj.Shape = self.make_preview_shape()
            doc.recompute()
            if obj.ViewObject is not None:
                obj.ViewObject.Transparency = 70
                obj.ViewObject.ShapeColor = (0.5, 0.5, 1.0)
                obj.ViewObject.Selectable = False
                if hasattr(obj.ViewObject, "ShowInTree"):
                    obj.ViewObject.ShowInTree = False
            obj.Placement = App.Placement(target_pos, target_rot)
            return obj
            
        count = len([o for o in doc.Objects if "Caixa de Passagem BIM" in o.Label]) + 1
        obj = doc.addObject("Part::FeaturePython", f"Caixa_{count:03d}")
        ProfessionalBIMJunctionBox(obj)
        
        obj.BoxType = self.box_type
        obj.Manufacturer = self.manufacturer
        obj.CommercialModel = self.model
        obj.Placement = App.Placement(target_pos, target_rot)
        
        # Cor Industrial
        color = (0.8, 0.8, 0.8)
        if "Incêndio" in self.box_type: color = (1.0, 0.0, 0.0)
        elif self.manufacturer == "Tigre": color = (1.0, 0.5, 0.0)
        elif self.manufacturer == "Amanco": color = (1.0, 1.0, 0.0)
        elif "Alumínio" in self.box_type or self.manufacturer in ["Tramontina", "Wetzel"]: color = (0.75, 0.75, 0.8)
        elif "Passagem Solo" in self.box_type: color = (0.5, 0.5, 0.5)
        elif "Piso" in self.box_type: color = (0.8, 0.7, 0.3)
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Proxy = 0
        label = f"Caixa de Passagem BIM {count:03d}"
        component = Arch.makeComponent(obj)
        target = component or obj
        if component:
            component.Label = label
        obj.Label = label
        
        # Organiza a caixinha na árvore de projeto dentro do nível/pavimento correto de forma inteligente
        try:
            levels = [o for o in doc.Objects if o.isDerivedFrom("App::DocumentObjectGroup") and hasattr(o, "addObject") and "BuildingPart" in o.TypeId]
            if levels:
                closest_level = min(levels, key=lambda lvl: abs(float(getattr(lvl, "LevelElevation", 0.0)) - self.z_level))
                closest_level.addObject(target)
        except Exception:
            pass
            
        doc.recompute()
        print(f"Caixa {count} inserida.")

Gui.addCommand('Eletrica_JunctionBox', JunctionBoxCommand())
