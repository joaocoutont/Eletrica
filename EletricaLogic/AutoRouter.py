# Algoritmos de Roteamento Automático de Infraestrutura
import FreeCAD

class AutoRouter:
    """
    Motor de roteamento para eletrodutos e eletrocalhas.
    """

    @staticmethod
    def route_orthogonal(start_point, end_point, height=2100):
        """
        Cria um caminho ortogonal (Manhattan) entre dois pontos em uma altura padrão.
        """
        # start_point e end_point são FreeCAD.Vector
        p1 = start_point
        p2 = end_point
        
        # Pontos intermediários para fazer o "Z" ou "L" ortogonal
        # 1. Sobe até a altura do teto/eletroduto
        # 2. Anda em X até o destino
        # 3. Anda em Y até o destino
        # 4. Desce até o componente
        
        nodes = [
            p1,
            FreeCAD.Vector(p1.x, p1.y, height),
            FreeCAD.Vector(p2.x, p1.y, height),
            FreeCAD.Vector(p2.x, p2.y, height),
            p2
        ]
        
        return nodes

    @staticmethod
    def create_auto_conduit(obj_start, obj_end):
        """
        Interliga dois objetos com um eletroduto automático.
        """
        if not hasattr(obj_start, "Placement") or not hasattr(obj_end, "Placement"):
            return None
            
        p1 = obj_start.Placement.Base
        p2 = obj_end.Placement.Base
        
        nodes = AutoRouter.route_orthogonal(p1, p2)
        
        # Aqui chamaria a lógica do Conduit.py para criar o objeto real
        from EletricaLogic.Conduit import ConduitManager
        conduit = ConduitManager.create_conduit_from_points(nodes)
        
        return conduit
