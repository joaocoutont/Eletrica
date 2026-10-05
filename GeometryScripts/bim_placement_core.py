import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui, QtCore
import Part
import math


def _format_dist_fc(dist_mm):
    """
    Formata uma distância (em mm) respeitando o esquema de unidades
    configurado no FreeCAD (mm, cm, m, polegadas, pés, etc.).
    Usa App.Units.Quantity para seguir a preferência do projeto.
    Fallback manual caso a API não esteja disponível.
    """
    try:
        q = App.Units.Quantity(dist_mm, App.Units.Length)
        return q.UserString          # ex.: "45,00 mm" / "4,50 cm" / "1,50 m"
    except Exception:
        pass
    # Fallback
    if dist_mm >= 1000:
        return f"{dist_mm/1000:.2f} m"
    elif dist_mm >= 10:
        return f"{dist_mm/10:.1f} cm"
    return f"{dist_mm:.0f} mm"


# Desenha linhas tracejadas e texto de distância diretamente no scenegraph 3D
# ─────────────────────────────────────────────────────────────────────────────
class Coin3DOverlay:
    """
    Overlay leve no scenegraph Coin3D para guias visuais de inserção.
    Todas as operações são no-op seguras após remove() ser chamado.
    """

    COLOR_DIR_LINE  = (0.0, 0.9, 1.0)   # ciano  — linha de direção (Shift)
    COLOR_REF_LINE  = (0.8, 0.0, 0.8)   # roxo   — linha de referência (R)
    COLOR_WALL_LINE = (0.0, 0.9, 0.2)   # verde  — linha de parede (W)

    def __init__(self, view):
        self.view         = view
        self._valid       = False   # torna-se True após _setup bem-sucedido
        self._root        = None
        self._dir_coords  = None
        self._ref_coords  = None
        self._wall_coords = None
        self._text_trans  = None
        self._text_node   = None
        self._text_material = None
        self._setup()

    def _setup(self):
        try:
            from pivy import coin
            sg = self.view.getSceneGraph()
            self._root = coin.SoSeparator()

            # ── Linha de direção (ciano tracejada) ──
            dir_sep = coin.SoSeparator()
            dm = coin.SoMaterial()
            dm.diffuseColor.setValue(self.COLOR_DIR_LINE)
            ds = coin.SoDrawStyle()
            ds.lineWidth.setValue(2.5)
            ds.linePattern.setValue(0xF0F0)
            self._dir_coords = coin.SoCoordinate3()
            self._dir_coords.point.setValues(0, 2, [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)])
            dls = coin.SoLineSet()
            dls.numVertices.setValues(0, 1, [2])
            for n in (dm, ds, self._dir_coords, dls):
                dir_sep.addChild(n)
            self._root.addChild(dir_sep)

            # ── Linha de referência (roxa tracejada) ──
            ref_sep = coin.SoSeparator()
            rm = coin.SoMaterial()
            rm.diffuseColor.setValue(self.COLOR_REF_LINE)
            rs = coin.SoDrawStyle()
            rs.lineWidth.setValue(2.5)
            rs.linePattern.setValue(0xAAAA)
            self._ref_coords = coin.SoCoordinate3()
            self._ref_coords.point.setValues(0, 2, [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)])
            rls = coin.SoLineSet()
            rls.numVertices.setValues(0, 1, [2])
            for n in (rm, rs, self._ref_coords, rls):
                ref_sep.addChild(n)
            self._root.addChild(ref_sep)

            # ── Linha de parede (verde tracejada) ──
            wall_sep = coin.SoSeparator()
            wm = coin.SoMaterial()
            wm.diffuseColor.setValue(self.COLOR_WALL_LINE)
            ws = coin.SoDrawStyle()
            ws.lineWidth.setValue(2.5)
            ws.linePattern.setValue(0xFF00)
            self._wall_coords = coin.SoCoordinate3()
            self._wall_coords.point.setValues(0, 2, [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)])
            wls = coin.SoLineSet()
            wls.numVertices.setValues(0, 1, [2])
            for n in (wm, ws, self._wall_coords, wls):
                wall_sep.addChild(n)
            self._root.addChild(wall_sep)

            # ── Rótulo de texto (distância) ──
            text_sep = coin.SoSeparator()
            self._text_trans = coin.SoTransform()
            self._text_trans.translation.setValue([0.0, 0.0, 0.0])
            self._text_material = coin.SoMaterial()
            self._text_material.diffuseColor.setValue([1.0, 1.0, 1.0])
            tf = coin.SoFont()
            tf.size = 28.0 # Texto maior para melhor visibilidade (era 16.0)
            self._text_node = coin.SoText2()
            try:
                self._text_node.justification = coin.SoText2.CENTER
            except Exception:
                try:
                    self._text_node.justification = coin.SoAsciiText.CENTER
                except Exception:
                    pass
            try:
                self._text_node.string.setValue("")
            except Exception:
                try:
                    self._text_node.string.setValues(0, 1, [""])
                except Exception:
                    pass
                
            for n in (self._text_trans, self._text_material, tf, self._text_node):
                text_sep.addChild(n)
            self._root.addChild(text_sep)

            sg.addChild(self._root)
            self._valid = True

        except Exception as e:
            App.Console.PrintWarning(
                f"[Eletrica] Overlay Coin3D não disponível: {e}\n")
            self._valid = False

    # ------------------------------------------------------------------
    def _set_line(self, coords, pt_a, pt_b):
        if not self._valid or coords is None:
            return
        try:
            if pt_a is not None and pt_b is not None:
                coords.point.setValues(
                    0, 2, [(pt_a.x, pt_a.y, pt_a.z),
                           (pt_b.x, pt_b.y, pt_b.z)])
            else:
                coords.point.setValues(0, 2, [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)])
        except Exception as e:
            App.Console.PrintWarning(f"[Eletrica] Erro ao desenhar linha do overlay: {e}\n")

    def _set_text(self, pt_mid, dist_mm, color=None):
        return

    def set_dir_line(self, pt_a, pt_b):
        """Linha ciano: ponto de origem de direção → cursor."""
        self._set_line(self._dir_coords, pt_a, pt_b)
        if pt_a is not None and pt_b is not None:
            dist = (pt_b - pt_a).Length
            mid  = App.Vector(
                (pt_a.x + pt_b.x) / 2.0,
                (pt_a.y + pt_b.y) / 2.0,
                max(pt_a.z, pt_b.z))
            self._set_text(mid, dist, self.COLOR_DIR_LINE)
        else:
            self._set_text(None, 0)

    def set_ref_line(self, pt_a, pt_b):
        """Linha roxa: ponto de referência → cursor (modo R)."""
        self._set_line(self._ref_coords, pt_a, pt_b)
        if pt_a is not None and pt_b is not None:
            dist = (pt_b - pt_a).Length
            mid  = App.Vector(
                (pt_a.x + pt_b.x) / 2.0,
                (pt_a.y + pt_b.y) / 2.0,
                max(pt_a.z, pt_b.z))
            self._set_text(mid, dist, self.COLOR_REF_LINE)
        else:
            self._set_text(None, 0)

    def set_wall_line(self, pt_a, pt_b):
        """Linha verde: 1º ponto da parede → cursor (modo W)."""
        self._set_line(self._wall_coords, pt_a, pt_b)

    def clear_all(self):
        if not self._valid:
            return
        zero = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)]
        try:
            if self._dir_coords:  self._dir_coords.point.setValues(0, 2, zero)
            if self._ref_coords:  self._ref_coords.point.setValues(0, 2, zero)
            if self._wall_coords: self._wall_coords.point.setValues(0, 2, zero)
            if self._text_node:
                try:
                    self._text_node.string.setValue("")
                except Exception:
                    try:
                        self._text_node.string.setValues(0, 1, [""])
                    except Exception:
                        pass
        except Exception:
            pass

    def remove(self):
        """Remove o overlay do scenegraph com segurança total."""
        self._valid = False
        try:
            if self._root is not None:
                sg = self.view.getSceneGraph()
                sg.removeChild(self._root)
        except Exception:
            pass
        self._root        = None
        self._dir_coords  = None
        self._ref_coords  = None
        self._wall_coords = None
        self._text_trans  = None
        self._text_node   = None
        self._text_material = None


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUEADOR DE SELEÇÃO
# ─────────────────────────────────────────────────────────────────────────────
class SelectionBlocker:
    """Bloqueia qualquer seleção no FreeCAD para impedir menus de contexto."""
    def __init__(self): self.notAllowedReason = ""
    def allow(self, doc, obj, sub): return False


# ─────────────────────────────────────────────────────────────────────────────
# FILTRO Qt DE TECLADO (GLOBAL)
# ─────────────────────────────────────────────────────────────────────────────
class QtKeyFilter(QtCore.QObject):
    """Filtro de teclado global instalado na MainWindow do FreeCAD."""
    def __init__(self, engine):
        super(QtKeyFilter, self).__init__()
        self.engine = engine

    # Mapa de teclas Qt → nome esperado pelo on_key (mesmo formato do SoKeyboardEvent)
    # NOTA: P foi removido — conflita com Sketcher_ConstrainParallel.
    #       Use Tab para alternar o painel.
    _KEY_MAP = {
        QtCore.Qt.Key_Escape:        'ESCAPE',
        QtCore.Qt.Key_R:             'R',
        QtCore.Qt.Key_G:             'G',
        QtCore.Qt.Key_F:             'F',
        QtCore.Qt.Key_W:             'W',
        QtCore.Qt.Key_H:             'H',
        QtCore.Qt.Key_T:             'T',
        QtCore.Qt.Key_N:             'N',
        QtCore.Qt.Key_A:             'A',
        QtCore.Qt.Key_M:             'M',
        QtCore.Qt.Key_I:             'I',
        QtCore.Qt.Key_Tab:           'TAB',
        QtCore.Qt.Key_BracketLeft:   'BRACKETLEFT',
        QtCore.Qt.Key_BracketRight:  'BRACKETRIGHT',
    }

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key_name = self._KEY_MAP.get(event.key())
            if key_name:
                App.Console.PrintMessage(f"[DEBUG] QtKeyFilter: key_name={key_name}\n")
                if key_name != 'ESCAPE':
                    # Nao intercepta se o foco estiver em um campo de entrada de texto real
                    try:
                        app = QtGui.QApplication.instance()
                        focus_widget = app.focusWidget() if app else None
                        if focus_widget:
                            cls_name = type(focus_widget).__name__
                            if any(k in cls_name for k in ("LineEdit", "TextEdit", "Console", "Python", "Terminal")):
                                return False
                    except Exception:
                        pass

                if key_name == 'ESCAPE':
                    self.engine.stop()
                else:
                    self.engine.on_key({'Key': key_name})
                event.accept()
                return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
# FILTRO Qt DE CLIQUE
# Intercepta MouseButtonPress antes do C++ do FreeCAD e repassa para a engine.
# ─────────────────────────────────────────────────────────────────────────────
class QtClickFilter(QtCore.QObject):
    """Filtro de eventos Qt — intercepta cliques na viewport 3D."""
    def __init__(self, engine):
        super(QtClickFilter, self).__init__()
        self.engine = engine

    def eventFilter(self, watched, event):
        if event.type() in (QtCore.QEvent.MouseButtonPress,
                             QtCore.QEvent.MouseButtonRelease,
                             QtCore.QEvent.MouseButtonDblClick):
            if event.button() == QtCore.Qt.LeftButton:
                state = "DOWN" if event.type() == QtCore.QEvent.MouseButtonPress else "UP"
                h = watched.height()
                pos = (event.x(), h - event.y())
                shift = bool(event.modifiers() & QtCore.Qt.ShiftModifier)

                event_data = {
                    'State':    state,
                    'Button':   'BUTTON1',
                    'Position': pos,
                    'Shift':    shift,
                    'Event':    event
                }
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    self.engine.on_click(event_data)

                event.accept()
                return True
        return False



# ─────────────────────────────────────────────────────────────────────────────
# MOTOR DE INSERÇÃO BIM
# ─────────────────────────────────────────────────────────────────────────────
class BIMPlacementEngine:
    """
    Motor v3.0 — Inserção com Modo de Direção por Ctrl+Clique.

    Atalhos:
      Clique simples        → insere na posição atual com rotação atual
      Ctrl + Clique         → define o ponto de origem da direção (sem inserir)
                              após o 1º Ctrl+Clique, o fantasma gira seguindo
                              a direção do cursor; clique simples insere.
      G                     → rotação manual +90°
      R                     → modo de referência (distância exata)
      H                     → cicla altura padrão
      P / TAB               → mostra/oculta painel
      ESC                   → cancela inserção
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

        self.callback      = None
        self.kb_callback   = None
        self.move_callback = None
        self.gate          = SelectionBlocker()
        self.view          = None
        self.panel         = None
        self.ghost         = None
        self.view_params   = App.ParamGet("User parameter:BaseApp/Preferences/Selection")
        self.previous_preselection = None

        # Estado de sincronização
        self.last_snap_point  = None
        self.last_snap_rot    = 0
        self.last_host_object = ""
        self.last_host_sub    = ""
        self.last_mouse_pos   = None
        self.move_counter     = 0
        self.saved_selectable = {}

        # Modo de referência (tecla R)
        self.ref_mode_active = False
        self.ref_point       = None
        self.temp_dim        = None

        # Modo de direção (Shift+Clique)
        self.dir_origin      = None   # ponto de origem da direção
        self.dir_locked      = False  # True após o 1º Shift+Clique

        # Modo de parede (tecla W) — alinha perpendicular à reta da parede
        self.wall_p1         = None   # 1° ponto da reta de parede
        self.wall_active     = False  # True enquanto aguarda os 2 cliques

        # Rotação manual
        self.manual_rot_offset = 0

        # Modo de rotação ativo
        # 1=Normal, 2=Rot90°, 3=Rot15° (fine), 4=Direção, 5=Parede, 6=Ref
        self.rot_mode = 1

        # Overlay Coin3D (criado em start())
        self.overlay = None

    # ------------------------------------------------------------------
    def is_quiet_mode(self):
        return bool(getattr(self.cmd, "quiet_placement", True))

    def should_query_view_objects(self):
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
            return "Eletrica_InsertSocket"
        elif cls_name == "JunctionBoxCommand":
            return "Eletrica_JunctionBox"
        return None

    @staticmethod
    def set_command_action_checked(cmd_name, checked):
        if not cmd_name: return
        try:
            mw = Gui.getMainWindow()
            if not mw: return
            actions = []
            found = mw.findChild(QtGui.QAction, cmd_name)
            if found: actions.append(found)
            for action in mw.findChildren(QtGui.QAction):
                try:
                    if action.objectName() == cmd_name or action.data() == cmd_name:
                        if action not in actions: actions.append(action)
                except Exception: pass
            for action in actions:
                action.blockSignals(True)
                if not action.isCheckable(): action.setCheckable(True)
                action.setChecked(checked)
                action.blockSignals(False)
        except Exception as e:
            print(f"Erro ao atualizar estado do botão {cmd_name}: {e}")

    @classmethod
    def clear_checkable_actions(cls, except_name=None):
        for name in cls.CHECKABLE_PLACEMENT_COMMANDS:
            if name != except_name:
                cls.set_command_action_checked(name, False)

    def set_action_checked(self, checked):
        cmd_name = self.get_command_name()
        if checked: self.clear_checkable_actions(except_name=cmd_name)
        self.set_command_action_checked(cmd_name, checked)

    # ------------------------------------------------------------------
    def start(self):
        if BIMPlacementEngine.active_engine is not None:
            try: BIMPlacementEngine.active_engine.stop()
            except Exception: pass

        try:
            self.view  = Gui.ActiveDocument.ActiveView
            self.panel = self.task_panel_class(self.cmd)
            Gui.Control.showDialog(self.panel)

            # Torna todos os objetos não selecionáveis durante a inserção
            self.saved_selectable = {}
            doc = App.ActiveDocument
            if doc:
                for obj in doc.Objects:
                    if getattr(obj, "ViewObject", None) is not None:
                        try:
                            self.saved_selectable[obj.Name] = obj.ViewObject.Selectable
                            obj.ViewObject.Selectable = False
                        except Exception: pass

            try:
                Gui.Selection.addSelectionGate("SELECT None")
            except Exception:
                Gui.Selection.addSelectionGate(self.gate)
            self.clear_preselection()
            self.show_placement_status()

            # Instala filtro Qt de cliques na viewport 3D e teclado globalmente
            self.gl_widget  = None
            self.qt_filter  = None   # filtro de cliques (gl_widget)
            self.key_filter = None   # filtro de teclas (global)
            try:
                # ── Filtro de TECLADO Global (QApplication) ──────────────
                app = QtGui.QApplication.instance()
                if app:
                    self.key_filter = QtKeyFilter(self)
                    app.installEventFilter(self.key_filter)
                    App.Console.PrintLog("[Eletrica] Filtro de teclado global instalado em QApplication\n")

                mw = Gui.getMainWindow()
                if mw:
                    # ── Filtro de CLIQUES no gl_widget ────────────────────────
                    mdi_area = None; widget_class = None
                    try:
                        from PySide2 import QtWidgets as W
                        mdi_area = mw.findChild(W.QMdiArea); widget_class = W.QWidget
                    except ImportError:
                        try:
                            from PySide6 import QtWidgets as W
                            mdi_area = mw.findChild(W.QMdiArea); widget_class = W.QWidget
                        except ImportError:
                            import PySide.QtGui as W
                            mdi_area = mw.findChild(W.QMdiArea); widget_class = W.QWidget
                    if mdi_area and mdi_area.activeSubWindow():
                        sub_win = mdi_area.activeSubWindow().widget()
                        if sub_win and widget_class:
                            candidates = [c for c in sub_win.findChildren(widget_class)
                                          if any(k in c.metaObject().className()
                                                 for k in ("GL","Quarter","OpenGL"))]
                            self.gl_widget = candidates[0] if candidates else sub_win
                            if self.gl_widget:
                                self.qt_filter = QtClickFilter(self)
                                self.gl_widget.installEventFilter(self.qt_filter)
                                App.Console.PrintLog(
                                    f"[Eletrica] Filtro de cliques Qt instalado em: "
                                    f"{self.gl_widget.metaObject().className()}\n")
            except Exception as e:
                App.Console.PrintError(f"[Eletrica] Erro ao instalar filtro Qt: {e}\n")
                self.gl_widget = None; self.qt_filter = None

            # Fallback Pivy se o filtro Qt falhar
            self.callback = None
            if not self.qt_filter:
                try:
                    from pivy import coin
                    self.callback = self.view.addEventCallbackPivy(
                        coin.SoMouseButtonEvent.getClassTypeId(), self.on_click_pivy)
                except Exception: pass

            # Fallback de teclado Pivy apenas se o filtro Qt de teclado falhar
            self.kb_callback = None
            if not self.key_filter:
                try:
                    self.kb_callback = self.view.addEventCallback("SoKeyboardEvent", self.on_key)
                except Exception: pass
            self.move_callback = self.view.addEventCallback("SoLocation2Event", self.on_move)

            self.ghost = None
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
            BIMPlacementEngine.active_engine = self
            self.set_action_checked(True)

            # Cria o overlay visual do Coin3D (desenhando apenas as linhas, sem o texto)
            try:
                self.overlay = Coin3DOverlay(self.view)
            except Exception as e:
                App.Console.PrintWarning(f"[Eletrica] Falha ao criar Coin3DOverlay: {e}\n")
                self.overlay = None

        except Exception:
            BIMPlacementEngine.active_engine = None
            self.clear_checkable_actions()
            try:
                self.restore_preselection(); self.clear_preselection()
                Gui.Selection.removeSelectionGate()
            except Exception: pass
            if getattr(self, "key_filter", None):
                try:
                    app = QtGui.QApplication.instance()
                    if app: app.removeEventFilter(self.key_filter)
                except Exception: pass
                self.key_filter = None
            if getattr(self, "gl_widget", None) and getattr(self, "qt_filter", None):
                try: self.gl_widget.removeEventFilter(self.qt_filter)
                except Exception: pass
                self.gl_widget = None; self.qt_filter = None
            if self.callback and self.view:
                try:
                    from pivy import coin
                    self.view.removeEventCallbackPivy(
                        coin.SoMouseButtonEvent.getClassTypeId(), self.callback)
                except Exception: pass
            for ev, cb in [("SoKeyboardEvent", self.kb_callback),
                           ("SoLocation2Event", self.move_callback)]:
                if cb and self.view:
                    try: self.view.removeEventCallback(ev, cb)
                    except Exception: pass
            try: Gui.Control.closeDialog()
            except Exception: pass
            try: QtGui.QApplication.restoreOverrideCursor()
            except Exception: pass
            raise

    # ------------------------------------------------------------------
    def disable_preselection(self):
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
        except Exception: pass

    def clear_preselection(self):
        for method_name in ("clearPreselection", "rmvPreselect", "removePreselection"):
            method = getattr(Gui.Selection, method_name, None)
            if method:
                try: method(); return
                except Exception: pass

    def show_placement_status(self):
        try:
            mw = Gui.getMainWindow()
            if not mw: return
            mode  = "contínuo" if getattr(self.cmd, "continuous_insert", True) else "uma vez"
            label = getattr(self.cmd, "tool_label", "tomada")
            rot   = getattr(self.cmd, 'rotation', 0)

            if self.wall_active:
                if self.wall_p1 is None:
                    extra = " | PAREDE: clique no 1° ponto da parede"
                else:
                    extra = " | PAREDE: clique no 2° ponto para definir ângulo | ESC cancela parede"
            elif self.dir_locked and self.dir_origin is not None:
                dist = 0.0
                if self.last_snap_point and self.dir_origin:
                    dist = (self.last_snap_point - self.dir_origin).Length
                extra = f" | DIREÇÃO | {_format_dist_fc(dist)} | Clique insere | Shift cancela"
            elif self.ref_mode_active:
                if self.ref_point is not None:
                    dist = 0.0
                    if self.last_snap_point and self.ref_point:
                        dist = (self.last_snap_point - self.ref_point).Length
                    extra = f" | REFERÊNCIA | {_format_dist_fc(dist)} | Enter ou clique"
                else:
                    extra = " | REFERÊNCIA: clique no 1° ponto"
            elif self.rot_mode == 3:
                extra = f" | FINO 15° | Rot={rot}° | [ -15°  ] +15° | F volta 90°"
            else:
                extra = f" | Rot={rot}° | G +90° | F fino | W parede | Shift dir. | R ref"
            mw.statusBar().showMessage(
                f"Inserindo {label} ({mode}): clique posiciona | ESC sai{extra}", 1200)
        except Exception: pass

    def refresh_ghost_transform(self):
        if not self.ghost or self.last_snap_point is None: return
        try:
            z   = float(self.cmd.get_final_z()) if hasattr(self.cmd, 'get_final_z') else float(self.cmd.z_level)
            rot = float(self.cmd.rotation)
            pt  = self.last_snap_point
            self.ghost.Placement = App.Placement(
                App.Vector(pt.x, pt.y, z), App.Rotation(App.Vector(0,0,1), rot))
            Gui.updateGui()
        except Exception: pass

    # ------------------------------------------------------------------
    def _apply_rotation(self, delta):
        """Aplica incremento de rotação, reseta modo direção e atualiza UI."""
        self.dir_origin = None; self.dir_locked = False
        self.wall_p1    = None
        if self.overlay: self.overlay.clear_all()
        self.cmd.rotation = (self.cmd.rotation + delta) % 360
        self.manual_rot_offset = self.cmd.rotation
        if hasattr(self.panel, 'sync_ui'):
            self.panel.sync_ui()
        else:
            try:
                if hasattr(self.panel, 'rot_in'):
                    self.panel.rot_in.blockSignals(True)
                    self.panel.rot_in.setValue(self.cmd.rotation)
                    self.panel.rot_in.blockSignals(False)
            except Exception:
                pass
        self.refresh_ghost_transform()
        self.show_placement_status()

    def set_rot_mode(self, mode):
        """Muda o modo de rotação ativo (1-6) e atualiza o painel."""
        self.rot_mode = mode
        # Cancela estados de modos anteriores se trocou
        if mode != 4:
            self.dir_origin = None; self.dir_locked = False
        if mode != 5:
            self.wall_p1 = None; self.wall_active = False
        if mode != 6:
            self.ref_mode_active = False
            if hasattr(self.panel, 'ref_btn'):
                self.panel.ref_btn.blockSignals(True)
                self.panel.ref_btn.setChecked(False)
                self.panel.ref_btn.blockSignals(False)
        if self.overlay:
            self.overlay.clear_all()
        # Ativa o modo parede
        if mode == 5:
            self.wall_active = True
        # Ativa o modo referência
        if mode == 6:
            self.ref_mode_active = True
            self.ref_point = None
            if hasattr(self.panel, 'ref_btn'):
                self.panel.ref_btn.blockSignals(True)
                self.panel.ref_btn.setChecked(True)
                self.panel.ref_btn.blockSignals(False)
        # Sincroniza botões do painel
        if hasattr(self.panel, 'sync_rot_mode_buttons'):
            self.panel.sync_rot_mode_buttons(self.rot_mode)
        self.show_placement_status()

    # ------------------------------------------------------------------
    def on_key(self, event_data):
        key = str(event_data['Key']).upper()
        App.Console.PrintMessage(f"[DEBUG] on_key: key={key}\n")
        if key == 'ESCAPE':
            # ESC cancela modo parede/direção antes de sair totalmente
            if self.wall_active:
                self.wall_p1 = None; self.wall_active = False
                self.rot_mode = 1
                if self.overlay: self.overlay.clear_all()
                if hasattr(self.panel, 'sync_rot_mode_buttons'):
                    self.panel.sync_rot_mode_buttons(1)
                self.show_placement_status()
            elif self.dir_locked:
                self.dir_origin = None; self.dir_locked = False
                if self.overlay: self.overlay.clear_all()
                self.show_placement_status()
            elif self.ref_mode_active:
                self.clear_reference_mode()
                self.rot_mode = 1
                if hasattr(self.panel, 'sync_rot_mode_buttons'):
                    self.panel.sync_rot_mode_buttons(1)
            else:
                self.stop()
        elif key == 'TAB':
            self.toggle_panel()
        elif key == 'G':
            # G sempre aplica +90° independente do modo fino
            self._apply_rotation(90)
        elif key == 'BRACKETLEFT':  # tecla [
            # Rotação fina -15°
            self._apply_rotation(-15)
        elif key == 'BRACKETRIGHT':  # tecla ]
            # Rotação fina +15°
            self._apply_rotation(15)
        elif key == 'F':
            # Toggle entre modo fino (3) e modo normal (1)
            if self.rot_mode == 3:
                self.set_rot_mode(1)
            else:
                self.set_rot_mode(3)
        elif key == 'W':
            # Ativa/desativa modo alinhamento de parede
            if self.wall_active:
                # Cancela modo parede
                self.wall_p1 = None; self.wall_active = False
                self.rot_mode = 1
                if self.overlay: self.overlay.clear_all()
                if hasattr(self.panel, 'sync_rot_mode_buttons'):
                    self.panel.sync_rot_mode_buttons(1)
                self.show_placement_status()
            else:
                self.set_rot_mode(5)
        elif key == 'R':
            # Toggle direto do modo referência
            if self.ref_mode_active:
                self.clear_reference_mode()
                self.rot_mode = 1
                if hasattr(self.panel, 'sync_rot_mode_buttons'):
                    self.panel.sync_rot_mode_buttons(1)
            else:
                self.set_rot_mode(6)
        elif key == 'H':
            if hasattr(self.cmd, 'cycle_height'):
                self.cmd.cycle_height()
            else:
                alturas = [300, 1100, 2200]
                cur = self.cmd.z_level
                idx = 0
                if cur < 1100: idx = 1
                elif cur < 2200: idx = 2
                self.cmd.z_level = alturas[idx]
            if hasattr(self.panel, 'sync_ui'):
                self.panel.sync_ui()
            else:
                try:
                    if hasattr(self.panel, 'z_in'):
                        self.panel.z_in.blockSignals(True)
                        self.panel.z_in.setValue(self.cmd.z_level)
                        self.panel.z_in.blockSignals(False)
                except Exception:
                    pass
            if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
            self.refresh_ghost_transform()
        elif key == 'T':
            if not hasattr(self.cmd, 'circuit_type'): return
            tipos = ["TUG (Geral)", "TUE (Específico)", "UPS (Emergência)"]
            idx = (tipos.index(self.cmd.circuit_type) + 1) % 3
            self.cmd.circuit_type = tipos[idx]
            if hasattr(self.panel, 'sync_ui'):   self.panel.sync_ui()
            if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
            self.refresh_ghost_transform()
        elif key == 'N':
            if hasattr(self.cmd, 'cycle_level'):
                self.cmd.cycle_level()
                if hasattr(self.panel, 'sync_ui'):   self.panel.sync_ui()
                if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
                self.refresh_ghost_transform()
        elif key == 'A':
            if hasattr(self.cmd, 'cycle_amperage'):
                self.cmd.cycle_amperage()
                if hasattr(self.panel, 'sync_ui'):   self.panel.sync_ui()
                if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
                self.refresh_ghost_transform()
        elif key == 'M':
            if hasattr(self.cmd, 'cycle_modules'):
                self.cmd.cycle_modules()
                if hasattr(self.panel, 'sync_ui'):   self.panel.sync_ui()
                if hasattr(self.panel, 'refresh_ghost'): self.panel.refresh_ghost()
                self.refresh_ghost_transform()
        elif key == 'I':
            if hasattr(self.cmd, 'cycle_insert_mode'):
                self.cmd.cycle_insert_mode()
                if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
                self.show_placement_status()

    # ------------------------------------------------------------------
    def get_projection_point(self, pos):
        """Projeta a posição do mouse em coordenadas 3D do mundo."""
        # 1. Draft Snapper nativo
        try:
            snapper = getattr(Gui, "Snapper", None)
            if snapper:
                pt = snapper.snap(pos, active=True)
                if pt is not None: return pt
        except Exception: pass

        # 2. getPoint se detecção de superfície habilitada
        if self.should_query_view_objects():
            try:
                pt = self.view.getPoint(int(pos[0]), int(pos[1]))
                if pt is not None: return pt
            except Exception: pass

        # 3. Raio projetado no plano Z=0 (funciona em qualquer vista 2D/3D)
        try:
            ray = self.view.getRay(int(pos[0]), int(pos[1]))
            if ray and len(ray) == 2:
                origin, direction = ray[0], ray[1]
                if abs(direction.z) > 1e-6:
                    t = -origin.z / direction.z; return origin + direction * t
                elif abs(direction.y) > 1e-6:
                    t = -origin.y / direction.y; return origin + direction * t
                elif abs(direction.x) > 1e-6:
                    t = -origin.x / direction.x; return origin + direction * t
        except Exception: pass

        # 4. Último recurso
        try:
            pt = self.view.getPoint(int(pos[0]), int(pos[1]))
            if pt is not None: return pt
        except Exception: pass

        return None

    # ------------------------------------------------------------------
    def on_move(self, event_data):
        try:
            pos = event_data['Position']
            pixel_pos = (int(pos[0]), int(pos[1]))
            if self.last_mouse_pos == pixel_pos: return
            self.last_mouse_pos = pixel_pos
            self.move_counter += 1

            info  = self.view.getObjectInfo(pos) if self.should_query_view_objects() else None
            point = self.get_projection_point(pos)
            self.capture_host_info(info)
            if self.move_counter % 10 == 0:
                self.clear_preselection()
                self.show_placement_status()

            if point is None: return

            px = point.x if hasattr(point, 'x') else point[0]
            py = point.y if hasattr(point, 'y') else point[1]
            z  = float(self.cmd.get_final_z()) if hasattr(self.cmd, 'get_final_z') else float(self.cmd.z_level)
            cursor_pt = App.Vector(px, py, z)

            # ── 1. SNAP EM CAIXA DE JUNÇÃO ──────────────────────────────────
            if info and 'Object' in info:
                target_obj = App.ActiveDocument.getObject(info['Object'])
                if target_obj and ("Caixa" in target_obj.Label or "JunctionBox" in target_obj.Label):
                    bp = target_obj.Placement.Base
                    px, py = bp.x, bp.y
                    cursor_pt = App.Vector(px, py, z)
                    try:
                        self.cmd.rotation = int(
                            target_obj.Placement.Rotation.Angle * (180/math.pi)) % 360
                    except Exception: pass

            # ── 2. CÁLCULO DA ROTAÇÃO POR DIREÇÃO ──────────────────────────
            rot = float(self.cmd.rotation)
            if self.dir_locked and self.dir_origin is not None:
                # Calcula ângulo da frente: do ponto fixo (dir_origin) até o cursor
                dx = cursor_pt.x - self.dir_origin.x
                dy = cursor_pt.y - self.dir_origin.y
                dist2d = math.sqrt(dx*dx + dy*dy)
                if dist2d > 5.0:
                    rot = math.degrees(math.atan2(dy, dx)) % 360
                    if self.cmd.rotation != int(rot):
                        self.cmd.rotation = int(rot)
                        if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
                # O fantasma fica FIXO em dir_origin — só a frente gira
                px, py = self.dir_origin.x, self.dir_origin.y

            # ── 3. OVERLAY VISUAL E MEDIÇÃO ──────────────────────────────────
            if self.dir_locked and self.dir_origin is not None:
                # Linha ciano: modo direção
                if self.overlay:
                    self.overlay.set_dir_line(self.dir_origin, cursor_pt)
                    self.overlay.set_ref_line(None, None)
                    self.overlay.set_wall_line(None, None)
                dist = (cursor_pt - self.dir_origin).Length
                mw = Gui.getMainWindow()
                if mw:
                    mw.statusBar().showMessage(
                        f"DIREÇÃO | {_format_dist_fc(dist)} | Clique insere | Shift cancela", 1200)
            elif self.wall_active and self.wall_p1 is not None:
                # Linha verde: modo parede, aguardando 2° ponto
                if self.overlay:
                    self.overlay.set_wall_line(self.wall_p1, cursor_pt)
                    self.overlay.set_dir_line(None, None)
                    self.overlay.set_ref_line(None, None)
                dist = (cursor_pt - self.wall_p1).Length
                # Calcula ângulo perpendicular para mostrar preview de rotação
                dx = cursor_pt.x - self.wall_p1.x
                dy = cursor_pt.y - self.wall_p1.y
                if math.sqrt(dx*dx + dy*dy) > 5.0:
                    wall_angle = math.degrees(math.atan2(dy, dx))
                    perp_angle = (wall_angle + 90.0) % 360
                    # Atualiza fantasma com rotação perpendicular em tempo real
                    if self.ghost:
                        self.ghost.Placement = App.Placement(
                            App.Vector(self.wall_p1.x, self.wall_p1.y, z),
                            App.Rotation(App.Vector(0,0,1), perp_angle))
                        Gui.updateGui()
                mw = Gui.getMainWindow()
                if mw:
                    mw.statusBar().showMessage(
                        f"PAREDE | {_format_dist_fc(dist)} | Clique define ângulo e insere", 1200)
            elif self.ref_point is not None:
                # Linha roxa: modo referência
                dist = (cursor_pt - self.ref_point).Length
                if self.overlay:
                    self.overlay.set_ref_line(self.ref_point, cursor_pt)
                    self.overlay.set_dir_line(None, None)
                    self.overlay.set_wall_line(None, None)
                # Atualiza spinbox no painel sem disparar signals
                if hasattr(self.panel, 'ref_dist_in') and not self.panel.ref_dist_in.hasFocus():
                    self.panel.ref_dist_in.blockSignals(True)
                    self.panel.ref_dist_in.setValue(dist)
                    self.panel.ref_dist_in.blockSignals(False)
                mw = Gui.getMainWindow()
                if mw:
                    mw.statusBar().showMessage(
                        f"REFERÊNCIA | {_format_dist_fc(dist)} | Enter no painel ou clique", 1200)
            else:
                if self.overlay:
                    self.overlay.clear_all()

            # ── 4. SALVA PARA O CLIQUE ──────────────────────────────────────
            # No modo de direção: clique sempre insere em dir_origin
            # No modo de parede com p1: fantasma fica em wall_p1 (gerenciado acima)
            if self.dir_locked and self.dir_origin is not None:
                self.last_snap_point = App.Vector(self.dir_origin.x, self.dir_origin.y, z)
            elif self.wall_active and self.wall_p1 is not None:
                # Fantasma já foi movido manualmente acima; apenas salva cursor para referência
                self.last_snap_point = cursor_pt
            else:
                self.last_snap_point = cursor_pt
            self.last_snap_rot   = rot

            # ── 5. POSICIONA O FANTASMA ─────────────────────────────────────
            ghost_init_pt = App.Vector(px, py, z)
            if not self.ghost:
                self.ghost = self.placement_func(cursor_pt, is_ghost=True)
                if self.ghost:
                    if getattr(self.ghost, "ViewObject", None) is not None:
                        try: self.ghost.ViewObject.Selectable = False
                        except Exception: pass
                    def _make_non_sel(name=self.ghost.Name):
                        try:
                            go = Gui.ActiveDocument.getObject(name)
                            if go: go.Selectable = False
                        except Exception: pass
                    QtCore.QTimer.singleShot(50, _make_non_sel)
            if self.ghost:
                self.ghost.Placement = App.Placement(
                    App.Vector(px, py, z), App.Rotation(App.Vector(0,0,1), rot))
                Gui.updateGui()

        except Exception as e:
            import traceback
            App.Console.PrintError(f"[Eletrica] Erro no on_move: {e}\n{traceback.format_exc()}\n")
            self.ghost = None

    # ------------------------------------------------------------------
    def on_click_pivy(self, event_callback):
        """Fallback Pivy: usado apenas se o filtro Qt não puder ser instalado."""
        try:
            from pivy import coin
            event = event_callback.getEvent()
            state = "DOWN" if event.getState() == coin.SoButtonEvent.DOWN else "UP"
            btn_val = event.getButton()
            button = {
                coin.SoMouseButtonEvent.BUTTON1: 'BUTTON1',
                coin.SoMouseButtonEvent.BUTTON2: 'BUTTON2',
                coin.SoMouseButtonEvent.BUTTON3: 'BUTTON3',
            }.get(btn_val, f"BUTTON{btn_val}")
            pos_val = event.getPosition()
            event_data = {
                'State': state, 'Button': button,
                'Position': (pos_val[0], pos_val[1]),
                'Shift': False,  # Pivy não expõe modificadores facilmente
                'Event': event
            }
            handled = self.on_click(event_data)
            if handled: event_callback.setHandled()
        except Exception as e:
            App.Console.PrintError(f"[Eletrica] Erro no on_click_pivy: {e}\n")

    # ------------------------------------------------------------------
    def on_click(self, event_data):
        """
        Lógica de clique principal.

        Ctrl+Clique:
          - Se não há ponto de direção → define dir_origin, NÃO insere.
          - Se já há ponto de direção  → cancela o modo de direção.

        Clique simples:
          - Se no modo de referência  → lógica de referência (R).
          - Caso contrário            → insere a tomada na posição atual.
        """
        try:
            Gui.Selection.clearSelection()

            if event_data['Button'] == 'BUTTON1' and event_data['State'] == 'DOWN':
                pos  = event_data['Position']
                shift = event_data.get('Shift', False)

                # Usa o último ponto calculado no on_move (mais preciso)
                fresh_point = self.last_snap_point
                if fresh_point is None:
                    if self.ghost:
                        self.ghost.ViewObject.Visibility = False; Gui.updateGui()
                    fresh_point = self.get_projection_point(pos)
                    if self.ghost:
                        self.ghost.ViewObject.Visibility = True; Gui.updateGui()

                if fresh_point is None:
                    return True

                target_point = fresh_point

                # ── Shift + Clique: define/cancela ponto de direção ─────────
                if shift:
                    if not self.dir_locked:
                        # 1º Shift+Clique: define a origem da direção
                        # Cancela modo parede se estiver ativo
                        self.wall_p1 = None; self.wall_active = False
                        if self.rot_mode == 5: self.rot_mode = 4
                        self.dir_origin = App.Vector(
                            target_point.x, target_point.y,
                            float(self.cmd.get_final_z()) if hasattr(self.cmd,'get_final_z')
                            else float(self.cmd.z_level))
                        self.dir_locked = True
                        if hasattr(self.panel, 'sync_rot_mode_buttons'):
                            self.panel.sync_rot_mode_buttons(4)
                        mw = Gui.getMainWindow()
                        if mw:
                            mw.statusBar().showMessage(
                                "DIREÇÃO: ponto fixo definido. Mova o mouse p/ girar. "
                                "Clique insere | Shift+Clique cancela", 5000)
                    else:
                        # 2º Shift+Clique: cancela o modo de direção
                        self.dir_origin = None; self.dir_locked = False
                        self.rot_mode = 1
                        if self.overlay: self.overlay.clear_all()
                        if hasattr(self.panel, 'sync_rot_mode_buttons'):
                            self.panel.sync_rot_mode_buttons(1)
                        mw = Gui.getMainWindow()
                        if mw:
                            mw.statusBar().showMessage("Modo de direção cancelado.", 3000)
                    return True

                # ── Clique simples: modo de parede ──────────────────────────
                if self.wall_active:
                    z = float(self.cmd.get_final_z()) if hasattr(self.cmd,'get_final_z') else float(self.cmd.z_level)
                    if self.wall_p1 is None:
                        # 1° clique: define o 1° ponto da reta de parede (posição da tomada)
                        self.wall_p1 = App.Vector(target_point.x, target_point.y, z)
                        mw = Gui.getMainWindow()
                        if mw:
                            mw.statusBar().showMessage(
                                "PAREDE: 1° ponto definido. Clique no 2° ponto da parede p/ definir ângulo.", 5000)
                        # Trava o fantasma no p1
                        if self.ghost:
                            self.ghost.Placement = App.Placement(
                                self.wall_p1, App.Rotation(App.Vector(0,0,1), self.cmd.rotation))
                            Gui.updateGui()
                        if getattr(self, 'gl_widget', None):
                            self.gl_widget.setFocus()
                        return True
                    else:
                        # 2° clique: calcula ângulo perpendicular, insere e limpa
                        dx = target_point.x - self.wall_p1.x
                        dy = target_point.y - self.wall_p1.y
                        dist2d = math.sqrt(dx*dx + dy*dy)
                        if dist2d > 5.0:
                            wall_angle = math.degrees(math.atan2(dy, dx))
                            self.cmd.rotation = int((wall_angle + 90.0) % 360)
                        self.apply_host_to_command()
                        self.placement_func(self.wall_p1, is_ghost=False)
                        # Limpa estado de parede para próxima inserção
                        self.wall_p1 = None
                        if self.overlay: self.overlay.clear_all()
                        if not getattr(self.cmd, "continuous_insert", True):
                            self.wall_active = False; self.rot_mode = 1
                            self.stop()
                        else:
                            mw = Gui.getMainWindow()
                            if mw:
                                mw.statusBar().showMessage(
                                    "PAREDE: inserido! Clique no próximo 1° ponto.", 3000)
                        return True

                # ── Clique simples: modo de referência ──────────────────────
                if self.ref_mode_active:
                    if self.ref_point is None:
                        # 1º clique: define o ponto de origem da referência
                        self.ref_point = target_point

                        if hasattr(self.panel, 'ref_dist_in'):
                            self.panel.ref_dist_in.setEnabled(True)
                            self.panel.ref_dist_in.setValue(0.0)
                            # NÃO damos foco ao spinbox — foco fica na viewport
                        mw = Gui.getMainWindow()
                        if mw:
                            mw.statusBar().showMessage(
                                "Referência definida. Clique no 2° ponto para inserir "
                                "ou digite a distância no painel.", 5000)
                        # Devolve foco ao widget da viewport 3D
                        if getattr(self, 'gl_widget', None):
                            self.gl_widget.setFocus()
                        return True
                    else:
                        # 2º clique: insere na posição atual
                        self.apply_host_to_command()
                        self.placement_func(target_point, is_ghost=False)
                        self.clear_reference_mode()
                        self.rot_mode = 1
                        if hasattr(self.panel, 'sync_rot_mode_buttons'):
                            self.panel.sync_rot_mode_buttons(1)
                        if not getattr(self.cmd, "continuous_insert", True):
                            self.stop()
                        return True


                # ── Clique simples: inserção normal ─────────────────────────
                self.apply_host_to_command()

                # Limpa o modo de direção após inserir (libera para a próxima inserção)
                if self.dir_locked:
                    self.dir_origin = None
                    self.dir_locked = False
                    if self.overlay: self.overlay.clear_all()

                active_doc = App.ActiveDocument
                if active_doc is None:
                    active_doc = App.newDocument("Projeto_Eletrico")
                existing_names = {obj.Name for obj in active_doc.Objects}
                self.placement_func(target_point, is_ghost=False)
                try:
                    if App.ActiveDocument is None:
                        App.setActiveDocument(active_doc.Name)
                except Exception: pass

                new_objects = [obj for obj in active_doc.Objects
                               if obj.Name not in existing_names]
                for new_obj in new_objects:
                    if getattr(new_obj, "ViewObject", None) is not None:
                        try: new_obj.ViewObject.Selectable = False
                        except Exception: pass
                    def _make_non_sel(name=new_obj.Name):
                        try:
                            go = Gui.ActiveDocument.getObject(name)
                            if go: go.Selectable = False
                        except Exception: pass
                    QtCore.QTimer.singleShot(50, _make_non_sel)

                    # Alocação automática em Níveis BIM
                    try:
                        already_in_level = False
                        for parent in getattr(new_obj, "InList", []):
                            if (getattr(parent, "IfcType", "") == "Building Storey"
                                    or parent.isDerivedFrom("Arch::BuildingPart")):
                                already_in_level = True; break
                        if not already_in_level:
                            obj_z = None
                            if hasattr(new_obj, "Placement") and new_obj.Placement is not None:
                                obj_z = new_obj.Placement.Base.z
                            if obj_z is not None:
                                best_level = None; best_diff = float('inf')
                                niveis = []
                                for o in active_doc.Objects:
                                    if (getattr(o, "IfcType", "") == "Building Storey"
                                            or o.isDerivedFrom("Arch::BuildingPart")):
                                        niveis.append(o)
                                if not niveis:
                                    for o in active_doc.Objects:
                                        if (o.Label == "Niveis"
                                                and o.isDerivedFrom("App::DocumentObjectGroup")):
                                            niveis.extend(getattr(o, "OutList", [])); break
                                for nivel in niveis:
                                    try:
                                        lvl_z = 0.0
                                        if hasattr(nivel, "Placement") and nivel.Placement:
                                            lvl_z = nivel.Placement.Base.z
                                        elif hasattr(nivel, "Elevation"):
                                            elev = getattr(nivel, "Elevation")
                                            lvl_z = float(elev.Value if hasattr(elev,"Value") else elev)
                                        diff = obj_z - lvl_z
                                        if diff >= -0.1 and diff < best_diff:
                                            best_diff = diff; best_level = nivel
                                    except Exception: pass
                                if best_level is not None and hasattr(best_level, "addObject"):
                                    gp = new_obj.Placement
                                    best_level.addObject(new_obj)
                                    try:
                                        new_obj.Placement = best_level.Placement.inverse() * gp
                                    except Exception: pass
                    except Exception as e:
                        App.Console.PrintWarning(f"[Eletrica] Falha ao alocar no BIM: {e}\n")

                Gui.Selection.clearSelection()
                QtCore.QTimer.singleShot(150, Gui.Selection.clearSelection)

                if not getattr(self.cmd, "continuous_insert", True):
                    self.stop()

            return True  # Consome TODOS os eventos BUTTON1 para evitar popup

        except Exception as e:
            import traceback
            App.Console.PrintError(f"[Eletrica] Erro no on_click: {e}\n{traceback.format_exc()}\n")
            try:
                from PySide2 import QtWidgets
            except ImportError:
                from PySide6 import QtWidgets
            QtWidgets.QMessageBox.critical(None, "Eletrica Error",
                                           f"Erro ao inserir componente:\n{e}")

    # ------------------------------------------------------------------
    def capture_host_info(self, info):
        old_host = self.last_host_object
        self.last_host_object = ""; self.last_host_sub = ""
        if not info:
            if old_host != "": self.show_placement_status()
            return
        self.last_host_object = info.get('Object', '') or ''
        self.last_host_sub    = info.get('Component', '') or info.get('SubElement', '') or ''
        if self.last_host_object != old_host: self.show_placement_status()

    def apply_host_to_command(self):
        if hasattr(self.cmd, 'host_object'): self.cmd.host_object = self.last_host_object
        if hasattr(self.cmd, 'host_sub'):    self.cmd.host_sub    = self.last_host_sub

    def is_snapped(self, pos):
        """Verifica se o mouse está sobre uma caixa de snap (JunctionBox)."""
        if not self.should_query_view_objects(): return False
        info = self.view.getObjectInfo(pos)
        if info and 'Object' in info:
            obj = App.ActiveDocument.getObject(info['Object'])
            if obj and ("Caixa" in obj.Label or "JunctionBox" in obj.Label):
                return True
        return False

    # ------------------------------------------------------------------
    def stop(self):
        # Remove overlay Coin3D
        if self.overlay:
            try: self.overlay.remove()
            except Exception: pass
            self.overlay = None

        self.delete_temp_line()
        self.set_action_checked(False)
        self.restore_preselection()
        self.clear_preselection()

        # Remove filtro Qt de teclado
        if getattr(self, "key_filter", None):
            try:
                app = QtGui.QApplication.instance()
                if app: app.removeEventFilter(self.key_filter)
            except Exception: pass
            self.key_filter = None

        # Remove filtro Qt de cliques
        if getattr(self, "gl_widget", None) and getattr(self, "qt_filter", None):
            try: self.gl_widget.removeEventFilter(self.qt_filter)
            except Exception: pass
            self.gl_widget = None; self.qt_filter = None

        # Restaura seleção dos objetos com atraso de 250ms
        saved = dict(getattr(self, "saved_selectable", {}))
        self.saved_selectable = {}

        def _delayed_restore():
            doc = App.ActiveDocument
            if not doc: return
            # Só restaura os objetos que nós salvamos — nunca toca em outros
            for name, sel_state in saved.items():
                try:
                    obj = doc.getObject(name)
                    if obj and getattr(obj, 'ViewObject', None):
                        obj.ViewObject.Selectable = sel_state
                except Exception:
                    pass
            try: Gui.Selection.clearSelection()
            except Exception: pass

        QtCore.QTimer.singleShot(250, _delayed_restore)

        try: Gui.Selection.clearSelection()
        except Exception: pass
        try: Gui.Selection.removeSelectionGate()
        except Exception: pass
        if self.callback:
            try:
                from pivy import coin
                self.view.removeEventCallbackPivy(
                    coin.SoMouseButtonEvent.getClassTypeId(), self.callback)
            except Exception: pass
        if self.kb_callback:   self.view.removeEventCallback("SoKeyboardEvent",  self.kb_callback)
        if self.move_callback: self.view.removeEventCallback("SoLocation2Event", self.move_callback)
        if self.ghost:
            try: App.ActiveDocument.removeObject(self.ghost.Name)
            except Exception: pass
            self.ghost = None
        QtGui.QApplication.restoreOverrideCursor()
        Gui.Control.closeDialog()

        if BIMPlacementEngine.active_engine == self:
            BIMPlacementEngine.active_engine = None
        self.clear_checkable_actions()
        # NÃO faz recompute aqui — evita recalcular links de arquitetura
        # e causar shapes nulos que tornam objetos invisíveis.

    # ------------------------------------------------------------------
    def toggle_panel(self):
        try:
            if Gui.Control.activeDialog() is not None:
                Gui.Control.closeDialog()
            else:
                Gui.Control.showDialog(self.panel)
                if hasattr(self.panel, 'sync_ui'): self.panel.sync_ui()
        except Exception as e:
            print(f"[Eletrica] Erro ao alternar painel: {e}")

    def place_at_distance(self, distance):
        """Insere a tomada a uma distância exata do ponto de referência."""
        if self.ref_point is None: return
        current_point = self.last_snap_point
        if current_point is None: return
        direction = current_point - self.ref_point
        if direction.Length > 1e-6:
            direction = direction.normalize()
            target_point = self.ref_point + direction * distance
        else:
            target_point = self.ref_point
        self.apply_host_to_command()
        self.placement_func(target_point, is_ghost=False)
        self.clear_reference_mode()
        if not getattr(self.cmd, "continuous_insert", True):
            self.stop()

    def clear_reference_mode(self):
        self.ref_point = None; self.ref_mode_active = False
        if hasattr(self.panel, 'ref_btn'):
            self.panel.ref_btn.blockSignals(True)
            self.panel.ref_btn.setChecked(False)
            self.panel.ref_btn.blockSignals(False)
            self.panel.ref_dist_in.blockSignals(True)
            self.panel.ref_dist_in.setEnabled(False)
            self.panel.ref_dist_in.setValue(0.0)
            self.panel.ref_dist_in.blockSignals(False)
        self.delete_temp_line()
        if self.overlay: self.overlay.clear_all()

    def delete_temp_line(self):
        doc = App.ActiveDocument
        if doc:
            line_name = "TEMP_Ref_Line"
            obj = doc.getObject(line_name)
            if obj:
                try:
                    doc.removeObject(line_name)
                    # NÃO chama recompute aqui — evita recalcular links externos
                except Exception:
                    pass
            try:
                Gui.updateGui()
            except Exception:
                pass
