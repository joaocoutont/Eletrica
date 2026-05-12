# Gerenciamento de Conduletes e Conexoes Aparentes
import FreeCAD
import math

class FittingManager:
    @staticmethod
    def add_conduletes_to_conduit(conduit_obj):
        """
        Analisa os pontos do eletroduto e insere caixas de condulete nos nos.
        """
        if not hasattr(conduit_obj, "Shape"): return
        
        doc = FreeCAD.ActiveDocument
        shape = conduit_obj.Shape
        # Pegar os vertices (pontos de conexao)
        vertices = shape.Vertexes
        
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        
        # Mapeamento de tipos (Simplificado)
        # 2 conexoes em angulo -> Condulete L
        # 3 conexoes -> Condulete T
        # Final de linha -> Condulete C ou E
        
        for i, v in enumerate(vertices):
            p = v.Point
            
            # Decidir o tipo baseado na posicao na lista
            if i == 0 or i == len(vertices) - 1:
                comp = "Condulete_Tipo_E.FCStd" # Final
            else:
                comp = "Condulete_Tipo_L.FCStd" # Curva (Assumindo L por padrao)
                
            # Inserir o componente
            # (Aqui precisaríamos ter esses arquivos na biblioteca)
            obj = lib.insert_component(comp, label=f"Condulete_{conduit_obj.Label}_{i}")
            if obj:
                obj.Placement.Base = p
                
        doc.recompute()
        FreeCAD.Console.PrintMessage(f"Conduletes adicionados ao longo de {conduit_obj.Label}.\n")

    @staticmethod
    def add_clamps(conduit_obj, spacing=1000):
        """
        Adiciona abracadeiras a cada X mm ao longo do eletroduto.
        """
        import Draft
        doc = FreeCAD.ActiveDocument
        shape = conduit_obj.Shape
        length = shape.Length
        
        num_clamps = int(length / spacing)
        
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        
        for i in range(1, num_clamps + 1):
            # Encontrar ponto proporcional ao longo da curva
            dist = i * spacing
            p = shape.valueAt(dist)
            
            # Inserir abracadeira
            obj = lib.insert_component("Abracadeira_Tipo_D.FCStd", label=f"Abracadeira_{conduit_obj.Label}_{i}")
            if obj:
                obj.Placement.Base = p
                # Orientacao basica (poderia ser refinada tangencialmente)
                
        doc.recompute()
        FreeCAD.Console.PrintMessage(f"{num_clamps} abracadeiras adicionadas a {conduit_obj.Label}.\n")

    @staticmethod
    def add_tray_fittings(tray_obj):
        """
        Analisa o caminho da eletrocalha e insere conexoes (curvas horiz/vert).
        """
        from EletricaLogic.Library import LibraryManager
        if not hasattr(tray_obj, "Shape"): return
        
        vertices = tray_obj.Shape.Vertexes
        lib = LibraryManager()
        
        for i in range(1, len(vertices) - 1):
            p1 = vertices[i-1].Point
            p2 = vertices[i].Point
            p3 = vertices[i+1].Point
            
            # Mudanca vertical detectada?
            is_vertical = abs(p1.z - p2.z) > 10.0 or abs(p2.z - p3.z) > 10.0
            
            if is_vertical:
                comp = "Curva_Inversao_Eletrocalha.FCStd"
            else:
                comp = "Curva_Horizontal_90_Eletrocalha.FCStd"
                
            obj = lib.insert_component(comp, label=f"Conexao_{tray_obj.Label}_{i}")
            if obj:
                obj.Placement.Base = p2
        
        FreeCAD.ActiveDocument.recompute()
