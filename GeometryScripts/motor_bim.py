import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_motor_v1"

def make_motor_plan_symbol(power_cv=1.0, phases=3):
    """Cria a simbologia 2D para motores elétricos conforme NBR / ISA."""
    try:
        r = 60.0
        parts = []
        center = App.Vector(0, 0, 0)
        
        # Símbolo base: Círculo
        parts.append(Part.makeCircle(r, center, App.Vector(0, 0, 1)))
        
        # O 'M' interno (representado simplificadamente por traços ou deixado para anotação)
        # Vamos desenhar um 'M' estilizado
        m_w = r * 0.6
        m_h = r * 0.6
        p1 = App.Vector(-m_w/2, -m_h/2, 0)
        p2 = App.Vector(-m_w/2, m_h/2, 0)
        p3 = App.Vector(0, 0, 0)
        p4 = App.Vector(m_w/2, m_h/2, 0)
        p5 = App.Vector(m_w/2, -m_h/2, 0)
        parts.append(Part.makePolygon([p1, p2, p3, p4, p5]))

        # Indicativo de Fases
        if phases == 3:
            parts.append(Part.makeLine(App.Vector(r*0.8, r*0.8, 0), App.Vector(r*1.2, r*1.2, 0)))
            parts.append(Part.makeLine(App.Vector(r*0.9, r*0.7, 0), App.Vector(r*1.3, r*1.1, 0)))
            parts.append(Part.makeLine(App.Vector(r*0.7, r*0.9, 0), App.Vector(r*1.1, r*1.3, 0)))
            
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source): return source
    return os.path.join(lib_3d, "Maquinas", "Motores", source)

def load_motor_family_shape(fname):
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
                if o.Shape.Volume > 10.0:
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

class ProfessionalBIMMotor:
    """Motor Geométrico para Motores Industriais (WEG W22 e similares)"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcElectricMotor"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Elétrica / Mecânica"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "Motor Elétrico"
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyFloat", "Power_cv", e).Power_cv = 1.0
        obj.addProperty("App::PropertyFloat", "Power_kW", e).Power_kW = 0.75
        obj.addProperty("App::PropertyInteger", "Poles", e).Poles = 4
        obj.addProperty("App::PropertyEnumeration", "Voltage", e).Voltage = ["220/380/440V", "380/660V", "220V", "440V"]
        obj.addProperty("App::PropertyFloat", "Efficiency", e).Efficiency = 85.0
        obj.addProperty("App::PropertyFloat", "PowerFactor", e).PowerFactor = 0.80
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyString", "Frame", g).Frame = "80"
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "Manufacturer", g).Manufacturer = "WEG"
        obj.addProperty("App::PropertyString", "Tag", g).Tag = "M-01"
        
    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or f"Motor_W22_{fp.Frame}.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                raw = load_motor_family_shape(fname)
                if raw:
                    bbox = raw.BoundBox
                    # Centraliza na base e no eixo da árvore (aproximado)
                    raw.translate(App.Vector(-bbox.Center.x, -bbox.Center.y, -bbox.XMin))
                    _SHAPE_CACHE[cache_key] = raw.exportBrepToString()
                    final_shape = raw
                else:
                    final_shape = None

            if not final_shape or final_shape.isNull():
                # Fallback: Cilindro deitado com uma base retangular
                body = Part.makeCylinder(80, 250)
                body.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
                base = Part.makeBox(150, 150, 20)
                base.translate(App.Vector(20, -75, -20))
                final_shape = Part.makeCompound([body, base])

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            
        except Exception: pass

    def getSnapPoints(self, obj):
        # Snap na caixa de ligação (geralmente topo/lado)
        b = obj.Shape.BoundBox
        return [App.Vector(b.Center.x, b.Center.y, b.ZMax)]
