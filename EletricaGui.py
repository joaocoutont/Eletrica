# ⚡ Eletrica - Engenharia Elétrica
# Autor: João Couto
# Contato: joaocoutont@hotmail.com
# GUI Commands for Eletrica Workbench
import FreeCAD
import FreeCADGui
import os
from EletricaLogic.i18n import tr

# Caminho para os ícones de forma robusta
try:
    ICON_DIR = os.path.join(os.path.dirname(__file__), "Icons")
except NameError:
    ICON_DIR = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Icons")

# --- COMPATIBILIDADE PYSIDE2 / PYSIDE6 (FreeCAD 1.1+) ---
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

# --- 1. GRUPO: INÍCIO E CONFIGURAÇÃO ---

class StartNewProject:
    """Cria um novo documento e prepara o ambiente de desenho"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'StartProject.png'),
            'MenuText': tr('Iniciar Novo Projeto Elétrico'),
            'ToolTip': tr('Cria um novo documento e prepara o ambiente BIM')
        }

    def Activated(self):
        import FreeCADGui
        import Draft
        doc = FreeCAD.newDocument("Novo_Projeto_Eletrica")
        
        view = FreeCADGui.activeDocument().activeView()
        if view:
            view.viewAxometric()
            
            
        # QtWidgets.QMessageBox.information(None, tr("Eletrica"), tr("Novo projeto iniciado! A tela de desenho está pronta."))
        pass

class ProjectPropertiesDialog(QtWidgets.QDialog):
    """Janela única para todas as propriedades do projeto - Versão Técnica"""
    def __init__(self, meta):
        super().__init__()
        self.meta = meta
        self.setWindowTitle(tr("Configuração da Obra"))
        self.setMinimumWidth(480)
        
        layout = QtWidgets.QFormLayout(self)
        layout.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
        
        # --- SEÇÃO: IDENTIFICAÇÃO DA OBRA ---
        self.edit_name   = QtWidgets.QLineEdit(getattr(self.meta, "ProjectName", ""))
        self.combo_type  = QtWidgets.QComboBox()
        self.combo_type.addItems(["Residencial", "Comercial", "Industrial", "Predial", "Público"])
        self.combo_type.setCurrentText(getattr(self.meta, "ProjectType", "Residencial"))
        self.combo_phase = QtWidgets.QComboBox()
        self.combo_phase.addItems(["Estudo Preliminar", "Projeto Básico", "Projeto Executivo", "As-Built"])
        self.combo_phase.setCurrentText(getattr(self.meta, "Phase", "Projeto Executivo"))
        
        self.edit_address = QtWidgets.QLineEdit()
        self.edit_address.setText(getattr(self.meta, "Address", ""))
        self.edit_address.setPlaceholderText(tr("Rua, Número, Bairro, Cidade - UF"))

        self.edit_utm_e = QtWidgets.QLineEdit()
        self.edit_utm_e.setText(getattr(self.meta, "UTM_E", ""))
        self.edit_utm_e.setPlaceholderText("E (m)")

        self.edit_utm_n = QtWidgets.QLineEdit()
        self.edit_utm_n.setText(getattr(self.meta, "UTM_N", ""))
        self.edit_utm_n.setPlaceholderText("N (m)")

        self.edit_utm_zone = QtWidgets.QLineEdit()
        self.edit_utm_zone.setText(getattr(self.meta, "UTM_Zone", ""))
        self.edit_utm_zone.setPlaceholderText("22S")

        layout.addRow(QtWidgets.QLabel(f"── {tr('Projeto')} ──"))
        layout.addRow(tr("Nome do Projeto:"), self.edit_name)
        layout.addRow(tr("Tipo de Obra:"),    self.combo_type)
        layout.addRow(tr("Fase do Projeto:"), self.combo_phase)

        # --- SEÇÃO: DADOS TÉCNICOS ---
        self.combo_utility = QtWidgets.QComboBox()
        self.combo_utility.addItems(["Enel", "CPFL", "Light", "Neoenergia", "Energisa", "Equatorial", "Cemig", "Copel", "Outra"])
        self.combo_utility.setCurrentText(getattr(self.meta, "Utility", "Enel"))
        self.combo_voltage = QtWidgets.QComboBox()
        self.combo_voltage.addItems(["127/220V", "220/380V", "127V", "127/254V (Rural)", "220V", "380/440V", "380/660V"])
        self.combo_voltage.setCurrentText(getattr(self.meta, "Voltage", "127/220V"))
        
        self.combo_phases = QtWidgets.QComboBox()
        self.combo_phases.addItems(["Monofásico", "Bifásico", "Trifásico"])
        self.combo_phases.setCurrentText(getattr(self.meta, "SystemPhases", "Trifásico"))

        self.combo_primary = QtWidgets.QComboBox()
        self.combo_primary.addItems(["13.8 kV", "25 kV", "34.5 kV", "69 kV", "138 kV"])
        self.combo_primary.setCurrentText(getattr(self.meta, "PrimaryVoltage", "13.8 kV"))

        self.combo_connection = QtWidgets.QComboBox()
        self.combo_connection.addItems(["Triângulo-Estrela (Dyn11)", "Estrela-Estrela (Yy0)", "Estrela-Triângulo (Yd1)", "Triângulo-Triângulo (Dd0)"])
        self.combo_connection.setCurrentText(getattr(self.meta, "TrafoConnection", "Triângulo-Estrela (Dyn11)"))

        self.combo_trafo_power = QtWidgets.QComboBox()
        self.combo_trafo_power.addItems(["30 kVA", "45 kVA", "75 kVA", "112.5 kVA", "150 kVA", "225 kVA", "300 kVA", "500 kVA", "750 kVA", "1000 kVA", "1500 kVA", "2000 kVA", "2500 kVA"])
        self.combo_trafo_power.setCurrentText(getattr(self.meta, "TrafoPower", "112.5 kVA"))

        self.combo_material = QtWidgets.QComboBox()
        self.combo_material.addItems(["Cobre (Cu)", "Alumínio (Al)"])
        self.combo_material.setCurrentText(getattr(self.meta, "ConductorMaterial", "Cobre (Cu)"))

        self.combo_insulation = QtWidgets.QComboBox()
        self.combo_insulation.addItems(["PVC (70°C)", "EPR/XLPE (90°C)"])
        self.combo_insulation.setCurrentText(getattr(self.meta, "InsulationType", "PVC (70°C)"))

        self.combo_cable_type = QtWidgets.QComboBox()
        self.combo_cable_type.addItems(["Unipolar (Single-core)", "Multipolar (Multi-core)"])
        self.combo_cable_type.setCurrentText(getattr(self.meta, "CableType", "Unipolar (Single-core)"))

        self.combo_method = QtWidgets.QComboBox()
        self.combo_method.addItems(["A1 - Condutores em Eletroduto (Parede Térmica)", "B1 - Eletroduto Aparente/Embutido", "C - Cabos Aparentes", "D - Eletroduto Enterrado", "E/F - Leitos e Bandejas", "G - Ao Ar Livre"])
        self.combo_method.setCurrentText(getattr(self.meta, "InstallationMethod", "B1 - Eletroduto Aparente/Embutido"))

        self.spin_ambient_temp = QtWidgets.QSpinBox()
        self.spin_ambient_temp.setRange(10, 80)
        self.spin_ambient_temp.setSuffix(" °C")
        self.spin_ambient_temp.setValue(getattr(self.meta, "AmbientTemperature", 30))

        self.spin_power_factor = QtWidgets.QDoubleSpinBox()
        self.spin_power_factor.setRange(0.1, 1.0)
        self.spin_power_factor.setSingleStep(0.01)
        self.spin_power_factor.setValue(getattr(self.meta, "PowerFactor", 0.92))

        self.combo_vdrop_limit = QtWidgets.QComboBox()
        self.combo_vdrop_limit.addItems(["4%", "5%", "7%"])
        self.combo_vdrop_limit.setCurrentText(getattr(self.meta, "MaxVoltageDrop", "4%"))

        self.spin_z_trafo = QtWidgets.QDoubleSpinBox()
        self.spin_z_trafo.setRange(1.0, 15.0)
        self.spin_z_trafo.setValue(getattr(self.meta, "TransformerImpedance", 5.0))
        self.spin_z_trafo.setSuffix(" %")

        layout.addRow(QtWidgets.QLabel(""))
        layout.addRow(QtWidgets.QLabel(f"── {tr('Demanda')} ──"))
        layout.addRow(tr("Concessionária:"), self.combo_utility)
        layout.addRow(tr("Tensão Primária (MT):"), self.combo_primary)
        layout.addRow(tr("Tensão Secundária (BT):"), self.combo_voltage)
        layout.addRow(tr("Sistema de Fases:"), self.combo_phases)
        layout.addRow(tr("Potência do Trafo:"), self.combo_trafo_power)
        layout.addRow(tr("Material do Condutor:"), self.combo_material)
        layout.addRow(tr("Tipo de Isolação:"), self.combo_insulation)
        layout.addRow(tr("Tipo de Cabo:"), self.combo_cable_type)
        layout.addRow(tr("Método de Instalação:"), self.combo_method)
        layout.addRow(tr("Temperatura Ambiente:"), self.spin_ambient_temp)
        layout.addRow(tr("Fator de Potência (cos φ):"), self.spin_power_factor)
        layout.addRow(tr("Limite Queda de Tensão (V%):"), self.combo_vdrop_limit)
        layout.addRow(tr("Ligação do Trafo:"), self.combo_connection)
        layout.addRow(tr("Impedância Trafo (Z%):"), self.spin_z_trafo)

        # --- SEÇÃO: RESPONSABILIDADE TÉCNICA ---
        self.edit_designer      = QtWidgets.QLineEdit(getattr(self.meta, "DesignerName", ""))
        self.combo_profession   = QtWidgets.QComboBox()
        self.combo_profession.addItems(["Engenheiro Eletricista", "Técnico em Eletrotécnica",
                                        "Engenheiro Civil", "Arquiteto", "Outro"])
        self.combo_profession.setCurrentText(getattr(self.meta, "DesignerProfession", "Engenheiro Eletricista"))
        self.edit_crea          = QtWidgets.QLineEdit(getattr(self.meta, "CREA", ""))
        self.edit_crea.setPlaceholderText("Ex: CREA-SP 123456/D")
        self.edit_art           = QtWidgets.QLineEdit(getattr(self.meta, "ART", ""))
        self.edit_art.setPlaceholderText("Número da ART registrada no CONFEA")

        layout.addRow(QtWidgets.QLabel(""))
        layout.addRow(QtWidgets.QLabel(f"── {tr('Autor')} ──"))
        layout.addRow(tr("Nome do Projetista:"),   self.edit_designer)
        layout.addRow(tr("Profissão:"),            self.combo_profession)
        layout.addRow(tr("CREA / CFEEE nº:"),      self.edit_crea)
        layout.addRow(tr("Fase do Projeto:"), self.combo_phase)

        layout.addRow(QtWidgets.QLabel(""))
        layout.addRow(QtWidgets.QLabel(f"── {tr('Localização')} ──"))
        layout.addRow(tr("Endereço:"), self.edit_address)
        
        utm_layout = QtWidgets.QHBoxLayout()
        utm_layout.addWidget(self.edit_utm_e)
        utm_layout.addWidget(self.edit_utm_n)
        utm_layout.addWidget(self.edit_utm_zone)
        layout.addRow(tr("Coord. UTM:"), utm_layout)

        layout.addRow(QtWidgets.QLabel(""))
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            'name':               self.edit_name.text(),
            'type':               self.combo_type.currentText(),
            'phase':              self.combo_phase.currentText(),
            'address':            self.edit_address.text(),
            'utm_e':              self.edit_utm_e.text(),
            'utm_n':              self.edit_utm_n.text(),
            'utm_zone':           self.edit_utm_zone.text(),
            'utility':            self.combo_utility.currentText(),
            'primary_voltage':    self.combo_primary.currentText(),
            'voltage':            self.combo_voltage.currentText(),
            'system_phases':      self.combo_phases.currentText(),
            'trafo_connection':   self.combo_connection.currentText(),
            'trafo_power':        self.combo_trafo_power.currentText(),
            'material':           self.combo_material.currentText(),
            'insulation':         self.combo_insulation.currentText(),
            'cable_type':         self.combo_cable_type.currentText(),
            'install_method':     self.combo_method.currentText(),
            'ambient_temp':       self.spin_ambient_temp.value(),
            'power_factor':       self.spin_power_factor.value(),
            'vdrop_limit':        self.combo_vdrop_limit.currentText(),
            'z_trafo':            self.spin_z_trafo.value(),
            'designer_name':      self.edit_designer.text(),
            'designer_profession':self.combo_profession.currentText(),
            'crea':               self.edit_crea.text(),
            'art':                self.edit_art.text()
        }

class ProjectProperties:
    """Configura os metadados do projeto elétrico com campos técnicos"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Report.png'),
            'MenuText': tr('Propriedades Técnicas do Projeto'),
            'ToolTip': tr('Define Nome, Autor, Tensão e Concessionária')
        }

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            QtWidgets.QMessageBox.warning(None, tr("Erro"), tr("Abra ou crie um projeto primeiro!"))
            return
            
        meta = doc.getObject("Eletrica_ProjectData")
        
        # --- LÓGICA DE AUTODETECÇÃO IFC ---
        ifc_data = self._detect_ifc_metadata(doc)
        if not meta:
            meta = doc.addObject("App::FeaturePython", "Eletrica_ProjectData")
            meta.addProperty("App::PropertyString", "ProjectName",         "Geral",    "Nome do Projeto").ProjectName = "Novo Projeto"
            meta.addProperty("App::PropertyString", "ProjectType",         "Geral",    "Tipo de Obra").ProjectType = "Residencial"
            meta.addProperty("App::PropertyString", "Phase",               "Geral",    "Fase do Projeto").Phase = "Projeto Executivo"
            meta.addProperty("App::PropertyString", "Address",             "Localização", "Endereço").Address = ""
            meta.addProperty("App::PropertyString", "UTM_E",               "Localização", "UTM Leste (E)").UTM_E = ""
            meta.addProperty("App::PropertyString", "UTM_N",               "Localização", "UTM Norte (N)").UTM_N = ""
            meta.addProperty("App::PropertyString", "UTM_Zone",            "Localização", "Zona UTM").UTM_Zone = ""
            meta.addProperty("App::PropertyString", "Utility",             "Técnico",  "Concessionária").Utility = "Enel"
            meta.addProperty("App::PropertyString", "PrimaryVoltage",      "Técnico",  "Tensão Primária").PrimaryVoltage = "13.8 kV"
            meta.addProperty("App::PropertyString", "Voltage",             "Técnico",  "Tensão Secundária").Voltage = "127/220V"
            meta.addProperty("App::PropertyString", "SystemPhases",        "Técnico",  "Sistema de Fases").SystemPhases = "Trifásico"
            meta.addProperty("App::PropertyString", "TrafoPower",          "Técnico",  "Potência do Trafo").TrafoPower = "112.5 kVA"
            meta.addProperty("App::PropertyString", "ConductorMaterial",   "Técnico",  "Material do Condutor").ConductorMaterial = "Cobre (Cu)"
            meta.addProperty("App::PropertyString", "InsulationType",      "Técnico",  "Tipo de Isolação").InsulationType = "PVC (70°C)"
            meta.addProperty("App::PropertyString", "CableType",           "Técnico",  "Tipo de Cabo").CableType = "Unipolar (Single-core)"
            meta.addProperty("App::PropertyString", "InstallationMethod",  "Técnico",  "Método de Instalação").InstallationMethod = "B1"
            meta.addProperty("App::PropertyInteger", "AmbientTemperature", "Técnico",  "Temperatura Ambiente").AmbientTemperature = 30
            meta.addProperty("App::PropertyFloat",   "PowerFactor",        "Técnico",  "Fator de Potência").PowerFactor = 0.92
            meta.addProperty("App::PropertyString",  "MaxVoltageDrop",     "Técnico",  "Limite Queda V%").MaxVoltageDrop = "4%"
            meta.addProperty("App::PropertyString", "TrafoConnection",     "Técnico",  "Ligação do Trafo").TrafoConnection = "Triângulo-Estrela (Dyn11)"
            meta.addProperty("App::PropertyFloat",  "TransformerImpedance", "Técnico",  "Impedância Trafo (%)").TransformerImpedance = 5.0
            meta.addProperty("App::PropertyString", "DesignerName",        "Projetista", "Nome do Projetista").DesignerName = ""
            meta.addProperty("App::PropertyString", "DesignerProfession",  "Projetista", "Profissão").DesignerProfession = "Engenheiro Eletricista"
            meta.addProperty("App::PropertyString", "CREA",                "Projetista", "CREA / CFEEE").CREA = ""
            meta.addProperty("App::PropertyString", "ART",                 "Projetista", "Número da ART").ART = ""
            meta.Visibility = False
        else:
            # Garante compatibilidade com arquivos antigos (migração automática)
            new_props = [
                ("App::PropertyString", "Address",             "Localização", "Endereço", ""),
                ("App::PropertyString", "UTM_E",               "Localização", "UTM Leste (E)", ""),
                ("App::PropertyString", "UTM_N",               "Localização", "UTM Norte (N)", ""),
                ("App::PropertyString", "UTM_Zone",            "Localização", "Zona UTM", ""),
                ("App::PropertyString", "Utility",             "Técnico",  "Concessionária", "Enel"),
                ("App::PropertyString", "PrimaryVoltage",      "Técnico",  "Tensão Primária", "13.8 kV"),
                ("App::PropertyString", "Voltage",             "Técnico",  "Tensão Secundária", "127/220V"),
                ("App::PropertyString", "SystemPhases",        "Técnico",  "Sistema de Fases", "Trifásico"),
                ("App::PropertyString", "TrafoPower",          "Técnico",  "Potência do Trafo", "112.5 kVA"),
                ("App::PropertyString", "ConductorMaterial",   "Técnico",  "Material do Condutor", "Cobre (Cu)"),
                ("App::PropertyString", "InsulationType",      "Técnico",  "Tipo de Isolação", "PVC (70°C)"),
                ("App::PropertyString", "CableType",           "Técnico",  "Tipo de Cabo", "Unipolar (Single-core)"),
                ("App::PropertyString", "InstallationMethod",  "Técnico",  "Método de Instalação", "B1"),
                ("App::PropertyInteger", "AmbientTemperature", "Técnico",  "Temperatura Ambiente", 30),
                ("App::PropertyFloat",   "PowerFactor",        "Técnico",  "Fator de Potência", 0.92),
                ("App::PropertyString",  "MaxVoltageDrop",     "Técnico",  "Limite Queda V%", "4%"),
                ("App::PropertyString", "TrafoConnection",     "Técnico",  "Ligação do Trafo", "Triângulo-Estrela (Dyn11)"),
                ("App::PropertyFloat",  "TransformerImpedance", "Técnico",  "Impedância Trafo (%)", 5.0),
                ("App::PropertyString", "Phase",               "Geral",    "Fase do Projeto", "Projeto Executivo"),
                ("App::PropertyString", "DesignerName",        "Projetista", "Nome do Projetista", ""),
                ("App::PropertyString", "DesignerProfession",  "Projetista", "Profissão", "Engenheiro Eletricista"),
                ("App::PropertyString", "CREA",                "Projetista", "CREA / CFEEE", ""),
                ("App::PropertyString", "ART",                 "Projetista", "Número da ART", "")
            ]
            for p_type, p_name, p_group, p_desc, p_val in new_props:
                if not hasattr(meta, p_name):
                    prop = meta.addProperty(p_type, p_name, p_group, p_desc)
                    setattr(meta, p_name, p_val)

        # Se campos de localização estão vazios no meta, tenta usar o que detectamos no IFC
        if not meta.Address and ifc_data['address']: meta.Address = ifc_data['address']
        if not meta.UTM_E and ifc_data['utm_e']:     meta.UTM_E = ifc_data['utm_e']
        if not meta.UTM_N and ifc_data['utm_n']:     meta.UTM_N = ifc_data['utm_n']

        diag = ProjectPropertiesDialog(meta)
        if diag.exec_() == QtWidgets.QDialog.Accepted:
            data = diag.get_data()
            meta.ProjectName          = data['name']
            meta.ProjectType          = data['type']
            meta.Phase                = data['phase']
            meta.Address              = data['address']
            meta.UTM_E                = data['utm_e']
            meta.UTM_N                = data['utm_n']
            meta.UTM_Zone             = data['utm_zone']
            meta.Utility              = data['utility']
            meta.PrimaryVoltage       = data['primary_voltage']
            meta.Voltage              = data['voltage']
            meta.SystemPhases         = data['system_phases']
            meta.TrafoPower           = data['trafo_power']
            meta.ConductorMaterial    = data['material']
            meta.InsulationType       = data['insulation']
            meta.CableType            = data['cable_type']
            meta.InstallationMethod   = data['install_method']
            meta.AmbientTemperature   = data['ambient_temp']
            meta.PowerFactor          = data['power_factor']
            meta.MaxVoltageDrop       = data['vdrop_limit']
            meta.TrafoConnection      = data['trafo_connection']
            meta.TransformerImpedance = data['z_trafo']
            meta.DesignerName         = data['designer_name']
            meta.DesignerProfession   = data['designer_profession']
            meta.CREA                 = data['crea']
            meta.ART                  = data['art']
            doc.recompute()
            QtWidgets.QMessageBox.information(None, tr("Sucesso"), tr("Dados técnicos salvos com sucesso!"))

    def _detect_ifc_metadata(self, doc):
        """Busca por metadados geográficos em objetos do tipo Site ou Project do FreeCAD/BIM"""
        data = {'address': '', 'utm_e': '', 'utm_n': '', 'utm_zone': ''}
        
        # Procura por objetos de Site (comum em IFC estrutural/arquitetônico)
        sites = doc.findObjects(Type="App::FeaturePython") # Sites costumam ser FeaturePython com Proxy de Site
        for s in sites:
            # Verifica se tem cara de Site do Arch/BIM
            if hasattr(s, "Address") or hasattr(s, "Street"):
                street = getattr(s, "Street", "")
                city = getattr(s, "City", "")
                country = getattr(s, "Country", "")
                if street:
                    data['address'] = f"{street}, {city} - {country}".strip(", ")
                
                # Coordenadas UTM ou Geográficas
                if hasattr(s, "Latitude") and hasattr(s, "Longitude"):
                    # Aqui poderíamos converter Lat/Long para UTM, mas por enquanto pegamos valores se existirem
                    data['utm_e'] = str(getattr(s, "Easting", ""))
                    data['utm_n'] = str(getattr(s, "Northing", ""))
                    data['utm_zone'] = str(getattr(s, "Zone", ""))
                break
        return data

class ToggleDashboard:
    """Liga/Desliga o painel lateral de métricas"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Dashboard.png'),
            'MenuText': tr('Abrir/Fechar Dashboard'),
            'ToolTip': tr('Alterna a visualização das métricas em tempo real')
        }

    def Activated(self):
        from EletricaPanel import toggle_dashboard
        toggle_dashboard()

# --- 2. GRUPO: MODELAGEM E CRIAÇÃO (BIM) ---

class CreatePanel:
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Panel.png'),
            'MenuText': tr('Criar Painel (QDC / CCM)'),
            'ToolTip': tr('Cria um painel inteligente')
        }
    def Activated(self):
        from EletricaLogic.Panels import PanelManager
        name, ok = QtWidgets.QInputDialog.getText(None, tr("Novo Painel"), tr("Nome do Painel:"))
        if ok and name:
            PanelManager.create_panel(name)

class OptimizePhases:
    """Otimiza a distribuição de cargas entre as fases R, S e T"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Dashboard.png'), # Usaremos o ícone do Dashboard temporariamente
            'MenuText': tr('Otimizar Fases'),
            'ToolTip': tr('Balanceia automaticamente as cargas entre R, S e T')
        }
    def Activated(self):
        from EletricaLogic.Circuits import PhaseOptimizer
        PhaseOptimizer.optimize()

class InsertSocket:
    """Insere tomadas com Assistente NBR 5410"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Socket.png'),
            'MenuText': tr('Inserir Tomada'),
            'ToolTip': tr('Insere uma tomada com sugestão NBR 5410')
        }

    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        import FreeCADGui
        
        power, ok1 = QtWidgets.QInputDialog.getInt(None, tr("NBR 5410"), tr("Potência (VA/W):"), 100, 100, 15000, 100)
        if not ok1: return
        
        suggestion = "TUG (Uso Geral - 10A)"
        if power == 600: suggestion = "TUG (Cozinha - 10A)"
        elif power >= 1200: suggestion = "TUE (Específico - 20A)"
            
        types = ["TUG (Uso Geral - 10A)", "TUG (Cozinha - 10A)", "TUE (Específico - 20A)"]
        sel_type, ok2 = QtWidgets.QInputDialog.getItem(None, "Tipo", "Classificação:", types, types.index(suggestion), False)
        if not ok2: return
        
        heights = {"Baixa (0.30m)": 300, "Média (1.10m)": 1100, "Alta (2.10m)": 2100}
        pos, ok3 = QtWidgets.QInputDialog.getItem(None, "Altura", "Selecione a Altura:", list(heights.keys()), 1, False)
        if not ok3: return
        z_offset = heights[pos]
        
        base_z = 0.0
        active_container = None
        selection = FreeCADGui.Selection.getSelection()
        for s in selection:
            if hasattr(s, "InList") and s.isDerivedFrom("App::Part"): 
                base_z = s.Placement.Base.z
                active_container = s
                break
        
        manager = LibraryManager()
        file_name = "Tomada_TUE.FCStd" if "TUE" in sel_type else "Tomada_TUG.FCStd"
        obj = manager.insert_component(file_name)
        
        if obj:
            obj.Placement.Base = FreeCAD.Vector(0, 0, base_z + z_offset)
            if not hasattr(obj, "Potencia"): obj.addProperty("App::PropertyInteger", "Potencia", "Eletrica")
            obj.Potencia = power
            if not hasattr(obj, "Classificacao"): obj.addProperty("App::PropertyString", "Classificacao", "Eletrica")
            obj.Classificacao = sel_type
            if active_container: active_container.addObject(obj)
            FreeCADGui.runCommand("Draft_Move")

class InsertLight:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Light.png'), 'MenuText': tr('Inserir Iluminação'), 'ToolTip': tr('Ponto de luz')}
    def Activated(self):
        FreeCAD.Console.PrintMessage("Inserindo luz...\n")

class InsertSwitch:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Switch.png'), 'MenuText': tr('Inserir Interruptor'), 'ToolTip': tr('Simples/Paralelo')}
    def Activated(self):
        from EletricaLogic.Lighting import LightingManager
        cmd, ok = QtWidgets.QInputDialog.getText(None, tr("Comando"), tr("Letra (a, b...):"), text="a")
        if ok: LightingManager.insert_switch("Simples", cmd)

class MergeSwitches:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Merge.png'), 'MenuText': tr('Mesclar Placas'), 'ToolTip': tr('2 ou 3 teclas')}
    def Activated(self):
        from EletricaLogic.Lighting import LightingManager
        LightingManager.merge_switches(FreeCADGui.Selection.getSelection())

class InsertSmartDevice:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SmartHome.png'), 'MenuText': tr('Inserir Smart/IoT'), 'ToolTip': tr('Automação') }
    def Activated(self):
        SmartHomeManager.insert_smart_device("Hub Zigbee")

class InsertSpecialSocket:
    """Insere Tomadas de Uso Específico (TUE) com catálogo de potências"""
    EQUIPMENT_DATABASE = {
        "Chuveiro Elétrico":   {"power": 5500, "voltage": "220V"},
        "Chuveiro Turbo":      {"power": 7500, "voltage": "220V"},
        "Micro-ondas":         {"power": 1200, "voltage": "127V"},
        "Geladeira / Freezer": {"power": 500,  "voltage": "127V"},
        "Máquina de Lavar":    {"power": 1000, "voltage": "127V"},
        "Forno Elétrico":      {"power": 2500, "voltage": "220V"},
        "Torneira Elétrica":   {"power": 4500, "voltage": "220V"},
        "Secadora de Roupas":  {"power": 2500, "voltage": "220V"},
        "Máquina de Lavar Louça": {"power": 1500, "voltage": "127V"},
        "Fogão por Indução":   {"power": 7000, "voltage": "220V"},
        "Outro (Manual)":      {"power": 100,  "voltage": "127V"}
    }

    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'SpecialSocket.png'),
            'MenuText': tr('Inserir TUE (Especial)'),
            'ToolTip': tr('Tomadas com potência definida por equipamento')
        }

    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Inserir TUE (Especial)"))
        layout = QtWidgets.QFormLayout(dlg)
        
        combo_eq = QtWidgets.QComboBox()
        combo_eq.addItems(list(self.EQUIPMENT_DATABASE.keys()))
        
        spin_p = QtWidgets.QDoubleSpinBox(); spin_p.setRange(0, 50000); spin_p.setSuffix(" W")
        combo_v = QtWidgets.QComboBox();     combo_v.addItems(["127V", "220V", "380V", "440V"])
        edit_label = QtWidgets.QLineEdit()

        def update_fields():
            data = self.EQUIPMENT_DATABASE.get(combo_eq.currentText())
            spin_p.setValue(data["power"])
            index = combo_v.findText(data["voltage"])
            if index >= 0: combo_v.setCurrentIndex(index)
            edit_label.setText(combo_eq.currentText())

        combo_eq.currentIndexChanged.connect(update_fields)
        update_fields() # Initial trigger

        layout.addRow(tr("Equipamento:"), combo_eq)
        layout.addRow(tr("Potência:"),    spin_p)
        layout.addRow(tr("Tensão:"),      combo_v)
        layout.addRow(tr("Etiqueta:"),    edit_label)
        
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)
        
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            manager = LibraryManager()
            obj = manager.insert_component("Tomada_Especial.FCStd")
            if obj:
                obj.Label = edit_label.text()
                obj.addProperty("App::PropertyFloat",  "Potencia",  "Eletrica", "Potência (W)").Potencia = spin_p.value()
                obj.addProperty("App::PropertyString", "Tensao",    "Eletrica", "Tensão").Tensao = combo_v.currentText()
                obj.addProperty("App::PropertyString", "TipoBIM",   "Eletrica", "Tipo").TipoBIM = "TUE"
                obj.addProperty("App::PropertyString", "Descricao", "Eletrica", "Descrição").Descricao = combo_eq.currentText()
                # BIM 6D - Gestão de Ativos
                obj.addProperty("App::PropertyString", "NumeroSerie",    "Manutencao", "Nº de Série")
                obj.addProperty("App::PropertyString", "DataInstalacao", "Manutencao", "Data Instalação")
                obj.addProperty("App::PropertyString", "DataManutencao", "Manutencao", "Próxima Manutenção")
                FreeCADGui.runCommand("Draft_Move")

class InsertAirConditioner:
    """Assistente para inserção de Ar Condicionado com conversão BTU -> Watts"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'AirConditioning.png'),
            'MenuText': tr('Inserir Ar Condicionado'),
            'ToolTip': tr('Dimensiona e insere ar condicionado (Split/Janela)')
        }

    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Assistente de Ar Condicionado"))
        dlg.setMinimumWidth(380)
        layout = QtWidgets.QFormLayout(dlg)

        # --- CALCULADORA DE CARGA TÉRMICA ---
        group_calc = QtWidgets.QGroupBox(tr("Cálculo de Carga Térmica"))
        form_calc = QtWidgets.QFormLayout(group_calc)
        
        spin_area   = QtWidgets.QDoubleSpinBox(); spin_area.setRange(1, 500); spin_area.setValue(20); spin_area.setSuffix(" m²")
        spin_people = QtWidgets.QSpinBox(); spin_people.setRange(1, 50); spin_people.setValue(2)
        spin_eletr  = QtWidgets.QSpinBox(); spin_eletr.setRange(0, 50); spin_eletr.setValue(1)
        
        btn_suggest = QtWidgets.QPushButton(tr("Sugerir BTUs"))
        form_calc.addRow(tr("Área do Ambiente:"), spin_area)
        form_calc.addRow(tr("Nº de Pessoas:"),     spin_people)
        form_calc.addRow(tr("Equipamentos/TV:"),  spin_eletr)
        form_calc.addRow(btn_suggest)
        layout.addWidget(group_calc)

        # --- ESPECIFICAÇÃO TÉCNICA ---
        group_spec = QtWidgets.QGroupBox(tr("Especificação do Equipamento"))
        form_spec = QtWidgets.QFormLayout(group_spec)

        btus_data = {
            "9.000 BTU/h (~800W)": 800,
            "12.000 BTU/h (~1100W)": 1100,
            "18.000 BTU/h (~1600W)": 1600,
            "24.000 BTU/h (~2200W)": 2200,
            "30.000 BTU/h (~2800W)": 2800,
            "36.000 BTU/h (~3300W)": 3300,
            "48.000 BTU/h (~4500W)": 4500,
            "60.000 BTU/h (~5500W)": 5500
        }

        combo_btu    = QtWidgets.QComboBox(); combo_btu.addItems(list(btus_data.keys()))
        spin_watts   = QtWidgets.QDoubleSpinBox(); spin_watts.setRange(100, 50000); spin_watts.setValue(800); spin_watts.setSuffix(" W")
        combo_v      = QtWidgets.QComboBox(); combo_v.addItems(["220V", "127V", "380V", "440V"])
        combo_phases = QtWidgets.QComboBox(); combo_phases.addItems(["Monofásico", "Bifásico", "Trifásico"])
        edit_label   = QtWidgets.QLineEdit("Ar_Cond_1")

        def calcular_carga():
            # Regra: 600 BTU/m² + 600 por pessoa extra + 600 por equipamento
            total_btu = (spin_area.value() * 600) + ((spin_people.value()-1) * 600) + (spin_eletr.value() * 600)
            
            # Encontrar a melhor opção fabricada (arredondando para cima)
            sorted_options = [9000, 12000, 18000, 24000, 30000, 36000, 48000, 60000]
            suggested = 9000
            for opt in sorted_options:
                if total_btu <= opt:
                    suggested = opt
                    break
            if total_btu > 60000: suggested = 60000

            # Atualizar UI
            for key in btus_data.keys():
                if str(suggested) in key:
                    combo_btu.setCurrentText(key)
                    break
            
            QtWidgets.QMessageBox.information(dlg, tr("Cálculo Térmico"), 
                f"Carga Térmica Estimada: {total_btu:.0f} BTU/h\nSugerido: {suggested} BTU/h")

        btn_suggest.clicked.connect(calcular_carga)

        def update_watts(text):
            spin_watts.setValue(btus_data[text])
            if "36.000" in text or "48.000" in text or "60.000" in text:
                combo_phases.setCurrentText("Trifásico")
            else:
                combo_phases.setCurrentText("Bifásico")

        combo_btu.currentTextChanged.connect(update_watts)

        form_spec.addRow(tr("Capacidade Sugerida:"), combo_btu)
        form_spec.addRow(tr("Potência Real (W):"),   spin_watts)
        form_spec.addRow(tr("Tensão:"),              combo_v)
        form_spec.addRow(tr("Sistema de Fases:"),    combo_phases)
        form_spec.addRow(tr("Nome/Etiqueta:"),       edit_label)
        layout.addWidget(group_spec)

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # Sincronizar com dados do projeto
            from EletricaLogic.Starters import StarterManager
            proj = StarterManager.get_project_settings()
            from EletricaLogic.Calculator import ElectricalCalculator
            
            # Recalcular potência baseada em BTUs
            watts = spin_watts.value()
            v_val = int(combo_v.currentText().replace("V", ""))
            
            manager = LibraryManager()
            obj = manager.insert_component("ArCondicionado_Split.FCStd")
            if obj:
                obj.Label = edit_label.text()
                obj.addProperty("App::PropertyFloat",   "Potencia", "Eletrica", "Potência (W)").Potencia = watts
                obj.addProperty("App::PropertyString",  "Tensao",   "Eletrica", "Tensão").Tensao = combo_v.currentText()
                obj.addProperty("App::PropertyInteger", "Fases",    "Eletrica", "Fases").Fases = 3 if "Trifásico" in combo_phases.currentText() else (2 if "Bifásico" in combo_phases.currentText() else 1)
                obj.addProperty("App::PropertyString",  "TipoBIM",  "Eletrica", "Tipo").TipoBIM = "ArCondicionado"
                obj.addProperty("App::PropertyString",  "BTU",      "HVAC",     "Capacidade").BTU = combo_btu.currentText()
                # BIM 6D - Gestão de Ativos
                obj.addProperty("App::PropertyString", "NumeroSerie",    "Manutencao", "Nº de Série")
                obj.addProperty("App::PropertyString", "DataInstalacao", "Manutencao", "Data Instalação")
                obj.addProperty("App::PropertyString", "DataManutencao", "Manutencao", "Próxima Manutenção")
                
                # Dimensionar cabo e proteção usando dados do projeto
                cur = ElectricalCalculator.calculate_current(watts, v_val, obj.Fases)
                wire = ElectricalCalculator.get_standard_wire_gauge(cur * 1.25, 
                    method=proj.get('method', 'B1'), 
                    insulation=proj.get('insulation', 'PVC'),
                    material=proj.get('material', 'Cu'))
                obj.addProperty("App::PropertyFloat", "SecaoCabo", "Engenharia", "Cabo Calculado (mm²)").SecaoCabo = wire
                
                FreeCADGui.runCommand("Draft_Move")
                FreeCAD.ActiveDocument.recompute()

class InsertPumpSet:
    """Assistente de Conjunto Motobomba (Hidráulica + Elétrica)"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'PumpSet.png'),
            'MenuText': tr('Inserir Conjunto Motobomba'),
            'ToolTip': tr('Dimensiona bomba pela vazão/altura e define motor')
        }

    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        from EletricaLogic.Starters import StarterManager
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Assistente de Motobomba Industrial"))
        dlg.setMinimumWidth(420)
        layout = QtWidgets.QVBoxLayout(dlg)

        # --- HIDRÁULICA ---
        group_hyd = QtWidgets.QGroupBox(tr("Dados Hidráulicos"))
        form_hyd = QtWidgets.QFormLayout(group_hyd)
        spin_flow = QtWidgets.QDoubleSpinBox(); spin_flow.setRange(0.1, 5000); spin_flow.setValue(10); spin_flow.setSuffix(" m³/h")
        spin_head = QtWidgets.QDoubleSpinBox(); spin_head.setRange(1, 1000);   spin_head.setValue(30); spin_head.setSuffix(" mca")
        spin_h_eff = QtWidgets.QDoubleSpinBox(); spin_h_eff.setRange(10, 95);  spin_h_eff.setValue(70); spin_h_eff.setSuffix(" %")
        form_hyd.addRow(tr("Vazão (Q):"), spin_flow)
        form_hyd.addRow(tr("Altura Manométrica (H):"), spin_head)
        form_hyd.addRow(tr("Rendimento Hidráulico:"), spin_h_eff)
        layout.addWidget(group_hyd)

        # --- ELÉTRICA ---
        group_ele = QtWidgets.QGroupBox(tr("Dados do Motor"))
        form_ele = QtWidgets.QFormLayout(group_ele)
        spin_cv    = QtWidgets.QDoubleSpinBox(); spin_cv.setRange(0.1, 1000); spin_cv.setValue(2); spin_cv.setSuffix(" CV")
        combo_v    = QtWidgets.QComboBox();      combo_v.addItems(["220V", "380V", "440V", "660V"])
        combo_met  = QtWidgets.QComboBox();      combo_met.addItems(["Direta", "Estrela-Triângulo", "Soft-Starter", "Inversor"])
        edit_label = QtWidgets.QLineEdit("Motobomba_1")
        form_ele.addRow(tr("Potência do Motor:"), spin_cv)
        form_ele.addRow(tr("Tensão:"),           combo_v)
        form_ele.addRow(tr("Método de Partida:"), combo_met)
        form_ele.addRow(tr("Nome/Etiqueta:"),     edit_label)
        layout.addWidget(group_ele)

        def sugerir_motor():
            # Fórmula: P(cv) = (Q * H) / (75 * rend_h * 3.6) - simplificada
            # Q em m3/h -> / 3.6 = m3/s * 1000 = L/s
            q_ls = (spin_flow.value() * 1000) / 3600
            h = spin_head.value()
            eff = spin_h_eff.value() / 100.0
            cv_req = (q_ls * h) / (75 * eff)
            
            # Sugere valor comercial acima
            cv_standards = [0.16, 0.25, 0.33, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 6, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 75, 100]
            suggested = 2
            for s in cv_standards:
                if cv_req <= s:
                    suggested = s
                    break
            spin_cv.setValue(suggested)
            QtWidgets.QMessageBox.information(dlg, tr("Cálculo Hidráulico"), 
                f"Potência Hidráulica Requerida: {cv_req:.2f} CV\nMotor Sugerido: {suggested} CV")

        btn_calc_hyd = QtWidgets.QPushButton(tr("Calcular Potência pela Hidráulica"))
        btn_calc_hyd.clicked.connect(sugerir_motor)
        layout.insertWidget(2, btn_calc_hyd)

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addWidget(btn_box)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            cv = spin_cv.value()
            voltage = int(combo_v.currentText().replace("V", ""))
            method = combo_met.currentText()
            res = StarterManager.dimension_motor(cv, voltage, method)
            
            # Sincronizar com dados do projeto
            proj = StarterManager.get_project_settings()
            from EletricaLogic.Calculator import ElectricalCalculator
            
            manager = LibraryManager()
            obj = manager.insert_component("Motobomba_Industrial.FCStd")
            if obj:
                obj.Label = edit_label.text()
                obj.addProperty("App::PropertyFloat",   "Potencia_CV", "Eletrica", "Potência (CV)").Potencia_CV = cv
                obj.addProperty("App::PropertyFloat",   "Vazao",      "Hidraulica", "Vazão (m³/h)").Vazao = spin_flow.value()
                obj.addProperty("App::PropertyFloat",   "MCA",        "Hidraulica", "Pressão (mca)").MCA = spin_head.value()
                obj.addProperty("App::PropertyString",  "Tensao",     "Eletrica", "Tensão").Tensao = combo_v.currentText()
                obj.addProperty("App::PropertyString",  "KitWEG",     "Motor",    "Componentes WEG").KitWEG = f"{res['protection']} + {res['contactor']}"
                obj.addProperty("App::PropertyString",  "TipoBIM",    "Eletrica", "Tipo").TipoBIM = "Motobomba"
                # BIM 6D - Gestão de Ativos
                obj.addProperty("App::PropertyString", "NumeroSerie",    "Manutencao", "Nº de Série")
                obj.addProperty("App::PropertyString", "DataInstalacao", "Manutencao", "Data Instalação")
                obj.addProperty("App::PropertyString", "DataManutencao", "Manutencao", "Próxima Manutenção")
                
                # Dimensionar cabo usando dados do projeto
                cur = res['in_nom_a']
                wire = ElectricalCalculator.get_standard_wire_gauge(cur * 1.25, 
                    method=proj.get('method', 'B1'), 
                    insulation=proj.get('insulation', 'PVC'),
                    material=proj.get('material', 'Cu'))
                obj.addProperty("App::PropertyFloat", "SecaoCabo", "Engenharia", "Cabo Calculado (mm²)").SecaoCabo = wire

                FreeCADGui.runCommand("Draft_Move")
                FreeCAD.ActiveDocument.recompute()

class LinkPumpSet:
    """Aplica propriedades de Motobomba a um objeto 3D já existente (importado)"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'BIMify.png'),
            'MenuText': tr('Vincular Dados de Motobomba'),
            'ToolTip': tr('Transforma objeto selecionado em uma Motobomba inteligente')
        }

    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            QtWidgets.QMessageBox.warning(None, tr("Erro"), tr("Selecione um objeto 3D primeiro!"))
            return
        
        target_obj = selection[0]
        from EletricaLogic.Starters import StarterManager
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Vincular Dados Técnicos - Motobomba"))
        dlg.setMinimumWidth(420)
        layout = QtWidgets.QVBoxLayout(dlg)

        # --- HIDRÁULICA ---
        group_hyd = QtWidgets.QGroupBox(tr("Dados Hidráulicos"))
        form_hyd = QtWidgets.QFormLayout(group_hyd)
        spin_flow = QtWidgets.QDoubleSpinBox(); spin_flow.setRange(0.1, 5000); spin_flow.setValue(10); spin_flow.setSuffix(" m³/h")
        spin_head = QtWidgets.QDoubleSpinBox(); spin_head.setRange(1, 1000);   spin_head.setValue(30); spin_head.setSuffix(" mca")
        spin_h_eff = QtWidgets.QDoubleSpinBox(); spin_h_eff.setRange(10, 95);  spin_h_eff.setValue(70); spin_h_eff.setSuffix(" %")
        form_hyd.addRow(tr("Vazão (Q):"), spin_flow)
        form_hyd.addRow(tr("Altura Manométrica (H):"), spin_head)
        form_hyd.addRow(tr("Rendimento Hidráulico:"), spin_h_eff)
        layout.addWidget(group_hyd)

        group_ele = QtWidgets.QGroupBox(tr("Dados do Motor"))
        form_ele = QtWidgets.QFormLayout(group_ele)
        spin_cv    = QtWidgets.QDoubleSpinBox(); spin_cv.setRange(0.1, 1000); spin_cv.setValue(2); spin_cv.setSuffix(" CV")
        combo_v    = QtWidgets.QComboBox();      combo_v.addItems(["220V", "380V", "440V", "660V"])
        combo_met  = QtWidgets.QComboBox();      combo_met.addItems(["Direta", "Estrela-Triângulo", "Soft-Starter", "Inversor"])
        form_ele.addRow(tr("Potência do Motor:"), spin_cv)
        form_ele.addRow(tr("Tensão:"),           combo_v)
        form_ele.addRow(tr("Método de Partida:"), combo_met)
        layout.addWidget(group_ele)

        def sugerir_motor():
            q_ls = (spin_flow.value() * 1000) / 3600
            h = spin_head.value()
            eff = spin_h_eff.value() / 100.0
            cv_req = (q_ls * h) / (75 * eff)
            cv_standards = [0.16, 0.25, 0.33, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 6, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 75, 100]
            suggested = 2
            for s in cv_standards:
                if cv_req <= s:
                    suggested = s
                    break
            spin_cv.setValue(suggested)

        btn_calc_hyd = QtWidgets.QPushButton(tr("Calcular Potência pela Hidráulica"))
        btn_calc_hyd.clicked.connect(sugerir_motor)
        layout.insertWidget(2, btn_calc_hyd)

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addWidget(btn_box)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            cv = spin_cv.value()
            voltage = int(combo_v.currentText().replace("V", ""))
            method = combo_met.currentText()
            res = StarterManager.dimension_motor(cv, voltage, method)
            
            # Sincronizar com dados do projeto
            proj = StarterManager.get_project_settings()
            from EletricaLogic.Calculator import ElectricalCalculator

            # Aplica propriedades ao objeto existente
            if not hasattr(target_obj, "Potencia_CV"): target_obj.addProperty("App::PropertyFloat", "Potencia_CV", "Eletrica", "Potência (CV)")
            target_obj.Potencia_CV = cv
            if not hasattr(target_obj, "Vazao"): target_obj.addProperty("App::PropertyFloat", "Vazao", "Hidraulica", "Vazão (m³/h)")
            target_obj.Vazao = spin_flow.value()
            if not hasattr(target_obj, "MCA"): target_obj.addProperty("App::PropertyFloat", "MCA", "Hidraulica", "Pressão (mca)")
            target_obj.MCA = spin_head.value()
            if not hasattr(target_obj, "Tensao"): target_obj.addProperty("App::PropertyString", "Tensao", "Eletrica", "Tensão")
            target_obj.Tensao = combo_v.currentText()
            if not hasattr(target_obj, "KitWEG"): target_obj.addProperty("App::PropertyString", "KitWEG", "Motor", "Componentes WEG")
            target_obj.KitWEG = f"{res['protection']} + {res['contactor']}"
            if not hasattr(target_obj, "TipoBIM"): target_obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo")
            target_obj.TipoBIM = "Motobomba"
            # BIM 6D - Gestão de Ativos
            if not hasattr(target_obj, "NumeroSerie"):    target_obj.addProperty("App::PropertyString", "NumeroSerie",    "Manutencao", "Nº de Série")
            if not hasattr(target_obj, "DataInstalacao"): target_obj.addProperty("App::PropertyString", "DataInstalacao", "Manutencao", "Data Instalação")
            if not hasattr(target_obj, "DataManutencao"): target_obj.addProperty("App::PropertyString", "DataManutencao", "Manutencao", "Próxima Manutenção")
            
            # Dimensionar cabo usando dados do projeto
            cur = res['in_nom_a']
            wire = ElectricalCalculator.get_standard_wire_gauge(cur * 1.25, 
                method=proj.get('method', 'B1'), 
                insulation=proj.get('insulation', 'PVC'),
                material=proj.get('material', 'Cu'))
            if not hasattr(target_obj, "SecaoCabo"): target_obj.addProperty("App::PropertyFloat", "SecaoCabo", "Engenharia", "Cabo Calculado (mm²)")
            target_obj.SecaoCabo = wire

            FreeCAD.ActiveDocument.recompute()
            QtWidgets.QMessageBox.information(None, tr("Sucesso"), tr("Objeto transformado em Motobomba BIM com sucesso!"))


# --- 3. GRUPO: INFRAESTRUTURA ---

class InsertTelecomPoint:
    """Insere pontos de cabeamento estruturado (Rede, TV, Tel)"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Telecom.png'),
            'MenuText': tr('Inserir Ponto de Telecom'),
            'ToolTip': tr('Rede / TV / Telefone / CFTV')
        }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Inserir Ponto de Telecom"))
        layout = QtWidgets.QFormLayout(dlg)
        
        combo_type = QtWidgets.QComboBox()
        combo_type.addItems([tr("Rede (RJ45)"), tr("TV a Cabo (Coaxial)"), tr("Telefone (RJ11)"), tr("CFTV / Câmera")])
        edit_label = QtWidgets.QLineEdit("Ponto_Rede_1")
        
        layout.addRow(tr("Tipo de Ponto:"), combo_type)
        layout.addRow(tr("Etiqueta:"),      edit_label)
        
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)
        
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            sel_type = combo_type.currentText()
            manager = LibraryManager()
            obj = manager.insert_component("Ponto_Telecom.FCStd")
            if obj:
                obj.Label = edit_label.text()
                obj.addProperty("App::PropertyString", "TipoTelecom", "Dados", "Tipo").TipoTelecom = sel_type
                obj.addProperty("App::PropertyString", "TipoBIM",     "Eletrica", "Tipo").TipoBIM = "Telecom"
                FreeCADGui.runCommand("Draft_Move")

class InsertVDIRack:
    """Insere Racks de Telecomunicações (VDI)"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Rack.png'),
            'MenuText': tr('Inserir Rack VDI'),
            'ToolTip': tr('VDI (Voz, Dados, Imagem)')
        }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Inserir Rack VDI"))
        layout = QtWidgets.QFormLayout(dlg)
        
        combo_size = QtWidgets.QComboBox()
        combo_size.addItems(["6U", "9U", "12U", "16U", "24U", "44U"])
        edit_label = QtWidgets.QLineEdit("Rack_Central")
        
        layout.addRow(tr("Tamanho do Rack (U):"), combo_size)
        layout.addRow(tr("Nome:"),                edit_label)
        
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)
        
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            manager = LibraryManager()
            obj = manager.insert_component("Rack_Telecom.FCStd")
            if obj:
                obj.Label = edit_label.text()
                obj.addProperty("App::PropertyString", "TamanhoU", "Dados", "Capacidade").TamanhoU = combo_size.currentText()
                obj.addProperty("App::PropertyString", "TipoBIM",  "Eletrica", "Tipo").TipoBIM = "Rack"
                FreeCADGui.runCommand("Draft_Move")

class ToggleVoltageDropHeatmap:
    """Ativa/Desativa visualização de Queda de Tensão no 3D"""
    def __init__(self):
        self.active = False
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'Heatmap.svg'),
            'MenuText': tr('Mapa de Queda de Tensão'),
            'ToolTip': tr('Colore o projeto conforme a perda de energia')
        }
    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        from EletricaLogic.Visuals import HeatmapManager
        self.active = not self.active
        # Atualizar cálculos antes de pintar
        if self.active:
            CircuitManager.generate_load_schedule()
        HeatmapManager.toggle_voltage_drop_heatmap(self.active)

class CreateConduit:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Conduit.png'), 'MenuText': tr('Criar Eletroduto'), 'ToolTip': tr('Tubo 3D')}
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        for obj in FreeCADGui.Selection.getSelection():
            if hasattr(obj, "Points"): ConduitManager.create_conduit(obj.Points)

class CreateCableTray:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Tray.png'), 'MenuText': 'Lançar Eletrocalha', 'ToolTip': 'Infra industrial'}
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        FreeCADGui.runCommand("Draft_Wire")
        wire = FreeCAD.ActiveDocument.Objects[-1]
        if hasattr(wire, "Points"): ConduitManager.create_cable_tray(wire.Points, 200, 100)

class CreateIndustrialConnection:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Industrial.png'), 'MenuText': tr('Infra Industrial'), 'ToolTip': tr('Conexões Pesadas') }
    def Activated(self):
        from EletricaLogic.Fittings import FittingManager
        for obj in FreeCADGui.Selection.getSelection():
            FittingManager.add_industrial_termination(obj, "M20")

class Generate3DWiring:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Wiring3D.png'), 'MenuText': tr('Fiação 3D'), 'ToolTip': tr('Gera condutores nos eletrodutos') }
    def Activated(self):
        from EletricaLogic.Wiring import WiringManager
        for obj in FreeCADGui.Selection.getSelection():
            WiringManager.generate_3d_cables(obj)

# --- 4. GRUPO: ENGENHARIA E CÁLCULOS ---

class ServiceEntranceWizard:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ServiceEntrance.png'), 'MenuText': tr('Assistente de Entrada'), 'ToolTip': tr('Cálculo de Demanda e Padrão') }
    def Activated(self):
        QtWidgets.QMessageBox.information(None, tr("Padrão"), tr("Assistente de Padrão de Entrada iniciado."))

class InsertSubstation:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Substation.svg'), 'MenuText': tr('Inserir Subestação BIM'), 'ToolTip': tr('MT/AT') }
    def Activated(self):
        QtWidgets.QMessageBox.information(None, tr("MT"), tr("Cálculo de Subestação iniciado."))

class InsertBoreholePump:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Pump.svg'), 'MenuText': tr('Bomba de Poço'), 'ToolTip': tr('Ebara/Submersa')}
    def Activated(self):
        QtWidgets.QMessageBox.information(None, tr("Poço"), tr("Cálculo de Bomba Submersa."))

class SetupEmergencyPower:
    """Assistente de Dimensionamento de Grupo Motor Gerador (GMG)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Generator.png'), 'MenuText': tr('Dimensionar Gerador'), 'ToolTip': tr('Dimensiona GMG baseado em cargas essenciais') }

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        essentials = []
        p_total_ess = 0.0
        max_start_p = 0.0
        
        for obj in doc.Objects:
            if hasattr(obj, "Potencia") and getattr(obj, "Emergencia", False):
                p = getattr(obj, "Potencia", 0.0)
                essentials.append(obj)
                p_total_ess += p
                
                # Identificar maior pico de partida (se for motor)
                if "Motor" in getattr(obj, "TipoBIM", ""):
                    start_p = p * 6.0 # Assumindo partida direta
                    if start_p > max_start_p: max_start_p = start_p
        
        if not essentials:
            QtWidgets.QMessageBox.warning(None, "Gerador", "Nenhuma carga foi marcada como 'Emergência'. Marque os equipamentos essenciais primeiro.")
            return
            
        # Cálculo de Sizing
        # 1. Carga em regime (S = P / 0.8)
        s_steady = (p_total_ess / 1000.0) / 0.8
        # 2. Partida do maior motor (S = (P_total - P_max) + P_start) / 0.8
        s_min = max(s_steady, (max_start_p / 1000.0) / 1.5) 
        
        # Sugestão Comercial
        gmg_sizes = [15, 25, 40, 55, 80, 115, 150, 180, 250, 350, 500, 750, 1000]
        suggested = gmg_sizes[0]
        for s in gmg_sizes:
            if s >= s_min:
                suggested = s
                break
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Dimensionamento de Grupo Gerador")
        layout = QtWidgets.QVBoxLayout(dlg)
        
        info = (
            f"<b>RELATÓRIO DE EMERGÊNCIA</b><br><br>"
            f"Cargas Essenciais: {len(essentials)}<br>"
            f"Potência Total Essencial: {p_total_ess/1000.0:.2f} kW<br>"
            f"Pico de Partida Estimado: {max_start_p/1000.0:.2f} kW<br><br>"
            f"Potência Mínima Sugerida: <b>{s_min:.2f} kVA</b><br>"
            f"GMG Comercial Recomendado: <b style='color:green'>{suggested} kVA</b>"
        )
        
        lbl = QtWidgets.QLabel(info)
        layout.addWidget(lbl)
        
        def inserir_gmg():
            from EletricaLogic.Library import LibraryManager
            manager = LibraryManager()
            obj = manager.insert_component("Gerador_Carenado.FCStd")
            if obj:
                obj.Label = f"Gerador_{suggested}kVA"
                if not hasattr(obj, "Potencia"): obj.addProperty("App::PropertyFloat", "Potencia", "Eletrica", "Potência (kVA)")
                obj.Potencia = suggested
                if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo")
                obj.TipoBIM = "Gerador"
            dlg.accept()

        btn_ins = QtWidgets.QPushButton("Inserir Gerador no 3D")
        btn_ins.clicked.connect(inserir_gmg)
        layout.addWidget(btn_ins)
        
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)
        
        dlg.exec_()

class GenerateLoadSchedule:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'LoadSchedule.svg'), 'MenuText': tr('Quadro de Cargas'), 'ToolTip': tr('Tabela de Circuitos') }
    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule()

class GenerateCableSchedule:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'CableSchedule.svg'), 'MenuText': tr('Lista de Cabos'), 'ToolTip': tr('De/Para') }
    def Activated(self):
        from EletricaLogic.CableSchedule import CableScheduleManager
        CableScheduleManager.export_to_spreadsheet()

class GenerateBudget:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BudgetPro.png'), 'MenuText': tr('Gerar Orçamento (BOM)'), 'ToolTip': tr('Custos') }
    def Activated(self):
        from EletricaLogic.Budget import BudgetManager
        BudgetManager.generate_budget_report({})

class GenerateUnifilar:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'UnifilarPro.png'), 'MenuText': tr('Diagrama Unifilar'), 'ToolTip': tr('Esquema') }
    def Activated(self):
        from EletricaLogic.Diagrams import UnifilarGenerator
        UnifilarGenerator.create_graphic_diagram(None)

class SyncTitleBlock:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'TitleBlock.png'), 'MenuText': tr('Sincronizar Selo'), 'ToolTip': tr('TechDraw') }
    def Activated(self):
        from EletricaLogic.Diagrams import UnifilarGenerator
        UnifilarGenerator.sync_title_block(None)

class RunProjectAudit:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Audit.png'), 'MenuText': tr('Auditoria Geral'), 'ToolTip': tr('Erros') }
    def Activated(self):
        from EletricaLogic.Auditor import ProjectAuditor
        ProjectAuditor.run_full_audit()

# =============================================================================
# FASE 2: ELÉTRICA INDUSTRIAL
# =============================================================================

class DimensionMotorStarter:
    """Assistente completo de dimensionamento de partida de motor trifásico"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'MotorStarter.svg'), 'MenuText': 'Partida de Motor (WEG)', 'ToolTip': 'Dimensiona disjuntor, contatora e cabo' }

    def Activated(self):
        from EletricaLogic.Starters import StarterManager

        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Assistente de Motor Industrial"))
        dlg.setMinimumWidth(460)
        layout = QtWidgets.QFormLayout(dlg)

        spin_cv    = QtWidgets.QDoubleSpinBox(); spin_cv.setRange(0.1, 500); spin_cv.setValue(5); spin_cv.setSuffix(" CV")
        combo_v    = QtWidgets.QComboBox(); combo_v.addItems(["380V", "220V", "440V", "660V"])
        combo_met  = QtWidgets.QComboBox(); combo_met.addItems(["Direta", "Estrela-Triângulo", "Soft-Starter", "Inversor de Frequência"])
        
        # --- NOVOS CAMPOS DE PLACA ---
        spin_fs    = QtWidgets.QDoubleSpinBox(); spin_fs.setRange(1.0, 2.0); spin_fs.setValue(1.15); spin_fs.setSingleStep(0.05)
        spin_rpm   = QtWidgets.QSpinBox(); spin_rpm.setRange(600, 3600); spin_rpm.setValue(1750); spin_rpm.setSuffix(" RPM")
        spin_polos = QtWidgets.QSpinBox(); spin_polos.setRange(2, 12); spin_polos.setValue(4); spin_polos.setSingleStep(2)
        combo_fec  = QtWidgets.QComboBox(); combo_fec.addItems(["3 Pontas (Direta)", "6 Pontas (Y-Δ)", "12 Pontas", "Série/Paralelo"])
        spin_eff   = QtWidgets.QDoubleSpinBox(); spin_eff.setRange(50, 99); spin_eff.setValue(92); spin_eff.setSuffix(" %")
        spin_cos   = QtWidgets.QDoubleSpinBox(); spin_cos.setRange(0.1, 1.0); spin_cos.setValue(0.85); spin_cos.setSingleStep(0.01)

        edit_label = QtWidgets.QLineEdit("Motor_1")

        layout.addRow("Potência do Motor:",   spin_cv)
        layout.addRow("Tensão de Alimentação:", combo_v)
        layout.addRow("Método de Partida:",   combo_met)
        layout.addRow("Fator de Serviço (FS):", spin_fs)
        layout.addRow("Rotação (RPM):",       spin_rpm)
        layout.addRow("Número de Polos:",     spin_polos)
        layout.addRow("Tipo de Fechamento:",  combo_fec)
        layout.addRow("Rendimento (η):",      spin_eff)
        layout.addRow("Fator de Potência:",    spin_cos)
        layout.addRow("Nome do Motor:",       edit_label)

        result_box = QtWidgets.QTextEdit()
        result_box.setReadOnly(True)
        result_box.setMinimumHeight(200)
        result_box.setPlaceholderText("Clique em 'Calcular' para ver o resultado...")
        layout.addRow(result_box)

        def calcular():
            cv      = spin_cv.value()
            voltage = int(combo_v.currentText().replace("V", ""))
            method  = combo_met.currentText()
            fs      = spin_fs.value()
            fp      = spin_cos.value()
            eta     = spin_eff.value()
            res     = StarterManager.dimension_motor(cv, voltage, method, fs=fs, fp=fp, eta=eta)
            txt = (
                f"=== PLACA DO MOTOR ===\n"
                f"Motor: {edit_label.text()} | {cv} CV | {voltage}V | {spin_rpm.value()} RPM\n"
                f"FS: {spin_fs.value()} | Polos: {spin_polos.value()} | η: {spin_eff.value()}%\n"
                f"Fechamento: {combo_fec.currentText()}\n"
                f"Método de Partida: {method}\n\n"
                f"--- CÁLCULOS TÉCNICOS ---\n"
                f"Corrente Nominal (In):   {res['in_nom_a']} A\n"
                f"Corrente de Partida:     {res['i_start_a']} A\n"
                f"Ajuste do Relé Térmico:  {res['relay_a']} A\n\n"
                f"--- CABOS E PROTEÇÃO ---\n"
                f"Seção do Cabo de Força:  {res['cable_mm2']} mm²\n"
                f"Disjuntor de Proteção:   {res['breaker_a']} A\n\n"
                f"--- COMPONENTES WEG ---\n"
                f"Proteção (MPW/DJ):       {res['protection']}\n"
                f"Acionamento:             {res['contactor']}\n"
            )
            result_box.setPlainText(txt)
            dlg._last_result = res
            dlg._last_label  = edit_label.text()
            dlg._last_plate  = {
                'fs': spin_fs.value(), 'rpm': spin_rpm.value(), 'polos': spin_polos.value(),
                'closure': combo_fec.currentText(), 'eff': spin_eff.value(), 'cos': spin_cos.value()
            }

        btn_row = QtWidgets.QDialogButtonBox()
        btn_calc  = btn_row.addButton("Calcular",  QtWidgets.QDialogButtonBox.ActionRole)
        btn_save  = btn_row.addButton("Salvar no Projeto", QtWidgets.QDialogButtonBox.AcceptRole)
        btn_close = btn_row.addButton("Fechar", QtWidgets.QDialogButtonBox.RejectRole)
        btn_calc.clicked.connect(calcular)
        btn_save.clicked.connect(dlg.accept)
        btn_close.clicked.connect(dlg.reject)
        layout.addRow(btn_row)

        if dlg.exec_() == QtWidgets.QDialog.Accepted and hasattr(dlg, '_last_result'):
            doc = FreeCAD.ActiveDocument
            if doc:
                res = dlg._last_result
                obj = doc.addObject("App::FeaturePython", dlg._last_label.replace(" ", "_"))
                obj.Label = dlg._last_label
                obj.addProperty("App::PropertyString",  "TipoBIM",      "Eletrica", "Tipo").TipoBIM = "Motor"
                obj.addProperty("App::PropertyFloat",   "Potencia_CV",  "Motor",    "Potência (CV)").Potencia_CV = res['cv']
                obj.addProperty("App::PropertyFloat",   "Potencia_kW",  "Motor",    "Potência (kW)").Potencia_kW = res['kw']
                obj.addProperty("App::PropertyFloat",   "Potencia",     "Eletrica", "Potência (VA)").Potencia = res['kw'] * 1000
                obj.addProperty("App::PropertyString",  "TipoPartida",  "Motor",    "Método de Partida").TipoPartida = res['start_method']
                obj.addProperty("App::PropertyFloat",   "CorrenteNom",  "Motor",    "In (A)").CorrenteNom = res['in_nom_a']
                
                # Dados da Placa
                plate = dlg._last_plate
                obj.addProperty("App::PropertyFloat",   "FatorServico", "Motor", "Fator de Serviço (FS)").FatorServico = plate['fs']
                obj.addProperty("App::PropertyInteger", "RPM",          "Motor", "Rotação (RPM)").RPM = plate['rpm']
                obj.addProperty("App::PropertyInteger", "Polos",        "Motor", "Número de Polos").Polos = plate['polos']
                obj.addProperty("App::PropertyString",  "Fechamento",   "Motor", "Tipo de Fechamento").Fechamento = plate['closure']
                obj.addProperty("App::PropertyFloat",   "Rendimento",   "Motor", "Rendimento (%)").Rendimento = plate['eff']
                obj.addProperty("App::PropertyFloat",   "CosPhi",       "Motor", "Fator de Potência").CosPhi = plate['cos']
                
                obj.addProperty("App::PropertyString",  "KitWEG",       "Motor",    "Componentes WEG").KitWEG = f"{res['protection']} + {res['contactor']}"
                doc.recompute()
                FreeCAD.Console.PrintMessage(f"Motor '{obj.Label}' salvo no projeto.\n")


class CheckSelectivity:
    """Realiza o estudo de seletividade e coordenação de proteção"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Selectivity.png'), 'MenuText': tr('Análise de Seletividade'), 'ToolTip': tr('Verifica coordenação entre disjuntores e concessionária') }

    def Activated(self):
        from EletricaLogic.Protection import ProtectionManager
        from EletricaLogic.Settings import ProjectSettings
        
        settings = ProjectSettings.get_settings_obj()
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Estudo de Seletividade e Proteção"))
        layout = QtWidgets.QFormLayout(dlg)
        
        # Campos Concessionária
        spin_icc = QtWidgets.QDoubleSpinBox(); spin_icc.setRange(0, 100); spin_icc.setSuffix(" kA")
        spin_icc.setValue(getattr(settings, "Icc_Concessionaria", 10.0))
        
        spin_xr = QtWidgets.QDoubleSpinBox(); spin_xr.setRange(0, 20)
        spin_xr.setValue(getattr(settings, "XR_Concessionaria", 7.0))
        
        layout.addRow("<b>DADOS DA CONCESSIONÁRIA</b>", QtWidgets.QLabel(""))
        layout.addRow("Icc de Entrega:", spin_icc)
        layout.addRow("Relação X/R:",     spin_xr)
        
        layout.addRow("---", QtWidgets.QLabel(""))
        
        result_box = QtWidgets.QTextEdit()
        result_box.setReadOnly(True)
        result_box.setMinimumHeight(250)
        
        def run_study():
            # Salvar dados novos
            settings.Icc_Concessionaria = spin_icc.value()
            settings.XR_Concessionaria = spin_xr.value()
            
            html_report = ProtectionManager.generate_protection_report()
            result_box.setHtml(html_report)
            
        btn_run = QtWidgets.QPushButton("Executar Estudo de Coordenação")
        btn_run.clicked.connect(run_study)
        
        layout.addRow(btn_run)
        layout.addRow(result_box)
        
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)
        
        dlg.exec_()


class BusbarSizing:
    """Dimensiona barramentos de cobre ou alumínio para painéis CCM/QDC"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Busbar.png'), 'MenuText': 'Dimensionar Barramento', 'ToolTip': 'Cu / Al' }

    def Activated(self):
        from EletricaLogic.Starters import BusbarCalculator

        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Dimensionamento de Barramento"))
        dlg.setMinimumWidth(420)
        layout = QtWidgets.QFormLayout(dlg)

        spin_i   = QtWidgets.QDoubleSpinBox(); spin_i.setRange(1, 5000); spin_i.setValue(200); spin_i.setSuffix(" A")
        combo_m  = QtWidgets.QComboBox(); combo_m.addItems(["Cobre", "Alumínio"])
        combo_ph = QtWidgets.QComboBox(); combo_ph.addItems(["3 fases + Neutro", "3 fases", "Monofásico"])
        result_box = QtWidgets.QTextEdit(); result_box.setReadOnly(True); result_box.setMinimumHeight(150)

        layout.addRow("Corrente Total do Painel:", spin_i)
        layout.addRow("Material:",                combo_m)
        layout.addRow("Configuração:",            combo_ph)
        layout.addRow(result_box)

        def calcular():
            phases = 3 if "3" in combo_ph.currentText() else 1
            res = BusbarCalculator.dimension_busbar(spin_i.value(), combo_m.currentText(), phases)
            txt = (
                f"=== BARRAMENTO DIMENSIONADO ===\n"
                f"Corrente de Projeto:  {res['current_a']} A\n"
                f"Material:            {res['material']}\n"
                f"Área Mínima:         {res['min_area_mm2']} mm²\n\n"
                f"Perfil Selecionado:  {res['designation']}\n"
                f"Capacidade:         {res['bar_capacity_a']} A\n"
                f"Peso Est. (kg/m):   {res['weight_kg_m']} kg\n"
                f"Configuração:       {res['phases_desc']}\n"
            )
            result_box.setPlainText(txt)

        btn_box = QtWidgets.QDialogButtonBox()
        btn_calc  = btn_box.addButton("Calcular",  QtWidgets.QDialogButtonBox.ActionRole)
        btn_close = btn_box.addButton("Fechar",    QtWidgets.QDialogButtonBox.RejectRole)
        btn_calc.clicked.connect(calcular)
        btn_close.clicked.connect(dlg.reject)
        layout.addRow(btn_box)
        dlg.exec_()


class CCMCommandDiagram:
    """Gera diagrama de comando CCM em planilha FreeCAD (texto estruturado)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'CCMDiagram.png'), 'MenuText': 'Gerar Diagrama de Comando CCM', 'ToolTip': 'Gera diagrama de comando para motores cadastrados no projeto' }

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            QtWidgets.QMessageBox.warning(None, "Erro", "Abra um projeto primeiro!")
            return

        motors = [o for o in doc.Objects if hasattr(o, 'TipoBIM') and o.TipoBIM == 'Motor']
        if not motors:
            QtWidgets.QMessageBox.information(None, "CCM", "Nenhum motor cadastrado no projeto.\nUse o Assistente de Motor Industrial primeiro.")
            return

        # Cria/atualiza planilha de diagrama
        sheet = doc.getObject("Diagrama_Comando_CCM")
        if not sheet:
            sheet = doc.addObject("Spreadsheet::Sheet", "Diagrama_Comando_CCM")

        headers = ["Motor", "CV", "kW", "In (A)", "Partida", "Proteção", "Contatora/Inversor", "Cabo Força (mm²)"]
        for col, h in enumerate(headers):
            cell = chr(65 + col) + "1"
            sheet.set(cell, h)
            sheet.setStyle(cell, "bold", "add")

        from EletricaLogic.Starters import StarterManager
        row = 2
        for m in motors:
            cv     = getattr(m, 'Potencia_CV', 0)
            method = getattr(m, 'TipoPartida', 'Direta')
            res    = StarterManager.dimension_motor(cv, start_method=method)
            data   = [m.Label, str(cv), str(res['kw']), str(res['in_nom_a']),
                      method, res['protection'], res['contactor'], str(res['cable_mm2'])]
            for col, val in enumerate(data):
                sheet.set(chr(65 + col) + str(row), val)
            row += 1

        doc.recompute()
        QtWidgets.QMessageBox.information(None, "Diagrama CCM",
            f"{len(motors)} motor(es) processado(s).\nVeja a planilha 'Diagrama_Comando_CCM' no documento.")


        dlg.exec_()

class PowerFactorCorrection:
    """Assistente para correção de Fator de Potência e Reativos"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'PowerFactor.png'),
            'MenuText': tr('Correção de Fator de Potência'),
            'ToolTip': tr('Dimensiona banco de capacitores para o projeto')
        }
    def Activated(self):
        from EletricaLogic.PowerFactor import PowerFactorManager
        
        data = PowerFactorManager.calculate_total_loads()
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Correção de Fator de Potência"))
        layout = QtWidgets.QFormLayout(dlg)
        
        lbl_p = QtWidgets.QLabel(f"<b>{data['p_kw']:.2f} kW</b>")
        lbl_q = QtWidgets.QLabel(f"<b>{data['q_kvar']:.2f} kVAr</b>")
        lbl_fp = QtWidgets.QLabel(f"<b style='color:red'>{data['fp']:.2f}</b>" if data['fp'] < 0.92 else f"<b style='color:green'>{data['fp']:.2f}</b>")
        
        spin_target = QtWidgets.QDoubleSpinBox(); spin_target.setRange(0.8, 1.0); spin_target.setValue(0.95); spin_target.setSingleStep(0.01)
        
        result_box = QtWidgets.QTextEdit()
        result_box.setReadOnly(True)
        
        def calcular():
            res = PowerFactorManager.dimension_capacitor_bank(spin_target.value())
            txt = f"=== RESULTADO DA CORREÇÃO ===\n\n"
            txt += f"FP Atual: {res['current_fp']:.2f}\n"
            txt += f"Potência Ativa: {res['p_kw']:.2f} kW\n"
            txt += f"Potência Reativa necessária: {res['needed_kvar']:.2f} kVAr\n\n"
            
            if res['needed_kvar'] > 0:
                txt += f"Sugestão: Instalar banco de {res['needed_kvar']:.1f} kVAr\n"
                if len(res['stages']) > 1:
                    txt += f"Estágios recomendados: {len(res['stages'])} x {res['stages'][0]:.1f} kVAr"
            else:
                txt += "Nenhuma ação necessária. O FP já está dentro do alvo."
                
            result_box.setPlainText(txt)

        btn_calc = QtWidgets.QPushButton("Calcular Banco de Capacitores")
        btn_calc.clicked.connect(calcular)
        
        layout.addRow("Potência Ativa Total:",   lbl_p)
        layout.addRow("Potência Reativa Atual:", lbl_q)
        layout.addRow("Fator de Potência Atual:", lbl_fp)
        layout.addRow("Fator de Potência Alvo:",  spin_target)
        layout.addRow(btn_calc)
        layout.addRow(result_box)
        
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)
        
        dlg.exec_()

class InsertEmergencyLight:
    """Insere luminária de emergência (Bloco Autônomo)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'EmergencyLight.png'), 'MenuText': tr('Luz de Emergência'), 'ToolTip': tr('Insere bloco autônomo de LED') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        manager = LibraryManager()
        obj = manager.insert_component("Luz_Emergencia_LED.FCStd")
        if obj:
            if not hasattr(obj, "Autonomia"): obj.addProperty("App::PropertyString", "Autonomia", "Seguranca", "Horas").Autonomia = "2h"
            if not hasattr(obj, "FluxoLuminoso"): obj.addProperty("App::PropertyInteger", "FluxoLuminoso", "Seguranca", "Lumens").FluxoLuminoso = 300
            if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "LuzEmergencia"
            FreeCADGui.runCommand("Draft_Move")

class InsertExitSign:
    """Insere placa de sinalização de saída"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ExitSign.png'), 'MenuText': tr('Sinalização de Saída'), 'ToolTip': tr('Placa de Abandono') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        manager = LibraryManager()
        obj = manager.insert_component("Placa_Saida_Sinalizacao.FCStd")
        if obj:
            if not hasattr(obj, "TipoSinal"): obj.addProperty("App::PropertyEnumeration", "TipoSinal", "Seguranca", "Tipo")
            obj.TipoSinal = ["Saida Direita", "Saida Esquerda", "Saida Frontal", "Escada"]
            if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "Sinalizacao"
            FreeCADGui.runCommand("Draft_Move")

class CableTrayAssistant:
    """Assistente de Eletrocalha Industrial com dimensionamento por cabo"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'TrayAssistant.png'), 'MenuText': 'Assistente de Leitos', 'ToolTip': 'Taxa de Ocupação em Bandejas' }

    def Activated(self):
        from EletricaLogic.Conduit import CableTrayCalculator

        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Assistente de Eletrocalha Industrial"))
        dlg.setMinimumWidth(480)
        layout = QtWidgets.QVBoxLayout(dlg)

        # --- Identificação ---
        form = QtWidgets.QFormLayout()
        edit_label   = QtWidgets.QLineEdit("Eletrocalha_1")
        combo_type   = QtWidgets.QComboBox()
        combo_type.addItems(["Perfurada", "Fechada", "Escada (Ladder)", "Arame (Wire Mesh)"])
        combo_mat    = QtWidgets.QComboBox()
        combo_mat.addItems(["Aço Galvanizado", "Aço Inox 304", "Aço Inox 316", "Alumínio", "PVC"])
        form.addRow("Nome:",     edit_label)
        form.addRow("Tipo:",     combo_type)
        form.addRow("Material:", combo_mat)
        layout.addLayout(form)

        # --- Tabela de Cabos ---
        layout.addWidget(QtWidgets.QLabel("Cabos na eletrocalha (quantidade x seção mm²):"))
        table = QtWidgets.QTableWidget(5, 2)
        table.setHorizontalHeaderLabels(["Quantidade", "Seção (mm²)"])
        table.horizontalHeader().setStretchLastSection(True)
        sections = ["1.5", "2.5", "4", "6", "10", "16", "25", "35", "50", "70", "95", "120"]
        for row in range(5):
            qty_item = QtWidgets.QTableWidgetItem("0")
            sec_combo = QtWidgets.QComboBox()
            sec_combo.addItems(sections)
            sec_combo.setCurrentText("2.5")
            table.setItem(row, 0, qty_item)
            table.setCellWidget(row, 1, sec_combo)
        layout.addWidget(table)

        result_box = QtWidgets.QTextEdit()
        result_box.setReadOnly(True)
        result_box.setMaximumHeight(120)
        layout.addWidget(result_box)

        def calcular():
            cables = []
            for row in range(table.rowCount()):
                try:
                    qty = int(table.item(row, 0).text())
                    sec = float(table.cellWidget(row, 1).currentText())
                    if qty > 0:
                        cables.append((qty, sec))
                except:
                    pass
            if not cables:
                result_box.setPlainText("Adicione ao menos um cabo.")
                return
            res = CableTrayCalculator.dimension_tray(cables)
            txt = (
                f"=== ELETROCALHA DIMENSIONADA ===\n"
                f"Área total de cabos:  {res['cables_area_mm2']} mm²\n"
                f"Área mínima (40%):   {res['required_area_mm2']} mm²\n"
                f"Eletrocalha:         {res['designation']}\n"
                f"Taxa de ocupação:   {res['fill_percent']}%\n"
            )
            result_box.setPlainText(txt)
            dlg._result = res

        btn_row = QtWidgets.QHBoxLayout()
        btn_calc  = QtWidgets.QPushButton("Calcular")
        btn_save  = QtWidgets.QPushButton("Salvar no Projeto")
        btn_close = QtWidgets.QPushButton("Fechar")
        btn_calc.clicked.connect(calcular)
        btn_save.clicked.connect(dlg.accept)
        btn_close.clicked.connect(dlg.reject)
        for b in [btn_calc, btn_save, btn_close]:
            btn_row.addWidget(b)
        layout.addLayout(btn_row)

        if dlg.exec_() == QtWidgets.QDialog.Accepted and hasattr(dlg, '_result'):
            FreeCAD.Console.PrintMessage(
                f"Eletrocalha '{edit_label.text()}' dimensionada: "
                f"{dlg._result['designation']} ({dlg._result['fill_percent']}% ocupação).\n"
                f"Desenhe o caminho no modelo para criar a geometria.\n"
            )


class RunSafetyAudit:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.png'), 'MenuText': 'Segurança (NR-10)', 'ToolTip': 'Arco Elétrico' }
    def Activated(self):
        from EletricaLogic.Safety import SafetyManager
        SafetyManager.apply_safety_to_panel(None)

class GenerateProjectQR:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'QR_AR.png'), 'MenuText': 'Gerar QR Code AR', 'ToolTip': 'Realidade Aumentada' }
    def Activated(self):
        from EletricaLogic.AR import ARManager
        ARManager.generate_project_qr_code(None)

class InsertIndustrialSocket:
    """Insere tomada industrial Steck (3P+N+T ou similar)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'IndustrialSocket.png'), 'MenuText': tr('Tomada Industrial'), 'ToolTip': tr('Tomada Steck 16A/32A/63A') }
    def Activated(self):
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Tomada Industrial Steck")
        layout = QtWidgets.QFormLayout(dlg)
        
        combo_current = QtWidgets.QComboBox()
        combo_current.addItems(["16A (Azul/220V)", "32A (Vermelha/380V)", "63A (Vermelha/380V)"])
        
        layout.addRow("Amperagem/Tipo:", combo_current)
        
        def inserir():
            from EletricaLogic.Library import LibraryManager
            manager = LibraryManager()
            # Escolher modelo baseado na amperagem
            model = "Steck_16A_3P_T.FCStd" if "16A" in combo_current.currentText() else "Steck_32A_3P_N_T.FCStd"
            obj = manager.insert_component(model)
            if obj:
                amps = 16 if "16A" in combo_current.currentText() else (32 if "32A" in combo_current.currentText() else 63)
                v = 220 if "220V" in combo_current.currentText() else 380
                watts = amps * v * 1.732 * 0.85 # Estimativa de potência plena
                
                obj.addProperty("App::PropertyFloat",  "Potencia", "Eletrica", "Watts").Potencia = watts
                obj.addProperty("App::PropertyString", "TipoBIM",  "Eletrica", "Tipo").TipoBIM = "TomadaIndustrial"
                obj.addProperty("App::PropertyString", "CorrenteNominal", "Eletrica", "Amperes").CorrenteNominal = f"{amps}A"
                
                # BIM 6D
                obj.addProperty("App::PropertyString", "NumeroSerie",    "Manutencao", "Nº de Série")
                obj.addProperty("App::PropertyString", "DataInstalacao", "Manutencao", "Data Instalação")
                
                FreeCADGui.runCommand("Draft_Move")
            dlg.accept()

        btn_ok = QtWidgets.QPushButton("Inserir")
        btn_ok.clicked.connect(inserir)
        layout.addRow(btn_ok)
        dlg.exec_()

class InsertPLC:
    """Insere CLP ou Módulo de E/S no painel"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PLC.png'), 'MenuText': tr('Inserir CLP/Remota'), 'ToolTip': tr('Controlador Lógico Programável') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        manager = LibraryManager()
        obj = manager.insert_component("CLP_Modular_Industrial.FCStd")
        if obj:
            if not hasattr(obj, "Protocolo"): obj.addProperty("App::PropertyEnumeration", "Protocolo", "Automacao", "Rede Principal")
            obj.Protocolo = ["Profinet", "Profibus DP", "Modbus TCP", "Modbus RTU", "EtherCAT", "Ethernet/IP", "CANopen", "AS-Interface", "MQTT", "OPC UA"]
            
            # Hardware I/O
            if not hasattr(obj, "EntradasDigitais"):   obj.addProperty("App::PropertyInteger", "EntradasDigitais",   "Automacao", "I/O - Entradas Digitais").EntradasDigitais = 16
            if not hasattr(obj, "SaidasDigitais"):    obj.addProperty("App::PropertyInteger", "SaidasDigitais",    "Automacao", "I/O - Saídas Digitais").SaidasDigitais = 16
            if not hasattr(obj, "EntradasAnalogicas"): obj.addProperty("App::PropertyInteger", "EntradasAnalogicas", "Automacao", "I/O - Entradas Analógicas").EntradasAnalogicas = 4
            if not hasattr(obj, "SaidasAnalogicas"):  obj.addProperty("App::PropertyInteger", "SaidasAnalogicas",  "Automacao", "I/O - Saídas Analógicas").SaidasAnalogicas = 2
            
            if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "CLP"
            
            # BIM 6D
            if not hasattr(obj, "NumeroSerie"): obj.addProperty("App::PropertyString", "NumeroSerie", "Manutencao", "Nº de Série")
            
            FreeCADGui.runCommand("Draft_Move")

class InsertHMI:
    """Insere Interface Homem-Máquina (IHM)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'HMI.png'), 'MenuText': tr('Inserir IHM'), 'ToolTip': tr('Interface Homem-Máquina') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        manager = LibraryManager()
        obj = manager.insert_component("IHM_Touch_7pol.FCStd")
        if obj:
            if not hasattr(obj, "Tamanho"): obj.addProperty("App::PropertyString", "Tamanho", "Automacao", "Polegadas").Tamanho = "7\""
            if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "IHM"
            FreeCADGui.runCommand("Draft_Move")

class MotorWiringWizard:
    """Assistente de Alimentação de Motores WEG"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'MotorStarter.png'), 'MenuText': tr('Dimensionar Alimentação Motor'), 'ToolTip': tr('Dimensiona cabos e disjuntores para motores') }
    
    def Activated(self):
        from EletricaLogic.Starters import MotorDimensioning
        import FreeCADGui
        from PySide import QtWidgets
        obj = FreeCADGui.Selection.getSelection()
        if not obj or not hasattr(obj[0], "Potencia"):
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione um Motor no 3D.")
            return
            
        motor = obj[0]
        # Puxar potência em CV/HP
        cv = 1.0
        if hasattr(motor, "PotenciaHP"): cv = motor.PotenciaHP
        elif hasattr(motor, "Potencia"): cv = motor.Potencia / 735.5 # W to CV
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Dimensionamento WEG - Motor")
        layout = QtWidgets.QFormLayout(dlg)
        
        combo_v = QtWidgets.QComboBox(); combo_v.addItems(["220V", "380V", "440V"])
        combo_m = QtWidgets.QComboBox(); combo_m.addItems(["Direta", "Estrela-Triângulo", "Soft-Starter", "Inversor"])
        
        layout.addRow("Tensão de Operação:", combo_v)
        layout.addRow("Método de Partida:", combo_m)
        
        def processar():
            v = int(combo_v.currentText().replace("V", ""))
            res = MotorDimensioning.get_sizing(cv, v, combo_m.currentText())
            
            # Aplicar ao objeto no 3D
            if not hasattr(motor, "SecaoCabo"): motor.addProperty("App::PropertyFloat", "SecaoCabo", "Eletrica", "Cabo (mm2)")
            if not hasattr(motor, "Disjuntor"): motor.addProperty("App::PropertyInteger", "Disjuntor", "Eletrica", "Disjuntor (A)")
            if not hasattr(motor, "CorrenteNom"): motor.addProperty("App::PropertyFloat", "CorrenteNom", "Eletrica", "Corrente (A)")
            if not hasattr(motor, "MetodoPartida"): motor.addProperty("App::PropertyString", "MetodoPartida", "Eletrica", "Método")
            
            motor.SecaoCabo = res['cable']
            motor.Disjuntor = res['breaker']
            motor.CorrenteNom = res['current']
            motor.MetodoPartida = combo_m.currentText()
            
            msg = f"Dimensionamento Concluído para {cv:.1f} CV:\n"
            msg += f"- Corrente: {res['current']:.1f} A\n"
            msg += f"- Cabo Sugerido: {res['cable']:.1f} mm²\n"
            msg += f"- Proteção Sugerida: {res['breaker']} A\n"
            msg += f"Nota: {res['comment']}"
            
            QtWidgets.QMessageBox.information(None, "Sizing WEG", msg)
            dlg.accept()

        btn = QtWidgets.QPushButton("Aplicar Dimensionamento ao Modelo")
        btn.clicked.connect(processar)
        layout.addRow(btn)
        dlg.exec_()

class LightingAnalysis:
    """Assistente de Cálculo Luminotécnico (Método dos Lúmens)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'LightingAnalysis.png'), 'MenuText': tr('Cálculo Luminotécnico'), 'ToolTip': tr('Dimensiona quantidade de luminárias') }
    
    def Activated(self):
        from EletricaLogic.Lighting import LightingExpert
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Dimensionamento Luminotécnico")
        layout = QtWidgets.QFormLayout(dlg)
        
        spin_l = QtWidgets.QDoubleSpinBox(); spin_l.setRange(1, 1000); spin_l.setValue(20); spin_l.setSuffix(" m")
        spin_w = QtWidgets.QDoubleSpinBox(); spin_w.setRange(1, 1000); spin_w.setValue(10); spin_w.setSuffix(" m")
        spin_lux = QtWidgets.QSpinBox(); spin_lux.setRange(50, 2000); spin_lux.setValue(300); spin_lux.setSuffix(" Lux")
        spin_flux = QtWidgets.QSpinBox(); spin_flux.setRange(500, 50000); spin_flux.setValue(4500); spin_flux.setSuffix(" lm")
        
        layout.addRow("Comprimento (X):", spin_l)
        layout.addRow("Largura (Y):", spin_w)
        layout.addRow("Iluminância Alvo:", spin_lux)
        layout.addRow("Fluxo por Luminária:", spin_flux)
        
        def calcular():
            res = LightingExpert.calculate_fixtures(spin_l.value(), spin_w.value(), 3.0, spin_lux.value(), spin_flux.value())
            report = LightingExpert.generate_lighting_report("Galpão Industrial", res)
            
            # Mostrar resultado
            QtWidgets.QMessageBox.information(None, "Resultado", f"Luminárias Necessárias: {res['n_fixtures']}\nArranjo Sugerido: {res['grid_x']}x{res['grid_y']}")
            
            # Opcional: Inserir as luminárias no 3D em grid
            if QtWidgets.QMessageBox.question(None, "Inserção", "Deseja inserir as luminárias no 3D?") == QtWidgets.QMessageBox.Yes:
                from EletricaLogic.Library import LibraryManager
                lib = LibraryManager()
                dx = (spin_l.value()*1000) / res['grid_x']
                dy = (spin_w.value()*1000) / res['grid_y']
                for ix in range(res['grid_x']):
                    for iy in range(res['grid_y']):
                        pos = FreeCAD.Vector(ix*dx + dx/2, iy*dy + dy/2, 4000)
                        obj = lib.insert_component("Luminaria_LED_Industrial.FCStd")
                        if obj: obj.Placement.Base = pos
            dlg.accept()

        btn = QtWidgets.QPushButton("Calcular e Reportar")
        btn.clicked.connect(calcular)
        layout.addRow(btn)
        dlg.exec_()

class PriceEditor:
    """Editor de Preços Paramétricos do Projeto"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'PriceEditor.png'), 'MenuText': tr('Editar Preços'), 'ToolTip': tr('Configura valores unitários para orçamento') }
    
    def Activated(self):
        from EletricaLogic.Budget import BudgetManager
        prices = BudgetManager.load_prices()
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Editor de Preços de Materiais")
        layout = QtWidgets.QVBoxLayout(dlg)
        
        table = QtWidgets.QTableWidget(len(prices), 2)
        table.setHorizontalHeaderLabels(["Item", "Preço Unitário (R$)"])
        
        for i, (item, price) in enumerate(prices.items()):
            table.setItem(i, 0, QtWidgets.QTableWidgetItem(item))
            table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            
        layout.addWidget(table)
        
        def salvar():
            new_prices = {}
            for i in range(table.rowCount()):
                item = table.item(i, 0).text()
                try: price = float(table.item(i, 1).text().replace(",", "."))
                except: price = 0.0
                new_prices[item] = price
            
            # Salvar em JSON no projeto
            import json
            doc = FreeCAD.ActiveDocument
            if doc and doc.FileName:
                path = os.path.join(os.path.dirname(doc.FileName), "precos.json")
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(new_prices, f, indent=4)
                QtWidgets.QMessageBox.information(None, "Sucesso", "Preços salvos no diretório do projeto.")
            else:
                QtWidgets.QMessageBox.warning(None, "Erro", "Salve o arquivo do FreeCAD primeiro para criar o banco de preços.")
            dlg.accept()

        btn = QtWidgets.QPushButton("Salvar Banco de Preços")
        btn.clicked.connect(salvar)
        layout.addWidget(btn)
        dlg.exec_()

class ArcFlashAnalysis:
    """Gera etiquetas de segurança NR-10 / IEEE 1584"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'ArcFlash.png'), 'MenuText': tr('Análise Arc Flash'), 'ToolTip': tr('Calcula energia de arco e EPI necessário') }
    
    def Activated(self):
        from EletricaLogic.Protection import ArcFlashManager, ProtectionManager
        obj = FreeCADGui.Selection.getSelection()
        if not obj:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione um Quadro ou Painel.")
            return
        
        panel = obj[0]
        icc = getattr(panel, "Icc_Calculada", 5.0) # kA
        
        res = ArcFlashManager.calculate_incident_energy(icc, 0.1) # 0.1s padrão de atuação
        
        # Mostrar em uma janela de relatório
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Análise de Arc Flash - NR-10")
        layout = QtWidgets.QVBoxLayout(dlg)
        
        info = QtWidgets.QLabel(f"""
            <b>RESULTADOS TÉCNICOS:</b><br>
            Energia Incidente: {res['incident_energy']:.2f} cal/cm²<br>
            Fronteira de Risco: {res['boundary_m']} metros<br>
            Categoria de EPI: {res['ppe_category']}<br>
        """)
        layout.addWidget(info)
        
        def exportar():
            path = ArcFlashManager.export_safety_label(panel)
            QtWidgets.QMessageBox.information(None, "Segurança", f"Etiqueta exportada para Downloads:\n{path}")
            os.startfile(path)
            
        btn_exp = QtWidgets.QPushButton("Gerar Etiqueta para Impressão (PDF/HTML)")
        btn_exp.clicked.connect(exportar)
        layout.addWidget(btn_exp)
        
        btn_close = QtWidgets.QPushButton("Fechar")
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)
        
        dlg.exec_()

class BIMifyEquipment:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BIMify.png'), 'MenuText': 'BIMificar Objeto', 'ToolTip': 'Converte objeto em equipamento elétrico' }
    def Activated(self):
        from EletricaLogic.Equipment import EquipmentManager
        EquipmentManager.bimify_equipment(None, "Motor")

class ExportDisciplineBIM:
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'IFCExport.png'), 'MenuText': 'Exportar BIM', 'ToolTip': 'Gera IFC da disciplina' }
    def Activated(self):
        from EletricaLogic.Exporter import DisciplineExporter
        DisciplineExporter.run_multi_export("Export")

class CloneFloor:
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'Replicate.svg'), 'MenuText': 'Replicar Redes (Andar)', 'ToolTip': 'Automação'}
    def Activated(self):
        from EletricaLogic.Automation import MultiStoreyManager
        MultiStoreyManager.clone_electrical_to_floor(None, None)

# =============================================================================
# FASE 3: DISTRIBUIÇÃO E ALTA TENSÃO
# =============================================================================

class AerialLineWizard:
    """Assistente de Dimensionamento de Linha Aérea de MT"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'AerialNetwork.png'), 'MenuText': 'Rede Aérea de Distribuição', 'ToolTip': 'Dimensiona linha aérea MT: condutor, postes, queda de tensão' }

    def Activated(self):
        from EletricaLogic.AerialNetwork import AerialNetworkCalculator

        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Assistente de Rede Aérea MT"))
        dlg.setMinimumWidth(480)
        layout = QtWidgets.QFormLayout(dlg)

        spin_kva    = QtWidgets.QDoubleSpinBox(); spin_kva.setRange(1,10000);  spin_kva.setValue(150); spin_kva.setSuffix(" kVA")
        combo_v     = QtWidgets.QComboBox();      combo_v.addItems(["13.8 kV","23.1 kV","34.5 kV","69.0 kV"])
        spin_km     = QtWidgets.QDoubleSpinBox(); spin_km.setRange(0.1,200);   spin_km.setValue(2);    spin_km.setSuffix(" km")
        combo_cond  = QtWidgets.QComboBox();      combo_cond.addItems(["CA","CAA"])
        combo_env   = QtWidgets.QComboBox();      combo_env.addItems(["Urbano","Periurbano","Rural","Travessia"])
        spin_fp     = QtWidgets.QDoubleSpinBox(); spin_fp.setRange(0.5,1.0);   spin_fp.setValue(0.92); spin_fp.setSingleStep(0.01)
        result_box  = QtWidgets.QTextEdit();      result_box.setReadOnly(True); result_box.setMinimumHeight(220)

        layout.addRow("Potência da Carga:",    spin_kva)
        layout.addRow("Tensão da Linha (MT):", combo_v)
        layout.addRow("Comprimento da Linha:", spin_km)
        layout.addRow("Tipo de Condutor:",     combo_cond)
        layout.addRow("Ambiente:",             combo_env)
        layout.addRow("Fator de Potência:",    spin_fp)
        layout.addRow(result_box)

        def calcular():
            kva  = spin_kva.value()
            v    = float(combo_v.currentText().split()[0])
            km   = spin_km.value()
            cond = combo_cond.currentText()
            env  = combo_env.currentText()
            fp   = spin_fp.value()
            res  = AerialNetworkCalculator.dimension_aerial_line(kva, v, km, fp, cond, env)
            txt = (
                f"=== LINHA AÉREA DE DISTRIBUIÇÃO ===\n"
                f"Carga: {kva} kVA | Tensão: {v} kV | Extensão: {km} km\n\n"
                f"--- CONDUTOR ---\n"
                f"Corrente de Linha:   {res['current_a']} A\n"
                f"Condutor Selecionado:{res['conductor']} ({res['conductor_cap_a']} A)\n\n"
                f"--- QUEDA DE TENSÃO ---\n"
                f"Queda calculada:     {res['drop_pct']}%  (limite 7%)\n"
                f"Status:              {res['status']}\n\n"
                f"--- ESTRUTURA ---\n"
                f"Vão médio ({env}): {res['span_m']} m\n"
                f"Número de postes:    {res['num_poles']} postes\n"
                f"Modelo de poste:     {res['pole_model']}\n\n"
                f"--- PROTEÇÃO ---\n"
                f"{res['protection']}\n"
            )
            result_box.setPlainText(txt)

        btn_box = QtWidgets.QDialogButtonBox()
        btn_calc  = btn_box.addButton("Calcular",  QtWidgets.QDialogButtonBox.ActionRole)
        btn_close = btn_box.addButton("Fechar",    QtWidgets.QDialogButtonBox.RejectRole)
        btn_calc.clicked.connect(calcular)
        btn_close.clicked.connect(dlg.reject)
        layout.addRow(btn_box)
        dlg.exec_()


class InsertGroundingRod:
    """Insere haste de aterramento (High-bond ou similar)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingRod.png'), 'MenuText': tr('Inserir Haste'), 'ToolTip': tr('Haste 5/8" x 2.4m') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        manager = LibraryManager()
        obj = manager.insert_component("Haste_Aterramento_3m.FCStd")
        if obj:
            if not hasattr(obj, "Material"): obj.addProperty("App::PropertyString", "Material", "Aterramento", "Tipo").Material = "Aço Cobreado"
            if not hasattr(obj, "Comprimento"): obj.addProperty("App::PropertyFloat", "Comprimento", "Aterramento", "Metros").Comprimento = 2.4
            if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "HasteAterramento"
            FreeCADGui.runCommand("Draft_Move")

class InsertGroundingMesh:
    """Assistente para geração automática de malha de aterramento"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingMesh.png'), 'MenuText': tr('Gerar Malha Terra'), 'ToolTip': tr('Gera grade de cabo nu') }
    
    def Activated(self):
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Assistente de Malha de Terra")
        layout = QtWidgets.QFormLayout(dlg)
        
        spin_w = QtWidgets.QDoubleSpinBox(); spin_w.setRange(1, 500); spin_w.setValue(10); spin_w.setSuffix(" m")
        spin_h = QtWidgets.QDoubleSpinBox(); spin_h.setRange(1, 500); spin_h.setValue(10); spin_h.setSuffix(" m")
        spin_s = QtWidgets.QDoubleSpinBox(); spin_s.setRange(0.5, 50); spin_s.setValue(3); spin_s.setSuffix(" m")
        
        layout.addRow("Largura Total (X):", spin_w)
        layout.addRow("Comprimento Total (Y):", spin_h)
        layout.addRow("Espaçamento (Grid):", spin_s)
        
        def gerar():
            import Draft
            w, h, s = spin_w.value() * 1000, spin_h.value() * 1000, spin_s.value() * 1000
            
            # Gerar linhas em X
            for y in range(0, int(h) + 1, int(s)):
                p1 = FreeCAD.Vector(0, y, 0)
                p2 = FreeCAD.Vector(w, y, 0)
                line = Draft.makeWire([p1, p2])
                line.Label = f"CaboNu_X_{y}"
                line.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "CaboNu"
                line.addProperty("App::PropertyFloat", "Secao", "Eletrica", "mm²").Secao = 50.0
            
            # Gerar linhas em Y
            for x in range(0, int(w) + 1, int(s)):
                p1 = FreeCAD.Vector(x, 0, 0)
                p2 = FreeCAD.Vector(x, h, 0)
                line = Draft.makeWire([p1, p2])
                line.Label = f"CaboNu_Y_{x}"
                line.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "CaboNu"
                line.addProperty("App::PropertyFloat", "Secao", "Eletrica", "mm²").Secao = 50.0
                
            FreeCAD.ActiveDocument.recompute()
            dlg.accept()

        btn_ok = QtWidgets.QPushButton("Gerar Malha 3D")
        btn_ok.clicked.connect(gerar)
        layout.addRow(btn_ok)
        dlg.exec_()

class InsertBareCable:
    """Traça condutor de cobre nu"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BareCable.png'), 'MenuText': tr('Cabo de Cobre Nu'), 'ToolTip': tr('Condutor para aterramento/malha') }
    def Activated(self):
        FreeCADGui.runCommand("Draft_Wire")
        obj = FreeCAD.ActiveDocument.ActiveObject
        if obj:
            if not hasattr(obj, "Secao"): obj.addProperty("App::PropertyFloat", "Secao", "Eletrica", "mm²").Secao = 50.0
            if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "CaboNu"

class InsertBEP:
    """Insere Barramento de Equipotencialização Principal (BEP)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BEP.png'), 'MenuText': tr('Barramento BEP'), 'ToolTip': tr('Equipotencialização Principal') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        manager = LibraryManager()
        obj = manager.insert_component("Barramento_Equipotencializacao_BEP.FCStd")
        if obj:
            if not hasattr(obj, "NumTerminais"): obj.addProperty("App::PropertyInteger", "NumTerminais", "Aterramento", "Furos").NumTerminais = 10
            if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "BEP"
            FreeCADGui.runCommand("Draft_Move")

class InsertGroundingBox:
    """Insere Caixa de Inspeção para Aterramento/SPDA"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingBox.png'), 'MenuText': tr('Caixa de Inspeção'), 'ToolTip': tr('Caixa de solo para aterramento') }
    def Activated(self):
        from EletricaLogic.Library import LibraryManager
        manager = LibraryManager()
        obj = manager.insert_component("Caixa_Inspecao_Solo.FCStd")
        if obj:
            if not hasattr(obj, "Material"): obj.addProperty("App::PropertyEnumeration", "Material", "Aterramento", "Tipo")
            obj.Material = ["Concreto", "Polipropileno", "PVC"]
            if not hasattr(obj, "Dimensoes"): obj.addProperty("App::PropertyString", "Dimensoes", "Aterramento", "Tamanho").Dimensoes = "300x300mm"
            if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo").TipoBIM = "CaixaInspecao"
            FreeCADGui.runCommand("Draft_Move")

class GenerateGroundingReport:
    """Gera relatório de conformidade NBR 15751 e exporta para Downloads"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'GroundingReport.png'), 'MenuText': tr('Relatório NBR 15751'), 'ToolTip': tr('Gera memória de cálculo de aterramento') }

    def Activated(self):
        from EletricaLogic.Protection import GroundingManager
        doc = FreeCAD.ActiveDocument
        
        # Coletar dados da malha do 3D
        cabos = [obj for obj in doc.Objects if getattr(obj, "TipoBIM", "") == "CaboNu"]
        hastes = [obj for obj in doc.Objects if getattr(obj, "TipoBIM", "") == "HasteAterramento"]
        
        l_cabos = sum([getattr(obj, "Length", 0.0)/1000.0 for obj in cabos])
        l_hastes = sum([getattr(obj, "Comprimento", 2.4) for obj in hastes])
        l_total = l_cabos + l_hastes
        
        # Estimar área (bounding box da malha)
        if cabos:
            pts = []
            for c in cabos: pts.extend([p for p in getattr(c, "Points", [])])
            if pts:
                xs = [p.x for p in pts]; ys = [p.y for p in pts]
                area = (max(xs) - min(xs)) * (max(ys) - min(ys)) / 1e6 # m2
            else: area = 100.0
        else: area = 100.0

        # Dialogo de Entrada de Solo
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Parâmetros NBR 15751")
        layout = QtWidgets.QFormLayout(dlg)
        
        spin_rho = QtWidgets.QDoubleSpinBox(); spin_rho.setRange(1, 5000); spin_rho.setValue(100); spin_rho.setSuffix(" ohm.m")
        spin_icc = QtWidgets.QDoubleSpinBox(); spin_icc.setRange(100, 50000); spin_icc.setValue(5000); spin_icc.setSuffix(" A")
        spin_t   = QtWidgets.QDoubleSpinBox(); spin_t.setRange(0.01, 2.0); spin_t.setValue(0.5); spin_t.setSuffix(" s")
        
        layout.addRow("Resistividade Solo (ρ):", spin_rho)
        layout.addRow("Corrente Falta Terra (Icc):", spin_icc)
        layout.addRow("Tempo de Falta (ts):", spin_t)
        
        def exportar():
            res = GroundingManager.calculate_nbr15751_safety(
                spin_rho.value(), spin_icc.value(), spin_t.value(), l_total, area, len(hastes)
            )
            
            # Gerar HTML similar ao site referenciado
            html = f"""
            <html><head><style>
                body {{ font-family: sans-serif; padding: 40px; line-height: 1.6; color: #333; }}
                .header {{ background: #004a99; color: white; padding: 20px; border-radius: 8px; }}
                .status-ok {{ color: green; font-weight: bold; }}
                .status-fail {{ color: red; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background: #f4f4f4; }}
            </style></head><body>
                <div class='header'>
                    <h1>Relatório de Aterramento - NBR 15751</h1>
                    <p>Projeto: {doc.Label} | Data: {QtCore.QDate.currentDate().toString("dd/MM/yyyy")}</p>
                </div>
                
                <h3>1. Dados do Sistema</h3>
                <table>
                    <tr><th>Parâmetro</th><th>Valor</th></tr>
                    <tr><td>Resistividade do Solo</td><td>{res['rho']} ohm.m</td></tr>
                    <tr><td>Comprimento Total Malha</td><td>{l_total:.2f} m</td></tr>
                    <tr><td>Área da Malha</td><td>{area:.2f} m²</td></tr>
                    <tr><td>Corrente de Defeito</td><td>{res['i_fault']} A</td></tr>
                </table>

                <h3>2. Análise de Segurança (Corpo Humano 50kg)</h3>
                <table>
                    <tr><th>Descrição</th><th>Limite Seguro (V)</th><th>Calculado (V)</th><th>Status</th></tr>
                    <tr>
                        <td>Tensão de Toque (Mesh)</td>
                        <td>{res['e_touch_limit']:.2f} V</td>
                        <td>{res['e_mesh_calc']:.2f} V</td>
                        <td class='{"status-ok" if res['e_mesh_calc'] < res['e_touch_limit'] else "status-fail"}'>
                            {"CONFORME" if res['e_mesh_calc'] < res['e_touch_limit'] else "NÃO CONFORME"}
                        </td>
                    </tr>
                    <tr>
                        <td>Tensão de Passo</td>
                        <td>{res['e_step_limit']:.2f} V</td>
                        <td>{res['e_step_calc']:.2f} V</td>
                        <td class='{"status-ok" if res['e_step_calc'] < res['e_step_limit'] else "status-fail"}'>
                            {"CONFORME" if res['e_step_calc'] < res['e_step_limit'] else "NÃO CONFORME"}
                        </td>
                    </tr>
                </table>

                <h3>3. Resultados Globais</h3>
                <p>Resistência de Aterramento Estimada: <b>{res['r_grid']:.4f} Ω</b></p>
                <p>Elevação de Potencial de Solo (GPR): <b>{res['gpr']:.2f} V</b></p>
                
                <hr>
                <p><i>Este relatório foi gerado automaticamente pelo Suite Elite BIM NBR 15751.</i></p>
            </body></html>
            """
            
            # Salvar na pasta Downloads
            download_path = os.path.join(os.path.expanduser("~"), "Downloads", f"Relatorio_Aterramento_{doc.Label}.html")
            with open(download_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            QtWidgets.QMessageBox.information(None, "Relatório", f"Relatório NBR 15751 gerado com sucesso em:\n{download_path}")
            os.startfile(download_path)
            dlg.accept()

        btn_ok = QtWidgets.QPushButton("Gerar Relatório Profissional")
        btn_ok.clicked.connect(exportar)
        layout.addRow(btn_ok)
        dlg.exec_()

class SPDAWizard:
    """Assistente SPDA Completo (NBR 5419) - Questionário de Análise de Risco"""
    def GetResources(self):
        return {'Pixmap': os.path.join(ICON_DIR, 'SPDA.svg'),
                'MenuText': tr('Análise de Risco SPDA (Para-Raios)'),
                'ToolTip': tr('Questionário NBR 5419-2 para determinar necessidade de SPDA')}

    def Activated(self):
        from EletricaLogic.SPDA import SPDACalculator, LOCATION_FACTORS, STRUCTURE_FACTORS, BRASIL_NG

        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Análise de Risco SPDA - NBR 5419"))
        dlg.setMinimumWidth(550)
        layout = QtWidgets.QVBoxLayout(dlg)

        # --- SEÇÃO 1: LOCALIZAÇÃO ---
        group_loc = QtWidgets.QGroupBox(tr("1. Localização e Ambiente"))
        form_loc = QtWidgets.QFormLayout(group_loc)
        
        combo_state = QtWidgets.QComboBox()
        combo_state.addItems(sorted(BRASIL_NG.keys()))
        combo_state.setCurrentText("SP")
        
        spin_ng = QtWidgets.QDoubleSpinBox()
        spin_ng.setRange(0.1, 50.0)
        spin_ng.setValue(BRASIL_NG["SP"])
        spin_ng.setSuffix(" raios/km²/ano")
        
        def update_ng():
            spin_ng.setValue(BRASIL_NG.get(combo_state.currentText(), 7.0))
        combo_state.currentTextChanged.connect(update_ng)

        combo_loc = QtWidgets.QComboBox()
        combo_loc.addItems(list(LOCATION_FACTORS.keys()))
        
        form_loc.addRow(tr("Estado (UF):"), combo_state)
        form_loc.addRow(tr("Densidade (Ng):"), spin_ng)
        form_loc.addRow(tr("Fator de Localização (Cd):"), combo_loc)
        layout.addWidget(group_loc)

        # --- SEÇÃO 2: ESTRUTURA ---
        group_est = QtWidgets.QGroupBox(tr("2. Características da Estrutura"))
        form_est = QtWidgets.QFormLayout(group_est)
        
        spin_l = QtWidgets.QDoubleSpinBox(); spin_l.setRange(1, 1000); spin_l.setValue(20); spin_l.setSuffix(" m")
        spin_w = QtWidgets.QDoubleSpinBox(); spin_w.setRange(1, 1000); spin_w.setValue(15); spin_w.setSuffix(" m")
        spin_h = QtWidgets.QDoubleSpinBox(); spin_h.setRange(1, 500);  spin_h.setValue(10); spin_h.setSuffix(" m")
        
        combo_str = QtWidgets.QComboBox()
        combo_str.addItems(list(STRUCTURE_FACTORS.keys()))
        
        form_est.addRow(tr("Comprimento (L):"), spin_l)
        form_est.addRow(tr("Largura (W):"),     spin_w)
        form_est.addRow(tr("Altura (H):"),      spin_h)
        form_est.addRow(tr("Tipo de Estrutura:"), combo_str)
        layout.addWidget(group_est)

        # --- SEÇÃO 3: RESULTADO ---
        result_box = QtWidgets.QTextEdit()
        result_box.setReadOnly(True)
        result_box.setMinimumHeight(200)
        result_box.setStyleSheet("background-color: #111; color: #00ff00; font-family: 'Consolas';")
        layout.addWidget(result_box)

        def calcular():
            res = SPDACalculator.full_design(
                spin_l.value(), spin_w.value(), spin_h.value(),
                spin_ng.value(), combo_loc.currentText(), combo_str.currentText())
            
            ra = res['risk_analysis']
            status_color = "#2ecc71" if not ra['spda_required'] else "#e74c3c"
            status_text = "NÃO OBRIGATÓRIO" if not ra['spda_required'] else f"OBRIGATÓRIO (Nível {res['level']})"
            
            txt = [
                "=== RELATÓRIO DE RISCO NBR 5419-2 ===",
                f"Projeto: {FreeCAD.ActiveDocument.Name}",
                f"Local: {combo_state.currentText()} (Ng={spin_ng.value()})",
                "-"*40,
                f"Área de Exposição (Ae): {ra['ae_m2']} m²",
                f"Frequência de Raios (Nd): {ra['nd_strikes_yr']:.6f} raios/ano",
                f"Risco Calculado (R): {ra['risk']:.2e}",
                f"Risco Tolerável (Rt): {ra['tolerable']:.2e}",
                "-"*40,
                f"STATUS: {status_text}",
                "-"*40
            ]
            
            if ra['spda_required']:
                txt += [
                    f"ESPECIFICAÇÕES TÉCNICAS (LPL {res['level']}):",
                    f"- Malha de Captação: {res['mesh']}",
                    f"- Condutor de Descida: {res['conductor_mm2']} mm²",
                    f"- Nº Mínimo Descidas: {res['down_conductors']}",
                    f"- Esfera Rolante: R={res['sphere_radius_m']}m",
                    f"- Aterramento: {res['grounding_rods']} hastes",
                    f"- Proteção: {res['dps_class']}"
                ]
            else:
                txt.append("A estrutura está abaixo do limite de risco normativo.")
                
            result_box.setPlainText("\n".join(txt))

        btn_box = QtWidgets.QDialogButtonBox()
        btn_calc = btn_box.addButton(tr("Processar Análise"), QtWidgets.QDialogButtonBox.ActionRole)
        btn_save = btn_box.addButton(tr("Salvar Memória"), QtWidgets.QDialogButtonBox.AcceptRole)
        btn_close = btn_box.addButton(tr("Fechar"), QtWidgets.QDialogButtonBox.RejectRole)
        
        btn_calc.clicked.connect(calcular)
        btn_save.clicked.connect(dlg.accept)
        btn_close.clicked.connect(dlg.reject)
        layout.addWidget(btn_box)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # Persistência dos dados de risco no documento para o Relatório Master
            doc = FreeCAD.ActiveDocument
            meta = doc.getObject("Eletrica_ProjectData")
            if meta:
                # Obter o último resultado calculado para salvar
                res = SPDACalculator.full_design(
                    spin_l.value(), spin_w.value(), spin_h.value(),
                    spin_ng.value(), combo_loc.currentText(), combo_str.currentText())
                ra = res['risk_analysis']
                
                # Criar propriedades se não existirem
                props = {
                    "SPDARisk": ("App::PropertyString", f"{ra['risk']:.2e}"),
                    "SPDAStatus": ("App::PropertyString", "OBRIGATÓRIO" if ra['spda_required'] else "NÃO OBRIGATÓRIO"),
                    "SPDALevel": ("App::PropertyString", res['level']),
                    "SPDAMesh": ("App::PropertyString", res['mesh']),
                    "SPDADowns": ("App::PropertyInteger", res['down_conductors']),
                    "SPDASphere": ("App::PropertyFloat", float(res['sphere_radius_m'])),
                    "SPDARequired": ("App::PropertyBool", bool(ra['spda_required']))
                }
                
                for p_name, (p_type, p_val) in props.items():
                    if not hasattr(meta, p_name):
                        meta.addProperty(p_type, p_name, "SPDA", "Resultado da última análise de risco")
                    setattr(meta, p_name, p_val)
                
                doc.recompute()
                FreeCAD.Console.PrintMessage("Análise SPDA vinculada à Memória Técnica do Projeto.\n")
            
            QtWidgets.QMessageBox.information(None, "Projeto QR", f"QR Code do Projeto gerado com sucesso!\nLink: {link}")

class GenerateMaintenanceQR:
    """Gera QR Codes de Manutenção para os equipamentos selecionados"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'QRMaintenance.png'),
            'MenuText': tr('Gerar QR Codes de Manutenção'),
            'ToolTip': tr('Cria fichas técnicas e QRs para gestão de ativos (BIM 7D)')
        }
    def Activated(self):
        from EletricaLogic.Maintenance import MaintenanceManager
        selection = FreeCADGui.Selection.getSelection()
        
        if not selection:
            QtWidgets.QMessageBox.warning(None, "Erro", "Selecione um ou mais equipamentos primeiro!")
            return
            
        count = 0
        for obj in selection:
            if hasattr(obj, "TipoBIM"):
                MaintenanceManager.generate_qr_for_obj(obj)
                count += 1
        
        if count > 0:
            QtWidgets.QMessageBox.information(None, "Sucesso", f"QR Codes e Fichas Técnicas gerados para {count} equipamento(s).\nVerifique a pasta 'Manutencao' no diretório do projeto.")
        else:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Nenhum objeto compatível (BIM) foi encontrado na seleção.")

class SubstationWizard:
    """Assistente de Subestação e Demanda Contratada"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Substation.png'), 'MenuText': tr('Assistente de Subestação'), 'ToolTip': tr('Dimensiona entrada e contrato de demanda') }

    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        from EletricaLogic.Settings import ProjectSettings
        
        settings = ProjectSettings.get_settings_obj()
        demand_data = CircuitManager.estimate_demand()
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(tr("Assistente de Subestação e Demanda"))
        layout = QtWidgets.QFormLayout(dlg)
        
        # Resumo de Cargas
        layout.addRow("<b>RESUMO DE CARGAS</b>", QtWidgets.QLabel(""))
        layout.addRow("Carga Instalada:", QtWidgets.QLabel(f"{demand_data['p_installed_kw']:.2f} kW"))
        layout.addRow("Demanda de Pico (Estimada):", QtWidgets.QLabel(f"<b>{demand_data['demand_peak_kw']:.2f} kW</b>"))
        
        layout.addRow("---", QtWidgets.QLabel(""))
        
        # Configuração de Contrato
        spin_contract = QtWidgets.QDoubleSpinBox(); spin_contract.setRange(0, 5000); spin_contract.setSuffix(" kW")
        spin_contract.setValue(getattr(settings, "DemandaContratada_kW", demand_data['demand_peak_kw']))
        
        combo_tariff = QtWidgets.QComboBox()
        combo_tariff.addItems(["Verde", "Azul", "Branca", "Convencional"])
        if hasattr(settings, "TipoTarifa"): combo_tariff.setCurrentText(settings.TipoTarifa)
        
        edit_v = QtWidgets.QLineEdit(getattr(settings, "TensaoFornecimento", "13.8 kV"))
        
        layout.addRow("<b>DADOS CONTRATUAIS</b>", QtWidgets.QLabel(""))
        layout.addRow("Demanda a Contratar:", spin_contract)
        layout.addRow("Modalidade Tarifária:", combo_tariff)
        layout.addRow("Tensão de Fornecimento:", edit_v)
        
        layout.addRow("---", QtWidgets.QLabel(""))
        
        # Sugestão de Trafo
        layout.addRow("Trafo Sugerido (S ≥ D/0.92):", QtWidgets.QLabel(f"<b style='color:blue'>{demand_data['suggested_trafo_kva']} kVA</b>"))
        
        def salvar():
            settings.DemandaContratada_kW = spin_contract.value()
            settings.TipoTarifa = combo_tariff.currentText()
            settings.TensaoFornecimento = edit_v.text()
            
            # Criar objeto BIM de Subestação se aceito
            from EletricaLogic.Library import LibraryManager
            manager = LibraryManager()
            obj = manager.insert_component("Subestacao_Industrial.FCStd")
            if obj:
                obj.Label = f"Subestacao_{demand_data['suggested_trafo_kva']}kVA"
                if not hasattr(obj, "PotenciaTrafo"): obj.addProperty("App::PropertyFloat", "PotenciaTrafo", "Eletrica", "Potência (kVA)")
                obj.PotenciaTrafo = demand_data['suggested_trafo_kva']
                if not hasattr(obj, "TipoBIM"): obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo")
                obj.TipoBIM = "Subestacao"
            
            dlg.accept()

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(salvar)
        btn_box.rejected.connect(dlg.reject)
        layout.addRow(btn_box)
        
        dlg.exec_()


class ConsolidateMultiDocument:
    """Agrega dados de todos os documentos elétricos abertos"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Consolidate.png'), 'MenuText': 'Consolidar Projeto (Multi-Arquivo)', 'ToolTip': 'Soma cargas e materiais de todos os documentos abertos' }

    def Activated(self):
        from EletricaLogic.ProjectManager import MultiDocumentManager
        total, summary = MultiDocumentManager.aggregate_load_data()
        
        txt = f"=== CONSOLIDAÇÃO MASTER ===\n"
        txt += f"Carga Total Master: {total:,.0f} VA\n\n"
        txt += "Detalhamento por Arquivo:\n"
        for doc_name, va in summary.items():
            txt += f"- {doc_name}: {va:,.0f} VA\n"
            
        QtWidgets.QMessageBox.information(None, "Master Project Manager", txt)

class RunProjectAudit:
    """Executa a auditoria completa de normas e segurança"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'SafetyNR10.png'),
            'MenuText': tr('Auditoria de Projeto'),
            'ToolTip': tr('Verifica erros de norma, queda de tensão e colisões')
        }
    def Activated(self):
        from EletricaLogic.Auditor import ProjectAuditor
        ProjectAuditor.run_full_audit()

class GenerateTags:
    """Gera etiquetas de identificação no 3D"""
    def GetResources(self):
        return {
            'Pixmap': os.path.join(ICON_DIR, 'QR_AR.png'),
            'MenuText': tr('Gerar Etiquetas 3D'),
            'ToolTip': tr('Cria etiquetas de circuito e bitola sobre os componentes')
        }
    def Activated(self):
        from EletricaLogic.Tagging import TagManager
        TagManager.generate_circuit_tags()

class ProjectMetadata(ProjectProperties):
    """Apelido para ProjectProperties"""
    pass

class ConsolidateProject(ConsolidateMultiDocument):
    """Apelido para ConsolidateMultiDocument"""
    pass

class ExportBOM:
    """Exporta Lista de Materiais (BOM) para Excel/CSV"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'BOM.png'), 'MenuText': tr('Exportar Lista de Materiais'), 'ToolTip': tr('Gera lista quantitativa de todos os componentes') }
    def Activated(self):
        from EletricaLogic.BOM import BOMManager
        BOMManager.export_bom_to_csv()

class MTInstrumentationWizard:
    """Dimensionamento de Instrumentação MT (TC/TP)"""
    def GetResources(self):
        return { 'Pixmap': os.path.join(ICON_DIR, 'Substation.png'), 'MenuText': tr('Dimensionar TC/TP'), 'ToolTip': tr('Dimensiona transformadores de instrumento para MT') }
    
    def Activated(self):
        from EletricaLogic.Substation import InstrumentationManager
        import FreeCADGui
        from PySide import QtWidgets
        
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("Dimensionamento TC/TP")
        layout = QtWidgets.QFormLayout(dlg)
        
        spin_i = QtWidgets.QDoubleSpinBox(); spin_i.setRange(1, 1000); spin_i.setValue(100); spin_i.setSuffix(" A")
        combo_v = QtWidgets.QComboBox(); combo_v.addItems(["13.8 kV", "23.1 kV", "34.5 kV"])
        
        layout.addRow("Corrente Primária Máxima:", spin_i)
        layout.addRow("Tensão do Sistema:", combo_v)
        
        def processar():
            v = float(combo_v.currentText().split()[0])
            tc = InstrumentationManager.dimension_tc(spin_i.value())
            tp = InstrumentationManager.dimension_tp(v)
            
            msg = "RESULTADO DA INSTRUMENTAÇÃO:\n\n"
            msg += f"TC Sugerido: {tc['ratio']} | Classe: {tc['class']} | Carga: {tc['burden']}\n"
            msg += f"TP Sugerido: {tp['ratio']} | Classe: {tp['class']} | Carga: {tp['burden']}\n"
            
            QtWidgets.QMessageBox.information(None, "Dimensionamento MT", msg)
            dlg.accept()

        btn = QtWidgets.QPushButton("Calcular Instrumentação")
        btn.clicked.connect(processar)
        layout.addRow(btn)
        dlg.exec_()

# --- REGISTRO DE COMANDOS ---
cmds = {
    'Eletrica_MTInstrumentationWizard': MTInstrumentationWizard(),
    'Eletrica_StartNewProject': StartNewProject(),
    'Eletrica_ProjectProperties': ProjectProperties(),
    'Eletrica_ToggleDashboard': ToggleDashboard(),
    'Eletrica_ConsolidateMultiDocument': ConsolidateMultiDocument(),
    'Eletrica_CreatePanel': CreatePanel(),
    'Eletrica_InsertSocket': InsertSocket(),
    'Eletrica_InsertSpecialSocket': InsertSpecialSocket(),
    'Eletrica_InsertLight': InsertLight(),
    'Eletrica_InsertSwitch': InsertSwitch(),
    'Eletrica_MergeSwitches': MergeSwitches(),
    'Eletrica_InsertSmartDevice': InsertSmartDevice(),
    'Eletrica_InsertAirConditioner': InsertAirConditioner(),
    'Eletrica_MotorWiringWizard': MotorWiringWizard(),
    'Eletrica_InsertPumpSet': InsertPumpSet(),
    'Eletrica_InsertTelecomPoint': InsertTelecomPoint(),
    'Eletrica_InsertVDIRack': InsertVDIRack(),
    'Eletrica_ToggleVoltageDropHeatmap': ToggleVoltageDropHeatmap(),
    'Eletrica_InsertPumpSet': InsertPumpSet(),
    'Eletrica_LinkPumpSet': LinkPumpSet(),
    'Eletrica_CreateConduit': CreateConduit(),
    'Eletrica_CreateCableTray': CreateCableTray(),
    'Eletrica_CreateIndustrialConnection': CreateIndustrialConnection(),
    'Eletrica_Generate3DWiring': Generate3DWiring(),
    'Eletrica_ServiceEntranceWizard': ServiceEntranceWizard(),
    'Eletrica_InsertSubstation': InsertSubstation(),
    'Eletrica_InsertBoreholePump': InsertBoreholePump(),
    # --- Fase 2: Industrial & Segurança ---
    'Eletrica_DimensionMotorStarter': DimensionMotorStarter(),
    'Eletrica_CheckSelectivity': CheckSelectivity(),
    'Eletrica_PowerFactorCorrection': PowerFactorCorrection(),
    'Eletrica_InsertEmergencyLight': InsertEmergencyLight(),
    'Eletrica_InsertExitSign': InsertExitSign(),
    'Eletrica_InsertIndustrialSocket': InsertIndustrialSocket(),
    'Eletrica_InsertPLC': InsertPLC(),
    'Eletrica_InsertHMI': InsertHMI(),
    'Eletrica_InsertGroundingRod': InsertGroundingRod(),
    'Eletrica_InsertGroundingMesh': InsertGroundingMesh(),
    'Eletrica_InsertBareCable': InsertBareCable(),
    'Eletrica_InsertBEP': InsertBEP(),
    'Eletrica_InsertGroundingBox': InsertGroundingBox(),
    'Eletrica_GenerateGroundingReport': GenerateGroundingReport(),
    'Eletrica_LightingAnalysis': LightingAnalysis(),
    'Eletrica_PriceEditor': PriceEditor(),
    'Eletrica_ArcFlashAnalysis': ArcFlashAnalysis(),
    'Eletrica_BusbarSizing': BusbarSizing(),
    'Eletrica_CCMCommandDiagram': CCMCommandDiagram(),
    'Eletrica_CableTrayAssistant': CableTrayAssistant(),
    # --- Fase 3: Distribuição e Alta Tensão ---
    'Eletrica_AerialLineWizard': AerialLineWizard(),
    'Eletrica_SPDAWizard': SPDAWizard(),
    'Eletrica_SubstationWizard': SubstationWizard(),
    # --- Outros ---
    'Eletrica_SetupEmergencyPower': SetupEmergencyPower(),
    'Eletrica_GenerateLoadSchedule': GenerateLoadSchedule(),
    'Eletrica_GenerateCableSchedule': GenerateCableSchedule(),
    'Eletrica_GenerateBudget': GenerateBudget(),
    'Eletrica_GenerateUnifilar': GenerateUnifilar(),
    'Eletrica_SyncTitleBlock': SyncTitleBlock(),
    'Eletrica_RunProjectAudit': RunProjectAudit(),
    'Eletrica_GenerateTags': GenerateTags(),
    'Eletrica_RunSafetyAudit': RunSafetyAudit(),
    'Eletrica_GenerateProjectQR': GenerateProjectQR(),
    'Eletrica_GenerateMaintenanceQR': GenerateMaintenanceQR(),
    'Eletrica_BIMifyEquipment': BIMifyEquipment(),
    'Eletrica_ExportDisciplineBIM': ExportDisciplineBIM(),
    'Eletrica_CloneFloor': CloneFloor(),
    'Eletrica_ConsolidateProject': ConsolidateProject(),
    'Eletrica_ProjectMetadata': ProjectMetadata(),
    'Eletrica_ExportBOM': ExportBOM()
}

for name, obj in cmds.items():
    FreeCADGui.addCommand(name, obj)
