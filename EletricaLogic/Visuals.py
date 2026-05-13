# Visualização de Metadados e Heatmaps 3D
import FreeCAD

class HeatmapManager:
    """
    Gerencia a coloração dinâmica de objetos baseada em métricas de engenharia.
    """

    @staticmethod
    def toggle_voltage_drop_heatmap(active=True):
        """
        Pinta os objetos com base na Queda de Tensão (%).
        Verde: < 1.0% (Excelente)
        Amarelo: 1.0% - 3.0% (Dentro da norma)
        Vermelho: > 3.0% (Crítico / Revisar)
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return

        for obj in doc.Objects:
            if not hasattr(obj, "ViewObject"): continue
            
            # Resetar cor se desativar
            if not active:
                # Retorna para a cor padrão (ex: cinza ou cor original)
                obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
                continue

            # Buscar queda de tensão (pode estar em propriedades custom ou calculada)
            # Para o MVP, vamos buscar em uma propriedade 'QuedaTensao' que o Circuits.py preenche
            drop = getattr(obj, "QuedaTensao", 0.0)
            
            # Se for um eletroduto, tenta buscar do seu circuito principal
            if hasattr(obj, "TaxaOcupacao") and hasattr(obj, "CircuitosPassantes"):
                # Simplificação: pega o maior drop dos circuitos que passam por ele
                # (Requereria integração com o Circuits_data)
                pass

            if drop == 0 and not hasattr(obj, "Potencia"):
                continue

            # Escala de Cores (RGB de 0.0 a 1.0)
            if drop < 1.0:
                obj.ViewObject.ShapeColor = (0.15, 0.68, 0.37) # Verde (Emerald)
            elif drop <= 3.0:
                obj.ViewObject.ShapeColor = (0.95, 0.77, 0.06) # Amarelo (Sunflower)
            else:
                obj.ViewObject.ShapeColor = (0.91, 0.30, 0.24) # Vermelho (Alizarin)

        FreeCAD.Console.PrintMessage(f"Heatmap de Queda de Tensão: {'Ativado' if active else 'Desativado'}\n")

    @staticmethod
    def toggle_occupancy_heatmap(active=True):
        """
        Pinta eletrodutos com base na Taxa de Ocupação (%).
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return

        for obj in doc.Objects:
            if not hasattr(obj, "TaxaOcupacao") or not hasattr(obj, "ViewObject"):
                continue
            
            if not active:
                obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
                continue

            occ = obj.TaxaOcupacao
            if occ < 30.0:
                obj.ViewObject.ShapeColor = (0.15, 0.68, 0.37)
            elif occ <= 40.0:
                obj.ViewObject.ShapeColor = (0.95, 0.77, 0.06)
            else:
                obj.ViewObject.ShapeColor = (0.91, 0.30, 0.24)
