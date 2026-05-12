# Assistente de Padrao de Entrada - Concessionarias Brasil
import FreeCAD

class ServiceEntranceWizard:
    @staticmethod
    def get_utilities_data():
        """Dados simplificados baseados nas normas tecnicas"""
        return {
            "CEMIG (ND-5.1)": {
                "Categorias": [
                    {"max_kw": 15, "fase": "Monofasico", "disjuntor": "40A", "cabo": "10mm2", "caixa": "CM-1"},
                    {"max_kw": 25, "fase": "Bifasico", "disjuntor": "50A", "cabo": "16mm2", "caixa": "CM-2"},
                    {"max_kw": 75, "fase": "Trifasico", "disjuntor": "100A", "cabo": "35mm2", "caixa": "CM-3"}
                ]
            },
            "ENERGISA (NDU-001)": {
                "Categorias": [
                    {"max_kw": 12, "fase": "Monofasico", "disjuntor": "50A", "cabo": "10mm2", "caixa": "Tipo E"},
                    {"max_kw": 24, "fase": "Bifasico", "disjuntor": "63A", "cabo": "16mm2", "caixa": "Tipo H"},
                    {"max_kw": 75, "fase": "Trifasico", "disjuntor": "100A", "cabo": "50mm2", "caixa": "Tipo N"}
                ]
            },
            "ENEL / CPFL": {
                "Categorias": [
                    {"max_kw": 10, "fase": "Monofasico", "disjuntor": "40A", "cabo": "10mm2", "caixa": "Individual"},
                    {"max_kw": 20, "fase": "Bifasico", "disjuntor": "50A", "cabo": "16mm2", "caixa": "Individual"},
                    {"max_kw": 75, "fase": "Trifasico", "disjuntor": "100A", "cabo": "35mm2", "caixa": "Individual"}
                ]
            }
        }

    @staticmethod
    def recommend_entrance(utility_name, total_kw):
        """Recomenda o padrao de entrada ideal"""
        data = ServiceEntranceWizard.get_utilities_data()
        if utility_name not in data: return None
        
        categories = data[utility_name]["Categorias"]
        recommendation = categories[-1] # Default para o maior se ultrapassar
        
        for cat in categories:
            if total_kw <= cat["max_kw"]:
                recommendation = cat
                break
                
        return recommendation

    @staticmethod
    def create_entrance_point(utility, kw):
        """Cria o ponto de entrada no projeto com os dados da norma"""
        rec = ServiceEntranceWizard.recommend_entrance(utility, kw)
        if not rec: return
        
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("App::FeaturePython", "Padrao_Entrada")
        obj.Label = f"Entrada_{utility.split(' ')[0]}"
        
        # Injetar Propriedades da Norma
        obj.addProperty("App::PropertyString", "Concessionaria", "Norma").Concessionaria = utility
        obj.addProperty("App::PropertyString", "Categoria", "Norma").Categoria = rec["fase"]
        obj.addProperty("App::PropertyString", "DisjuntorEntrada", "Componentes").DisjuntorEntrada = rec["disjuntor"]
        obj.addProperty("App::PropertyString", "CaboEntrada", "Componentes").CaboEntrada = rec["cabo"]
        obj.addProperty("App::PropertyString", "CaixaMedicao", "Componentes").CaixaMedicao = rec["caixa"]
        
        FreeCAD.ActiveDocument.recompute()
        return obj
