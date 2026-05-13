# Gerenciador de Etiquetas de Circuito (Tags)
import FreeCAD
import Draft

class TagManager:
    @staticmethod
    def generate_circuit_tags(symbol_height=2700.0):
        """
        Cria etiquetas de texto para cada componente identificando seu circuito.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        # 1. Limpar tags antigas para evitar duplicatas
        for obj in doc.Objects:
            if obj.Label.startswith("Tag_"):
                doc.removeObject(obj.Name)
        
        # 2. Criar novas tags
        for obj in doc.Objects:
            if hasattr(obj, "Circuito"):
                c_name = obj.Circuito
                if not c_name or c_name == "Geral": continue
                
                # Obter bitola se existir
                wire = ""
                if hasattr(obj, "SecaoCabo"):
                    wire = f" ({obj.SecaoCabo}mm²)"
                
                text_content = f"{c_name}{wire}"
                
                # Posicao: Um pouco deslocada do objeto
                pos = obj.Placement.Base
                tag_pos = FreeCAD.Vector(pos.x + 150, pos.y + 150, pos.z + 100)
                
                # Criar o texto
                tag = Draft.make_text([text_content], placement=tag_pos)
                tag.Label = f"Tag_{obj.Label}"
                tag.ViewObject.FontSize = 120 
                
                # Cores por tipo
                if "Iluminacao" in obj.Label or "Luz" in obj.Label:
                    tag.ViewObject.TextColor = (1.0, 1.0, 0.0) # Amarelo para luz
                else:
                    tag.ViewObject.TextColor = (0.0, 1.0, 1.0) # Ciano para força
                
        doc.recompute()
        FreeCAD.Console.PrintMessage("Etiquetas inteligentes (Circuito + Bitola) geradas com sucesso!\n")
