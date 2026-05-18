# Gestor de Dispositivos Smart Home e IoT (Zigbee, KNX, WiFi)
import FreeCAD

class SmartHomeManager:
    """
    Gerencia a biblioteca de componentes de automação e sensores inteligentes.
    """
    
    # Biblioteca de dispositivos suportados (Expandida)
    IOT_DEVICES = {
        # Automação Geral
        "Sensor_Presenca": {"Protocolo": "Zigbee", "Consumo": 0.05, "Icon": "Automation.svg"},
        "Interruptor_Smart": {"Protocolo": "WiFi", "Consumo": 0.5, "Icon": "SmartHome.svg"},
        "Atuador_KNX": {"Protocolo": "KNX", "Consumo": 1.2, "Icon": "Automation.svg"},
        "Termostato_Smart": {"Protocolo": "WiFi", "Consumo": 2.0, "Icon": "Automation.svg"},
        
        # Segurança (Fase 6)
        "Camera_IP": {"Protocolo": "WiFi/PoE", "Consumo": 5.0, "Icon": "Camera.svg"},
        "Sensor_Porta": {"Protocolo": "Zigbee", "Consumo": 0.02, "Icon": "Safety.svg"},
        "Sensor_Quebra_Vidro": {"Protocolo": "Zigbee", "Consumo": 0.03, "Icon": "Safety.svg"},
        "Sirene_Smart": {"Protocolo": "Zigbee", "Consumo": 1.5, "Icon": "Safety.svg"},
        "Fechadura_Eletronica": {"Protocolo": "Zigbee/BT", "Consumo": 0.1, "Icon": "Safety.svg"},
    }

    @staticmethod
    def add_smart_device(device_type, position=FreeCAD.Vector(0,0,0), label=None):
        """Insere um dispositivo inteligente no documento com metadados de automação."""
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        info = SmartHomeManager.IOT_DEVICES.get(device_type)
        if not info:
            FreeCAD.Console.PrintWarning(f"SmartHome: Tipo '{device_type}' não encontrado.\n")
            return
            
        # Criar Objeto BIM (usando FeaturePython para flexibilidade)
        obj = doc.addObject("App::FeaturePython", label or f"Smart_{device_type}")
        obj.Placement.Base = position
        
        # Adicionar Propriedades Customizadas
        obj.addProperty("App::PropertyString", "TipoBIM", "Geral", "Tipo de dispositivo").TipoBIM = "SmartDevice"
        obj.addProperty("App::PropertyString", "Protocolo", "Automacao", "Protocolo de comunicacao").Protocolo = info["Protocolo"]
        obj.addProperty("App::PropertyFloat", "ConsumoStandby", "Automacao", "Consumo em standby (W)").ConsumoStandby = info["Consumo"]
        obj.addProperty("App::PropertyString", "DeviceType", "Automacao", "Modelo do dispositivo").DeviceType = device_type
        obj.addProperty("App::PropertyBool", "IsOnline", "Status", "Status de conexao").IsOnline = True
        obj.addProperty("App::PropertyString", "SceneGroup", "Automacao", "Grupo de Cena").SceneGroup = "Nenhum"
        
        doc.recompute()
        FreeCAD.Console.PrintMessage(f"SmartHome: {device_type} adicionado via {info['Protocolo']}.\n")
        return obj

    @staticmethod
    def calculate_automation_load():
        """Calcula o consumo total de standby do sistema de automação."""
        doc = FreeCAD.ActiveDocument
        total_w = 0.0
        count = 0
        for obj in doc.Objects:
            if hasattr(obj, "ConsumoStandby"):
                total_w += float(obj.ConsumoStandby)
                count += 1
        return total_w, count

    @staticmethod
    def generate_iot_report():
        """Gera um resumo técnico dos dispositivos IoT do projeto."""
        load, count = SmartHomeManager.calculate_automation_load()
        report = [
            "--- RELATÓRIO DE AUTOMAÇÃO (SMART HOME) ---",
            f"Total de Dispositivos: {count}",
            f"Consumo Base (Standby): {load:.2f} W",
            "------------------------------------------"
        ]
        
        doc = FreeCAD.ActiveDocument
        for obj in doc.Objects:
            if hasattr(obj, "Protocolo"):
                report.append(f"[{obj.Protocolo}] {obj.Label} - {obj.DeviceType}")
                
        return "\n".join(report)

class SceneManager:
    """
    Gerencia cenários (Cenas) e grupos de dispositivos.
    """
    
    @staticmethod
    def create_scene(name, devices):
        """
        Agrupa dispositivos sob um nome de cena.
        devices: lista de objetos do FreeCAD.
        """
        for dev in devices:
            if hasattr(dev, "SceneGroup"):
                dev.SceneGroup = name
        FreeCAD.Console.PrintMessage(f"SmartHome: Cena '{name}' criada com {len(devices)} dispositivos.\n")

    @staticmethod
    def get_topology_report():
        """Gera um relatório de topologia de rede inteligente."""
        doc = FreeCAD.ActiveDocument
        topology = {"Zigbee": [], "WiFi": [], "KNX": [], "Outros": []}
        
        for obj in doc.Objects:
            if hasattr(obj, "Protocolo"):
                p = obj.Protocolo
                if "Zigbee" in p: topology["Zigbee"].append(obj.Label)
                elif "WiFi" in p: topology["WiFi"].append(obj.Label)
                elif "KNX" in p: topology["KNX"].append(obj.Label)
                else: topology["Outros"].append(obj.Label)
        
        report = ["--- TOPOLOGIA DE REDE SMART HOME ---"]
        for proto, devs in topology.items():
            report.append(f"{proto}: {len(devs)} dispositivo(s)")
            if devs:
                report.append(f"  > {', '.join(devs)}")
        
        return "\n".join(report)

    @staticmethod
    def simulate_scene_activation(scene_name):
        """Simula a ativação de uma cena, verificando quais dispositivos estão online."""
        doc = FreeCAD.ActiveDocument
        activated = 0
        offline = 0
        
        for obj in doc.Objects:
            if hasattr(obj, "SceneGroup") and obj.SceneGroup == scene_name:
                if getattr(obj, "IsOnline", True):
                    activated += 1
                else:
                    offline += 1
        
        msg = f"Cena '{scene_name}': {activated} OK"
        if offline > 0:
            msg += f" | ⚠️ {offline} OFFLINE"
        
        FreeCAD.Console.PrintMessage(msg + "\n")
        return activated, offline
