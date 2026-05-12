# Exportador Seletivo por Disciplina (BIM Multi-Export)
import FreeCAD
import ImportGui

class DisciplineExporter:
    @staticmethod
    def export_by_discipline(discipline, file_path):
        """
        Exporta apenas os objetos pertencentes a uma disciplina especifica.
        """
        doc = FreeCAD.ActiveDocument
        export_list = []
        
        # Filtros baseados nas propriedades dos objetos
        for obj in doc.Objects:
            is_match = False
            
            if discipline == "Elétrica":
                if hasattr(obj, "TipoBIM") and obj.TipoBIM in ["QDC", "CCM", "CCA", "Tomada", "Luminaria", "Eletroduto"]:
                    is_match = True
            elif discipline == "SPDA":
                if "SPDA" in obj.Label or (hasattr(obj, "TipoBIM") and "SPDA" in str(obj.TipoBIM)):
                    is_match = True
            elif discipline == "Fotovoltaico":
                if "Solar" in obj.Label or "Painel" in obj.Label or "Inversor" in obj.Label:
                    is_match = True
            
            if is_match:
                export_list.append(obj)
        
        if export_list:
            # Exportar para IFC ou STEP conforme extensao
            if file_path.lower().endswith(".ifc"):
                import ArchIFC
                ArchIFC.export(export_list, file_path)
            else:
                ImportGui.export(export_list, file_path)
            return len(export_list)
        return 0

    @staticmethod
    def run_multi_export(base_path):
        """Executa a exportacao de todas as disciplinas em arquivos separados"""
        results = {}
        for disc in ["Elétrica", "SPDA", "Fotovoltaico"]:
            path = f"{base_path}_{disc}.ifc"
            count = DisciplineExporter.export_by_discipline(disc, path)
            results[disc] = count
        return results
