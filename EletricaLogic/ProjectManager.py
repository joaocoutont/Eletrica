# Gestor de Projetos Multi-Documento (Master Project Manager)
import FreeCAD

class MultiDocumentManager:
    """
    Agrega dados de múltiplos arquivos .FCStd para gerar documentação consolidada.
    Útil para prédios com pavimentos em arquivos separados.
    """

    @staticmethod
    def get_all_electrical_documents():
        """Retorna todos os documentos abertos que possuem dados da bancada Eletrica."""
        docs = []
        for doc in FreeCAD.listDocuments().values():
            if doc.getObject("Eletrica_ProjectData") or any(hasattr(obj, "Potencia") for obj in doc.Objects):
                docs.append(doc)
        return docs

    @staticmethod
    def aggregate_load_data():
        """Calcula a carga total instalada somando todos os documentos abertos."""
        total_va = 0.0
        docs = MultiDocumentManager.get_all_electrical_documents()
        
        summary = {} # {DocumentName: VA}
        
        for doc in docs:
            doc_va = 0.0
            for obj in doc.Objects:
                if hasattr(obj, "Potencia"):
                    doc_va += float(obj.Potencia)
            summary[doc.Name] = doc_va
            total_va += doc_va
            
        return total_va, summary

    @staticmethod
    def generate_master_bom():
        """Gera uma Lista de Materiais consolidada de todos os pavimentos/documentos."""
        master_bom = {} # {Item: Qtd}
        docs = MultiDocumentManager.get_all_electrical_documents()
        
        for doc in docs:
            for obj in doc.Objects:
                # Componentes
                if hasattr(obj, "Potencia") and not obj.Label.startswith("Simbolo_"):
                    name = obj.Label.split('_')[0]
                    master_bom[name] = master_bom.get(name, 0) + 1
                
                # Infraestrutura
                if hasattr(obj, "Diameter") and hasattr(obj, "Shape"):
                    diam = f"Eletroduto {obj.Diameter}mm"
                    length = obj.Shape.Length / 1000.0 # metros
                    master_bom[diam] = master_bom.get(diam, 0.0) + length
                    
        return master_bom

    @staticmethod
    def sync_project_metadata(master_doc):
        """Sincroniza os metadados (RT, CREA, ART) do documento mestre para todos os outros."""
        master_meta = master_doc.getObject("Eletrica_ProjectData")
        if not master_meta: return
        
        props = ["DesignerName", "CREA", "ART", "Utility", "Voltage"]
        docs = MultiDocumentManager.get_all_electrical_documents()
        
        updated = 0
        for doc in docs:
            if doc == master_doc: continue
            
            target_meta = doc.getObject("Eletrica_ProjectData")
            if not target_meta: continue
            
            for p in props:
                if hasattr(master_meta, p) and hasattr(target_meta, p):
                    setattr(target_meta, p, getattr(master_meta, p))
            updated += 1
            
        FreeCAD.Console.PrintMessage(f"Projeto: Metadados sincronizados em {updated} documentos.\n")
        return updated
