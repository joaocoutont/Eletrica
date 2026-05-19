# Logica de Roteamento Automatico de Eletrodutos - Algoritmo A* 3D
import FreeCAD
import Draft
import math
from EletricaLogic.Conduit import ConduitManager


def _manhattan_3d(a, b):
    """Heurística Manhattan 3D para A*."""
    return abs(a.x - b.x) + abs(a.y - b.y) + abs(a.z - b.z)


class AutoRouter:
    """Roteamento automático de eletrodutos com algoritmo A* Manhattan 3D."""

    # Passo da grade de roteamento (mm) — menor = mais preciso, mais lento
    GRID_STEP = 100  # 10 cm

    @staticmethod
    def get_best_connection_point(obj, target_point=None):
        """
        Retorna o ponto de conexão global mais adequado de um objeto.
        Se target_point for fornecido, escolhe o snap mais próximo dele.
        Caso contrário, ou se não houver snaps, retorna Placement.Base.
        """
        local_pts = []
        
        # 1. Tenta obter pontos de snap do Proxy (caso seja uma Caixa ou outro FeaturePython)
        if hasattr(obj, "Proxy") and obj.Proxy and hasattr(obj.Proxy, "getSnapPoints"):
            try:
                local_pts = obj.Proxy.getSnapPoints(obj)
            except Exception:
                pass
                
        # 2. Se for uma tomada instanciada (Part::Feature), busca da sua tomada matriz
        if not local_pts and hasattr(obj, "LibraryMatrixObject") and obj.LibraryMatrixObject:
            try:
                doc = obj.Document
                matriz = doc.getObject(obj.LibraryMatrixObject)
                if matriz and hasattr(matriz, "Proxy") and matriz.Proxy and hasattr(matriz.Proxy, "getSnapPoints"):
                    local_pts = matriz.Proxy.getSnapPoints(matriz)
            except Exception:
                pass
                
        # 3. Fallback genérico: o objeto implementa getSnapPoints diretamente
        #    (sem Proxy). Chamado SEM argumento extra — assinatura: def getSnapPoints(self)
        if not local_pts:
            for attr in ["getSnapPoints", "get_snap_points"]:
                method = getattr(obj, attr, None)
                if callable(method):
                    try:
                        local_pts = method()  # sem obj — é bound method
                        break
                    except Exception:
                        pass
                        
        if not local_pts:
            return obj.Placement.Base
            
        # 4. Transforma os pontos locais de snap para coordenadas globais
        global_pts = []
        for pt in local_pts:
            try:
                global_pts.append(obj.Placement.multVec(pt))
            except Exception:
                try:
                    m = obj.Placement.toMatrix()
                    global_pts.append(m.multiply(pt))
                except Exception:
                    pass
                    
        if not global_pts:
            return obj.Placement.Base
            
        # 5. Seleciona o ponto global mais próximo do ponto de destino
        if target_point is not None:
            try:
                if hasattr(target_point, 'x'):
                    target_vec = target_point
                else:
                    target_vec = FreeCAD.Vector(*target_point)
                best_pt = min(global_pts, key=lambda pt: (pt - target_vec).Length)
                return best_pt
            except Exception:
                pass
                
        return global_pts[0]

    @staticmethod
    def _is_blocked(point_s, obstacles_bbox):
        """Verifica se um ponto (snapado) colide com alguma bounding box de obstáculo."""
        px, py, pz = point_s
        # Margem de segurança de 20mm
        margin = 20
        for bbox in obstacles_bbox:
            if (bbox.XMin - margin <= px <= bbox.XMax + margin and
                bbox.YMin - margin <= py <= bbox.YMax + margin and
                bbox.ZMin - margin <= pz <= bbox.ZMax + margin):
                return True
        return False

    @staticmethod
    def route_astar(start: FreeCAD.Vector, end: FreeCAD.Vector,
                    obstacles=None, ceiling_z=2800.0):
        """
        Encontra o caminho de menor custo entre dois pontos usando A*.
        Respeita o teto (ceiling_z), desvia de obstáculos e gera trajetória ortogonal.
        """
        step = AutoRouter.GRID_STEP

        def snap(v):
            return (
                round(v.x / step) * step,
                round(v.y / step) * step,
                round(v.z / step) * step,
            )

        start_s = snap(start)
        end_s   = snap(end)
        ceil_s  = round(ceiling_z / step) * step

        # Preparar bounding boxes dos obstáculos para performance
        obstacles_bbox = []
        if obstacles:
            for obj in obstacles:
                if hasattr(obj, "Shape") and obj.Shape:
                    obstacles_bbox.append(obj.Shape.BoundBox)

        # Movimentos ortogonais (6 direções 3D)
        moves = [
            (step, 0, 0), (-step, 0, 0),
            (0, step, 0), (0, -step, 0),
            (0, 0, step), (0, 0, -step),
        ]

        open_set   = {start_s: 0}
        came_from  = {}
        g_score    = {start_s: 0}
        f_score    = {start_s: _manhattan_3d(FreeCAD.Vector(*start_s), FreeCAD.Vector(*end_s))}

        max_iter = 5000  # Aumentado para lidar com desvios
        iteration = 0

        while open_set and iteration < max_iter:
            iteration += 1
            current = min(open_set, key=lambda n: f_score.get(n, float('inf')))

            if current == end_s:
                # Reconstruir caminho
                path = []
                while current in came_from:
                    path.append(FreeCAD.Vector(*current))
                    current = came_from[current]
                path.append(FreeCAD.Vector(*start_s))
                path.reverse()
                return AutoRouter._simplify_path(path)

            del open_set[current]
            cx, cy, cz = current

            for dx, dy, dz in moves:
                neighbor = (cx + dx, cy + dy, cz + dz)
                
                # 1. Respeitar teto
                if neighbor[2] > ceil_s:
                    continue
                
                # 2. Verificar colisão
                if AutoRouter._is_blocked(neighbor, obstacles_bbox):
                    continue

                tentative_g = g_score[current] + step

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor]   = tentative_g
                    f_score[neighbor]   = tentative_g + _manhattan_3d(
                        FreeCAD.Vector(*neighbor), FreeCAD.Vector(*end_s))
                    open_set[neighbor]  = f_score[neighbor]

        # Fallback
        FreeCAD.Console.PrintWarning("AutoRouter: A* falhou ou obstáculo intransponível. Usando rota direta.\n")
        return [start, FreeCAD.Vector(start.x, start.y, ceiling_z), FreeCAD.Vector(end.x, end.y, ceiling_z), end]

    @staticmethod
    def _simplify_path(path):
        """Remove pontos colineares consecutivos para simplificar o polilinha."""
        if len(path) < 3:
            return path
        simplified = [path[0]]
        for i in range(1, len(path) - 1):
            p_prev = path[i - 1]
            p_curr = path[i]
            p_next = path[i + 1]
            d1 = (p_curr - p_prev).normalize()
            d2 = (p_next - p_curr).normalize()
            if abs(d1.dot(d2) - 1.0) > 1e-6:  # Direção mudou
                simplified.append(p_curr)
        simplified.append(path[-1])
        return simplified

    @staticmethod
    def connect_with_obstacles(objects, ceiling_z=2800.0):
        """
        Conecta objetos em sequência desviando de outros objetos BIM no documento.
        Considera automaticamente 'Walls', 'Structure' e 'Columns' como obstáculos.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        # Filtra obstáculos comuns de arquitetura
        obstacles = [obj for obj in doc.Objects if any(s in obj.Label for s in ["Wall", "Parede", "Viga", "Coluna", "Pilar"])]
        
        for i in range(len(objects) - 1):
            p1 = AutoRouter.get_best_connection_point(objects[i], objects[i + 1].Placement.Base)
            p2 = AutoRouter.get_best_connection_point(objects[i + 1], p1)
            path = AutoRouter.route_astar(p1, p2, obstacles=obstacles, ceiling_z=ceiling_z)
            ConduitManager.create_conduit(path, label=f"Elet_Smart_{objects[i].Label}")
        
        doc.recompute()

    @staticmethod
    def connect_in_sequence(objects, ceiling_z=2800.0, diameter=20.0):
        """Conecta uma lista de objetos em sequência com eletrodutos roteados via A*."""
        if len(objects) < 2:
            return
        for i in range(len(objects) - 1):
            p1 = AutoRouter.get_best_connection_point(objects[i], objects[i + 1].Placement.Base)
            p2 = AutoRouter.get_best_connection_point(objects[i + 1], p1)
            path = AutoRouter.route_astar(p1, p2, ceiling_z=ceiling_z)
            ConduitManager.create_conduit(path, diameter=diameter,
                                          label=f"Eletroduto_{objects[i].Label}_to_{objects[i+1].Label}")
        FreeCAD.ActiveDocument.recompute()

    @staticmethod
    def connect_to_nearest_ceiling(device_objs, ceiling_z=2800.0):
        """Conecta cada dispositivo ao ponto de luz de teto mais próximo via A*."""
        doc = FreeCAD.ActiveDocument
        lights = [obj for obj in doc.Objects if "Luz" in obj.Label or "Lampada" in obj.Label]

        if not lights:
            FreeCAD.Console.PrintWarning("Nenhum ponto de luz encontrado.\n")
            return

        for dev in device_objs:
            p_dev = dev.Placement.Base
            nearest = min(lights, key=lambda l: (l.Placement.Base - p_dev).Length)
            p1 = AutoRouter.get_best_connection_point(dev, nearest.Placement.Base)
            p2 = AutoRouter.get_best_connection_point(nearest, p1)
            path = AutoRouter.route_astar(p1, p2, ceiling_z=ceiling_z)
            ConduitManager.create_conduit(path, label=f"Elet_{dev.Label}_to_{nearest.Label}")

        doc.recompute()

    @staticmethod
    def connect_with_cable_tray(objects, ceiling_z=3500.0, width=200, height=100):
        """Conecta objetos em sequência usando eletrocalhas industriais via A*."""
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        obstacles = [obj for obj in doc.Objects if any(s in obj.Label for s in ["Wall", "Parede", "Viga", "Coluna", "Pilar"])]
        
        for i in range(len(objects) - 1):
            p1 = AutoRouter.get_best_connection_point(objects[i], objects[i + 1].Placement.Base)
            p2 = AutoRouter.get_best_connection_point(objects[i + 1], p1)
            path = AutoRouter.route_astar(p1, p2, obstacles=obstacles, ceiling_z=ceiling_z)
            ConduitManager.create_cable_tray(path, width=width, height=height, 
                                            label=f"Leito_{objects[i].Label}")
        doc.recompute()
