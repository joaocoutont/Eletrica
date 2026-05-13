# Gerenciador de Subestacoes Particulares (NBR 14039 / ABNT)
import FreeCAD

class InstrumentationManager:
    """Dimensionamento de TC (Transformador de Corrente) e TP (Potencial)"""
    
    @staticmethod
    def dimension_tc(nominal_current):
        """Sugere TC baseado na corrente nominal"""
        ratios = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 400, 500]
        chosen = next((r for r in ratios if r >= nominal_current * 1.2), ratios[-1])
        return {
            "ratio": f"{chosen}/5A",
            "class": "0.6 C20" if chosen < 100 else "0.3 C50",
            "burden": "12.5 VA"
        }

    @staticmethod
    def dimension_tp(primary_v):
        """Sugere TP baseado na tensão primária"""
        v_map = {13.8: "13800/115V", 23.1: "23100/115V", 34.5: "34500/115V"}
        ratio = v_map.get(primary_v, "13800/115V")
        return {
            "ratio": ratio,
            "class": "0.3 P25",
            "burden": "25 VA"
        }

# Tensões nominais de distribuição no Brasil
VOLTAGE_CLASSES = {
    13.8: "15 kV",
    23.1: "24.2 kV",
    34.5: "36.2 kV",
    69.0: "72.5 kV",
}

class SubstationManager:
    @staticmethod
    def dimension_substation(kva, voltage_kv=13.8):
        """Define o tipo de subestação baseado na potência (kVA) e tensão de MT."""
        classe = VOLTAGE_CLASSES.get(voltage_kv, "15 kV")
        is_rural = voltage_kv >= 34.5

        if kva <= 75:
            return {
                "Tipo": "Aérea Poste Único",
                "kVA": kva,
                "Tensao_MT": f"{voltage_kv} kV",
                "Classe": classe,
                "Estrutura": f"Poste CP-11/600 + Transformador {kva}kVA",
                "Protecao_MT": f"Chave Fusível tipo K {classe}",
                "Transformador": f"TR Monofásico {kva}kVA {voltage_kv}/{0.22}kV",
                "Para_Raios": f"Para-raios de Óxido de Zinco {classe}",
                "Nota": "Subestação aérea padrão concessionária."
            }
        elif kva <= 300:
            return {
                "Tipo": "Aérea Estrutura H",
                "kVA": kva,
                "Tensao_MT": f"{voltage_kv} kV",
                "Classe": classe,
                "Estrutura": f"2x Postes CP-11/600 - Estrutura H",
                "Protecao_MT": f"Chave Fusível {classe} + Para-raios ZnO",
                "Transformador": f"TR Trifásico {kva}kVA {voltage_kv}/0.38kV",
                "Para_Raios": f"3x Para-raios ZnO {classe}",
                "Nota": "Subestação aérea H - mais de 1 transformador possível."
            }
        elif kva <= 1000:
            return {
                "Tipo": "Cabine Secundária Pré-Fabricada (CSP)",
                "kVA": kva,
                "Tensao_MT": f"{voltage_kv} kV",
                "Classe": classe,
                "Estrutura": "Cabine Pré-Fabricada GIS ou Metal Clad",
                "Protecao_MT": f"Chave Seccionadora + Disjuntor MT {classe}",
                "Transformador": f"TR Trifásico {kva}kVA ONAN/ONAF {voltage_kv}/0.38kV",
                "Para_Raios": f"Para-raios ZnO embutido no transformador",
                "Nota": "Cabine pré-fabricada compacta — ideal para urbano."
            }
        else:
            return {
                "Tipo": "Subestação Abrigada (Alvenaria/Metálica)",
                "kVA": kva,
                "Tensao_MT": f"{voltage_kv} kV",
                "Classe": classe,
                "Estrutura": "Sala de Média Tensão + Sala de Baixa Tensão",
                "Protecao_MT": f"Cubículos de MT com Disjuntor + Relé 50/51 ({classe})",
                "Transformador": f"TR Trifásico {kva}kVA ONAN {voltage_kv}/0.38kV",
                "Para_Raios": f"Para-raios ZnO {classe} na entrada de MT",
                "Nota": "Subestação abrigada com proteção seletiva por relés."
            }

    @staticmethod
    def create_substation_bim(kva, voltage_kv=13.8):
        """Insere a subestação no projeto com metadados de MT."""
        data = SubstationManager.dimension_substation(kva, voltage_kv)

        doc = FreeCAD.ActiveDocument
        if not doc: return None

        obj = doc.addObject("App::FeaturePython", f"SE_MT_{kva}kVA")
        obj.Label = f"SE_{data['Tipo'].split()[0]}_{kva}kVA"

        obj.addProperty("App::PropertyFloat",  "PotenciaKVA",      "MT", "Potência (kVA)").PotenciaKVA = float(kva)
        obj.addProperty("App::PropertyString", "TensaoPrimaria",   "MT", "Tensão MT").TensaoPrimaria = data["Tensao_MT"]
        obj.addProperty("App::PropertyString", "ClasseIsolamento", "MT", "Classe").ClasseIsolamento = data["Classe"]
        obj.addProperty("App::PropertyString", "TipoSubestacao",   "Eng", "Tipo").TipoSubestacao = data["Tipo"]
        obj.addProperty("App::PropertyString", "Transformador",    "Eng", "Transformador").Transformador = data["Transformador"]
        obj.addProperty("App::PropertyString", "ProtecaoMT",       "Eng", "Proteção MT").ProtecaoMT = data["Protecao_MT"]
        obj.addProperty("App::PropertyString", "TipoBIM",          "Eletrica", "Tipo BIM").TipoBIM = "Subestacao"

        FreeCAD.ActiveDocument.recompute()
        return obj
