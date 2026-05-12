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
            msg += f"Sugestao: {result['PointsSuggested']} pontos de luz\n"
            
            QtWidgets.QMessageBox.information(None, "Analise de Iluminacao", msg)
            FreeCAD.Console.PrintMessage(msg)

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
