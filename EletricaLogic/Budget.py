# Gestor de Orcamentos e Precos
import FreeCAD
import os

class BudgetManager:
    @staticmethod
    def generate_budget_report(bom_data):
        """
        Gera um relatório de custos baseados nos itens do BOM.
        """
        # Exemplo de precos (Poderia ser carregado de um CSV externo)
        prices = {
            "Tomada_TUG": 15.00,
            "Disjuntor_10A": 12.50,
            "Disjuntor_20A": 18.00,
            "Eletroduto_PVC_25": 4.50, # por metro
            "Cabo_2.5mm2": 3.20, # por metro
            "Curva_Horizontal_90": 25.00,
            "Suporte_Mao_Francesa": 45.00
        }
        
        total_cost = 0.0
        report = ["--- ORÇAMENTO ESTIMADO DE MATERIAIS ---"]
        
        for item, qty in bom_data.items():
            price = prices.get(item, 0.0)
            if price == 0.0:
                # Tenta busca parcial (ex: Eletroduto_PVC_Cinza)
                for key in prices:
                    if key in item:
                        price = prices[key]
                        break
            
            subtotal = qty * price
            total_cost += subtotal
            report.append(f"{item}: {qty} un/m x R$ {price:.2f} = R$ {subtotal:.2f}")
            
        report.append("\n========================================")
        report.append(f"TOTAL ESTIMADO: R$ {total_cost:.2f}")
        report.append("========================================")
        
        return "\n".join(report)
