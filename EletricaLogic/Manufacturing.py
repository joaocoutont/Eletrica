# Motor de Manufatura e Exportação para CNC (Dobra de Barramentos)
import math

class BusbarManufacturing:
    """Ferramentas para planificação e exportação de barramentos para CNC."""

    @staticmethod
    def flatten_busbar(width_mm, thickness_mm, segment_lengths_mm, angles_deg):
        """
        Calcula o comprimento total planificado considerando o fator K (fibra neutra).
        Retorna o comprimento total e as posições de dobra.
        """
        # Fator K para cobre/alumínio ~0.33 para dobras em V
        k_factor = 0.33
        total_length = sum(segment_lengths_mm)
        
        bend_deductions = []
        for angle in angles_deg:
            # Simplificação da dedução de dobra: (pi * (R + K*T) * angle/180) - 2*(R+T)
            # Para facilitar: Adicionamos compensação baseada no ângulo
            deduction = (angle / 90.0) * thickness_mm * k_factor
            bend_deductions.append(round(deduction, 2))
            
        final_length = total_length + sum(bend_deductions)
        
        return {
            "flat_length_mm": round(final_length, 2),
            "bend_positions": [round(sum(segment_lengths_mm[:i+1]), 2) for i in range(len(segment_lengths_mm)-1)],
            "material_weight_kg": round((final_length * width_mm * thickness_mm * 8.96e-6), 3) # Densidade Cu
        }

    @staticmethod
    def export_to_dxf(filename, flat_data):
        """Mock para exportação de DXF de planificação."""
        return f"Arquivo {filename}.dxf gerado com marcas de dobra em {flat_data['bend_positions']}."
