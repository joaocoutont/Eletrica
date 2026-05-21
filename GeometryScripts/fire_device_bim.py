import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_fire_v1"

def make_fire_plan_symbol(device_type="Detector de Fumaça"):
    """Cria a simbologia 2D de incêndio conforme NBR 17240 / NBR 5444."""
    try:
        parts = []
        r = 50.0
        center = App.Vector(0, 0, 0)
        
        if "Fumaça" in device_type or "Detector" in device_type:
            # Detector: Círculo com um ponto central ou cruz
            parts.append(Part.makeCircle(r, center, App.Vector(0, 0, 1)))
            parts.append(Part.makeCircle(r*0.1, center, App.Vector(0, 0, 1)))
            if "Termovelocimétrico" in device_type or "Calor" in device_type:
                # Detector de calor: Adiciona um traço diagonal
                parts.append(Part.makeLine(App.Vector(-r, 0, 0), App.Vector(r, 0, 0)))

        elif "Acionador" in device_type or "Manual" in device_type:
            # Acionador Manual: Quadrado com um círculo interno
            p1 = App.Vector(-r, -r, 0); p2 = App.Vector(r, -r, 0)
            p3 = App.Vector(r, r, 0); p4 = App.Vector(-r, r, 0)
            parts.append(Part.makePolygon([p1, p2, p3, p4, p1]))
            parts.append(Part.makeCircle(r*0.6, center, App.Vector(0, 0, 1)))

        elif "Sirene" in device_type or "Alarme" in device_type:
            # Sirene: Triângulo equilátero (como alto-falante)
            p1 = App.Vector(-r, -r*0.8, 0); p2 = App.Vector(r, -r*0.8, 0)
            p3 = App.Vector(0, r*0.8, 0)
            parts.append(Part.makePolygon([p1, p2, p3, p1]))
            if "Visual" in device_type:
                # Se tiver flash, adiciona raios de luz
                for a in [45, 90, 135]:
                    rad = math.radians(a)
                    parts.append(Part.makeLine(App.Vector(0, r*0.8, 0), App.Vector(r*math.cos(rad), r*1.5*math.sin(rad), 0)))
            
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source): return source
    return os.path.join(lib_3d, "Incendio", source)

def load_fire_family_shape(fname):
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

class ProfessionalBIMFireDevice:
    """Motor Geométrico para Dispositivos de Detecção de Incêndio"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcFireSuppressionTerminal"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Sistemas de Incêndio"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "Incêndio"
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyEnumeration", "DeviceType", e).DeviceType = [
            "Detector de Fumaça Óptico", "Detector de Calor", "Detector Termovelocimétrico",
            "Acionador Manual", "Sirene Audiovisual", "Sinalizador Visual"
        ]
        obj.addProperty("App::PropertyEnumeration", "Protocol", e).Protocol = ["Endereçável", "Convencional"]
        obj.addProperty("App::PropertyInteger", "LoopAddress", e).LoopAddress = 1
        obj.addProperty("App::PropertyString", "CentralPanel", e).CentralPanel = "Central Incêndio 01"
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "Mounting", g).Mounting = ["Teto", "Parede", "Embutir"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "Tag", g).Tag = "DET-001"
        
    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "Fire_Detector_Generic.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                raw = load_fire_family_shape(fname)
                if raw:
                    bbox = raw.BoundBox
                    raw.translate(App.Vector(-bbox.Center.x, -bbox.Center.y, -bbox.Center.z))
                    _SHAPE_CACHE[cache_key] = raw.exportBrepToString()
                    final_shape = raw
                else:
                    final_shape = None

            if not final_shape or final_shape.isNull():
                # Fallback: Disco pequeno para detectores
                final_shape = Part.makeCylinder(50, 20)

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            
            # Ajuste IFC e Tag
            if "Detector" in fp.DeviceType:
                fp.IFC_Class = "IfcSensor"
                fp.Tag = f"DET-{fp.LoopAddress:03d}"
            elif "Acionador" in fp.DeviceType:
                fp.IFC_Class = "IfcAlarm"
                fp.Tag = f"ACI-{fp.LoopAddress:03d}"
            else:
                fp.IFC_Class = "IfcAlarm"
                fp.Tag = f"SIR-{fp.LoopAddress:03d}"
                
        except Exception: pass

    def getSnapPoints(self, obj):
        return [App.Vector(0,0,0)]
