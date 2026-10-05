import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_modular_v1"
_MODULAR_3D_ARROW_ALIGNMENT_DEG = 180.0

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source):
        return source
    if os.sep in source:
        return os.path.join(lib_3d, source)
    return os.path.join(lib_3d, "Conjuntos_Modulares", source)

def load_modular_family_shape(fname):
    full_path_fcstd = _resolve_family_path(fname)
    if not os.path.exists(full_path_fcstd):
        return None
    previous_doc_name = None
    try:
        if App.ActiveDocument:
            previous_doc_name = App.ActiveDocument.Name
    except Exception:
        previous_doc_name = None
    tmp_doc = App.openDocument(full_path_fcstd, True, True)
    try:
        best_s = None
        max_vol = -1.0
        for o in tmp_doc.Objects:
            temp_s = None
            if hasattr(o, "Shape") and o.Shape and not o.Shape.isNull():
                if o.Shape.Volume > 1.0:
                    temp_s = o.Shape.copy()
                    if hasattr(o, "Placement") and o.Placement:
                        temp_s.transformShape(o.Placement.toMatrix())
            elif hasattr(o, "Tip") and o.Tip and o.Tip.Shape and not o.Tip.Shape.isNull():
                temp_s = o.Tip.Shape.copy()
                if hasattr(o, "Placement") and o.Placement:
                    temp_s.transformShape(o.Placement.toMatrix())
            
            if temp_s and temp_s.Volume > max_vol:
                max_vol = temp_s.Volume
                best_s = temp_s
        return best_s
    finally:
        try:
            App.closeDocument(tmp_doc.Name)
        finally:
            if previous_doc_name:
                try:
                    App.setActiveDocument(previous_doc_name)
                except Exception:
                    pass

def normalize_modular_shape(shape):
    if not shape: return None
    try:
        bbox = shape.BoundBox
        center = bbox.Center
        shape.translate(App.Vector(-center.x, -center.y, -center.z))
        shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), _MODULAR_3D_ARROW_ALIGNMENT_DEG)
    except Exception: pass
    return shape

class ProfessionalBIMModularSet:
    """Motor Geométrico para Conjuntos Modulares (Tomada + Interruptor, etc.)"""
    def __init__(self, obj):
        obj.Proxy = self
        
        # --- CLASSIFICAÇÃO BIM ---
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcDistributionElement"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Elétrica"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "ModularAssembly"
        obj.addProperty("App::PropertyString", "FamilyCategory", t).FamilyCategory = "Conjunto Modular"
        
        # --- COMPOSIÇÃO ---
        c = "BIM_Composicao"
        obj.addProperty("App::PropertyStringList", "Modules", c).Modules = ["Tomada 10A", "Interruptor Simples"]
        obj.addProperty("App::PropertyString", "Composition", c).Composition = "T1-S1"
        obj.addProperty("App::PropertyInteger", "SocketCount", c).SocketCount = 1
        obj.addProperty("App::PropertyInteger", "SwitchCount", c).SwitchCount = 1
        obj.addProperty("App::PropertyEnumeration", "PlateSize", c).PlateSize = ["4x2", "4x4"]
        
        # --- ENGENHARIA ELÉTRICA (Agregada) ---
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyString", "CircuitNumber", e).CircuitNumber = "C-01/C-02"
        obj.addProperty("App::PropertyString", "PanelBoard", e).PanelBoard = ""
        obj.addProperty("App::PropertyString", "LoadClassification", e).LoadClassification = "Misto"
        
        # --- PARÂMETROS DE MODELAGEM ---
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyLength", "MountingHeight", g).MountingHeight = 1100.0
        
        # --- LIMITES 3D PARA CONECTORES MEP ---
        sn = "BIM_Snap"
        obj.addProperty("App::PropertyFloat", "Snap_XMin", sn).Snap_XMin = -60.0
        obj.addProperty("App::PropertyFloat", "Snap_XMax", sn).Snap_XMax =  60.0
        obj.addProperty("App::PropertyFloat", "Snap_YMin", sn).Snap_YMin =  -8.5
        obj.addProperty("App::PropertyFloat", "Snap_YMax", sn).Snap_YMax =  10.0
        obj.addProperty("App::PropertyFloat", "Snap_ZMin", sn).Snap_ZMin = -40.0
        obj.addProperty("App::PropertyFloat", "Snap_ZMax", sn).Snap_ZMax =  40.0

    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "Conjunto_Modular_Padrao.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                final_shape = normalize_modular_shape(load_modular_family_shape(fname))
                if final_shape:
                    _SHAPE_CACHE[cache_key] = final_shape.exportBrepToString()

            if not final_shape or final_shape.isNull():
                final_shape = Part.makeBox(120, 5, 80)
                final_shape.translate(App.Vector(-60, -8.5, -40))

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            
        except Exception: pass

    def getSnapPoints(self, obj):
        b = obj.Shape.BoundBox
        cx = (b.XMax + b.XMin) / 2
        cy = (b.YMax + b.YMin) / 2
        z_mid = (b.ZMax + b.ZMin) / 2
        return [
            App.Vector(cx, b.YMax, z_mid), 
            App.Vector(cx, b.YMin, z_mid),
            App.Vector(b.XMax, cy, z_mid),
            App.Vector(b.XMin, cy, z_mid)
        ]
