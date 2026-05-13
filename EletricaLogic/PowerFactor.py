# Motor de Cálculo de Fator de Potência e Reativos
import FreeCAD
import math

class PowerFactorManager:
    """Calcula potências ativa/reativa e dimensiona bancos de capacitores."""

    @staticmethod
    def calculate_total_loads():
        """Soma P, Q e S de todos os componentes do documento."""
        doc = FreeCAD.ActiveDocument
        p_total = 0.0 # Watts
        q_total = 0.0 # VAr
        
        for obj in doc.Objects:
            if hasattr(obj, "Potencia"):
                p = getattr(obj, "Potencia", 0.0)
                fp = getattr(obj, "FatorPotencia", 0.95)
                
                # S = P / FP
                # Q = sqrt(S^2 - P^2) -> ou Q = P * tan(acos(FP))
                phi = math.acos(max(0.1, min(1.0, fp)))
                q = p * math.tan(phi)
                
                p_total += p
                q_total += q
        
        s_total = math.sqrt(p_total**2 + q_total**2)
        fp_global = p_total / s_total if s_total > 0 else 1.0
        
        return {
            "p_kw": p_total / 1000.0,
            "q_kvar": q_total / 1000.0,
            "s_kva": s_total / 1000.0,
            "fp": fp_global
        }

    @staticmethod
    def dimension_capacitor_bank(target_fp=0.95):
        """Calcula a potência necessária do banco de capacitores (kVAr)."""
        current = PowerFactorManager.calculate_total_loads()
        p_kw = current["p_kw"]
        q_current = current["q_kvar"]
        
        if current["fp"] >= target_fp:
            return {"needed_kvar": 0.0, "status": "FP ja esta no alvo"}
            
        # Q_alvo = P * tan(acos(FP_alvo))
        phi_target = math.acos(target_fp)
        q_target = p_kw * math.tan(phi_target)
        
        needed_kvar = q_current - q_target
        
        # Sugestão de estágios (simplificada)
        stages = []
        if needed_kvar > 50:
            stages = [needed_kvar/4] * 4
        elif needed_kvar > 0:
            stages = [needed_kvar]
            
        return {
            "current_fp": current["fp"],
            "needed_kvar": needed_kvar,
            "p_kw": p_kw,
            "stages": stages
        }
