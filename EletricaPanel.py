# ⚡ Eletrica - Engenharia Elétrica
# Autor: João Couto
# Contato: joaocoutont@hotmail.com
# Sidebar Dashboard for Eletrica Workbench
# Dashboard Lateral - Eletrica
import FreeCAD
import FreeCADGui
from EletricaLogic.i18n import tr

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

class ClickableFrame(QtWidgets.QFrame):
    """Um QFrame que emite um sinal ao ser clicado."""
    clicked = QtCore.Signal(str)

    def __init__(self, kpi_type):
        super().__init__()
        self.kpi_type = kpi_type

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.kpi_type)
        super().mousePressEvent(event)

class EletricaDashboard(QtWidgets.QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("Dashboard"))
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        
        self.main_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        
        # Estilo Premium para FreeCAD 1.1 Dark Mode
        self.main_widget.setStyleSheet("""
            QWidget { background-color: #1a1a1a; color: #e0e0e0; font-family: 'Segoe UI', 'Ubuntu', sans-serif; }
            QLabel { font-size: 11px; }
            .header { font-size: 14px; font-weight: bold; color: #f1c40f; margin-bottom: 12px; border-bottom: 1px solid #333; padding-bottom: 5px; }
            .kpi_box { background-color: #2d2d2d; border: 1px solid #3d3d3d; border-radius: 8px; padding: 12px; margin-bottom: 8px; }
            .kpi_box:hover { background-color: #383838; border-color: #f1c40f; }
            .value { font-size: 18px; font-weight: bold; color: #2ecc71; }
            .alert { color: #e74c3c; font-weight: bold; }
            QPushButton { background-color: #3498db; color: white; border: none; border-radius: 4px; padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1c598a; }
        """)
        
        self.init_ui()
        self.setWidget(self.main_widget)
        
    def init_ui(self):
        # Titulo
        lbl_title = QtWidgets.QLabel(tr("Dashboard").upper())
        lbl_title.setProperty("class", "header")
        self.layout.addWidget(lbl_title)
        
        # KPI 1: Potência Instalada
        self.box_power = self.create_kpi_box(tr("Potencia Instalada"), "0 VA", "power_val", "power")
        self.layout.addWidget(self.box_power)
        
        # KPI 2: Demanda Estimada
        self.box_demand = self.create_kpi_box(tr("Demanda"), "0 kVA", "demand_val", "demand")
        self.layout.addWidget(self.box_demand)
        
        # KPI 3: Custo Estimado
        self.box_cost = self.create_kpi_box(tr("Orcamento"), "R$ 0,00", "cost_val", "budget")
        self.layout.addWidget(self.box_cost)
        
        # Auditoria
        self.lbl_audit = QtWidgets.QLabel(tr("Status: Saudavel"))
        self.layout.addWidget(self.lbl_audit)
        
        # Botão Atualizar
        self.btn_refresh = QtWidgets.QPushButton(tr("Atualizar"))
        self.btn_refresh.clicked.connect(self.update_metrics)
        self.layout.addWidget(self.btn_refresh)
        
        self.layout.addStretch()
        
    def create_kpi_box(self, label, value, object_name, kpi_type):
        box = ClickableFrame(kpi_type)
        box.setProperty("class", "kpi_box")
        box.clicked.connect(self.on_kpi_clicked)
        l = QtWidgets.QVBoxLayout(box)
        l.addWidget(QtWidgets.QLabel(label))
        val = QtWidgets.QLabel(value)
        val.setObjectName(object_name)
        val.setProperty("class", "value")
        l.addWidget(val)
        return box

    def on_kpi_clicked(self, kpi_type):
        """Lógica de seleção inteligente ao clicar nos KPIs."""
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        FreeCADGui.Selection.clearSelection()
        
        if kpi_type == "power" or kpi_type == "demand":
            # Seleciona todos os objetos com carga
            for obj in doc.Objects:
                if hasattr(obj, "Potencia"):
                    FreeCADGui.Selection.addSelection(obj)
            FreeCAD.Console.PrintMessage(f"Dashboard: Selecionando cargas do projeto.\n")
            
        elif kpi_type == "budget":
            # Seleciona infraestrutura e equipamentos
            for obj in doc.Objects:
                if hasattr(obj, "Potencia") or hasattr(obj, "Diameter"):
                    FreeCADGui.Selection.addSelection(obj)
            FreeCAD.Console.PrintMessage(f"Dashboard: Selecionando itens do orçamento.\n")
        
    def update_metrics(self):
        # Aqui chamamos a logica de calculo em tempo real
        from EletricaLogic.Calculator import ElectricalCalculator
        from EletricaLogic.Budget import BudgetManager
        from EletricaLogic.BOM import BOMManager
        
        doc = FreeCAD.ActiveDocument
        if not doc: return

        # 1. Obter dados brutos do Central Data Engine
        bom_data = BOMManager.get_raw_bom_data()
        
        # 2. Calcular Potência Instalada
        total_va = 0.0
        for obj in doc.Objects:
            if hasattr(obj, "Potencia"):
                total_va += float(obj.Potencia)
                
        self.findChild(QtWidgets.QLabel, "power_val").setText(f"{total_va:,.0f} VA")
        
        # 3. Demanda (Cálculo real NBR 5410)
        meta = doc.getObject("Eletrica_ProjectData")
        p_type = meta.ProjectType if meta and hasattr(meta, "ProjectType") else "Residencial"
        demand_kva = ElectricalCalculator.calculate_demand(total_va, project_type=p_type)
        self.findChild(QtWidgets.QLabel, "demand_val").setText(f"{demand_kva:.2f} kVA")
        
        # 4. Orçamento (Cálculo real via BudgetManager usando BOM unificado)
        try:
            _, total_cost = BudgetManager.generate_budget_report(bom_data)
            self.findChild(QtWidgets.QLabel, "cost_val").setText(f"R$ {total_cost:,.2f}")
        except:
            self.findChild(QtWidgets.QLabel, "cost_val").setText(tr("Erro no Calculo"))
        
        # Auditoria Visual
        if total_va > 20000:
            self.lbl_audit.setText(tr("Status: Carga Elevada"))
            self.lbl_audit.setStyleSheet("color: #ffaa00;")
        elif total_va == 0:
            self.lbl_audit.setText("Status: ⚪ Sem Cargas")
            self.lbl_audit.setStyleSheet("color: #aaaaaa;")
        else:
            self.lbl_audit.setText(tr("Status: Saudavel"))
            self.lbl_audit.setStyleSheet("color: #00ff00;")

def toggle_dashboard():
    import FreeCADGui
    mw = FreeCADGui.getMainWindow()
    existing = mw.findChild(QtWidgets.QDockWidget, "Dashboard Eletrica")
    
    if existing:
        existing.setVisible(not existing.isVisible())
    else:
        db = EletricaDashboard()
        mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, db)


class ToggleDashboardCommand:
    """Comando para exibir ou ocultar o Dashboard do projeto"""
    def Activated(self):
        try:
            toggle_dashboard()
        except Exception as e:
            import FreeCAD
            FreeCAD.Console.PrintError(f"Erro ao alternar Dashboard: {e}\n")

    def GetResources(self):
        import os
        import FreeCAD
        DIR = os.path.normpath(os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica"))
        icon_path = os.path.join(DIR, "Icons", "Dashboard.svg")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(DIR, "Icons", "Raio.svg") # fallback
        return {
            'Pixmap': icon_path,
            'MenuText': 'Exibir Dashboard Eletrica',
            'ToolTip': 'Liga/Desliga o painel lateral de métricas do projeto'
        }
