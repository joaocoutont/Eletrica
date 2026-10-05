import unittest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Save original modules so we can restore them in tearDownModule
import types
original_freecad = sys.modules.get("FreeCAD")
original_freecad_gui = sys.modules.get("FreeCADGui")
original_part = sys.modules.get("Part")

class MockDocObj:
    def __init__(self, name):
        self.Name = name
        self.Label = name
        self._props = {}
        self.Group = []
        self.InList = []
        self.Type = ""
    def addProperty(self, prop_type, name, group, desc=""):
        self._props[name] = {"type": prop_type, "group": group, "desc": desc}
        setattr(self, name, None)
        return self
    def hasattr(self, name):
        return hasattr(self, name)
    def addObject(self, obj):
        self.Group.append(obj)
        if hasattr(obj, "InList") and isinstance(obj.InList, list):
            if self not in obj.InList:
                obj.InList.append(self)
    def isDerivedFrom(self, class_name):
        if class_name == "App::DocumentObjectGroup":
            return self.Type == "App::DocumentObjectGroup"
        return False
    @property
    def OutList(self):
        return self.Group

class MockDocument:
    def __init__(self, name="doc"):
        self.Name = name
        self.Objects = []
    def getObject(self, name):
        for o in self.Objects:
            if o.Name == name:
                return o
        return None
    def addObject(self, type_name, obj_name):
        o = MockDocObj(obj_name)
        o.Type = type_name
        self.Objects.append(o)
        return o
    def removeObject(self, name):
        self.Objects = [o for o in self.Objects if o.Name != name]
    def copyObject(self, obj, recursive=True):
        new_obj = MockDocObj(obj.Name + "_copy")
        new_obj.Label = obj.Label
        new_obj.Type = getattr(obj, "Type", "")
        for k, v in obj.__dict__.items():
            if k not in ["Name", "Label", "Group", "InList"]:
                setattr(new_obj, k, v)
        self.Objects.append(new_obj)
        return new_obj
    def recompute(self):
        pass

class MockProgressIndicator:
    def start(self, label, steps): pass
    def next(self): pass
    def stop(self): pass

class MockShape:
    def __init__(self):
        self.brep_data = ""
    def importBrepFromString(self, data):
        self.brep_data = data

# Setup mocks in sys.modules using delegation wrappers
class FreeCADWrapper:
    def __init__(self, real_module=None):
        self._real = real_module
        self.ActiveDocument = None
        self._documents = {}
        
        if real_module is not None:
            self.Console = getattr(real_module, "Console", None)
            self.Base = getattr(real_module, "Base", None)
            self.GuiUp = getattr(real_module, "GuiUp", False)
        
        if not hasattr(self, "Console") or self.Console is None:
            self.Console = types.SimpleNamespace(
                PrintMessage=lambda msg: None,
                PrintWarning=lambda msg: None,
                PrintError=lambda msg: None
            )
        if not hasattr(self, "Base") or self.Base is None:
            self.Base = types.SimpleNamespace(
                ProgressIndicator=MockProgressIndicator
            )
        if not hasattr(self, "GuiUp") or self.GuiUp is None:
            self.GuiUp = False

    def newDocument(self, name="doc"):
        d = MockDocument(name)
        self._documents[name] = d
        self.ActiveDocument = d
        return d

    def getDocument(self, name):
        return self._documents.get(name)

    def setActiveDocument(self, name):
        if name in self._documents:
            self.ActiveDocument = self._documents[name]

    def closeDocument(self, name):
        if name in self._documents:
            del self._documents[name]
            if self.ActiveDocument and self.ActiveDocument.Name == name:
                self.ActiveDocument = None

    def getImportType(self, t):
        return []

    def __getattr__(self, name):
        if self._real is not None:
            return getattr(self._real, name)
        raise AttributeError(f"Mock FreeCAD has no attribute '{name}'")

class FreeCADGuiWrapper:
    def __init__(self, real_module=None):
        self._real = real_module
        self.Selection = types.SimpleNamespace(
            getSelection=lambda: []
        )
    def __getattr__(self, name):
        if self._real is not None:
            return getattr(self._real, name)
        raise AttributeError(f"Mock FreeCADGui has no attribute '{name}'")

class PartWrapper:
    def __init__(self, real_module=None):
        self._real = real_module
        self.Shape = MockShape
        self.makeCompound = lambda shapes: MockShape()
    def __getattr__(self, name):
        if self._real is not None:
            return getattr(self._real, name)
        raise AttributeError(f"Mock Part has no attribute '{name}'")

sys.modules["FreeCAD"] = FreeCADWrapper(original_freecad)
sys.modules["FreeCADGui"] = FreeCADGuiWrapper(original_freecad_gui)
sys.modules["Part"] = PartWrapper(original_part)


def tearDownModule():
    # Restore original modules at the end of the test module to avoid side effects
    for key, val in [("FreeCAD", original_freecad), ("FreeCADGui", original_freecad_gui), ("Part", original_part)]:
        if val is None:
            sys.modules.pop(key, None)
        else:
            sys.modules[key] = val



# Mock FreeCAD objects for testing
class MockObject:
    def __init__(self, label, tipo_bim=None, potencia=None):
        self.Label = label
        self.Name = label.replace(" ", "_")
        if tipo_bim: self.TipoBIM = tipo_bim
        if potencia: self.Potencia = potencia
        self._props = {}

    def addProperty(self, prop_type, name, group, desc):
        self._props[name] = {"type": prop_type, "group": group, "desc": desc}
        setattr(self, name, None)
        return self

    def hasattr(self, name):
        return hasattr(self, name)

class MockDoc:
    def __init__(self):
        self.Objects = []
    def getObject(self, name):
        for o in self.Objects:
            if o.Name == name: return o
        return None


class TestIFCIntegration(unittest.TestCase):
    
    def test_property_mapping_logic(self):
        # Como o IFC.py importa FreeCAD, precisamos mockar o módulo se estivermos fora dele
        # Mas aqui vamos testar a lógica de mapeamento indiretamente ou garantir que o arquivo carrega
        try:
            from EletricaLogic.IFC import IFC_TYPE_MAP, PROP_MAP
            self.assertIn("Tomada", IFC_TYPE_MAP)
            self.assertEqual(IFC_TYPE_MAP["Tomada"][0], "IfcOutlet")
            
            self.assertIn("Potencia", PROP_MAP)
            self.assertEqual(PROP_MAP["Potencia"][0], "NominalPower")
        except ImportError:
            self.skipTest("FreeCAD module not available for full integration test")

    def test_import_reference_file_ifc_sys_path(self):
        import tempfile
        import shutil
        
        # Cria estrutura de diretórios temporária para simular o Mod/BIM
        temp_home = tempfile.mkdtemp()
        bim_path = os.path.join(temp_home, "Mod", "BIM")
        os.makedirs(os.path.join(bim_path, "importers"), exist_ok=True)

        import FreeCAD
        orig_getHomePath = getattr(FreeCAD, "getHomePath", None)
        orig_getUserAppDataDir = getattr(FreeCAD, "getUserAppDataDir", None)
        
        FreeCAD.getHomePath = lambda: temp_home
        FreeCAD.getUserAppDataDir = lambda: None

        from EletricaGuiCommands.ProjectSetup import import_reference_file
        
        # Cria um arquivo temporário com extensão .ifc
        with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
            tmp_path = tmp.name
        
        from EletricaGuiCommands import ProjectSetup
        original_widgets = ProjectSetup.QtWidgets
        ProjectSetup.QtWidgets = None

        try:
            # Salva o sys.path original e remove caminhos do BIM temporariamente
            original_sys_path = list(sys.path)
            sys.path = [p for p in sys.path if "BIM" not in p]
            
            # Executa a função (ela tentará importar no console e falhará silenciosamente, mas adicionará o path antes)
            import_reference_file("IFC", tmp_path)
            
            # Verifica se algum caminho do BIM foi adicionado
            has_bim = any("BIM" in p for p in sys.path)
            self.assertTrue(has_bim, "Caminho do BIM não foi adicionado ao sys.path durante importação de IFC")
        finally:
            ProjectSetup.QtWidgets = original_widgets
            # Restaura o sys.path e remove o arquivo temporário e diretório temporário
            sys.path = original_sys_path
            if orig_getHomePath is not None:
                FreeCAD.getHomePath = orig_getHomePath
            if orig_getUserAppDataDir is not None:
                FreeCAD.getUserAppDataDir = orig_getUserAppDataDir
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            try:
                shutil.rmtree(temp_home)
            except Exception:
                pass

    def test_import_ifc_as_lightweight_reference(self):
        import FreeCAD
        import sys
        import tempfile
        import types
        from EletricaGuiCommands.ProjectSetup import import_ifc_as_lightweight_reference, import_reference_file

        # Salva o módulo original
        original_ifcopenshell = sys.modules.get("ifcopenshell", None)
        
        try:
            # 1. Configurar dados geométricos mockados (Wall, Slab, e Opening para ser descartado)
            mock_geom_wall = types.SimpleNamespace(
                id=123,
                type="IfcWallStandardCase",
                geometry=types.SimpleNamespace(
                    brep_data="DB 1.0\n..."
                )
            )
            mock_geom_slab = types.SimpleNamespace(
                id=124,
                type="IfcSlab",
                geometry=types.SimpleNamespace(
                    brep_data="DB 1.0\n..."
                )
            )
            mock_geom_opening = types.SimpleNamespace(
                id=125,
                type="IfcOpeningElement",
                geometry=types.SimpleNamespace(
                    brep_data="DB 1.0\n..."
                )
            )
            
            class MockIterator:
                def __init__(self, settings, ifc_file):
                    self.items = [mock_geom_wall, mock_geom_slab, mock_geom_opening]
                    self.idx = 0
                def initialize(self):
                    return True
                def get(self):
                    return self.items[self.idx]
                def next(self):
                    if self.idx < len(self.items) - 1:
                        self.idx += 1
                        return True
                    return False
                    
            mock_ifcopenshell = types.SimpleNamespace(
                open=lambda path: types.SimpleNamespace(
                    by_type=lambda t: ["mock_product"]
                ),
                geom=types.SimpleNamespace(
                    settings=lambda: types.SimpleNamespace(
                        set=lambda param, val: None,
                        USE_BREP_DATA="USE_BREP_DATA",
                        USE_WORLD_COORDS="USE_WORLD_COORDS"
                    ),
                    iterator=MockIterator
                )
            )
            sys.modules["ifcopenshell"] = mock_ifcopenshell
            sys.modules["ifcopenshell.geom"] = mock_ifcopenshell.geom
            
            # 2. Criar documento mock e executar importador
            doc = FreeCAD.newDocument("TestLightweightDoc")
            FreeCAD.ActiveDocument = doc
            
            with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
                tmp_path = tmp.name
                
            try:
                imported_objs = import_ifc_as_lightweight_reference(tmp_path, "TestLightweightDoc")
                
                # Deve retornar 3 objetos: o grupo, e os dois subgrupos criados (Paredes, Lajes e Tetos)
                # O OpeningElement deve ter sido descartado
                self.assertEqual(len(imported_objs), 3)
                
                group = imported_objs[0]
                self.assertEqual(group.Type, "App::DocumentObjectGroup")
                self.assertTrue(group.Label.startswith("Referência IFC -"))
                
                # O grupo deve conter os dois objetos importados (Paredes e Lajes)
                self.assertEqual(len(group.Group), 2)
                self.assertEqual(group.Group[0], imported_objs[1])
                self.assertEqual(group.Group[1], imported_objs[2])
                
                self.assertEqual(imported_objs[1].Label, "Paredes")
                self.assertEqual(imported_objs[1].Type, "App::DocumentObjectGroup")
                # Paredes subgroup should contain 1 individual Part::Feature element
                self.assertEqual(len(imported_objs[1].Group), 1)
                wall_elem = imported_objs[1].Group[0]
                self.assertEqual(wall_elem.Type, "Part::Feature")
                self.assertTrue(wall_elem.Name.endswith("_123"))
                self.assertTrue(wall_elem.Label.startswith("Parede #123"))

                self.assertEqual(imported_objs[2].Label, "Lajes e Tetos")
                self.assertEqual(imported_objs[2].Type, "App::DocumentObjectGroup")
                # Lajes e Tetos subgroup should contain 1 individual Part::Feature element
                self.assertEqual(len(imported_objs[2].Group), 1)
                slab_elem = imported_objs[2].Group[0]
                self.assertEqual(slab_elem.Type, "Part::Feature")
                self.assertTrue(slab_elem.Name.endswith("_124"))
                self.assertTrue(slab_elem.Label.startswith("Laje #124"))
                
                # 3. Testar a rota do import_reference_file
                config = {"ifc_importer": "Referência Leve (rápido, sem objetos individuais)"}
                doc.Objects = []
                
                res = import_reference_file("IFC", tmp_path, config)
                self.assertEqual(len(res), 3)
                self.assertEqual(res[0].Type, "App::DocumentObjectGroup")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        finally:
            if original_ifcopenshell is not None:
                sys.modules["ifcopenshell"] = original_ifcopenshell
            elif "ifcopenshell" in sys.modules:
                del sys.modules["ifcopenshell"]
            if "ifcopenshell.geom" in sys.modules:
                del sys.modules["ifcopenshell.geom"]

    def test_import_ifc_lightweight_canceled(self):
        import FreeCAD
        import sys
        import tempfile
        import types
        from EletricaGuiCommands.ProjectSetup import import_ifc_as_lightweight_reference, import_reference_file, ImportCanceledError
        
        # Salva estados originais
        original_ifcopenshell = sys.modules.get("ifcopenshell", None)
        original_gui_up = getattr(FreeCAD, "GuiUp", None)
        
        # Ativa GuiUp para entrar no caminho do diálogo
        FreeCAD.GuiUp = True
        
        try:
            # Mock ifcopenshell
            mock_geom = types.SimpleNamespace(
                id=123,
                geometry=types.SimpleNamespace(
                    brep_data="DB 1.0\n..."
                )
            )
            class MockIterator:
                def __init__(self, settings, ifc_file):
                    pass
                def initialize(self):
                    return True
                def get(self):
                    return mock_geom
                def next(self):
                    return True # Continua retornando True para testar break no cancelamento
                    
            mock_ifcopenshell = types.SimpleNamespace(
                open=lambda path: types.SimpleNamespace(
                    by_type=lambda t: ["mock_product"]
                ),
                geom=types.SimpleNamespace(
                    settings=lambda: types.SimpleNamespace(
                        set=lambda param, val: None,
                        USE_BREP_DATA="USE_BREP_DATA",
                        USE_WORLD_COORDS="USE_WORLD_COORDS"
                    ),
                    iterator=MockIterator
                )
            )
            sys.modules["ifcopenshell"] = mock_ifcopenshell
            sys.modules["ifcopenshell.geom"] = mock_ifcopenshell.geom
            
            # Mock QtWidgets e QProgressDialog
            from EletricaGuiCommands import ProjectSetup
            original_widgets = ProjectSetup.QtWidgets
            
            class MockProgressDialog:
                def __init__(self, label="", cancel="", min_val=0, max_val=100, parent=None):
                    self._max = max_val
                def setWindowTitle(self, title): pass
                def setWindowModality(self, modality): pass
                def setMinimumDuration(self, duration): pass
                def setAutoClose(self, val): pass
                def setAutoReset(self, val): pass
                def setMaximum(self, val):
                    self._max = val
                def maximum(self):
                    return self._max
                def setValue(self, val): pass
                def show(self): pass
                def setLabelText(self, text): pass
                def wasCanceled(self):
                    return True # Simula clique em Cancelar
                def close(self): pass
                
            class MockApp:
                @staticmethod
                def processEvents():
                    pass
                    
            mock_widgets = types.SimpleNamespace(
                QProgressDialog=MockProgressDialog,
                QApplication=MockApp
            )
            ProjectSetup.QtWidgets = mock_widgets
            
            # Executa teste
            doc = FreeCAD.newDocument("TestCanceledDoc")
            FreeCAD.ActiveDocument = doc
            
            with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
                tmp_path = tmp.name
                
            try:
                # 1. Testando importador direto (deve levantar ImportCanceledError)
                with self.assertRaises(ImportCanceledError):
                    import_ifc_as_lightweight_reference(tmp_path, "TestCanceledDoc")
                    
                # 2. Testando rota via import_reference_file (deve retornar lista vazia)
                config = {"ifc_importer": "Referência Leve (rápido, sem objetos individuais)"}
                res = import_reference_file("IFC", tmp_path, config)
                self.assertEqual(res, [])
            finally:
                ProjectSetup.QtWidgets = original_widgets
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        finally:
            if original_gui_up is not None:
                FreeCAD.GuiUp = original_gui_up
            elif hasattr(FreeCAD, "GuiUp"):
                delattr(FreeCAD, "GuiUp")
                
            if original_ifcopenshell is not None:
                sys.modules["ifcopenshell"] = original_ifcopenshell
            elif "ifcopenshell" in sys.modules:
                del sys.modules["ifcopenshell"]
            if "ifcopenshell.geom" in sys.modules:
                del sys.modules["ifcopenshell.geom"]

    def test_reference_locking_and_observer(self):
        class MockViewObject:
            def __init__(self):
                self.Selectable = True

        class MockDocumentObject:
            def __init__(self, name):
                self.Name = name
                self.Label = name
                self.LockedReference = False
                self.ViewObject = MockViewObject()
                self.OutList = []

        parent = MockDocumentObject("ParentRef")
        child1 = MockDocumentObject("ChildRef1")
        child2 = MockDocumentObject("ChildRef2")
        parent.OutList = [child1, child2]

        import sys
        import types
        if "PySide" not in sys.modules:
            try:
                import PySide6
                sys.modules["PySide"] = PySide6
            except ImportError:
                mock_pyside = types.SimpleNamespace()
                mock_pyside.QtGui = types.SimpleNamespace()
                mock_pyside.QtCore = types.SimpleNamespace()
                class MockQObject:
                    def __init__(self, *args, **kwargs): pass
                mock_pyside.QtCore.QObject = MockQObject
                sys.modules["PySide"] = mock_pyside


        from GeometryScripts.socket_gui import EletricaDocumentObserver
        observer = EletricaDocumentObserver()

        parent.LockedReference = True
        observer.slotChangedObject(parent, "LockedReference")

        self.assertFalse(parent.ViewObject.Selectable)

        self.assertTrue(child1.LockedReference)
        observer.slotChangedObject(child1, "LockedReference")
        self.assertFalse(child1.ViewObject.Selectable)

        self.assertTrue(child2.LockedReference)
        observer.slotChangedObject(child2, "LockedReference")
        self.assertFalse(child2.ViewObject.Selectable)

        from EletricaGuiCommands.ProjectSetup import ToggleReferenceLock
        cmd = ToggleReferenceLock()

        class MockDocForLockToggle:
            def __init__(self):
                self.Objects = [parent, child1, child2]
            def recompute(self):
                pass

        import FreeCAD
        orig_doc = FreeCAD.ActiveDocument
        mock_doc = MockDocForLockToggle()
        FreeCAD.ActiveDocument = mock_doc

        try:
            import sys
            import types
            
            orig_gui = sys.modules.get("FreeCADGui")
            class MockMainWindow:
                def statusBar(self):
                    class MockStatusBar:
                        def showMessage(self, msg): pass
                    return MockStatusBar()
            
            sys.modules["FreeCADGui"] = types.SimpleNamespace(
                getMainWindow=lambda: MockMainWindow()
            )

            cmd.Activated()

            self.assertFalse(parent.LockedReference)
            
            if orig_gui:
                sys.modules["FreeCADGui"] = orig_gui
            else:
                del sys.modules["FreeCADGui"]
        finally:
            FreeCAD.ActiveDocument = orig_doc

    def test_reload_reference_ifc(self):
        import FreeCAD
        import FreeCADGui
        import Part
        from unittest.mock import patch
        from EletricaGuiCommands.ProjectSetup import ReloadReference

        dummy_file = "dummy_reference.ifc"
        doc = FreeCAD.newDocument("TestMainDoc")
        FreeCAD.ActiveDocument = doc

        ref_group = doc.addObject("App::DocumentObjectGroup", "Referenca_Leve_Grupo_dummy")
        ref_group.Label = "Referência IFC - dummy"
        ref_group.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
        ref_group.addProperty("App::PropertyString", "ReferenceSource", "BIM_Referencia")
        ref_group.OriginalFile = dummy_file
        ref_group.ReferenceSource = "IFC"

        # Categoria Paredes como subgrupo
        walls_group = doc.addObject("App::DocumentObjectGroup", "RefLeve_dummy_Paredes")
        walls_group.Label = "Paredes"
        walls_group.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
        walls_group.OriginalFile = dummy_file
        ref_group.addObject(walls_group)

        # Parede individual
        wall_obj = doc.addObject("Part::Feature", "RefElem_dummy_123")
        wall_obj.Label = "Parede #123"
        wall_obj.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
        wall_obj.OriginalFile = dummy_file
        walls_group.addObject(wall_obj)

        initial_shape = Part.Shape()
        initial_shape.brep_data = "initial_wall"
        wall_obj.Shape = initial_shape

        FreeCADGui.Selection.getSelection = lambda: [ref_group]

        def mock_import_reference_file(source, file_path, config=None):
            active_doc = FreeCAD.ActiveDocument
            self.assertEqual(active_doc.Name, "Temp_ReloadReference")

            t_group = active_doc.addObject("App::DocumentObjectGroup", "TempGroup")
            t_group.Label = "Referência IFC - temp"

            t_walls_group = active_doc.addObject("App::DocumentObjectGroup", "TempWalls")
            t_walls_group.Label = "Paredes"
            t_group.addObject(t_walls_group)

            t_wall = active_doc.addObject("Part::Feature", "RefElem_dummy_123")
            t_wall.Label = "Parede #123"
            new_shape = Part.Shape()
            new_shape.brep_data = "new_wall"
            t_wall.Shape = new_shape
            t_walls_group.addObject(t_wall)

            t_slabs_group = active_doc.addObject("App::DocumentObjectGroup", "TempSlabs")
            t_slabs_group.Label = "Lajes e Tetos"
            t_group.addObject(t_slabs_group)

            t_slab = active_doc.addObject("Part::Feature", "RefElem_dummy_124")
            t_slab.Label = "Laje #124"
            slab_shape = Part.Shape()
            slab_shape.brep_data = "new_slab"
            t_slab.Shape = slab_shape
            t_slabs_group.addObject(t_slab)

            return [t_group, t_walls_group, t_slabs_group]

        with patch("os.path.exists", return_value=True), \
             patch("EletricaGuiCommands.ProjectSetup.import_reference_file", side_effect=mock_import_reference_file):
            
            cmd = ReloadReference()
            cmd.Activated()

        self.assertEqual(wall_obj.Shape.brep_data, "new_wall")
        self.assertEqual(wall_obj.OriginalFile, dummy_file)

        children = {c.Label: c for c in ref_group.Group}
        self.assertIn("Lajes e Tetos", children)
        self.assertEqual(children["Lajes e Tetos"].Type, "App::DocumentObjectGroup")
        
        slabs_children = children["Lajes e Tetos"].Group
        self.assertEqual(len(slabs_children), 1)
        self.assertEqual(slabs_children[0].Shape.brep_data, "new_slab")
        self.assertEqual(slabs_children[0].OriginalFile, dummy_file)

        self.assertIsNone(FreeCAD.getDocument("Temp_ReloadReference"))
        self.assertEqual(FreeCAD.ActiveDocument.Name, "TestMainDoc")

    def test_reload_reference_cad(self):
        import FreeCAD
        import FreeCADGui
        from unittest.mock import patch
        from EletricaGuiCommands.ProjectSetup import ReloadReference

        dummy_file = "dummy_reference.dxf"
        doc = FreeCAD.newDocument("TestMainDocCAD")
        FreeCAD.ActiveDocument = doc

        ref_group = doc.addObject("App::DocumentObjectGroup", "Referenca_Leve_Grupo_cad")
        ref_group.Label = "Referência CAD"
        ref_group.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
        ref_group.addProperty("App::PropertyString", "ReferenceSource", "BIM_Referencia")
        ref_group.OriginalFile = dummy_file
        ref_group.ReferenceSource = "CAD"

        line_obj = doc.addObject("Part::Feature", "CADLine")
        line_obj.Label = "Line"
        line_obj.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
        line_obj.OriginalFile = dummy_file
        ref_group.addObject(line_obj)

        FreeCADGui.Selection.getSelection = lambda: [ref_group]

        def mock_import_reference_file(source, file_path, config=None):
            active_doc = FreeCAD.ActiveDocument
            self.assertEqual(active_doc.Name, "Temp_ReloadReference")

            t_obj = active_doc.addObject("Part::Feature", "NewCADLine")
            t_obj.Label = "Line"
            t_obj.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
            t_obj.OriginalFile = dummy_file
            
            return [t_obj]

        with patch("os.path.exists", return_value=True), \
             patch("EletricaGuiCommands.ProjectSetup.import_reference_file", side_effect=mock_import_reference_file):
            
            cmd = ReloadReference()
            cmd.Activated()

        self.assertIsNone(doc.getObject("CADLine"))
        new_copied = doc.getObject("NewCADLine_copy")
        self.assertIsNotNone(new_copied)
        self.assertIn(new_copied, ref_group.Group)
        self.assertEqual(new_copied.OriginalFile, dummy_file)

    def test_reload_reference_file_relocation(self):
        import FreeCAD
        import FreeCADGui
        from unittest.mock import patch, MagicMock
        from EletricaGuiCommands.ProjectSetup import ReloadReference

        old_file = "missing_reference.ifc"
        new_file = "found_reference.ifc"
        doc = FreeCAD.newDocument("TestMainDocReloc")
        FreeCAD.ActiveDocument = doc

        ref_group = doc.addObject("App::DocumentObjectGroup", "Referenca_Leve_Grupo_reloc")
        ref_group.Label = "Referência IFC"
        ref_group.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
        ref_group.addProperty("App::PropertyString", "ReferenceSource", "BIM_Referencia")
        ref_group.OriginalFile = old_file
        ref_group.ReferenceSource = "IFC"

        FreeCADGui.Selection.getSelection = lambda: [ref_group]

        orig_gui_up = getattr(FreeCAD, "GuiUp", False)
        FreeCAD.GuiUp = True

        from EletricaGuiCommands import ProjectSetup
        original_widgets = ProjectSetup.QtWidgets

        mock_msgbox = MagicMock()
        mock_msgbox.Yes = 16384
        mock_msgbox.No = 65536
        mock_msgbox.question = MagicMock(return_value=mock_msgbox.Yes)
        
        mock_filedialog = MagicMock()
        mock_filedialog.getOpenFileName = MagicMock(return_value=(new_file, "IFC Files (*.ifc)"))

        mock_widgets = MagicMock()
        mock_widgets.QMessageBox = mock_msgbox
        mock_widgets.QFileDialog = mock_filedialog
        ProjectSetup.QtWidgets = mock_widgets

        def mock_exists(path):
            if path == old_file:
                return False
            if path == new_file:
                return True
            return False

        def mock_import_reference_file(source, file_path, config=None):
            active_doc = FreeCAD.ActiveDocument
            t_group = active_doc.addObject("App::DocumentObjectGroup", "TempGroup")
            return [t_group]

        try:
            with patch("os.path.exists", side_effect=mock_exists), \
                 patch("EletricaGuiCommands.ProjectSetup.import_reference_file", side_effect=mock_import_reference_file):
                
                cmd = ReloadReference()
                cmd.Activated()
        finally:
            FreeCAD.GuiUp = orig_gui_up
            ProjectSetup.QtWidgets = original_widgets

        self.assertEqual(ref_group.OriginalFile, new_file)

    def test_ifc_category_filtering(self):
        import FreeCAD
        import sys
        import tempfile
        import types
        from EletricaGuiCommands.ProjectSetup import import_ifc_as_lightweight_reference, ReloadReference

        # Salva o módulo original
        original_ifcopenshell = sys.modules.get("ifcopenshell", None)
        
        try:
            # 1. Configurar dados geométricos mockados (Wall, Slab, Door, Beam, Outros)
            mock_geom_wall = types.SimpleNamespace(
                id=123,
                type="IfcWallStandardCase",
                geometry=types.SimpleNamespace(brep_data="brep_wall")
            )
            mock_geom_slab = types.SimpleNamespace(
                id=124,
                type="IfcSlab",
                geometry=types.SimpleNamespace(brep_data="brep_slab")
            )
            mock_geom_door = types.SimpleNamespace(
                id=125,
                type="IfcDoor",
                geometry=types.SimpleNamespace(brep_data="brep_door")
            )
            mock_geom_beam = types.SimpleNamespace(
                id=126,
                type="IfcBeam",
                geometry=types.SimpleNamespace(brep_data="brep_beam")
            )
            mock_geom_other = types.SimpleNamespace(
                id=127,
                type="IfcFixture",
                geometry=types.SimpleNamespace(brep_data="brep_other")
            )
            
            class MockIterator:
                def __init__(self, settings, ifc_file):
                    self.items = [mock_geom_wall, mock_geom_slab, mock_geom_door, mock_geom_beam, mock_geom_other]
                    self.idx = 0
                def initialize(self):
                    return True
                def get(self):
                    return self.items[self.idx]
                def next(self):
                    if self.idx < len(self.items) - 1:
                        self.idx += 1
                        return True
                    return False
                    
            mock_ifcopenshell = types.SimpleNamespace(
                open=lambda path: types.SimpleNamespace(
                    by_type=lambda t: ["mock_product"]
                ),
                geom=types.SimpleNamespace(
                    settings=lambda: types.SimpleNamespace(
                        set=lambda param, val: None,
                        USE_BREP_DATA="USE_BREP_DATA",
                        USE_WORLD_COORDS="USE_WORLD_COORDS"
                    ),
                    iterator=MockIterator
                )
            )
            sys.modules["ifcopenshell"] = mock_ifcopenshell
            sys.modules["ifcopenshell.geom"] = mock_ifcopenshell.geom
            
            # Criar documento mock e executar importador com apenas "Paredes" e "Portas e Janelas"
            doc = FreeCAD.newDocument("TestCategoryFilterDoc")
            FreeCAD.ActiveDocument = doc
            
            with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
                tmp_path = tmp.name
                
            try:
                config = {
                    "ifc_categories": ["Paredes", "Portas e Janelas"]
                }
                imported_objs = import_ifc_as_lightweight_reference(tmp_path, "TestCategoryFilterDoc", config)
                
                # Deve retornar o grupo principal e as duas sub-estruturas selecionadas:
                # 1. Grupo principal
                # 2. Subgrupo "Paredes"
                # 3. Part::Feature "Portas e Janelas"
                self.assertEqual(len(imported_objs), 3)
                
                labels = [obj.Label for obj in imported_objs]
                self.assertIn("Paredes", labels)
                self.assertIn("Portas e Janelas", labels)
                self.assertNotIn("Lajes e Tetos", labels)
                self.assertNotIn("Estrutura", labels)
                self.assertNotIn("Outros", labels)
                
                # Paredes group must contain 1 wall elem
                p_group = next(obj for obj in imported_objs if obj.Label == "Paredes")
                self.assertEqual(len(p_group.Group), 1)
                self.assertEqual(p_group.Group[0].Label, "Parede #123")
                
                # Test ReloadReference category mapping
                # Simular que recarregamos o vínculo a partir de um ref_group contendo apenas a categoria "Paredes"
                doc_reload = FreeCAD.newDocument("TestCategoryReloadDoc")
                FreeCAD.ActiveDocument = doc_reload
                
                ref_group = doc_reload.addObject("App::DocumentObjectGroup", "Referenca_Leve_Grupo_mock")
                ref_group.Label = "Referência IFC - mock"
                ref_group.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
                ref_group.addProperty("App::PropertyString", "ReferenceSource", "BIM_Referencia")
                ref_group.OriginalFile = tmp_path
                ref_group.ReferenceSource = "IFC"
                
                walls_group = doc_reload.addObject("App::DocumentObjectGroup", "RefLeve_mock_Paredes")
                walls_group.Label = "Paredes"
                walls_group.addProperty("App::PropertyString", "OriginalFile", "BIM_Referencia")
                walls_group.OriginalFile = tmp_path
                ref_group.addObject(walls_group)
                
                import FreeCADGui
                FreeCADGui.Selection.getSelection = lambda: [ref_group]
                
                # Chamando o comando ReloadReference diretamente
                # Deve recarregar e importar APENAS Paredes, já que é a única categoria atual no ref_group
                cmd = ReloadReference()
                
                # Mock do import_reference_file para capturar qual config foi passada
                captured_config = {}
                from EletricaGuiCommands import ProjectSetup
                original_import = ProjectSetup.import_reference_file
                
                def dummy_import_reference_file(source, file_path, cfg=None):
                    nonlocal captured_config
                    captured_config = cfg
                    return original_import(source, file_path, cfg)
                    
                ProjectSetup.import_reference_file = dummy_import_reference_file
                try:
                    cmd.Activated()
                finally:
                    ProjectSetup.import_reference_file = original_import
                
                # O captured_config deve conter apenas ["Paredes"] em "ifc_categories"
                self.assertIn("ifc_categories", captured_config)
                self.assertEqual(captured_config["ifc_categories"], ["Paredes"])
                
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        finally:
            if original_ifcopenshell is not None:
                sys.modules["ifcopenshell"] = original_ifcopenshell
            elif "ifcopenshell" in sys.modules:
                del sys.modules["ifcopenshell"]
            if "ifcopenshell.geom" in sys.modules:
                del sys.modules["ifcopenshell.geom"]

if __name__ == "__main__":
    unittest.main()
