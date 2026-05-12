# Gerenciador de Subestacoes Particulares
import FreeCAD

class SubstationManager:
    @staticmethod
    def dimension_substation(kva):
        """Define o tipo de subestacao baseado na potencia (kVA)"""
        if kva <= 75:
            return {
                "Tipo": "Aérea (Poste Único)",
                "Estrutura": "Poste de 11m/600daN",
                "Protecao": "Chave Fusível 15kV",
                "Nota": "Padrão simplificado para pequenas cargas."
            }
        elif kva <= 300:
            return {
                "Tipo": "Aérea (Estrutura H)",
                "Estrutura": "Dois Postes 11m/600daN",
                "Protecao": "Chave Fusível + Para-raios",
                "Nota": "Necessário projeto de estrutura reforçada."
            }
        else:
            return {
                "Tipo": "Abrigada (Cabine de Alvenaria)",
                "Estrutura": "Cubículos de Alvenaria ou Blindada",
                "Protecao": "Disjuntor de MT com Relé Secundário",
                "Nota": "Exige projeto de alvenaria e malha de aterramento robusta."
            }

    @staticmethod
    def create_substation_bim(kva, utility="Geral"):
        """Insere a subestacao no projeto com metadados"""
        data = SubstationManager.dimension_substation(kva)
        
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("App::FeaturePython", f"Subestacao_{kva}kVA")
        obj.Label = f"SE_{kva}kVA_{data['Tipo'].split(' ')[0]}"
        
        # Propriedades BIM de Subestacao
        obj.addProperty("App::PropertyFloat", "PotenciaKVA", "Elétrica").PotenciaKVA = kva
        obj.addProperty("App::PropertyString", "TipoSubestacao", "Engenharia").TipoSubestacao = data["Tipo"]
        obj.addProperty("App::PropertyString", "ProtecaoPrimaria", "Engenharia").ProtecaoPrimaria = data["Protecao"]
        obj.addProperty("App::PropertyString", "EstruturaNecessaria", "Civil").EstruturaNecessaria = data["Estrutura"]
        
        FreeCAD.ActiveDocument.recompute()
        return obj
