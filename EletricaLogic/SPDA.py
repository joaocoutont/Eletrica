# Sistema de Protecao contra Descargas Atmosfericas - SPDA Completo (NBR 5419)
import math

# Densidades de raios para o Brasil (raios/km²/ano) por estado
# Fonte: INPE / NBR 5419-2
BRASIL_NG = {
    "AM": 15, "PA": 12, "MT": 10, "MS": 9, "GO": 9,
    "MG": 8,  "SP": 7,  "RJ": 6,  "RS": 5, "PR": 6,
    "SC": 5,  "BA": 6,  "PE": 4,  "CE": 5, "MA": 8,
    "TO": 11, "RO": 14,
 "AC": 16, "RR": 14, "AP": 12,
    "SE": 5,  "AL": 4,  "PB": 4,  "RN": 4,  "PI": 7,
    "ES": 5,  "DF": 9,
}

# Fator de localização (Cd) — NBR 5419-2 Tabela C2
LOCATION_FACTORS = {
    "Isolada (morro/topo)": 2.0,
    "Maior que vizinhos":   1.0,
    "Igual aos vizinhos":   0.5,
    "Menor que vizinhos":   0.25,
    "Rodeada por mais altas": 0.25,
}

# Fator de estrutura (Ks) — NBR 5419-2
STRUCTURE_FACTORS = {
    "Metal (risco baixo)":        0.5,
    "Concreto / Alvenaria":       1.0,
    "Madeira / Inflamável":       2.0,
    "Com explosivos / Produtos perigosos": 3.0,
}

# Especificações de malha por nível (NBR 5419)
SPDA_LEVELS = {
    "I":   {"malha": "5x5 m",   "espacamento_descidas": 10, "fio_mm2": 50,  "haste_m": 3.0},
    "II":  {"malha": "10x10 m", "espacamento_descidas": 15, "fio_mm2": 35,  "haste_m": 2.4},
    "III": {"malha": "15x15 m", "espacamento_descidas": 20, "fio_mm2": 25,  "haste_m": 2.4},
    "IV":  {"malha": "20x20 m", "espacamento_descidas": 25, "fio_mm2": 16,  "haste_m": 1.5},
}


class SPDACalculator:
    """SPDA completo conforme NBR 5419 — Franklin, Faraday, Aterramento, DPS."""

    # ---- Métodos de Proteção ----
    @staticmethod
    def franklin_radius(height_m, angle_deg=45):
        """Raio de proteção pelo método Franklin (hastes e agulhas)."""
        return round(height_m * math.tan(math.radians(angle_deg)), 2)

    @staticmethod
    def rolling_sphere_radius(level):
        """Raio da esfera rolante por nível (NBR 5419 Tabela 3)."""
        radii = {"I": 20, "II": 30, "III": 45, "IV": 60}
        return radii.get(level, 45)

    @staticmethod
    def faraday_mesh(level):
        """Dimensões da malha de Faraday e seção mínima do condutor."""
        return SPDA_LEVELS.get(level, SPDA_LEVELS["III"])

    @staticmethod
    def down_conductors(perimeter_m, level):
        """Número mínimo de descidas baseado no perímetro e nível."""
        spacing = SPDA_LEVELS.get(level, SPDA_LEVELS["III"])["espacamento_descidas"]
        num = math.ceil(perimeter_m / spacing)
        return max(2, num)

    # ---- Análise de Risco NBR 5419-2 ----
    @staticmethod
    def risk_analysis(length_m, width_m, height_m, ng, location_key, structure_key):
        """
        Análise completa de risco conforme NBR 5419-2.
        Retorna se SPDA é necessário e o nível recomendado.
        """
        cd = LOCATION_FACTORS.get(location_key, 1.0)
        ks = STRUCTURE_FACTORS.get(structure_key, 1.0)

        # Área de exposição equivalente (Ae)
        ae = (length_m * width_m) + (6 * height_m * (length_m + width_m)) + (9 * math.pi * height_m**2)

        # Frequência de incidência (Nd)
        nd = ng * ae * cd * 1e-6

        # Risco total
        risk = nd * ks
        tolerable = 1e-5  # Perda de vida humana — NBR 5419

        required = risk > tolerable

        # Nível
        if risk > 1e-3:   level = "I"
        elif risk > 1e-4: level = "II"
        elif risk > 1e-5: level = "III"
        else:             level = "IV"

        return {
            "ae_m2": round(ae, 1),
            "nd_strikes_yr": round(nd, 6),
            "risk": round(risk, 8),
            "tolerable": tolerable,
            "spda_required": required,
            "level": level if required else "Não obrigatório",
            "level_specs": SPDA_LEVELS.get(level, {}) if required else {},
        }

    # ---- Dimensionamento Completo ----
    @staticmethod
    def full_design(length_m, width_m, height_m, ng, location_key, structure_key):
        """
        Retorna o projeto SPDA completo: risco, captores, descidas, aterramento.
        """
        risk = SPDACalculator.risk_analysis(length_m, width_m, height_m, ng, location_key, structure_key)
        level = risk["level"].split()[0] if risk["spda_required"] else "III"  # default de projeto

        specs = SPDA_LEVELS.get(level, SPDA_LEVELS["III"])
        perimeter = 2 * (length_m + width_m)
        descidas = SPDACalculator.down_conductors(perimeter, level)
        esfera = SPDACalculator.rolling_sphere_radius(level)

        # Hastes de aterramento (2,4m padrão NBR)
        from EletricaLogic.Grounding import GroundingManager
        # Resistividade padrão 100 Ω·m (solo mediano) — usuário pode ajustar
        grounding = GroundingManager.calculate_rods(100.0, target_resistance=10.0,
                                                    rod_length=specs["haste_m"])

        return {
            "risk_analysis": risk,
            "level": level,
            "mesh": specs["malha"],
            "conductor_mm2": specs["fio_mm2"],
            "down_conductors": descidas,
            "sphere_radius_m": esfera,
            "franklin_radius_m": SPDACalculator.franklin_radius(height_m),
            "grounding_rods": grounding["RequiredRods"],
            "grounding_r_ohm": grounding["SingleRodResistance"],
            "dps_required": True,  # Sempre recomendado
            "dps_class": "DPS Classe I+II na entrada + Classe III nos quadros",
        }
