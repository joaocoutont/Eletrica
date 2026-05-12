# Gerenciamento de Quadros e Hierarquia
import FreeCAD

class PanelManager:
    @staticmethod
    def create_panel(name, panel_type="QDC"):
        """Cria um quadro de distribuicao inteligente com suporte industrial"""
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("App::FeaturePython", name.replace(" ", "_"))
        obj.Label = name
        
        # Propriedades de Hierarquia e Tipo
        obj.addProperty("App::PropertyEnumeration", "Funcao", "Eletrica", "Função do Painel")
        obj.Funcao = ["QDC (Distribuição)", "CCM (Motores)", "CCA (Automação)", "Medidores"]
        obj.Funcao = str(panel_type)
        
        obj.addProperty("App::PropertyLink", "AlimentadoPor", "Hierarquia", "Quadro que alimenta este quadro")
        
        # Gestao de Fluxo Industrial (Entrada/Saida)
        group = "Fluxo Industrial"
        obj.addProperty("App::PropertyStringList", "EntradaForca", group, "Cabos de Força (Entrada)")
        obj.addProperty("App::PropertyStringList", "EntradaComando", group, "Sinais/Rede (Entrada)")
        obj.addProperty("App::PropertyStringList", "SaidaForca", group, "Alimentação de Cargas (Saída)")
        obj.addProperty("App::PropertyStringList", "SaidaComando", group, "Sinais de Controle (Saída)")
        
        obj.addProperty("App::PropertyFloat", "PotenciaAcumulada", "Eletrica", "Soma das cargas (VA)")
        obj.PotenciaAcumulada = 0.0
        
        # Protecoes Adicionais
        obj.addProperty("App::PropertyBool", "PossuiDR", "Proteção", "Se possui IDR")
        obj.addProperty("App::PropertyBool", "PossuiDPS", "Proteção", "Se possui DPS")
        
        if not hasattr(obj, "TipoBIM"):
            obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo de componente")
        obj.TipoBIM = "Quadro"
        
        FreeCAD.ActiveDocument.recompute()
        return obj

    @staticmethod
    def recalculate_hierarchy():
        """Soma as cargas de todos os componentes vinculados aos quadros"""
        doc = FreeCAD.ActiveDocument
        
        # 1. Resetar potencias dos quadros
        panels = [o for o in doc.Objects if hasattr(o, "TipoBIM") and o.TipoBIM == "Quadro"]
        for p in panels:
            p.PotenciaAcumulada = 0.0
            
        # 2. Somar cargas terminais vinculadas a cada quadro
        for obj in doc.Objects:
            if hasattr(obj, "Circuito") and hasattr(obj, "Potencia") and hasattr(obj, "QuadroVinculado"):
                if obj.QuadroVinculado:
                    obj.QuadroVinculado.PotenciaAcumulada += float(obj.Potencia)
                    
        # 3. Propagar cargas na hierarquia (sub-quadros para quadros pais)
        # Fazemos varias passagens para garantir que a carga suba todos os níveis
        for _ in range(3):
            for p in panels:
                if p.AlimentadoPor:
                    p.AlimentadoPor.PotenciaAcumulada += p.PotenciaAcumulada
                    
        FreeCAD.Console.PrintMessage("Hierarquia de quadros recalculada!\n")
