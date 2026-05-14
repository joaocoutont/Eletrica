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
        val = obj.TensaoPadrao
        return float(val.replace("V", ""))

    @staticmethod
    def get_fp():
        obj = ProjectSettings.get_settings_obj()
        if not obj: return 0.95
        return obj.FatorPotencia
