# Dimensionamento de Redes Aéreas de Distribuição (NBR 14039 / ABNT)
import math

# Tabela de condutores aéreos comerciais (ACSR = CA/CAA, AAC = CA, AAC/AAAC)
# Formato: (secao_mm2, nome_comercial, capacidade_A, resistencia_ohm_km)
AERIAL_CONDUCTORS = [
    # CA (Alumínio Nu)
    (10,   "CA-10",   65,   2.91),
    (16,   "CA-16",   90,   1.82),
    (25,   "CA-25",  120,   1.16),
    (35,   "CA-35",  145,   0.83),
    (50,   "CA-50",  180,   0.59),
    (70,   "CA-70",  225,   0.42),
    (95,   "CA-95",  265,   0.31),
    (120,  "CA-120", 305,   0.25),
    (150,  "CA-150", 345,   0.20),
    (185,  "CA-185", 390,   0.16),
    (240,  "CA-240", 450,   0.12),
    # CAA (Cabo de Alumínio com Alma de Aço - ACSR)
    (16,   "CAA-16",  100,  1.80),
    (35,   "CAA-35",  160,  0.82),
    (50,   "CAA-50",  200,  0.59),
    (70,   "CAA-70",  245,  0.42),
    (95,   "CAA-95",  295,  0.31),
    (120,  "CAA-120", 340,  0.25),
    (150,  "CAA-150", 390,  0.20),
    (185,  "CAA-185", 440,  0.16),
    (240,  "CAA-240", 510,  0.12),
    (300,  "CAA-300", 580,  0.10),
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
    (9,   300): "CP-9/300 (Concreto) ou MA-9/300 (Madeira)",
    (9,   600): "CP-9/600 (Concreto)",
    (11,  300): "CP-11/300 (Concreto)",
    (11,  600): "CP-11/600 (Concreto)",
    (11, 1000): "CP-11/1000 (Concreto)",
    (12,  600): "CP-12/600 (Concreto)",
    (13, 1000): "CP-13/1000 (Concreto)",
}


class AerialNetworkCalculator:
    """Dimensionamento de redes aéreas de distribuição conforme ABNT/ANEEL."""

    @staticmethod
    def get_conductor(current_a, conductor_type="CA"):
        """Seleciona o condutor mínimo para a corrente informada."""
        for sec, nome, cap, res in AERIAL_CONDUCTORS:
            if conductor_type in nome and cap >= current_a:
                return {"secao_mm2": sec, "nome": nome, "capacidade_a": cap, "resist_ohm_km": res}
        # Retorna o maior disponível
        biggest = [c for c in AERIAL_CONDUCTORS if conductor_type in c[1]]
        last = biggest[-1]
        return {"secao_mm2": last[0], "nome": last[1], "capacidade_a": last[2], "resist_ohm_km": last[3]}

    @staticmethod
    def calculate_voltage_drop_aerial(current_a, length_km, resist_ohm_km, voltage_kv=13.8, fp=0.92):
        """Queda de tensão em linha aérea (%) — monofásico ou trifásico."""
        r_total = resist_ohm_km * length_km
        # Queda de tensão trifásica: ΔU = √3 × I × (R×cosφ) / Vn
        delta_u = math.sqrt(3) * current_a * r_total * fp
        drop_pct = (delta_u / (voltage_kv * 1000)) * 100
        return round(drop_pct, 3)

    @staticmethod
    def dimension_aerial_line(power_kva, voltage_kv, length_km, fp=0.92,
                               conductor_type="CA", environment="Rural"):
        """
        Dimensiona uma linha aérea completa.
        Retorna: condutor, queda de tensão, postes necessários.
        """
        # Corrente de linha
        current_a = (power_kva * 1000) / (math.sqrt(3) * voltage_kv * 1000)

        conductor = AerialNetworkCalculator.get_conductor(current_a, conductor_type)
        drop = AerialNetworkCalculator.calculate_voltage_drop_aerial(
            current_a, length_km, conductor["resist_ohm_km"], voltage_kv, fp)

        # Número de postes
        span_m = POLE_SPANS.get(environment, 80)
        num_poles = math.ceil((length_km * 1000) / span_m) + 1

        # Poste padrão por tipo de ambiente
        pole_model = {
            "Urbano":    "CP-11/600 (Concreto)",
            "Periurbano":"CP-11/600 (Concreto)",
            "Rural":     "CP-11/300 (Concreto) ou MA-11/300 (Madeira)",
            "Travessia": "CP-13/1000 (Concreto)",
        }.get(environment, "CP-11/600 (Concreto)")

        # Proteção
        if voltage_kv <= 15:
            protecao = "Chave Fusível tipo K 15kV"
        elif voltage_kv <= 36.2:
            protecao = "Chave Fusível tipo K 36.2kV"
        else:
            protecao = "Chave Seccionadora 69kV"

        status = "OK" if drop <= 7.0 else "REVISAR (Queda > 7%)"

        return {
            "power_kva": power_kva,
            "voltage_kv": voltage_kv,
            "length_km": length_km,
            "current_a": round(current_a, 2),
            "conductor": conductor["nome"],
            "conductor_cap_a": conductor["capacidade_a"],
            "drop_pct": drop,
            "num_poles": num_poles,
            "span_m": span_m,
            "pole_model": pole_model,
            "protection": protecao,
            "environment": environment,
            "status": status,
        }
