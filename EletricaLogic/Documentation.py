# Automação de Pranchas e Documentação Técnica (TechDraw)
import FreeCAD
import os

class TechDrawManager:
    """
    Automatiza a criação de desenhos 2D (Pranchas) a partir do modelo 3D.
    """

    @staticmethod
    def create_project_sheet():
        """
        Cria uma nova página do TechDraw com carimbo preenchido.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return

        # 1. Criar a página
        page = doc.addObject('TechDraw::DrawPage', 'Prancha_Eletrica')
        
        # 2. Tentar carregar um template (A3 padrão do FreeCAD)
        template_path = os.path.join(FreeCAD.getResourceDir(), "Mod", "TechDraw", "Templates", "A3_Landscape_ISO7200_NC.svg")
        template = doc.addObject('TechDraw::DrawSVGTemplate', 'Template_A3')
        template.Template = template_path
        page.Template = template
        
        # 3. Preencher Carimbo (TitleBlock) usando ProjectData
        meta = doc.getObject("Eletrica_ProjectData")
        if meta:
            # TechDraw usa dicionário para preencher campos editáveis do SVG
            fields = {
                "Title": getattr(meta, "ProjectName", "Projeto Elétrico"),
                "Author": getattr(meta, "DesignerName", "Engenheiro"),
                "Date": "2026-05-13",
                "Project": "Suite Elite BIM"
            }
            # Nota: O preenchimento real depende dos IDs do SVG do template
            # page.EditableTexts = fields 
            
        FreeCAD.Console.PrintMessage("Prancha técnica criada com sucesso.\n")
        doc.recompute()
        return page

    @staticmethod
    def add_top_view(page):
        """
        Adiciona uma vista de topo (planta baixa) à página informada.
        """
        doc = FreeCAD.ActiveDocument
        if not doc or not page:
            return None

        view = doc.addObject('TechDraw::DrawViewPart', 'Planta_Baixa')
        view.Source = [o for o in doc.Objects if hasattr(o, "Shape")]
        view.Direction = (0, 0, 1) # Vista de topo
        page.addView(view)
        
        FreeCAD.Console.PrintMessage("Vista de planta baixa adicionada à prancha.\n")
        doc.recompute()

    @staticmethod
    def generate_legend(page):
        """
        Gera uma legenda automática de símbolos baseada nos itens usados no projeto.
        """
        # Futura implementação: criar uma tabela TechDraw com os ícones da Library.py
        pass
