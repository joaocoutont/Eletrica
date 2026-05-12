# Gerenciador de Subestacoes Particulares
import FreeCAD

class SubstationManager:
    @staticmethod
    def dimension_substation(kva, voltage_kv=13.8):
        """Define o tipo de subestacao baseado na potencia (kVA) e tensao de MT"""
        is_34 = voltage_kv > 20
        classe = "36.2 kV" if is_34 else "15 kV"
        
        if kva <= 75:
            return {
                "Tipo": "Aérea (Poste Único)",
                "Estrutura": f"Poste de 11m/600daN - Classe {classe}",
                "Protecao": f"Chave Fusível {classe}",
                "Nota": f"Subestação de Média Tensão ({voltage_kv}kV) em poste único."
            }
        elif kva <= 300:
            return {
                "Tipo": "Aérea (Estrutura H)",
                "Estrutura": f"Dois Postes 11m/600daN - Classe {classe}",
                "Protecao": f"Chave Fusível + Para-raios {classe}",
                "Nota": f"Subestação de Média Tensão ({voltage_kv}kV) em estrutura H."
            }
        else:
            return {
                "Tipo": "Abrigada (Cabine de Alvenaria)",
                "Estrutura": f"Cubículos de MT - Classe {classe}",
                "Protecao": f"Disjuntor de MT com Relé Secundário (50/51)",
                "Nota": f"Subestação Abrigada de Média Tensão ({voltage_kv}kV)."
            }

    @staticmethod
    def create_substation_bim(kva, voltage_kv=13.8):
        """Insere a subestacao no projeto com metadados de MT"""
        data = SubstationManager.dimension_substation(kva, voltage_kv)
        
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("App::FeaturePython", f"Subestacao_MT_{kva}kVA")
        obj.Label = f"SE_MT_{kva}kVA"
        
        # Propriedades BIM de Subestacao MT
        obj.addProperty("App::PropertyFloat", "PotenciaKVA", "Média Tensão").PotenciaKVA = kva
        obj.addProperty("App::PropertyString", "TensaoPrimaria", "Média Tensão").TensaoPrimaria = f"{voltage_kv} kV"
        obj.addProperty("App::PropertyString", "TipoSubestacao", "Engenharia").TipoSubestacao = data["Tipo"]
        obj.addProperty("App::PropertyString", "ProtecaoMT", "Engenharia").ProtecaoMT = data["Protecao"]
        
        FreeCAD.ActiveDocument.recompute()
        return obj
 Broadway
