# Dimensionamento de Partidas de Motores (Padrão WEG) + Barramentos
import FreeCAD
import math

class StarterManager:

    # --- CATÁLOGO WEG EXPANDIDO (1 a 1000 CV) ---
    # Colunas: (cv_max, kw_max, in_380A, proteção, contator, soft-starter, inversor)
    # Proteções: MPW (até 100A), DWJ-Caixa Moldada (até 1600A), ACB-Aberto (acima)
    # Soft-Starters: SSW05→SSW900 (BT), SSW3000 (grande porte)
    # Inversores: CFW300→CFW700→CFW11 (todos BT até 1000 CV em 380V)
    WEG_TABLE = [
        # ---- BAIXA POTÊNCIA (até 10 CV) ----
        (1,     0.75,    2.0,  "MPW10",               "CWM9",       "SSW05",   "CFW300-B"),
        (2,     1.5,     3.5,  "MPW10",               "CWM9",       "SSW05",   "CFW300-B"),
        (3,     2.2,     5.0,  "MPW18",               "CWM9",       "SSW05",   "CFW300-B"),
        (5,     3.7,     8.0,  "MPW25",               "CWM9",       "SSW05",   "CFW300-B"),
        (7.5,   5.5,    11.5,  "MPW40",               "CWM18",      "SSW07",   "CFW500-B"),
        (10,    7.5,    15.5,  "MPW40",               "CWM18",      "SSW07",   "CFW500-B"),
        # ---- MÉDIA POTÊNCIA (15 a 75 CV) ----
        (15,   11.0,    22.0,  "MPW65",               "CWM32",      "SSW075",  "CFW500-B"),
        (20,   15.0,    28.5,  "MPW65",               "CWM32",      "SSW100",  "CFW700-B"),
        (25,   18.5,    35.0,  "MPW65",               "CWM50",      "SSW100",  "CFW700-B"),
        (30,   22.0,    41.0,  "MPW65",               "CWM50",      "SSW100",  "CFW700-B"),
        (40,   30.0,    55.0,  "MPW100",              "CWM65",      "SSW300",  "CFW11"),
        (50,   37.0,    68.0,  "MPW100",              "CWM80",      "SSW300",  "CFW11"),
        (60,   45.0,    82.0,  "MPW100",              "CWM105",     "SSW450",  "CFW11"),
        (75,   55.0,   102.0,  "MPW100",              "CWM105",     "SSW450",  "CFW11"),
        # ---- GRANDE POTÊNCIA BT (100 a 300 CV) - DWJ Caixa Moldada ----
        (100,  75.0,   136.0,  "DWJ 250A",            "CWM145",     "SSW900",  "CFW11"),
        (125,  93.0,   170.0,  "DWJ 250A",            "CWM145",     "SSW900",  "CFW11"),
        (150, 112.0,   203.0,  "DWJ 400A",            "CWM200",     "SSW900",  "CFW11"),
        (175, 132.0,   239.0,  "DWJ 400A",            "CWM200",     "SSW900",  "CFW11"),
        (200, 150.0,   272.0,  "DWJ 400A",            "CWM265",     "SSW900",  "CFW11"),
        (250, 187.0,   340.0,  "DWJ 630A",            "CWM265",     "SSW900",  "CFW11"),
        (300, 224.0,   405.0,  "DWJ 630A",            "CWM265",     "SSW900",  "CFW11"),
        # ---- ALTA POTÊNCIA BT (350 a 600 CV) - DWJ 800/1000 ----
        (350, 261.0,   472.0,  "DWJ 800A",            "CWM300",     "SSW900",  "CFW11"),
        (400, 298.0,   539.0,  "DWJ 800A",            "CWM300",     "SSW900",  "CFW11"),
        (500, 373.0,   675.0,  "DWJ 1000A",           "CWM300",     "SSW900",  "CFW11"),
        (600, 448.0,   810.0,  "DWJ 1000A",           "CWM300",     "SSW3000", "CFW11"),
        # ---- ALTÍSSIMA POTÊNCIA BT (700 a 1000 CV) - ACB Disjuntor Aberto ----
        (700, 522.0,   945.0,  "DWJ 1600A",           "CWM300",     "SSW3000", "CFW11"),
        (800, 597.0,  1080.0,  "ACB 2000A (Aberto)",  "Contator MV","SSW3000", "CFW11"),
        (900, 671.0,  1215.0,  "ACB 2000A (Aberto)",  "Contator MV","SSW3000", "CFW11"),
        (1000,746.0,  1350.0,  "ACB 2500A (Aberto)",  "Contator MV","SSW3000", "CFW11"),
    ]

    @staticmethod
    def get_row(cv):
        """Retorna a linha da tabela WEG para a potência informada."""
        for row in StarterManager.WEG_TABLE:
            if cv <= row[0]:
                return row
        return StarterManager.WEG_TABLE[-1]  # Maior disponível

    @staticmethod
    def get_nominal_current(cv, voltage=380, fp=0.87, eta=0.90):
        """Corrente nominal do motor (A) — fórmula IEC."""
        kw = cv * 0.7355
        return kw * 1000 / (math.sqrt(3) * voltage * fp * (eta/100.0 if eta > 1 else eta))

    @staticmethod
    def get_project_settings():
        """Recupera as configurações globais do projeto a partir do objeto Eletrica_ProjectData."""
        doc = FreeCAD.ActiveDocument
        if not doc: return {}
        meta = doc.getObject("Eletrica_ProjectData")
        if not meta: return {}
        
        return {
            'material':   getattr(meta, "ConductorMaterial", "Cobre (Cu)"),
            'insulation': getattr(meta, "InsulationType", "PVC (70°C)"),
            'ambient_t':  getattr(meta, "AmbientTemperature", 30),
            'method':     getattr(meta, "InstallationMethod", "B1")
        }

    @staticmethod
    def dimension_motor(cv, voltage=380, start_method="Direta", fs=1.0, fp=0.87, eta=0.90):
        """
        Dimensiona completamente uma partida de motor industrial.
        Retorna dicionário com todos os componentes e cabos.
        """
        row = StarterManager.get_row(cv)
        in_nom = StarterManager.get_nominal_current(cv, voltage, fp, eta)

        # Correntes de partida por método (múltiplo de In)
        start_multipliers = {
            "Direta":             6.0,
            "Estrela-Triângulo":  2.0,
            "Soft-Starter":       3.0,
            "Inversor de Frequência": 1.1,
        }
        mult = start_multipliers.get(start_method, 6.0)
        i_start = in_nom * mult

        # Relé de sobrecarga: ajustar In * FS
        relay_setting = round(in_nom * fs, 1)

        # Seção do cabo de força (Usa configurações do projeto)
        settings = StarterManager.get_project_settings()
        from EletricaLogic.Calculator import ElectricalCalculator
        
        cable = ElectricalCalculator.get_standard_wire_gauge(
            in_nom * 1.25, 
            method=settings.get('method', 'B1'),
            insulation=settings.get('insulation', 'PVC'),
            material=settings.get('material', 'Cu'),
            ambient_temp=settings.get('ambient_t', 30)
        )
        breaker = ElectricalCalculator.get_standard_breaker(in_nom * 1.25)

        # Componentes WEG
        weg = {
            "mpw":  row[3],
            "cwm":  row[4],
            "ssw":  row[5],
            "cfw":  row[6],
        }
        acionamento = {
            "Direta":             weg["cwm"],
            "Estrela-Triângulo":  f"3x {weg['cwm']} + Temporizador",
            "Soft-Starter":       weg["ssw"],
            "Inversor de Frequência": weg["cfw"],
        }.get(start_method, weg["cwm"])

        return {
            "cv": cv,
            "kw": round(cv * 0.7355, 2),
            "voltage": voltage,
            "start_method": start_method,
            "fs": fs,
            "fp": fp,
            "eta": eta,
            "in_nom_a": round(in_nom, 2),
            "i_start_a": round(i_start, 2),
            "relay_a": relay_setting,
            "cable_mm2": cable,
            "breaker_a": breaker,
            "protection": weg["mpw"],
            "contactor": acionamento,
        }

    @staticmethod
    def dimension_starter(obj):
        """Dimensiona a partida para um objeto Motor selecionado (legado)."""
        if not hasattr(obj, "Potencia_CV"): return None
        cv     = obj.Potencia_CV
        method = obj.TipoPartida if hasattr(obj, "TipoPartida") else "Direta"
        result = StarterManager.dimension_motor(cv, start_method=method)
        if not hasattr(obj, "KitPartida"):
            obj.addProperty("App::PropertyString", "KitPartida", "Engenharia").KitPartida = str(result)
        return result


class BusbarCalculator:
    """Dimensionamento de barramentos de cobre e alumínio."""

    # Capacidade de condução de corrente por mm² (A/mm²)
    # Valores conservadores para barramento nu ao ar (40°C)
    CURRENT_DENSITY = {
        "Cobre":     2.5,
        "Alumínio":  1.6,
    }

    STANDARD_BARS = {
        # (largura_mm, espessura_mm) -> área_mm²
        "Cobre": [
            (15, 3, 45), (20, 3, 60), (25, 3, 75), (25, 5, 125),
            (30, 5, 150), (40, 5, 200), (50, 5, 250), (60, 5, 300),
            (60, 10, 600), (80, 10, 800), (100, 10, 1000),
        ],
        "Alumínio": [
            (25, 4, 100), (30, 4, 120), (40, 4, 160), (50, 5, 250),
            (60, 5, 300), (80, 5, 400), (80, 10, 800), (100, 10, 1000),
        ],
    }

    @staticmethod
    def dimension_busbar(current_a, material="Cobre", phases=3):
        """
        Dimensiona o barramento para a corrente informada.
        Retorna o perfil comercial mínimo e dados de projeto.
        """
        density = BusbarCalculator.CURRENT_DENSITY.get(material, 2.5)
        min_area = current_a / density

        bars = BusbarCalculator.STANDARD_BARS.get(material, [])
        chosen = None
        for w, t, area in bars:
            if area >= min_area:
                chosen = (w, t, area)
                break

        if not chosen:
            chosen = bars[-1]  # Maior disponível

        cap = chosen[2] * density

        return {
            "current_a": round(current_a, 1),
            "material": material,
            "phases": phases,
            "min_area_mm2": round(min_area, 1),
            "bar_w_mm": chosen[0],
            "bar_t_mm": chosen[1],
            "bar_area_mm2": chosen[2],
            "bar_capacity_a": round(cap, 1),
            "weight_kg_m": round((chosen[2] / 1e6) * (8960 if material == "Cobre" else 2700), 3),
            "designation": f"{chosen[0]}x{chosen[1]}mm ({material})",
            "phases_desc": f"{phases}x {chosen[0]}x{chosen[1]}mm" + (" + Neutro" if phases == 3 else ""),
        }

class MotorDimensioning:
    """Lógica de dimensionamento de condutores e proteção para motores (Padrão WEG)"""
    
    # Tabela simplificada: CV -> Corrente (220V/380V) -> Cabo (mm2) -> Disjuntor (A)
    MOTOR_TABLE = {
        0.5:  {"i220": 2.1,  "i380": 1.2,  "cable": 1.5, "breaker": 6},
        1.0:  {"i220": 3.6,  "i380": 2.1,  "cable": 1.5, "breaker": 10},
        2.0:  {"i220": 6.8,  "i380": 3.9,  "cable": 2.5, "breaker": 16},
        5.0:  {"i220": 15.2, "i380": 8.8,  "cable": 4.0, "breaker": 25},
        10.0: {"i220": 28.0, "i380": 16.2, "cable": 6.0, "breaker": 40},
        20.0: {"i220": 54.0, "i380": 31.0, "cable": 16.0, "breaker": 63},
        50.0: {"i220": 130.0, "i380": 75.0, "cable": 35.0, "breaker": 100}
    }

    @staticmethod
    def get_sizing(cv, voltage, method):
        """Retorna dimensionamento completo"""
        # Busca a potência mais próxima
        p_list = sorted(MotorDimensioning.MOTOR_TABLE.keys())
        cv_match = min(p_list, key=lambda x: abs(x - cv))
        data = MotorDimensioning.MOTOR_TABLE[cv_match]
        
        current = data['i220'] if voltage < 300 else data['i380']
        cable = data['cable']
        breaker = data['breaker']
        
        # Ajustes por método de partida
        if method == "Estrela-Triângulo":
            cable = cable * 0.58 # 1/sqrt(3) para cabos internos
            comment = "Fiação interna para 6 terminais."
        elif method in ["Soft-Starter", "Inversor"]:
            breaker = breaker * 1.2 # Margem para harmônicos
            comment = "Considerar cabos blindados (Inversor)."
        else:
            comment = "Partida Direta Convencional."
            
        return {
            "current": current,
            "cable": cable,
            "breaker": breaker,
            "cv_used": cv_match,
            "comment": comment
        }
