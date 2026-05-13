# Gerenciamento de Configuracoes Globais do Projeto
import FreeCAD

class ProjectSettings:
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

            obj.addProperty("App::PropertyEnumeration", "Sistema", "Eletrica", "Sistema de fornecimento")
            obj.Sistema = ["Monofasico (F+N)", "Bifasico (2F+N)", "Trifasico (3F+N)"]
            obj.Sistema = "Trifasico (3F+N)"
            
            obj.addProperty("App::PropertyEnumeration", "Tensao", "Eletrica", "Tensao nominal")
            obj.Tensao = ["127V", "220V", "380V"]
            obj.Tensao = "220V"
            
            obj.addProperty("App::PropertyFloat", "FatorPotencia", "Eletrica", "Fator de potencia global")
            obj.FatorPotencia = 0.95

            obj.addProperty("App::PropertyFloat", "TransformerImpedance", "Engenharia", "Impedância do Trafo (%)")
            obj.TransformerImpedance = 5.0

            # --- DADOS DA CONCESSIONÁRIA ---
            obj.addProperty("App::PropertyFloat", "Icc_Concessionaria", "Concessionaria", "Icc no Ponto de Entrega (kA)")
            obj.Icc_Concessionaria = 10.0
            obj.addProperty("App::PropertyFloat", "XR_Concessionaria",  "Concessionaria", "Relação X/R")
            obj.XR_Concessionaria = 7.0
            obj.addProperty("App::PropertyFloat", "Scc_Concessionaria", "Concessionaria", "Potência de Curto (MVA)")
            obj.Scc_Concessionaria = 250.0

            # --- DADOS DE CONTRATO E DEMANDA ---
            obj.addProperty("App::PropertyFloat", "DemandaContratada_kW", "Contrato", "Demanda Contratada (kW)")
            obj.DemandaContratada_kW = 50.0
            obj.addProperty("App::PropertyEnumeration", "TipoTarifa", "Contrato", "Modalidade Tarifária")
            obj.TipoTarifa = ["Verde", "Azul", "Branca", "Convencional"]
            obj.addProperty("App::PropertyString", "TensaoFornecimento", "Contrato", "Tensão de Fornecimento (kV)").TensaoFornecimento = "13.8 kV"
            
            obj.addProperty("App::PropertyFloat", "DemandaEstimada_kW", "Engenharia", "Demanda Estimada de Pico (kW)")
            obj.DemandaEstimada_kW = 0.0

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
        val = obj.Tensao
        return float(val.replace("V", ""))

    @staticmethod
    def get_fp():
        obj = ProjectSettings.get_settings_obj()
        if not obj: return 0.95
        return obj.FatorPotencia
