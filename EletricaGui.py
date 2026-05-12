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

FreeCADGui.addCommand('Eletrica_InsertSocket', InsertSocket())
FreeCADGui.addCommand('Eletrica_InsertLight', InsertLight())
