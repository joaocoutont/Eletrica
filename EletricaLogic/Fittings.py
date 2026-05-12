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
    def add_industrial_termination(conduit_obj, gland_type="PG16"):
        """Adiciona Sealtub e Prensa-Cabo no final do tubo"""
        from EletricaLogic.Library import LibraryManager
        if not hasattr(conduit_obj, "Shape"): return
        
        # 1. Obter o ultimo ponto do tubo
        points = conduit_obj.Shape.Vertexes
        end_point = points[-1].Point
        direction = conduit_obj.Shape.tangentAt(conduit_obj.Shape.Length)
        
        lib = LibraryManager()
        
        # 2. Inserir Prensa-Cabo
        gland = lib.insert_component("Prensa_Cabo.FCStd", label=f"PrensaCabo_{conduit_obj.Label}")
        if gland:
            gland.Placement.Base = end_point
            # Orientar conforme o tubo
            
        # 3. Marcar o tubo como Sealtub
        if not hasattr(conduit_obj, "TipoMaterial"):
            conduit_obj.addProperty("App::PropertyString", "TipoMaterial", "Eletrica", "Material")
        conduit_obj.TipoMaterial = "Sealtub (Flexível Estanque)"
        conduit_obj.ViewObject.ShapeColor = (0.2, 0.2, 0.2) # Preto/Grafite
        
        FreeCAD.ActiveDocument.recompute()

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

    @staticmethod
    def add_tray_supports(tray_obj, support_type="Teto_Trapezio", spacing=1500):
        """
        Adiciona suportes (Mão Francesa, Trapezio ou Tirante Central) ao longo da calha.
        """
        from EletricaLogic.Library import LibraryManager
        if not hasattr(tray_obj, "Shape"): return
        
        shape = tray_obj.Shape
        length = shape.Length
        num_supports = int(length / spacing)
        lib = LibraryManager()
        
        # Mapeamento de componentes
        comps = {
            "Teto_Trapezio": "Suporte_Trapezio_Duplo.FCStd",
            "Teto_Central": "Suporte_Tirante_Central.FCStd",
            "Parede": "Suporte_Mao_Francesa.FCStd"
        }
        comp = comps.get(support_type, "Suporte_Trapezio_Duplo.FCStd")
        
        for i in range(1, num_supports + 1):
            dist = i * spacing
            p = shape.valueAt(dist)
            
            obj = lib.insert_component(comp, label=f"Suporte_{tray_obj.Label}_{i}")
            if obj:
                obj.Placement.Base = p
                
        FreeCAD.Console.PrintMessage(f"{num_supports} suportes tipo {support_type} adicionados.\n")
