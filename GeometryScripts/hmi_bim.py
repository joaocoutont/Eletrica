import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_hmi_v1"

def make_hmi_plan_symbol(screen_size="7\""):
    """Cria a simbologia 2D para IHMs (Retângulo com moldura dupla)."""
    try:
        # Dimensões aproximadas baseadas na polegada (escala 1:1 mm)
        size_val = 7.0
        try: size_val = float(screen_size.replace("\"", ""))
        except: pass
        
        w = size_val * 25.4 * 1.2 # Moldura externa
        h = w * 0.7
        parts = []
        
        # Moldura Externa
        p1 = App.Vector(-w/2, -h/2, 0); p2 = App.Vector(w/2, -h/2, 0)
        p3 = App.Vector(w/2, h/2, 0); p4 = App.Vector(-w/2, h/2, 0)
        parts.append(Part.makePolygon([p1, p2, p3, p4, p1]))
        
        # Área da Tela (Moldura Interna)
        wi = w * 0.85; hi = h * 0.85
        i1 = App.Vector(-wi/2, -hi/2, 0); i2 = App.Vector(wi/2, -hi/2, 0)
        i3 = App.Vector(wi/2, hi/2, 0); i4 = App.Vector(-wi/2, hi/2, 0)
        parts.append(Part.makePolygon([i1, i2, i3, i4, i1]))
        
        # Indicativo de Touch (Círculo pequeno no canto)
        parts.append(Part.makeCircle(h*0.05, App.Vector(wi/2 - 10, -hi/2 + 10, 0)))
            
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source): return source
    return os.path.join(lib_3d, "Automacao", "IHM", source)

def load_hmi_family_shape(fname):
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

class ProfessionalBIMHMI:
    """Motor Geométrico para Interfaces Homem-Máquina (IHM)"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcCommunicationsAppliance"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Automação Industrial"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "IHM"
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyString", "ScreenSize", e).ScreenSize = "7\""
        obj.addProperty("App::PropertyString", "Resolution", e).Resolution = "800x480"
        obj.addProperty("App::PropertyEnumeration", "TouchType", e).TouchType = ["Capacitivo", "Resistivo", "Multitouch"]
        obj.addProperty("App::PropertyString", "SupplyVoltage", e).SupplyVoltage = "24V DC"
        obj.addProperty("App::PropertyStringList", "Protocols", e).Protocol = ["Ethernet", "RS-485", "RS-232"]
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "Mounting", g).Mounting = ["Embutir (Painel)", "VESA 75", "VESA 100", "Braço Articulado"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "Manufacturer", g).Manufacturer = ""
        obj.addProperty("App::PropertyString", "Tag", g).Tag = "HMI-01"
        
    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "HMI_7_Inch_Generic.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                raw = load_hmi_family_shape(fname)
                if raw:
                    bbox = raw.BoundBox
                    raw.translate(App.Vector(-bbox.Center.x, -bbox.Center.y, -bbox.Center.z))
                    _SHAPE_CACHE[cache_key] = raw.exportBrepToString()
                    final_shape = raw
                else:
                    final_shape = None

            if not final_shape or final_shape.isNull():
                # Fallback: Tablet/IHM simples
                final_shape = Part.makeBox(200, 140, 30)
                final_shape.translate(App.Vector(-100, -70, -15))

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            fp.Tag = f"HMI-{fp.ScreenSize.replace('\"','')}"
            
        except Exception: pass

    def getSnapPoints(self, obj):
        b = obj.Shape.BoundBox
        return [App.Vector(0,0,0), App.Vector(0,b.YMin,0)] # Snap atrás (para fiação)
