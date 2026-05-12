# Gerenciador de Biblioteca de Objetos
import os
import FreeCAD

class LibraryManager:
    def __init__(self, path_3d=None):
        self.path_3d = path_3d or r"D:\Objetos 3D\Curso FRECAD ELETRICO\HRC_Nova_Biblioteca_3D"
        self.path_2d = None # A ser definido pelo usuario

    def list_components(self):
        """Lista todos os componentes .FCStd disponiveis na biblioteca 3D"""
        if not os.path.exists(self.path_3d):
            return []
        return [f for f in os.listdir(self.path_3d) if f.endswith('.FCStd')]

    def insert_component(self, filename, label=None):
        """
        Insere um componente da biblioteca no documento ativo usando App::Link.
        Isso mantem o arquivo original como referencia (BIM).
        """
        full_path = os.path.join(self.path_3d, filename)
        if not os.path.exists(full_path):
            FreeCAD.Console.PrintError(f"Arquivo nao encontrado: {full_path}\n")
            return None
        
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument("ProjetoEletrico")
            
        # Nome do objeto baseado no arquivo
        obj_name = filename.replace(".FCStd", "")
        
        # Criar um Link para o arquivo externo
        # No FreeCAD, o App::Link pode apontar para um arquivo externo
        try:
            link = doc.addObject("App::Link", obj_name)
            link.LinkedObject = FreeCAD.open(full_path).Objects[0] # Pega o primeiro objeto do arquivo
            link.Label = label or obj_name
            
            # Adicionar propriedades elétricas customizadas (BIM)
            if not hasattr(link, "Potencia"):
                link.addProperty("App::PropertyPower", "Potencia", "Eletrica", "Potencia instalada em VA")
                link.Potencia = 100.0 # Valor default
                
            if not hasattr(link, "Circuito"):
                link.addProperty("App::PropertyString", "Circuito", "Eletrica", "Identificacao do Circuito")
                link.Circuito = "Geral"
            
            doc.recompute()
            FreeCAD.Console.PrintMessage(f"Inserido: {obj_name}\n")
            return link
        except Exception as e:
            FreeCAD.Console.PrintError(f"Erro ao inserir componente: {str(e)}\n")
            return None

    def get_symbol_for_3d(self, component_name):
        """
        Mapeia um objeto 3D para seu simbolo 2D correspondente.
        Isso permite que ao inserir uma tomada 3D, o simbolo 2D seja carregado automaticamente.
        """
        # Logica de mapeamento (Ex: HRC_Tomada_1_10A.FCStd -> Simbolo_Tomada.svg/dxf)
        pass
