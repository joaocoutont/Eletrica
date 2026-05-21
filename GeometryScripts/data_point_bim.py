import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_data_v1"
_DATA_3D_ARROW_ALIGNMENT_DEG = 180.0

def make_data_plan_symbol(category="Dados", ports=1):
    """Cria a simbologia 2D de planta para pontos de telecom (NBR)."""
    try:
        s = 100.0
        h_tri = s * math.sqrt(3) / 2
        y_offset_base = 20.0
        
        parts = []
        p_base_left = App.Vector(-s / 2, y_offset_base, 0)
        p_base_right = App.Vector(s / 2, y_offset_base, 0)
        p_vertex = App.Vector(0, y_offset_base + h_tri, 0)
        p_mid = App.Vector(0, y_offset_base, 0)

        # Base do Telecom: Triângulo equilátero (como tomada, mas com marcação interna)
        triangle = Part.makePolygon([p_base_left, p_base_right, p_vertex, p_base_left])
        parts.append(triangle)

        # Marcação por Categoria
        if category == "Dados (RJ45)":
            # Dados: Uma linha diagonal cortando o triângulo ou letra 'D'
            parts.append(Part.makeLine(p_base_left, p_vertex))
        elif category == "Voz (RJ11)":
            # Voz: Uma linha vertical ou letra 'T'
            parts.append(Part.makeLine(p_mid, p_vertex))
        elif category == "TV (Coaxial)":
            # TV: Um círculo pequeno no centro ou letra 'TV'
            parts.append(Part.makeCircle(s*0.2, App.Vector(0, y_offset_base + h_tri*0.4, 0)))
        elif category == "Fibra Óptica":
            # Fibra: Dois traços internos paralelos
            parts.append(Part.makeLine(App.Vector(-s*0.2, y_offset_base + h_tri*0.2, 0), App.Vector(-s*0.2, y_offset_base + h_tri*0.8, 0)))
            parts.append(Part.makeLine(App.Vector(s*0.2, y_offset_base + h_tri*0.2, 0), App.Vector(s*0.2, y_offset_base + h_tri*0.8, 0)))

        # Se tiver múltiplas portas, adicionamos traços externos
        if ports > 1:
            for i in range(1, ports):
                offset = i * 15.0
                parts.append(Part.makeLine(App.Vector(-s/2 - offset, y_offset_base, 0), App.Vector(-s/2 - offset, y_offset_base + 30, 0)))

        # Linha ligando à parede
        parts.append(Part.makeLine(App.Vector(0, 0, 0), p_mid))
        
        # Linha da parede
        wall_half = s / 1.5
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
    return os.path.join(lib_3d, "Telecom", source)

def load_data_family_shape(fname):
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

def normalize_data_shape(shape):
    if not shape:
        return None
    try:
        bbox = shape.BoundBox
        center = bbox.Center
        shape.translate(App.Vector(-center.x, -center.y, -center.z))
        shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), _DATA_3D_ARROW_ALIGNMENT_DEG)
    except Exception:
        pass
    return shape

class ProfessionalBIMDataPoint:
    """Motor Geométrico para Pontos de Dados e Telecom"""
    def __init__(self, obj):
        obj.Proxy = self
        
        # --- CLASSIFICAÇÃO BIM ---
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcCommunicationsAppliance"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Telecomunicações"
        
        # --- PARÂMETROS TELECOM ---
        tel = "BIM_Telecom"
        obj.addProperty("App::PropertyEnumeration", "Category", tel).Category = [
            "Dados (RJ45)", "Voz (RJ11)", "TV (Coaxial)", "Fibra Óptica", "Multimídia (HDMI/USB)"
        ]
        obj.addProperty("App::PropertyEnumeration", "Standard", tel).Standard = ["Cat5e", "Cat6", "Cat6a", "Cat7", "Fiber SingleMode", "Fiber MultiMode"]
        obj.addProperty("App::PropertyInteger", "PortCount", tel).PortCount = 1
        obj.addProperty("App::PropertyString", "LabelText", tel).LabelText = "TI"
        
        # --- PARÂMETROS DE MODELAGEM ---
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyLength", "MountingHeight", g).MountingHeight = 300.0
        obj.addProperty("App::PropertyLength", "FinalElevation", g).FinalElevation = 300.0
        obj.addProperty("App::PropertyString", "Tag", g).Tag = "DAT-01"

        # --- SIMBOLOGIA 2D / PLOTAGEM ---
        s = "BIM_Simbologia"
        obj.addProperty("App::PropertyEnumeration", "SymbolPlaneMode", s).SymbolPlaneMode = ["Plano de simbologia", "Junto do dispositivo"]
        obj.addProperty("App::PropertyLength", "SymbolFinalElevation", s).SymbolFinalElevation = 0.0

        # --- LIMITES 3D PARA CONECTORES MEP ---
        sn = "BIM_Snap"
        obj.addProperty("App::PropertyFloat", "Snap_XMin", sn).Snap_XMin = -60.0
        obj.addProperty("App::PropertyFloat", "Snap_XMax", sn).Snap_XMax =  60.0
        obj.addProperty("App::PropertyFloat", "Snap_YMin", sn).Snap_YMin =  -8.5
        obj.addProperty("App::PropertyFloat", "Snap_YMax", sn).Snap_YMax =  10.0

    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "Tomada_Dados_RJ45.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                best_s = normalize_data_shape(load_data_family_shape(fname))
                if best_s:
                    _SHAPE_CACHE[cache_key] = best_s.exportBrepToString()
                    final_shape = Part.Shape()
                    final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
                else:
                    final_shape = None

            if not final_shape or final_shape.isNull():
                final_shape = Part.makeBox(120, 5, 80)
                final_shape.translate(App.Vector(-60, -8.5, -40))

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            
            # Tag dinâmica
            cat = fp.Category[0].upper() if fp.Category else "D"
            fp.Tag = f"{cat}-{fp.PortCount:02d}"
            
        except Exception:
            pass

    def getSnapPoints(self, obj):
        b = obj.Shape.BoundBox
        cx = (b.XMax + b.XMin) / 2
        cy = (b.YMax + b.YMin) / 2
        return [App.Vector(cx, b.YMax, 0), App.Vector(cx, b.YMin, 0)]
