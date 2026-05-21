import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_special_v1"
_SOCKET_3D_ARROW_ALIGNMENT_DEG = 180.0

def make_special_socket_plan_symbol(height_type, modules="1 Módulo", amperage="20A"):
    """Cria a simbologia 2D de TUE (Tomada preenchida) conforme NBR 5444."""
    try:
        s = 150.0
        h_tri = s * math.sqrt(3) / 2
        y_offset_base = 40.0
        count = 1 # TUE geralmente é unitária, mas mantemos lógica para flexibilidade
        spacing_y = h_tri + 15.0
        
        parts = []

        for idx in range(count):
            cx = 0.0
            y_offset = y_offset_base + (idx * spacing_y)
            
            p_base_left = App.Vector(cx - s / 2, y_offset, 0)
            p_base_right = App.Vector(cx + s / 2, y_offset, 0)
            p_vertex = App.Vector(cx, y_offset + h_tri, 0)
            p_mid = App.Vector(cx, y_offset, 0)

            # Símbolo TUE (Tomada de Uso Especial) é um triângulo PREENCHIDO (Face)
            wire = Part.makePolygon([p_base_left, p_base_right, p_vertex, p_base_left])
            
            if "Baixa" in height_type:
                # Tomada Baixa TUE: Metade preenchida ou preenchimento com hachura? 
                # NBR 5444: Baixa = Contorno, Média = Meio cheia, Alta = Toda cheia.
                # Para TUE ser distinta, usaremos preenchimento total ou parcial conforme altura.
                parts.append(wire)
            elif "Média" in height_type or "Media" in height_type:
                # Média: Metade preenchida
                wire_left = Part.makePolygon([p_base_left, p_mid, p_vertex, p_base_left])
                parts.append(Part.Face(wire_left))
                parts.append(wire)
            else:
                # Alta: Toda preenchida
                parts.append(Part.Face(wire))

            if idx == 0:
                parts.append(Part.makeLine(App.Vector(0, 0, 0), p_mid))
            else:
                prev_vertex = App.Vector(cx, y_offset_base + ((idx - 1) * spacing_y) + h_tri, 0)
                parts.append(Part.makeLine(prev_vertex, p_mid))

        wall_half = s / 2
        parts.append(Part.makeLine(App.Vector(-wall_half, 0, 0), App.Vector(wall_half, 0, 0)))
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source):
        return source
    if os.sep in source:
        return os.path.join(lib_3d, source)
    return os.path.join(lib_3d, "Tomadas", source)

def load_special_socket_family_shape(fname):
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

def normalize_special_socket_shape(shape):
    if not shape: return None
    try:
        bbox = shape.BoundBox
        center = bbox.Center
        shape.translate(App.Vector(-center.x, -center.y, -center.z))
        shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), _SOCKET_3D_ARROW_ALIGNMENT_DEG)
    except Exception: pass
    return shape

class ProfessionalBIMSpecialSocket:
    """Motor Geométrico para Tomadas de Uso Especial (TUE)"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcFlowTerminal"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Elétrica"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "Tomada Especial"
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyString", "EquipmentType", e).EquipmentType = "Genérico"
        obj.addProperty("App::PropertyString", "CircuitNumber", e).CircuitNumber = "C-01"
        obj.addProperty("App::PropertyEnumeration", "Voltage", e).Voltage = ["127V", "220V", "380V"]
        obj.addProperty("App::PropertyFloat", "Power", e).Power = 1000.0
        obj.addProperty("App::PropertyFloat", "ApparentPowerVA", e).ApparentPowerVA = 1000.0
        obj.addProperty("App::PropertyFloat", "ActivePowerW", e).ActivePowerW = 1000.0
        obj.addProperty("App::PropertyFloat", "PowerFactor", e).PowerFactor = 1.0
        obj.addProperty("App::PropertyString", "LoadClassification", e).LoadClassification = "TUE"
        obj.addProperty("App::PropertyString", "PanelBoard", e).PanelBoard = ""
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "Amperage", g).Amperage = ["20A", "10A"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyLength", "MountingHeight", g).MountingHeight = 1100.0
        
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
            fname = getattr(fp, "SourceFile", "") or "Tomada_Simples_20A.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                final_shape = normalize_special_socket_shape(load_special_socket_family_shape(fname))
                if final_shape:
                    _SHAPE_CACHE[cache_key] = final_shape.exportBrepToString()

            if not final_shape or final_shape.isNull():
                final_shape = Part.makeBox(120, 5, 80)
                final_shape.translate(App.Vector(-60, -8.5, -40))

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            
            # Tag baseada no equipamento
            prefix = "TUE"
            fp.Tag = f"{prefix}-{getattr(fp, 'EquipmentType', 'GEN')}"
            
        except Exception: pass

    def getSnapPoints(self, obj):
        b = obj.Shape.BoundBox
        cx = (b.XMax + b.XMin) / 2
        cy = (b.YMax + b.YMin) / 2
        z_mid = (b.ZMax + b.ZMin) / 2
        return [App.Vector(cx, b.YMax, z_mid), App.Vector(cx, b.YMin, z_mid)]
