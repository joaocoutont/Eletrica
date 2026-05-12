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
        # Simplificacao: Vamos assumir que cada circuito tem F+N+T
        # Se for um circuito de retorno (iluminacao), desenharia R
        num_circuits = len(conduit_obj.CircuitosPassantes)
        
        # Posicao inicial (Z ajustado para o plano de simbolos)
        base_pos = FreeCAD.Vector(mid_point.x, mid_point.y, symbol_height)
        
        offset = 80 # Espacamento entre simbolos
        start_pos = base_pos - (tangent * (offset * num_circuits * 2))
        
        for i in range(num_circuits):
            current_pos = start_pos + (tangent * (i * offset * 4))
            
            # 1. FASE (Traço perpendicular completo)
            p1 = current_pos + (perp * 60)
            p2 = current_pos - (perp * 60)
            Draft.make_line(p1, p2).Label = f"Tick_F_{conduit_obj.Label}_{i}"
            
            # 2. NEUTRO (L - Traço perpendicular + bracinho horizontal)
            p_n1 = (current_pos + tangent * offset)
            p_n2 = p_n1 + (perp * 60)
            p_n3 = p_n2 + (tangent * 40) # Bracinho
            Draft.make_wire([p_n1, p_n2, p_n3]).Label = f"Tick_N_{conduit_obj.Label}_{i}"
            
            # 3. TERRA (T - Traço perpendicular + braco em T)
            p_t1 = (current_pos + tangent * (offset * 2))
            p_t2 = p_t1 + (perp * 60)
            p_t3 = p_t2 + (tangent * 30)
            p_t4 = p_t2 - (tangent * 30)
            Draft.make_wire([p_t1, p_t2]).Label = f"Tick_T_stem_{conduit_obj.Label}_{i}"
            Draft.make_wire([p_t3, p_t4]).Label = f"Tick_T_bar_{conduit_obj.Label}_{i}"
            
        doc.recompute()
        FreeCAD.Console.PrintMessage(f"Tick marks gerados para {conduit_obj.Label}\n")
