# Auditoria de Projeto (Check-list de Erros)
import FreeCAD

class ProjectAuditor:
    @staticmethod
    def run_full_audit():
        """Varre o projeto em busca de inconsistencias tecnicas"""
        doc = FreeCAD.ActiveDocument
        errors = []
        warnings = []
        
        # 1. Verificar Pontos sem Circuito ou sem Quadro
        for obj in doc.Objects:
            if hasattr(obj, "Potencia"):
                if not hasattr(obj, "Circuito") or obj.Circuito == "Geral":
                    warnings.append(f"Objeto [{obj.Label}] sem circuito definido.")
                if not hasattr(obj, "QuadroVinculado") or obj.QuadroVinculado is None:
                    errors.append(f"Objeto [{obj.Label}] nao esta vinculado a nenhum Quadro (QDC).")
        
        # 2. Verificar Eletrodutos Vazios ou Superlotados
        for obj in doc.Objects:
            if hasattr(obj, "TaxaOcupacao"):
                if not obj.CircuitosPassantes:
                    warnings.append(f"Eletroduto [{obj.Label}] esta vazio (sem circuitos).")
                if obj.TaxaOcupacao > 40.0:
                    errors.append(f"Eletroduto [{obj.Label}] esta com ocupacao critica ({round(obj.TaxaOcupacao, 2)}%).")
        
        # 3. Verificar Colisoes (Clash Detection)
        conduits = [o for o in doc.Objects if hasattr(o, "TaxaOcupacao")]
        for i in range(len(conduits)):
            for j in range(i + 1, len(conduits)):
                bb1 = conduits[i].Shape.BoundBox
                bb2 = conduits[j].Shape.BoundBox
                if bb1.intersect(bb2):
                    # Verificacao mais fina se necessário, ou apenas avisar
                    warnings.append(f"Possivel colisao entre {conduits[i].Label} e {conduits[j].Label}")
                    # Destacar no 3D
                    conduits[i].ViewObject.ShapeColor = (1.0, 0.5, 0.0)
                    conduits[j].ViewObject.ShapeColor = (1.0, 0.5, 0.0)
        
        return {
            "Errors": errors,
            "Warnings": warnings
        }
