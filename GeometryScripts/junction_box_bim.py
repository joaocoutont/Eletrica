import FreeCAD as App
import Part
import math

class ProfessionalBIMJunctionBox:
    """Motor Geométrico Industrial com Conectores Inteligentes (Estilo Revit MEP)."""
    
    def __init__(self, obj):
        obj.Proxy = self
        self.init_properties(obj)

    def init_properties(self, obj):
        # --- CLASSIFICAÇÃO E TIPO ---
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyEnumeration", "BoxType", t).BoxType = [
            "4x2 PVC (Embutir)", "4x4 PVC (Embutir)", "Octogonal (Laje)", "Chapa Aço (20x20)", "Customizada"
        ]
        
        # --- GEOMETRIA ---
        g = "BIM_3D_Geometria"
        obj.addProperty("App::PropertyLength", "Length", g).Length = 100.0
        obj.addProperty("App::PropertyLength", "Width",  g).Width = 100.0
        obj.addProperty("App::PropertyLength", "Height", g).Height = 50.0
        obj.addProperty("App::PropertyLength", "Thickness", g).Thickness = 2.0
        
        # --- CONECTORES (MEP) ---
        c = "MEP_Conectores"
        obj.addProperty("App::PropertyBool", "ShowConnectors", c).ShowConnectors = True
        obj.addProperty("App::PropertyEnumeration", "NorthPort", c).NorthPort = ["Nenhum", "1/2\"", "3/4\"", "1\"", "1 1/4\""]
        obj.addProperty("App::PropertyEnumeration", "SouthPort", c).SouthPort = ["Nenhum", "1/2\"", "3/4\"", "1\"", "1 1/4\""]
        obj.addProperty("App::PropertyEnumeration", "EastPort",  c).EastPort  = ["Nenhum", "1/2\"", "3/4\"", "1\"", "1 1/4\""]
        obj.addProperty("App::PropertyEnumeration", "WestPort",  c).WestPort  = ["Nenhum", "1/2\"", "3/4\"", "1\"", "1 1/4\""]
        obj.addProperty("App::PropertyEnumeration", "BottomPort", c).BottomPort = ["Nenhum", "1/2\"", "3/4\"", "1\"", "1 1/4\""]
        
        # BIM DATA
        obj.addProperty("App::PropertyString", "Tag", "BIM_Classificacao").Tag = "CX-01"

    def execute(self, fp):
        try:
            l, w, h, t = fp.Length.Value, fp.Width.Value, fp.Height.Value, fp.Thickness.Value
            
            # Ajuste de dimensões por tipo
            if "4x2" in fp.BoxType: l, w, h = 101.0, 51.0, 45.0
            elif "4x4" in fp.BoxType: l, w, h = 101.0, 101.0, 45.0
            elif "Octogonal" in fp.BoxType: l, w, h = 105.0, 105.0, 50.0
            
            # Gerar Corpo da Caixa
            box = Part.makeBox(l, w, h)
            inner = Part.makeBox(l - 2*t, w - 2*t, h - t)
            inner.translate(App.Vector(t, t, t))
            box = box.cut(inner)
            
            # ADICIONAR FUROS DOS CONECTORES (Visualização MEP)
            if fp.ShowConnectors:
                box = self.apply_connectors(fp, box, l, w, h, t)
            
            fp.Shape = box
            
        except Exception as e:
            App.Console.PrintError(f"Erro na Caixa BIM: {str(e)}\n")

    def apply_connectors(self, fp, box, l, w, h, t):
        """Cria os furos ou marcações de conexão nas faces da caixa."""
        connectors = []
        # Centro das faces
        cx, cy, cz = l/2, w/2, h/2
        
        # Dicionário de Portas e suas localizações [Ponto, Eixo de Extrusão, Diâmetro Aproximado]
        ports = {
            "North": [App.Vector(cx, w, cz), App.Vector(0, 1, 0), 20],
            "South": [App.Vector(cx, 0, cz), App.Vector(0, -1, 0), 20],
            "East":  [App.Vector(l, cy, cz), App.Vector(1, 0, 0), 20],
            "West":  [App.Vector(0, cy, cz), App.Vector(-1, 0, 0), 20],
            "Bottom": [App.Vector(cx, cy, 0), App.Vector(0, 0, -1), 20]
        }
        
        for name, data in ports.items():
            prop = getattr(fp, name + "Port")
            if prop != "Nenhum":
                # Desenha o furo (relevo negativo)
                pos, axis, radius = data[0], data[1], 10
                cyl = Part.makeCylinder(radius, t*2, pos - axis*t, axis)
                box = box.cut(cyl)
        
        return box

    def getSnapPoints(self, obj):
        """Fornece pontos magnéticos para o sistema de Snap do FreeCAD (Igual Revit)."""
        l, w, h = obj.Length.Value, obj.Width.Value, obj.Height.Value
        cx, cy, cz = l/2, w/2, h/2
        
        # Retorna os centros das faces como pontos de Snap
        return [
            App.Vector(cx, w, cz), # Norte
            App.Vector(cx, 0, cz), # Sul
            App.Vector(l, cy, cz), # Leste
            App.Vector(0, cy, cz), # Oeste
            App.Vector(cx, cy, 0), # Fundo
            App.Vector(cx, cy, h)  # Topo (Centro da Tampa)
        ]

def create_junction_box():
    import Arch
    doc = App.ActiveDocument or App.newDocument("Projeto_Eletrico")
    obj = doc.addObject("Part::FeaturePython", "Caixa_MEP")
    ProfessionalBIMJunctionBox(obj)
    component = Arch.makeComponent(obj)
    if component:
        component.Label = obj.Label
    # Estética de Condulete PVC
    obj.ViewObject.ShapeColor = (0.85, 0.85, 0.85)
    doc.recompute()
    return obj
