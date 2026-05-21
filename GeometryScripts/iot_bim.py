import FreeCAD as App
import Part
import math
import os

_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_iot_v1"
_IOT_3D_ARROW_ALIGNMENT_DEG = 180.0

def _float_value(value, default=0.0):
    try:
        if hasattr(value, "Value"):
            return float(value.Value)
        return float(value)
    except Exception:
        return default

def make_iot_plan_symbol(device_type="Sensor", protocol="Wi-Fi"):
    """Cria a simbologia 2D de planta para dispositivos IoT."""
    try:
        s = 100.0
        r = s / 2
        y_offset_base = 20.0
        
        parts = []
        center_y = y_offset_base + r
        center = App.Vector(0, center_y, 0)
        
        # Forma base: Losango (Diamante) para diferenciar de tomadas(triângulo) e interruptores(círculo)
        p1 = App.Vector(0, y_offset_base, 0)         # Sul
        p2 = App.Vector(r, center_y, 0)              # Leste
        p3 = App.Vector(0, y_offset_base + 2*r, 0)   # Norte
        p4 = App.Vector(-r, center_y, 0)             # Oeste
        
        diamond = Part.makePolygon([p1, p2, p3, p4, p1])
        parts.append(diamond)

        # Se for Hub/Gateway, adicionamos um quadrado interno
        if "Hub" in device_type or "Gateway" in device_type:
            hr = r * 0.5
            p1_h = App.Vector(-hr, center_y - hr, 0)
            p2_h = App.Vector(hr, center_y - hr, 0)
            p3_h = App.Vector(hr, center_y + hr, 0)
            p4_h = App.Vector(-hr, center_y + hr, 0)
            parts.append(Part.makePolygon([p1_h, p2_h, p3_h, p4_h, p1_h]))
        
        # Se for Sensor, um círculo interno
        elif "Sensor" in device_type:
            parts.append(Part.makeCircle(r * 0.4, center, App.Vector(0, 0, 1)))

        # Se for Wi-Fi ou Wireless genérico, tenta desenhar um "sinal" no topo
        if protocol in ["Wi-Fi", "Zigbee", "Z-Wave", "Matter"]:
            arc1 = Part.makeCircle(r*1.2, center, App.Vector(0, 0, 1), 60, 120)
            arc2 = Part.makeCircle(r*1.6, center, App.Vector(0, 0, 1), 70, 110)
            parts.append(arc1)
            parts.append(arc2)

        # Linha ligando à parede (se for de parede)
        parts.append(Part.makeLine(App.Vector(0, 0, 0), p1))
        
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
    return os.path.join(lib_3d, "IoT", source)

def load_iot_family_shape(fname):
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

def normalize_iot_shape(shape):
    if not shape:
        return None
    try:
        if shape.isNull():
            return None
    except Exception:
        pass
    
    try:
        bbox = shape.BoundBox
        center = bbox.Center
        shape.translate(App.Vector(-center.x, -center.y, -center.z))
        shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), _IOT_3D_ARROW_ALIGNMENT_DEG)
    except Exception as e:
        App.Console.PrintError(f"Erro em normalize_iot_shape: {e}\n")
        
    return shape

class ProfessionalBIMIoT:
    """Motor Geométrico para Dispositivos IoT e Smart Home"""
    def __init__(self, obj):
        obj.Proxy = self
        
        # --- CLASSIFICAÇÃO BIM ---
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcCommunicationsAppliance"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Automação"
        
        # --- PARÂMETROS IOT ESPECÍFICOS ---
        iot = "BIM_IoT"
        obj.addProperty("App::PropertyEnumeration", "DeviceType", iot).DeviceType = [
            "Sensor de Presença", "Sensor Porta/Janela", "Módulo Relé", 
            "Smart Switch", "Smart Plug", "Hub/Gateway", "Câmera IP", "Outros"
        ]
        obj.addProperty("App::PropertyEnumeration", "Protocol", iot).Protocol = [
            "Wi-Fi", "Zigbee", "Matter", "Z-Wave", "Bluetooth", "Cabo (Ethernet)"
        ]
        obj.addProperty("App::PropertyEnumeration", "PowerSource", iot).PowerSource = [
            "Rede Elétrica", "Bateria/Pilha", "PoE (Power over Ethernet)", "Solar"
        ]
        
        # --- ENGENHARIA ELÉTRICA ---
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyString", "CircuitNumber", e).CircuitNumber = "C-01"
        obj.addProperty("App::PropertyEnumeration", "Voltage", e).Voltage = ["Bivolt (100-240V)", "5V DC", "12V DC", "24V DC", "Bateria"]
        obj.addProperty("App::PropertyFloat", "Power", e).Power = 2.0 # Geralmente baixo consumo
        obj.addProperty("App::PropertyString", "PanelBoard", e).PanelBoard = ""
        obj.addProperty("App::PropertyString", "CircuitObject", e).CircuitObject = ""
        obj.addProperty("App::PropertyString", "SpaceOrSector", e).SpaceOrSector = ""
        
        # --- PARÂMETROS DE MODELAGEM ---
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "MountingType", g).MountingType = ["Parede", "Teto", "Embutir", "Móvel/Mesa"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "Manufacturer", g).Manufacturer = ""
        obj.addProperty("App::PropertyString", "Model", g).Model = ""
        obj.addProperty("App::PropertyString", "ReferenceLevel", g).ReferenceLevel = "Projeto"
        obj.addProperty("App::PropertyString", "ReferenceLevelObject", g).ReferenceLevelObject = ""
        obj.addProperty("App::PropertyLength", "LevelElevation", g).LevelElevation = 0.0
        obj.addProperty("App::PropertyLength", "MountingHeight", g).MountingHeight = 2200.0
        obj.addProperty("App::PropertyLength", "FinalElevation", g).FinalElevation = 2200.0
        obj.addProperty("App::PropertyString", "HostObject", g).HostObject = ""
        obj.addProperty("App::PropertyString", "HostFace", g).HostFace = ""
        obj.addProperty("App::PropertyLength", "SurfaceOffset", g).SurfaceOffset = 0.0
        if not hasattr(obj, "Tag"):
            obj.addProperty("App::PropertyString", "Tag", g).Tag = "IOT-01"

        # --- SIMBOLOGIA 2D / PLOTAGEM ---
        s = "BIM_Simbologia"
        obj.addProperty("App::PropertyEnumeration", "SymbolPlaneMode", s).SymbolPlaneMode = ["Plano de simbologia", "Junto do dispositivo"]
        try:
            obj.SymbolPlaneMode = "Plano de simbologia"
        except Exception:
            pass
        obj.addProperty("App::PropertyString", "SymbolPlaneName", s).SymbolPlaneName = "Plano de Simbologia"
        obj.addProperty("App::PropertyLength", "SymbolPlaneHeight", s).SymbolPlaneHeight = 0.0
        obj.addProperty("App::PropertyLength", "SymbolFinalElevation", s).SymbolFinalElevation = 0.0
        obj.addProperty("App::PropertyFloat", "SymbolZOffset", s).SymbolZOffset = 0.0

        # --- LIMITES 3D PARA CONECTORES MEP ---
        sn = "BIM_Snap"
        obj.addProperty("App::PropertyFloat", "Snap_XMin", sn).Snap_XMin = -40.0
        obj.addProperty("App::PropertyFloat", "Snap_XMax", sn).Snap_XMax =  40.0
        obj.addProperty("App::PropertyFloat", "Snap_YMin", sn).Snap_YMin =  -5.0
        obj.addProperty("App::PropertyFloat", "Snap_YMax", sn).Snap_YMax =  10.0
        obj.addProperty("App::PropertyFloat", "Snap_ZMin", sn).Snap_ZMin = -40.0
        obj.addProperty("App::PropertyFloat", "Snap_ZMax", sn).Snap_ZMax =  40.0

    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            fname = getattr(fp, "SourceFile", "") or "IoT_Generico.FCStd"
            final_shape = None
            
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[cache_key])
                try:
                    center = final_shape.BoundBox.Center
                    if abs(center.x) > 1.0 or abs(center.y) > 1.0:
                        del _SHAPE_CACHE[cache_key]
                        final_shape = None
                except Exception:
                    pass
            
            if not final_shape:
                best_s = normalize_iot_shape(load_iot_family_shape(fname))
                if best_s:
                    brep_data = best_s.exportBrepToString()
                    _SHAPE_CACHE[cache_key] = brep_data
                    final_shape = Part.Shape()
                    final_shape.importBrepFromString(brep_data)
                
                if not final_shape:
                    full_path_fcstd = _resolve_family_path(fname)
                    if os.path.exists(full_path_fcstd):
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
                                elif hasattr(o, "Tip") and o.Tip and not o.Tip.Shape.isNull():
                                    temp_s = o.Tip.Shape.copy()
                                    if hasattr(o, "Placement") and o.Placement:
                                        temp_s.transformShape(o.Placement.toMatrix())
                                if temp_s:
                                    if not best_s or temp_s.Volume > max_vol:
                                        max_vol = temp_s.Volume
                                        best_s = temp_s.copy()
                            if best_s:
                                best_s = normalize_iot_shape(best_s)
                                if best_s:
                                    brep_data = best_s.exportBrepToString()
                                    _SHAPE_CACHE[cache_key] = brep_data
                                    final_shape = Part.Shape()
                                    final_shape.importBrepFromString(brep_data)
                        finally:
                            App.closeDocument(tmp_doc.Name)

            if not final_shape or final_shape.isNull():
                # Fallback: Disco pequeno representando um dispositivo IoT genérico
                final_shape = Part.makeCylinder(40, 15)
                final_shape.translate(App.Vector(0, 0, -7.5))

            if final_shape and not final_shape.isNull():
                try:
                    b = final_shape.BoundBox
                    fp.Snap_XMin = b.XMin; fp.Snap_XMax = b.XMax
                    fp.Snap_YMin = b.YMin; fp.Snap_YMax = b.YMax
                    fp.Snap_ZMin = b.ZMin; fp.Snap_ZMax = b.ZMax
                except Exception:
                    pass

            if final_shape and not final_shape.isNull():
                try:
                    center = final_shape.BoundBox.Center
                    if abs(center.x) > 0.1 or abs(center.y) > 0.1 or abs(center.z) > 0.1:
                        final_shape.translate(App.Vector(-center.x, -center.y, -center.z))
                except Exception as e:
                    pass

            try:
                current_placement = fp.Placement
                base = current_placement.Base
                if (
                    abs(base.x) > 0.001
                    or abs(base.y) > 0.001
                    or abs(base.z) > 0.001
                    or abs(current_placement.Rotation.Angle) > 0.000001
                ):
                    final_shape.transformShape(current_placement.inverse().toMatrix())
            except Exception:
                pass
            fp.Shape = final_shape
            try:
                fp.Placement = App.Placement()
            except Exception:
                pass
            
            # Atualiza a classe IFC baseada no tipo para melhor exportação BIM
            if "Sensor" in fp.DeviceType:
                fp.IFC_Class = "IfcSensor"
            elif "Relé" in fp.DeviceType or "Switch" in fp.DeviceType:
                fp.IFC_Class = "IfcSwitchingDevice"
            else:
                fp.IFC_Class = "IfcCommunicationsAppliance"

            # Tag genérica
            prefix = "IOT"
            if "Sensor" in fp.DeviceType: prefix = "SEN"
            if "Hub" in fp.DeviceType: prefix = "HUB"
            fp.Tag = f"{prefix}-{fp.Protocol[:2].upper()}"
            
        except Exception as e:
            import traceback
            App.Console.PrintError(f"Erro no motor BIM (IoT): {str(e)}\n{traceback.format_exc()}\n")

    def getSnapPoints(self, obj):
        try:
            snap_props = ["Snap_XMin", "Snap_XMax", "Snap_YMin", "Snap_YMax", "Snap_ZMin", "Snap_ZMax"]
            if all(hasattr(obj, p) for p in snap_props):
                xmin, xmax = obj.Snap_XMin, obj.Snap_XMax
                ymin, ymax = obj.Snap_YMin, obj.Snap_YMax
                zmin, zmax = obj.Snap_ZMin, obj.Snap_ZMax
            else:
                b = obj.Shape.BoundBox
                xmin, xmax = b.XMin, b.XMax
                ymin, ymax = b.YMin, b.YMax
                zmin, zmax = b.ZMin, b.ZMax

            cx = (xmax + xmin) / 2
            cy = (ymax + ymin) / 2
            z_mid = (zmax + zmin) / 2

            return [
                App.Vector(cx,   ymax,  z_mid),
                App.Vector(cx,   ymin,  z_mid),
                App.Vector(xmax, cy,    z_mid),
                App.Vector(xmin, cy,    z_mid),
                App.Vector(cx,   cy,    zmin),
            ]
        except Exception:
            return [App.Vector(0, 0, 0)]