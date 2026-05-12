# Gerador de Simbologia de Fiacao (Tick Marks)
import FreeCAD
import Draft
import math

class AnnotationManager:
    @staticmethod
    def create_tick_marks(conduit_obj, symbol_height=2700.0):
        """
        Gera os simbolos de fiação (F, N, T, R) sobre o eletroduto.
        """
        doc = FreeCAD.ActiveDocument
        if not hasattr(conduit_obj, "CircuitosPassantes") or not hasattr(conduit_obj, "Shape"):
            return
            
        # 1. Obter ponto central e direcao do tubo
        shape = conduit_obj.Shape
        mid_point = shape.valueAt(shape.Length / 2.0)
        tangent = shape.tangentAt(shape.Length / 2.0)
        
        # Vetor perpendicular para desenhar os traços
        perp = FreeCAD.Vector(-tangent.y, tangent.x, 0).normalize()
        
        # 2. Determinar o que desenhar
        num_circuits = len(conduit_obj.CircuitosPassantes)
        if num_circuits == 0: return
        
        # Posicao inicial (Z ajustado para o plano de simbolos)
        base_pos = FreeCAD.Vector(mid_point.x, mid_point.y, symbol_height)
        
        offset = 80 # Espacamento entre simbolos
        start_pos = base_pos - (tangent * (offset * num_circuits * 2))
        
        for i in range(num_circuits):
            current_pos = start_pos + (tangent * (i * offset * 4))
            
            # FASE
            p1 = current_pos + (perp * 60)
            p2 = current_pos - (perp * 60)
            Draft.make_line(p1, p2).Label = f"Tick_F_{conduit_obj.Label}_{i}"
            
            # NEUTRO
            p_n1 = (current_pos + tangent * offset)
            p_n2 = p_n1 + (perp * 60)
            p_n3 = p_n2 + (tangent * 40)
            Draft.make_wire([p_n1, p_n2, p_n3]).Label = f"Tick_N_{conduit_obj.Label}_{i}"
            
            # TERRA
            p_t1 = (current_pos + tangent * (offset * 2))
            p_t2 = p_t1 + (perp * 60)
            p_t3 = p_t2 + (tangent * 30)
            p_t4 = p_t2 - (tangent * 30)
            Draft.make_wire([p_t1, p_t2]).Label = f"Tick_T_stem_{conduit_obj.Label}_{i}"
            Draft.make_wire([p_t3, p_t4]).Label = f"Tick_T_bar_{conduit_obj.Label}_{i}"
            
        doc.recompute()

    @staticmethod
    def create_rise_fall_symbols(conduit_obj):
        """Insere simbolos de prumada se o tubo mudar de nivel verticalmente"""
        if not hasattr(conduit_obj, "Shape"): return
        
        points = conduit_obj.Shape.Vertexes
        for i in range(len(points) - 1):
            p1 = points[i].Point
            p2 = points[i+1].Point
            
            if abs(p1.z - p2.z) > 100: 
                p_ref = p1 if abs(p1.z - p2.z) > 0 else p2
                Draft.make_circle(radius=50, placement=FreeCAD.Placement(p_ref, FreeCAD.Rotation()))
                if p1.z > p2.z: # Desce
                    Draft.make_line(p_ref + FreeCAD.Vector(-35,-35,0), p_ref + FreeCAD.Vector(35,35,0))
                    Draft.make_line(p_ref + FreeCAD.Vector(-35,35,0), p_ref + FreeCAD.Vector(35,-35,0))
                else: # Sobe
                    Draft.make_circle(radius=15, placement=FreeCAD.Placement(p_ref, FreeCAD.Rotation()), face=True)
        return True

    @staticmethod
    def annotate_circuits(conduit_obj):
        """Escreve o nome dos circuitos ao lado do eletroduto"""
        if not hasattr(conduit_obj, "CircuitosPassantes") or not conduit_obj.CircuitosPassantes:
            return
            
        shape = conduit_obj.Shape
        mid_point = shape.valueAt(shape.Length / 2.0)
        tangent = shape.tangentAt(shape.Length / 2.0)
        perp = FreeCAD.Vector(-tangent.y, tangent.x, 0).normalize()
        
        text_pos = mid_point + (perp * 200) # Offset para nao ficar em cima do tubo
        circuit_text = ", ".join(conduit_obj.CircuitosPassantes)
        
        Draft.make_text(circuit_text, placement=FreeCAD.Placement(text_pos, FreeCAD.Rotation()))
        return True
