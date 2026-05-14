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
        
        # Propriedades de Tensao e Sistema (Conforme sua observação técnica)
        group_v = "Parametros Eletricos"
        obj.addProperty("App::PropertyEnumeration", "TensaoNominal", group_v, "Tensão de operação do barramento")
        obj.TensaoNominal = ["220V", "127V", "380V", "440V", "13.8kV", "34.5kV"]
        obj.TensaoNominal = "220V" # Padrao comum
        
        obj.addProperty("App::PropertyEnumeration", "Sistema", group_v, "Configuração de fases")
        obj.Sistema = ["3F+N (380/220V)", "3F (220V Delta)", "2F+N (220/110V)", "2F (220V)", "1F+N (220V)", "1F+N (127V)"]
        obj.Sistema = "3F+N (380/220V)" # Padrao industrial/residencial comum
        
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
        # Ordenar por nivel de hierarquia para evitar dupla contagem
        # (filhos propagam primeiro, depois os netos, etc.)
        already_propagated = set()
        max_depth = 5  # suporta até 5 niveis de sub-quadros
        for _ in range(max_depth):
            for p in panels:
                if p.AlimentadoPor and p.Name not in already_propagated:
                    p.AlimentadoPor.PotenciaAcumulada += p.PotenciaAcumulada
                    already_propagated.add(p.Name)
                    
        FreeCAD.Console.PrintMessage("Hierarquia de quadros recalculada!\n")
