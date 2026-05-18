import FreeCAD as App
import Part
import math
import os

# Cache global para evitar abrir o arquivo da biblioteca repetidamente (Performance)
_SHAPE_CACHE = {}

def make_socket_plan_symbol(height_type, modules="1 Módulo", amperage="10A"):
    """Cria a simbologia 2D de planta usada pela tomada real e pelo fantasma."""
    try:
        s = 150.0
        h_tri = s * math.sqrt(3) / 2
        y_offset = 40.0
        count = 3 if str(modules).startswith("3") else 2 if str(modules).startswith("2") else 1
        spacing = 95.0
        x0 = -spacing * (count - 1) / 2.0
        parts = []

        for idx in range(count):
            cx = x0 + idx * spacing
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
            else:
                wire_outer = Part.makePolygon([p_base_left, p_base_right, p_vertex, p_base_left])
                parts.append(Part.Face(wire_outer))

            parts.append(Part.makeLine(App.Vector(0, 0, 0), p_mid))

            if str(amperage) == "20A":
                mark_y = y_offset + h_tri * 0.38
                parts.append(Part.makeCircle(12.0, App.Vector(cx, mark_y, 0), App.Vector(0, 0, 1)))

        wall_half = (s / 2) + spacing * max(0, count - 1) / 2.0
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
        obj.addProperty("App::PropertyEnumeration", "Phase", e).Phase = ["R", "S", "T", "RS", "RT", "ST", "RST"]
        obj.addProperty("App::PropertyString", "PanelBoard", e).PanelBoard = ""
        obj.addProperty("App::PropertyString", "CircuitObject", e).CircuitObject = ""
        obj.addProperty("App::PropertyString", "SpaceOrSector", e).SpaceOrSector = ""
        
        # --- PARÂMETROS DE MODELAGEM ---
        g = "BIM_3D_Parametros"
        obj.addProperty("App::PropertyEnumeration", "Modules", g).Modules = ["1 Módulo", "2 Módulos", "3 Módulos"]
        obj.addProperty("App::PropertyEnumeration", "Amperage", g).Amperage = ["10A", "20A"]
        obj.addProperty("App::PropertyEnumeration", "PlateSize", g).PlateSize = ["4x2", "4x4"]
        obj.addProperty("App::PropertyEnumeration", "CircuitType", g).CircuitType = ["TUG (Geral)", "TUE (Específico)", "UPS (Emergência)"]
        obj.addProperty("App::PropertyEnumeration", "HeightType", g).HeightType = ["Baixa (300mm)", "Média (1100mm)", "Alta (2200mm)"]
        obj.addProperty("App::PropertyString", "SourceFile", g).SourceFile = ""
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

    def execute(self, fp):
        global _SHAPE_CACHE
        try:
            # Mapeamento de Arquivos
            is_2 = "2 Módulos" in fp.Modules
            is_20 = "20A" in fp.Amperage
            
            if getattr(fp, "SourceFile", ""):
                fname = fp.SourceFile
            elif is_2:
                fname = "Tomada_Dupla_20A.FCStd" if is_20 else "Tomada_Dupla_10A_10A.FCStd"
            else:
                fname = "Tomada_Simples_20A.FCStd" if is_20 else "Tomada_Simples_10A.FCStd"
            
            final_shape = None
            
            # Verifica Cache (Usa serialização BREP String para evitar problemas de perda de documento e maximizar performance)
            if fname in _SHAPE_CACHE:
                final_shape = Part.Shape()
                final_shape.importBrepFromString(_SHAPE_CACHE[fname])
            else:
                # 1. TENTA PRIMEIRO A VERSÃO .brep (INFINITAMENTE MAIS RÁPIDA!)
                base_fname, _ = os.path.splitext(fname)
                brep_fname = base_fname + ".brep"
                full_path_brep = _resolve_family_path(brep_fname)
                
                if os.path.exists(full_path_brep):
                    try:
                        best_s = Part.read(full_path_brep)
                        if best_s and not best_s.isNull():
                            # Alinha o objeto conforme o seu ajuste de -8.5
                            bbox = best_s.BoundBox
                            center = bbox.Center
                            best_s.translate(App.Vector(-center.x, -bbox.YMin - 8.5, -center.z))
                            
                            # Salva em cache
                            brep_data = best_s.exportBrepToString()
                            _SHAPE_CACHE[fname] = brep_data
                            final_shape = best_s
                    except Exception as e:
                        App.Console.PrintWarning(f"[Eletrica BIM] Erro ao ler .brep de '{brep_fname}': {str(e)}. Tentando FCStd.\n")
                
                # 2. SE NÃO ENCONTROU O .brep, TENTA A VERSÃO CLÁSSICA .FCStd
                if not final_shape:
                    full_path_fcstd = _resolve_family_path(fname)
                    if os.path.exists(full_path_fcstd):
                        tmp_doc = App.openDocument(full_path_fcstd)
                        best_s = None
                        max_vol = -1.0
                        for o in tmp_doc.Objects:
                            temp_s = None
                            if hasattr(o, "Shape") and o.Shape and not o.Shape.isNull():
                                if o.Shape.Volume > 1.0:
                                    temp_s = o.Shape
                            elif hasattr(o, "Tip") and o.Tip and not o.Tip.Shape.isNull():
                                temp_s = o.Tip.Shape
                            
                            if temp_s:
                                if not best_s or temp_s.Volume > max_vol:
                                    max_vol = temp_s.Volume
                                    best_s = temp_s.copy()
                                    bbox = best_s.BoundBox
                                    center = bbox.Center
                                    best_s.translate(App.Vector(-center.x, -bbox.YMin - 8.5, -center.z))

                        if best_s:
                            brep_data = best_s.exportBrepToString()
                            _SHAPE_CACHE[fname] = brep_data
                            final_shape = Part.Shape()
                            final_shape.importBrepFromString(brep_data)
                        App.closeDocument(tmp_doc.Name)
                    else:
                        import FreeCADGui as Gui
                        App.Console.PrintWarning(f"[Eletrica BIM] Arquivo 3D nao localizado: '{fname}' ou '{brep_fname}' em '{_resolve_family_path('')}'\n")
                        Gui.statusMessage(f"AVISO: Arquivo 3D nao localizado: {fname}")

            # FALLBACK (Caso falhe, cria o bloco 4x2 com o espelho sobressaindo apenas 2mm na frente da parede de Y=0)
            if not final_shape or final_shape.isNull():
                final_shape = Part.makeBox(120, 5, 80)
                final_shape.translate(App.Vector(-60, -8.5, -40))

            # Gira 180 graus para alinhar a frente da tomada 3D com a ponta da seta do símbolo 2D (+Y)
            if final_shape:
                final_shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180.0)

            # SIMBOLOGIA 2D NBR 5444
            symbol_2d = self.make_nbr_symbol(fp.HeightType, fp.Modules, fp.Amperage)
            if symbol_2d:
                # O símbolo agora é colocado no (0,0,1) já que o 3D está centrado
                symbol_2d.translate(App.Vector(0, 0, 1.0))
                final_shape = Part.makeCompound([final_shape, symbol_2d])

            fp.Shape = final_shape
            
            # Metadados
            prefix = "TUG" if "Geral" in fp.CircuitType else "TUE"
            if "UPS" in fp.CircuitType: prefix = "UPS"
            fp.Tag = f"{prefix}-{fp.Amperage}"
            
        except Exception as e:
            App.Console.PrintError(f"Erro no motor BIM: {str(e)}\n")

    def make_nbr_symbol(self, height_type, modules="1 Módulo", amperage="10A"):
        """Cria o símbolo 2D padrão NBR 5444 alinhado e escalado com a mira no (0,0)."""
        return make_socket_plan_symbol(height_type, modules, amperage)

    def getSnapPoints(self, obj):
        """
        Gera 5 pontos de conexão padrão (Revit Style) para a caixa da tomada.
        """
        try:
            # Pegamos as dimensões reais da caixa para posicionar os imãs
            bbox = obj.Shape.BoundBox
            cx, cy = 0, 0 # Como está centralizado, o centro é 0,0
            
            # Altura média da caixa (Z)
            z_mid = (bbox.ZMax + bbox.ZMin) / 2
            
            # Lista de Imãs (Conectores):
            points = [
                App.Vector(cx, bbox.YMax, z_mid),  # Topo (Norte)
                App.Vector(cx, bbox.YMin, z_mid),  # Base (Sul)
                App.Vector(bbox.XMax, cy, z_mid),  # Direita (Leste)
                App.Vector(bbox.XMin, cy, z_mid),  # Esquerda (Oeste)
                App.Vector(cx, cy, bbox.ZMin),     # Fundo (Centro)
            ]
            
            return points
        except:
            return [App.Vector(0,0,0)]
