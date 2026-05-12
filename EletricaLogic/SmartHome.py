# Modulo de Automação e Casa Inteligente (Smart Home)
import FreeCAD

class SmartHomeManager:
    @staticmethod
    def get_automation_presets():
        return {
            "Sensor de Presença (PIR)": {"Potencia": 2.0, "Icon": "pir_sensor"},
            "Câmera IP Wi-Fi": {"Potencia": 10.0, "Icon": "camera_ip"},
            "Módulo Relé Wi-Fi (Sonoff)": {"Potencia": 1.5, "Icon": "smart_relay"},
            "Hub de Automação (Zigbee)": {"Potencia": 5.0, "Icon": "hub_gateway"},
            "Fechadura Eletrônica": {"Potencia": 5.0, "Icon": "smart_lock"}
        }

    @staticmethod
    def insert_smart_device(device_type):
        """Insere um dispositivo de automacao no projeto BIM"""
        presets = SmartHomeManager.get_automation_presets()
        if device_type not in presets: return
        
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("App::FeaturePython", device_type.replace(" ", "_"))
        obj.Label = device_type
        
        # Adicionar propriedades BIM de automacao
        obj.addProperty("App::PropertyString", "Protocolo", "Automação", "Protocolo de Comunicação (Wi-Fi/Zigbee)")
        obj.Protocolo = "Wi-Fi"
        
        obj.addProperty("App::PropertyFloat", "Potencia", "Eletrica", "Consumo em Standby (W)")
        obj.Potencia = presets[device_type]["Potencia"]
        
        obj.addProperty("App::PropertyString", "Integracao", "Automação", "Sistema (Alexa/Google/HomeAssistant)")
        obj.Integracao = "Alexa / Google Home"
        
        FreeCAD.ActiveDocument.recompute()
        return obj
