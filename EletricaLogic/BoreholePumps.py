# Gerenciador de Bombas de Poco Submersas (Ebara)
import FreeCAD

class BoreholePumpManager:
    @staticmethod
    def get_ebara_models():
        """Modelos comuns da Ebara (Simplificado)"""
        return {
            "4BPS (4 Polegadas)": {"Potencia_CV": [0.5, 1.0, 2.0, 3.0, 5.0, 7.5]},
            "6BPS (6 Polegadas)": {"Potencia_CV": [5.0, 7.5, 10.0, 15.0, 20.0, 30.0]}
        }

    @staticmethod
    def calculate_deep_voltage_drop(cv, voltage, depth_m, horizontal_m=20):
        """Calcula a bitola necessaria para garantir <3% de queda em profundidade"""
        # Corrente aproximada (380V)
        amps = cv * 2.0 # Regra de bolso simplificada para 380V
        total_dist = depth_m + horizontal_m
        
        # Bitolas disponiveis
        gauges = [2.5, 4, 6, 10, 16, 25, 35, 50]
        selected_gauge = 2.5
        
        for g in gauges:
            # Formula simplificada: dV% = (2 * L * I) / (56 * S * V)
            drop = (2 * total_dist * amps) / (56 * g * voltage) * 100
            if drop <= 3.0:
                selected_gauge = g
                break
        
        return selected_gauge, drop

    @staticmethod
    def insert_ebara_pump(model, cv, depth):
        """Insere a bomba Ebara no projeto BIM"""
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("App::FeaturePython", f"Bomba_Ebara_{cv}CV")
        obj.Label = f"Bomba_Poco_Ebara_{cv}CV_{depth}m"
        
        # Propriedades de Poco
        obj.addProperty("App::PropertyFloat", "Profundidade_m", "Poço").Profundidade_m = depth
        obj.addProperty("App::PropertyFloat", "Potencia_CV", "Elétrica").Potencia_CV = cv
        obj.addProperty("App::PropertyString", "Modelo_Ebara", "BIM").Modelo_Ebara = model
        
        # Dimensionamento de Cabo
        gauge, drop = BoreholePumpManager.calculate_deep_voltage_drop(cv, 380, depth)
        obj.addProperty("App::PropertyFloat", "CaboNecessario_mm2", "Dimensionamento").CaboNecessario_mm2 = gauge
        obj.addProperty("App::PropertyFloat", "QuedaTensaoCalculada", "Dimensionamento").QuedaTensaoCalculada = drop
        
        FreeCAD.ActiveDocument.recompute()
        return obj
 Broadway
