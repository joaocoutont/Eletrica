# Gerenciamento de Configuracoes Globais do Projeto
import FreeCAD

class ProjectSettings:
    @staticmethod
    def parse_voltage(value, default=220.0):
        """Converte valores como 220V, 127/220V, 13.8kV ou numeros em volts."""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()
        if not text:
            return default
        if "/" in text:
            text = text.split("/")[-1]

        import re
        text = text.replace(",", ".")
        lower = text.lower()
        multiplier = 1000.0 if "kv" in lower else 1.0
        lower = lower.replace("kv", "").replace("v", "").replace(" ", "")
        numbers = re.findall(r"\d+(?:\.\d+)?", lower)
        if numbers:
            lower = numbers[-1]

        try:
            return float(lower) * multiplier
        except ValueError:
            return default

    @staticmethod
    def format_voltage(value, default="220V"):
        """Retorna uma tensao em texto compativel com enums comuns da bancada."""
        voltage = ProjectSettings.parse_voltage(value, ProjectSettings.parse_voltage(default))
        if voltage >= 1000:
            return f"{voltage / 1000.0:g}kV"
        return f"{int(voltage) if voltage.is_integer() else voltage:g}V"

    @staticmethod
    def _ensure_property(obj, prop_type, name, group, description, default=None):
        """Adiciona a propriedade se ela ainda nao existir."""
        if not hasattr(obj, name):
            obj.addProperty(prop_type, name, group, description)
            if default is not None:
                setattr(obj, name, default)

    @staticmethod
    def get_project_data_obj():
        """Retorna ou cria os metadados do projeto usados em pranchas, IFC e relatorios."""
        doc = FreeCAD.ActiveDocument
        if not doc:
            return None

        obj = doc.getObject("Eletrica_ProjectData")
        if not obj:
            obj = doc.addObject("App::FeaturePython", "Eletrica_ProjectData")
            obj.Label = "Dados do Projeto Eletrica"

        legacy = doc.getObject("Configuracoes_Eletrica")

        ProjectSettings._ensure_property(obj, "App::PropertyString", "ProjectName", "Geral", "Nome do projeto", getattr(legacy, "NomeProjeto", ""))
        ProjectSettings._ensure_property(obj, "App::PropertyString", "Author", "Geral", "Autor / Engenheiro responsavel", getattr(legacy, "Autor", ""))
        ProjectSettings._ensure_property(obj, "App::PropertyString", "ProjectType", "Geral", "Tipo de obra", "")

        ProjectSettings._ensure_property(obj, "App::PropertyString", "Utility", "Tecnico", "Concessionaria de energia", "")
        ProjectSettings._ensure_property(obj, "App::PropertyString", "PrimaryVoltage", "Tecnico", "Tensao primaria MT", "")
        ProjectSettings._ensure_property(obj, "App::PropertyString", "Voltage", "Tecnico", "Tensao secundaria BT", getattr(legacy, "TensaoPadrao", "220V"))
        ProjectSettings._ensure_property(obj, "App::PropertyString", "SystemPhases", "Tecnico", "Sistema de fases", getattr(legacy, "SistemaPadrao", "Trifasico (3F+N)"))
        ProjectSettings._ensure_property(obj, "App::PropertyFloat", "TrafoPower", "Tecnico", "Potencia do transformador em kVA", 0.0)
        ProjectSettings._ensure_property(obj, "App::PropertyFloat", "TransformerImpedance", "Tecnico", "Impedancia do transformador em percentual", 5.0)
        ProjectSettings._ensure_property(obj, "App::PropertyFloat", "Icc_Concessionaria", "Tecnico", "Icc no ponto de entrega em kA", 10.0)
        ProjectSettings._ensure_property(obj, "App::PropertyEnumeration", "ConductorMaterial", "Tecnico", "Material do condutor")
        obj.ConductorMaterial = ["Cobre", "Aluminio"]
        ProjectSettings._ensure_property(obj, "App::PropertyEnumeration", "InsulationType", "Tecnico", "Tipo de isolacao")
        obj.InsulationType = ["PVC 70C", "EPR 90C"]
        ProjectSettings._ensure_property(obj, "App::PropertyEnumeration", "CableType", "Tecnico", "Construcao do cabo")
        obj.CableType = ["Unipolar", "Multipolar"]
        ProjectSettings._ensure_property(obj, "App::PropertyString", "InstallationMethod", "Tecnico", "Metodo de instalacao NBR 5410", "B1")
        ProjectSettings._ensure_property(obj, "App::PropertyFloat", "AmbientTemperature", "Tecnico", "Temperatura ambiente em C", 30.0)
        ProjectSettings._ensure_property(obj, "App::PropertyFloat", "PowerFactor", "Tecnico", "Fator de potencia global", getattr(legacy, "FatorPotencia", 0.95))
        ProjectSettings._ensure_property(obj, "App::PropertyString", "MaxVoltageDrop", "Tecnico", "Limite de queda de tensao", "4%")
        ProjectSettings._ensure_property(obj, "App::PropertyString", "TrafoConnection", "Tecnico", "Grupo vetorial do transformador", "")
        ProjectSettings._ensure_property(obj, "App::PropertyString", "Phase", "Tecnico", "Fase do projeto", "Executivo")

        ProjectSettings._ensure_property(obj, "App::PropertyString", "DesignerName", "Projetista", "Nome do responsavel tecnico", "")
        ProjectSettings._ensure_property(obj, "App::PropertyString", "DesignerProfession", "Projetista", "Profissao do responsavel tecnico", "")
        ProjectSettings._ensure_property(obj, "App::PropertyString", "CREA", "Projetista", "Numero do CREA / CFT", "")
        ProjectSettings._ensure_property(obj, "App::PropertyString", "ART", "Projetista", "Numero da ART", "")

        try:
            obj.ViewObject.Proxy = None
        except Exception:
            pass

        return obj

    @staticmethod
    def get_settings_obj():
        """Retorna ou cria o objeto de configuracoes no documento"""
        doc = FreeCAD.ActiveDocument
        if not doc: return None
        
        obj = doc.getObject("Configuracoes_Eletrica")
        if not obj:
            obj = doc.addObject("App::FeaturePython", "Configuracoes_Eletrica")
            obj.addProperty("App::PropertyString", "Autor", "Geral", "Autor do projeto")
            obj.addProperty("App::PropertyString", "NomeProjeto", "Geral", "Nome do projeto")
            
            obj.addProperty("App::PropertyEnumeration", "Language", "Geral", "Idioma da Interface")
            obj.Language = ["pt-BR", "en-US", "es-ES"]
            obj.Language = "pt-BR"

            obj.addProperty("App::PropertyEnumeration", "SistemaPadrao", "Eletrica", "Sistema Padrão do Projeto")
            obj.SistemaPadrao = ["Monofasico (F+N)", "Bifasico (2F+N)", "Trifasico (3F+N)"]
            obj.SistemaPadrao = "Trifasico (3F+N)"
            
            obj.addProperty("App::PropertyEnumeration", "TensaoPadrao", "Eletrica", "Tensão Padrão do Projeto")
            obj.TensaoPadrao = ["127V", "220V", "380V"]
            obj.TensaoPadrao = "220V"
            
            obj.addProperty("App::PropertyFloat", "FatorPotencia", "Eletrica", "Fator de potencia global")
            obj.FatorPotencia = 0.95

            # --- ESQUEMA DE ATERRAMENTO NBR 5410 ---
            obj.addProperty("App::PropertyEnumeration", "EsquemaAterramento", "Engenharia", "Esquema de Aterramento (NBR 5410)")
            obj.EsquemaAterramento = ["TN-S", "TN-C", "TN-C-S", "TT", "IT"]
            obj.EsquemaAterramento = 0 # Default TN-S
            
            obj.ViewObject.Proxy = None # Objeto sem representacao visual
            
        return obj

    @staticmethod
    def get_voltage():
        obj = ProjectSettings.get_settings_obj()
        if not obj: return 220.0
        return ProjectSettings.parse_voltage(obj.TensaoPadrao)

    @staticmethod
    def get_fp():
        obj = ProjectSettings.get_settings_obj()
        if not obj: return 0.95
        return obj.FatorPotencia
