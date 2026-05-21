import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_plc_v1"

def make_plc_plan_symbol(device_type="CPU", di=0, do=0, ai=0, ao=0):
    """Cria a simbologia 2D para CLPs e Módulos (Retângulo com identificação)."""
    try:
        w = 120.0
        h = 100.0
        parts = []
        center = App.Vector(0, 0, 0)
        
        # Símbolo base: Retângulo
        p1 = App.Vector(-w/2, -h/2, 0)
        p2 = App.Vector(w/2, -h/2, 0)
        p3 = App.Vector(w/2, h/2, 0)
        p4 = App.Vector(-w/2, h/2, 0)
        parts.append(Part.makePolygon([p1, p2, p3, p4, p1]))
        
        # Divisão interna para cabeçalho
        parts.append(Part.makeLine(App.Vector(-w/2, h/2 - 25, 0), App.Vector(w/2, h/2 - 25, 0)))
        
        # Marcação simplificada de I/O
        if di > 0 or ai > 0: # Entradas no topo
            parts.append(Part.makeLine(App.Vector(-w/3, h/2, 0), App.Vector(-w/3, h/2 + 10, 0)))
        if do > 0 or ao > 0: # Saídas embaixo
            parts.append(Part.makeLine(App.Vector(-w/3, -h/2, 0), App.Vector(-w/3, -h/2 - 10, 0)))
            
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source): return source
    return os.path.join(lib_3d, "Automacao", "CLP", source)

def load_plc_family_shape(fname):
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

class ProfessionalBIMPLC:
    """Motor Geométrico para CLPs e Módulos de Expansão"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcController"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Automação Industrial"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "CLP"
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyEnumeration", "DeviceType", e).DeviceType = ["CPU Principal", "Módulo DI/DO", "Módulo AI/AO", "Módulo Misto", "Gateway/Comunicação"]
        obj.addProperty("App::PropertyInteger", "DI_Count", e).DI_Count = 8
        obj.addProperty("App::PropertyInteger", "DO_Count", e).DO_Count = 6
        obj.addProperty("App::PropertyInteger", "AI_Count", e).AI_Count = 0
        obj.addProperty("App::PropertyInteger", "AO_Count", e).AO_Count = 0
        obj.addProperty("App::PropertyString", "SupplyVoltage", e).SupplyVoltage = "24V DC"
        obj.addProperty("App::PropertyEnumeration", "Protocol", e).Protocol = ["Profinet", "Modbus TCP", "Ethernet/IP", "EtherCAT", "Nenhum (Expansão)"]
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "Mounting", g).Mounting = ["Trilho DIN", "Painel/Parafuso", "Rack"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "Manufacturer", g).Manufacturer = ""
        obj.addProperty("App::PropertyString", "Model", g).Model = ""
        obj.addProperty("App::PropertyString", "Tag", g).Tag = "PLC-01"
        
    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "PLC_S7_1200_Generic.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                raw = load_plc_family_shape(fname)
                if raw:
                    bbox = raw.BoundBox
                    raw.translate(App.Vector(-bbox.Center.x, -bbox.Center.y, -bbox.Center.z))
                    _SHAPE_CACHE[cache_key] = raw.exportBrepToString()
                    final_shape = raw
                else:
                    final_shape = None

            if not final_shape or final_shape.isNull():
                # Fallback: Bloco retangular de CLP
                final_shape = Part.makeBox(100, 75, 90)
                final_shape.translate(App.Vector(-50, -37.5, -45))

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            
            # Tag dinâmica
            prefix = "PLC" if "CPU" in fp.DeviceType else "MOD"
            fp.Tag = f"{prefix}-{fp.Model or '01'}"
            
        except Exception: pass

    def getSnapPoints(self, obj):
        b = obj.Shape.BoundBox
        return [App.Vector(0,0,0), App.Vector(0,0,b.ZMax)]
