# Gerenciamento de Equipamentos Especiais (TUEs) e Caixas
import FreeCAD

class EquipmentManager:
    @staticmethod
    def get_tue_presets():
        return {
            "Chuveiro Comum (5500W)": {"power": 5500, "pf": 1.0, "label": "Chuveiro"},
            "Chuveiro Turbo (7500W)": {"power": 7500, "pf": 1.0, "label": "Chuveiro_Turbo"},
            "Ar Cond. 9000 BTU": {"power": 1200, "pf": 0.85, "label": "Ar_Cond"},
            "Ar Cond. 12000 BTU": {"power": 1600, "pf": 0.85, "label": "Ar_Cond"},
            "Forno Eletrico": {"power": 3000, "pf": 1.0, "label": "Forno"},
            "Motor 1cv (Monofasico)": {"power": 735, "pf": 0.75, "label": "Motor"}
        }

    @staticmethod
    def insert_tue(preset_name, position=None):
        """Insere um equipamento TUE com configuracoes pre-definidas"""
        presets = EquipmentManager.get_tue_presets()
        if preset_name not in presets: return None
        
        data = presets[preset_name]
        from EletricaLogic.Library import LibraryManager
        manager = LibraryManager()
        
        # Inserir um ponto de bocal ou tomada como base
        obj = manager.insert_component("HRC_Tomada_1_20A.FCStd", label=data["label"])
        if obj:
            obj.Potencia = data["power"]
            obj.Circuito = f"TUE_{data['label']}"
            if position:
                obj.Placement.Base = position
                
            # Adicionar Tag de TUE para o BOM
            if not hasattr(obj, "TipoBIM"):
                obj.addProperty("App::PropertyString", "TipoBIM", "Eletrica", "Tipo de componente para o BOM")
            obj.TipoBIM = "TUE"
            
        return obj

    @staticmethod
    def add_boxes_to_all():
        """Detecta componentes e adiciona caixas de passagem virtuais para o BOM"""
        doc = FreeCAD.ActiveDocument
        count_4x2 = 0
        count_octo = 0
        
        for obj in doc.Objects:
            if hasattr(obj, "Potencia"):
                if "Luz" in obj.Label or "Lampada" in obj.Label:
                    count_octo += 1
                else:
                    count_4x2 += 1
        
        # Guardar esses dados em um objeto de projeto para o BOM ler
        from EletricaLogic.Settings import ProjectSettings
        settings = ProjectSettings.get_settings_obj()
        if not hasattr(settings, "QtdCaixas4x2"):
            settings.addProperty("App::PropertyInteger", "QtdCaixas4x2", "Quantitativos", "Quantidade de caixas 4x2")
            settings.addProperty("App::PropertyInteger", "QtdCaixasOcto", "Quantitativos", "Quantidade de caixas Octogonais")
        
        settings.QtdCaixas4x2 = count_4x2
        settings.QtdCaixasOcto = count_octo
        return count_4x2, count_octo
