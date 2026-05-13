# Gerador de Diagramas Unifilares Graficos (TechDraw)
import FreeCAD
import Draft
import TechDraw
import os

class UnifilarGenerator:
    """
    Gera diagramas unifilares automáticos integrados ao TechDraw.
    """

    @staticmethod
    def create_graphic_diagram(panel_obj):
        """Gera o desenho tecnico do diagrama unifilar do quadro com dados reais"""
        doc = FreeCAD.ActiveDocument
        if not doc: return False
        
        # 1. Criar uma pasta para o diagrama
        group_name = f"Diagrama_{panel_obj.Label}"
        if doc.getObject(group_name):
            doc.removeObject(group_name)
        group = doc.addObject("App::DocumentObjectGroup", group_name)
        
        # 2. Desenhar o Barramento Principal
        bus_length = 250
        busbar = Draft.make_line(FreeCAD.Vector(0,0,0), FreeCAD.Vector(bus_length, 0, 0))
        busbar.Label = "Barramento_Principal"
        busbar.ViewObject.LineWidth = 3.0
        group.addObject(busbar)
        
        # 3. Coletar Circuitos vinculados (Garante dados do Circuits.py)
        circuits_data = {}
        for obj in doc.Objects:
            if hasattr(obj, "Circuito") and getattr(obj, "QuadroVinculado", None) == panel_obj:
                c_id = obj.Circuito
                if c_id not in circuits_data:
                    circuits_data[c_id] = {
                        "power": 0.0,
                        "breaker": getattr(obj, "Disjuntor", 20),
                        "wire": getattr(obj, "SecaoCabo", 2.5),
                        "label": obj.Label
                    }
                circuits_data[c_id]["power"] += float(obj.Potencia)

        # 4. Desenhar os Circuitos (Derivações)
        spacing = 25
        x_pos = 15
        for c_id, data in sorted(circuits_data.items()):
            # Linha de derivação
            derivation = Draft.make_line(FreeCAD.Vector(x_pos, 0, 0), FreeCAD.Vector(x_pos, -40, 0))
            group.addObject(derivation)
            
            # Símbolo de Disjuntor NBR (Chave com proteção térmica)
            # Desenha uma pequena linha inclinada para representar o contato
            breaker_line = Draft.make_line(FreeCAD.Vector(x_pos, -10, 0), FreeCAD.Vector(x_pos + 5, -20, 0))
            group.addObject(breaker_line)
            
            # Texto Técnico (Vertical ou Horizontal abaixo)
            info_str = f"{c_id}\n{data['power']:.0f}VA\n{data['breaker']}A\n{data['wire']}mm²"
            txt = Draft.make_text(info_str, placement=FreeCAD.Vector(x_pos - 5, -65, 0))
            group.addObject(txt)
            
            x_pos += spacing
            if x_pos > bus_length - 15: break 
            
        # 5. Criar/Configurar Pagina TechDraw
        page_name = "Folha_Diagramas_Unifilares"
        page = doc.getObject(page_name)
        if not page:
            page = doc.addObject("TechDraw::DrawPage", page_name)
            template = doc.addObject("TechDraw::DrawSVGTemplate", "Template_Diagrama")
            # Usa template padrão do FreeCAD
            template.Template = os.path.join(FreeCAD.getResourceDir(), "Mod", "TechDraw", "Templates", "A3_Landscape_ISO7200_NC.svg")
            page.Template = template
            
        # 6. Preencher Carimbo (Sincronização)
        UnifilarGenerator.sync_title_block(page)

        # 7. Criar a Vista
        view_name = f"Vista_{panel_obj.Label}"
        if doc.getObject(view_name): doc.removeObject(view_name)
        
        view = doc.addObject("TechDraw::DrawViewDraft", view_name)
        view.Source = group
        page.addView(view)
        view.X = 150
        view.Y = 150
        
        doc.recompute()
        FreeCAD.Console.PrintMessage(f"Diagrama Unifilar de '{panel_obj.Label}' gerado com sucesso!\n")
        return True

    @staticmethod
    def sync_title_block(page_obj=None):
        """Preenche o carimbo da folha com os metadados do projeto"""
        doc = FreeCAD.ActiveDocument
        meta = doc.getObject("Eletrica_ProjectData")
        if not meta: return False
        
        # Se não passar uma página específica, procura a primeira disponível
        if not page_obj:
            pages = doc.findObjects("TechDraw::DrawPage")
            if pages:
                page_obj = pages[0]
            else:
                return False

        # Mapeamento de campos padrão do FreeCAD (SVG IDs comuns)
        # 'FreeCAD_Title', 'FreeCAD_Author', etc são os IDs internos do template A3 padrão
        texts = page_obj.EditableTexts
        
        # Tenta preencher os campos conhecidos
        if "FreeCAD_Title" in texts: texts["FreeCAD_Title"] = getattr(meta, "ProjectName", "Projeto Elétrico")
        if "FreeCAD_Author" in texts: texts["FreeCAD_Author"] = getattr(meta, "DesignerName", "Eletrica")
        if "FreeCAD_Project" in texts: texts["FreeCAD_Project"] = f"{getattr(meta, 'ProjectType', 'Residencial')} - {getattr(meta, 'Phase', 'Executivo')}"
        if "FreeCAD_Date" in texts:
            import datetime
            texts["FreeCAD_Date"] = datetime.date.today().strftime("%d/%m/%Y")
            
        page_obj.EditableTexts = texts
        
        FreeCAD.Console.PrintMessage(f"TechDraw: Carimbo de '{page_obj.Label}' sincronizado com sucesso!\n")
        doc.recompute()
        return True
