import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}

def make_panel_plan_symbol(width=600, depth=250, panel_type="QDC"):
    """Cria a simbologia 2D de planta para quadros elétricos conforme NBR 5444."""
    try:
        parts = []
        w = width
        d = depth
        
        # Símbolo base: Retângulo com dimensões REAIS do quadro
        p1 = App.Vector(-w/2, 0, 0); p2 = App.Vector(w/2, 0, 0)
        p3 = App.Vector(w/2, d, 0); p4 = App.Vector(-w/2, d, 0)
        rect = Part.makePolygon([p1, p2, p3, p4, p1])
        parts.append(rect)

        if panel_type == "QDC" or "Distribuição" in panel_type:
            # QDC: Metade preenchida (diagonal) ou hachura
            wire_half = Part.makePolygon([p1, p2, p3, p1])
            parts.append(Part.Face(wire_half))
        elif panel_type == "CCM" or "Motor" in panel_type:
            # CCM: Retângulo com um "X" interno
            parts.append(Part.makeLine(p1, p3))
            parts.append(Part.makeLine(p2, p4))
        else:
            # Comando / Geral: Linha central
            parts.append(Part.makeLine(App.Vector(0, 0, 0), App.Vector(0, d, 0)))
            
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source): return source
    return os.path.join(lib_3d, "Quadros", source)

class ProfessionalBIMPanel:
    """Motor Geométrico para Quadros Elétricos Paramétricos"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcElectricDistributionBoard"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Elétrica"
        obj.addProperty("App::PropertyEnumeration", "PanelType", t).PanelType = ["QDC (Distribuição)", "QGBT (Geral)", "CCM (Motores)", "Quadro de Comando"]
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyFloat", "MainAmperage", e).MainAmperage = 100.0
        obj.addProperty("App::PropertyFloat", "SCCR_kA", e).SCCR_kA = 10.0
        obj.addProperty("App::PropertyEnumeration", "Voltage", e).Voltage = ["220/127V", "380/220V", "440V", "24V DC"]
        obj.addProperty("App::PropertyInteger", "MaxCircuits", e).MaxCircuits = 24
        obj.addProperty("App::PropertyString", "IP_Rating", e).IP_Rating = "IP54"
        
        d = "BIM_Dimensoes"
        obj.addProperty("App::PropertyLength", "Width", d).Width = 400.0
        obj.addProperty("App::PropertyLength", "Height", d).Height = 600.0
        obj.addProperty("App::PropertyLength", "Depth", d).Depth = 200.0
        obj.addProperty("App::PropertyEnumeration", "Mounting", d).Mounting = ["Sobrepor", "Embutir", "Autosustentado (Coluna)"]
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "Tag", g).Tag = "QD-01"
        
    def execute(self, fp):
        try:
            # Gera geometria paramétrica baseada nas dimensões (Fallback ou se não houver SourceFile)
            w = fp.Width.Value if hasattr(fp.Width, "Value") else fp.Width
            h = fp.Height.Value if hasattr(fp.Height, "Value") else fp.Height
            d = fp.Depth.Value if hasattr(fp.Depth, "Value") else fp.Depth
            
            box = Part.makeBox(w, d, h)
            box.translate(App.Vector(-w/2, 0, 0)) # Centraliza no eixo X, encosta na parede (Y=0)
            
            # Adiciona uma "moldura" se for de embutir
            if "Embutir" in fp.Mounting:
                frame = Part.makeBox(w + 40, 5, h + 40)
                frame.translate(App.Vector(-(w+40)/2, -5, -20))
                fp.Shape = Part.makeCompound([box, frame])
            else:
                fp.Shape = box
                
            fp.Placement = App.Placement()
            
        except Exception as e:
            App.Console.PrintError(f"Erro no motor BIM (Quadro): {e}\n")

    def getSnapPoints(self, obj):
        w = obj.Width.Value; h = obj.Height.Value; d = obj.Depth.Value
        return [
            App.Vector(0, d, h/2), # Frente centro
            App.Vector(w/2, d/2, h/2), # Direita
            App.Vector(-w/2, d/2, h/2), # Esquerda
            App.Vector(0, d/2, h), # Topo
            App.Vector(0, d/2, 0)  # Base
        ]
