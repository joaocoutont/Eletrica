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

FreeCADGui.addCommand('Eletrica_InsertSocket', InsertSocket())
FreeCADGui.addCommand('Eletrica_InsertLight', InsertLight())
FreeCADGui.addCommand('Eletrica_CreateConduit', CreateConduit())
FreeCADGui.addCommand('Eletrica_GenerateLoadSchedule', GenerateLoadSchedule())
FreeCADGui.addCommand('Eletrica_GenerateLegend', GenerateLegend())
FreeCADGui.addCommand('Eletrica_OpenSettings', OpenSettings())
