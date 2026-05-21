import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_light_v1"

def make_light_plan_symbol(mount_type="Teto", lamp_type="LED"):
    """Cria a simbologia 2D de iluminação conforme NBR 5444."""
    try:
        s = 120.0
        r = s / 2
        parts = []
        
        if mount_type == "Parede (Arandela)":
            # Arandela: Círculo encostado na parede com um traço central
            center = App.Vector(0, r + 10.0, 0)
            parts.append(Part.makeCircle(r, center, App.Vector(0, 0, 1)))
            parts.append(Part.makeLine(App.Vector(0, 0, 0), App.Vector(0, 10.0, 0)))
            # Linha da parede
            parts.append(Part.makeLine(App.Vector(-s, 0, 0), App.Vector(s, 0, 0)))
        else:
            # Teto (Ponto de Luz): Círculo com um "X" ou cruz interna
            center = App.Vector(0, 0, 0)
            parts.append(Part.makeCircle(r, center, App.Vector(0, 0, 1)))
            # Cruz interna NBR
            parts.append(Part.makeLine(App.Vector(-r*0.7, -r*0.7, 0), App.Vector(r*0.7, r*0.7, 0)))
            parts.append(Part.makeLine(App.Vector(-r*0.7, r*0.7, 0), App.Vector(r*0.7, -r*0.7, 0)))
            
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source): return source
    return os.path.join(lib_3d, "Iluminacao", source)

def load_light_family_shape(fname):
    full_path_fcstd = _resolve_family_path(fname)
    if not os.path.exists(full_path_fcstd): return None
    previous_doc_name = None
    try:
        if App.ActiveDocument: previous_doc_name = App.ActiveDocument.Name
        tmp_doc = App.openDocument(full_path_fcstd, True, True)
        best_s = None
        max_vol = -1.0
        for o in tmp_doc.Objects:
            temp_s = None
            if hasattr(o, "Shape") and o.Shape and not o.Shape.isNull():
                if o.Shape.Volume > 1.0:
                    temp_s = o.Shape.copy()
                    if hasattr(o, "Placement"): temp_s.transformShape(o.Placement.toMatrix())
            if temp_s and temp_s.Volume > max_vol:
                max_vol = temp_s.Volume
                best_s = temp_s
        return best_s
    finally:
        try: App.closeDocument(tmp_doc.Name)
        except: pass
        if previous_doc_name:
            try: App.setActiveDocument(previous_doc_name)
            except: pass

class ProfessionalBIMLight:
    """Motor Geométrico para Luminárias"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcLightFixture"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Elétrica"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "Luminária"
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyFloat", "Power", e).Power = 10.0
        obj.addProperty("App::PropertyFloat", "LuminousFlux", e).LuminousFlux = 800.0
        obj.addProperty("App::PropertyEnumeration", "LampType", e).LampType = ["LED", "Fluorescente", "Incandescente", "Halógena"]
        obj.addProperty("App::PropertyString", "ColorTemperature", e).ColorTemperature = "3000K"
        obj.addProperty("App::PropertyString", "CircuitNumber", e).CircuitNumber = "C-01"
        obj.addProperty("App::PropertyString", "PanelBoard", e).PanelBoard = ""
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "MountingType", g).MountingType = ["Teto", "Parede (Arandela)", "Embutir", "Piso"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyLength", "MountingHeight", g).MountingHeight = 2800.0
        
    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "Luminaria_LED_Basica.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                raw = load_light_family_shape(fname)
                if raw:
                    bbox = raw.BoundBox
                    raw.translate(App.Vector(-bbox.Center.x, -bbox.Center.y, -bbox.Center.z))
                    _SHAPE_CACHE[cache_key] = raw.exportBrepToString()
                    final_shape = raw
                else:
                    final_shape = None

            if not final_shape or final_shape.isNull():
                final_shape = Part.makeCylinder(100, 20)

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            fp.Tag = f"LUM-{fp.Power:.0f}W"
        except Exception: pass

    def getSnapPoints(self, obj):
        b = obj.Shape.BoundBox
        return [App.Vector(b.Center.x, b.Center.y, b.Center.z)]
