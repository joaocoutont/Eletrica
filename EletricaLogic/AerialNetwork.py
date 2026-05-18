# Dimensionamento de Redes Aéreas de Distribuição (NBR 14039 / ABNT)
import math

# Tabela de condutores aéreos comerciais (ACSR = CA/CAA, AAC = CA, AAC/AAAC)
# Formato: (secao_mm2, nome_comercial, capacidade_A, resistencia_ohm_km, diametro_mm, peso_kg_km)
AERIAL_CONDUCTORS = [
    # CA (Alumínio Nu)
    (10,   "CA-10",   65,   2.91,  4.0,  30),
    (16,   "CA-16",   90,   1.82,  5.1,  45),
    (25,   "CA-25",  120,   1.16,  6.4,  70),
    (35,   "CA-35",  145,   0.83,  7.5,  100),
    (50,   "CA-50",  180,   0.59,  9.0,  140),
    (70,   "CA-70",  225,   0.42,  10.7, 200),
    (95,   "CA-95",  265,   0.31,  12.5, 270),
    (120,  "CA-120", 305,   0.25,  14.1, 340),
    (150,  "CA-150", 345,   0.20,  15.8, 420),
    (185,  "CA-185", 390,   0.16,  17.5, 520),
    (240,  "CA-240", 450,   0.12,  20.1, 670),
    # CAA (Cabo de Alumínio com Alma de Aço - ACSR)
    (16,   "CAA-16",  100,  1.80,  5.3,  60),
    (35,   "CAA-35",  160,  0.82,  7.8,  130),
    (50,   "CAA-50",  200,  0.59,  9.3,  190),
    (70,   "CAA-70",  245,  0.42,  11.0, 260),
    (95,   "CAA-95",  295,  0.31,  12.9, 360),
    (120,  "CAA-120", 340,  0.25,  14.5, 450),
    (150,  "CAA-150", 390,  0.20,  16.3, 560),
    (185,  "CAA-185", 440,  0.16,  18.1, 700),
    (240,  "CAA-240", 510,  0.12,  20.8, 920),
    (300,  "CAA-300", 580,  0.10,  23.3, 1150),
    # Fios de Aço Zincado (Comuns em MRT Rural)
    (4,    "Aço-4AWG",  40,   12.5,   5.2,   120),
    (6,    "Aço-6AWG",  30,   20.1,   4.1,   85),
]

# Cabos Protegidos (Rede Compacta / Spacer Cable) - Alumínio XLPE 90°C
# Formato: (secao_mm2, nome_comercial, capacidade_A, resistencia_ohm_km, diametro_ext_mm, peso_kg_km)
COMPACT_CONDUCTORS = [
    (35,   "Compacto-35",  165,  0.83,  13.5,  190),
    (50,   "Compacto-50",  205,  0.59,  15.0,  250),
    (70,   "Compacto-70",  255,  0.42,  16.5,  330),
    (95,   "Compacto-95",  305,  0.31,  18.5,  440),
    (120,  "Compacto-120", 350,  0.25,  20.5,  540),
    (150,  "Compacto-150", 395,  0.20,  22.5,  660),
    (185,  "Compacto-185", 450,  0.16,  25.0,  810),
    (240,  "Compacto-240", 520,  0.12,  28.5,  1050),
]

# Cabos Multiplexados de Baixa Tensão (BT) - Alumínio XLPE 0.6/1kV
# Formato: (secao_mm2, nome_comercial, capacidade_A, resistencia_ohm_km, diametro_mm, peso_kg_km)
BT_CONDUCTORS = [
    (16,   "Triplex-16",  85,   1.91,   15.0,  150),
    (25,   "Triplex-25",  115,  1.20,   18.5,  220),
    (35,   "Triplex-35",  140,  0.86,   21.0,  300),
    (50,   "Triplex-50",  175,  0.64,   24.0,  410),
    (70,   "Triplex-70",  220,  0.44,   27.5,  560),
    (95,   "Triplex-95",  270,  0.32,   31.5,  750),
    (120,  "Triplex-120", 315,  0.25,   35.0,  920),
]

# Cabos Protegidos (Rede Compacta / Spacer Cable) - Alumínio XLPE 90°C
# Formato: (secao_mm2, nome_comercial, capacidade_A, resistencia_ohm_km, diametro_ext_mm, peso_kg_km)
COMPACT_CONDUCTORS = [
    (35,   "Compacto-35",  165,  0.83,  13.5,  190),
    (50,   "Compacto-50",  205,  0.59,  15.0,  250),
    (70,   "Compacto-70",  255,  0.42,  16.5,  330),
    (95,   "Compacto-95",  305,  0.31,  18.5,  440),
    (120,  "Compacto-120", 350,  0.25,  20.5,  540),
    (150,  "Compacto-150", 395,  0.20,  22.5,  660),
    (185,  "Compacto-185", 450,  0.16,  25.0,  810),
    (240,  "Compacto-240", 520,  0.12,  28.5, 1050),
]

# Vãos típicos por classe de poste (metros)
POLE_SPANS = {
    "Urbano":    50,
    "Periurbano": 80,
    "Rural":    100,
    "Travessia":  40,
}

# Postes de madeira (MA) e concreto (CP) — altura x carga
POLES = {
    # (altura_m, carga_daN): modelo
    (9,   150):  "CP-9/150 (Concreto)",
    (9,   300):  "CP-9/300 (Concreto)",
    (9,   600):  "CP-9/600 (Concreto)",
    (11,  150):  "CP-11/150 (Concreto)",
    (11,  200):  "CP-11/200 (Concreto)",
    (11,  300):  "CP-11/300 (Concreto)",
    (11,  600):  "CP-11/600 (Concreto)",
    (11,  1000): "CP-11/1000 (Concreto)",
    (11,  1500): "CP-11/1500 (Concreto)",
    (12,  600):  "CP-12/600 (Concreto)",
    (12,  1000): "CP-12/1000 (Concreto)",
    (13,  1000): "CP-13/1000 (Concreto)",
    (13,  1500): "CP-13/1500 (Concreto)",
    # Postes de Madeira (Tratada)
    (9,   200):  "MA-9/200 (Madeira)",
    (11,  300):  "MA-11/300 (Madeira)",
    (12,  400):  "MA-12/400 (Madeira)",
}


class AerialNetworkCalculator:
    """Dimensionamento de redes aéreas de distribuição conforme ABNT/ANEEL."""

    @staticmethod
    def get_conductor(current_a, conductor_type="CA"):
        """Seleciona o condutor mínimo para a corrente informada."""
        if "Compacto" in conductor_type: table = COMPACT_CONDUCTORS
        elif "Triplex" in conductor_type or "BT" in conductor_type: table = BT_CONDUCTORS
        else: table = AERIAL_CONDUCTORS
        
        for item in table:
            if len(item) >= 6:
                sec, nome, cap, res, diam, weight = item[0], item[1], item[2], item[3], item[4], item[5]
            else:
                sec, nome, cap, res, diam, weight = item[0], item[1], item[2], item[3], 0.0, item[4]
            if cap >= current_a:
                return {
                    "secao_mm2": sec, 
                    "nome": nome, 
                    "capacidade_a": cap, 
                    "resist_ohm_km": res,
                    "diameter_mm": diam,
                    "weight_kg_km": weight
                }
        
        last = table[-1]
        return {
            "secao_mm2": last[0], 
            "nome": last[1], 
            "capacidade_a": last[2], 
            "resist_ohm_km": last[3],
            "diameter_mm": last[4] if len(last) >= 6 else 0.0,
            "weight_kg_km": last[5] if len(last) >= 6 else last[4]
        }

    @staticmethod
    def calculate_sag(span_m, tension_dan, weight_kg_m):
        """Calcula a flecha do condutor (Sag) em metros."""
        # Fórmula: f = (w * L^2) / (8 * H)
        # w = peso por metro (kg/m), L = vão (m), H = tração (daN)
        if tension_dan <= 0: return 0
        sag = (weight_kg_m * (span_m ** 2)) / (8 * tension_dan)
        return round(sag, 3)

    @staticmethod
    def calculate_pole_load(span_m, weight_kg_m, diam_mm, wind_pressure=60, angle_deg=0):
        """Calcula a carga resultante no topo do poste (daN)."""
        # Carga de vento no condutor: Pv = P_vento * Diametro * Vão * Sen(angulo_vento)
        # Assumindo vento perpendicular (sen=1)
        wind_load_cond = (wind_pressure * (diam_mm / 1000.0) * span_m)
        
        # Carga de vento no poste (simplificada: média de 10daN para postes urbanos)
        wind_load_pole = 15.0 
        
        # Tração resultante em ângulos
        # Tração de trabalho estimada em 15% da ruptura (ou 20% do peso linear para simplificar)
        tension_work = weight_kg_m * 1000 * 0.18 # 18% como fator médio
        
        if angle_deg > 0:
            resultant_tension = 2 * tension_work * math.sin(math.radians(angle_deg / 2))
            # Vetorialmente, vento e tração podem se somar. Usamos a soma direta para segurança.
            total_load = wind_load_cond + wind_load_pole + resultant_tension
            return round(total_load, 2)
        
        return round(wind_load_cond + wind_load_pole, 2)

    @staticmethod
    def calculate_voltage_drop_bt(current_a, length_m, resist_ohm_km, voltage_v=220, fp=0.95):
        """Queda de tensão em rede de baixa tensão (%)"""
        # ΔU = √3 * I * R * L * cosφ (Trifásico)
        r_total = resist_ohm_km * (length_m / 1000.0)
        delta_u = math.sqrt(3) * current_a * r_total * fp
        drop_pct = (delta_u / voltage_v) * 100
        return round(drop_pct, 3)

    @staticmethod
    def calculate_voltage_drop_aerial(current_a, length_km, resist_ohm_km, voltage_kv=13.8, fp=0.92):
        """Queda de tensão em linha aérea MT (%)"""
        r_total = resist_ohm_km * length_km
        delta_u = math.sqrt(3) * current_a * r_total * fp
        drop_pct = (delta_u / (voltage_kv * 1000)) * 100
        return round(drop_pct, 3)

    @staticmethod
    def dimension_aerial_line(power_kva, voltage_kv, length_km, fp=0.92,
                                conductor_type="CA", environment="Rural", angle_deg=0,
                                wind_pressure=60, system="Trifásico"):
        """
        Dimensiona uma linha aérea completa (RDU ou RDR).
        """
        is_bt = voltage_kv < 1.0
        v_base = voltage_kv * 1000
        
        # Corrente de linha baseada no sistema
        if "Trifásico" in system:
            current_a = (power_kva * 1000) / (math.sqrt(3) * v_base)
        elif "MRT" in system: # Monofilar com Retorno por Terra
            current_a = (power_kva * 1000) / (v_base / math.sqrt(3)) # Fase-Terra
        else: # Bifásico ou Monofásico F-N
            current_a = (power_kva * 1000) / v_base

        if is_bt and conductor_type == "CA": conductor_type = "Triplex"
        if "MRT" in system: conductor_type = "Aço"

        conductor = AerialNetworkCalculator.get_conductor(current_a, conductor_type)
        
        if is_bt:
            drop = AerialNetworkCalculator.calculate_voltage_drop_bt(
                current_a, length_km * 1000, conductor["resist_ohm_km"], v_base, fp)
        else:
            drop = AerialNetworkCalculator.calculate_voltage_drop_aerial(
                current_a, length_km, conductor["resist_ohm_km"], voltage_kv, fp)

        # Número de postes
        span_m = POLE_SPANS.get(environment, 80)
        num_poles = math.ceil((length_km * 1000) / span_m) + 1

        # Cálculo de Carga no Poste
        weight_kg_m = conductor["weight_kg_km"] / 1000.0
        pole_effort = AerialNetworkCalculator.calculate_pole_load(
            span_m, weight_kg_m, conductor["diameter_mm"], wind_pressure=wind_pressure, angle_deg=angle_deg)
        
        # Seleção de Poste baseada na carga (daN)
        # Valores padrão: 150, 200, 300, 400, 600, 800, 1000, 1200, 1500
        possible_loads = [150, 200, 300, 600, 1000, 1500]
        p_cap = 150
        for load in possible_loads:
            if pole_effort <= load:
                p_cap = load
                break
        else:
            p_cap = 1500 # Máximo se exceder
        
        pole_height = 11 if "Urbano" in environment else 9
        pole_model = f"CP-{pole_height}/{p_cap} (Concreto)"

        # Flecha (Assumindo tração de segurança de 20% do peso linear * 1000)
        safety_tension = (conductor["weight_kg_km"] * 0.2)
        sag = AerialNetworkCalculator.calculate_sag(span_m, safety_tension, weight_kg_m)

        # Nível Básico de Isolamento (NBI / BIL) sugerido por classe de tensão
        nbi_table = {13.8: 95, 23.1: 125, 34.5: 150, 69.0: 350}
        nbi_sug = nbi_table.get(voltage_kv, 95)
        if 15 < voltage_kv < 25: nbi_sug = 125
        elif 25 <= voltage_kv < 40: nbi_sug = 150

        # Proteção e Estrutura
        if voltage_kv <= 15:
            protecao = "Chave Fusível tipo K 15kV"
            espacamento = "Estrutura Compacta CE-1" if "Compacto" in conductor_type else "Estrutura N1"
        else:
            protecao = "Chave Fusível tipo K 36.2kV"
            espacamento = "Estrutura CE-2" if "Compacto" in conductor_type else "Estrutura N2"

        status = "OK" if drop <= 7.0 else "REVISAR (Queda > 7%)"

        return {
            "power_kva": power_kva,
            "voltage_kv": voltage_kv,
            "nbi_kv": nbi_sug,
            "length_km": length_km,
            "current_a": round(current_a, 2),
            "conductor": conductor["nome"],
            "conductor_cap_a": conductor["capacidade_a"],
            "drop_pct": drop,
            "num_poles": num_poles,
            "span_m": span_m,
            "pole_model": pole_model,
            "pole_effort_dan": pole_effort,
            "sag_m": sag,
            "structure": espacamento,
            "protection": protecao,
            "environment": environment,
            "status": status,
        }

# Kits de Materiais por Estrutura (Padrão ABNT/Concessionária)
STRUCTURE_KITS = {
    "N1": {
        "Cruzeta de Concreto 2,40m": 1,
        "Isolador de Pino 15kV": 3,
        "Pino para Isolador": 3,
        "Parafuso M16x250mm c/ Porca": 2,
        "Mão Francesa Plana": 2,
        "Arruela Quadrada 38mm": 4
    },
    "N3": {
        "Cruzeta de Concreto 2,40m": 2,
        "Isolador de Disco 15kV (Polimérico)": 6,
        "Grampo de Ancoragem": 6,
        "Parafuso M16x300mm": 4,
        "Mão Francesa Perfil L": 4,
        "Suporte para Chave": 3
    },
    "CE1": {
        "Braço Tipo C para Compacta": 1,
        "Isolador de Pino Polimérico": 3,
        "Espaçador Losangular (Spacer)": 1,
        "Parafuso M16x200mm": 2,
        "Cinta de Poste DT/SC": 1
    },
    "CE3": {
        "Suporte de Ancoragem para Compacta": 2,
        "Isolador de Disco 15kV": 6,
        "Alça Preformada": 6,
        "Parafuso M16x250mm": 4,
        "Espaçador de Fim de Linha": 1
    },
    "M1": {
        "Pino de Topo": 1,
        "Isolador de Pino 15kV": 1,
        "Arruela Redonda": 1,
        "Parafuso Cabeça Quadrada": 1
    }
}


def get_fuse_link(power_kva, voltage_kv=13.8):
    """Sugere o elo fusivel (Tipo K ou H) para protecao do transformador."""
    table_13_8 = {
        5: "1H", 10: "2H", 15: "3H", 30: "5K", 45: "6K", 75: "10K",
        112.5: "15K", 150: "20K", 300: "40K"
    }
    table_34_5 = {
        15: "1H", 30: "2H", 45: "3H", 75: "6K", 112.5: "10K", 150: "15K"
    }
    table = table_13_8 if voltage_kv < 20 else table_34_5
    return table.get(power_kva, "Verificar Tabela")


AerialNetworkCalculator.get_fuse_link = staticmethod(get_fuse_link)
