# GUI Commands for Eletrica Workbench
import FreeCAD
import FreeCADGui

class InsertSocket:
    """Comando para inserir uma tomada (placeholder)"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad', # Usando icone padrao por enquanto
            'MenuText': 'Inserir Tomada',
            'ToolTip': 'Insere uma tomada 2P+T no projeto'
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Comando Inserir Tomada Ativado\n")
        # Aqui entraria a logica de criacao do objeto 3D BIM
        return

class InsertLight:
    """Comando para inserir um ponto de luz (placeholder)"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Iluminacao',
            'ToolTip': 'Insere um ponto de luz no teto/parede'
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Comando Inserir Iluminacao Ativado\n")
        return

class CreateConduit:
    """Comando para criar um eletroduto a partir de uma selecao ou desenho"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Criar Eletroduto',
            'ToolTip': 'Converte uma linha selecionada em um Eletroduto BIM'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Conduit import ConduitManager
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            FreeCAD.Console.PrintWarning("Selecione uma linha ou wire primeiro.\n")
            # Opcionalmente: Ativar a ferramenta de desenho de linha
            FreeCADGui.runCommand("Draft_Wire")
            return
            
        for obj in selection:
            if hasattr(obj, "Points"): # Verifica se e algo que tem pontos (Wire, Line)
                ConduitManager.create_conduit(obj.Points)
                FreeCAD.Console.PrintMessage(f"Objeto {obj.Label} convertido em Eletroduto.\n")
        
        return

class GenerateLoadSchedule:
    """Comando para gerar o quadro de cargas em planilha"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Quadro de Cargas',
            'ToolTip': 'Cria uma planilha com o resumo de cargas e dimensionamento'
        }

    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule()
        return

class GenerateLegend:
    """Comando para gerar a legenda de simbolos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Legenda',
            'ToolTip': 'Cria uma tabela com todos os simbolos usados no projeto'
        }

    def Activated(self):
        from EletricaLogic.Legend import LegendManager
        LegendManager.generate_legend()
        return

class OpenSettings:
    """Comando para abrir as configuracoes do projeto"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Configuracoes do Projeto',
            'ToolTip': 'Define tensao, fator de potencia e outros dados globais'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Settings import ProjectSettings
        
        obj = ProjectSettings.get_settings_obj()
        if not obj: return
        
        # Dialogo Simples
        tensao, ok = QtWidgets.QInputDialog.getItem(
            None, "Configuracoes Eletrica", "Selecione a Tensao do Projeto:", 
            ["127V", "220V", "380V"], 0, False
        )
        if ok:
            obj.Tensao = tensao
            FreeCAD.Console.PrintMessage(f"Tensao definida para {tensao}\n")

class AnalyzeSpaceLighting:
    """Comando para sugerir iluminacao baseada no Arch Space selecionado"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Analisar Iluminacao do Espaco',
            'ToolTip': 'Calcula potencia e pontos de luz para o espaco selecionado'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Spaces import SpaceLightingManager
        from PySide2 import QtWidgets
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            FreeCAD.Console.PrintWarning("Selecione um objeto 'Space' do Workbench BIM.\n")
            return
            
        space = selection[0]
        result = SpaceLightingManager.analyze_space(space)
        
        if result:
            msg = f"--- Analise do Espaco: {space.Label} ---\n"
            msg += f"Area: {result['Area']:.2f} m2\n"
            msg += f"Potencia Minima (NBR 5410): {result['PowerVA']} VA\n"
            msg += f"Alvo Luminotecnico: {result['LuxTarget']} lux\n"
            msg += f"Sugestao: {result['PointsSuggested']} pontos de luz\n\n"
            msg += "Deseja distribuir esses pontos automaticamente em grid agora?"
            
            res = QtWidgets.QMessageBox.question(None, "Analise de Iluminacao", msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if res == QtWidgets.QMessageBox.Yes:
                SpaceLightingManager.distribute_lights(space, result['PointsSuggested'])

class CreateTechnicalSheet:
    """Comando para gerar a prancha final do projeto no TechDraw"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Prancha do Projeto',
            'ToolTip': 'Cria uma folha de desenho com quadro de cargas e legenda'
        }

    def Activated(self):
        from EletricaLogic.Documentation import DocumentationManager
        DocumentationManager.create_technical_sheet()
        return

class BalancePhases:
    """Comando para equilibrar as fases do projeto"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Equilibrar Fases',
            'ToolTip': 'Distribui os circuitos entre R, S e T automaticamente'
        }

    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.balance_phases()
        return

class CalculateWiring:
    """Comando para calcular comprimentos e quedas de tensao"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Calcular Fiacao',
            'ToolTip': 'Calcula metragem de cabos e verifica queda de tensao'
        }

    def Activated(self):
        from EletricaLogic.Wiring import WiringManager
        from PySide2 import QtWidgets
        lengths = WiringManager.calculate_circuit_lengths()
        
        msg = "--- Resumo de Fiacao ---\n"
        for c, l in lengths.items():
            msg += f"Circuito {c}: {l/1000.0:.2f} metros\n"
        
        QtWidgets.QMessageBox.information(None, "Relatorio de Fiacao", msg)

class PrepareIFC:
    """Comando para preparar a exportacao BIM/IFC"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Preparar IFC',
            'ToolTip': 'Mapeia propriedades para o padrao internacional IFC4'
        }

    def Activated(self):
        from EletricaLogic.IFC import IFCExportManager
        IFCExportManager.prepare_for_ifc()
        return

class GenerateTags:
    """Comando para gerar etiquetas de identificacao de circuito nos objetos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Etiquetas de Circuito',
            'ToolTip': 'Cria textos de identificacao (Ex: C1) ao lado de cada componente'
        }

    def Activated(self):
        from EletricaLogic.Tagging import TagManager
        TagManager.generate_circuit_tags()
        return

class GenerateWireSymbols:
    """Comando para gerar simbolos de fios (Tick Marks) nos eletrodutos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Símbolos de Fiação',
            'ToolTip': 'Desenha símbolos de Fase, Neutro e Terra sobre os eletrodutos'
        }

    def Activated(self):
        from EletricaLogic.Annotations import AnnotationManager
        selection = FreeCADGui.Selection.getSelection()
        
        if not selection:
            # Se nada selecionado, processar todos os eletrodutos
            for obj in FreeCAD.ActiveDocument.Objects:
                if hasattr(obj, "CircuitosPassantes"):
                    AnnotationManager.create_tick_marks(obj)
        else:
            for obj in selection:
                AnnotationManager.create_tick_marks(obj)
        return

class InsertTUE:
    """Comando para inserir equipamentos de uso especifico (Chuveiro, AC, etc)"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Equipamento Especial (TUE)',
            'ToolTip': 'Insere chuveiros, ar condicionado e outros com carga definida'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Equipment import EquipmentManager
        
        presets = EquipmentManager.get_tue_presets()
        choice, ok = QtWidgets.QInputDialog.getItem(None, "Inserir TUE", "Selecione o equipamento:", list(presets.keys()), 0, False)
        
        if ok:
            EquipmentManager.insert_tue(choice)
            FreeCAD.Console.PrintMessage(f"Equipamento {choice} inserido.\n")

class ApplyHeatmap:
    """Comando para aplicar mapa de calor nos eletrodutos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Mapa de Calor (Inspeção)',
            'ToolTip': 'Colore eletrodutos baseado na ocupação (Verde/Vermelho)'
        }

    def Activated(self):
        from EletricaLogic.Visuals import VisualManager
        VisualManager.apply_voltage_drop_heatmap()

class ManageBoxes:
    """Comando para calcular caixas de passagem"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Calcular Caixas de Passagem',
            'ToolTip': 'Conta as caixas 4x2 e Octogonais baseadas nos componentes'
        }

    def Activated(self):
        from EletricaLogic.Equipment import EquipmentManager
        from PySide2 import QtWidgets
        c4x2, cocto = EquipmentManager.add_boxes_to_all()
        QtWidgets.QMessageBox.information(None, "Quantitativo de Caixas", f"Projeto Analisado:\n- Caixas 4x2: {c4x2}\n- Caixas Octogonais (Teto): {cocto}")

class CheckConduitFill:
    """Comando para verificar a ocupacao dos eletrodutos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Verificar Ocupacao de Tubos',
            'ToolTip': 'Calcula se os fios cabem nos eletrodutos (Max 40%)'
        }

    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        from PySide2 import QtWidgets
        alerts = ConduitManager.check_all_conduits_fill()
        
        if alerts:
            msg = "\n".join(alerts)
            QtWidgets.QMessageBox.warning(None, "Alerta de Ocupacao", msg)
        else:
            QtWidgets.QMessageBox.information(None, "Ocupacao OK", "Todos os eletrodutos estao dentro dos limites da NBR 5410.")

class GenerateBOM:
    """Comando para gerar a lista de materiais completa"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Lista de Materiais',
            'ToolTip': 'Cria uma planilha com o quantitativo de componentes, tubos e cabos'
        }

    def Activated(self):
        from EletricaLogic.BOM import BOMManager
        BOMManager.generate_global_bom()
        return

FreeCADGui.addCommand('Eletrica_InsertSocket', InsertSocket())
FreeCADGui.addCommand('Eletrica_InsertLight', InsertLight())
FreeCADGui.addCommand('Eletrica_CreateConduit', CreateConduit())
FreeCADGui.addCommand('Eletrica_GenerateLoadSchedule', GenerateLoadSchedule())
FreeCADGui.addCommand('Eletrica_GenerateLegend', GenerateLegend())
FreeCADGui.addCommand('Eletrica_OpenSettings', OpenSettings())
FreeCADGui.addCommand('Eletrica_AnalyzeSpaceLighting', AnalyzeSpaceLighting())
FreeCADGui.addCommand('Eletrica_BalancePhases', BalancePhases())
FreeCADGui.addCommand('Eletrica_CalculateWiring', CalculateWiring())
FreeCADGui.addCommand('Eletrica_PrepareIFC', PrepareIFC())
FreeCADGui.addCommand('Eletrica_CreateTechnicalSheet', CreateTechnicalSheet())
FreeCADGui.addCommand('Eletrica_GenerateTags', GenerateTags())
FreeCADGui.addCommand('Eletrica_CheckConduitFill', CheckConduitFill())
FreeCADGui.addCommand('Eletrica_GenerateBOM', GenerateBOM())
FreeCADGui.addCommand('Eletrica_GenerateWireSymbols', GenerateWireSymbols())
FreeCADGui.addCommand('Eletrica_InsertTUE', InsertTUE())
FreeCADGui.addCommand('Eletrica_ApplyHeatmap', ApplyHeatmap())
FreeCADGui.addCommand('Eletrica_ManageBoxes', ManageBoxes())
