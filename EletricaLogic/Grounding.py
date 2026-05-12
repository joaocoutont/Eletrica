# Calculadora de Aterramento (Hastes)
import math

class GroundingManager:
    @staticmethod
    def calculate_rods(resistivity, target_resistance=10.0, rod_length=2.4, rod_diameter=0.015):
        """
        Calcula o numero de hastes necessarias para atingir a resistencia desejada.
        Formula simplificada: R = (rho / (2 * pi * L)) * [ln(8L/d) - 1]
        """
        # Resistencia de uma haste unica
        r1 = (resistivity / (2 * math.pi * rod_length)) * (math.log((8 * rod_length) / rod_diameter) - 1)
        
        # Numero de hastes (considerando fator de eficiencia de agrupamento de ~0.9)
        num_rods = math.ceil(r1 / (target_resistance * 0.9))
        
        return {
            "SingleRodResistance": round(r1, 2),
            "RequiredRods": max(1, num_rods),
            "TargetResistance": target_resistance
        }
