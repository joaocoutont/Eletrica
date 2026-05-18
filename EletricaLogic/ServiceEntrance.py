# Assistente de Padrao de Entrada - Concessionarias Brasil
import FreeCAD
import Part
import os
from EletricaLogic.i18n import tr

class ServiceEntranceProxy:
    def __init__(self, obj):
        obj.Proxy = self
        self.init_properties(obj)

    def init_properties(self, obj):
        # Propriedades de Dados da Concessionária
        if not hasattr(obj, "Concessionaria"):
            obj.addProperty("App::PropertyEnumeration", "Concessionaria", "Norma", "Concessionária de Energia")
            obj.Concessionaria = ["Cemig", "Enel", "CPFL", "Energisa", "Neoenergia", "Copel", "Equatorial"]
        
        if not hasattr(obj, "CargaInstalada"):
            obj.addProperty("App::PropertyFloat", "CargaInstalada", "Elétrica", "Carga total instalada (kW)")
            obj.CargaInstalada = 10.0

        if not hasattr(obj, "TipoPoste"):
            obj.addProperty("App::PropertyEnumeration", "TipoPoste", "Geometria", "Tipo de poste de entrada")
            obj.TipoPoste = ["Concreto DT (Quadrado)", "Concreto SC (Circular)", "Ferro Galvanizado"]
            
        if not hasattr(obj, "AlturaPoste"):
            obj.addProperty("App::PropertyFloat", "AlturaPoste", "Geometria", "Altura visível do poste (m)")
            obj.AlturaPoste = 7.0

        # Propriedades calculadas/automáticas
        group_norma = "Resultado da Norma"
        if not hasattr(obj, "Categoria"):
            obj.addProperty("App::PropertyString", "Categoria", group_norma)
        if not hasattr(obj, "DisjuntorGeral"):
            obj.addProperty("App::PropertyString", "DisjuntorGeral", group_norma)
        if not hasattr(obj, "CaboEntrada"):
            obj.addProperty("App::PropertyString", "CaboEntrada", group_norma)
        if not hasattr(obj, "CaixaMedicao"):
            obj.addProperty("App::PropertyString", "CaixaMedicao", group_norma)

        if not hasattr(obj, "TipoBIM"):
            obj.addProperty("App::PropertyString", "TipoBIM", "BIM")
        obj.TipoBIM = "EntradaServico"

    def execute(self, obj):
        """Gera a geometria paramétrica do padrão de entrada."""
        # 1. Obter dados da norma
        rec = ServiceEntranceWizard.recommend_entrance(obj.Concessionaria, obj.CargaInstalada)
        if rec:
            obj.Categoria = rec["fase"]
            obj.DisjuntorGeral = rec["disjuntor"]
            obj.CaboEntrada = rec["cabo"]
            obj.CaixaMedicao = rec["caixa"]

        # 2. Construir Geometria
        shapes = []
        
        # Poste
        h = obj.AlturaPoste * 1000 # mm
        if "Circular" in obj.TipoPoste:
            post = Part.makeCylinder(100, h) # Raio 100mm
        elif "Ferro" in obj.TipoPoste:
            post = Part.makeCylinder(40, h) # Cano de ferro ~3 polegadas
        else: # Quadrado DT
            # Poste DT tem seção variável, mas faremos fixo para simplificar
            post = Part.makeBox(150, 150, h)
            post = post.translate(FreeCAD.Vector(-75, -75, 0))
        shapes.append(post)

        # Caixa de Medição (Posicionada a 1.6m de altura)
        box_h = 400
        box_w = 300
        box_d = 200
        box = Part.makeBox(box_w, box_d, box_h)
        box = box.translate(FreeCAD.Vector(-box_w/2, -box_d/2 - 100, 1500)) # 1.5m de altura
        shapes.append(box)

        # Haste de Aterramento (Simbólica)
        rod = Part.makeCylinder(10, 2400)
        rod = rod.translate(FreeCAD.Vector(300, 0, -2300)) # 2.4m enterrada
        shapes.append(rod)

        # Ramal de Entrada (Cano do poste para a caixa)
        conduit = Part.makeCylinder(25, 1000)
        conduit.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
        conduit.translate(FreeCAD.Vector(0, -150, 1700))
        # shapes.append(conduit) # Opcional

        obj.Shape = Part.makeCompound(shapes)

class ServiceEntranceViewProvider:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Icons", "ServiceEntrance.svg")
        if os.path.exists(icon_path):
            return icon_path
        return ""

    def getDefaultDisplayMode(self):
        return "Shaded"

class ServiceEntranceWizard:
    @staticmethod
    def get_utilities_data():
        """Dados baseados nas principais concessionárias brasileiras"""
        return {
            "Cemig": {
                "norma": "ND-5.1",
                "Categorias": [
                    {"max_kw": 15, "fase": "Monofasico", "disjuntor": "40A", "cabo": "10mm2", "caixa": "CM-1"},
                    {"max_kw": 25, "fase": "Bifasico",   "disjuntor": "50A", "cabo": "16mm2", "caixa": "CM-2"},
                    {"max_kw": 75, "fase": "Trifasico",  "disjuntor": "100A","cabo": "35mm2", "caixa": "CM-3"}
                ]
            },
            "Enel": {
                "norma": "NTC-901001",
                "Categorias": [
                    {"max_kw": 10, "fase": "Monofasico", "disjuntor": "40A", "cabo": "10mm2", "caixa": "Tipo E"},
                    {"max_kw": 20, "fase": "Bifasico",   "disjuntor": "50A", "cabo": "16mm2", "caixa": "Tipo H"},
                    {"max_kw": 75, "fase": "Trifasico",  "disjuntor": "100A","cabo": "35mm2", "caixa": "Tipo N"}
                ]
            },
            "CPFL": {
                "norma": "GED-13",
                "Categorias": [
                    {"max_kw": 12, "fase": "Monofasico", "disjuntor": "50A", "cabo": "10mm2", "caixa": "Individual"},
                    {"max_kw": 25, "fase": "Bifasico",   "disjuntor": "63A", "cabo": "16mm2", "caixa": "Individual"},
                    {"max_kw": 75, "fase": "Trifasico",  "disjuntor": "100A","cabo": "50mm2", "caixa": "Individual"}
                ]
            },
            "Copel": {
                "norma": "NTC-901100",
                "Categorias": [
                    {"max_kw": 15, "fase": "Monofasico", "disjuntor": "40A", "cabo": "10mm2", "caixa": "Tipo I"},
                    {"max_kw": 25, "fase": "Bifasico",   "disjuntor": "50A", "cabo": "16mm2", "caixa": "Tipo II"},
                    {"max_kw": 75, "fase": "Trifasico",  "disjuntor": "100A","cabo": "35mm2", "caixa": "Tipo III"}
                ]
            }
        }

    @staticmethod
    def recommend_entrance(utility_name, total_kw):
        data = ServiceEntranceWizard.get_utilities_data()
        # Busca direta ou aproximada
        actual_key = "Cemig"
        for key in data:
            if utility_name.lower() in key.lower():
                actual_key = key
                break
            
        categories = data[actual_key]["Categorias"]
        for cat in categories:
            if total_kw <= cat["max_kw"]:
                return cat
        return categories[-1]

    @staticmethod
    def create_entrance_point(utility, kw):
        """Cria o padrão de entrada paramétrico (Chamado pelo Diálogo)"""
        obj = create_service_entrance(f"Padrao_{utility}")
        obj.Concessionaria = utility
        obj.CargaInstalada = kw
        FreeCAD.ActiveDocument.recompute()
        return obj

def create_service_entrance(name="Entrada_Servico"):
    doc = FreeCAD.ActiveDocument
    if not doc:
        doc = FreeCAD.newDocument("Projeto")
        
    obj = doc.addObject("Part::FeaturePython", name)
    ServiceEntranceProxy(obj)
    ServiceEntranceViewProvider(obj.ViewObject)
    doc.recompute()
    return obj
