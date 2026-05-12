# Gerenciamento de Grupos Geradores e QTA
import FreeCAD

class GeneratorManager:
    @staticmethod
    def dimension_generator(critical_kva):
        """Sugere gerador e QTA baseado na carga critica"""
        # Presets de mercado
        generator_kva = [20, 30, 55, 80, 110, 150, 250, 500, 750, 1000]
        selected_kva = next((x for x in generator_kva if x >= critical_kva), generator_kva[-1])
        
        # Dimensionar QTA (Corrente aproximada em 380V)
        qta_amp = (selected_kva * 1000) / (1.732 * 380)
        selected_qta = next((x for x in [40, 63, 100, 160, 250, 400, 630, 800, 1000, 1250] if x >= qta_amp), 1250)
        
        return {
            "Gerador_kVA": selected_kva,
            "QTA_Amp": selected_qta,
            "Tipo": "Diesel Estacionário",
            "Autonomia": "8 horas (Tanque Base)"
        }

    @staticmethod
    def create_generator_bim(critical_kva):
        """Insere o Gerador e QTA no modelo BIM"""
        data = GeneratorManager.dimension_generator(critical_kva)
        doc = FreeCAD.ActiveDocument
        
        # Objeto Gerador
        gen = doc.addObject("App::FeaturePython", f"Gerador_{data['Gerador_kVA']}kVA")
        gen.Label = f"Gerador_Emergencia_{data['Gerador_kVA']}kVA"
        gen.addProperty("App::PropertyFloat", "PotenciaKVA", "Emergência").PotenciaKVA = data["Gerador_kVA"]
        gen.addProperty("App::PropertyString", "Combustivel", "Emergência").Combustivel = "Diesel"
        
        # Objeto QTA
        qta = doc.addObject("App::FeaturePython", f"QTA_{data['QTA_Amp']}A")
        qta.Label = f"QTA_{data['QTA_Amp']}A"
        qta.addProperty("App::PropertyString", "TipoTransferencia", "Engenharia").TipoTransferencia = "Automática (Aberta)"
        qta.addProperty("App::PropertyFloat", "CorrenteNominal", "Engenharia").CorrenteNominal = data["QTA_Amp"]
        
        FreeCAD.ActiveDocument.recompute()
        return gen, qta
