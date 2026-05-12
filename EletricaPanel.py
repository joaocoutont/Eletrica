# Interface de Gerenciamento da Biblioteca Eletrica
from PySide2 import QtCore, QtGui, QtWidgets
import FreeCAD
import FreeCADGui
from EletricaLogic.Library import LibraryManager

class LibraryPanel:
    def __init__(self):
        self.manager = LibraryManager()
        self.form = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.form)
        
        # Titulo
        self.label = QtWidgets.QLabel("Biblioteca 3D HRC")
        self.label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        self.layout.addWidget(self.label)
        
        # Lista de componentes
        self.list_widget = QtWidgets.QListWidget()
        self.refresh_list()
        self.layout.addWidget(self.list_widget)
        
        # Botao Inserir
        self.btn_insert = QtWidgets.QPushButton("Inserir no Projeto")
        self.btn_insert.clicked.connect(self.on_insert)
        self.btn_insert.setMinimumHeight(40)
        self.btn_insert.setStyleSheet("background-color: #2c3e50; color: white; border-radius: 5px;")
        self.layout.addWidget(self.btn_insert)
        
        # Info
        self.info = QtWidgets.QLabel("Dica: Selecione um item e clique em Inserir.")
        self.info.setWordWrap(True)
        self.layout.addWidget(self.info)

    def refresh_list(self):
        self.list_widget.clear()
        components = self.manager.list_components()
        for c in components:
            self.list_widget.addItem(c)

    def on_insert(self):
        selected = self.list_widget.currentItem()
        if not selected:
            FreeCAD.Console.PrintWarning("Selecione um item da lista primeiro.\n")
            return
        
        filename = selected.text()
        self.manager.insert_component(filename)

# Comando para abrir o painel
class OpenLibraryCommand:
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Navegador de Biblioteca',
            'ToolTip': 'Abre o navegador de componentes 3D'
        }

    def Activated(self):
        # Adicionar o painel como um DockWidget no FreeCAD
        mw = FreeCADGui.getMainWindow()
        panel = LibraryPanel()
        dock = QtWidgets.QDockWidget("Eletrica - Biblioteca", mw)
        dock.setWidget(panel.form)
        mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

FreeCADGui.addCommand('Eletrica_OpenLibrary', OpenLibraryCommand())
