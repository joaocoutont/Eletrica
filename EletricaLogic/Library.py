# Gerenciador de Biblioteca de Objetos
import os
import FreeCAD

class LibraryManager:
    def __init__(self, path_3d=None, path_2d=None):
        self.path_3d = path_3d or r"D:\Objetos 3D\Curso FRECAD ELETRICO\HRC_Nova_Biblioteca_3D"
        self.path_2d = path_2d or r"D:\Objetos 3D\Curso FRECAD ELETRICO\Biblioteca 2D"

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
            
            # Tentar inserir simbolo 2D correspondente
            symbol_file = self.get_symbol_for_3d(filename)
            if symbol_file:
                self.insert_symbol(symbol_file, link)
                FreeCAD.Console.PrintMessage(f"Simbolo 2D '{symbol_file}' vinculado.\n")
            
            FreeCAD.Console.PrintMessage(f"Inserido: {obj_name}\n")
            return link
        except Exception as e:
            FreeCAD.Console.PrintError(f"Erro ao inserir componente: {str(e)}\n")
            return None

    def get_symbol_for_3d(self, filename_3d):
        """
        Tenta encontrar o simbolo 2D mais adequado para o componente 3D.
        """
        # Mapeamento basico manual (podemos expandir isso)
        mapping = {
            "HRC_Tomada_1_10A": "Tomada Baixa.FCStd",
            "HRC_Tomada_1_20A": "Tomada Baixa.FCStd",
            "HRC_Interruptor_1Botao": "Interruptor Simples.FCStd",
            "HRC_Interruptor_2Botoes": "Interruptor 2 Seções.FCStd",
            "HRC_Caixa de Distribuição": "Quadro de distribuição.FCStd",
            "Bocal e Lampada": "Ponto de Luz no teto.FCStd"
        }
        
        # Tentar busca por prefixo se nao estiver no mapping
        base_name = filename_3d.replace(".FCStd", "")
        if base_name in mapping:
            return mapping[base_name]
            
        # Busca generica por palavras chave
        if "Tomada" in base_name: return "Tomada Baixa.FCStd"
        if "Interruptor" in base_name: return "Interruptor Simples.FCStd"
        if "Luz" in base_name or "Lampada" in base_name: return "Ponto de Luz no teto.FCStd"
        
        return None

    def insert_symbol(self, symbol_filename, parent_obj=None):
        """Insere o simbolo 2D e o vincula ao objeto 3D"""
        if not symbol_filename: return
        
        full_path = os.path.join(self.path_2d, symbol_filename)
        if not os.path.exists(full_path): return
        
        doc = FreeCAD.ActiveDocument
        try:
            # Inserir o simbolo como um Link tambem, para manter o original
            sym_name = "Simbolo_" + symbol_filename.replace(".FCStd", "")
            sym_link = doc.addObject("App::Link", sym_name)
            sym_link.LinkedObject = FreeCAD.open(full_path).Objects[0]
            
            # Se tiver um pai (objeto 3D), vincula a posicao
            if parent_obj:
                # No FreeCAD, podemos colocar em um Group ou apenas manter proximo
                # O ideal para BIM e que o simbolo seja um 'filho' visual
                pass
                
            return sym_link
        except:
            return None
