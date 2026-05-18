import FreeCAD
import FreeCADGui
import os
try:
    from PySide import QtCore, QtWidgets, QtGui
except ImportError:
    try:
        from PySide2 import QtCore, QtWidgets, QtGui
    except ImportError:
        from PySide6 import QtCore, QtWidgets, QtGui

from EletricaLogic.i18n import tr
from EletricaLogic.Settings import ProjectSettings

class ProjectMetadataDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ProjectMetadataDialog, self).__init__(parent)
        self.setWindowTitle(tr("Propriedades Master do Projeto"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        self.obj = ProjectSettings.get_project_data_obj()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Cabeçalho Premium
        header = QtWidgets.QLabel(tr("Configuração de Metadados BIM"))
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)
        
        # --- TAB GERAL ---
        tab_geral = QtWidgets.QWidget()
        layout_geral = QtWidgets.QFormLayout(tab_geral)
        self.field_project_name = QtWidgets.QLineEdit()
        self.field_author = QtWidgets.QLineEdit()
        self.field_type = QtWidgets.QComboBox()
        self.field_type.addItems([tr("Residencial"), tr("Comercial"), tr("Industrial"), tr("Hospitalar"), tr("Público")])
        
        layout_geral.addRow(tr("Nome do Projeto:"), self.field_project_name)
        layout_geral.addRow(tr("Autor / Engenheiro:"), self.field_author)
        layout_geral.addRow(tr("Tipo de Obra:"), self.field_type)
        self.tabs.addTab(tab_geral, tr("Geral"))
        
        # --- TAB TÉCNICO ---
        tab_tecnico = QtWidgets.QWidget()
        scroll_tecnico = QtWidgets.QScrollArea()
        scroll_tecnico.setWidgetResizable(True)
        content_tecnico = QtWidgets.QWidget()
        layout_tecnico = QtWidgets.QFormLayout(content_tecnico)
        
        self.field_utility = QtWidgets.QLineEdit()
        self.field_primary_v = QtWidgets.QLineEdit()
        self.field_secondary_v = QtWidgets.QComboBox()
        self.field_secondary_v.addItems(["127V", "220V", "380V", "440V", "127/220V", "220/380V"])
        
        self.field_system = QtWidgets.QComboBox()
        self.field_system.addItems(["Monofasico (F+N)", "Bifasico (2F+N)", "Trifasico (3F+N)"])
        
        self.field_trafo_power = QtWidgets.QDoubleSpinBox()
        self.field_trafo_power.setRange(0, 5000)
        self.field_trafo_power.setSuffix(" kVA")
        
        self.field_icc = QtWidgets.QDoubleSpinBox()
        self.field_icc.setRange(0, 100)
        self.field_icc.setSuffix(" kA")
        
        self.field_material = QtWidgets.QComboBox()
        self.field_material.addItems(["Cobre", "Aluminio"])
        
        self.field_insulation = QtWidgets.QComboBox()
        self.field_insulation.addItems(["PVC 70C", "EPR 90C", "XLPE 90C"])
        
        self.field_fp = QtWidgets.QDoubleSpinBox()
        self.field_fp.setRange(0.1, 1.0)
        self.field_fp.setSingleStep(0.01)
        
        layout_tecnico.addRow(tr("Concessionária:"), self.field_utility)
        layout_tecnico.addRow(tr("Tensão Primária (MT):"), self.field_primary_v)
        layout_tecnico.addRow(tr("Tensão Secundária (BT):"), self.field_secondary_v)
        layout_tecnico.addRow(tr("Sistema de Fases:"), self.field_system)
        layout_tecnico.addRow(tr("Potência Trafo:"), self.field_trafo_power)
        layout_tecnico.addRow(tr("Icc Concessionária:"), self.field_icc)
        layout_tecnico.addRow(tr("Material Condutor:"), self.field_material)
        layout_tecnico.addRow(tr("Isolação Padrão:"), self.field_insulation)
        layout_tecnico.addRow(tr("Fator de Potência Global:"), self.field_fp)
        
        scroll_tecnico.setWidget(content_tecnico)
        vbox_tecnico = QtWidgets.QVBoxLayout(tab_tecnico)
        vbox_tecnico.addWidget(scroll_tecnico)
        self.tabs.addTab(tab_tecnico, tr("Técnico"))
        
        # --- TAB RESPONSÁVEL ---
        tab_resp = QtWidgets.QWidget()
        layout_resp = QtWidgets.QFormLayout(tab_resp)
        self.field_designer_name = QtWidgets.QLineEdit()
        self.field_crea = QtWidgets.QLineEdit()
        self.field_art = QtWidgets.QLineEdit()
        
        layout_resp.addRow(tr("Nome Completo:"), self.field_designer_name)
        layout_resp.addRow(tr("CREA / CFT:"), self.field_crea)
        layout_resp.addRow(tr("Número da ART:"), self.field_art)
        self.tabs.addTab(tab_resp, tr("Responsável"))
        
        # Botões
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_data(self):
        if not self.obj: return
        self.field_project_name.setText(self.obj.ProjectName)
        self.field_author.setText(self.obj.Author)
        self.field_type.setCurrentText(self.obj.ProjectType)
        
        self.field_utility.setText(self.obj.Utility)
        self.field_primary_v.setText(self.obj.PrimaryVoltage)
        self.field_secondary_v.setCurrentText(self.obj.Voltage)
        self.field_system.setCurrentText(self.obj.SystemPhases)
        self.field_trafo_power.setValue(self.obj.TrafoPower)
        self.field_icc.setValue(self.obj.Icc_Concessionaria)
        self.field_material.setCurrentText(self.obj.ConductorMaterial)
        self.field_insulation.setCurrentText(self.obj.InsulationType)
        self.field_fp.setValue(self.obj.PowerFactor)
        
        self.field_designer_name.setText(self.obj.DesignerName)
        self.field_crea.setText(self.obj.CREA)
        self.field_art.setText(self.obj.ART)

    def accept(self):
        # Salvar dados no objeto do FreeCAD
        doc = FreeCAD.ActiveDocument
        doc.openTransaction(tr("Atualizar Metadados do Projeto"))
        try:
            self.obj.ProjectName = self.field_project_name.text()
            self.obj.Author = self.field_author.text()
            self.obj.ProjectType = self.field_type.currentText()
            
            self.obj.Utility = self.field_utility.text()
            self.obj.PrimaryVoltage = self.field_primary_v.text()
            self.obj.Voltage = self.field_secondary_v.currentText()
            self.obj.SystemPhases = self.field_system.currentText()
            self.obj.TrafoPower = self.field_trafo_power.value()
            self.obj.Icc_Concessionaria = self.field_icc.value()
            self.obj.ConductorMaterial = self.field_material.currentText()
            self.obj.InsulationType = self.field_insulation.currentText()
            self.obj.PowerFactor = self.field_fp.value()
            
            self.obj.DesignerName = self.field_designer_name.text()
            self.obj.CREA = self.field_crea.text()
            self.obj.ART = self.field_art.text()
            
            doc.commitTransaction()
            super(ProjectMetadataDialog, self).accept()
        except Exception as e:
            doc.abortTransaction()
            QtWidgets.QMessageBox.critical(self, "Erro", tr("Falha ao salvar metadados: ") + str(e))

class GlobalSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(GlobalSettingsDialog, self).__init__(parent)
        self.setWindowTitle(tr("Configurações Globais - Eletrica"))
        self.setMinimumWidth(550)
        
        self.param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Eletrica")
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        group_paths = QtWidgets.QGroupBox(tr("Caminhos da Biblioteca"))
        layout_paths = QtWidgets.QGridLayout(group_paths)
        
        self.path_3d_edit = QtWidgets.QLineEdit()
        self.path_2d_edit = QtWidgets.QLineEdit()
        
        btn_browse_3d = QtWidgets.QPushButton(tr("Selecionar..."))
        btn_browse_2d = QtWidgets.QPushButton(tr("Selecionar..."))
        
        btn_open_3d = QtWidgets.QPushButton(tr("Abrir Pasta"))
        btn_open_2d = QtWidgets.QPushButton(tr("Abrir Pasta"))
        
        layout_paths.addWidget(QtWidgets.QLabel(tr("Biblioteca 3D (Componentes):")), 0, 0)
        layout_paths.addWidget(self.path_3d_edit, 0, 1)
        layout_paths.addWidget(btn_browse_3d, 0, 2)
        layout_paths.addWidget(btn_open_3d, 0, 3)
        
        layout_paths.addWidget(QtWidgets.QLabel(tr("Biblioteca 2D (Simbologia):")), 1, 0)
        layout_paths.addWidget(self.path_2d_edit, 1, 1)
        layout_paths.addWidget(btn_browse_2d, 1, 2)
        layout_paths.addWidget(btn_open_2d, 1, 3)
        
        layout.addWidget(group_paths)
        
        # Carregar valores atuais
        default_base = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Library")
        self.path_3d_edit.setText(self.param.GetString("Path3D", os.path.join(default_base, "3D")))
        self.path_2d_edit.setText(self.param.GetString("Path2D", os.path.join(default_base, "2D")))
        
        # Conexões
        btn_browse_3d.clicked.connect(lambda: self.browse_path(self.path_3d_edit))
        btn_browse_2d.clicked.connect(lambda: self.browse_path(self.path_2d_edit))
        btn_open_3d.clicked.connect(lambda: os.startfile(self.path_3d_edit.text()))
        btn_open_2d.clicked.connect(lambda: os.startfile(self.path_2d_edit.text()))
        
        # Botões Rodapé
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def browse_path(self, edit_field):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, tr("Selecionar Pasta"), edit_field.text())
        if path:
            edit_field.setText(path)

    def save_settings(self):
        self.param.SetString("Path3D", self.path_3d_edit.text())
        self.param.SetString("Path2D", self.path_2d_edit.text())
        QtWidgets.QMessageBox.information(self, tr("Sucesso"), tr("Configurações salvas com sucesso!"))
        self.accept()

class ServiceEntranceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ServiceEntranceDialog, self).__init__(parent)
        self.setWindowTitle(tr("Assistente de Entrada de Serviço"))
        self.setMinimumWidth(400)
        
        from EletricaLogic.ServiceEntrance import ServiceEntranceWizard
        self.data = ServiceEntranceWizard.get_utilities_data()
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        form = QtWidgets.QFormLayout()
        self.combo_utility = QtWidgets.QComboBox()
        self.combo_utility.addItems(sorted(self.data.keys()))
        
        self.spin_kw = QtWidgets.QDoubleSpinBox()
        self.spin_kw.setRange(0.1, 500)
        self.spin_kw.setValue(15.0)
        self.spin_kw.setSuffix(" kW")
        
        form.addRow(tr("Concessionária:"), self.combo_utility)
        form.addRow(tr("Carga Instalada (kW):"), self.spin_kw)
        layout.addLayout(form)
        
        self.info_box = QtWidgets.QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setMaximumHeight(100)
        self.info_box.setStyleSheet("background-color: #f8f9fa; color: #2c3e50; border: 1px solid #dee2e6;")
        layout.addWidget(self.info_box)
        
        self.spin_kw.valueChanged.connect(self.update_preview)
        self.combo_utility.currentTextChanged.connect(self.update_preview)
        
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.update_preview()

    def update_preview(self):
        from EletricaLogic.ServiceEntrance import ServiceEntranceWizard
        rec = ServiceEntranceWizard.recommend_entrance(self.combo_utility.currentText(), self.spin_kw.value())
        if rec:
            txt = f"<b>{tr('Recomendação Técnica:')}</b><br/>"
            txt += f"{tr('Categoria:')} {rec['fase']}<br/>"
            txt += f"{tr('Disjuntor:')} {rec['disjuntor']} | {tr('Cabo:')} {rec['cabo']}<br/>"
            txt += f"{tr('Caixa:')} {rec['caixa']}"
            self.info_box.setHtml(txt)

    def accept(self):
        from EletricaLogic.ServiceEntrance import ServiceEntranceWizard
        ServiceEntranceWizard.create_entrance_point(self.combo_utility.currentText(), self.spin_kw.value())
        super(ServiceEntranceDialog, self).accept()

def show_service_entrance_dialog():
    dialog = ServiceEntranceDialog(FreeCADGui.getMainWindow())
    dialog.exec_()

def show_metadata_dialog():
    dialog = ProjectMetadataDialog(FreeCADGui.getMainWindow())
    dialog.exec_()
