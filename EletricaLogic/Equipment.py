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
            "Motor 1cv (Monofasico)": {"power": 735, "pf": 0.75, "label": "Motor"},
            "Compressor de Ar (5cv)": {"power": 3675, "pf": 0.80, "label": "Compressor"},
            "Maquina de Solda (Mig/Mag)": {"power": 8000, "pf": 0.60, "label": "Solda"},
            "Ponte Rolante (10ton)": {"power": 15000, "pf": 0.85, "label": "Ponte_Rolante"},
            "Nobreak Rack (3kVA)": {"power": 2400, "pf": 0.95, "label": "UPS"}
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
            
            # Definir tensao do equipamento (ex: chuveiro costuma ser 220V)
            if "Chuveiro" in preset_name:
                obj.Tensao = "220V"
            
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
        
        # Adicionar caixas de entrada
        count_30x30 = 0
        for obj in doc.Objects:
            if "Caixa_Passagem_30x30" in obj.Label:
                count_30x30 += 1
        
        if not hasattr(settings, "QtdCaixas30x30"):
            settings.addProperty("App::PropertyInteger", "QtdCaixas30x30", "Quantitativos", "Quantidade de caixas 30x30")
        settings.QtdCaixas30x30 = count_30x30
        
        return count_4x2, count_octo

    @staticmethod
    def bimify_equipment(obj, equipment_type="Motor"):
        """Transforma um objeto 3D generico em um componente eletrico inteligente"""
        if not obj: return
        
        # Adicionar Propriedades de Potencia
        if not hasattr(obj, "Potencia"):
            obj.addProperty("App::PropertyFloat", "Potencia", "Eletrica", "Potência Ativa (W)")
            obj.addProperty("App::PropertyFloat", "Potencia_CV", "Eletrica", "Potência em CV").Potencia_CV = 1.0
            obj.addProperty("App::PropertyFloat", "FatorPotencia", "Eletrica", "Fator de Potencia").FatorPotencia = 0.85
            obj.addProperty("App::PropertyFloat", "Rendimento", "Eletrica", "Rendimento (%)").Rendimento = 90.0
            
        # Adicionar Propriedades de Instalacao
        if not hasattr(obj, "Tensao"):
            obj.addProperty("App::PropertyString", "Tensao", "Eletrica", "Tensão de Operação").Tensao = "380V"
            obj.addProperty("App::PropertyEnumeration", "TipoPartida", "Eletrica", "Método de Partida")
            obj.TipoPartida = ["Direta", "Estrela-Triangulo", "Soft-Starter", "Inversor de Frequencia"]
            obj.addProperty("App::PropertyString", "Circuito", "Eletrica", "Circuito de Alimentação").Circuito = "C1"
            
        # Adicionar Tag BIM
        if not hasattr(obj, "TipoBIM"):
            obj.addProperty("App::PropertyString", "TipoBIM", "BIM", "Categoria").TipoBIM = equipment_type
            
        # Adicionar Propriedades de Ciclo de Vida (BIM 6D / O&M)
        if not hasattr(obj, "NumeroSerie"):
            obj.addProperty("App::PropertyString", "NumeroSerie",    "Manutencao", "Nº de Série")
            obj.addProperty("App::PropertyString", "DataInstalacao", "Manutencao", "Data Instalação")
            obj.addProperty("App::PropertyString", "DataManutencao", "Manutencao", "Próxima Manutenção")
            
        FreeCAD.Console.PrintMessage(f"Objeto {obj.Label} agora é um componente elétrico BIM.\n")
        FreeCAD.ActiveDocument.recompute()
        return True
