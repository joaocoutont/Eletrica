import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_ind_v1"

def make_industrial_plan_symbol(device_type="Sensor de Pressão", label="P"):
    """Cria a simbologia 2D de instrumentação conforme ISA-5.1."""
    try:
        r = 50.0
        parts = []
        center = App.Vector(0, 0, 0)
        
        # Símbolo base: Círculo (Instrumento local)
        parts.append(Part.makeCircle(r, center, App.Vector(0, 0, 1)))
        
        # Se for atuador (como válvula), adicionamos um triângulo de cada lado (forma de ampulheta)
        if "Atuador" in device_type or "Válvula" in device_type:
            p1 = App.Vector(-r, -r*0.7, 0)
            p2 = App.Vector(-r, r*0.7, 0)
            p3 = App.Vector(r, -r*0.7, 0)
            p4 = App.Vector(r, r*0.7, 0)
            parts.append(Part.makePolygon([p1, p2, center, p1]))
            parts.append(Part.makePolygon([p3, p4, center, p3]))
        
        # Texto/Letra identificadora será tratada como geometria simples ou via Annotation futuramente
        # Por enquanto, adicionamos uma linha horizontal se for instrumento montado em painel
        # (Não adicionaremos texto Part aqui para evitar dependências de fontes no motor core)
            
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source): return source
    return os.path.join(lib_3d, "Automacao", source)

def load_industrial_family_shape(fname):
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

class ProfessionalBIMIndustrialDevice:
    """Motor Geométrico para Sensores e Atuadores Industriais"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcSensor"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Automação Industrial"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "Automação"
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyEnumeration", "DeviceCategory", e).DeviceCategory = ["Instrumentação/Sensor", "Atuador/Execução", "Interface/HMI"]
        obj.addProperty("App::PropertyEnumeration", "SignalType", e).SignalType = ["4-20 mA", "0-10 V", "Digital (PNP/NPN)", "Modbus RTU", "Profinet/Ethernet"]
        obj.addProperty("App::PropertyString", "ProcessConnection", e).ProcessConnection = "Rosca 1/2 NPT"
        obj.addProperty("App::PropertyString", "SupplyVoltage", e).SupplyVoltage = "24V DC"
        obj.addProperty("App::PropertyString", "IP_Rating", e).IP_Rating = "IP67"
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "Manufacturer", g).Manufacturer = ""
        obj.addProperty("App::PropertyString", "Tag", g).Tag = "FIT-101"
        
    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "Sensor_Generico.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                raw = load_industrial_family_shape(fname)
                if raw:
                    bbox = raw.BoundBox
                    raw.translate(App.Vector(-bbox.Center.x, -bbox.Center.y, -bbox.Center.z))
                    _SHAPE_CACHE[cache_key] = raw.exportBrepToString()
                    final_shape = raw
                else:
                    final_shape = None

            if not final_shape or final_shape.isNull():
                # Fallback: Um cilindro com uma caixa (representando transmissor)
                c = Part.makeCylinder(30, 80)
                b = Part.makeBox(60, 60, 60)
                b.translate(App.Vector(-30, -30, 80))
                final_shape = Part.makeCompound([c, b])

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            
            # Ajuste IFC dinâmico
            if "Atuador" in fp.DeviceCategory:
                fp.IFC_Class = "IfcActuator"
            else:
                fp.IFC_Class = "IfcSensor"
                
        except Exception: pass

    def getSnapPoints(self, obj):
        b = obj.Shape.BoundBox
        return [App.Vector(0,0,0), App.Vector(0,0,b.ZMax)]
