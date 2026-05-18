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
        panel_options = {
            "QDC": "QDC (Distribuição)",
            "CCM": "CCM (Motores)",
            "CCA": "CCA (Automação)",
            "Medidores": "Medidores",
        }
        obj.Funcao = panel_options.get(str(panel_type), "QDC (Distribuição)")
        
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
    def sync_voltage_from_source(panel_obj):
        """Sincroniza a tensão do quadro baseada na sua fonte de alimentação (Trafo ou Quadro Pai)"""
        if not hasattr(panel_obj, "AlimentadoPor") or not panel_obj.AlimentadoPor:
            return
        
        source = panel_obj.AlimentadoPor
        
        # Se a fonte for uma Subestação (Transformador)
        if hasattr(source, "TipoBIM") and source.TipoBIM == "Subestacao":
            if hasattr(source, "TensaoSecundaria"):
                panel_obj.TensaoNominal = source.TensaoSecundaria
                FreeCAD.Console.PrintMessage(f"Quadro {panel_obj.Label} herdou {source.TensaoSecundaria} da Subestação.\n")
        
        # Se a fonte for outro Quadro (Cascata de QDCs)
        elif hasattr(source, "TipoBIM") and source.TipoBIM == "Quadro":
            if hasattr(source, "TensaoNominal"):
                panel_obj.TensaoNominal = source.TensaoNominal
                FreeCAD.Console.PrintMessage(f"Quadro {panel_obj.Label} herdou {source.TensaoNominal} do Quadro Pai {source.Label}.\n")

        FreeCAD.ActiveDocument.recompute()

    @staticmethod
    def recalculate_hierarchy():
        """
        Soma as cargas de todos os componentes vinculados aos quadros de forma hierárquica.
        Garante que a carga de um sub-quadro seja propagada para todos os seus alimentadores.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        panels = [o for o in doc.Objects if hasattr(o, "TipoBIM") and o.TipoBIM == "Quadro"]
        
        # 1. Resetar potencias acumuladas (limpa cálculos anteriores)
        for p in panels:
            p.PotenciaAcumulada = 0.0
            
        # 2. Primeira Passagem: Somar apenas cargas terminais (objetos vinculados diretamente)
        terminal_loads = {} # {PanelName: total_terminal_power}
        for obj in doc.Objects:
            if hasattr(obj, "Potencia") and hasattr(obj, "QuadroVinculado") and obj.QuadroVinculado:
                p_name = obj.QuadroVinculado.Name
                terminal_loads[p_name] = terminal_loads.get(p_name, 0.0) + float(obj.Potencia)
        
        # Aplicar cargas terminais iniciais
        for p in panels:
            p.PotenciaAcumulada = terminal_loads.get(p.Name, 0.0)
                    
        # 3. Segunda Passagem: Propagação Ascendente
        # Para cada quadro, pegamos sua carga terminal e subimos a hierarquia adicionando aos pais
        for p in panels:
            val_to_propagate = terminal_loads.get(p.Name, 0.0)
            if val_to_propagate == 0: continue
            
            parent = getattr(p, "AlimentadoPor", None)
            visited = {p.Name} # Proteção contra loops infinitos (circularidade)
            
            while parent and parent.Name not in visited:
                if hasattr(parent, "PotenciaAcumulada"):
                    parent.PotenciaAcumulada += val_to_propagate
                    visited.add(parent.Name)
                    parent = getattr(parent, "AlimentadoPor", None)
                else:
                    break
                    
        FreeCAD.Console.PrintMessage(f"Hierarquia de {len(panels)} quadros recalculada com sucesso.\n")
