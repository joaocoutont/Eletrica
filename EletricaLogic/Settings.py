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
            obj.addProperty("App::PropertyEnumeration", "Tensao", "Geral", "Tensao nominal do projeto")
            obj.Tensao = ["127V", "220V", "380V"]
            obj.Tensao = "220V"
            
            obj.addProperty("App::PropertyFloat", "FatorPotencia", "Geral", "Fator de potencia global")
            obj.FatorPotencia = 0.95
            
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
