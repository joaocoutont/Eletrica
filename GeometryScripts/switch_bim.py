import FreeCAD as App
import Part
import math
import os

# Cache global para evitar abrir o arquivo da biblioteca repetidamente (Performance)
_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_switch_v1"
_SWITCH_3D_ARROW_ALIGNMENT_DEG = 180.0

def _float_value(value, default=0.0):
    try:
        if hasattr(value, "Value"):
            return float(value.Value)
        return float(value)
    except Exception:
        return default

def make_switch_plan_symbol(keys="1 Tecla", switch_type="Simples"):
    """Cria a simbologia 2D de planta usada pelo interruptor real e pelo fantasma."""
    try:
        s = 100.0
        r = s / 2
        y_offset_base = 20.0
        
        parts = []
        center = App.Vector(0, y_offset_base + r, 0)
        
        # O interruptor simples na NBR 5444 é um círculo
        circle = Part.makeCircle(r, center, App.Vector(0, 0, 1))
        
        if "Paralelo" in switch_type or "Three" in switch_type:
            # Paralelo: Círculo preenchido no meio ou com subdivisão.
            # Representaremos como um círculo completo com uma linha cortando.
            parts.append(circle)
            parts.append(Part.makeLine(App.Vector(-r, y_offset_base + r, 0), App.Vector(r, y_offset_base + r, 0)))
        elif "Intermediário" in switch_type or "Four" in switch_type:
            # Intermediário: Círculo com um "X" dentro ou cruz.
            parts.append(circle)
            parts.append(Part.makeLine(App.Vector(-r*0.7, y_offset_base + r - r*0.7, 0), App.Vector(r*0.7, y_offset_base + r + r*0.7, 0)))
            parts.append(Part.makeLine(App.Vector(-r*0.7, y_offset_base + r + r*0.7, 0), App.Vector(r*0.7, y_offset_base + r - r*0.7, 0)))
        else:
            # Simples: Apenas o círculo
            parts.append(circle)

        # Se tiver mais de uma tecla, desenha linhas adicionais indicativas (representação simplificada)
        count = 3 if str(keys).startswith("3") else 2 if str(keys).startswith("2") else 1
        if count > 1:
            # Adiciona traços saindo do círculo para indicar múltiplas teclas
            for i in range(1, count):
                angle = math.pi / 4 + (i * math.pi / 4)
                dx = r * math.cos(angle)
                dy = r * math.sin(angle)
                parts.append(Part.makeLine(center, App.Vector(dx, y_offset_base + r + dy, 0)))

        # Linha ligando à parede
        parts.append(Part.makeLine(App.Vector(0, 0, 0), App.Vector(0, y_offset_base, 0)))
        
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
    return os.path.join(lib_3d, "Interruptores", source)

def load_switch_family_shape(fname):
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

def normalize_switch_shape(shape):
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
        # Centraliza exatamente na origem
        shape.translate(App.Vector(-center.x, -center.y, -center.z))
        
        # Gira 180 para alinhar com a frente do 2D (mesma lógica da tomada)
        shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), _SWITCH_3D_ARROW_ALIGNMENT_DEG)
    except Exception as e:
        App.Console.PrintError(f"Erro em normalize_switch_shape: {e}\n")
        
    return shape

class ProfessionalBIMSwitch:
    """Motor Geométrico para Interruptores"""
    def __init__(self, obj):
        obj.Proxy = self
        
        # --- CLASSIFICAÇÃO BIM ---
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcSwitchingDevice"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Elétrica"
        obj.addProperty("App::PropertyEnumeration", "SwitchType", t).SwitchType = ["Simples", "Paralelo", "Intermediário", "Misto"]
        
        # --- ENGENHARIA ELÉTRICA ---
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyString", "CircuitNumber", e).CircuitNumber = "C-01"
        obj.addProperty("App::PropertyEnumeration", "Voltage", e).Voltage = ["127V", "220V", "380V"]
        obj.addProperty("App::PropertyString", "LoadClassification", e).LoadClassification = "Iluminação"
        obj.addProperty("App::PropertyString", "PanelBoard", e).PanelBoard = ""
        obj.addProperty("App::PropertyString", "CircuitObject", e).CircuitObject = ""
        obj.addProperty("App::PropertyString", "SpaceOrSector", e).SpaceOrSector = ""
        
        # --- PARÂMETROS DE MODELAGEM ---
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "Keys", g).Keys = ["1 Tecla", "2 Teclas", "3 Teclas"]
        obj.addProperty("App::PropertyInteger", "KeyCount", g).KeyCount = 1
        obj.addProperty("App::PropertyEnumeration", "PlateSize", g).PlateSize = ["4x2", "4x4"]
        obj.addProperty("App::PropertyEnumeration", "CircuitType", g).CircuitType = ["Iluminação", "Automação"]
        obj.addProperty("App::PropertyEnumeration", "HeightType", g).HeightType = ["Baixa (300mm)", "Média (1100mm)", "Alta (2200mm)"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "SwitchApplication", g).SwitchApplication = "Predial"
        obj.addProperty("App::PropertyString", "IP_Rating", g).IP_Rating = "IP20"
        obj.addProperty("App::PropertyString", "ElectricalStandard", g).ElectricalStandard = "NBR 5410"
        obj.addProperty("App::PropertyString", "ReferenceLevel", g).ReferenceLevel = "Projeto"
        obj.addProperty("App::PropertyString", "ReferenceLevelObject", g).ReferenceLevelObject = ""
        obj.addProperty("App::PropertyLength", "LevelElevation", g).LevelElevation = 0.0
        obj.addProperty("App::PropertyLength", "MountingHeight", g).MountingHeight = 1100.0
        obj.addProperty("App::PropertyLength", "FinalElevation", g).FinalElevation = 1100.0
        obj.addProperty("App::PropertyString", "HostObject", g).HostObject = ""
        obj.addProperty("App::PropertyString", "HostFace", g).HostFace = ""
        obj.addProperty("App::PropertyLength", "SurfaceOffset", g).SurfaceOffset = 0.0
        if not hasattr(obj, "Tag"):
            obj.addProperty("App::PropertyString", "Tag", g).Tag = "INT-01"

        # --- SIMBOLOGIA 2D / PLOTAGEM ---
        s = "BIM_Simbologia"
        obj.addProperty("App::PropertyEnumeration", "SymbolPlaneMode", s).SymbolPlaneMode = ["Plano de simbologia", "Junto do interruptor"]
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
        obj.addProperty("App::PropertyFloat", "Snap_XMin", sn).Snap_XMin = -60.0
        obj.addProperty("App::PropertyFloat", "Snap_XMax", sn).Snap_XMax =  60.0
        obj.addProperty("App::PropertyFloat", "Snap_YMin", sn).Snap_YMin =  -8.5
        obj.addProperty("App::PropertyFloat", "Snap_YMax", sn).Snap_YMax =  10.0
        obj.addProperty("App::PropertyFloat", "Snap_ZMin", sn).Snap_ZMin = -40.0
        obj.addProperty("App::PropertyFloat", "Snap_ZMax", sn).Snap_ZMax =  40.0

    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            is_2 = "2 Teclas" in fp.Keys
            is_3 = "3 Teclas" in fp.Keys
            is_paralelo = "Paralelo" in fp.SwitchType
            is_intermediario = "Intermediário" in fp.SwitchType
            
            # Tenta resolver o nome do arquivo dinamicamente se não estiver preenchido
            if getattr(fp, "SourceFile", ""):
                fname = fp.SourceFile
            else:
                prefix = "Interruptor"
                tipo = "Simples"
                if is_paralelo: tipo = "Paralelo"
                if is_intermediario: tipo = "Intermediario"
                
                teclas = "1_Tecla"
                if is_2: teclas = "2_Teclas"
                if is_3: teclas = "3_Teclas"
                
                fname = f"{prefix}_{tipo}_{teclas}.FCStd"
            
            final_shape = None
            
            # Verifica Cache
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
                best_s = normalize_switch_shape(load_switch_family_shape(fname))
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
                                best_s = normalize_switch_shape(best_s)
                                if best_s:
                                    brep_data = best_s.exportBrepToString()
                                    _SHAPE_CACHE[cache_key] = brep_data
                                    final_shape = Part.Shape()
                                    final_shape.importBrepFromString(brep_data)
                        finally:
                            App.closeDocument(tmp_doc.Name)
                    else:
                        import FreeCADGui as Gui
                        App.Console.PrintWarning(f"[Eletrica BIM] Arquivo 3D nao localizado: '{fname}' em '{_resolve_family_path('')}'\n")

            # FALLBACK
            if not final_shape or final_shape.isNull():
                final_shape = Part.makeBox(120, 5, 80)
                final_shape.translate(App.Vector(-60, -8.5, -40))

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
            
            # Metadados de Tag
            prefix_tag = "INT"
            if is_paralelo: prefix_tag = "3W"
            if is_intermediario: prefix_tag = "4W"
            fp.Tag = f"{prefix_tag}-{fp.Keys[0]}"
            
        except Exception as e:
            import traceback
            App.Console.PrintError(f"Erro no motor BIM (Interruptor): {str(e)}\n{traceback.format_exc()}\n")

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