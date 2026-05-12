# Analise de Risco SPDA conforme NBR 5419-2
import math

class SPDARiskManager:
    @staticmethod
    def calculate_risk(data):
        """
        Analise simplificada de risco.
        data: {length, width, height, ng, factor_location, factor_structure}
        """
        # 1. Area de exposicao equivalente (Ae)
        # Ae = (L*W) + 6*H*(L+W) + 9*PI*H^2
        l, w, h = data['length'], data['width'], data['height']
        ae = (l * w) + (6 * h * (l + w)) + (9 * math.pi * (h**2))
        
        # 2. Frequencia de raios na estrutura (Nd)
        # Nd = Ng * Ae * Cd * 10^-6
        ng = data['ng'] # Densidade de raios local
        cd = data['factor_location'] # Fator de localizacao (ex: 1.0 para isolado)
        nd = ng * ae * cd * 1e-6
        
        # 3. Risco (Simplificado para o Wizard)
        # Se Nd for maior que o risco toleravel (geralmente 10^-5 para perda de vida humana)
        tolerable_risk = 1e-5
        risk_result = nd * data['factor_structure']
        
        required = risk_result > tolerable_risk
        
        return {
            "Nd": nd,
            "Risk": risk_result,
            "Required": required,
            "Level": SPDARiskManager.suggest_level(risk_result)
        }

    @staticmethod
    def suggest_level(risk):
        if risk > 1e-3: return "Nivel I (Maximo)"
        if risk > 1e-4: return "Nivel II"
        if risk > 1e-5: return "Nivel III"
        return "Nivel IV"
