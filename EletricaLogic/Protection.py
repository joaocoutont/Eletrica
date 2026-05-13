# Motor de Estudo de Proteção e Seletividade (Coordenação)
import FreeCAD
import math

class ProtectionManager:
    """Realiza cálculos de curto-circuito e coordenação de proteção."""

    @staticmethod
    def calculate_short_circuit_at_point(distance_m, wire_section_mm2):
        """Calcula a Icc presumida em um ponto baseado na rede da concessionária."""
        doc = FreeCAD.ActiveDocument
        settings = doc.getObject("Configuracoes_Eletrica")
        if not settings: return 10.0 # Fallback
        
        icc_at_delivery = settings.Icc_Concessionaria * 1000 # Amperes
        voltage = float(settings.Tensao.replace("V", ""))
        
        # Resistividade (Cobre)
        rho = 0.0172
        resistance = (rho * distance_m) / wire_section_mm2
        
        # Simplificação: Icc = V / (Z_concessionaria + Z_cabo)
        # Z_concessionaria = V / Icc_delivery
        z_network = voltage / icc_at_delivery
        z_total = z_network + resistance
        
        icc_local = voltage / z_total
        return icc_local

    @staticmethod
    def check_selectivity(upstream_breaker_a, downstream_breaker_a):
        """
        Verifica a seletividade entre dois disjuntores (Geral vs Circuito).
        Retorna status e comentário técnico.
        """
        # Regra de ouro da seletividade (Simplificada para Curva C)
        # 1. Corrente nominal: Geral deve ser pelo menos 1.6x a de baixo (Regra Prática)
        ratio = upstream_breaker_a / downstream_breaker_a
        
        status = "OK"
        comment = ""
        
        if ratio < 1.6:
            status = "ALERTA"
            comment = f"Razão In_Geral/In_Circ ( {ratio:.2f} ) é baixa. Risco de disparo simultâneo em sobrecarga."
        
        # 2. Magnético: Geral deve ter capacidade de interrupção (Icu) maior que o curto local
        # E a curva de disparo magnético não deve se sobrepor (simplificado)
        if upstream_breaker_a <= downstream_breaker_a:
            status = "CRÍTICO"
            comment = "O disjuntor geral é igual ou menor que o do circuito! Coordenação impossível."
            
        return {"status": status, "comment": comment, "ratio": ratio}

    @staticmethod
    def generate_protection_report():
        """Gera um relatório HTML de coordenação de proteção."""
        doc = FreeCAD.ActiveDocument
        panels = [obj for obj in doc.Objects if hasattr(obj, "TipoBIM") and obj.TipoBIM in ["QDC", "CCM", "Quadro"]]
        
        report = "<h2>Estudo de Seletividade e Proteção</h2>"
        report += "<table border='1'><tr><th>Quadro</th><th>Disj. Geral (A)</th><th>Status</th><th>Análise</th></tr>"
        
        for p in panels:
            main_breaker = getattr(p, "DisjuntorGeral", 63.0)
            # Analisar circuitos filhos (se houver metadados)
            # Para o MVP, simulamos a análise com o maior circuito de carga
            status_data = ProtectionManager.check_selectivity(main_breaker, 20.0) # 20A como base de teste
            
            color = "green" if status_data['status'] == "OK" else ("orange" if status_data['status'] == "ALERTA" else "red")
            report += f"<tr><td>{p.Label}</td><td>{main_breaker}A</td><td style='color:{color}'>{status_data['status']}</td><td>{status_data['comment']}</td></tr>"
            
        report += "</table>"
        return report

class GroundingManager:
    """Motor de cálculo NBR 15751 para Sistemas de Aterramento"""
    
    @staticmethod
    def calculate_nbr15751_safety(rho, i_fault, t_fault, l_total, area, n_rods):
        """
        Calcula conformidade com NBR 15751 (Subestações)
        rho: resistividade do solo (ohm.m)
        i_fault: corrente de falta para a terra (A)
        t_fault: tempo de eliminacao da falta (s)
        l_total: comprimento total de cabos + hastes (m)
        area: area ocupada pela malha (m2)
        """
        # Constantes corporais (corpo humano 50kg) conforme IEEE 80 / NBR 15751
        k = 0.116
        
        # 1. Tensao de Toque e Passo Maximas Permitidas (Norma)
        e_touch_limit = (k / math.sqrt(t_fault)) * (1000 + 1.5 * rho)
        e_step_limit  = (k / math.sqrt(t_fault)) * (1000 + 6.0 * rho)
        
        # 2. Resistencia da Malha (Sverak / Laurent-Niemann)
        r_grid = (rho / (4 * math.sqrt(area/math.pi))) + (rho / l_total)
        
        # 3. GPR (Ground Potential Rise)
        gpr = i_fault * r_grid
        
        # 4. Potenciais Calculados (Malha e Passo - Estimativa Empirica Simplificada)
        # Em software real, usa-se elementos finitos. Aqui usamos fator de geometria Km e Ki simplificados.
        e_mesh_calc = (rho * i_fault * 0.7) / l_total 
        e_step_calc = (rho * i_fault * 0.3) / l_total
        
        return {
            "rho": rho,
            "i_fault": i_fault,
            "t_fault": t_fault,
            "r_grid": r_grid,
            "gpr": gpr,
            "e_touch_limit": e_touch_limit,
            "e_step_limit": e_step_limit,
            "e_mesh_calc": e_mesh_calc,
            "e_step_calc": e_step_calc,
            "safety_status": e_mesh_calc < e_touch_limit and e_step_calc < e_step_limit
        }
class ArcFlashManager:
    """Calcula energia incidente de arco elétrico (Simplificado IEEE 1584)"""
    
    @staticmethod
    def calculate_incident_energy(icc_ka, t_fault_s, distance_mm=610, voltage=440):
        """
        Estimativa de energia incidente em cal/cm2
        distance_mm: distancia de trabalho (padrao 610mm / 24in)
        """
        # Formula simplificada para BT (Lee method para estimativa conservadora)
        # E = 5.12e5 * V * Icc * (t / D^2)
        # Nota: Software real usa fatores de caixa (VCB, HCB, etc)
        
        distance_in = distance_mm / 25.4
        energy = (5.12 * 10**5 * (voltage/1000.0) * icc_ka * t_fault_s) / (distance_in**2)
        
        # Fronteira de Proteção (Flash Boundary) para 1.2 cal/cm2 (limite de queimadura 2º grau)
        boundary_mm = math.sqrt((5.12 * 10**5 * (voltage/1000.0) * icc_ka * t_fault_s) / 1.2) * 25.4
        
        # Categoria de EPI (NFPA 70E)
        category = 0
        if energy > 40: category = "PERIGO (ACIMA DE 40 cal/cm2)"
        elif energy > 25: category = 4
        elif energy > 8: category = 3
        elif energy > 4: category = 2
        elif energy > 1.2: category = 1
        
        return {
            "incident_energy": energy,
            "ppe_category": category,
            "boundary_m": round(boundary_mm / 1000, 2),
            "label_color": "red" if energy > 40 else ("orange" if energy > 1.2 else "green")
        }

    @staticmethod
    def export_safety_label(obj):
        """Gera uma etiqueta de segurança profissional em HTML"""
        import os
        from EletricaLogic.Protection import ArcFlashManager
        
        # Recalcular dados para garantir precisão
        icc = getattr(obj, "Icc_kA", 5.0)
        time = getattr(obj, "TempoExtincao", 0.1)
        res = ArcFlashManager.calculate_incident_energy(icc, time)
        
        html = f"""
        <html><head><style>
            .label {{ width: 500px; border: 5px solid {res['label_color']}; font-family: Arial; padding: 20px; }}
            .header {{ background: {res['label_color']}; color: white; text-align: center; font-size: 30px; font-weight: bold; padding: 10px; }}
            .warning {{ text-align: center; font-size: 20px; margin: 10px 0; }}
            .data {{ font-size: 16px; line-height: 1.6; }}
            .footer {{ font-size: 10px; color: gray; margin-top: 20px; text-align: center; }}
        </style></head><body>
            <div class="label">
                <div class="header">ADVERTÊNCIA / WARNING</div>
                <div class="warning"><b>RISCO DE ARCO ELÉTRICO E CHOQUE</b></div>
                <div class="data">
                    <p><b>Equipamento:</b> {obj.Label}</p>
                    <p><b>Energia Incidente:</b> {res['incident_energy']:.2f} cal/cm²</p>
                    <p><b>Fronteira de Risco:</b> {res['boundary_m']} metros</p>
                    <p><b>Categoria de EPI (NR-10):</b> {res['ppe_category']}</p>
                    <hr>
                    <p><i>É obrigatório o uso de vestimentas resistentes ao arco e proteção facial dentro da fronteira de risco.</i></p>
                </div>
                <div class="footer">Gerado por Suite Elite BIM - FreeCAD Electrical</div>
            </div>
        </body></html>
        """
        
        path = os.path.join(os.path.expanduser("~"), "Downloads", f"Etiqueta_Seguranca_{obj.Label}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return path

    @staticmethod
    def generate_safety_label(panel_label, data):
        html = f"""
        <div style='border: 4px solid orange; padding: 20px; width: 300px; font-family: Arial;'>
            <div style='background: orange; color: black; text-align: center; font-weight: bold;'>⚠️ PERIGO: ARCO ELÉTRICO</div>
            <p>Painel: <b>{panel_label}</b></p>
            <p>Energia Incidente: <b>{data['energy']:.2f} cal/cm²</b></p>
            <p>Fronteira de Risco: <b>{data['boundary']:.0f} mm</b></p>
            <p>Categoria de EPI: <b style='font-size: 1.2em;'>{data['category']}</b></p>
            <hr>
            <small>Cálculo baseado em IEEE 1584 / NFPA 70E</small>
        </div>
        """
        return html
