# Logica de Interruptores e Comando de Iluminacao
import FreeCAD

class LightingManager:
    @staticmethod
    def insert_switch(switch_type="Simples", cmd_letter="a"):
        """Insere um interruptor e define sua logica de comando"""
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        
        # Escolher componente baseado no tipo
        comp_map = {
            "Simples": "Interrup_Simples.FCStd",
            "Paralelo": "Interrup_Paralelo.FCStd",
            "Intermediario": "Interrup_FourWay.FCStd"
        }
        
        comp = comp_map.get(switch_type, "Interrup_Simples.FCStd")
        obj = lib.insert_component(comp, label=f"Interrup_{cmd_letter}")
        
        if obj:
            # Adicionar Propriedades de Comando
            if not hasattr(obj, "Comando"):
                obj.addProperty("App::PropertyString", "Comando", "Iluminação", "Letra de Comando (ex: a)").Comando = cmd_letter
                obj.addProperty("App::PropertyEnumeration", "TipoInterruptor", "Iluminação", "Tipo")
                obj.TipoInterruptor = ["Simples", "Paralelo", "Intermediario"]
                obj.TipoInterruptor = switch_type
                obj.addProperty("App::PropertyInteger", "QtdTeclas", "Iluminação", "Quantidade de Teclas").QtdTeclas = 1
                
        FreeCAD.ActiveDocument.recompute()
        return obj

    @staticmethod
    def merge_switches(switch_list):
        """Mescla varios interruptores em uma unica placa (2 ou 3 teclas)"""
        if len(switch_list) < 2: return
        
        base_obj = switch_list[0]
        commands = [s.Comando for s in switch_list]
        
        # Atualiza o primeiro objeto para ser multi-tecla
        base_obj.Label = "Interrup_" + "_".join(commands)
        base_obj.Comando = ", ".join(commands)
        base_obj.QtdTeclas = len(switch_list)
        
        # Remove os outros para nao duplicar no BOM (apenas a placa fica)
        doc = FreeCAD.ActiveDocument
        for i in range(1, len(switch_list)):
            doc.removeObject(switch_list[i].Name)
            
        FreeCAD.Console.PrintMessage(f"Interruptores mesclados: {len(commands)} teclas na mesma caixa.\n")
        doc.recompute()
