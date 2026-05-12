# Sistema de Protecao contra Descargas Atmosfericas (SPDA)
import math

class SPDACalculator:
    @staticmethod
    def calculate_franklin_radius(height, alpha=45):
        """Calcula o raio de protecao pelo metodo de Franklin"""
        # R = h * tan(alpha)
        rad = math.radians(alpha)
        radius = height * math.tan(rad)
        return round(radius, 2)

    @staticmethod
    def calculate_faraday_mesh(level):
        """Sugere a malha de Faraday baseada no nível de proteção (I a IV)"""
        mesh_sizes = {
            "I": "5x5 m",
            "II": "10x10 m",
            "III": "15x15 m",
            "IV": "20x20 m"
        }
        return mesh_sizes.get(level, "15x15 m")

    @staticmethod
    def suggest_down_conductors(perimeter, level):
        """Sugere o numero de descidas baseado no perimetro e nivel"""
        spacing = {"I": 10, "II": 15, "III": 20, "IV": 25}
        s = spacing.get(level, 20)
        num = math.ceil(perimeter / s)
        return max(2, num)
