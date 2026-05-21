import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_security_v1"

def make_security_plan_symbol(device_type="Câmera Dome", fov_angle=90.0):
    """Cria a simbologia 2D para Câmeras e Segurança."""
    try:
        parts = []
        r = 50.0
        center = App.Vector(0, 0, 0)
        
        if "Câmera" in device_type:
            # Câmera: Triângulo apontando para baixo (direção da visão)
            p_top_left = App.Vector(-r, r, 0)
            p_top_right = App.Vector(r, r, 0)
            p_bottom = App.Vector(0, -r, 0)
            parts.append(Part.makePolygon([p_top_left, p_top_right, p_bottom, p_top_left]))
            
            # Se for Dome, adiciona um semi-círculo no topo
            if "Dome" in device_type:
                parts.append(Part.makeCircle(r, App.Vector(0, r, 0), App.Vector(0, 0, 1), 0, 180))
            # Se for PTZ, adiciona setas cruzadas
            elif "PTZ" in device_type:
                parts.append(Part.makeLine(App.Vector(-r*0.5, 0, 0), App.Vector(r*0.5, 0, 0)))
                parts.append(Part.makeLine(App.Vector(0, -r*0.5, 0), App.Vector(0, r*0.5, 0)))

            # Cone de Visão (Field of View) - Linhas tracejadas/finas no 2D real, aqui simplificado
            rad_half = math.radians(fov_angle / 2.0)
            len_fov = 150.0
            fov_p1 = App.Vector(-len_fov * math.sin(rad_half), -len_fov * math.cos(rad_half), 0)
            fov_p2 = App.Vector(len_fov * math.sin(rad_half), -len_fov * math.cos(rad_half), 0)
            parts.append(Part.makeLine(p_bottom, fov_p1))
            parts.append(Part.makeLine(p_bottom, fov_p2))

        elif "Leitor" in device_type or "Acesso" in device_type:
            # Controle de Acesso: Quadrado com "RFID" ou ícone de cartão
            p1 = App.Vector(-r*0.8, -r, 0); p2 = App.Vector(r*0.8, -r, 0)
            p3 = App.Vector(r*0.8, r, 0); p4 = App.Vector(-r*0.8, r, 0)
            parts.append(Part.makePolygon([p1, p2, p3, p4, p1]))
            # Linha representando ranhura do cartão
            parts.append(Part.makeLine(App.Vector(-r*0.5, 0, 0), App.Vector(r*0.5, 0, 0)))

        elif "Sensor" in device_type or "PIR" in device_type:
            # Sensor de Intrusão PIR
            parts.append(Part.makeCircle(r*0.8, center, App.Vector(0, 0, 1)))
            # "Ondas" de detecção
            parts.append(Part.makeLine(App.Vector(-r, -r, 0), App.Vector(r, r, 0)))
            parts.append(Part.makeLine(App.Vector(-r, r, 0), App.Vector(r, -r, 0)))
            
        return Part.makeCompound(parts)
    except Exception:
        return None

def _resolve_family_path(fname):
    base_path = os.path.dirname(os.path.dirname(__file__))
    lib_3d = os.path.join(base_path, "Library", "3D")
    source = str(fname or "").replace("\\", os.sep).replace("/", os.sep).strip(os.sep)
    if os.path.isabs(source): return source
    return os.path.join(lib_3d, "Seguranca", source)

def load_security_family_shape(fname):
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

class ProfessionalBIMSecurityDevice:
    """Motor Geométrico para Dispositivos de CFTV e Segurança"""
    def __init__(self, obj):
        obj.Proxy = self
        
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcCommunicationsAppliance"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Segurança Eletrônica"
        obj.addProperty("App::PropertyString", "TipoBIM", t).TipoBIM = "CFTV / Acesso"
        
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyEnumeration", "DeviceType", e).DeviceType = [
            "Câmera Dome", "Câmera Bullet", "Câmera PTZ", "Câmera Fisheye 360",
            "Leitor de Acesso (RFID/Biometria)", "Sensor de Intrusão (PIR)", "Catraca/Tornoquete"
        ]
        obj.addProperty("App::PropertyString", "Resolution", e).Resolution = "2 MP (1080p)"
        obj.addProperty("App::PropertyString", "Lens", e).Lens = "2.8mm"
        obj.addProperty("App::PropertyFloat", "FOV_Angle", e).FOV_Angle = 90.0
        obj.addProperty("App::PropertyString", "PowerSupply", e).PowerSupply = "PoE (802.3af)"
        obj.addProperty("App::PropertyString", "Network", e).Network = "IP / RJ45"
        
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "Mounting", g).Mounting = ["Teto", "Parede", "Poste", "Embutir"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "Tag", g).Tag = "CAM-01"
        
    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "Camera_Dome_Generic.FCStd"
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
            else:
                raw = load_security_family_shape(fname)
                if raw:
                    bbox = raw.BoundBox
                    raw.translate(App.Vector(-bbox.Center.x, -bbox.Center.y, -bbox.Center.z))
                    _SHAPE_CACHE[cache_key] = raw.exportBrepToString()
                    final_shape = raw
                else:
                    final_shape = None

            if not final_shape or final_shape.isNull():
                # Fallback
                final_shape = Part.makeSphere(40)
                final_shape.translate(App.Vector(0, 0, -20))

            fp.Shape = final_shape
            fp.Placement = App.Placement()
            
            # Ajuste IFC dinâmico
            if "Sensor" in fp.DeviceType or "Câmera" in fp.DeviceType:
                fp.IFC_Class = "IfcSensor"
            
        except Exception: pass

    def getSnapPoints(self, obj):
        return [App.Vector(0,0,0)]
