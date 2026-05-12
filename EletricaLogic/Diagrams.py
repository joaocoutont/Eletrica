# Gerador de Diagramas Unifilares Graficos (TechDraw)
import FreeCAD
import Draft
import TechDraw

class UnifilarGenerator:
    @staticmethod
    def create_graphic_diagram(panel_obj):
        """Gera o desenho tecnico do diagrama unifilar do quadro"""
        doc = FreeCAD.ActiveDocument
        
        # 1. Criar uma pasta para o diagrama
        group = doc.addObject("App::DocumentObjectGroup", f"Diagrama_{panel_obj.Label}")
        
        # 2. Desenhar o Barramento (Linha horizontal)
        busbar = Draft.make_line(FreeCAD.Vector(0,0,0), FreeCAD.Vector(100,0,0))
        group.addObject(busbar)
        
        # 3. Desenhar os Circuitos (Linhas verticais + Simbolos)
        # (Aqui iterariamos sobre os circuitos vinculados ao quadro)
        
        # 4. Criar a Pagina TechDraw (se nao existir)
        page = doc.getObject("Folha_Diagramas")
        if not page:
            page = doc.addObject("TechDraw::DrawPage", "Folha_Diagramas")
            template = doc.addObject("TechDraw::DrawSVGTemplate", "Template")
            template.Template = "/usr/share/freecad/Mod/TechDraw/Templates/A3_Landscape_ISO7200TD.svg"
            page.Template = template
            
        # 5. Criar a Vista do Diagrama
        view = doc.addObject("TechDraw::DrawViewDraft", f"Vista_{panel_obj.Label}")
        view.Source = group
        page.addView(view)
        
        doc.recompute()
        return True

    @staticmethod
    def sync_title_block(page_obj):
        """Preenche o carimbo da folha com os metadados do projeto"""
        from EletricaLogic.Settings import ProjectSettings
        settings = ProjectSettings.get_settings_obj()
        
        # Mapeamento de campos comuns em templates SVG do TechDraw
        # (Depende dos IDs definidos no SVG do template)
        fields = {
            "FreeCAD_Title": settings.Cliente,
            "FreeCAD_Author": settings.ResponsavelTecnico,
            "FreeCAD_Date": "12/05/2026",
            "FreeCAD_Project": "Projeto Elétrico BIM"
        }
        
        for field, value in fields.items():
            try:
                page_obj.setAnnotation(field, value)
            except:
                pass
            
        FreeCAD.ActiveDocument.recompute()
        return True
