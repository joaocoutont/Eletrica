# ⚡ SUITE ELITE BIM - Engenharia Elétrica
# Autor: João Couto
# Contato: joaocoutont@hotmail.com
# Sidebar Dashboard for Eletrica Workbench
# Dashboard Lateral - Eletrica BIM
import FreeCAD
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

class EletricaDashboard(QtWidgets.QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Eletrica BIM")
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        
        self.main_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        
        # Estilo Premium
        self.main_widget.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: white; font-family: 'Segoe UI'; }
            QLabel { font-size: 12px; }
            .header { font-size: 16px; font-weight: bold; color: #ffcc00; margin-bottom: 10px; }
            .kpi_box { background-color: #3d3d3d; border-radius: 5px; padding: 10px; margin-bottom: 5px; }
            .value { font-size: 18px; font-weight: bold; color: #00ff00; }
            .alert { color: #ff4444; font-weight: bold; }
        """)
        
        self.init_ui()
        self.setWidget(self.main_widget)
        
    def init_ui(self):
        # Titulo
        lbl_title = QtWidgets.QLabel("MÉTRICAS DO PROJETO")
        lbl_title.setProperty("class", "header")
        self.layout.addWidget(lbl_title)
        
        # KPI 1: Potência Instalada
        self.box_power = self.create_kpi_box("Potência Instalada", "0 VA", "power_val")
        self.layout.addWidget(self.box_power)
        
        # KPI 2: Demanda Estimada
        self.box_demand = self.create_kpi_box("Demanda (NBR 5410)", "0 kVA", "demand_val")
        self.layout.addWidget(self.box_demand)
        
        # KPI 3: Custo Estimado
        self.box_cost = self.create_kpi_box("Orçamento Estimado", "R$ 0,00", "cost_val")
        self.layout.addWidget(self.box_cost)
        
        # Auditoria
        self.lbl_audit = QtWidgets.QLabel("Status: ✅ Projeto Saudável")
        self.layout.addWidget(self.lbl_audit)
        
        # Botão Atualizar
        self.btn_refresh = QtWidgets.QPushButton("Atualizar Métricas")
        self.btn_refresh.clicked.connect(self.update_metrics)
        self.layout.addWidget(self.btn_refresh)
        
        self.layout.addStretch()
        
    def create_kpi_box(self, label, value, object_name):
        box = QtWidgets.QFrame()
        box.setProperty("class", "kpi_box")
        l = QtWidgets.QVBoxLayout(box)
        l.addWidget(QtWidgets.QLabel(label))
        val = QtWidgets.QLabel(value)
        val.setObjectName(object_name)
        val.setProperty("class", "value")
        l.addWidget(val)
        return box
        
    def update_metrics(self):
        # Aqui chamamos a logica de calculo em tempo real
        total_va = 0.0
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Potencia"):
                total_va += float(obj.Potencia)
                
        self.findChild(QtWidgets.QLabel, "power_val").setText(f"{total_va:.0f} VA")
        self.findChild(QtWidgets.QLabel, "demand_val").setText(f"{(total_va*0.6)/1000.0:.2f} kVA")
        
        # Alerta se houver erros (Simulacao)
        if total_va > 15000:
            self.lbl_audit.setText("Status: ⚠️ Verifique Circuitos")
            self.lbl_audit.setStyleSheet("color: #ff4444;")
        else:
            self.lbl_audit.setText("Status: ✅ Projeto Saudável")
            self.lbl_audit.setStyleSheet("color: #00ff00;")

def toggle_dashboard():
    import FreeCADGui
    mw = FreeCADGui.getMainWindow()
    existing = mw.findChild(QtWidgets.QDockWidget, "Dashboard Eletrica BIM")
    
    if existing:
        existing.setVisible(not existing.isVisible())
    else:
        db = EletricaDashboard()
        mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, db)
