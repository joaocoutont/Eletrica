# Dimensionamento de Partidas de Motores (Padrao WEG)
import FreeCAD

class StarterManager:
    @staticmethod
    def get_weg_components(cv, voltage=380):
        """Simula a selecao de componentes WEG baseada na potencia"""
        # Tabela simplificada de exemplo (seria expandida com o catalogo completo)
        if cv <= 5:
            return {"MPW": "MPW25", "CWM": "CWM9", "CFW": "CFW300", "SSW": "SSW05"}
        elif cv <= 10:
            return {"MPW": "MPW40", "CWM": "CWM18", "CFW": "CFW500", "SSW": "SSW07"}
        elif cv <= 50:
            return {"MPW": "MPW65", "CWM": "CWM50", "CFW": "CFW700", "SSW": "SSW900"}
        else:
            return {"MPW": "Disjuntor Aberto", "CWM": "CWM105", "CFW": "CFW11", "SSW": "SSW900"}

    @staticmethod
    def dimension_starter(obj):
        """Dimensiona a partida para um objeto Motor selecionado"""
        if not hasattr(obj, "Potencia_CV"): return None
        
        cv = obj.Potencia_CV
        method = obj.TipoPartida if hasattr(obj, "TipoPartida") else "Direta"
        weg = StarterManager.get_weg_components(cv)
        
        result = {
            "Metodo": method,
            "Protecao": weg["MPW"],
            "Acionamento": ""
        }
        
        if method == "Direta":
            result["Acionamento"] = weg["CWM"]
        elif method == "Soft-Starter":
            result["Acionamento"] = weg["SSW"]
        elif method == "Inversor de Frequencia":
            result["Acionamento"] = weg["CFW"]
        elif method == "Estrela-Triangulo":
            result["Acionamento"] = f"3x {weg['CWM']} + Temporizador"
            
        # Salvar no objeto para o BOM
        if not hasattr(obj, "KitPartida"):
            obj.addProperty("App::PropertyString", "KitPartida", "Engenharia").KitPartida = str(result)
            
        return result
