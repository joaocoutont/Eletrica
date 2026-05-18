import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore

class SelectionBlocker:
    """Bloqueia qualquer seleção no FreeCAD para impedir menus de contexto."""
    def __init__(self):
        self.notAllowedReason = ""

    def allow(self, doc, obj, sub):
        return False

class QtClickFilter(QtCore.QObject):
    """Filtro de eventos Qt para bloquear cliques de mouse no FreeCAD e interceptá-los."""
    def __init__(self, engine):
        super(QtClickFilter, self).__init__()
        self.engine = engine

    def eventFilter(self, watched, event):
        if event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease, QtCore.QEvent.MouseButtonDblClick):
            if event.button() == QtCore.Qt.LeftButton:
                state = "DOWN" if event.type() == QtCore.QEvent.MouseButtonPress else "UP"
                # Converte coordenada Y do Qt para o sistema de coordenadas da viewport do FreeCAD (Coin3D)
                h = watched.height()
                pos = (event.x(), h - event.y())
                
                event_data = {
                    'State': state,
                    'Button': 'BUTTON1',
                    'Position': pos,
                    'Event': event
                }
                
                # Apenas processa o clique real no estado de clique DOWN
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    self.engine.on_click(event_data)
                
                # Aceita o evento no Qt e retorna True para impedir que chegue ao C++ do FreeCAD
                event.accept()
                return True
        return super(QtClickFilter, self).eventFilter(watched, event)

class BIMPlacementEngine:
    """
    Motor v2.2 - Sincronização Total de Snap.
    Garante que a tomada real seja criada exatamente na posição da mira.
    """
    active_engine = None
    CHECKABLE_PLACEMENT_COMMANDS = {
        "Eletrica_InsertSocket",
        "Eletrica_InsertSpecialSocket",
        "Eletrica_InsertModularSet",
    }

    def __init__(self, command_obj, task_panel_class, placement_func):
        self.cmd = command_obj
        self.task_panel_class = task_panel_class
        self.placement_func = placement_func
        
        self.callback = None
        self.kb_callback = None
        self.move_callback = None
        self.gate = SelectionBlocker()
        self.view = None
        self.panel = None
        self.ghost = None
        self.view_params = App.ParamGet("User parameter:BaseApp/Preferences/Selection")
        self.previous_preselection = None
        self.last_status_counter = 0
        
        # Variáveis de Sincronização
        self.last_snap_point = None
        self.last_snap_rot = 0
        self.last_host_object = ""
        self.last_host_sub = ""
        self.last_mouse_pos = None
        self.move_counter = 0
        self.saved_selectable = {}

    def is_quiet_mode(self):
        return bool(getattr(self.cmd, "quiet_placement", True))

    def should_query_view_objects(self):
        if self.is_quiet_mode():
            return False
        return bool(
            getattr(self.cmd, "detect_surfaces", False)
            or getattr(self.cmd, "snap_to_junction_boxes", False)
        )

    def get_command_name(self):
        if hasattr(self.cmd, "command_name") and self.cmd.command_name:
            return self.cmd.command_name
        cls_name = self.cmd.__class__.__name__
        if cls_name == "SocketCommand":
            if getattr(self.cmd, "circuit_type", "") == "TUE (Específico)":
                return "Eletrica_InsertSpecialSocket"
            else:
                return "Eletrica_InsertSocket"
        elif cls_name == "JunctionBoxCommand":
            return "Eletrica_JunctionBox"
        return None

    @staticmethod
    def set_command_action_checked(cmd_name, checked):
        if not cmd_name:
            return
        try:
            mw = Gui.getMainWindow()
            if not mw:
                return
            actions = []
            found = mw.findChild(QtGui.QAction, cmd_name)
            if found:
                actions.append(found)
            for action in mw.findChildren(QtGui.QAction):
                try:
                    if action.objectName() == cmd_name or action.data() == cmd_name:
                        if action not in actions:
                            actions.append(action)
                except Exception:
                    pass

            for action in actions:
                action.blockSignals(True)
                if not action.isCheckable():
                    action.setCheckable(True)
                action.setChecked(checked)
                action.blockSignals(False)
        except Exception as e:
            print(f"Error updating checked state for {cmd_name}: {e}")

    @classmethod
    def clear_checkable_actions(cls, except_name=None):
        for name in cls.CHECKABLE_PLACEMENT_COMMANDS:
            if name != except_name:
                cls.set_command_action_checked(name, False)

    def set_action_checked(self, checked):
        cmd_name = self.get_command_name()
        if checked:
            self.clear_checkable_actions(except_name=cmd_name)
        self.set_command_action_checked(cmd_name, checked)

    def start(self):
        if BIMPlacementEngine.active_engine is not None:
            try:
                BIMPlacementEngine.active_engine.stop()
            except Exception:
                pass

        try:
            self.view = Gui.ActiveDocument.ActiveView
            self.panel = self.task_panel_class(self.cmd)
            Gui.Control.showDialog(self.panel)

            # Salva o estado de seleção de todos os objetos e torna-os temporariamente não selecionáveis
            self.saved_selectable = {}
            doc = App.ActiveDocument
            if doc:
                for obj in doc.Objects:
                    if getattr(obj, "ViewObject", None) is not None:
                        try:
                            self.saved_selectable[obj.Name] = obj.ViewObject.Selectable
                            obj.ViewObject.Selectable = False
                        except Exception:
                            pass

            try:
                Gui.Selection.addSelectionGate("SELECT None")
            except Exception:
                Gui.Selection.addSelectionGate(self.gate)
            self.disable_preselection()
            self.clear_preselection()
            self.quiet_draft_snapper()
            self.show_placement_status()

            # Instala o filtro Qt para interceptação total de cliques e desvio da engine C++ do FreeCAD
            self.gl_widget = None
            self.qt_filter = None
            try:
                mw = Gui.getMainWindow()
                if mw:
                    # Encontra o MdiArea no FreeCAD de forma segura e portável para Qt5/Qt6
                    mdi_area = None
                    widget_class = None
                    try:
                        from PySide2 import QtWidgets as PySide2Widgets
                        mdi_area = mw.findChild(PySide2Widgets.QMdiArea)
                        widget_class = PySide2Widgets.QWidget
                    except ImportError:
                        try:
                            from PySide6 import QtWidgets as PySide6Widgets
                            mdi_area = mw.findChild(PySide6Widgets.QMdiArea)
                            widget_class = PySide6Widgets.QWidget
                        except ImportError:
                            import PySide.QtGui as PySideQtGui
                            mdi_area = mw.findChild(PySideQtGui.QMdiArea)
                            widget_class = PySideQtGui.QWidget
                    
                    if mdi_area and mdi_area.activeSubWindow():
                        sub_win = mdi_area.activeSubWindow().widget()
                        if sub_win and widget_class:
                            # Procura pelo widget 3D real (geralmente QuarterWidget ou QGLWidget/QOpenGLWidget)
                            candidates = []
                            for child in sub_win.findChildren(widget_class):
                                class_name = child.metaObject().className()
                                if "GL" in class_name or "Quarter" in class_name or "OpenGL" in class_name:
                                    candidates.append(child)
                            if candidates:
                                self.gl_widget = candidates[0]
                            else:
                                self.gl_widget = sub_win

                            if self.gl_widget:
                                self.qt_filter = QtClickFilter(self)
                                self.gl_widget.installEventFilter(self.qt_filter)
                                App.Console.PrintLog(f"Filtro Qt de Clique instalado com sucesso no widget: {self.gl_widget.metaObject().className()}.\n")
            except Exception as e:
                App.Console.PrintError(f"Erro ao instalar filtro Qt de clique: {e}. Usando callback Pivy como fallback.\n")
                self.gl_widget = None
                self.qt_filter = None

            # Fallback Pivy (Apenas se o filtro Qt falhar):
            self.callback = None
            if not self.qt_filter:
                try:
                    from pivy import coin
                    self.callback = self.view.addEventCallbackPivy(
                        coin.SoMouseButtonEvent.getClassTypeId(),
                        self.on_click_pivy
                    )
                except Exception:
                    pass
            self.kb_callback = self.view.addEventCallback("SoKeyboardEvent", self.on_key)
            self.move_callback = self.view.addEventCallback("SoLocation2Event", self.on_move)

            self.ghost = None
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
            BIMPlacementEngine.active_engine = self
            self.set_action_checked(True)
        except Exception:
            BIMPlacementEngine.active_engine = None
            self.clear_checkable_actions()
            try:
                self.restore_preselection()
                self.clear_preselection()
                Gui.Selection.removeSelectionGate()
            except Exception:
                pass
            if self.callback and self.view:
                try:
                    from pivy import coin
                    self.view.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.callback)
                except Exception:
                    pass
            for event_name, callback in [
                ("SoKeyboardEvent", self.kb_callback),
                ("SoLocation2Event", self.move_callback),
            ]:
                if callback and self.view:
                    try:
                        self.view.removeEventCallback(event_name, callback)
                    except Exception:
                        pass
            try:
                Gui.Control.closeDialog()
            except Exception:
                pass
            try:
                QtGui.QApplication.restoreOverrideCursor()
            except Exception:
                pass
            raise

    def disable_preselection(self):
        """Evita mensagens/realces de Face, Edge e Vertex durante a inserção."""
        try:
            self.previous_preselection = self.view_params.GetBool("EnablePreselection", True)
            self.view_params.SetBool("EnablePreselection", False)
        except Exception:
            self.previous_preselection = None
        self.clear_preselection()

    def restore_preselection(self):
        try:
            if self.previous_preselection is not None:
                self.view_params.SetBool("EnablePreselection", self.previous_preselection)
        except Exception:
            pass

    def clear_preselection(self):
        for method_name in ("clearPreselection", "rmvPreselect", "removePreselection"):
            method = getattr(Gui.Selection, method_name, None)
            if method:
                try:
                    method()
                    return
                except Exception:
                    pass

    def show_placement_status(self):
        try:
            mw = Gui.getMainWindow()
            if mw:
                mode = "continuo" if getattr(self.cmd, "continuous_insert", True) else "uma vez"
                label = getattr(self.cmd, "tool_label", "tomada")
                mw.statusBar().showMessage(f"Inserindo {label} ({mode}): clique para posicionar | I alterna | ESC sai", 1000)
        except Exception:
            pass

    def quiet_draft_snapper(self):
        """Esconde rastreadores do Draft Snapper que exibem Object/Edge/Vertex."""
        try:
            snapper = getattr(Gui, "Snapper", None)
            if not snapper:
                return
            if hasattr(snapper, "hide"):
                snapper.hide()
            if hasattr(snapper, "off"):
                try:
                    snapper.off()
                except TypeError:
                    snapper.off(False)
        except Exception:
            pass

    def refresh_ghost_transform(self):
        if not self.ghost or self.last_snap_point is None:
            return
        try:
            z = float(self.cmd.get_final_z()) if hasattr(self.cmd, 'get_final_z') else float(self.cmd.z_level)
            rot = float(self.cmd.rotation)
            point = self.last_snap_point
            self.ghost.Placement = App.Placement(
                App.Vector(point.x, point.y, z),
                App.Rotation(App.Vector(0,0,1), rot)
            )
            Gui.updateGui()
        except Exception:
            pass

    def on_key(self, event_data):
        if event_data['Key'] == 'ESCAPE': self.stop()
        elif event_data['Key'] == 'P' or event_data['Key'] == 'TAB':
            self.toggle_panel()
        elif event_data['Key'] == 'SPACE':
            self.cmd.rotation = (self.cmd.rotation + 90) % 360
            if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
            self.refresh_ghost_transform()
        elif event_data['Key'] == 'H':
            if hasattr(self.cmd, 'cycle_height'):
                self.cmd.cycle_height()
            else:
                alturas = [300, 1100, 2200]; current = self.cmd.z_level; next_idx = 0
                if current < 1100: next_idx = 1
                elif current < 2200: next_idx = 2
                self.cmd.z_level = alturas[next_idx]
            if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
            if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
            self.refresh_ghost_transform()
        elif event_data['Key'] == 'T':
            if not hasattr(self.cmd, 'circuit_type'):
                return
            tipos = ["TUG (Geral)", "TUE (Específico)", "UPS (Emergência)"]
            idx = (tipos.index(self.cmd.circuit_type) + 1) % 3
            self.cmd.circuit_type = tipos[idx]
            if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
            if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
            self.refresh_ghost_transform()
        elif event_data['Key'] == 'N':
            if hasattr(self.cmd, 'cycle_level'):
                self.cmd.cycle_level()
                if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
                if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
                self.refresh_ghost_transform()
        elif event_data['Key'] == 'A':
            if hasattr(self.cmd, 'cycle_amperage'):
                self.cmd.cycle_amperage()
                if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
                if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
                self.refresh_ghost_transform()
        elif event_data['Key'] == 'M':
            if hasattr(self.cmd, 'cycle_modules'):
                self.cmd.cycle_modules()
                if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
                if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
                self.refresh_ghost_transform()
        elif event_data['Key'] == 'I':
            if hasattr(self.cmd, 'cycle_insert_mode'):
                self.cmd.cycle_insert_mode()
                if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
                self.show_placement_status()

    def get_projection_point(self, pos):
        # 1. TENTA PROJEÇÃO EM GEOMETRIA REAL (Se habilitado)
        if self.should_query_view_objects():
            try:
                pt = self.view.getPoint(int(pos[0]), int(pos[1]))
                if pt is not None:
                    return pt
            except Exception:
                pass
            
        # 2. FALLBACK PLANAR INTELIGENTE (Funciona em qualquer vista 2D/3D!)
        try:
            ray = self.view.getRay(int(pos[0]), int(pos[1]))
            if ray and len(ray) == 2:
                origin, direction = ray[0], ray[1]
                if abs(direction.z) > 1e-6:
                    t = -origin.z / direction.z
                    return origin + direction * t
                elif abs(direction.y) > 1e-6:
                    t = -origin.y / direction.y
                    return origin + direction * t
                elif abs(direction.x) > 1e-6:
                    t = -origin.x / direction.x
                    return origin + direction * t
        except Exception:
            pass

        # 3. ÚLTIMO RECURSO: Tenta obter o ponto sob o mouse diretamente da geometria real
        try:
            pt = self.view.getPoint(int(pos[0]), int(pos[1]))
            if pt is not None:
                return pt
        except Exception:
            pass

        return None

    def on_move(self, event_data):
        try:
            pos = event_data['Position']
            pixel_pos = (int(pos[0]), int(pos[1]))
            if self.last_mouse_pos == pixel_pos:
                return
            self.last_mouse_pos = pixel_pos
            self.move_counter += 1

            info = self.view.getObjectInfo(pos) if self.should_query_view_objects() else None
            point = self.get_projection_point(pos)
            self.capture_host_info(info)
            if self.move_counter % 8 == 0:
                self.clear_preselection()
                self.quiet_draft_snapper()
                self.show_placement_status()
            
            if point is not None:
                px = point.x if hasattr(point, 'x') else point[0]
                py = point.y if hasattr(point, 'y') else point[1]
                z = float(self.cmd.get_final_z()) if hasattr(self.cmd, 'get_final_z') else float(self.cmd.z_level)
                rot = float(self.cmd.rotation)
                
                # --- LÓGICA DE SNAP (Sincronizada) ---
                if info and 'Object' in info:
                    target_obj = App.ActiveDocument.getObject(info['Object'])
                    if target_obj and ("Caixa" in target_obj.Label or "JunctionBox" in target_obj.Label):
                        point = target_obj.Placement.Base
                        px = point.x if hasattr(point, 'x') else point[0]
                        py = point.y if hasattr(point, 'y') else point[1]
                        try:
                            rot = target_obj.Placement.Rotation.Angle * (180/3.14159)
                        except Exception:
                            rot = 0.0
                
                # Salva para o clique real
                self.last_snap_point = point
                self.last_snap_rot = rot
                
                if not self.ghost:
                    self.ghost = self.placement_func(point, is_ghost=True)
                    if self.ghost:
                        # Síncrono imediato para evitar corrida de cliques rápidos
                        if getattr(self.ghost, "ViewObject", None) is not None:
                            try:
                                self.ghost.ViewObject.Selectable = False
                            except Exception:
                                pass
                        # Assíncrono adicional para segurança
                        def make_ghost_non_selectable(name=self.ghost.Name):
                            try:
                                gui_obj = Gui.ActiveDocument.getObject(name)
                                if gui_obj:
                                    gui_obj.Selectable = False
                            except Exception:
                                pass
                        QtCore.QTimer.singleShot(50, make_ghost_non_selectable)
                if self.ghost:
                    self.ghost.Placement = App.Placement(App.Vector(px, py, z), App.Rotation(App.Vector(0,0,1), rot))
        except Exception as e:
            import traceback
            App.Console.PrintError(f"Erro no on_move: {str(e)}\n{traceback.format_exc()}\n")
            self.ghost = None

    def on_click_pivy(self, event_callback):
        try:
            from pivy import coin
            event = event_callback.getEvent()
            state = "DOWN" if event.getState() == coin.SoButtonEvent.DOWN else "UP"
            
            btn_val = event.getButton()
            if btn_val == coin.SoMouseButtonEvent.BUTTON1:
                button = 'BUTTON1'
            elif btn_val == coin.SoMouseButtonEvent.BUTTON2:
                button = 'BUTTON2'
            elif btn_val == coin.SoMouseButtonEvent.BUTTON3:
                button = 'BUTTON3'
            else:
                button = f"BUTTON{btn_val}"
                
            pos_val = event.getPosition()
            pos = (pos_val[0], pos_val[1])
            
            event_data = {
                'State': state,
                'Button': button,
                'Position': pos,
                'Event': event
            }
            
            handled = self.on_click(event_data)
            if handled:
                event_callback.setHandled()
        except Exception as e:
            App.Console.PrintError(f"Erro no on_click_pivy: {e}\n")

    def on_click(self, event_data):
        try:
            # Limpa qualquer tentativa de seleção antes do processamento
            Gui.Selection.clearSelection()
            
            if event_data['Button'] == 'BUTTON1':
                if event_data['State'] == 'DOWN':
                    pos = event_data['Position']
                    
                    # TRUQUE: Esconde o fantasma por um milissegundo para o clique "atravessar" ele
                    if self.ghost: self.ghost.ViewObject.Visibility = False
                    
                    # Agora pegamos o ponto real lá no fundo (parede/piso/chão)
                    fresh_point = self.get_projection_point(pos)
                    
                    # Mostra o fantasma de novo
                    if self.ghost: self.ghost.ViewObject.Visibility = True

                    if fresh_point is None and self.last_snap_point is not None:
                        fresh_point = self.last_snap_point
                    
                    if fresh_point is not None:
                        # Se estivermos em cima de uma caixa (Snap), usamos o snap. 
                        # Senão, usamos o ponto exato onde o clique "atravessou" a mira.
                        snapped = self.is_snapped(pos)
                        target_point = self.last_snap_point if snapped and self.last_snap_point is not None else fresh_point
                        self.apply_host_to_command()
                        if snapped:
                            self.cmd.rotation = self.last_snap_rot
                            if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
                        
                        existing_names = {obj.Name for obj in App.ActiveDocument.Objects}
                        self.placement_func(target_point, is_ghost=False)
                        new_objects = [obj for obj in App.ActiveDocument.Objects if obj.Name not in existing_names]
                        for new_obj in new_objects:
                            # Síncrono imediato para evitar corrida de cliques rápidos
                            if getattr(new_obj, "ViewObject", None) is not None:
                                try:
                                    new_obj.ViewObject.Selectable = False
                                except Exception:
                                    pass
                            # Assíncrono adicional para segurança
                            def make_non_selectable(name=new_obj.Name):
                                try:
                                    gui_obj = Gui.ActiveDocument.getObject(name)
                                    if gui_obj:
                                        gui_obj.Selectable = False
                                except Exception:
                                    pass
                            QtCore.QTimer.singleShot(50, make_non_selectable)

                        # Limpa qualquer seleção imediatamente e agenda uma limpeza após 150ms
                        # para garantir que o evento de clique UP do mouse seja "limpo" no FreeCAD
                        Gui.Selection.clearSelection()
                        QtCore.QTimer.singleShot(150, Gui.Selection.clearSelection)
                        
                        if not getattr(self.cmd, "continuous_insert", True):
                            self.stop()
                return True # Consome todos os eventos do BUTTON1 (DOWN e UP) para evitar popup de seleção!
        except Exception as e:
            import traceback
            App.Console.PrintError(f"Erro no on_click: {str(e)}\n{traceback.format_exc()}\n")
            try:
                from PySide2 import QtWidgets
            except ImportError:
                from PySide6 import QtWidgets
            QtWidgets.QMessageBox.critical(None, "Eletrica Error", f"Erro ao inserir componente:\n{str(e)}")

    def capture_host_info(self, info):
        self.last_host_object = ""
        self.last_host_sub = ""
        if not info:
            return
        self.last_host_object = info.get('Object', '') or ''
        self.last_host_sub = info.get('Component', '') or info.get('SubElement', '') or ''

    def apply_host_to_command(self):
        if hasattr(self.cmd, 'host_object'):
            self.cmd.host_object = self.last_host_object
        if hasattr(self.cmd, 'host_sub'):
            self.cmd.host_sub = self.last_host_sub

    def is_snapped(self, pos):
        """Verifica se o mouse ainda está sobre uma caixa de snap."""
        if not self.should_query_view_objects():
            return False
        info = self.view.getObjectInfo(pos)
        if info and 'Object' in info:
            obj = App.ActiveDocument.getObject(info['Object'])
            if obj and ("Caixa" in obj.Label or "JunctionBox" in obj.Label):
                return True
        return False

    def stop(self):
        self.set_action_checked(False)
        self.restore_preselection()
        self.clear_preselection()
        
        # Remove o filtro de cliques Qt
        if hasattr(self, "gl_widget") and self.gl_widget and hasattr(self, "qt_filter") and self.qt_filter:
            try:
                self.gl_widget.removeEventFilter(self.qt_filter)
            except Exception:
                pass
            self.gl_widget = None
            self.qt_filter = None
        
        # Restaura o estado de seleção original dos objetos com atraso de 250ms para garantir que o clique do mouse (DOWN e UP) termine antes
        saved_selectable_copy = dict(getattr(self, "saved_selectable", {}))
        self.saved_selectable = {}
        
        def delayed_restore():
            doc = App.ActiveDocument
            if doc:
                for name, selectable in saved_selectable_copy.items():
                    obj = doc.getObject(name)
                    if obj and getattr(obj, "ViewObject", None) is not None:
                        try:
                            obj.ViewObject.Selectable = selectable
                        except Exception:
                            pass
                # Garante que novos objetos inseridos fiquem selecionáveis
                for obj in doc.Objects:
                    if obj.Name not in saved_selectable_copy and getattr(obj, "ViewObject", None) is not None:
                        try:
                            obj.ViewObject.Selectable = True
                        except Exception:
                            pass
            try:
                Gui.Selection.clearSelection()
            except Exception:
                pass
                
        QtCore.QTimer.singleShot(250, delayed_restore)

        try:
            Gui.Selection.clearSelection()
        except Exception:
            pass
        try:
            Gui.Selection.removeSelectionGate()
        except Exception:
            pass
        if self.callback:
            try:
                from pivy import coin
                self.view.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.callback)
            except Exception:
                pass
        if self.kb_callback: self.view.removeEventCallback("SoKeyboardEvent", self.kb_callback)
        if self.move_callback: self.view.removeEventCallback("SoLocation2Event", self.move_callback)
        if self.ghost:
            try:
                App.ActiveDocument.removeObject(self.ghost.Name)
            except Exception:
                pass
            self.ghost = None
        QtGui.QApplication.restoreOverrideCursor()
        Gui.Control.closeDialog()
        
        if BIMPlacementEngine.active_engine == self:
            BIMPlacementEngine.active_engine = None
        self.clear_checkable_actions()

        if App.ActiveDocument:
            App.ActiveDocument.recompute()

    def toggle_panel(self):
        try:
            if Gui.Control.activeDialog() is not None:
                Gui.Control.closeDialog()
                App.Console.PrintLog("Painel de Controle Elétrico ocultado. Pressione 'P' ou 'TAB' para exibir.\n")
            else:
                Gui.Control.showDialog(self.panel)
                if hasattr(self.panel, 'sync_ui'):
                    self.panel.sync_ui()
                App.Console.PrintLog("Painel de Controle Elétrico exibido. Pressione 'P' ou 'TAB' para ocultar.\n")
        except Exception as e:
            print(f"Erro ao alternar painel: {e}")
