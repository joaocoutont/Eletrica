# Logica de Visualizacao e Mapas de Calor
import FreeCAD

class VisualManager:
    @staticmethod
    def apply_voltage_drop_heatmap():
        """
        Colore os eletrodutos baseado na queda de tensao ou ocupacao.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        for obj in doc.Objects:
            # Foco em eletrodutos
            if hasattr(obj, "TaxaOcupacao") and hasattr(obj, "ViewObject"):
                occ = obj.TaxaOcupacao
                
                # Cores RGB (R, G, B) de 0.0 a 1.0
                if occ > 40.0:
                    color = (1.0, 0.0, 0.0) # Vermelho (Critico)
                elif occ > 30.0:
                    color = (1.0, 1.0, 0.0) # Amarelo (Alerta)
                else:
                    color = (0.0, 1.0, 0.0) # Verde (OK)
                
                obj.ViewObject.ShapeColor = color
                
        doc.recompute()
        FreeCAD.Console.PrintMessage("Mapa de calor aplicado aos eletrodutos.\n")

    @staticmethod
    def reset_colors():
        """Reseta as cores originais"""
        doc = FreeCAD.ActiveDocument
        for obj in doc.Objects:
            if hasattr(obj, "TaxaOcupacao") and hasattr(obj, "ViewObject"):
                obj.ViewObject.ShapeColor = (0.7, 0.7, 0.7)
        doc.recompute()
