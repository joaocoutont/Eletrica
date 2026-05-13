# Gestor de Orcamentos e Precos
import FreeCAD
import os
import csv
import json

class BudgetManager:
    # Preços padrão para fallback
    DEFAULT_PRICES = {
        "Tomada": 15.00,
        "Interruptor": 12.00,
        "Luminaria": 45.00,
        "Disjuntor": 18.00,
        "Eletroduto": 4.50,
        "Cabo": 3.20,
        "Quadro": 150.00,
        "Motor": 1200.00,
        "Haste": 35.00
    }

    @staticmethod
    def load_prices():
        """
        Carrega preços de JSON ou CSV na pasta do projeto.
        """
        prices = BudgetManager.DEFAULT_PRICES.copy()
        doc = FreeCAD.ActiveDocument
        if not doc or not doc.FileName:
            return prices

        # 1. Tentar JSON (Prioridade)
        json_path = os.path.join(os.path.dirname(doc.FileName), "precos.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    prices.update(json.load(f))
                    return prices
            except: pass

        # 2. Tentar CSV
        csv_path = os.path.join(os.path.dirname(doc.FileName), "precos_eletrica.csv")
        if os.path.exists(csv_path):
            try:
                with open(csv_path, mode='r', encoding='utf-8') as f:
                    # Detecta delimitador (vírgula ou ponto-e-vírgula)
                    content = f.read(1024); f.seek(0)
                    dialect = csv.Sniffer().sniff(content, delimiters=',;')
                    reader = csv.reader(f, dialect)
                    for row in reader:
                        if len(row) >= 2:
                            item, price = row[0], row[1]
                            try:
                                prices[item] = float(price.replace(',', '.'))
                            except: continue
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Budget: Erro ao ler CSV ({e}). Usando padrões.\n")
        
        return prices

    @staticmethod
    def generate_budget_report(bom_data):
        """
        Gera um relatório de custos baseados nos itens do BOM.
        """
        prices = BudgetManager.load_prices()
        
        total_cost = 0.0
        report = ["--- ORÇAMENTO ESTIMADO DE MATERIAIS ---"]
        report.append(f"Projeto: {FreeCAD.ActiveDocument.Name if FreeCAD.ActiveDocument else 'Sem Nome'}\n")
        
        for item, qty in bom_data.items():
            price = 0.0
            found = False
            
            # Busca inteligente (exata depois parcial)
            if item in prices:
                price = prices[item]
                found = True
            else:
                for key in prices:
                    if key.lower() in item.lower():
                        price = prices[key]
                        found = True
                        break
            
            subtotal = qty * price
            total_cost += subtotal
            status = "" if found else " (⚠️ s/ preço)"
            report.append(f"{item}: {qty:.2f} x R$ {price:.2f} = R$ {subtotal:.2f}{status}")
            
        report.append("\n" + "="*40)
        report.append(f"TOTAL ESTIMADO: R$ {total_cost:.2f}")
        report.append("="*40)
        
        return "\n".join(report), total_cost
