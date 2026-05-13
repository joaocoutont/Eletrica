# Lógica de Proteção e Segurança - NBR 5410
import FreeCAD

class SafetyManager:
    """
    Especialista em Proteção (DR, DPS, Aterramento).
    """

    @staticmethod
    def analyze_protection_needs():
        """
        Analisa o projeto e sugere proteções DR e DPS.
        """
        doc = FreeCAD.ActiveDocument
        if not doc: return {}

        results = {
            "DR_Required": [],
            "DPS_Recommendation": "Classe II (Quadro Geral)",
            "Grounding_Check": "OK"
        }

        # 1. Analisar necessidade de DR (Áreas Molhadas / Tomadas Externas)
        wet_keywords = ["Cozinha", "Banheiro", "Lavanderia", "Area", "Externo", "Chuveiro", "Piscina", "Jardim"]
        
        for obj in doc.Objects:
            if hasattr(obj, "Circuito"):
                c_name = obj.Circuito
                if any(kw.lower() in c_name.lower() for kw in wet_keywords):
                    if c_name not in results["DR_Required"]:
                        results["DR_Required"].append(c_name)

        # 2. Analisar DPS baseado no ProjectData
        meta = doc.getObject("Eletrica_ProjectData")
        if meta:
            p_type = getattr(meta, "ProjectType", "Residencial")
            if p_type == "Industrial" or getattr(meta, "SPDARequired", False):
                results["DPS_Recommendation"] = "Classe I + II (Entrada)"
        
        return results

    @staticmethod
    def apply_protections_to_panels():
        """
        Aplica as recomendações de proteção aos objetos de Quadro (Panels).
        """
        doc = FreeCAD.ActiveDocument
        needs = SafetyManager.analyze_protection_needs()
        
        panels = [o for o in doc.Objects if hasattr(o, "TipoBIM") and o.TipoBIM == "Quadro"]
        
        for p in panels:
            if not hasattr(p, "PossuiDR"):
                p.addProperty("App::PropertyBool", "PossuiDR", "Proteção", "Se possui IDR")
            if not hasattr(p, "PossuiDPS"):
                p.addProperty("App::PropertyBool", "PossuiDPS", "Proteção", "Se possui DPS")
            
            # Sugestão inteligente
            if needs["DR_Required"]:
                p.PossuiDR = True
            
            if "Classe I" in needs["DPS_Recommendation"]:
                p.PossuiDPS = True
        
        return needs
