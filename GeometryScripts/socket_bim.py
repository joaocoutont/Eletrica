import FreeCAD as App
import Part
import math
import os

# Cache global para evitar abrir o arquivo da biblioteca repetidamente (Performance)
_SHAPE_CACHE = {}
_SHAPE_CACHE_ALIGNMENT = "fcstd_normalized_centered_v18"
_SOCKET_3D_ARROW_ALIGNMENT_DEG = 180.0

def _float_value(value, default=0.0):
    try:
        if hasattr(value, "Value"):
            return float(value.Value)
        return float(value)
    except Exception:
        return default

def make_socket_plan_symbol(height_type, modules="1 Módulo", amperage="10A"):
    """Cria a simbologia 2D de planta usada pela tomada real e pelo fantasma."""
    try:
        s = 150.0
        h_tri = s * math.sqrt(3) / 2
        y_offset_base = 50.0
        count = 3 if str(modules).startswith("3") else 2 if str(modules).startswith("2") else 1
        spacing_y = h_tri + 15.0 # Espaçamento vertical entre os triângulos
        
        parts = []

        for idx in range(count):
            # No Revit, eles ficam um na frente do outro (eixo Y), o X é sempre o centro 0
            cx = 0.0
            y_offset = y_offset_base + (idx * spacing_y)
            
            p_base_left = App.Vector(cx - s / 2, y_offset, 0)
            p_base_right = App.Vector(cx + s / 2, y_offset, 0)
            p_vertex = App.Vector(cx, y_offset + h_tri, 0)
            p_mid = App.Vector(cx, y_offset, 0)

            if "Baixa" in height_type:
                parts.append(Part.makePolygon([p_base_left, p_base_right, p_vertex, p_base_left]))
            elif "Média" in height_type or "Media" in height_type:
                wire_left = Part.makePolygon([p_base_left, p_mid, p_vertex, p_base_left])
                wire_right = Part.makePolygon([p_mid, p_base_right, p_vertex, p_mid])
                parts.append(Part.Face(wire_left))
                parts.append(wire_right)
            elif "Piso" in height_type:
                # Tomada de Piso: Triângulo com um círculo ao redor
                parts.append(Part.makePolygon([p_base_left, p_base_right, p_vertex, p_base_left]))
                c_center = App.Vector(cx, y_offset + h_tri / 2.5, 0)
                parts.append(Part.makeCircle(s * 0.7, c_center, App.Vector(0, 0, 1)))
            else:
                wire_outer = Part.makePolygon([p_base_left, p_base_right, p_vertex, p_base_left])
                parts.append(Part.Face(wire_outer))

            # A linha que liga à parede deve vir da base do primeiro triângulo (mais próximo da parede)
            # até a base do triângulo atual (para conectar todos eles na mesma haste vertical)
            if idx == 0:
                parts.append(Part.makeLine(App.Vector(0, 0, 0), p_mid))
            else:
                prev_vertex = App.Vector(cx, y_offset_base + ((idx - 1) * spacing_y) + h_tri, 0)
                parts.append(Part.makeLine(prev_vertex, p_mid))

        # wall_half = s / 2
        # parts.append(Part.makeLine(App.Vector(-wall_half, 0, 0), App.Vector(wall_half, 0, 0)))
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

def _existing_socket_source(fname, modules="", amperage=""):
    source = str(fname or "").replace("\\", "/").strip("/")
    if os.path.exists(_resolve_family_path(source)):
        return source

    is_3 = "3" in str(modules)
    is_2 = "2" in str(modules)
    is_20 = "20A" in str(amperage)
    module_count = 3 if is_3 else 2 if is_2 else 1

    candidates = [
        f"Tomadas/Cx_4x2_T{module_count}.FCStd",
        f"Cx_4x2_T{module_count}.FCStd",
    ]
    if module_count == 3:
        candidates.extend([
            "Tomadas/Tomada_Tripla_20A.FCStd" if is_20 else "Tomadas/Tomada_Tripla_10A.FCStd",
            "Tomada_Tripla_20A.FCStd" if is_20 else "Tomada_Tripla_10A.FCStd",
        ])
    elif module_count == 2:
        candidates.extend([
            "Tomadas/Tomada_Dupla_20A.FCStd" if is_20 else "Tomadas/Tomada_Dupla_10A_10A.FCStd",
            "Tomada_Dupla_20A.FCStd" if is_20 else "Tomada_Dupla_10A_10A.FCStd",
        ])
    else:
        candidates.extend([
            "Tomadas/Tomada_Simples_20A.FCStd" if is_20 else "Tomadas/Tomada_Simples_10A.FCStd",
            "Tomada_Simples_20A.FCStd" if is_20 else "Tomada_Simples_10A.FCStd",
        ])

    for candidate in candidates:
        if os.path.exists(_resolve_family_path(candidate)):
            if source and source != candidate:
                App.Console.PrintWarning(
                    f"[Eletrica BIM] Familia 3D '{source}' nao encontrada. "
                    f"Usando '{candidate}' como alternativa.\n"
                )
            return candidate
    return source

def load_socket_family_shape(fname):
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

def load_socket_family_metadata(fname):
    full_path_fcstd = _resolve_family_path(fname)
    if not os.path.exists(full_path_fcstd):
        return {}
    previous_doc_name = None
    try:
        if App.ActiveDocument:
            previous_doc_name = App.ActiveDocument.Name
    except Exception:
        previous_doc_name = None

    tmp_doc = App.openDocument(full_path_fcstd, True, True)
    try:
        source = str(fname or "").replace("\\", "/").strip("/")
        base = os.path.splitext(os.path.basename(source))[0]
        meta = {
            "id": base.lower().replace(" ", "_"),
            "name": base.replace("_", " "),
            "category": "Tomada",
            "discipline": "Eletrica",
            "ifc_class": "IfcFlowTerminal",
            "source_3d": source,
        }
        candidates = list(getattr(tmp_doc, "Objects", []) or [])
        candidates.sort(key=lambda obj: 0 if hasattr(obj, "Shape") else 1)
        prop_map = {
            "FamilyName": "name",
            "FamilyCategory": "category",
            "IFC_Class": "ifc_class",
            "Modules": "modules",
            "ModuleCount": "modules",
            "Amperage": "amperage",
            "Voltage": "voltage",
            "Power": "power",
            "ApparentPowerVA": "apparent_power_va",
            "ActivePowerW": "active_power_w",
            "PowerFactor": "power_factor",
            "DemandFactor": "demand_factor",
            "Phase": "phase",
            "LoadClassification": "load_classification",
            "SocketApplication": "socket_application",
            "IP_Rating": "ip_rating",
            "ElectricalStandard": "electrical_standard",
            "HeightType": "height_type",
            "MountingHeight": "mounting_height",
            "Manufacturer": "manufacturer",
            "Model": "model",
            "CatalogCode": "catalog_code",
            "FamilyDescription": "description",
        }
        for obj in candidates:
            for prop, key in prop_map.items():
                if not hasattr(obj, prop):
                    continue
                try:
                    value = getattr(obj, prop)
                    if hasattr(value, "Value"):
                        value = value.Value
                    if key == "modules" and isinstance(value, int):
                        value = f"{value} Modulos" if value > 1 else "1 Modulo"
                    if value not in [None, ""]:
                        meta[key] = value
                except Exception:
                    pass
        return meta
    finally:
        try:
            App.closeDocument(tmp_doc.Name)
        finally:
            if previous_doc_name:
                try:
                    App.setActiveDocument(previous_doc_name)
                except Exception:
                    pass

def normalize_socket_shape(shape):
    if not shape:
        return None
    try:
        if shape.isNull():
            return None
    except Exception:
        pass
    
    # Os arquivos 3D (.FCStd) já foram corrigidos de fábrica para estarem 
    # centralizados na origem e rotacionados corretamente.
    return shape


class ProfessionalBIMSocket:
    """Motor Geométrico para Tomadas (Versão Final Estabilizada)"""
    def __init__(self, obj):
        obj.Proxy = self
        
        # --- CLASSIFICAÇÃO BIM ---
        t = "BIM_Classificacao"
        obj.addProperty("App::PropertyString", "IFC_Class", t).IFC_Class = "IfcFlowTerminal"
        obj.addProperty("App::PropertyString", "Discipline", t).Discipline = "Elétrica"
        obj.addProperty("App::PropertyEnumeration", "SocketType", t).SocketType = ["Simples", "Dupla", "Tripla"]
        
        # --- ENGENHARIA ELÉTRICA ---
        e = "BIM_Engenharia"
        obj.addProperty("App::PropertyString", "CircuitNumber", e).CircuitNumber = "C-01"
        obj.addProperty("App::PropertyEnumeration", "Voltage", e).Voltage = ["127V", "220V", "380V"]
        obj.addProperty("App::PropertyFloat", "Power", e).Power = 100.0 # Watts
        obj.addProperty("App::PropertyFloat", "ApparentPowerVA", e).ApparentPowerVA = 100.0
        obj.addProperty("App::PropertyFloat", "ActivePowerW", e).ActivePowerW = 100.0
        obj.addProperty("App::PropertyFloat", "PowerFactor", e).PowerFactor = 1.0
        obj.addProperty("App::PropertyFloat", "DemandFactor", e).DemandFactor = 1.0
        obj.addProperty("App::PropertyString", "LoadClassification", e).LoadClassification = "TUG"
        obj.addProperty("App::PropertyEnumeration", "Phase", e).Phase = ["R", "S", "T", "RS", "RT", "ST", "RST"]
        obj.addProperty("App::PropertyString", "PanelBoard", e).PanelBoard = ""
        obj.addProperty("App::PropertyString", "CircuitObject", e).CircuitObject = ""
        obj.addProperty("App::PropertyString", "SpaceOrSector", e).SpaceOrSector = ""
        
        # --- PARÂMETROS DE MODELAGEM ---
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "Modules", g).Modules = ["1 Módulo", "2 Módulos", "3 Módulos"]
        obj.addProperty("App::PropertyInteger", "ModuleCount", g).ModuleCount = 1
        obj.addProperty("App::PropertyEnumeration", "Amperage", g).Amperage = ["10A", "20A"]
        obj.addProperty("App::PropertyEnumeration", "PlateSize", g).PlateSize = ["4x2", "4x4"]
        obj.addProperty("App::PropertyEnumeration", "CircuitType", g).CircuitType = ["TUG (Geral)", "TUE (Específico)", "UPS (Emergência)"]
        obj.addProperty("App::PropertyEnumeration", "HeightType", g).HeightType = ["Baixa (300mm)", "Média (1100mm)", "Alta (2200mm)", "Piso (0mm)"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
        obj.addProperty("App::PropertyString", "SocketApplication", g).SocketApplication = "Predial"
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
            obj.addProperty("App::PropertyString", "Tag", g).Tag = "TOM-01"

        # --- SIMBOLOGIA 2D / PLOTAGEM ---
        s = "BIM_Simbologia"
        obj.addProperty("App::PropertyEnumeration", "SymbolPlaneMode", s).SymbolPlaneMode = ["Plano de simbologia", "Junto da tomada"]
        try:
            obj.SymbolPlaneMode = "Plano de simbologia"
        except Exception:
            pass
        obj.addProperty("App::PropertyString", "SymbolPlaneName", s).SymbolPlaneName = "Plano de Simbologia"
        obj.addProperty("App::PropertyLength", "SymbolPlaneHeight", s).SymbolPlaneHeight = 0.0
        obj.addProperty("App::PropertyLength", "SymbolFinalElevation", s).SymbolFinalElevation = 0.0
        obj.addProperty("App::PropertyFloat", "SymbolZOffset", s).SymbolZOffset = 0.0

        # --- LIMITES 3D PARA CONECTORES MEP ---
        # Calculados sobre a geometria 3D pura, antes do símbolo 2D, para que
        # getSnapPoints retorne posições nas faces físicas da caixa.
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
            # Mapeamento de Arquivos
            is_2 = "2 Módulos" in fp.Modules
            is_3 = "3 Módulos" in fp.Modules
            is_20 = "20A" in fp.Amperage
            
            if getattr(fp, "SourceFile", ""):
                fname = fp.SourceFile
            elif is_3:
                fname = "Tomada_Tripla_20A.FCStd" if is_20 else "Tomada_Tripla_10A.FCStd"
            elif is_2:
                fname = "Tomada_Dupla_20A.FCStd" if is_20 else "Tomada_Dupla_10A_10A.FCStd"
            else:
                fname = "Tomada_Simples_20A.FCStd" if is_20 else "Tomada_Simples_10A.FCStd"
            fname = _existing_socket_source(fname, fp.Modules, fp.Amperage)
            
            final_shape = None

            # Verifica mtime do arquivo físico no disco para invalidação do cache
            full_path_fcstd = _resolve_family_path(fname)
            current_mtime = 0.0
            if os.path.exists(full_path_fcstd):
                try:
                    current_mtime = os.path.getmtime(full_path_fcstd)
                except Exception:
                    pass

            # Verifica Cache (Usa serialização BREP String para evitar problemas de perda de documento e maximizar performance)
            cache_key = f"{fname}|{_SHAPE_CACHE_ALIGNMENT}"

            if cache_key in _SHAPE_CACHE:
                cached_brep, cached_mtime = _SHAPE_CACHE[cache_key]
                if abs(cached_mtime - current_mtime) < 0.001:
                    final_shape = Part.Shape()
                    final_shape.importBrepFromString(cached_brep)
                    # Valida que o cache esta realmente centrado na origem
                    # Se nao estiver (cache antigo corrompido), descarta e recarrega
                    try:
                        center = final_shape.BoundBox.Center
                        if abs(center.x) > 1.0 or abs(center.y) > 1.0:
                            App.Console.PrintWarning(f"[BIM] Cache deslocado ({center.x:.1f}, {center.y:.1f}) - recalculando...\n")
                            del _SHAPE_CACHE[cache_key]
                            final_shape = None
                    except Exception:
                        pass
                else:
                    App.Console.PrintMessage(f"[BIM] Arquivo '{fname}' modificado no disco. Atualizando cache...\n")
                    del _SHAPE_CACHE[cache_key]
            
            if not final_shape:
                best_s = normalize_socket_shape(load_socket_family_shape(fname))
                if best_s:
                    brep_data = best_s.exportBrepToString()
                    _SHAPE_CACHE[cache_key] = (brep_data, current_mtime)
                    final_shape = Part.Shape()
                    final_shape.importBrepFromString(brep_data)
                # 1. REMOVIDO: O suporte a .brep foi removido pois perdia a matriz de Placement 
                # (origem de inserção) das famílias originais. Agora usamos apenas FCStd direto.
                
                # 2. SE NÃO ENCONTROU O .brep, TENTA A VERSÃO CLÁSSICA .FCStd
                if not final_shape:
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
                                elif hasattr(o, "Tip") and o.Tip and o.Tip.Shape and not o.Tip.Shape.isNull():
                                    temp_s = o.Tip.Shape.copy()
                                    if hasattr(o, "Placement") and o.Placement:
                                        temp_s.transformShape(o.Placement.toMatrix())
                                if temp_s:
                                    if not best_s or temp_s.Volume > max_vol:
                                        max_vol = temp_s.Volume
                                        best_s = temp_s.copy()
                            if best_s:
                                best_s = normalize_socket_shape(best_s)
                                if best_s:
                                    brep_data = best_s.exportBrepToString()
                                    _SHAPE_CACHE[cache_key] = (brep_data, current_mtime)
                                    final_shape = Part.Shape()
                                    final_shape.importBrepFromString(brep_data)
                        finally:
                            App.closeDocument(tmp_doc.Name)
                    else:
                        App.Console.PrintWarning(f"[Eletrica BIM] Arquivo 3D nao localizado: '{fname}' em '{_resolve_family_path('')}'\n")
                        try:
                            import FreeCADGui as Gui
                            if hasattr(Gui, "getMainWindow") and Gui.getMainWindow():
                                Gui.getMainWindow().statusBar().showMessage(f"AVISO: Arquivo 3D nao localizado: {fname}", 5000)
                        except Exception:
                            pass

            # FALLBACK: cria bloco 4x2 no mesmo ponto funcional das familias:
            # X centralizado, Y ancorado na parede/cursor com pequeno encaixe, Z centralizado.
            if not final_shape or final_shape.isNull():
                final_shape = Part.makeBox(120, 5, 80)
                final_shape.translate(App.Vector(-60, -8.5, -40))

            # Armazena os limites 3D puros ANTES de qualquer simbologia 2D.
            # O símbolo 2D agora é gerado como objeto separado pelo socket_gui,
            # mantendo fp.Shape com geometria física pura para BBox e snap corretos.
            if final_shape and not final_shape.isNull():
                try:
                    b = final_shape.BoundBox
                    fp.Snap_XMin = b.XMin; fp.Snap_XMax = b.XMax
                    fp.Snap_YMin = b.YMin; fp.Snap_YMax = b.YMax
                    fp.Snap_ZMin = b.ZMin; fp.Snap_ZMax = b.ZMax
                except Exception:
                    pass

            # GARANTIA FINAL: normaliza SEMPRE antes de gravar no objeto.
            if final_shape and not final_shape.isNull():
                try:
                    center = final_shape.BoundBox.Center
                    if abs(center.x) > 0.1 or abs(center.y) > 0.1 or abs(center.z) > 0.1:
                        final_shape.translate(App.Vector(-center.x, -center.y, -center.z))
                except Exception as e:
                    App.Console.PrintError(f"[BIM] Erro ao centralizar shape: {e}\n")

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
            
            # Metadados
            prefix = "TUG" if "Geral" in fp.CircuitType else "TUE"
            if "UPS" in fp.CircuitType: prefix = "UPS"
            fp.Tag = f"{prefix}-{fp.Amperage}"
            
        except Exception as e:
            import traceback
            App.Console.PrintError(f"Erro no motor BIM: {str(e)}\n{traceback.format_exc()}\n")

    def make_nbr_symbol(self, height_type, modules="1 Módulo", amperage="10A"):
        """Cria o símbolo 2D padrão NBR 5444 alinhado e escalado com a mira no (0,0)."""
        return make_socket_plan_symbol(height_type, modules, amperage)

    def getSnapPoints(self, obj):
        """
        Gera 5 pontos de conexão MEP (Revit Style) baseados na geometria 3D física.
        Usa os limites armazenados em Snap_* que são calculados ANTES do símbolo 2D,
        garantindo que os conectores fiquem nas faces reais da caixa da tomada.
        """
        try:
            # Usa os limites 3D armazenados (sem contaminação do símbolo 2D)
            snap_props = ["Snap_XMin", "Snap_XMax", "Snap_YMin", "Snap_YMax", "Snap_ZMin", "Snap_ZMax"]
            if all(hasattr(obj, p) for p in snap_props):
                xmin, xmax = obj.Snap_XMin, obj.Snap_XMax
                ymin, ymax = obj.Snap_YMin, obj.Snap_YMax
                zmin, zmax = obj.Snap_ZMin, obj.Snap_ZMax
            else:
                # Fallback: usa o BoundBox da shape atual
                b = obj.Shape.BoundBox
                xmin, xmax = b.XMin, b.XMax
                ymin, ymax = b.YMin, b.YMax
                zmin, zmax = b.ZMin, b.ZMax

            # Centro real da caixa (não hardcoded em 0,0)
            cx = (xmax + xmin) / 2
            cy = (ymax + ymin) / 2
            z_mid = (zmax + zmin) / 2

            return [
                App.Vector(cx,   ymax,  z_mid),  # Norte (frente/parede)
                App.Vector(cx,   ymin,  z_mid),  # Sul   (fundo/parede)
                App.Vector(xmax, cy,    z_mid),  # Leste (direita)
                App.Vector(xmin, cy,    z_mid),  # Oeste (esquerda)
                App.Vector(cx,   cy,    zmin),   # Fundo (entrada do eletroduto)
            ]
        except Exception:
            return [App.Vector(0, 0, 0)]
