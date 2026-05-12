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
                if not c_name: continue
                
                # Posicao: Um pouco deslocada do objeto para nao sobrepor
                pos = obj.Placement.Base
                # Se for um simbolo no teto, usamos a altura do teto
                z = symbol_height
                if obj.Label.startswith("Simbolo_"):
                    z = pos.z
                
                tag_pos = FreeCAD.Vector(pos.x + 200, pos.y + 200, z)
                
                # Criar o texto
                tag = Draft.make_text([c_name], placement=tag_pos)
                tag.Label = f"Tag_{obj.Label}"
                tag.ViewObject.FontSize = 150 # Tamanho legivel em mm
                tag.ViewObject.FontName = "Arial"
                
        doc.recompute()
        FreeCAD.Console.PrintMessage("Etiquetas de circuito geradas!\n")
